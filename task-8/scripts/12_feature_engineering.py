import pandas as pd
import numpy as np

def main():
    print("Starting Feature Engineering...")
    input_path = 'data/clean/master_orders.csv'
    output_path = 'data/clean/master_orders_features.csv'
    
    print(f"Reading {input_path}...")
    df = pd.read_csv(input_path)
    
    # ---------------------------------------------------------
    # 1. Financial Features
    # ---------------------------------------------------------
    df['revenue'] = df['price']  # Item-level revenue
    df['approx_cost'] = df['freight_value']  # Approximation proxy for COGS
    df['approx_profit'] = df['revenue'] - df['approx_cost']
    
    # Calculate margin safely avoiding division by zero
    df['approx_profit_margin'] = np.where(
        df['revenue'] > 0, 
        df['approx_profit'] / df['revenue'], 
        0.0
    )
    
    # ---------------------------------------------------------
    # 2. Time/Date Features
    # ---------------------------------------------------------
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'], errors='coerce')
    df['order_month'] = df['order_purchase_timestamp'].dt.month
    df['order_quarter'] = df['order_purchase_timestamp'].dt.quarter
    df['order_year'] = df['order_purchase_timestamp'].dt.year
    df['is_weekend_order'] = df['order_purchase_timestamp'].dt.dayofweek >= 5  # 5=Sat, 6=Sun
    
    # ---------------------------------------------------------
    # 3. High Value Customer Flag (Substituted for "Membership")
    # ---------------------------------------------------------
    # Group by unique customer to find lifetime spend
    customer_spend = df.groupby('customer_unique_id')['price'].sum()
    
    # Define top 20% threshold
    spend_threshold = customer_spend.quantile(0.80)
    high_value_customers = customer_spend[customer_spend >= spend_threshold].index
    
    df['high_value_customer'] = df['customer_unique_id'].isin(high_value_customers)
    
    # ---------------------------------------------------------
    # SKIPPED FEATURES (Per Prompt 6 Field Mapping Notes)
    # ---------------------------------------------------------
    # discount_amount: Olist dataset contains no discount, coupon, or promo code data.
    # customer_age_group: Olist dataset contains no demographic data (Age/Gender).
    
    # Save the enriched table
    print(f"Saving enriched dataset to {output_path}...")
    df.to_csv(output_path, index=False)
    
    # ---------------------------------------------------------
    # Print Summary
    # ---------------------------------------------------------
    print("\n==================================================")
    print("         FEATURE ENGINEERING SUMMARY              ")
    print("==================================================")
    print(f"Total Rows Processed: {len(df):,}")
    print(f"Approx Profit Range:  R${df['approx_profit'].min():.2f} to R${df['approx_profit'].max():.2f}")
    
    # Convert margin to percentage string safely handling edge cases
    min_margin = df['approx_profit_margin'].min() * 100
    max_margin = df['approx_profit_margin'].max() * 100
    print(f"Approx Margin Range:  {min_margin:.2f}% to {max_margin:.2f}%")
    
    weekend_pct = df['is_weekend_order'].mean() * 100
    print(f"Weekend Orders:       {weekend_pct:.2f}%")
    
    hvc_pct = df['high_value_customer'].mean() * 100
    print(f"HVC Orders %:         {hvc_pct:.2f}% (Orders placed by High-Value Customers)")
    
    total_cust = df['customer_unique_id'].nunique()
    print(f"\nTop 20% Lifetime Spend Threshold: R${spend_threshold:.2f}")
    print(f"Unique High-Value Customers:      {len(high_value_customers):,} out of {total_cust:,}")
    print("==================================================")
    
if __name__ == "__main__":
    main()
