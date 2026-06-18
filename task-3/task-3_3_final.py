import pandas as pd

df = pd.read_csv('ecom_sales.csv')

print("All Sales on Ecommerce:")
print(df)

# Task 1: Display Dataset Summary
print("\nTotal Records:", len(df))
print("\nTotal columns:", len(df.columns))
print("\nColumns Name:")
for col in df.columns:
    print(col)
print("\nData types:")
print(df.dtypes)

# Task 2: Calculate Total Revenue
df["Revenue"] = df["Quantity"] * df["Price"]
total_revenue = df["Revenue"].sum()
print("\nTotal Revenue from Ecommerce:", total_revenue)

# Task 3: Average Order Revenue
average_revenue = df["Revenue"].mean()
print("\nAverage revenue:", average_revenue)

# Task 4: Highest Revenue Order
# max_revenue = df["Revenue"].max()
# Highest_Revenue_Order = df[df["Revenue"] == max_revenue]
# print("Order with Highest Revenue :", Highest_Revenue_Order)

#Task 4: Highest Revenue Order
max_row = df.loc[df["Revenue"].idxmax()]
print("\nHighest Revenue Order:")
print("Order ID:", max_row["OrderID"])
print("Customer:", max_row["Customer"])
print("Revenue:", max_row["Revenue"])

# Task 5: Lowest Revenue Order
