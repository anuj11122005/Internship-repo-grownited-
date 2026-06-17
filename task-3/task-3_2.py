import pandas as pd

df = pd.read_csv("inventory.csv")

print("Inventory Data:")
print (df)

# Find total stock.
total_stock = df['Stock'].sum()
print("\n Total Stock :", total_stock)

# Find product with highest stock.
highest_stock = df['Stock'].max()
product_highest_stock = df[df["Stock"] == highest_stock]
print("\n Product with Highest Stock\n", product_highest_stock)

# Find product with lowest stock.
lowest_stock = df['Stock'].min()
product_lowest_stock = df[df['Stock'] == lowest_stock]
print("\n Product with Lowest Stock :\n", product_lowest_stock)

# Calculate category-wise stock.
category_stock = df.groupby('Category')['Stock'].sum()
print("\nCategory-wise Stock of product:\n", category_stock)

# Display products with stock less than 10.
product_less_stock = df[df['Stock']<10]
print("\n Product with Stock less than 10:\n", product_less_stock)

# Sort products by stock.
sort_product = df.sort_values(by='Stock', ascending=False)
print("\nProduct sorted With there Stock:")
print(sort_product)

# Generate inventory report.
print("\n==============================")
print("INVENTORY REPORT")

print("Total Stock:", total_stock)
print("Highest Stock Product:", product_highest_stock["Product"].values[0])
print("Lowest Stock Product:", product_lowest_stock["Product"].values[0])

print("\nCategory-wise Stock:")
print(category_stock)

print("\nLow Stock Products:")
print(product_less_stock["Product"].values)

print("==============================")