from tkinter import *
from tkinter import messagebox
import sqlite3

# Database Connection setup
def setup_db():
    try:
        # Connect to SQLite database (creates it if it doesn't exist)
        conn = sqlite3.connect("employee_db.db")
        cursor = conn.cursor()

        # Create the employees table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                emp_id TEXT PRIMARY KEY,
                name TEXT,
                position TEXT,
                salary INTEGER
            )
        """)
        conn.commit()
        return conn, cursor
    except sqlite3.Error as err:
        return None, None

# ---------------- FUNCTIONS ---------------- #

def add_employee():
    emp_id = entry_id.get()
    name = entry_name.get()
    position = entry_position.get()
    salary = entry_salary.get()

    if not all([emp_id, name, position, salary]):
        messagebox.showwarning("Warning", "All fields are required")
        return

    try:
        salary = int(salary)
    except ValueError:
        messagebox.showerror("Error", "Salary must be a valid number")
        return

    try:
        query = "INSERT INTO employees (emp_id, name, position, salary) VALUES (?, ?, ?, ?)"
        values = (emp_id, name, position, salary)
        cursor.execute(query, values)
        conn.commit()
        messagebox.showinfo("Success", "Employee Added Successfully")
        clear_entries()
        display_employees()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Employee ID already exists")
    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong: {e}")

def remove_employee():
    emp_id = entry_id.get()
    
    if not emp_id:
        messagebox.showwarning("Warning", "Employee ID is required for removal")
        return

    try:
        # Check if exists first
        cursor.execute("SELECT * FROM employees WHERE emp_id=?", (emp_id,))
        if not cursor.fetchone():
            messagebox.showerror("Error", "Employee Not Found")
            return

        query = "DELETE FROM employees WHERE emp_id=?"
        cursor.execute(query, (emp_id,))
        conn.commit()
        messagebox.showinfo("Success", "Employee Removed Successfully")
        clear_entries()
        display_employees()
    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong: {e}")

def promote_employee():
    emp_id = entry_id.get()
    increment_str = entry_salary.get()

    if not emp_id or not increment_str:
        messagebox.showwarning("Warning", "Employee ID and Increment (in Salary field) are required")
        return

    try:
        increment = int(increment_str)
    except ValueError:
        messagebox.showerror("Error", "Increment must be a valid number")
        return

    try:
        query = "SELECT salary FROM employees WHERE emp_id=?"
        cursor.execute(query, (emp_id,))
        result = cursor.fetchone()

        if result:
            new_salary = result[0] + increment
            update_query = "UPDATE employees SET salary=? WHERE emp_id=?"
            cursor.execute(update_query, (new_salary, emp_id))
            conn.commit()
            messagebox.showinfo("Success", f"Employee Promoted! New Salary: {new_salary}")
            clear_entries()
            display_employees()
        else:
            messagebox.showerror("Error", "Employee Not Found")
    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong: {e}")

def display_employees():
    if not cursor:
        return
    try:
        cursor.execute("SELECT * FROM employees")
        records = cursor.fetchall()

        display_text.delete("1.0", END)
        if not records:
            display_text.insert(END, "No employees found.\n")
            return

        for row in records:
            display_text.insert(END, f"ID: {row[0]} | Name: {row[1]} | Position: {row[2]} | Salary: {row[3]}\n")
    except Exception as e:
        display_text.insert(END, f"Error fetching records: {e}\n")

def clear_entries():
    entry_id.delete(0, END)
    entry_name.delete(0, END)
    entry_position.delete(0, END)
    entry_salary.delete(0, END)

# ---------------- UI ---------------- #

root = Tk()
root.title("Employee Management System")
root.geometry("600x550")
root.configure(padx=20, pady=20)

# Connect to DB
conn, cursor = setup_db()
if not conn:
    messagebox.showwarning("Database Connection Failed", "Failed to setup local SQLite database.")

# Title Label
Label(root, text="Employee Management System", font=("Helvetica", 16, "bold")).pack(pady=(0, 15))

# Input Frame
frame = Frame(root)
frame.pack(pady=10)

Label(frame, text="Employee ID:", font=("Arial", 10)).grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_id = Entry(frame, width=30)
entry_id.grid(row=0, column=1, padx=10, pady=5)

Label(frame, text="Name:", font=("Arial", 10)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
entry_name = Entry(frame, width=30)
entry_name.grid(row=1, column=1, padx=10, pady=5)

Label(frame, text="Position:", font=("Arial", 10)).grid(row=2, column=0, padx=10, pady=5, sticky="e")
entry_position = Entry(frame, width=30)
entry_position.grid(row=2, column=1, padx=10, pady=5)

Label(frame, text="Salary / Increment:", font=("Arial", 10)).grid(row=3, column=0, padx=10, pady=5, sticky="e")
entry_salary = Entry(frame, width=30)
entry_salary.grid(row=3, column=1, padx=10, pady=5)

# Buttons Frame
btn_frame = Frame(root)
btn_frame.pack(pady=15)

Button(btn_frame, text="Add Employee", width=15, bg="lightblue", command=add_employee).grid(row=0, column=0, padx=10, pady=5)
Button(btn_frame, text="Remove Employee", width=15, bg="lightcoral", command=remove_employee).grid(row=0, column=1, padx=10, pady=5)
Button(btn_frame, text="Promote Employee", width=15, bg="lightgreen", command=promote_employee).grid(row=1, column=0, padx=10, pady=5)
Button(btn_frame, text="Display Employees", width=15, bg="lightyellow", command=display_employees).grid(row=1, column=1, padx=10, pady=5)

# Display Area
Label(root, text="Employee Records:", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(10, 0))
display_text = Text(root, height=12, width=70, font=("Courier", 10))
display_text.pack(pady=5)

# Initial load
if cursor:
    display_employees()

root.mainloop()