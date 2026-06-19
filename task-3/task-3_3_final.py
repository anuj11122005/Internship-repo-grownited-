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
low_row = df.loc[df["Revenue"].idxmin()]
print("\nlowest revenue order:")
print("Order ID:",low_row["OrderID"])
print("Revenue:", low_row["Revenue"])

# Task 6: Product Wise Revenue
product_wise_revenue = df.groupby('Product')["Revenue"].sum()
print("Product wise Revenue is:",product_wise_revenue)

# Task 7: Category Wise Revenue
category_wise_revenue = df.groupby('Category')["Revenue"].sum()
print("Category wise Revenue is:",category_wise_revenue)

# Task 8: Customer Wise Revenue
customer_wise_revenue = df.groupby('Customer')["Revenue"].sum()
print("Customer Wise Revenue is:", customer_wise_revenue)

# Task 9: Top Customer
top_customer = customer_wise_revenue.idxmax()
print("\nTop Customer is:")
print(top_customer)
print("Revenue:",customer_wise_revenue.max())

# Task 10: Top Product
top_product = product_wise_revenue.idxmax()
print("\nTop Product is:")
print(top_product)
print("Revenue:",product_wise_revenue.max())

# Task 11: City Wise Revenue
city_wise_revenue = df.groupby('City')["Revenue"].sum()
print("City Wise Revenue is:",city_wise_revenue)

# Task 12: Orders Above Average Revenue
above_avg_order = df[df["Revenue"]>average_revenue]
print("Orders Above the Average Revenue is:")
print(above_avg_order["OrderID"])

# Task 13: Sort Orders by Revenue Descending
sorted_orders = df.sort_values(by="Revenue" , ascending=False)
print("Sort Orders by Revenue Descending is:")
print(sorted_orders["OrderID"],sorted_orders["Revenue"])

# Task 14: Export Reports
customer_report = customer_wise_revenue.reset_index()
customer_report.columns = ["Customer", "Total Revenue"]
customer_report.to_csv("customer_report.csv", index=False)

product_report = product_wise_revenue.reset_index()
product_report.columns = ["Product", "Revenue"]
product_report.to_csv("product_report.csv", index=False)

print("\nReports exported successfully!")


# Task 15: Final Business Report

top_category = category_wise_revenue.idxmax()
top_city = city_wise_revenue.idxmax()

print("\n=========================================")
print("E-COMMERCE SALES REPORT")
print("=========================================")

print("Total Orders :", len(df))
print("Total Revenue :", total_revenue)
print("Average Revenue :", average_revenue)

print("Top Customer :", top_customer)
print("Customer Revenue :", customer_wise_revenue.max())

print("Top Product :", top_product)
print("Product Revenue :", product_wise_revenue.max())

print("Top Category :", top_category)
print("Category Revenue :", category_wise_revenue.max())

print("Top City :", top_city)
print("City Revenue :", city_wise_revenue.max())

print("=========================================")
print("END OF REPORT")
print("=========================================")


# Bonus: Revenue Percentage Contribution

print("\nRevenue Percentage Contribution:")
percentage = (product_wise_revenue / total_revenue) * 100

for product in percentage.index:
    print(product, "=", round(percentage[product], 2), "%")