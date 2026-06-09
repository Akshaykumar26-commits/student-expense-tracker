import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os

FILE = "expenses.csv"

# Create CSV if not exists
if not os.path.exists(FILE):
    with open(FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Item", "Category", "Amount"])


def add_expense():
    item = item_entry.get()
    category = category_combo.get()
    amount = amount_entry.get()

    if not item or not amount:
        messagebox.showerror("Error", "Please fill all fields")
        return

    try:
        float(amount)
    except ValueError:
        messagebox.showerror("Error", "Amount must be a number")
        return

    with open(FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([item, category, amount])

    item_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)

    load_expenses()


def load_expenses():
    for row in tree.get_children():
        tree.delete(row)

    total = 0

    with open(FILE, "r") as f:
        reader = csv.reader(f)
        next(reader)

        for row in reader:
            tree.insert("", tk.END, values=row)
            total += float(row[2])

    total_label.config(text=f"Total Expense: ₹{total}")


def delete_expense():
    selected = tree.selection()

    if not selected:
        messagebox.showwarning("Warning", "Select an expense")
        return

    values = tree.item(selected[0])["values"]

    rows = []

    with open(FILE, "r") as f:
        reader = csv.reader(f)
        rows = list(reader)

    header = rows[0]
    data = rows[1:]

    data = [r for r in data if r != [str(v) for v in values]]

    with open(FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)

    load_expenses()


# Main Window
root = tk.Tk()
root.title("Expense Tracker Pro")
root.geometry("700x500")

# Input Frame
frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Expense Name").grid(row=0, column=0)
item_entry = tk.Entry(frame)
item_entry.grid(row=0, column=1)

tk.Label(frame, text="Category").grid(row=1, column=0)

category_combo = ttk.Combobox(
    frame,
    values=["Food", "Travel", "Shopping", "Bills", "Entertainment", "Others"]
)
category_combo.grid(row=1, column=1)
category_combo.current(0)

tk.Label(frame, text="Amount").grid(row=2, column=0)
amount_entry = tk.Entry(frame)
amount_entry.grid(row=2, column=1)

tk.Button(frame, text="Add Expense", command=add_expense)\
.grid(row=3, column=0, columnspan=2, pady=10)

# Table
tree = ttk.Treeview(
    root,
    columns=("Item", "Category", "Amount"),
    show="headings"
)

tree.heading("Item", text="Item")
tree.heading("Category", text="Category")
tree.heading("Amount", text="Amount")

tree.pack(fill="both", expand=True, padx=20, pady=10)

# Bottom Frame
bottom = tk.Frame(root)
bottom.pack(pady=10)

total_label = tk.Label(
    bottom,
    text="Total Expense: ₹0",
    font=("Arial", 12, "bold")
)
total_label.pack()

tk.Button(
    bottom,
    text="Delete Selected",
    command=delete_expense
).pack(pady=5)

load_expenses()

root.mainloop()
import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os

FILE = "expenses.csv"

# Create file if missing
if not os.path.exists(FILE):
    with open(FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Item", "Category", "Amount"])


class ExpenseTracker:

    def __init__(self, root):

        self.root = root
        self.root.title("Expense Tracker Pro")
        self.root.geometry("850x600")

        title = tk.Label(
            root,
            text="Expense Tracker Pro",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=10)

        self.create_input_frame()
        self.create_search_frame()
        self.create_table()

        self.total_label = tk.Label(
            root,
            text="Total Expense: ₹0",
            font=("Arial", 14, "bold")
        )
        self.total_label.pack(pady=10)

        self.load_expenses()

    def create_input_frame(self):

        frame = tk.LabelFrame(
            self.root,
            text="Add Expense",
            padx=10,
            pady=10
        )
        frame.pack(fill="x", padx=10)

        tk.Label(frame, text="Item").grid(row=0, column=0)

        self.item_entry = tk.Entry(frame, width=25)
        self.item_entry.grid(row=0, column=1)

        tk.Label(frame, text="Category").grid(row=0, column=2)

        self.category_combo = ttk.Combobox(
            frame,
            values=[
                "Food",
                "Travel",
                "Shopping",
                "Bills",
                "Entertainment",
                "Others"
            ],
            width=20
        )

        self.category_combo.grid(row=0, column=3)
        self.category_combo.current(0)

        tk.Label(frame, text="Amount").grid(row=0, column=4)

        self.amount_entry = tk.Entry(frame, width=15)
        self.amount_entry.grid(row=0, column=5)

        tk.Button(
            frame,
            text="Add Expense",
            command=self.add_expense
        ).grid(row=0, column=6, padx=10)

    def create_search_frame(self):

        frame = tk.Frame(self.root)
        frame.pack(fill="x", pady=10)

        tk.Label(frame, text="Search").pack(side="left", padx=10)

        self.search_entry = tk.Entry(frame)
        self.search_entry.pack(side="left")

        tk.Button(
            frame,
            text="Search",
            command=self.search_expense
        ).pack(side="left", padx=5)

        tk.Button(
            frame,
            text="Show All",
            command=self.load_expenses
        ).pack(side="left")

    def create_table(self):

        columns = ("Item", "Category", "Amount")

        self.tree = ttk.Treeview(
            self.root,
            columns=columns,
            show="headings"
        )

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)

        self.tree.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        tk.Button(
            self.root,
            text="Delete Selected",
            command=self.delete_expense
        ).pack()

    def add_expense(self):

        item = self.item_entry.get()
        category = self.category_combo.get()
        amount = self.amount_entry.get()

        if not item or not amount:
            messagebox.showerror(
                "Error",
                "Please fill all fields"
            )
            return

        try:
            float(amount)
        except:
            messagebox.showerror(
                "Error",
                "Amount must be numeric"
            )
            return

        with open(FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                item,
                category,
                amount
            ])

        self.item_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)

        self.load_expenses()

    def load_expenses(self):

        for row in self.tree.get_children():
            self.tree.delete(row)

        total = 0

        with open(FILE, "r") as f:

            reader = csv.reader(f)
            next(reader)

            for row in reader:

                self.tree.insert(
                    "",
                    tk.END,
                    values=row
                )

                total += float(row[2])

        self.total_label.config(
            text=f"Total Expense: ₹{total}"
        )

    def search_expense(self):

        keyword = self.search_entry.get().lower()

        for row in self.tree.get_children():
            self.tree.delete(row)

        with open(FILE, "r") as f:

            reader = csv.reader(f)
            next(reader)

            for row in reader:

                if keyword in row[0].lower():

                    self.tree.insert(
                        "",
                        tk.END,
                        values=row
                    )

    def delete_expense(self):

        selected = self.tree.selection()

        if not selected:
            return

        values = self.tree.item(selected[0])["values"]

        rows = []

        with open(FILE, "r") as f:
            rows = list(csv.reader(f))

        header = rows[0]
        data = rows[1:]

        data = [
            row for row in data
            if row != [str(v) for v in values]
        ]

        with open(FILE, "w", newline="") as f:

            writer = csv.writer(f)

            writer.writerow(header)
            writer.writerows(data)

        self.load_expenses()


root = tk.Tk()
app = ExpenseTracker(root)
root.mainloop()