import csv
import os
import json
from datetime import datetime
from collections import defaultdict

# ──────────────────────────────────────────────
#  CONFIG
# ──────────────────────────────────────────────
FILE         = "expenses.csv"
BUDGET_FILE  = "budgets.json"
CURRENCY     = "₹"

CATEGORIES = {
    "1": "Food",
    "2": "Travel",
    "3": "Shopping",
    "4": "Bills",
    "5": "Entertainment",
    "6": "Others",
}

CATEGORY_COLORS = {
    "Food":          "\033[92m",   # green
    "Travel":        "\033[94m",   # blue
    "Shopping":      "\033[95m",   # magenta
    "Bills":         "\033[91m",   # red
    "Entertainment": "\033[93m",   # yellow
    "Others":        "\033[96m",   # cyan
}

RESET  = "\033[0m"
BOLD   = "\033[1m"
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
DIM    = "\033[2m"


# ──────────────────────────────────────────────
#  HELPERS
# ──────────────────────────────────────────────
def clear():
    os.system("cls" if os.name == "nt" else "clear")

def divider(char="─", width=55):
    print(char * width)

def header(title):
    clear()
    divider("═")
    print(f"{BOLD}  💰  EXPENSE TRACKER PRO  │  {title}{RESET}")
    divider("═")
    print()

def pause():
    input(f"\n{DIM}  Press Enter to continue…{RESET}")

def colored(text, color):
    return f"{color}{text}{RESET}"

def fmt_amount(amount):
    return f"{CURRENCY}{amount:,.2f}"


# ──────────────────────────────────────────────
#  FILE INITIALISATION
# ──────────────────────────────────────────────
def initialize_file():
    if not os.path.exists(FILE):
        with open(FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Item", "Category", "Amount", "Date", "Note"])

def  load_expenses():
    if not os.path.exists(FILE):
        initialize_file()

    expenses = []

    with open(FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            expenses.append(row)
    return expenses

def save_expenses(expenses):
    with open(FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["ID", "Item", "Category", "Amount", "Date", "Note"])
        writer.writeheader()
        writer.writerows(expenses)

def next_id(expenses):
    if not expenses:
        return 1
    return max(int(e["ID"]) for e in expenses) + 1


# ──────────────────────────────────────────────
#  BUDGET
# ──────────────────────────────────────────────
def load_budgets():
    if os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE, "r") as f:
            return json.load(f)
    return {}

def save_budgets(budgets):
    with open(BUDGET_FILE, "w") as f:
        json.dump(budgets, f, indent=2)

def check_budget_alert(category, expenses):
    budgets = load_budgets()
    if category not in budgets:
        return
    current_month = datetime.now().strftime("%Y-%m")
    spent = sum(
        float(e["Amount"])
        for e in expenses
        if e["Category"] == category and e["Date"].startswith(current_month)
    )
    limit = budgets[category]
    pct = (spent / limit) * 100 if limit > 0 else 0
    if pct >= 100:
        print(colored(f"\n  ⚠️  BUDGET EXCEEDED for {category}! "
                      f"Spent {fmt_amount(spent)} / Limit {fmt_amount(limit)}", RED))
    elif pct >= 80:
        print(colored(f"\n  ⚠️  Warning: {pct:.0f}% of {category} budget used "
                      f"({fmt_amount(spent)} / {fmt_amount(limit)})", YELLOW))

def manage_budgets():
    header("Budget Manager")
    budgets = load_budgets()

    print(f"  {BOLD}Current Budgets (monthly):{RESET}\n")
    if budgets:
        for cat, amt in budgets.items():
            color = CATEGORY_COLORS.get(cat, "")
            print(f"  {color}{cat:<15}{RESET} {fmt_amount(amt)}")
    else:
        print(f"  {DIM}No budgets set yet.{RESET}")

    print(f"\n  {BOLD}Set / Update a Budget:{RESET}")
    print()
    for k, v in CATEGORIES.items():
        color = CATEGORY_COLORS.get(v, "")
        print(f"  {k}. {color}{v}{RESET}")
    print("  0. Back")
    print()

    choice = input("  Choose category: ").strip()
    if choice == "0" or choice not in CATEGORIES:
        return

    cat = CATEGORIES[choice]
    try:
        limit = float(input(f"  Monthly budget for {cat} ({CURRENCY}): ").strip())
        budgets[cat] = limit
        save_budgets(budgets)
        print(colored(f"\n  ✅  Budget set: {cat} → {fmt_amount(limit)}", GREEN))
    except ValueError:
        print(colored("  Invalid amount.", RED))
    pause()


# ──────────────────────────────────────────────
#  ADD EXPENSE
# ──────────────────────────────────────────────
def add_expense():
    header("Add Expense")
    expenses = load_expenses()

    item = input("  Expense name : ").strip()
    if not item:
        print(colored("  Name cannot be empty.", RED))
        pause(); return

    print(f"\n  {BOLD}Categories:{RESET}")
    for k, v in CATEGORIES.items():
        color = CATEGORY_COLORS.get(v, "")
        print(f"  {k}. {color}{v}{RESET}")
    print()

    choice   = input("  Choose category: ").strip()
    category = CATEGORIES.get(choice, "Others")

    try:
        amount = float(input(f"  Amount ({CURRENCY}): ").strip())
        if amount <= 0:
            raise ValueError
    except ValueError:
        print(colored("  Invalid amount.", RED))
        pause(); return

    note = input("  Note (optional): ").strip()
    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    expenses.append({
        "ID":       next_id(expenses),
        "Item":     item,
        "Category": category,
        "Amount":   amount,
        "Date":     date,
        "Note":     note,
    })
    save_expenses(expenses)
    print(colored(f"\n  ✅  Expense added!", GREEN))
    check_budget_alert(category, expenses)
    pause()


# ──────────────────────────────────────────────
#  VIEW EXPENSES
# ──────────────────────────────────────────────
def view_expenses(filter_month=None, filter_cat=None, title="All Expenses"):
    header(title)
    expenses = load_expenses()

    if filter_month:
        expenses = [e for e in expenses if e["Date"].startswith(filter_month)]
    if filter_cat:
        expenses = [e for e in expenses if e["Category"] == filter_cat]

    if not expenses:
        print(f"  {DIM}No expenses found.{RESET}")
        pause(); return

    total = 0.0
    print(f"  {'ID':<5} {'Item':<20} {'Category':<14} {'Amount':>10}  {'Date':<16}  Note")
    divider()
    for e in expenses:
        color  = CATEGORY_COLORS.get(e["Category"], "")
        amount = float(e["Amount"])
        total += amount
        note   = (e["Note"][:18] + "…") if len(e.get("Note","")) > 18 else e.get("Note","")
        print(f"  {e['ID']:<5} {e['Item']:<20} "
              f"{color}{e['Category']:<14}{RESET} "
              f"{fmt_amount(amount):>10}  {e['Date']:<16}  {DIM}{note}{RESET}")

    divider()
    print(f"  {'TOTAL':>41}  {BOLD}{fmt_amount(total)}{RESET}")
    pause()


# ──────────────────────────────────────────────
#  SEARCH
# ──────────────────────────────────────────────
def search_expense():
    header("Search Expenses")
    keyword   = input("  Search by name or note: ").strip().lower()
    expenses  = load_expenses()
    results   = [e for e in expenses
                 if keyword in e["Item"].lower() or keyword in e.get("Note","").lower()]

    if not results:
        print(colored("  No matching expenses found.", YELLOW))
    else:
        print(f"\n  Found {len(results)} result(s):\n")
        for e in results:
            color = CATEGORY_COLORS.get(e["Category"], "")
            print(f"  [{e['ID']}] {e['Item']} | "
                  f"{color}{e['Category']}{RESET} | "
                  f"{fmt_amount(float(e['Amount']))} | {e['Date']}")
            if e.get("Note"):
                print(f"        {DIM}Note: {e['Note']}{RESET}")
    pause()


# ──────────────────────────────────────────────
#  EDIT EXPENSE
# ──────────────────────────────────────────────
def edit_expense():
    header("Edit Expense")
    expenses = load_expenses()
    if not expenses:
        print(f"  {DIM}No expenses to edit.{RESET}")
        pause(); return

    for e in expenses:
        print(f"  [{e['ID']}] {e['Item']} | {e['Category']} | {fmt_amount(float(e['Amount']))} | {e['Date']}")

    print()
    try:
        eid = int(input("  Enter ID to edit: ").strip())
    except ValueError:
        print(colored("  Invalid ID.", RED)); pause(); return

    target = next((e for e in expenses if int(e["ID"]) == eid), None)
    if not target:
        print(colored("  Expense not found.", RED)); pause(); return

    print(f"\n  Editing: {BOLD}{target['Item']}{RESET}  (leave blank to keep current value)\n")

    new_item = input(f"  Name [{target['Item']}]: ").strip()
    if new_item:
        target["Item"] = new_item

    print(f"\n  Categories:")
    for k, v in CATEGORIES.items():
        color = CATEGORY_COLORS.get(v, "")
        print(f"  {k}. {color}{v}{RESET}")
    cat_choice = input(f"\n  Category [{target['Category']}]: ").strip()
    if cat_choice in CATEGORIES:
        target["Category"] = CATEGORIES[cat_choice]

    new_amt = input(f"  Amount [{fmt_amount(float(target['Amount']))}]: ").strip()
    if new_amt:
        try:
            target["Amount"] = float(new_amt)
        except ValueError:
            print(colored("  Invalid amount, keeping original.", YELLOW))

    new_note = input(f"  Note [{target.get('Note','')}]: ").strip()
    if new_note:
        target["Note"] = new_note

    save_expenses(expenses)
    print(colored("\n  ✅  Expense updated!", GREEN))
    pause()


# ──────────────────────────────────────────────
#  DELETE EXPENSE
# ──────────────────────────────────────────────
def delete_expense():
    header("Delete Expense")
    expenses = load_expenses()
    if not expenses:
        print(f"  {DIM}No expenses to delete.{RESET}")
        pause(); return

    for e in expenses:
        print(f"  [{e['ID']}] {e['Item']} | {e['Category']} | {fmt_amount(float(e['Amount']))} | {e['Date']}")

    print()
    try:
        eid = int(input("  Enter ID to delete: ").strip())
    except ValueError:
        print(colored("  Invalid ID.", RED)); pause(); return

    target = next((e for e in expenses if int(e["ID"]) == eid), None)
    if not target:
        print(colored("  Expense not found.", RED)); pause(); return

    confirm = input(f"  Delete '{target['Item']}' ({fmt_amount(float(target['Amount']))})? [y/N]: ").strip().lower()
    if confirm == "y":
        expenses.remove(target)
        save_expenses(expenses)
        print(colored("  ✅  Deleted successfully!", GREEN))
    else:
        print("  Cancelled.")
    pause()


# ──────────────────────────────────────────────
#  MONTHLY REPORT
# ──────────────────────────────────────────────
def monthly_report():
    header("Monthly Report")
    current_month = datetime.now().strftime("%Y-%m")
    month_label   = datetime.now().strftime("%B %Y")
    expenses      = load_expenses()
    budgets       = load_budgets()

    monthly = [e for e in expenses if e["Date"].startswith(current_month)]

    if not monthly:
        print(f"  {DIM}No expenses for {month_label}.{RESET}")
        pause(); return

    by_cat = defaultdict(float)
    for e in monthly:
        by_cat[e["Category"]] += float(e["Amount"])

    total = sum(by_cat.values())

    print(f"  {BOLD}{month_label}{RESET}  —  {len(monthly)} transactions\n")
    divider()

    for cat, spent in sorted(by_cat.items(), key=lambda x: -x[1]):
        color  = CATEGORY_COLORS.get(cat, "")
        pct    = (spent / total) * 100 if total else 0
        bar_w  = int(pct / 3)           # max ~33 chars
        bar    = "█" * bar_w

        # budget status
        if cat in budgets:
            limit      = budgets[cat]
            budget_pct = (spent / limit) * 100
            if budget_pct >= 100:
                status = colored(f" ⚠ {budget_pct:.0f}% of budget", RED)
            elif budget_pct >= 80:
                status = colored(f" ⚠ {budget_pct:.0f}% of budget", YELLOW)
            else:
                status = colored(f" ✓ {budget_pct:.0f}% of budget", GREEN)
        else:
            status = ""

        print(f"  {color}{cat:<14}{RESET} {fmt_amount(spent):>10}  "
              f"{color}{bar:<34}{RESET} {pct:4.1f}%{status}")

    divider()
    print(f"  {'TOTAL':<14} {BOLD}{fmt_amount(total):>10}{RESET}")
    pause()


# ──────────────────────────────────────────────
#  ANALYTICS  (ASCII charts)
# ──────────────────────────────────────────────
def analytics():
    header("Spending Analytics")
    expenses = load_expenses()

    if not expenses:
        print(f"  {DIM}No data available.{RESET}")
        pause(); return

    print(f"  {BOLD}1.{RESET} Category breakdown (all time)")
    print(f"  {BOLD}2.{RESET} Monthly trend (last 6 months)")
    print(f"  {BOLD}3.{RESET} Top 5 biggest expenses")
    print(f"  {BOLD}0.{RESET} Back\n")

    choice = input("  Choose: ").strip()

    if choice == "1":
        _chart_by_category(expenses)
    elif choice == "2":
        _chart_monthly_trend(expenses)
    elif choice == "3":
        _top_expenses(expenses)

def _chart_by_category(expenses):
    header("Category Breakdown")
    by_cat = defaultdict(float)
    for e in expenses:
        by_cat[e["Category"]] += float(e["Amount"])

    total   = sum(by_cat.values())
    max_amt = max(by_cat.values())
    BAR_MAX = 38

    divider()
    for cat, amt in sorted(by_cat.items(), key=lambda x: -x[1]):
        color = CATEGORY_COLORS.get(cat, "")
        pct   = (amt / total) * 100
        bar_w = int((amt / max_amt) * BAR_MAX)
        bar   = "█" * bar_w
        print(f"  {color}{cat:<14}{RESET} {color}{bar:<38}{RESET} {fmt_amount(amt):>11}  {pct:4.1f}%")
    divider()
    print(f"  {'TOTAL':<14} {' '*38} {BOLD}{fmt_amount(total):>11}{RESET}")
    pause()

def _chart_monthly_trend(expenses):
    header("Monthly Trend — Last 6 Months")
    monthly = defaultdict(float)
    for e in expenses:
        month = e["Date"][:7]
        monthly[month] += float(e["Amount"])

    sorted_months = sorted(monthly.keys())[-6:]
    if not sorted_months:
        print(f"  {DIM}Not enough data.{RESET}"); pause(); return

    max_amt = max(monthly[m] for m in sorted_months)
    BAR_MAX = 38

    divider()
    for month in sorted_months:
        amt    = monthly[month]
        bar_w  = int((amt / max_amt) * BAR_MAX) if max_amt else 0
        bar    = "█" * bar_w
        label  = datetime.strptime(month, "%Y-%m").strftime("%b %Y")
        print(f"  {CYAN}{label:<10}{RESET}  {CYAN}{bar:<38}{RESET}  {fmt_amount(amt):>11}")
    divider()
    pause()

def _top_expenses(expenses):
    header("Top 5 Biggest Expenses")
    sorted_exp = sorted(expenses, key=lambda e: float(e["Amount"]), reverse=True)[:5]
    divider()
    for i, e in enumerate(sorted_exp, 1):
        color = CATEGORY_COLORS.get(e["Category"], "")
        print(f"  {BOLD}{i}.{RESET} {e['Item']:<22} {color}{e['Category']:<14}{RESET}"
              f" {BOLD}{fmt_amount(float(e['Amount'])):>10}{RESET}  {DIM}{e['Date']}{RESET}")
    divider()
    pause()


# ──────────────────────────────────────────────
#  FILTER BY MONTH / CATEGORY
# ──────────────────────────────────────────────
def filter_view():
    header("Filter Expenses")
    print(f"  {BOLD}1.{RESET} Filter by month")
    print(f"  {BOLD}2.{RESET} Filter by category")
    print(f"  {BOLD}0.{RESET} Back\n")
    choice = input("  Choose: ").strip()

    if choice == "1":
        month = input("  Enter month (YYYY-MM): ").strip()
        label = datetime.strptime(month, "%Y-%m").strftime("%B %Y") if len(month) == 7 else month
        view_expenses(filter_month=month, title=f"Expenses — {label}")

    elif choice == "2":
        for k, v in CATEGORIES.items():
            color = CATEGORY_COLORS.get(v, "")
            print(f"  {k}. {color}{v}{RESET}")
        cat_choice = input("\n  Choose category: ").strip()
        cat = CATEGORIES.get(cat_choice)
        if cat:
            view_expenses(filter_cat=cat, title=f"Expenses — {cat}")


# ──────────────────────────────────────────────
#  MAIN MENU
# ──────────────────────────────────────────────
def main():
    initialize_file()
    while True:
        header("Main Menu")
        options = [
            ("1", "➕", "Add Expense"),
            ("2", "📋", "View All Expenses"),
            ("3", "🔍", "Search Expenses"),
            ("4", "✏️ ", "Edit Expense"),
            ("5", "🗑️ ", "Delete Expense"),
            ("6", "📅", "Monthly Report"),
            ("7", "📊", "Analytics & Charts"),
            ("8", "🔎", "Filter Expenses"),
            ("9", "💰", "Manage Budgets"),
            ("0", "🚪", "Exit"),
        ]
        for key, icon, label in options:
            print(f"  {BOLD}{key}.{RESET}  {icon}  {label}")

        print()
        choice = input("  Choose option: ").strip()

        if   choice == "1": add_expense()
        elif choice == "2": view_expenses()
        elif choice == "3": search_expense()
        elif choice == "4": edit_expense()
        elif choice == "5": delete_expense()
        elif choice == "6": monthly_report()
        elif choice == "7": analytics()
        elif choice == "8": filter_view()
        elif choice == "9": manage_budgets()
        elif choice == "0":
            clear()
            print(colored("\n  👋  Goodbye! Stay on budget.\n", GREEN))
            break
        else:
            print(colored("  Invalid option.", RED))
            pause()

if __name__ == "__main__":
    main()