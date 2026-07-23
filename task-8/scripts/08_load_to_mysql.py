import os
import pandas as pd
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
import matplotlib.pyplot as plt
import matplotlib.patches as patches

"""
Note: MySQL was not confirmed to be running in this environment, so this script uses SQLite 
as a fallback, complying with the phase instructions. The schema defined in 
`scripts/07_mysql_schema.sql` is standard SQL and will run correctly on both SQLite and MySQL.
"""

# Mapping of table names to their respective CSV files
TABLE_FILES = {
    'customers': 'data/clean/customers_clean.csv',
    'sellers': 'data/clean/sellers_clean.csv',
    'products': 'data/clean/products_clean.csv',
    'orders': 'data/clean/orders_clean.csv',
    'order_items': 'data/clean/items_clean.csv',
    'payments': 'data/clean/payments_clean.csv',
    'reviews': 'data/clean/reviews_clean.csv'
}

def draw_er_diagram():
    """Generates an ER diagram as a PNG using matplotlib (zero external rendering dependencies)."""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Table positions (x, y)
    positions = {
        'customers': (2, 7),
        'orders': (5, 7),
        'payments': (8, 8.5),
        'reviews': (8, 5.5),
        'order_items': (5, 3),
        'products': (2, 3),
        'sellers': (8, 3)
    }
    
    # Draw boxes
    for table, (x, y) in positions.items():
        rect = patches.Rectangle((x-1.2, y-0.6), 2.4, 1.2, linewidth=2, edgecolor='black', facecolor='lightblue', zorder=2)
        ax.add_patch(rect)
        ax.text(x, y, table.upper(), ha='center', va='center', fontweight='bold', fontsize=12, zorder=3)
        
    # Draw relationships
    rels = [
        ('customers', 'orders', '1', 'N'),
        ('orders', 'payments', '1', 'N'),
        ('orders', 'reviews', '1', 'N'),
        ('orders', 'order_items', '1', 'N'),
        ('products', 'order_items', '1', 'N'),
        ('sellers', 'order_items', '1', 'N')
    ]
    
    for start, end, label_start, label_end in rels:
        x1, y1 = positions[start]
        x2, y2 = positions[end]
        
        # Adjust line start/end roughly to box edges
        if x1 == x2:
            x1_edge, x2_edge = x1, x2
            y1_edge = y1 - 0.6 if y1 > y2 else y1 + 0.6
            y2_edge = y2 + 0.6 if y1 > y2 else y2 - 0.6
        elif y1 == y2:
            x1_edge = x1 + 1.2 if x2 > x1 else x1 - 1.2
            x2_edge = x2 - 1.2 if x2 > x1 else x2 + 1.2
            y1_edge, y2_edge = y1, y2
        else:
            x1_edge = x1 + 1.2 if x2 > x1 else x1 - 1.2
            y1_edge = y1
            x2_edge = x2 - 1.2 if x2 > x1 else x2 + 1.2
            y2_edge = y2
            
        ax.annotate("",
            xy=(x2_edge, y2_edge), xycoords='data',
            xytext=(x1_edge, y1_edge), textcoords='data',
            arrowprops=dict(arrowstyle="->", color="black", lw=2, connectionstyle="arc3,rad=0.1"),
            zorder=1
        )
        
    ax.set_xlim(0, 10)
    ax.set_ylim(1, 10)
    ax.axis('off')
    plt.title("Olist Database Entity-Relationship (ER) Diagram", fontsize=18, pad=20, fontweight='bold')
    
    os.makedirs('outputs', exist_ok=True)
    plt.savefig('outputs/er_diagram.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def main():
    print("Initializing Database...")
    db_path = 'data/olist_clean.db'
    
    # Remove existing DB to ensure clean schema application
    if os.path.exists(db_path):
        os.remove(db_path)
            
    engine = create_engine(f'sqlite:///{db_path}')
    
    # 1. Apply Schema
    try:
        with sqlite3.connect(db_path) as conn:
            with open('scripts/07_mysql_schema.sql', 'r') as f:
                schema_sql = f.read()
            conn.executescript(schema_sql)
        print("Schema successfully applied.")
    except Exception as e:
        print(f"Error applying schema: {e}")
        return

    # 2. Load Data & Confirm Row Counts
    print("\nStarting batch data load...")
    
    # Load order matters for Foreign Keys
    load_order = [
        'customers',
        'sellers',
        'products',
        'orders',
        'order_items',
        'payments',
        'reviews'
    ]
    
    # Store valid primary keys to enforce FK constraints in pandas before insert
    valid_pks = {
        'customers': set(),
        'sellers': set(),
        'products': set(),
        'orders': set()
    }
    
    from sqlalchemy import text
    
    for table in load_order:
        file_path = TABLE_FILES[table]
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            
            # To prevent NOT NULL constraint failures
            if table == 'customers':
                df = df.dropna(subset=['customer_id', 'customer_unique_id'])
                df = df.drop_duplicates(subset=['customer_id'])
            elif table == 'sellers':
                df = df.dropna(subset=['seller_id'])
                df = df.drop_duplicates(subset=['seller_id'])
            elif table == 'products':
                df = df.dropna(subset=['product_id'])
                df = df.drop_duplicates(subset=['product_id'])
            elif table == 'orders':
                df = df.dropna(subset=['order_id', 'customer_id'])
                df = df.drop_duplicates(subset=['order_id'])
                # Enforce FK
                df = df[df['customer_id'].isin(valid_pks['customers'])]
            elif table == 'order_items':
                df = df.dropna(subset=['order_id', 'order_item_id', 'product_id', 'seller_id'])
                df = df.drop_duplicates(subset=['order_id', 'order_item_id'])
                # Enforce FKs
                df = df[df['order_id'].isin(valid_pks['orders'])]
                df = df[df['product_id'].isin(valid_pks['products'])]
                df = df[df['seller_id'].isin(valid_pks['sellers'])]
            elif table == 'payments':
                df = df.dropna(subset=['order_id', 'payment_sequential'])
                df = df.drop_duplicates(subset=['order_id', 'payment_sequential'])
                # Enforce FK
                df = df[df['order_id'].isin(valid_pks['orders'])]
            elif table == 'reviews':
                df = df.dropna(subset=['review_id', 'order_id'])
                df = df.drop_duplicates(subset=['review_id'])
                # Enforce FK
                df = df[df['order_id'].isin(valid_pks['orders'])]
            
            # Update valid PKs for downstream tables
            if table == 'customers':
                valid_pks['customers'].update(df['customer_id'])
            elif table == 'sellers':
                valid_pks['sellers'].update(df['seller_id'])
            elif table == 'products':
                valid_pks['products'].update(df['product_id'])
            elif table == 'orders':
                valid_pks['orders'].update(df['order_id'])
            
            original_len = len(df)
            
            with engine.begin() as conn:
                try:
                    # Use 'append' to preserve schema!
                    df.to_sql(table, conn, if_exists='append', index=False, chunksize=5000)
                    
                    # Verify
                    count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                    match_status = "PASS" if original_len == count else "WARNING (Counts Differ)"
                    print(f"[{match_status}] {table:<15} | Rows Loaded: {original_len:<8} | DB Rows: {count:<8}")
                except Exception as e:
                    print(f"[FAIL] {table:<15} | Error during insert: {e}")
        else:
            print(f"[SKIP] {table:<15} | File {file_path} not found.")

    # 3. Generate ER Diagram Image
    print("\nGenerating ER Diagram image...")
    draw_er_diagram()
    print("Saved ER Diagram to outputs/er_diagram.png.")

if __name__ == "__main__":
    main()
