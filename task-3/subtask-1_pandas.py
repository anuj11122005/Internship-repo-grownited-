import pandas as pd

df = pd.read_csv("student.csv")

print("All Students:")
print(df)

max_marks = df["Marks"].max()
print("\nHighest Marks:", max_marks)

min_marks = df["Marks"].min()
print("Lowest Marks:", min_marks)

avg_marks = df["Marks"].mean()
print("Average Marks:", round(avg_marks, 2))

above_80 = df[df["Marks"] > 80]
print("\nStudents scoring above 80:")
print(above_80[["Name", "Marks"]])

below_avg = df[df["Marks"] < avg_marks]
print("\nStudents scoring below average:")
print(below_avg[["Name", "Marks"]])

pass_students = df[df["Marks"] >= 40]
fail_students = df[df["Marks"] < 40]

print("\nPass Students:", len(pass_students))
print("Fail Students:", len(fail_students))

sorted_df = df.sort_values(by="Marks", ascending=False)
print("\nStudents sorted by marks (descending):")
print(sorted_df[["Name", "Marks"]])