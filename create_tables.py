import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()

PASSWORD = os.getenv('SQL_PASSWORD')

db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASS'),
    'database': os.getenv('DB_NAME')
}

# Create a connection to the database
conn = mysql.connector.connect(**db_config)

# Create a table for customers
cursor = conn.cursor()
customer_table_query = '''
CREATE TABLE customers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    balance DECIMAL(10, 2) NOT NULL DEFAULT 0.00
);
'''
cursor.execute(customer_table_query)

# Create a table for vehicles
vehicle_table_query = '''
CREATE TABLE vehicles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    model VARCHAR(255) NOT NULL,
    category ENUM('small', 'family', 'van') NOT NULL,
    daily_rate DECIMAL(10, 2) NOT NULL
);
'''
cursor.execute(vehicle_table_query)

# Create a table for bookings
booking_table_query = '''
CREATE TABLE bookings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    vehicle_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    amount_paid DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
);
'''
cursor.execute(booking_table_query)
