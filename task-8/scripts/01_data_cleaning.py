import pandas as pd
import numpy as np
import os

# Paths
RAW_DIR = 'data/raw'
CLEAN_DIR = 'data/clean'
LOG_FILE = os.path.join(CLEAN_DIR, 'cleaning_log.txt')

def log_msg(msg):
    print(msg)
    with open(LOG_FILE, 'a') as f:
        f.write(msg + '\n')

def main():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    
    log_msg("=== Starting Data Cleaning Pipeline ===\n")
    
    # 1. Load Data
    log_msg("--- Loading Data ---")
    datasets = {
        'customers': 'olist_customers_dataset.csv',
        'orders': 'olist_orders_dataset.csv',
        'items': 'olist_order_items_dataset.csv',
        'payments': 'olist_order_payments_dataset.csv',
        'reviews': 'olist_order_reviews_dataset.csv',
        'products': 'olist_products_dataset.csv',
        'sellers': 'olist_sellers_dataset.csv',
        'translation': 'product_category_name_translation.csv'
        # Note: geolocation intentionally skipped for this stage per user request
    }
    
    dfs = {}
    for name, filename in datasets.items():
        path = os.path.join(RAW_DIR, filename)
        log_msg(f"Loading {filename}...")
        dfs[name] = pd.read_csv(path)
        log_msg(f"  Rows loaded: {len(dfs[name])}")
        
    # 2. Basic Cleaning (Deduplication, Text casing, Timestamps)
    log_msg("\n--- Basic Cleaning ---")
    
    for name, df in dfs.items():
        initial_len = len(df)
        df.drop_duplicates(inplace=True)
        dropped = initial_len - len(df)
        if dropped > 0:
            log_msg(f"{name}: Dropped {dropped} duplicate rows.")
            
        # Standardize text (city -> title case, state -> uppercase)
        for col in df.columns:
            if df[col].dtype == 'object':
                if 'city' in col:
                    df[col] = df[col].str.title()
                elif 'state' in col:
                    df[col] = df[col].str.upper()
                
        # Fix timestamps in orders, reviews and items
        if name == 'orders':
            time_cols = ['order_purchase_timestamp', 'order_approved_at', 
                         'order_delivered_carrier_date', 'order_delivered_customer_date', 
                         'order_estimated_delivery_date']
            for col in time_cols:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        elif name == 'reviews':
            time_cols = ['review_creation_date', 'review_answer_timestamp']
            for col in time_cols:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        elif name == 'items':
            df['shipping_limit_date'] = pd.to_datetime(df['shipping_limit_date'], errors='coerce')
            
    # 3. Missing values & Invalid records
    log_msg("\n--- Handling Missing Values & Invalid Records ---")
    
    # Orders missing purchase timestamp
    orders = dfs['orders']
    missing_purchase = orders['order_purchase_timestamp'].isna().sum()
    if missing_purchase > 0:
        log_msg(f"orders: Dropping {missing_purchase} rows with missing order_purchase_timestamp")
        orders = orders.dropna(subset=['order_purchase_timestamp'])
    dfs['orders'] = orders
    
    # Items (price <= 0)
    items = dfs['items']
    invalid_price = (items['price'] <= 0).sum()
    if invalid_price > 0:
        log_msg(f"items: Dropping {invalid_price} rows with price <= 0")
        items = items[items['price'] > 0]
    dfs['items'] = items
    
    # Reviews (scores outside 1-5)
    reviews = dfs['reviews']
    invalid_scores = (~reviews['review_score'].between(1, 5)).sum()
    if invalid_scores > 0:
        log_msg(f"reviews: Dropping {invalid_scores} rows with invalid review scores")
        reviews = reviews[reviews['review_score'].between(1, 5)]
    dfs['reviews'] = reviews
    
    # Payments (negative values)
    payments = dfs['payments']
    invalid_payments = (payments['payment_value'] < 0).sum()
    if invalid_payments > 0:
        log_msg(f"payments: Dropping {invalid_payments} rows with negative payment_value")
        payments = payments[payments['payment_value'] >= 0]
    dfs['payments'] = payments
    
    # Log other missing values (general summary)
    for name, df in dfs.items():
        missing_counts = df.isna().sum()
        missing_counts = missing_counts[missing_counts > 0]
        if not missing_counts.empty:
            log_msg(f"{name} missing values summary:\n{missing_counts.to_string()}")
            
    # 4. Translation
    log_msg("\n--- Translating Product Categories ---")
    products = dfs['products']
    translation = dfs['translation']
    products = products.merge(translation, on='product_category_name', how='left')
    products['product_category_name'] = products['product_category_name_english'].combine_first(products['product_category_name'])
    products.drop(columns=['product_category_name_english'], inplace=True, errors='ignore')
    dfs['products'] = products
    log_msg("Translated product_category_name to English where available.")
    
    # 5. Aggregations
    log_msg("\n--- Aggregating Payments and Reviews ---")
    payments_agg = dfs['payments'].groupby('order_id', as_index=False)['payment_value'].sum()
    payments_agg.rename(columns={'payment_value': 'total_payment_value'}, inplace=True)
    
    reviews_agg = dfs['reviews'].groupby('order_id', as_index=False)['review_score'].mean()
    
    log_msg(f"Aggregated payments down to {len(payments_agg)} order-level rows.")
    log_msg(f"Aggregated reviews down to {len(reviews_agg)} order-level rows.")
    
    # 6. Referential Integrity
    log_msg("\n--- Referential Integrity Checks ---")
    orders = dfs['orders']
    customers = dfs['customers']
    sellers = dfs['sellers']
    
    orphaned_items_orders = ~items['order_id'].isin(orders['order_id'])
    log_msg(f"Orphaned order_items (missing order): {orphaned_items_orders.sum()}")
    
    orphaned_items_prods = ~items['product_id'].isin(products['product_id'])
    log_msg(f"Orphaned order_items (missing product): {orphaned_items_prods.sum()}")
    
    orphaned_items_sellers = ~items['seller_id'].isin(sellers['seller_id'])
    log_msg(f"Orphaned order_items (missing seller): {orphaned_items_sellers.sum()}")
    
    orphaned_orders_customers = ~orders['customer_id'].isin(customers['customer_id'])
    log_msg(f"Orphaned orders (missing customer): {orphaned_orders_customers.sum()}")
    
    # 7. Master Table Creation
    log_msg("\n--- Creating Master Table ---")
    
    integrity_warning = (
        "DATA INTEGRITY WARNING: total_payment_value and review_score are order-level values "
        "duplicated across item rows. Do NOT sum total_payment_value across master_orders.csv "
        "rows for revenue calculations — this will overcount. Use price (item-level) for "
        "item/revenue rollups, or aggregate to order_id first before summing payments."
    )
    log_msg(integrity_warning)
    
    # Base is order_items, then left join others to maintain order-item grain
    master = items.merge(orders, on='order_id', how='left')
    master = master.merge(customers, on='customer_id', how='left')
    master = master.merge(products, on='product_id', how='left')
    master = master.merge(sellers, on='seller_id', how='left')
    master = master.merge(payments_agg, on='order_id', how='left')
    master = master.merge(reviews_agg, on='order_id', how='left')
    
    # Feature Engineering
    log_msg("Calculating derived time and delivery features...")
    master['year'] = master['order_purchase_timestamp'].dt.year
    master['month'] = master['order_purchase_timestamp'].dt.month
    master['year_month'] = master['order_purchase_timestamp'].dt.to_period('M').astype(str)
    master['weekday'] = master['order_purchase_timestamp'].dt.day_name()
    
    master['delivery_days'] = (master['order_delivered_customer_date'] - master['order_purchase_timestamp']).dt.days
    master['delivery_delay'] = (master['order_delivered_customer_date'] - master['order_estimated_delivery_date']).dt.days
    
    # 8. Verification and Saving
    log_msg("\n--- Saving Cleaned Data ---")
    for name, df in dfs.items():
        if name != 'translation': # No need to save the translation table again
            out_path = os.path.join(CLEAN_DIR, f"{name}_clean.csv")
            df.to_csv(out_path, index=False)
            log_msg(f"Saved {name}_clean.csv ({len(df)} rows)")
        
    master_path = os.path.join(CLEAN_DIR, 'master_orders.csv')
    master.to_csv(master_path, index=False)
    log_msg(f"Saved master_orders.csv")
    
    log_msg("\n=== Final Summary ===")
    log_msg(f"Master Orders Row Count: {len(master)}")
    log_msg(f"Cleaned Order Items Row Count: {len(items)}")
    
    if len(master) == len(items):
        log_msg("SUCCESS: Master table row count matches order_items row count (no join fan-out).")
    else:
        log_msg("WARNING: Master table row count does NOT match order_items row count!")
        
    min_date = master['order_purchase_timestamp'].min()
    max_date = master['order_purchase_timestamp'].max()
    log_msg(f"Data Date Range: {min_date} to {max_date}")

if __name__ == "__main__":
    main()
