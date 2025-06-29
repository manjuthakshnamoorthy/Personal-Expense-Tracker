# 💰 Personal Expense Tracker

A simple desktop application built using **Python (Tkinter)** and **MySQL** to help users track their daily expenses and income.

---

## 📌 Features

- 🧑 User registration and login
- 📤 Add daily expenses with category and description
- 💵 Add sources of income
- 📊 View total income, expenses, and balance
- 📂 Categorized view of spending
- 📈 View for highest spending category (MySQL View)
- 🔐 Secure MySQL connectivity
- 🖥️ GUI powered by Tkinter

---

## 🛠️ Tech Stack

- **Frontend (GUI)**: Tkinter (Python)
- **Backend**: Python
- **Database**: MySQL
- **Tools**: MySQL Workbench / XAMPP / phpMyAdmin

---

## 🧩 Database Structure

**Database Name**: `expense_tracker`

### Tables:
- `users` – user credentials
- `expenses` – user’s expense entries
- `income` – user’s income records

### View:
- `highest_spending_category` – calculated view to find top spending categories per user

📁 SQL setup script available inside the repo (`expense_tracker.sql`)

---

## 🚀 How to Run

1. 🔧 Make sure **MySQL server** is running.
2. ⚙️ Import the `expense_tracker.sql` into MySQL to set up the database.
3. 🐍 Install Python dependencies (if any).
4. ▶️ Run the main Python script:

```bash
python app.py
