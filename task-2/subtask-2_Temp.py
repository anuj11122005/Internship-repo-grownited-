import random

# with open("temps.txt", "w") as file:
#     for _ in range(30):
#         temp = random.uniform(20, 45)
#         file.write(str(round(temp, 2)) + "\n")

temperatures = []

with open("temps.txt", "r") as file:
    for line in file:
        temperatures.append(float(line.strip()))

max_temp = max(temperatures)
hottest_day = temperatures.index(max_temp) + 1

print("Temperatures:", temperatures)
print("Hottest Temperature:", max_temp)
print("Hottest Day:", hottest_day)
