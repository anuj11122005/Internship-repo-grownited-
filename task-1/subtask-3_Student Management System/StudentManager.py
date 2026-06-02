from Student import Student

class StudentManager:
    def __init__(self):
        self.students = []

    # Add Student
    def addStudent(self):
        try:
            studentId = int(input("Enter Student ID: "))

            # Check unique ID
            for s in self.students:
                if s.studentId == studentId:
                    print("Error: Student ID must be unique!")
                    return

            name = input("Enter Name: ")
            if name == "":
                print("Error: Name cannot be empty!")
                return

            age = int(input("Enter Age: "))
            if age <= 0:
                print("Error: Age must be greater than 0!")
                return

            course = input("Enter Course: ")

            email = input("Enter Email: ")
            if "@" not in email:
                print("Error: Invalid Email!")
                return

            student = Student(studentId, name, age, course, email)
            self.students.append(student)

            print("Student Added Successfully!")

        except Exception as e:
            print("Invalid Input!", e)

    # Search Student
    def searchStudent(self):
        studentId = int(input("Enter Student ID: "))

        for s in self.students:
            if s.studentId == studentId:
                print("\nStudent Found")
                print("ID     :", s.studentId)
                print("Name   :", s.name)
                print("Age    :", s.age)
                print("Course :", s.course)
                print("Email  :", s.email)
                return

        print("Student Not Found")

    # Delete Student
    def deleteStudent(self):
        studentId = int(input("Enter Student ID: "))

        for s in self.students:
            if s.studentId == studentId:
                self.students.remove(s)
                print("Student Deleted Successfully")
                return

        print("Student Not Found")

    # Display All Students
    def displayStudents(self):
        if len(self.students) == 0:
            print("No Records Found!")
            return

        print("\n------ STUDENT LIST ------")
        for s in self.students:
            print("---------------------------------")
            print("ID :", s.studentId)
            print("Name :", s.name)
            print("Course :", s.course)
        print("---------------------------------")

    # Save to File
    def saveToFile(self):
        with open("students.txt", "w") as file:
            for s in self.students:
                file.write(str(s) + "\n")
        print("Data Saved Successfully!")

    # Load from File
    def loadFromFile(self):
        try:
            with open("students.txt", "r") as file:
                for line in file:
                    data = line.strip().split(",")
                    student = Student(int(data[0]), data[1], int(data[2]), data[3], data[4])
                    self.students.append(student)
        except FileNotFoundError:
            pass