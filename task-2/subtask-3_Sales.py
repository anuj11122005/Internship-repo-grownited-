import random

# with open("sales.txt", "w") as file:
#     for _ in range(12):
#         sale = random.randint(10000, 50000)
#         file.write(str(sale) + "\n")

sales = []

with open("sales.txt", "r") as file:
    for line in file:
        sales.append(float(line.strip()))

q1 = sum(sales[0:3])
q2 = sum(sales[3:6])
q3 = sum(sales[6:9])
q4 = sum(sales[9:12])

quarters = [q1, q2, q3, q4]

max_sales = max(quarters)
highest_quarter = quarters.index(max_sales) + 1

print("Sales:", sales)
print("Quarter Sales:", quarters)
print("Highest Sales:", max_sales)
print("Quarter with Highest Sales: Q", highest_quarter)