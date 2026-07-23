import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def main():
    print("Starting outlier detection...")
    
    master_path = 'data/clean/master_orders.csv'
    log_path = 'data/clean/cleaning_log.txt'
    figures_dir = 'outputs/figures'
    
    os.makedirs(figures_dir, exist_ok=True)
    
    print(f"Reading {master_path}...")
    df = pd.read_csv(master_path)
    
    # Calculate delivery_days if it doesn't exist natively
    if 'delivery_days' not in df.columns:
        print("Calculating delivery_days...")
        # We parse the dates explicitly
        purchase = pd.to_datetime(df['order_purchase_timestamp'], errors='coerce')
        delivered = pd.to_datetime(df['order_delivered_customer_date'], errors='coerce')
        df['delivery_days'] = (delivered - purchase).dt.total_seconds() / (24 * 3600)
    
    columns_to_check = ['price', 'freight_value', 'delivery_days']
    
    log_lines = ["\n--- Outlier Detection (Phase 3 Extension) ---"]
    
    for col in columns_to_check:
        if col not in df.columns:
            print(f"Column {col} not found in master_orders.csv. Skipping.")
            continue
            
        print(f"Processing {col}...")
        
        # Calculate IQR
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Identify outliers
        outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
        
        # Add flag column (True if outlier, False otherwise)
        flag_col_name = f'is_{col}_outlier'
        df[flag_col_name] = outlier_mask
        
        # Calculate stats
        num_outliers = outlier_mask.sum()
        pct_outliers = (num_outliers / len(df)) * 100
        
        finding = f"Column: {col} | Outliers: {num_outliers} | Percentage: {pct_outliers:.2f}% | IQR Bounds: [{lower_bound:.2f}, {upper_bound:.2f}]"
        print(f"  -> {finding}")
        log_lines.append(finding)
        
        # Visualize Boxplot
        plt.figure(figsize=(10, 4))
        sns.boxplot(x=df[col].dropna(), color='lightcoral')
        plt.title(f"Outlier Detection Boxplot: {col}", pad=15)
        plt.xlabel(col)
        
        # Add boundary lines for visualization
        plt.axvline(lower_bound, color='red', linestyle='--', alpha=0.5, label='Lower Bound')
        plt.axvline(upper_bound, color='red', linestyle='--', alpha=0.5, label='Upper Bound')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, f"outlier_boxplot_{col}.png"), dpi=300)
        plt.close()
        
    print("Writing updated master_orders.csv with flag columns...")
    df.to_csv(master_path, index=False)
    
    # Append to log
    if os.path.exists(log_path):
        mode = 'a'
    else:
        mode = 'w'
        log_lines.insert(0, "==================================================")
        log_lines.insert(1, "               DATA CLEANING LOG                  ")
        log_lines.insert(2, "==================================================")
        
    with open(log_path, mode, encoding='utf-8') as f:
        f.write("\n" + "\n".join(log_lines) + "\n")
        
    print(f"Findings appended to {log_path}")
    print("Done!")

if __name__ == "__main__":
    main()
