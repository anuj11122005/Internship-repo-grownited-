import numpy as np

vector = np.random.randint(1, 1000, 50)

print("Generated Vector:")
print(vector)

sorted_vector = np.sort(vector)

smallest_3 = sorted_vector[:3]

largest_3 = sorted_vector[-3:]

print("\nSmallest 3 values:", smallest_3)
print("Largest 3 values:", largest_3)