import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import mysql.connector
from datetime import datetime
import csv
from fpdf import FPDF
import matplotlib.pyplot as plt
import re

# Database connection setup
def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Manju_04072003",
        database="expense_tracker"
    )

# User table creation
def initialize_db():
    db = connect_to_db()
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            userid INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255),
            email VARCHAR(255),
            password VARCHAR(255)
        )
    """)
    cursor.execute("""
        CREATE TABLE
        IF NOT EXISTS expenses (
            expid INT AUTO_INCREMENT PRIMARY KEY,
            userid INT,
            category VARCHAR(255),
            description TEXT,
            amount FLOAT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (userid) REFERENCES users(userid)
        )
    """)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS income (
            income_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            income_amount DECIMAL(10, 2),
            FOREIGN KEY (user_id) REFERENCES users(userid)
        )
    ''')
    db.commit()
    db.close()

initialize_db()

# GUI Application
class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Expense Tracker")
        self.root.attributes("-fullscreen", False)
        self.root.configure(bg="powderblue")

        self.userid = None
        self.username = None

        self.categories = ["Food", "Transport", "Shopping", "Utilities", "Entertainment", "Health"]

        self.home_page()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def home_page(self):
        self.clear_window()
        tk.Label(self.root, text="Welcome to Your Personal Expense Tracker", font=("Arial", 40,"bold"),bg="powderblue").pack(padx=10,pady=30)
        tk.Label(self.root, text="Track, Save, Succeed!", font=("Arial", 26, "bold"),bg="powderblue").pack(pady=8)
        tk.Label(self.root, text="",bg="powderblue").pack(pady=5) 
        tk.Label(self.root, text="💰 Take control of your finances today!", font=("Arial", 20, "italic"),bg="powderblue").pack(pady=8)
        tk.Label(self.root, text="📊 Track every rupee, save every penny.", font=("Arial", 20, "italic"),bg="powderblue").pack(pady=8)
        tk.Label(self.root, text="🌟 Your journey to smart spending starts here!", font=("Arial", 20, "italic"),bg="powderblue").pack(pady=8)
        tk.Label(self.root, text="",bg="powderblue").pack(pady=5) 
        tk.Label(self.root, text="Already have an account?", font=("Arial", 18),bg="powderblue").pack(pady=10)
        tk.Button(self.root, text="Login", command=self.login_page, width=15, font=("Arial", 15), bg="lightpink").pack(pady=10)
        tk.Label(self.root, text="",bg="powderblue").pack(pady=5)
        tk.Label(self.root, text="Are you a new user?", font=("Arial", 18),bg="powderblue").pack(pady=10)
        tk.Button(self.root, text="Register", command=self.register_page, width=15, font=("Arial", 15), bg="lightgreen").pack(pady=10)

    def validate_email(self, email):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

    def validate_password(self, password):
        return len(password) > 0
    
    def forgot_password_page(self):
        self.clear_window()
        tk.Label(self.root, text="Forgot Password", font=("Arial", 16)).pack(pady=20)

        tk.Label(self.root, text="Enter your registered email").pack()
        email_entry = tk.Entry(self.root)
        email_entry.pack()

        def reset_password():
            email = email_entry.get()
            if not email:
                messagebox.showerror("Error", "Email is required")
                return

            db = connect_to_db()
            cursor = db.cursor()
            cursor.execute("SELECT userid FROM users WHERE email=%s", (email,))
            user = cursor.fetchone()
            db.close()

            if user:
                new_password = simpledialog.askstring("Reset Password", "Enter new password:")
                if new_password:
                    db = connect_to_db()
                    cursor = db.cursor()
                    cursor.execute("UPDATE users SET password=%s WHERE email=%s", (new_password, email))
                    db.commit()
                    db.close()
                    messagebox.showinfo("Success", "Password reset successfully")
                    self.login_page()
                else:   
                    messagebox.showerror("Error", "Password reset canceled")
            else:
                messagebox.showerror("Error", "Email not found")

        tk.Button(self.root, text="Reset Password", command=reset_password, bg="lightpink").pack(pady=10)
        tk.Button(self.root, text="Back", command=self.login_page, bg="lightgray").pack()


     
    def login_page(self):
        self.clear_window()
        tk.Label(self.root, text="Login", font=("Arial", 40, "bold"),bg="powderblue").pack(padx=30,pady=40)
        tk.Label(self.root, text="Enter your Email:", font=("Arial", 25),bg="powderblue").pack(pady=10)
        email_entry = tk.Entry(self.root, font=("Arial", 14), width=30)
        email_entry.pack(pady=10)
        tk.Label(self.root, text="Enter your Password:", font=("Arial", 25),bg="powderblue").pack(pady=10)
        password_entry = tk.Entry(self.root, font=("Arial", 14), show="*", width=30)
        password_entry.pack(pady=10)
        tk.Label(self.root, text="",bg="powderblue").pack(pady=10)


        def login():
            email = email_entry.get()
            password = password_entry.get()

            # Email validation
            if not self.validate_email(email):
                messagebox.showerror("Error", "Invalid email format")
                return

            if not self.validate_password(password):
                messagebox.showerror("Error", "Password is required")
                return
    
            db = connect_to_db()
            cursor = db.cursor()
            cursor.execute("SELECT userid, username FROM users WHERE email=%s AND password=%s", (email, password))
            user = cursor.fetchone()
            db.close()

            if user:
                self.userid, self.username = user
                messagebox.showinfo("Success", "Login Successful")
                # Check if income already exists for the user
                db = connect_to_db()
                cursor = db.cursor()
                cursor.execute("SELECT income_amount FROM income WHERE user_id=%s", (self.userid,))
                income = cursor.fetchone()
                db.close()

                if income:
                    # If income exists, directly go to the menu page
                    self.menu_page()
                else:
                    # If no income, open income page
                    self.open_income_page(self.userid)
            else:
                messagebox.showerror("Error", "Invalid email or password")

        tk.Button(self.root, text="Login", command=login, font=("Arial", 14), bg="lightpink", width=15).pack(pady=10)
        tk.Button(self.root, text="Forgot Password?", command=self.forgot_password_page, font=("Arial", 12), bg="lightgray", width=15).pack(pady=5)
        tk.Button(self.root, text="Back", command=self.home_page, font=("Arial", 12), bg="lightgray", width=15).pack(pady=5)

    def register_page(self):
        self.clear_window()
        tk.Label(self.root, text="Register", font=("Arial", 40, "bold"), bg="powderblue").pack(padx=30, pady=40)

        tk.Label(self.root, text="Enter your Username:", font=("Arial", 25), bg="powderblue").pack(pady=10)
        username_entry = tk.Entry(self.root, font=("Arial", 14), width=30)
        username_entry.pack(pady=10)

        tk.Label(self.root, text="Enter your Email:", font=("Arial", 25), bg="powderblue").pack(pady=10)
        email_entry = tk.Entry(self.root, font=("Arial", 14), width=30)
        email_entry.pack(pady=10)

        tk.Label(self.root, text="Enter your Password:", font=("Arial", 25), bg="powderblue").pack(pady=10)
        password_entry = tk.Entry(self.root, font=("Arial", 14), show="*", width=30)
        password_entry.pack(pady=10)
        tk.Label(self.root, text="", bg="powderblue").pack(pady=10)


        def register():
            username = username_entry.get()
            email = email_entry.get()
            password = password_entry.get()

            # Email validation
            if not self.validate_email(email):
                messagebox.showerror("Error", "Invalid email format")
                return

            if not self.validate_password(password):
                messagebox.showerror("Error", "Password is required")
                return
    
            db = connect_to_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                           (username, email, password))
            db.commit()
            db.close()

            messagebox.showinfo("Success", "Registration Successful")
            self.login_page()

        tk.Button(self.root, text="Register", command=register,  font=("Arial", 14), bg="lightgreen", width=15).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.home_page, font=("Arial", 12), bg="lightgray", width=15).pack()

    # Open Income Page
    def open_income_page(self, user_id):
        self.clear_window()
        tk.Label(self.root, text="Track Your Earnings, Shape Your Future!", font=("Arial", 40, "bold"), bg="powderblue").pack(padx=30, pady=40)
        tk.Label(self.root, text='"Income is the key to financial freedom. Let’s start with a step!"', font=("Arial", 18, "italic"), bg="powderblue").pack(pady=20)

        tk.Label(self.root, text="Enter your monthly income:", font=("Arial", 25), bg="powderblue").pack(pady=10)
        income_entry = tk.Entry(self.root, font=("Arial", 14), width=30)
        income_entry.pack(pady=10)
    
        def submit_income(user_id):
            income_amount = income_entry.get()
            if not income_amount:
                messagebox.showerror("Error", "Please enter your income")
                return

            try:
                conn = connect_to_db()
                cursor = conn.cursor()
                query = "INSERT INTO income (user_id, income_amount) VALUES (%s, %s)"
                cursor.execute(query, (user_id, income_amount))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Income recorded successfully!")
                self.menu_page()
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error: {err}")
                
        tk.Button(self.root, text="Submit", command=lambda: submit_income(user_id), bg="lightgreen", font=("Arial", 14), width=20).pack(pady=10)
        
    def get_balance(self, user_id):
        db = connect_to_db()
        cursor = db.cursor()
    
        # Get total income for the user
        cursor.execute("SELECT SUM(income_amount) FROM income WHERE user_id=%s", (user_id,))
        total_income = cursor.fetchone()[0] or 0  # If no income, set to 0
    
        # Get total expenses for the user
        cursor.execute("SELECT SUM(amount) FROM expenses WHERE userid=%s", (user_id,))
        total_expenses = cursor.fetchone()[0] or 0  # If no expenses, set to 0
    
        # Ensure both values are float for subtraction
        total_income = float(total_income)
        total_expenses = float(total_expenses)
    
        db.close()
    
        # Calculate balance
        balance = total_income - total_expenses
        return balance

    def show_update_income_page(self):
        new_income = simpledialog.askstring("Update Income", "Enter your new income:", parent=self.root)
    
        if new_income:  # Check if the user provided an input
            if new_income.isdigit(): 
                try:
                    conn = connect_to_db()  
                    cursor = conn.cursor()

                    # Update the income in the database
                    cursor.execute("UPDATE income SET income_amount = %s WHERE user_id = %s", (new_income, self.userid))
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Success", "Income updated successfully!")
                except mysql.connector.Error as err:
                    messagebox.showerror("Error", f"Error: {err}")
                    self.menu_page()  # Assuming you want to go back to the menu if there's an error
            else:
                messagebox.showerror("Invalid Input", "Please enter a valid numeric value for income.")
    
   
    def menu_page(self):
        self.clear_window()
        balance = self.get_balance(self.userid)
    
        balance_status = f"Balance: ₹{balance:.2f}"
        if balance < 0:
            balance_status = f"Over Budget: ₹{abs(balance):.2f}"

        tk.Label(self.root, text=f"{self.username}'s Personal Expense Tracker", font=("Arial", 40, "bold"), bg="powderblue").pack(padx=30, pady=40)
        tk.Label(self.root, text="Menu", font=("Arial", 25, "italic"), bg="powderblue").pack(pady=20)
        tk.Label(self.root, text=balance_status, font=("Arial", 18), fg="green" if balance >= 0 else "red", bg="powderblue").pack(pady=20)

        button_style = {"font": ("Arial", 14), "width": 20} 
        tk.Button(self.root, text="Add Expense", command=self.add_expense_page, bg="lightpink", **button_style).pack(pady=10)
        tk.Button(self.root, text="Delete Expense", command=self.delete_expense_page, bg="lightcoral", **button_style).pack(pady=10)
        tk.Button(self.root, text="Update Expense", command=self.update_expense_page, bg="lightgoldenrod", **button_style).pack(pady=10)
        tk.Button(self.root, text="View Expense", command=self.view_expense_page, bg="lightgreen", **button_style).pack(pady=10)
        tk.Button(self.root, text="Update Income", command=self.show_update_income_page, bg="thistle", **button_style).pack(pady=10)
        tk.Button(self.root, text="Logout", command=self.home_page, bg="lightgray", **button_style).pack(pady=10)

    def add_expense_page(self):
        self.clear_window()
    
        # Title and instructions with consistent styling
        tk.Label(self.root, text="Add Expense", font=("Arial", 40, "bold"), bg="powderblue").pack(padx=30, pady=20)
        tk.Label(self.root, text="Shape Your Financial Journey!", font=("Arial", 18, "italic"), bg="powderblue").pack(pady=20)

        # Category section
        tk.Label(self.root, text="Select your Category:", font=("Arial", 20), bg="powderblue").pack(padx=5,pady=10)
        category_combobox = ttk.Combobox(self.root, values=self.categories, state="readonly", font=("Arial", 14), width=30)
        category_combobox.pack(pady=10)

        # Add New Category Button
        def add_new_category():
            new_category = simpledialog.askstring("Add Category", "Enter new category:")
            if new_category and new_category not in self.categories:
                self.categories.append(new_category)
                category_combobox["values"] = self.categories
                messagebox.showinfo("Success", "New category added.")

        button_style = {"font": ("Arial", 14), "width": 20}
        tk.Button(self.root, text="Add New Category", command=add_new_category, bg="lightpink", **button_style).pack(pady=5)

        # Description field
        tk.Label(self.root, text="Enter Description:", font=("Arial", 20), bg="powderblue").pack(padx=5,pady=10)
        description_entry = tk.Entry(self.root, font=("Arial", 14), width=30)
        description_entry.pack(pady=10)

        # Amount field
        tk.Label(self.root, text="Enter Amount:", font=("Arial", 20), bg="powderblue").pack(padx=5,pady=10)
        amount_entry = tk.Entry(self.root, font=("Arial", 14), width=30)
        amount_entry.pack(pady=10)

        # Save Expense function
        def save_expense():
            category = category_combobox.get()
            description = description_entry.get()
            amount = amount_entry.get()

            if not category or not description or not amount:
                messagebox.showerror("Error", "All fields are required")
                return

            db = connect_to_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO expenses (userid, category, description, amount) VALUES (%s, %s, %s, %s)",
                           (self.userid, category, description, float(amount)))
            db.commit()
            db.close()

            messagebox.showinfo("Success", "Expense Added Successfully")
            self.menu_page()

        # Buttons for Save and Back with consistent styling
        tk.Button(self.root, text="Save", command=save_expense, bg="lightpink", **button_style).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.menu_page, bg="lightgray", **button_style).pack(pady=10)

    def delete_expense_page(self):
        self.clear_window()

        # Title with catchy message
        tk.Label(self.root, text="Delete Expense", font=("Arial", 40, "bold"), bg="powderblue").pack(padx=30, pady=20)
        tk.Label(self.root, text="Remove unwanted expenses and keep your budget in check!", font=("Arial", 18, "italic"), bg="powderblue").pack(pady=20)

        # Category selection
        tk.Label(self.root, text="Select Category:", font=("Arial", 20), bg="powderblue").pack(pady=10)
        category_combobox = ttk.Combobox(self.root, values=self.categories, state="readonly", font=("Arial", 14), width=30)
        category_combobox.pack(pady=10)

        # Description input field
        tk.Label(self.root, text="Enter Description:", font=("Arial", 20), bg="powderblue").pack(pady=10)
        description_entry = tk.Entry(self.root, font=("Arial", 14), width=30)
        description_entry.pack(pady=10)

        # Delete expense function
        def delete_expense():
            category = category_combobox.get()
            description = description_entry.get()

            if not category or not description:
                messagebox.showerror("Error", "All fields are required")
                return

            db = connect_to_db()
            cursor = db.cursor()
            cursor.execute("DELETE FROM expenses WHERE userid=%s AND category=%s AND description=%s", 
                           (self.userid, category, description))
            db.commit()
            db.close()

            messagebox.showinfo("Success", "Expense Deleted Successfully")
            self.menu_page()

        # Buttons for Delete and Back with consistent style
        button_style = {"font": ("Arial", 14), "width": 20}
        tk.Button(self.root, text="Delete", command=delete_expense, bg="lightcoral", **button_style).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.menu_page, bg="lightgray", **button_style).pack(pady=10)


    def update_expense_page(self):
        self.clear_window()

        # Title with catchy message
        tk.Label(self.root, text="Update Expense", font=("Arial", 40, "bold"), bg="powderblue").pack(padx=30, pady=20)
        tk.Label(self.root, text="Edit and keep track of your expenses for better budgeting!", font=("Arial", 18, "italic"), bg="powderblue").pack(pady=20)

        # Category selection
        tk.Label(self.root, text="Select Category:", font=("Arial", 20), bg="powderblue").pack(pady=10)
        category_combobox = ttk.Combobox(self.root, values=self.categories, state="readonly", font=("Arial", 14), width=30)
        category_combobox.pack(pady=10)

        # Old description input field
        tk.Label(self.root, text="Enter Old Description:", font=("Arial", 20), bg="powderblue").pack(pady=10)
        old_description_entry = tk.Entry(self.root, font=("Arial", 14), width=30)
        old_description_entry.pack(pady=10)

        # New description input field
        tk.Label(self.root, text="Enter New Description:", font=("Arial", 20), bg="powderblue").pack(pady=10)
        new_description_entry = tk.Entry(self.root, font=("Arial", 14), width=30)
        new_description_entry.pack(pady=10)

        # New amount input field
        tk.Label(self.root, text="Enter New Amount:", font=("Arial", 20), bg="powderblue").pack(pady=10)
        new_amount_entry = tk.Entry(self.root, font=("Arial", 14), width=30)
        new_amount_entry.pack(pady=10)

        # Update expense function
        def update_expense():
            category = category_combobox.get()
            old_description = old_description_entry.get()
            new_description = new_description_entry.get()
            new_amount = new_amount_entry.get()

            if not category or not old_description or not new_description or not new_amount:
                messagebox.showerror("Error", "All fields are required")
                return

            db = connect_to_db()
            cursor = db.cursor()
            cursor.execute("""
                UPDATE expenses SET description=%s, amount=%s WHERE userid=%s AND category=%s AND description=%s
            """, (new_description, float(new_amount), self.userid, category, old_description))
            db.commit()
            db.close()

            messagebox.showinfo("Success", "Expense Updated Successfully")
            self.menu_page()

        # Buttons for Update and Back with consistent style
        button_style = {"font": ("Arial", 14), "width": 20}
        tk.Button(self.root, text="Update", command=update_expense, bg="lightgoldenrod", **button_style).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.menu_page, bg="lightgray", **button_style).pack(pady=10)

    def view_expense_page(self):
        self.clear_window()
    
        # Title with catchy message
        tk.Label(self.root, text="VIEW EXPENSE", font=("Arial", 40, "bold"), bg="powderblue").pack(padx=30, pady=40)
        tk.Label(self.root, text="Track your expenses and get insights into your spending patterns!", font=("Arial", 18, "italic"), bg="powderblue").pack(pady=20)

        # Table View Section
        self.table_view_section()

        # Graphical Representation Section
        self.graphical_representation_section()

    def table_view_section(self):
        tk.Label(self.root, text="Table View", font=("Arial", 25,"bold"), bg="powderblue").pack(pady=20)

        # Dropdown for category selection
        tk.Label(self.root, text="View by Category", font=("Arial", 20), bg="powderblue").pack(pady=10)
        category_combobox = ttk.Combobox(self.root, values=["All"] + self.categories, state="readonly", font=("Arial", 14), width=30)
        category_combobox.pack(pady=10)

        def generate_csv(rows):
            filename = f"expenses_{self.userid}.csv"
            with open(filename, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Category", "Description", "Amount", "Date"])
                writer.writerows(rows)
            messagebox.showinfo("Success", f"CSV file saved as {filename}")

        def generate_pdf(rows):
            filename = f"expenses_{self.userid}.pdf"
            #filename = f"expenses.pdf"
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()

            # Title
            pdf.set_font("Arial", style='B', size=16)  # Bold font for the title
            pdf.cell(200, 10, txt="Personal Expense Tracker", ln=True, align='C')
            pdf.ln(10)  # Line break after the title

            db = connect_to_db()
            cursor = db.cursor()

            # Create the view (No need to commit here)
            cursor.execute("""
                CREATE OR REPLACE VIEW highest_spending_category AS
                SELECT  e.userid, u.username, e.category, SUM(e.amount) AS total_spent
                FROM expenses e
                JOIN users u ON e.userid = u.userid
                GROUP BY e.userid, e.category
                HAVING SUM(e.amount) = (
                SELECT MAX(category_spending)
                    FROM (
                        SELECT e.userid, SUM(e.amount) AS category_spending
                        FROM expenses e
                        GROUP BY e.userid, e.category
                    ) AS subquery
                    WHERE subquery.userid = e.userid
                );
            """)

            # Fetch highest spending category data
            cursor.execute("SELECT * FROM highest_spending_category WHERE userid = %s", (self.userid,))
        
            result = cursor.fetchone()  # Fetch the first (and only) result

            # Unpack the result for highest spending category
            userid, username, category, total_spent = result

            # Fetch all expense details for the user
            cursor.execute("SELECT category, description, amount, date FROM expenses WHERE userid = %s", (result[0],))
            expenses = cursor.fetchall()

            # Close connection
            db.close()

            # Display the Highest Spending Category Information
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Highest Spending Category: {category}", ln=True, align='L')
            pdf.cell(200, 10, txt=f"Total Spent: {total_spent}", ln=True, align='L')
            pdf.ln(10)  # Line break after the spending info

            # Table Header (Bold)
            pdf.set_font("Arial", style='B', size=12)  # Bold font for headers
            pdf.cell(40, 10, 'Category', border=1, align='C')
            pdf.cell(70, 10, 'Description', border=1, align='C')
            pdf.cell(30, 10, 'Amount', border=1, align='C')
            pdf.cell(40, 10, 'Date', border=1, align='C')
            pdf.ln()

            # Table Rows
            pdf.set_font("Arial", size=12)  # Regular font for rows
            for row in rows:
                pdf.cell(40, 10, row[0], border=1, align='C')
                pdf.cell(70, 10, row[1], border=1, align='C')
                pdf.cell(30, 10, str(row[2]), border=1, align='C')
                pdf.cell(40, 10, str(row[3]), border=1, align='C')
                pdf.ln()

            pdf.output(filename)
            messagebox.showinfo("Success", f"PDF file saved as {filename}")

        def view_expenses():
            category = category_combobox.get()
            if not category:
                messagebox.showwarning("Warning", "Please select a category!")
                return
            db = connect_to_db()
            cursor = db.cursor()
            query = "SELECT category, description, amount, date FROM expenses WHERE userid=%s"
            params = [self.userid]

            if category != "All":
                query += " AND category=%s"
                params.append(category)

            cursor.execute(query, params)
            rows = cursor.fetchall()
            db.close()

            # Display expenses in table format
            result_window = tk.Toplevel(self.root)
            result_window.title("Expenses")
            result_window.geometry("700x400")

            columns = ("Category", "Description", "Amount", "Date")
            tree = ttk.Treeview(result_window, columns=columns, show="headings")
            tree.heading("Category", text="Category")
            tree.heading("Description", text="Description")
            tree.heading("Amount", text="Amount")
            tree.heading("Date", text="Date")

            for row in rows:
                tree.insert("", tk.END, values=row)

            tree.pack(fill=tk.BOTH, expand=True)

            # Export buttons
            button_style = {"font": ("Arial", 14), "width": 20}
            tk.Button(result_window, text="Export to CSV", command=lambda: generate_csv(rows), bg="lightpink", **button_style).pack(pady=5)
            tk.Button(result_window, text="Export to PDF", command=lambda: generate_pdf(rows), bg="lightgreen", **button_style).pack(pady=5)
            tk.Button(result_window, text="Back", command=result_window.destroy, bg="lightgray", **button_style).pack(pady=5)

        # View Button with consistent style
        button_style = {"font": ("Arial", 14), "width": 20}
        tk.Button(self.root, text="View", command=view_expenses, bg="lightgreen", **button_style).pack(pady=10)

    def graphical_representation_section(self):
        tk.Label(self.root, text="Graphical Representation", font=("Arial", 25, "bold"), bg="powderblue").pack(pady=20)

        def plot_bar_chart():
            db = connect_to_db()
            cursor = db.cursor()
            cursor.execute("SELECT category, SUM(amount) FROM expenses WHERE userid=%s GROUP BY category", (self.userid,))
            data = cursor.fetchall()
            db.close()

            categories = [row[0] for row in data]
            amounts = [row[1] for row in data]

            plt.bar(categories, amounts, color=["blue", "orange", "green", "red", "purple", "brown"])
            plt.title("Expense Categories")
            plt.xlabel("Category")
            plt.ylabel("Amount")
            for i in range(len(categories)):
                plt.text(i, amounts[i] + 1, str(amounts[i]), ha='center')  
            plt.show()

        def plot_pie_chart():
            db = connect_to_db()
            cursor = db.cursor()
            cursor.execute("SELECT category, SUM(amount) FROM expenses WHERE userid=%s GROUP BY category", (self.userid,))
            data = cursor.fetchall()
            db.close()

            categories = [row[0] for row in data]
            amounts = [row[1] for row in data]

            plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
            plt.title("Expense Distribution by Category")
            plt.show()

        # Buttons for different charts with consistent style
        button_style = {"font": ("Arial", 14), "width": 20}
        tk.Button(self.root, text="Bar Chart", command=plot_bar_chart, bg="lightpink", **button_style).pack(pady=10)
        tk.Button(self.root, text="Pie Chart", command=plot_pie_chart, bg="lightgreen", **button_style).pack(pady=5)

        # Back Button with consistent style
        tk.Button(self.root, text="Back", command=self.menu_page, bg="lightgray", **button_style).pack(pady=10)

    
# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
