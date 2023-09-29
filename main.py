
import sqlite3
import datetime
# Connect to the database
conn = sqlite3.connect('bookstore.db')
cursor = conn.cursor()
# Create Customers table
cursor.execute('''CREATE TABLE IF NOT EXISTS Customers (
    Customer_Id INTEGER PRIMARY KEY,
    Customer_Name TEXT,
    Customer_Add1 TEXT,
    Customer_Add2 TEXT,
    Customer_Pincode INTEGER,
    Joined_Date TEXT,
    Monthly_Payment REAL,
    Active_Inactive TEXT
)''')

# Create Books table
cursor.execute('''CREATE TABLE IF NOT EXISTS Books (
    Book_Id INTEGER PRIMARY KEY,
    Book_Name TEXT,
    Book_Author TEXT,
    Book_Type TEXT,
    Published_Date TEXT,
    Total_No_Books INTEGER,
    Received_Date TEXT,
    Book_Condition TEXT
)''')

# Create Book_Transactions table
cursor.execute('''CREATE TABLE IF NOT EXISTS Book_Transactions (
    Book_Id INTEGER,
    Customer_Id INTEGER,
    Transacted_Date TEXT,
    Due_Date TEXT,
    Returned_Date TEXT,
    FOREIGN KEY (Book_Id) REFERENCES Books (Book_Id),
    FOREIGN KEY (Customer_Id) REFERENCES Customers (Customer_Id)
)''')





# Function to get stock of all books or a particular book
def get_book_stock(book_id=None):
    if book_id is None:
        cursor.execute("SELECT Book_Id, Book_Name, Stock FROM Books")
    else:
        cursor.execute("SELECT Book_Id, Book_Name, Stock FROM Books WHERE Book_Id = ?", (book_id,))
    return cursor.fetchall()

# Function to get due date of a book
def get_due_date(book_id):
    cursor.execute("SELECT Due_Date FROM Book_Transactions WHERE Book_Id = ? AND Returned_Date IS NULL", (book_id,))
    return cursor.fetchone()

# Function to get overdue of a book
def get_overdue(book_id):
    cursor.execute("SELECT Due_Date, Returned_Date FROM Book_Transactions WHERE Book_Id = ? AND Returned_Date IS NOT NULL", (book_id,))
    rows = cursor.fetchall()
    overdue = []
    for row in rows:
        due_date = datetime.datetime.strptime(row[0], '%Y-%m-%d')
        returned_date = datetime.datetime.strptime(row[1], '%Y-%m-%d')
        days_overdue = (returned_date - due_date).days
        if days_overdue > 0:
            overdue.append(days_overdue)
    return overdue

# Function to get active customers
def get_active_customers():
    cursor.execute("SELECT Customer_Name FROM Customers WHERE Active_Inactive = 'Active'")
    return cursor.fetchall()

# Function to get monthly rent not paid by customers
def get_unpaid_rent():
    cursor.execute("SELECT Customer_Name, Monthly_Payment FROM Customers WHERE Active_Inactive = 'Active'")
    unpaid_rent = []
    rows = cursor.fetchall()
    for row in rows:
        customer_name = row[0]
        monthly_payment = row[1]
        customer_id = row[2]
        cursor.execute("SELECT SUM(Monthly_Payment) FROM Book_Transactions WHERE Customer_Id = ? AND Returned_Date IS NULL", (customer_id,))
        total_payment = cursor.fetchone()[0]
        if total_payment is None:
            unpaid_rent.append((customer_name, monthly_payment))
        elif total_payment < monthly_payment:
            unpaid_rent.append((customer_name, monthly_payment - total_payment))
    return unpaid_rent

# Function to get book condition
def get_book_condition(condition):
    if condition == 'G':
        cursor.execute("SELECT Book_Id, Book_Name FROM Books WHERE Book_Condition = 'Good'")
    elif condition == 'B':
        cursor.execute("SELECT Book_Id, Book_Name FROM Books WHERE Book_Condition = 'Bad'")
    else:
        cursor.execute("SELECT Book_Id, Book_Name FROM Books")
    return cursor.fetchall()# Display book stock
stock = get_book_stock()
print("Book Stock:")
for book in stock:
    book_id, book_name, stock = book
    print(f"Book ID: {book_id}, Book Name: {book_name}, Stock: {stock}")

# Display active customers
active_customers = get_active_customers()
print("Active Customers:")
for customer in active_customers:
    customer_name = customer[0]
    print(f"Customer Name: {customer_name}")

# Display unpaid rent
unpaid_rent = get_unpaid_rent()
print("Unpaid Rent:")
for customer_rent in unpaid_rent:
    customer_name, rent = customer_rent
    print(f"Customer Name: {customer_name}, Monthly Rent: {rent}")

# Display books in a specific condition (e.g. good condition)
book_condition = get_book_condition('G')
print("Books in Good Condition:")
for book in book_condition:
    book_id, book_name = book
    print(f"Book ID: {book_id}, Book Name: {book_name}")


# Close the connection
conn.close()
