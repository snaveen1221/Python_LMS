import csv
from datetime import datetime
from pathlib import Path

EXPENSES_FILE = Path("expenses.csv")

# Global variables to hold expenses and budget
expenses = []
monthly_budget = None


def add_expense():
    try:
        date_str = input("Enter date (YYYY-MM-DD): ").strip()
        # Validate date format
        datetime.strptime(date_str, "%Y-%m-%d")

        category = input("Enter category (e.g., Food, Travel): ").strip()
        if not category:
            print("Category cannot be empty.")
            return

        amount_str = input("Enter amount spent: ").strip()
        amount = float(amount_str)
        if amount < 0:
            print("Amount cannot be negative.")
            return

        description = input("Enter description: ").strip()
        if not description:
            print("Description cannot be empty.")
            return

        expense = {
            "date": date_str,
            "category": category,
            "amount": amount,
            "description": description,
        }
        expenses.append(expense)
        print("Expense added successfully.\n")

    except ValueError as e:
        print(f"Invalid input: {e}\n")


def view_expenses():
    if not expenses:
        print("No expenses recorded.\n")
        return

    print(f"\n{'Date':<12} | {'Category':<15} | {'Amount':<10} | Description")
    print("-" * 60)
    for exp in expenses:
        # Validate required fields
        if not all(
            key in exp and exp[key] != "" and exp[key] is not None
            for key in ("date", "category", "amount", "description")
        ):
            print("Skipping incomplete expense entry.")
            continue
        print(
            f"{exp['date']:<12} | {exp['category']:<15} | €{exp['amount']:<9.2f} | {exp['description']}"
        )
    print()


def set_budget():
    global monthly_budget
    try:
        amount_str = input("Enter your monthly budget amount: ").strip()
        amount = float(amount_str)
        if amount < 0:
            print("Budget cannot be negative.\n")
            return
        monthly_budget = amount
        print(f"Monthly budget set to €{monthly_budget:.2f}\n")
    except ValueError:
        print("Invalid amount. Please enter a number.\n")


def track_budget():
    if monthly_budget is None:
        print("Monthly budget is not set yet.\n")
        return
    total_spent = sum(exp["amount"] for exp in expenses)
    print(f"Total expenses so far: €{total_spent:.2f}")
    if total_spent > monthly_budget:
        print("Warning: You have exceeded your budget!\n")
    else:
        remaining = monthly_budget - total_spent
        print(f"You have €{remaining:.2f} left for the month.\n")


def save_expenses():
    with open(EXPENSES_FILE, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(["date", "category", "amount", "description"])
        # Write all expenses
        for exp in expenses:
            writer.writerow([exp["date"], exp["category"], exp["amount"], exp["description"]])
    print(f"Expenses saved to '{EXPENSES_FILE}'.\n")


def load_expenses():
    if not EXPENSES_FILE.exists():
        return
    with open(EXPENSES_FILE, mode="r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Convert amount string to float
            try:
                amount = float(row["amount"])
                expense = {
                    "date": row["date"],
                    "category": row["category"],
                    "amount": amount,
                    "description": row["description"],
                }
                expenses.append(expense)
            except (ValueError, KeyError):
                print("Skipping invalid row in expenses file.")


def main():
    load_expenses()

    while True:
        print("==== Personal Expense Tracker ====")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Track Budget")
        print("4. Save Expenses")
        print("5. Exit")
        choice = input("Select an option: ").strip()

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            if monthly_budget is None:
                set_budget()
            else:
                track_budget()
        elif choice == "4":
            save_expenses()
        elif choice == "5":
            save_expenses()
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.\n")


if __name__ == "__main__":
    main()
