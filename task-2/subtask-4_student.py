import numpy as np

students = np.array([
    "Amit","Neha","Rahul","Priya",
    "Karan","Sneha","Jay","Riya"
])

marks = np.array([45, 78, 92, 67, 55, 88, 34, 95])

print("Student Data:")
for i in range(len(students)):
    print(students[i], ":", marks[i])

total = np.sum(marks)
print("\nTotal Marks =", total)

average = np.mean(marks)
print("Average Marks =", round(average, 2))

max_marks = np.max(marks)
topper = students[np.argmax(marks)]
print("\nHighest Marks =", max_marks)
print("Topper =", topper)

min_marks = np.min(marks)
lowest = students[np.argmin(marks)]
print("\nLowest Marks =", min_marks)
print("Student =", lowest)

passing_marks = 40
passed = students[marks >= passing_marks]
failed = students[marks < passing_marks]

print("\nPassed Students:")
for s in passed:
    print(s)

print("\nFailed Students:")
for s in failed:
    print(s)

above_avg = students[marks > average]
print("\nStudents Above Average:")
for s in above_avg:
    print(s)

print("\nGrades:")
for i in range(len(marks)):
    if marks[i] >= 90:
        grade = "A"
    elif marks[i] >= 75:
        grade = "B"
    elif marks[i] >= 60:
        grade = "C"
    elif marks[i] >= 40:
        grade = "D"
    else:
        grade = "F"
    print(students[i], ":", grade)

sorted_indices = np.argsort(marks)[::-1]
top3_indices = sorted_indices[:3]

print("\nTop 3 Students:")
for i in top3_indices:
    print(students[i], marks[i])

median = np.median(marks)
std_dev = np.std(marks)

print("\nClass Statistics")
print("Highest Marks :", max_marks)
print("Lowest Marks :", min_marks)
print("Average Marks :", round(average, 2))
print("Median Marks :", median)
print("Standard Deviation :", round(std_dev, 2))

pass_percentage = (len(passed) / len(students)) * 100
scholarship = students[marks >= 85]

print("\n==================================")
print("STUDENT PERFORMANCE REPORT")
print("Total Students :", len(students))

print("\nHighest Marks :", max_marks)
print("Topper :", topper)

print("\nLowest Marks :", min_marks)
print("Lowest Performer :", lowest)

print("\nAverage Marks :", round(average, 2))
print("\nPass Percentage :", round(pass_percentage, 2), "%")

print("\nScholarship Students :")
for s in scholarship:
    print(s)

print("\nTop 3 Students :")
for i in top3_indices:
    print(students[i], "-", marks[i])

print("==================================")
print("END OF REPORT")