
import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_NAME = os.path.join(BASE_DIR, "expenses.json")


def load_expenses():
    if not os.path.exists(FILE_NAME):
        return []

    try:
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            return []

        valid = []

        for item in data:
            if isinstance(item, dict) and "amount" in item:
                valid.append(item)

        return valid

    except (json.JSONDecodeError, OSError):
        print("Could not load expenses.")
        return []


expenses = load_expenses()


def save_expenses():
    try:
        with open(FILE_NAME, "w", encoding="utf-8") as file:
            json.dump(expenses, file, indent=4)
        return True
    except OSError:
        print("Could not save expenses.")
        return False


def add_expense():
    try:
        amount = float(input("Enter amount: "))
        if amount <= 0:
            print("Amount must be greater than zero.")
            return

        category = input("Enter category: ").strip()
        description = input("Enter description: ").strip()

        if not category or not description:
            print("Category and description are required.")
            return

        expense = {
            "amount": amount,
            "category": category,
            "description": description,
            "date": datetime.now().strftime("%Y-%m-%d")
            }

        expenses.append(expense)

        if save_expenses():
            print("Expense added successfully!")
        else:
            expenses.pop()

    except ValueError:
        print("Invalid amount.")


def view_expenses():
    if not expenses:
        print("No expenses found.")
        return

    for i, expense in enumerate(expenses, start=1):
        print(f"\nExpense {i}")
        print("Amount:", expense.get("amount", 0))
        print("Category:", expense.get("category", "Unknown"))
        print("Description:", expense.get("description", ""))
        print("Date:", expense.get("date", "Not recorded"))


def calculate_total():
    total = sum(
        expense.get("amount", 0)
        for expense in expenses
    )
    print(f"Total Expenses: ₹{total:.2f}")


def search_expenses():
    category = input("Enter category: ").strip().lower()
    found = False

    for i, expense in enumerate(expenses, start=1):
        if expense.get("category", "").lower() == category:
            print(f"\nExpense {i}")
            print(expense)
            found = True

    if not found:
        print("Category not found.")


def delete_expense():
    view_expenses()

    if not expenses:
        return

    try:
        number = int(input("Enter expense number to delete: "))

        if 1 <= number <= len(expenses):
            deleted = expenses.pop(number - 1)

            if save_expenses():
                print("Expense deleted.")
            else:
                expenses.insert(number - 1, deleted)
        else:
            print("Invalid number.")

    except ValueError:
        print("Enter a valid number.")


def edit_expense():
    view_expenses()

    if not expenses:
        return

    try:
        number = int(input("Enter expense number to edit: "))

        if not 1 <= number <= len(expenses):
            print("Invalid number.")
            return

        expense = expenses[number - 1]
        old = expense.copy()

        amount = input(f"Amount [{expense.get('amount', 0)}]: ").strip()
        category = input(f"Category [{expense.get('category', '')}]: ").strip()
        description = input(f"Description [{expense.get('description', '')}]: ").strip()
        date = input(f"Date [{expense.get('date', '')}]: ").strip()

        if amount:
            new_amount = float(amount)
            if new_amount <= 0:
                print("Amount must be greater than zero.")
                return
        else:
            new_amount = expense.get("amount", 0)

        if date:
            datetime.strptime(date, "%Y-%m-%d")

        expense["amount"] = new_amount
        expense["category"] = category or expense.get("category", "")
        expense["description"] = description or expense.get("description", "")
        expense["date"] = date or expense.get("date", "")

        if save_expenses():
            print("Expense updated!")
        else:
            expenses[number - 1] = old

    except ValueError:
        print("Invalid amount, number, or date.")


def category_report():
    totals = {}

    for expense in expenses:
        category = expense.get("category", "Unknown")
        amount = expense.get("amount", 0)
        totals[category] = totals.get(category, 0) + amount

    print("\n===== CATEGORY REPORT =====")
    for category, amount in totals.items():
        print(f"{category}: ₹{amount:.2f}")


def monthly_report():
    totals = {}

    for expense in expenses:
        month = expense.get("date", "Unknown")[:7]
        totals[month] = totals.get(month, 0) + expense.get("amount", 0)

    print("\n===== MONTHLY REPORT =====")
    for month, amount in sorted(totals.items(), reverse=True):
        print(f"{month}: ₹{amount:.2f}")


def budget_alert():
    try:
        budget = float(input("Enter monthly budget: ₹"))
        month = datetime.now().strftime("%Y-%m")

        spent = sum(
            expense.get("amount", 0)
            for expense in expenses
            if expense.get("date", "").startswith(month)
        )

        remaining = budget - spent

        print(f"Budget: ₹{budget:.2f}")
        print(f"Spent: ₹{spent:.2f}")

        if remaining < 0:
            print(f"Over budget by ₹{abs(remaining):.2f}")
        else:
            print(f"Remaining: ₹{remaining:.2f}")

            if spent >= budget * 0.8:
                print("Warning: 80% of budget used!")

    except ValueError:
        print("Invalid budget.")


def expense_summary():
    if not expenses:
        print("No expenses.")
        return

    amounts = [e.get("amount", 0) for e in expenses]
    total = sum(amounts)

    print("\n===== EXPENSE SUMMARY =====")
    print("Transactions:", len(expenses))
    print(f"Total: ₹{total:.2f}")
    print(f"Highest: ₹{max(amounts):.2f}")
    print(f"Average: ₹{total / len(amounts):.2f}")


def main():
    while True:
        print("\n===== JSON EXPENSE TRACKER =====")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Total Expenses")
        print("4. Exit")
        print("5. Search Category")
        print("6. Delete Expense")
        print("7. Edit Expense")
        print("8. Category Report")
        print("9. Monthly Report")
        print("10. Budget Alert")
        print("11. Expense Summary")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            calculate_total()
        elif choice == "4":
            break
        elif choice == "5":
            search_expenses()
        elif choice == "6":
            delete_expense()
        elif choice == "7":
            edit_expense()
        elif choice == "8":
            category_report()
        elif choice == "9":
            monthly_report()
        elif choice == "10":
            budget_alert()
        elif choice == "11":
            expense_summary()
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
