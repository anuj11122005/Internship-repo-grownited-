from StudentManager import StudentManager

manager = StudentManager()
manager.loadFromFile()

while True:
    print("\n===== STUDENT MANAGEMENT SYSTEM =====")
    print("1. Add Student")
    print("2. Search Student")
    print("3. Delete Student")
    print("4. Display Students")
    print("5. Save Data")
    print("6. Exit")

    choice = int(input("Enter Choice: "))

    if choice == 1:
        manager.addStudent()

    elif choice == 2:
        manager.searchStudent()

    elif choice == 3:
        manager.deleteStudent()

    elif choice == 4:
        manager.displayStudents()

    elif choice == 5:
        manager.saveToFile()

    elif choice == 6:
        manager.saveToFile()
        print("Exiting Program...")
        break

    else:
        print("Invalid Choice!")