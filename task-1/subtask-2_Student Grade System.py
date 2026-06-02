# Function to calculate grade
def calculate_grade(marks):
    if marks >= 90:
        return "A+"
    elif marks >= 80:
        return "A"
    elif marks >= 70:
        return "B"
    elif marks >= 60:
        return "C"
    elif marks >= 50:
        return "D"
    else:
        return "Fail"

# Function to calculate result (pass/fail)
def check_result(marks):
    if marks >= 50:
        return "Pass"
    else:
        return "Fail"

# Main Program
print("===== STUDENT GRADE SYSTEM =====")

# Input
name = input("Enter student name: ")
marks = float(input("Enter marks (0-100): "))

# Processing
grade = calculate_grade(marks)
result = check_result(marks)

# Output
print("\n----- RESULT -----")
print("Student Name:", name)
print("Marks:", marks)
print("Grade:", grade)
print("Result:", result)