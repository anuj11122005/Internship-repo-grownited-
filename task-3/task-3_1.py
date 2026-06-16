import pandas as pd

df = pd.read_csv("employee.csv")

print("All Employees:")
print(df)

max_salary = df["Salary"].max()
highest_paid = df[df["Salary"] == max_salary]
print("\nHighest Paid Employee:")
print(highest_paid)


min_salary = df['Salary'].min()
lowest_paid = df[df['Salary'] == min_salary]
print("\nlowest Paid Employee:")
print(lowest_paid)

average_salary = df["Salary"].mean()
print("Average Salary of employees:" , average_salary)

above_avg_salary = df[df["Salary"] > average_salary]
print("\n Employees earnig above Average Salary :\n" , above_avg_salary)

dept_avg_salary = df.groupby('Department')['Salary'].mean()
print("\n Department-wise Average Salary :\n", dept_avg_salary)

count_emp_dept = df.groupby('Department')['EmpID'].count()
print("\n Count of Employees per Department:\n", count_emp_dept)

sort_emp_salary = df.sort_values(by="Salary", ascending=False)
print("\n Employees Sorted with there Salary:\n" )
print(sort_emp_salary)