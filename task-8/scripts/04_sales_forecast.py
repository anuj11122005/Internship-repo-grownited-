import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
import xgboost as xgb
import warnings
warnings.filterwarnings("ignore")

def create_features(df):
    """Create time series features based on time series index."""
    df = df.copy()
    df['dayofweek'] = df.index.dayofweek
    df['quarter'] = df.index.quarter
    df['month'] = df.index.month
    df['year'] = df.index.year
    df['dayofyear'] = df.index.dayofyear
    df['dayofmonth'] = df.index.day
    df['is_weekend'] = df['dayofweek'].isin([5, 6]).astype(int)
    return df

def add_lags(df):
    target_map = df['revenue'].to_dict()
    df['lag1'] = (df.index - pd.Timedelta('1 days')).map(target_map)
    df['lag7'] = (df.index - pd.Timedelta('7 days')).map(target_map)
    df['lag30'] = (df.index - pd.Timedelta('30 days')).map(target_map)
    df['rolling_mean_7'] = df['revenue'].rolling(window=7).mean().shift(1)
    df['rolling_mean_30'] = df['revenue'].rolling(window=30).mean().shift(1)
    return df

def main():
    print("Loading data...")
    df = pd.read_csv('data/clean/master_orders.csv')
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    
    if 'freight_value' in df.columns:
        df['revenue'] = df['price'] + df['freight_value']
    else:
        df['revenue'] = df['price']
        
    df['date'] = df['order_purchase_timestamp'].dt.date
    
    # 1. Aggregate to daily
    daily_sales = df.groupby('date')['revenue'].sum().reset_index()
    daily_sales['date'] = pd.to_datetime(daily_sales['date'])
    daily_sales.set_index('date', inplace=True)
    
    # 2. Handle gaps
    full_date_range = pd.date_range(start=daily_sales.index.min(), end=daily_sales.index.max(), freq='D')
    daily_sales = daily_sales.reindex(full_date_range, fill_value=0)
    daily_sales.index.name = 'date'
    
    print(f"Data aggregated daily from {daily_sales.index.min().date()} to {daily_sales.index.max().date()}.")
    print("Justification: Chose daily aggregation because day-of-week seasonality (e.g., weekday vs weekend differences) is a strong driver in e-commerce. Daily data preserves this signal and provides more data points for ML models to learn from.")
    
    # 3. Train/Test split
    # Hold out last 90 days
    test_days = 90
    train = daily_sales.iloc[:-test_days].copy()
    test = daily_sales.iloc[-test_days:].copy()
    
    print(f"\nTrain shape: {train.shape}, Test shape: {test.shape}")
    
    # 4. Approach 1: Holt-Winters (Exponential Smoothing)
    print("\nTraining Holt-Winters (Exponential Smoothing) Baseline...")
    hw_model = ExponentialSmoothing(train['revenue'], seasonal_periods=7, trend='add', seasonal='add', initialization_method="estimated").fit()
    hw_preds = hw_model.forecast(test_days)
    
    # 5. Approach 2: XGBoost with feature engineering
    print("Training XGBoost with Feature Engineering...")
    df_xgb = create_features(daily_sales)
    df_xgb = add_lags(df_xgb)
    
    # Drop NaNs from lag creation
    df_xgb_dropna = df_xgb.dropna()
    
    train_xgb = df_xgb_dropna[df_xgb_dropna.index <= train.index.max()]
    test_xgb = df_xgb_dropna[df_xgb_dropna.index > train.index.max()]
    
    FEATURES = ['dayofweek', 'quarter', 'month', 'year', 'dayofyear', 'dayofmonth', 'is_weekend', 'lag1', 'lag7', 'lag30', 'rolling_mean_7', 'rolling_mean_30']
    TARGET = 'revenue'
    
    X_train = train_xgb[FEATURES]
    y_train = train_xgb[TARGET]
    X_test = test_xgb[FEATURES]
    y_test = test_xgb[TARGET]
    
    xgb_reg = xgb.XGBRegressor(n_estimators=1000, early_stopping_rounds=50, learning_rate=0.05, max_depth=5, random_state=42)
    xgb_reg.fit(X_train, y_train, eval_set=[(X_train, y_train), (X_test, y_test)], verbose=False)
    
    xgb_preds = xgb_reg.predict(X_test)
    xgb_preds_series = pd.Series(xgb_preds, index=test_xgb.index)
    
    # Evaluate
    def evaluate(y_true, y_pred, model_name):
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mape = mean_absolute_percentage_error(y_true, y_pred) * 100
        print(f"[{model_name}] MAE: {mae:.2f} | RMSE: {rmse:.2f} | MAPE: {mape:.2f}%")
        return mae, rmse, mape

    print("\n--- Evaluation on Test Set (Last 90 days) ---")
    hw_metrics = evaluate(test['revenue'], hw_preds, "Holt-Winters")
    xgb_metrics = evaluate(y_test, xgb_preds_series, "XGBoost")
    
    # Determine winner (lower MAE)
    winner_name = "Holt-Winters" if hw_metrics[0] < xgb_metrics[0] else "XGBoost"
    print(f"\nWinning Model: {winner_name} (based on lowest MAE)")
    
    # 6. Forecast next 90 days
    print(f"\nRetraining {winner_name} on full dataset and forecasting next 90 days...")
    future_dates = pd.date_range(start=daily_sales.index.max() + pd.Timedelta(days=1), periods=90, freq='D')
    
    if winner_name == "Holt-Winters":
        final_model = ExponentialSmoothing(daily_sales['revenue'], seasonal_periods=7, trend='add', seasonal='add', initialization_method="estimated").fit()
        future_forecast = final_model.forecast(90)
        
        residuals = final_model.resid
        std_resid = np.std(residuals)
        upper_bound = future_forecast + 1.96 * std_resid
        lower_bound = future_forecast - 1.96 * std_resid
        lower_bound[lower_bound < 0] = 0
        
    else:
        X_all = df_xgb_dropna[FEATURES]
        y_all = df_xgb_dropna[TARGET]
        final_xgb = xgb.XGBRegressor(n_estimators=xgb_reg.best_iteration + 1, learning_rate=0.05, max_depth=5, random_state=42)
        final_xgb.fit(X_all, y_all)
        
        future_forecast = []
        current_df = df_xgb.copy()
        
        for date in future_dates:
            new_row = pd.DataFrame(index=[date])
            new_row['revenue'] = np.nan
            current_df = pd.concat([current_df, new_row])
            
            current_df = create_features(current_df)
            current_df = add_lags(current_df)
            
            X_pred = current_df.loc[[date], FEATURES]
            pred = final_xgb.predict(X_pred)[0]
            pred = max(0, pred)
            future_forecast.append(pred)
            current_df.loc[date, 'revenue'] = pred
            
        future_forecast = pd.Series(future_forecast, index=future_dates)
        
        residuals = y_test - xgb_preds_series
        std_resid = np.std(residuals)
        upper_bound = future_forecast + 1.96 * std_resid
        lower_bound = future_forecast - 1.96 * std_resid
        lower_bound[lower_bound < 0] = 0
        
    # Save forecast
    os.makedirs('outputs/figures', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)
    
    forecast_df = pd.DataFrame({
        'date': future_dates,
        'forecast_revenue': future_forecast.values,
        'lower_bound': lower_bound.values,
        'upper_bound': upper_bound.values
    })
    forecast_df.to_csv('outputs/sales_forecast.csv', index=False)
    
    total_forecasted = forecast_df['forecast_revenue'].sum()
    
    # 7. Plotting
    plt.figure(figsize=(15, 8))
    
    plot_start_date = daily_sales.index.max() - pd.Timedelta(days=180)
    plt.plot(daily_sales[daily_sales.index >= plot_start_date].index, 
             daily_sales.loc[daily_sales.index >= plot_start_date, 'revenue'], 
             label='Actual Revenue', color='black')
             
    if winner_name == "Holt-Winters":
        plt.plot(test.index, hw_preds, label='Test Set Prediction (Holt-Winters)', color='blue', alpha=0.7, linestyle='--')
    else:
        plt.plot(test_xgb.index, xgb_preds_series, label='Test Set Prediction (XGBoost)', color='blue', alpha=0.7, linestyle='--')
        
    plt.plot(future_forecast.index, future_forecast, label='Future Forecast (Next 90 Days)', color='red')
    plt.fill_between(future_forecast.index, lower_bound, upper_bound, color='red', alpha=0.2, label='95% Confidence Interval')
    
    plt.title(f"Sales Forecast - Next 90 Days ({winner_name})")
    plt.xlabel("Date")
    plt.ylabel("Daily Revenue")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('outputs/figures/sales_forecast.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Print Summary
    print("\n" + "="*50)
    print("FORECAST SUMMARY")
    print("="*50)
    print(f"Model Selected: {winner_name}")
    print(f"Reason: Achieved lowest Mean Absolute Error (MAE) on the 90-day test set.")
    print(f"Forecasted Total Revenue (Next 90 Days): ${total_forecasted:,.2f}")
    print("\nCaveats:")
    print("1. Model does not account for future planned promotions, marketing events, or holidays not present in the historical training data.")
    print("2. Confidence intervals assume normally distributed residuals, which may underestimate extremes during high-volatility periods.")
    print("3. Extrapolating trend beyond a few months can be risky; short-term (30-day) forecasts are typically more reliable.")
    print(f"\nOutputs saved to:")
    print("- outputs/sales_forecast.csv")
    print("- outputs/figures/sales_forecast.png")
    print("="*50)

if __name__ == "__main__":
    main()
