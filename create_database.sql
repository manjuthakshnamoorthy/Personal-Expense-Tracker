-- Create Database
CREATE DATABASE IF NOT EXISTS expense_tracker;
USE expense_tracker;

-- Create 'users' table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(100)
);

-- Create 'expenses' table
CREATE TABLE IF NOT EXISTS expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    amount DECIMAL(10, 2),
    category VARCHAR(50),
    expense_date DATE,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create 'income' table
CREATE TABLE IF NOT EXISTS income (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    amount DECIMAL(10, 2),
    source VARCHAR(100),
    income_date DATE,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create a view for highest spending category
CREATE OR REPLACE VIEW highest_spending_category AS
SELECT 
    user_id,
    category,
    SUM(amount) AS total_spent
FROM 
    expenses
GROUP BY 
    user_id, category
ORDER BY 
    total_spent DESC;
