import csv
import os

FILE = "expenses.csv"

def initialize_file():
    if not os.path.exists(FILE):
        with open(FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Item", "Amount"])

def add_expense():
    item = input("Enter expense item: ")
    amount = input("Enter amount: ")

    with open(FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([item, amount])

    print(f"Added: {item} - ₹{amount}")

def view_expenses():
    total = 0

    with open(FILE, "r") as f:
        reader = csv.reader(f)
        next(reader)

        print("\nExpenses:")

        for row in reader:
            print(f"{row[0]} - ₹{row[1]}")
            total += float(row[1])

    print(f"\nTotal Spent: ₹{total}")

def delete_expense():
    expenses = []

    with open(FILE, "r") as f:
        reader = csv.reader(f)
        header = next(reader)

        for row in reader:
            expenses.append(row)

    for i, expense in enumerate(expenses):
        print(f"{i+1}. {expense[0]} - ₹{expense[1]}")

    choice = int(input("Enter expense number to delete: "))

    if 1 <= choice <= len(expenses):
        expenses.pop(choice - 1)

        with open(FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(expenses)

        print("Expense deleted.")

def main():
    initialize_file()

    while True:
        print("\n--- Expense Tracker ---")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Delete Expense")
        print("4. Exit")

        choice = input("Choose option: ")

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            delete_expense()
        elif choice == "4":
            break
        else:
            print("Invalid choice")

main()