
from flask import Flask
from flask_restful import Resource, Api
import sqlite3
import datetime

app = Flask(__name__)
api = Api(app)

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

# Insert data into customers table
cursor.execute("INSERT INTO Customers (Customer_Name, Customer_Add1, Customer_Add2, Customer_Pincode, Joined_Date, Monthly_Payment, Active_Inactive) VALUES (?, ?, ?, ?, ?, ?, ?)", ('John Doe', '123 Street', 'Apt 4', 12345, '2022-01-01', 50.00, 'Active'))

cursor.execute("INSERT INTO Customers (Customer_Name, Customer_Add1, Customer_Add2, Customer_Pincode, Joined_Date, Monthly_Payment, Active_Inactive) VALUES (?, ?, ?, ?, ?, ?, ?)", ('Jane Smith', '456 Street', 'Apt 8', 54321, '2022-02-01', 70.00, 'Active'))


# Insert data into Books table
# Insert data into Books table without specifying Book_Id
cursor.execute("INSERT INTO Books (Book_Name, Book_Author, Book_Type, Published_Date, Total_No_Books, Received_Date, Book_Condition) VALUES (?, ?, ?, ?, ?, ?, ?)", ('Book 1', 'Author 1', 'Fiction', '2021-01-01', 10, '2021-01-01', 'Good'))

cursor.execute("INSERT INTO Books (Book_Name, Book_Author, Book_Type, Published_Date, Total_No_Books, Received_Date, Book_Condition) VALUES (?, ?, ?, ?, ?, ?, ?)", ('Book 2', 'Author 2', 'Non-Fiction', '2020-01-01', 5, '2020-01-01', 'Bad'))

conn.commit()

class BookStock(Resource):
    def get(self, book_id=None):
        if book_id is None:
            cursor.execute("SELECT Book_Id, Book_Name, Stock FROM Books")
        else:
            cursor.execute("SELECT Book_Id, Book_Name, Stock FROM Books WHERE Book_Id = ?", (book_id,))
        return cursor.fetchall()


class DueDate(Resource):
    def get(self, book_id):
        cursor.execute("SELECT Due_Date FROM Book_Transactions WHERE Book_Id = ? AND Returned_Date IS NULL", (book_id,))
        return cursor.fetchone()


class Overdue(Resource):
    def get(self, book_id):
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


class ActiveCustomers(Resource):
    def get(self):
        cursor.execute("SELECT Customer_Name FROM Customers WHERE Active_Inactive = 'Active'")
        return cursor.fetchall()


class UnpaidRent(Resource):
    def get(self):
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


class BookCondition(Resource):
    def get(self, condition):
        if condition == 'G':
            cursor.execute("SELECT Book_Id, Book_Name FROM Books WHERE Book_Condition = 'Good'")
        elif condition == 'B':
            cursor.execute("SELECT Book_Id, Book_Name FROM Books WHERE Book_Condition = 'Bad'")
        else:
            cursor.execute("SELECT Book_Id, Book_Name FROM Books")
        return cursor.fetchall()


api.add_resource(BookStock, '/books', '/books/<int:book_id>',methods=['GET'])
api.add_resource(DueDate, '/due-date/<int:book_id>',methods=['GET'])
api.add_resource(Overdue, '/overdue/<int:book_id>',methods=['GET'])
api.add_resource(ActiveCustomers, '/active-customers',methods=['GET'])
api.add_resource(UnpaidRent, '/unpaid-rent',methods=['GET'])
api.add_resource(BookCondition, '/book-condition/<string:condition>',methods=['GET'])


if __name__ == '__main__':
    app.run(debug=True,port=5000)

# Close the connection
conn.close()
