class Student:
    def __init__(self, studentId, name, age, course, email):
        self.studentId = studentId
        self.name = name
        self.age = age
        self.course = course
        self.email = email

    def __str__(self):
        return f"{self.studentId},{self.name},{self.age},{self.course},{self.email}"