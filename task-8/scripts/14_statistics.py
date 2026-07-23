import pandas as pd
import numpy as np
import os

def calculate_mode(series):
    modes = series.mode()
    if len(modes) > 0:
        return modes.iloc[0]
    return np.nan

def main():
    print("Starting Phase 6: Statistical Analysis...")
    
    input_path = 'data/clean/master_orders_features.csv'
    output_path = 'outputs/statistics_summary.txt'
    
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found. Please run Phase 4 first.")
        return
        
    print(f"Reading {input_path}...")
    df = pd.read_csv(input_path)
    
    cols_of_interest = ['price', 'freight_value', 'review_score', 'delivery_days', 'approx_profit_margin']
    available_cols = [c for c in cols_of_interest if c in df.columns]
    
    print(f"Calculating descriptive statistics for: {', '.join(available_cols)}...")
    
    # Compute descriptive statistics
    stats_dict = {}
    
    for c in available_cols:
        series = df[c].dropna()
        
        q1 = series.quantile(0.25)
        q2 = series.median()
        q3 = series.quantile(0.75)
        
        stats_dict[c] = {
            'Mean': series.mean(),
            'Median': q2,
            'Mode': calculate_mode(series),
            'Variance': series.var(),
            'Std Deviation': series.std(),
            'Q1 (25th)': q1,
            'Q2 (50th)': q2,
            'Q3 (75th)': q3,
            'IQR': q3 - q1,
            '90th Percentile': series.quantile(0.90),
            '95th Percentile': series.quantile(0.95)
        }
        
    stats_df = pd.DataFrame(stats_dict)
    
    print("Calculating correlation and covariance matrices for all numeric columns...")
    numeric_df = df.select_dtypes(include=[np.number])
    corr_matrix = numeric_df.corr()
    cov_matrix = numeric_df.cov()
    
    os.makedirs('outputs', exist_ok=True)
    
    print(f"Writing results to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("========================================================\n")
        f.write("                 STATISTICAL SUMMARY                    \n")
        f.write("========================================================\n\n")
        
        f.write("--- Descriptive Statistics ---\n")
        f.write(stats_df.round(4).to_string())
        f.write("\n\n\n")
        
        f.write("--- Correlation Matrix (All Numeric Columns) ---\n")
        f.write(corr_matrix.round(4).to_string())
        f.write("\n\n\n")
        
        f.write("--- Covariance Matrix (All Numeric Columns) ---\n")
        f.write(cov_matrix.round(4).to_string())
        f.write("\n\n")
        
    print("Phase 6 Statistical Analysis complete!")

if __name__ == "__main__":
    main()
