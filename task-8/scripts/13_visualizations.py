"""
Phase 5: Visualizations
This script generates exactly 20 charts saved to outputs/figures/.
NOTE: "Gender Distribution" and "Membership Analysis" from the original brief 
are substituted with geographic views and high-value-customer views respectively, 
per the field mapping doc (as Olist data lacks demographics).
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib.ticker as ticker

def main():
    print("Starting Phase 5: Generating Visualizations...")
    
    input_path = 'data/clean/master_orders_features.csv'
    output_dir = 'outputs/figures'
    
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return
        
    os.makedirs(output_dir, exist_ok=True)
    
    df = pd.read_csv(input_path)
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    
    # Pre-calculate delivery delay safely
    if 'order_delivered_customer_date' in df.columns and 'order_estimated_delivery_date' in df.columns:
        actual = pd.to_datetime(df['order_delivered_customer_date'])
        est = pd.to_datetime(df['order_estimated_delivery_date'])
        df['delivery_delay_days'] = (actual - est).dt.total_seconds() / (24*3600)
    else:
        df['delivery_delay_days'] = 0

    sns.set_theme(style="whitegrid")

    # ---------------------------------------------------------
    # SALES (4)
    # ---------------------------------------------------------
    
    # 01. Monthly Sales Trend
    plt.figure(figsize=(12, 6))
    monthly_sales = df.set_index('order_purchase_timestamp').resample('ME')['revenue'].sum().reset_index()
    sns.lineplot(data=monthly_sales, x='order_purchase_timestamp', y='revenue', marker='o')
    plt.title('01. Monthly Sales Trend')
    plt.xlabel('Month')
    plt.ylabel('Revenue (R$)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/01_monthly_sales_trend.png')
    plt.close()
    
    # 02. Daily Sales
    plt.figure(figsize=(12, 6))
    daily_sales = df.set_index('order_purchase_timestamp').resample('D')['revenue'].sum().reset_index()
    sns.lineplot(data=daily_sales, x='order_purchase_timestamp', y='revenue', alpha=0.7)
    plt.title('02. Daily Sales Trend')
    plt.xlabel('Date')
    plt.ylabel('Revenue (R$)')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/02_daily_sales.png')
    plt.close()
    
    # 03. Revenue Distribution (Histogram)
    plt.figure(figsize=(10, 6))
    # Clip to 99th percentile to make histogram readable
    rev_99 = df['revenue'].quantile(0.99)
    sns.histplot(df[df['revenue'] <= rev_99]['revenue'], bins=50, kde=True, color='green')
    plt.title('03. Revenue Distribution (Item Level - Capped at 99th Percentile)')
    plt.xlabel('Revenue (R$)')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/03_revenue_distribution.png')
    plt.close()
    
    # 04. Sales Growth Rate (MoM %)
    plt.figure(figsize=(12, 6))
    monthly_sales['growth_pct'] = monthly_sales['revenue'].pct_change() * 100
    sns.barplot(data=monthly_sales, x='order_purchase_timestamp', y='growth_pct', color='teal')
    plt.title('04. Month-over-Month Sales Growth Rate (%)')
    plt.xlabel('Month')
    plt.ylabel('Growth Rate (%)')
    # Use month-year for labels
    labels = [ts.strftime('%Y-%m') for ts in monthly_sales['order_purchase_timestamp']]
    plt.xticks(ticks=range(len(labels)), labels=labels, rotation=45)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/04_sales_growth_rate.png')
    plt.close()

    # ---------------------------------------------------------
    # PRODUCTS (4)
    # ---------------------------------------------------------
    
    # 05. Top 10 Products by Revenue
    plt.figure(figsize=(10, 6))
    top_products = df.groupby('product_id')['revenue'].sum().sort_values(ascending=False).head(10).reset_index()
    # Shorten UUIDs for display
    top_products['product_id_short'] = top_products['product_id'].str[:8]
    sns.barplot(data=top_products, y='product_id_short', x='revenue', palette='viridis')
    plt.title('05. Top 10 Products by Revenue')
    plt.xlabel('Revenue (R$)')
    plt.ylabel('Product ID (Shortened)')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/05_top_10_products_revenue.png')
    plt.close()
    
    # 06. Bottom 10 Products by Revenue ("worst")
    plt.figure(figsize=(10, 6))
    bottom_products = df.groupby('product_id')['revenue'].sum().sort_values(ascending=True).head(10).reset_index()
    bottom_products['product_id_short'] = bottom_products['product_id'].str[:8]
    sns.barplot(data=bottom_products, y='product_id_short', x='revenue', palette='Reds_r')
    plt.title('06. Bottom 10 Products by Revenue')
    plt.xlabel('Revenue (R$)')
    plt.ylabel('Product ID (Shortened)')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/06_bottom_10_products_revenue.png')
    plt.close()
    
    # 07. Revenue by Category (Bar)
    plt.figure(figsize=(12, 8))
    cat_revenue = df.groupby('product_category_name')['revenue'].sum().sort_values(ascending=False).head(20).reset_index()
    sns.barplot(data=cat_revenue, y='product_category_name', x='revenue', palette='mako')
    plt.title('07. Revenue by Product Category (Top 20)')
    plt.xlabel('Revenue (R$)')
    plt.ylabel('Category')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/07_revenue_by_category.png')
    plt.close()
    
    # 08. Category Order Count vs Revenue (Dual View)
    cat_stats = df.groupby('product_category_name').agg(
        total_revenue=('revenue', 'sum'),
        order_count=('order_id', 'nunique')
    ).sort_values('total_revenue', ascending=False).head(15).reset_index()
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()
    
    sns.barplot(data=cat_stats, x='product_category_name', y='total_revenue', ax=ax1, color='lightblue', alpha=0.7)
    sns.lineplot(data=cat_stats, x='product_category_name', y='order_count', ax=ax2, color='darkblue', marker='o', linewidth=2)
    
    ax1.set_title('08. Category Revenue vs Order Count (Top 15 Categories)')
    ax1.set_xlabel('Category')
    ax1.set_ylabel('Total Revenue (R$)', color='lightblue')
    ax2.set_ylabel('Order Count', color='darkblue')
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/08_category_revenue_vs_orders.png')
    plt.close()

    # ---------------------------------------------------------
    # CUSTOMERS (4)
    # ---------------------------------------------------------
    
    # 09. City-wise Customer Count (Top 10)
    plt.figure(figsize=(10, 6))
    city_counts = df.groupby('customer_city')['customer_unique_id'].nunique().sort_values(ascending=False).head(10).reset_index()
    sns.barplot(data=city_counts, y='customer_city', x='customer_unique_id', palette='crest')
    plt.title('09. Top 10 Cities by Customer Count')
    plt.xlabel('Unique Customers')
    plt.ylabel('City')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/09_top_cities_customers.png')
    plt.close()
    
    # 10. State-wise Customer Count
    plt.figure(figsize=(12, 6))
    state_counts = df.groupby('customer_state')['customer_unique_id'].nunique().sort_values(ascending=False).reset_index()
    sns.barplot(data=state_counts, x='customer_state', y='customer_unique_id', palette='rocket')
    plt.title('10. State-wise Customer Count')
    plt.xlabel('State')
    plt.ylabel('Unique Customers')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/10_state_customers.png')
    plt.close()
    
    # 11. High-Value vs Regular Customer Spend Comparison
    plt.figure(figsize=(8, 6))
    spend_comp = df.groupby('high_value_customer')['revenue'].sum().reset_index()
    spend_comp['Segment'] = spend_comp['high_value_customer'].map({True: 'High-Value (Top 20%)', False: 'Regular (Bottom 80%)'})
    sns.barplot(data=spend_comp, x='Segment', y='revenue', palette='Set2')
    plt.title('11. Total Spend: High-Value vs Regular Customers')
    plt.ylabel('Total Revenue (R$)')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/11_high_value_vs_regular_spend.png')
    plt.close()
    
    # 12. Customer Spending Distribution (Histogram)
    plt.figure(figsize=(10, 6))
    cust_spend = df.groupby('customer_unique_id')['revenue'].sum()
    spend_95 = cust_spend.quantile(0.95)
    sns.histplot(cust_spend[cust_spend <= spend_95], bins=50, kde=True, color='purple')
    plt.title('12. Customer Lifetime Spend Distribution (Capped at 95th Pct)')
    plt.xlabel('Lifetime Spend (R$)')
    plt.ylabel('Number of Customers')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/12_customer_spending_distribution.png')
    plt.close()

    # ---------------------------------------------------------
    # BUSINESS / STATISTICAL (8)
    # ---------------------------------------------------------
    
    # 13. Correlation Heatmap
    plt.figure(figsize=(8, 6))
    corr_cols = ['price', 'freight_value', 'review_score', 'delivery_days', 'approx_profit_margin']
    corr_df = df[[c for c in corr_cols if c in df.columns]].corr()
    sns.heatmap(corr_df, annot=True, cmap='coolwarm', fmt=".2f", vmin=-1, vmax=1)
    plt.title('13. Correlation Heatmap')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/13_correlation_heatmap.png')
    plt.close()
    
    # 14. Box Plots for price, freight_value, delivery_days (Outlier view)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    sns.boxplot(y=df['price'], ax=axes[0], color='skyblue')
    axes[0].set_title('Price Distribution')
    sns.boxplot(y=df['freight_value'], ax=axes[1], color='lightgreen')
    axes[1].set_title('Freight Value Distribution')
    
    if 'delivery_days' in df.columns:
        sns.boxplot(y=df['delivery_days'], ax=axes[2], color='salmon')
        axes[2].set_title('Delivery Days Distribution')
        
    plt.suptitle('14. Outlier Detection Box Plots')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/14_outlier_boxplots.png')
    plt.close()
    
    # 15. Scatter Plot (Price vs Review Score)
    plt.figure(figsize=(10, 6))
    # Group by order_item_id or just sample 10000 to avoid massive scatter plot overplotting
    sample_df = df.sample(min(10000, len(df)), random_state=42)
    sns.scatterplot(data=sample_df, x='price', y='review_score', alpha=0.3, color='dodgerblue')
    plt.title('15. Price vs Review Score (Sampled)')
    plt.xlabel('Price (R$)')
    plt.ylabel('Review Score')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/15_scatter_price_vs_review.png')
    plt.close()
    
    # 16. Scatter Plot (Delivery Delay vs Review Score)
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=sample_df, x='delivery_delay_days', y='review_score', alpha=0.3, color='coral')
    plt.axvline(0, color='red', linestyle='--', label='On Time Deadline')
    plt.title('16. Delivery Delay (Days) vs Review Score')
    plt.xlabel('Delivery Delay (Positive = Late)')
    plt.ylabel('Review Score')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{output_dir}/16_scatter_delay_vs_review.png')
    plt.close()
    
    # 17. Pair Plot
    pair_cols = ['price', 'freight_value', 'review_score', 'delivery_days']
    pair_cols = [c for c in pair_cols if c in df.columns]
    # Sample down significantly for pairplot speed
    pair_df = df[pair_cols].dropna().sample(min(2000, len(df)), random_state=42)
    pairplot = sns.pairplot(pair_df, diag_kind='kde', plot_kws={'alpha':0.5})
    pairplot.fig.suptitle('17. Pair Plot of Key Metrics', y=1.02)
    pairplot.savefig(f'{output_dir}/17_pair_plot.png')
    plt.close()
    
    # 18. Revenue by Weekday Heatmap
    plt.figure(figsize=(10, 4))
    df['weekday'] = df['order_purchase_timestamp'].dt.day_name()
    # Sort order
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_rev = df.groupby('weekday')['revenue'].sum().reindex(days).to_frame().T
    sns.heatmap(weekday_rev, cmap='YlGnBu', annot=True, fmt=".0f")
    plt.title('18. Revenue Heatmap by Weekday')
    plt.yticks([])
    plt.tight_layout()
    plt.savefig(f'{output_dir}/18_revenue_by_weekday_heatmap.png')
    plt.close()
    
    # 19. Revenue by Hour-of-Day
    plt.figure(figsize=(10, 6))
    df['hour'] = df['order_purchase_timestamp'].dt.hour
    hourly_rev = df.groupby('hour')['revenue'].sum().reset_index()
    sns.barplot(data=hourly_rev, x='hour', y='revenue', palette='magma')
    plt.title('19. Revenue by Hour of Day')
    plt.xlabel('Hour (24h format)')
    plt.ylabel('Total Revenue (R$)')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/19_revenue_by_hour.png')
    plt.close()
    
    # 20. Payment Method Distribution
    plt.figure(figsize=(8, 8))
    # payment_type is in payments_clean.csv, not master
    payments_df = pd.read_csv('data/clean/payments_clean.csv')
    order_payment = df[['order_id']].drop_duplicates().merge(payments_df, on='order_id', how='inner')
    pay_counts = order_payment['payment_type'].value_counts()
    plt.pie(pay_counts, labels=pay_counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
    plt.title('20. Payment Method Distribution')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/20_payment_method_distribution.png')
    plt.close()

    print("Phase 5 completed! Generated 20 charts in outputs/figures/")

if __name__ == "__main__":
    main()
