import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configure page layout and title
st.set_page_config(page_title="E-commerce Dashboard", page_icon="🛒", layout="wide")

@st.cache_data
def load_data():
    """Load and prepare data for the dashboard."""
    # Load data
    master = pd.read_csv('data/clean/master_orders_features.csv')
    payments = pd.read_csv('data/clean/payments_clean.csv')
    
    # Process dates
    master['order_purchase_timestamp'] = pd.to_datetime(master['order_purchase_timestamp'])
    master['date'] = master['order_purchase_timestamp'].dt.date
    master['hour'] = master['order_purchase_timestamp'].dt.hour
    
    # Standardize weekday to title case for logical sorting later
    master['weekday'] = master['weekday'].str.title()
    
    # Pre-calculate revenue per item
    if 'revenue' not in master.columns:
        master['revenue'] = master['price'] + master['freight_value']
    
    return master, payments

@st.cache_data
def convert_df(df):
    """Convert dataframe to CSV for downloading."""
    return df.to_csv(index=False).encode('utf-8')

# --- Load Data ---
master_df, payments_df = load_data()

# --- Title and Freshness ---
min_date = master_df['date'].min()
max_date = master_df['date'].max()

st.title("🛒 E-Commerce Interactive Dashboard")
st.markdown(f"**Data Freshness:** _{min_date}_ to _{max_date}_")

# --- Sidebar Filters ---
st.sidebar.header("Global Filters")

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Handle partial date selections gracefully
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

# Categorical filters
all_categories = sorted([str(x) for x in master_df['product_category_name'].dropna().unique()])
selected_categories = st.sidebar.multiselect("Filter by Product Category", options=all_categories)

all_states = sorted([str(x) for x in master_df['customer_state'].dropna().unique()])
selected_states = st.sidebar.multiselect("Filter by Customer State", options=all_states)

# --- Apply Filters ---
mask = (master_df['date'] >= start_date) & (master_df['date'] <= end_date)

if selected_categories:
    mask &= master_df['product_category_name'].isin(selected_categories)
if selected_states:
    mask &= master_df['customer_state'].isin(selected_states)

filtered_df = master_df[mask]

# Filter payments to only match the filtered orders
filtered_orders = filtered_df['order_id'].unique()
filtered_payments = payments_df[payments_df['order_id'].isin(filtered_orders)]

# --- Sidebar Download Button ---
st.sidebar.markdown("---")
csv_data = convert_df(filtered_df)
st.sidebar.download_button(
    label="📥 Download Filtered Data (CSV)",
    data=csv_data,
    file_name='filtered_ecommerce_data.csv',
    mime='text/csv',
)

# --- Overview KPIs ---
if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

total_revenue = filtered_df['revenue'].sum()
total_profit = filtered_df['approx_profit'].sum() if 'approx_profit' in filtered_df.columns else 0
total_orders = filtered_df['order_id'].nunique()
total_customers_count = filtered_df['customer_unique_id'].nunique()
aov = total_revenue / total_orders if total_orders > 0 else 0

# Repeat customer logic
customer_order_counts = filtered_df.groupby('customer_unique_id')['order_id'].nunique()
repeat_customers_count = (customer_order_counts > 1).sum()
total_customers = customer_order_counts.count()
repeat_customer_rate = (repeat_customers_count / total_customers) * 100 if total_customers > 0 else 0

avg_review_score = filtered_df['review_score'].mean()

cols = st.columns(6)
cols[0].metric("Total Revenue", f"${total_revenue:,.2f}")
cols[1].metric("Total Approx. Profit", f"${total_profit:,.2f}", help="Approximate - freight-based proxy")
cols[2].metric("Total Customers", f"{total_customers_count:,}")
cols[3].metric("Total Orders", f"{total_orders:,}")
cols[4].metric("AOV", f"${aov:,.2f}")
cols[5].metric("Repeat Cust %", f"{repeat_customer_rate:.1f}%")

st.markdown("---")

# --- Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["📈 Sales Trends", "👥 Customer Behavior", "📦 Products", "📊 Correlation & Profit"])

# --- Tab 1: Sales Trends ---
with tab1:
    st.subheader("Sales & Order Volume Trends")
    
    # We group by year_month
    trend_data = filtered_df.groupby('year_month').agg(
        total_revenue=('revenue', 'sum'),
        total_orders=('order_id', 'nunique')
    ).reset_index().sort_values('year_month')
    
    c1, c2 = st.columns(2)
    with c1:
        fig_rev = px.line(trend_data, x='year_month', y='total_revenue', markers=True,
                          title="Monthly Revenue Trend", labels={'year_month': 'Month', 'total_revenue': 'Revenue ($)'})
        st.plotly_chart(fig_rev, use_container_width=True)
        
    with c2:
        fig_ord = px.bar(trend_data, x='year_month', y='total_orders',
                         title="Monthly Order Volume Trend", labels={'year_month': 'Month', 'total_orders': 'Total Orders'})
        st.plotly_chart(fig_ord, use_container_width=True)

    st.markdown("---")
    st.subheader("Order Heatmap")
    
    heatmap_data = filtered_df.groupby(['weekday', 'hour'])['order_id'].nunique().reset_index(name='orders')
    
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    # Pivot for imshow
    heatmap_pivot = heatmap_data.pivot(index='weekday', columns='hour', values='orders').reindex(days_order)
    
    fig_heat = px.imshow(heatmap_pivot, aspect='auto', color_continuous_scale='Viridis',
                         title="Order Volume by Weekday and Hour",
                         labels=dict(x="Hour of Day", y="Day of Week", color="Orders"))
    st.plotly_chart(fig_heat, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Revenue Distribution")
    fig_hist_rev = px.histogram(filtered_df, x='revenue', nbins=50, 
                                title="Revenue Distribution (Histogram)",
                                labels={'revenue': 'Revenue ($)'},
                                color_discrete_sequence=['green'])
    # Cap at 99th percentile for readability
    fig_hist_rev.update_xaxes(range=[0, filtered_df['revenue'].quantile(0.99)])
    st.plotly_chart(fig_hist_rev, use_container_width=True)

# --- Tab 2: Customer Behavior ---
with tab2:
    st.subheader("Customer Insights")
    c1, c2 = st.columns(2)
    
    with c1:
        # Orders per customer distribution
        # Most customers have 1 order, so let's clip it or use discrete bins
        counts_df = customer_order_counts.value_counts().reset_index()
        counts_df.columns = ['Orders per Customer', 'Number of Customers']
        counts_df = counts_df.sort_values('Orders per Customer')
        # To avoid long tails, let's group anything >= 5
        counts_df['Orders per Customer'] = counts_df['Orders per Customer'].apply(lambda x: str(x) if x < 5 else '5+')
        grouped_counts = counts_df.groupby('Orders per Customer')['Number of Customers'].sum().reset_index()
        # Sort again correctly
        sort_dict = {'1': 1, '2': 2, '3': 3, '4': 4, '5+': 5}
        grouped_counts['sort_key'] = grouped_counts['Orders per Customer'].map(sort_dict)
        grouped_counts = grouped_counts.sort_values('sort_key')
        
        fig_hist = px.bar(grouped_counts, x='Orders per Customer', y='Number of Customers',
                          title="Orders per Customer Distribution")
        st.plotly_chart(fig_hist, use_container_width=True)

        # Revenue Split: Repeat vs One-Time
        cust_types = pd.DataFrame(customer_order_counts).reset_index()
        cust_types.columns = ['customer_unique_id', 'order_count']
        cust_types['Customer Type'] = cust_types['order_count'].apply(lambda x: 'Repeat' if x > 1 else 'One-Time')
        
        # Merge type back to main df to sum revenue
        rev_by_cust = filtered_df.groupby('customer_unique_id')['revenue'].sum().reset_index()
        rev_by_cust = rev_by_cust.merge(cust_types[['customer_unique_id', 'Customer Type']], on='customer_unique_id')
        
        rev_split = rev_by_cust.groupby('Customer Type')['revenue'].sum().reset_index()
        
        fig_pie_type = px.pie(rev_split, names='Customer Type', values='revenue', hole=0.4,
                              title="Revenue Split: Repeat vs One-Time Customers",
                              color='Customer Type', color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie_type, use_container_width=True)

    with c2:
        # Payment Method Breakdown
        payment_totals = filtered_payments.groupby('payment_type')['payment_value'].sum().reset_index()
        fig_pay = px.pie(payment_totals, names='payment_type', values='payment_value', hole=0.4,
                         title="Revenue Breakdown by Payment Method")
        st.plotly_chart(fig_pay, use_container_width=True)
        
        # Top states by revenue
        state_rev = filtered_df.groupby('customer_state')['revenue'].sum().reset_index()
        state_rev = state_rev.sort_values('revenue', ascending=False).head(10)
        
        fig_state = px.bar(state_rev, x='customer_state', y='revenue',
                           title="Top 10 States by Revenue",
                           labels={'customer_state': 'State', 'revenue': 'Total Revenue ($)'})
        st.plotly_chart(fig_state, use_container_width=True)

    st.markdown("---")
    st.subheader("Top Customers & Cities")
    c3, c4 = st.columns(2)
    
    with c3:
        # Top 10 Customers
        top_cust = filtered_df.groupby('customer_unique_id')['revenue'].sum().reset_index()
        top_cust = top_cust.sort_values('revenue', ascending=False).head(10)
        top_cust['customer_unique_id'] = top_cust['customer_unique_id'].str[:8] + '...' # shorten id
        fig_cust = px.bar(top_cust, x='customer_unique_id', y='revenue',
                          title="Top 10 Customers by Revenue",
                          labels={'customer_unique_id': 'Customer ID', 'revenue': 'Total Revenue ($)'})
        st.plotly_chart(fig_cust, use_container_width=True)
        
    with c4:
        # Top 10 Cities
        city_rev = filtered_df.groupby('customer_city')['revenue'].sum().reset_index()
        city_rev = city_rev.sort_values('revenue', ascending=False).head(10)
        fig_city = px.bar(city_rev, x='customer_city', y='revenue',
                          title="Top 10 Cities by Revenue",
                          labels={'customer_city': 'City', 'revenue': 'Total Revenue ($)'})
        st.plotly_chart(fig_city, use_container_width=True)

# --- Tab 3: Products ---
with tab3:
    st.subheader("Product & Category Performance")
    
    c1, c2 = st.columns(2)
    
    # Aggregate category stats
    cat_stats = filtered_df.groupby('product_category_name').agg(
        Total_Revenue=('revenue', 'sum'),
        Total_Orders=('order_id', 'nunique'),
        Average_Rating=('review_score', 'mean')
    ).reset_index().sort_values('Total_Revenue', ascending=False)
    
    with c1:
        st.markdown("**Top Selling Categories (Table)**")
        st.dataframe(cat_stats.head(50), use_container_width=True)
        
    with c2:
        # Treemap for category revenue
        top_cats = cat_stats.head(20).copy()
        top_cats['Total_Revenue'] = top_cats['Total_Revenue'].round(2)
        fig_tree = px.treemap(top_cats, path=[px.Constant("All Categories"), 'product_category_name'], 
                              values='Total_Revenue', title="Top 20 Categories by Revenue (Treemap)")
        st.plotly_chart(fig_tree, use_container_width=True)
        
    st.markdown("---")
    
    st.subheader("Top Products & Ratings")
    c3, c4 = st.columns(2)
    
    with c3:
        # Top 10 Products by Revenue
        top_prods = filtered_df.groupby('product_id')['revenue'].sum().reset_index()
        top_prods = top_prods.sort_values('revenue', ascending=False).head(10)
        top_prods['product_id'] = top_prods['product_id'].str[:8] + '...' # shorten id
        fig_prod = px.bar(top_prods, x='revenue', y='product_id', orientation='h',
                          title="Top 10 Products by Revenue",
                          labels={'product_id': 'Product ID', 'revenue': 'Revenue ($)'})
        fig_prod.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_prod, use_container_width=True)
        
    with c4:
        # Price vs Review Score Scatter Plot
        # Aggregate at product level
        prod_stats = filtered_df.groupby('product_id').agg(
            Average_Price=('price', 'mean'),
            Average_Rating=('review_score', 'mean'),
            Orders=('order_id', 'nunique'),
            Category=('product_category_name', 'first')
        ).reset_index()
        
        # Filter out products with very few orders to reduce noise in ratings
        min_orders_for_rating = 5
        prod_scatter = prod_stats[prod_stats['Orders'] >= min_orders_for_rating]
        
        if not prod_scatter.empty:
            fig_scatter = px.scatter(prod_scatter, x='Average_Price', y='Average_Rating', 
                                     size='Orders', color='Category', hover_name='product_id',
                                     title=f"Price vs Average Review Score (Products with >= {min_orders_for_rating} orders)",
                                     labels={'Average_Price': 'Average Price ($)', 'Average_Rating': 'Average Review Score'})
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("Not enough data to display Price vs Review Score scatter plot (requires products with at least 5 orders).")

# --- Tab 4: Correlation & Profit ---
with tab4:
    st.subheader("Profit Analysis & Correlations")
    
    c1, c2 = st.columns(2)
    
    with c1:
        if 'approx_profit' in filtered_df.columns:
            profit_stats = filtered_df.groupby('product_category_name')['approx_profit'].sum().reset_index()
            profit_stats = profit_stats.sort_values('approx_profit', ascending=False).head(15)
            fig_profit = px.bar(profit_stats, x='approx_profit', y='product_category_name', orientation='h',
                                title="Top 15 Categories by Approx. Profit",
                                labels={'approx_profit': 'Approx. Profit ($)', 'product_category_name': 'Category'})
            fig_profit.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_profit, use_container_width=True)
        else:
            st.info("Profit data not available.")
            
    with c2:
        numeric_cols = ['price', 'freight_value', 'review_score', 'delivery_days', 'approx_profit_margin']
        valid_cols = [c for c in numeric_cols if c in filtered_df.columns]
        
        if len(valid_cols) > 1:
            corr_matrix = filtered_df[valid_cols].corr()
            fig_corr = px.imshow(corr_matrix, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu_r",
                                 title="Correlation Heatmap (Numeric Variables)")
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.info("Not enough numeric columns for correlation heatmap.")
