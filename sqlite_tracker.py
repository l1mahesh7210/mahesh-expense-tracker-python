
import sqlite3
import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "expenses.db")
JSON_FILE = os.path.join(BASE_DIR, "expenses.json")


# ============== DATABASE CONNECTION ==============

def connect_db():
    return sqlite3.connect(DB_NAME)


# ============== CREATE DATABASE ==============

def initialize_database():
    try:
        with connect_db() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    date TEXT NOT NULL
                )
            """)

        print("Database initialized successfully!")
        print("Database location:", DB_NAME)

        import_json_data()

    except sqlite3.Error as error:
        print("Database error:", error)


# ============== IMPORT JSON DATA ==============

def import_json_data():
    if not os.path.exists(JSON_FILE):
        print("No old JSON file found. Starting with empty database.")
        return

    try:
        with connect_db() as conn:

            count = conn.execute(
                "SELECT COUNT(*) FROM expenses"
            ).fetchone()[0]

            if count > 0:
                print("Database already has data. Import skipped.")
                return

            with open(JSON_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, list):
                print("Invalid JSON data.")
                return

            imported = 0

            for item in data:
                if not isinstance(item, dict):
                    continue

                amount = item.get("amount")
                category = item.get("category")
                description = item.get("description")
                date = item.get("date") or datetime.now().strftime("%Y-%m-%d")

                if amount is None or not category or not description:
                    continue

                try:
                    amount = float(amount)
                    datetime.strptime(date, "%Y-%m-%d")

                    if amount <= 0:
                        continue

                    conn.execute("""
                        INSERT INTO expenses
                        (amount, category, description, date)
                        VALUES (?, ?, ?, ?)
                    """, (amount, category, description, date))

                    imported += 1

                except (ValueError, sqlite3.Error):
                    continue

            print(f"Imported {imported} expenses from JSON.")

    except (OSError, json.JSONDecodeError, sqlite3.Error) as error:
        print("Import error:", error)


# ============== ADD EXPENSE ==============

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

        date = datetime.now().strftime("%Y-%m-%d")

        with connect_db() as conn:
            conn.execute("""
                INSERT INTO expenses (amount, category, description, date)
                VALUES (?, ?, ?, ?)
            """, (amount, category, description, date))

        print("Expense added successfully!")

    except ValueError:
        print("Enter a valid amount.")

    except sqlite3.Error as error:
        print("Database error:", error)


# ============== VIEW EXPENSES ==============

def view_expenses():
    with connect_db() as conn:
        rows = conn.execute("""
            SELECT id, amount, category, description, date
            FROM expenses
            ORDER BY id
        """).fetchall()

    if not rows:
        print("No expenses found.")
        return

    for row in rows:
        print(f"\nID: {row[0]}")
        print(f"Amount: ₹{row[1]:.2f}")
        print(f"Category: {row[2]}")
        print(f"Description: {row[3]}")
        print(f"Date: {row[4]}")


# ============== TOTAL EXPENSES ==============

def calculate_total():
    with connect_db() as conn:
        total = conn.execute(
            "SELECT SUM(amount) FROM expenses"
        ).fetchone()[0]

    print(f"Total Expenses: ₹{total or 0:.2f}")


# ============== SEARCH CATEGORY ==============

def search_expenses():
    category = input("Enter category: ").strip()

    with connect_db() as conn:
        rows = conn.execute("""
            SELECT id, amount, category, description, date
            FROM expenses
            WHERE category = ? COLLATE NOCASE
            ORDER BY id
        """, (category,)).fetchall()

    if not rows:
        print("Category not found.")
        return

    for row in rows:
        print(f"\nID: {row[0]}")
        print(f"Amount: ₹{row[1]:.2f}")
        print(f"Category: {row[2]}")
        print(f"Description: {row[3]}")
        print(f"Date: {row[4]}")


# ============== DELETE EXPENSE ==============

def delete_expense():
    view_expenses()

    try:
        expense_id = int(input("Enter expense ID to delete: "))

        with connect_db() as conn:
            cursor = conn.execute(
                "DELETE FROM expenses WHERE id = ?",
                (expense_id,)
            )

        if cursor.rowcount > 0:
            print("Expense deleted successfully!")
        else:
            print("Expense ID not found.")

    except ValueError:
        print("Enter a valid ID.")

    except sqlite3.Error as error:
        print("Database error:", error)


# ============== EDIT EXPENSE ==============

def edit_expense():
    view_expenses()

    try:
        expense_id = int(input("Enter expense ID to edit: "))

        with connect_db() as conn:
            row = conn.execute("""
                SELECT amount, category, description, date
                FROM expenses WHERE id = ?
            """, (expense_id,)).fetchone()

        if row is None:
            print("Expense not found.")
            return

        print("Leave blank to keep the old value.")

        amount = input(f"Amount [{row[0]}]: ").strip()
        category = input(f"Category [{row[1]}]: ").strip()
        description = input(f"Description [{row[2]}]: ").strip()
        date = input(f"Date [{row[3]}]: ").strip()

        new_amount = float(amount) if amount else row[0]
        new_category = category if category else row[1]
        new_description = description if description else row[2]
        new_date = date if date else row[3]

        if new_amount <= 0:
            print("Amount must be greater than zero.")
            return

        datetime.strptime(new_date, "%Y-%m-%d")

        with connect_db() as conn:
            conn.execute("""
                UPDATE expenses
                SET amount = ?, category = ?, description = ?, date = ?
                WHERE id = ?
            """, (
                new_amount,
                new_category,
                new_description,
                new_date,
                expense_id
            ))

        print("Expense updated successfully!")

    except ValueError:
        print("Invalid amount or date. Use YYYY-MM-DD.")

    except sqlite3.Error as error:
        print("Database error:", error)


# ============== CATEGORY REPORT ==============

def category_report():
    with connect_db() as conn:
        rows = conn.execute("""
            SELECT category, SUM(amount)
            FROM expenses
            GROUP BY category
            ORDER BY SUM(amount) DESC
        """).fetchall()

    print("\n===== CATEGORY REPORT =====")

    if not rows:
        print("No expenses found.")
        return

    for category, total in rows:
        print(f"{category}: ₹{total:.2f}")


# ============== MONTHLY REPORT ==============

def monthly_report():
    with connect_db() as conn:
        rows = conn.execute("""
            SELECT SUBSTR(date, 1, 7), SUM(amount)
            FROM expenses
            GROUP BY SUBSTR(date, 1, 7)
            ORDER BY SUBSTR(date, 1, 7) DESC
        """).fetchall()

    print("\n===== MONTHLY REPORT =====")

    if not rows:
        print("No expenses found.")
        return

    for month, total in rows:
        print(f"{month}: ₹{total:.2f}")


# ============== BUDGET ALERT ==============

def budget_alert():
    try:
        budget = float(input("Enter monthly budget: ₹"))

        if budget <= 0:
            print("Budget must be greater than zero.")
            return

        month = datetime.now().strftime("%Y-%m")

        with connect_db() as conn:
            total = conn.execute("""
                SELECT SUM(amount)
                FROM expenses
                WHERE date LIKE ?
            """, (month + "%",)).fetchone()[0] or 0

        remaining = budget - total

        print("\n===== BUDGET REPORT =====")
        print(f"Budget: ₹{budget:.2f}")
        print(f"Spent: ₹{total:.2f}")

        if remaining < 0:
            print(f"Over budget by ₹{abs(remaining):.2f}")
        else:
            print(f"Remaining: ₹{remaining:.2f}")

            if total >= budget * 0.8:
                print("WARNING: 80% of your budget has been used!")

    except ValueError:
        print("Enter a valid budget.")

    except sqlite3.Error as error:
        print("Database error:", error)


# ============== EXPENSE SUMMARY ==============

def expense_summary():
    with connect_db() as conn:
        row = conn.execute("""
            SELECT COUNT(*), SUM(amount), MAX(amount), AVG(amount)
            FROM expenses
        """).fetchone()

    count, total, highest, average = row

    print("\n===== EXPENSE SUMMARY =====")
    print("Transactions:", count)
    print(f"Total: ₹{total or 0:.2f}")
    print(f"Highest: ₹{highest or 0:.2f}")
    print(f"Average: ₹{average or 0:.2f}")


# ============== MAIN MENU ==============

def main():
    initialize_database()

    while True:
        print("\n===== SQLITE EXPENSE TRACKER =====")
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
            print("Thank you!")
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
