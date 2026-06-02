while True:
    print("\n===== PYTHON CALCULATOR =====")
    print("1. Addition")
    print("2. Subtraction")
    print("3. Multiplication")
    print("4. Division")
    print("5. Modulus")
    print("6. Power")
    print("7. Floor Division")
    print("8. Square")
    print("9. Cube")
    print("10. Square Root")
    print("11. Absolute Value")
    print("12. Maximum of Two Numbers")
    print("13. Minimum of Two Numbers")
    print("14. Even or Odd Check")
    print("15. Percentage")
    print("16. Exit")

    choice = int(input("Enter your choice (1-16): "))

    if choice == 16:
        print("Exiting Calculator...")
        break

    # Two number operations
    if choice in [1,2,3,4,5,6,7,12,13,15]:
        a = float(input("Enter first number: "))
        b = float(input("Enter second number: "))

    # Single number operations
    elif choice in [8,9,10,11,14]:
        a = float(input("Enter a number: "))

    # Operations
    if choice == 1:
        print("Result:", a + b)

    elif choice == 2:
        print("Result:", a - b)

    elif choice == 3:
        print("Result:", a * b)

    elif choice == 4:
        if b != 0:
            print("Result:", a / b)
        else:
            print("Error: Division by zero!")

    elif choice == 5:
        print("Result:", a % b)

    elif choice == 6:
        print("Result:", a ** b)

    elif choice == 7:
        print("Result:", a // b)

    elif choice == 8:
        print("Result:", a ** 2)

    elif choice == 9:
        print("Result:", a ** 3)

    elif choice == 10:
        if a >= 0:
            print("Result:", a ** 0.5)
        else:
            print("Error: Negative number!")

    elif choice == 11:
        print("Result:", abs(a))

    elif choice == 12:
        if a > b:
            print("Maximum:", a)
        else:
            print("Maximum:", b)

    elif choice == 13:
        if a < b:
            print("Minimum:", a)
        else:
            print("Minimum:", b)

    elif choice == 14:
        if a % 2 == 0:
            print("Even Number")
        else:
            print("Odd Number")

    elif choice == 15:
        if b != 0:
            print("Percentage:", (a / b) * 100)
        else:
            print("Error: Division by zero!")

    else:
        print("Invalid Choice!")