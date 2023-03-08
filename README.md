# Car Hire Management System.

## Questions
```
[+]  If a vehicle is available, the customer's details are recorded (if not stored already) and a new booking is made.

[+] Customers must pay for the vehicle at the time of hire.

[Q] the first point refers to the customer can place a booking without login
second refers to the existing login system to the customer can pay
so I just got confused, please explain it more
__________________________________
[+] If the booking has been made in advance, a confirmation letter will be sent to the customer.
[Q] is it a confirmation email? that should be clicked so the booking got confirmed. or just email to say  "hay, here is your booking"
__________________________________
[+] On receiving an enquiry, employees are required to check availability of cars and vans.
[Q] does Database should have employees users and they receive a booking, then accept it/refuse it?
__________________________________
[+] A report is printed at the start of each day showing the bookings for that particular day.
[Q] is this a background task or an admin widget?
```

## A- Requirements:
Details: The main focus of the business is renting cars and vans, and the database is to manage the
booking system.
---
1. Vehicles are categorized into small cars (suitable for carrying up to 4 people), family cars
(suitable for carrying up to 7 adults), and vans.

2. Information stored for each booking includes customer, car, date of hire and date on which the
vehicle is to be returned.

3. A customer cannot hire a car for longer than a week.

4. If a vehicle is available, the customer&#39;s details are recorded (if not stored already) and a new
booking is made.

5. Potential or existing customers can book a vehicle up to 7 days in advance depending on
availability

6. Customers must pay for the vehicle at the time of hire.

7. On receiving an enquiry, employees are required to check availability of cars and vans.

8. An invoice is written at the time of booking for the customer.

9. If the booking has been made in advance, a confirmation letter will be sent to the customer.

10. A report is printed at the start of each day showing the bookings for that particular day.
---
## B- Deliverables:
(all deliverables should be placed on GIT (your personal Github account). and we may
want to check your commits and branches.)
1. An ERD diagram describes the DB design, field types, relationships, constraints, etc. ( a
screenshot on your repo is fine)
![image](https://user-images.githubusercontent.com/94250125/223620113-be1dc1e2-e3ee-417f-b7b3-c7d1dbddadb1.png)
___
2. SQL which implements above ERD. (MySQL)
```
CREATE TABLE user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
);

CREATE TABLE customers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    balance DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    FOREIGN KEY (id) REFERENCES user(id)
);

CREATE TABLE vehicles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    model VARCHAR(255) NOT NULL,
    category ENUM('small', 'family', 'van') NOT NULL,
    daily_rate DECIMAL(10, 2) NOT NULL
);

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
```
___
3. A Python microservice implemented using Flask microframework that should connect to MySQL
DB and have the following endpoints:
an endpoint to add new customer.
a. an endpoint to update customer
b. an endpoint to delete customer
c. an endpoint to get customer.
### Access ready [PostMan API](https://warped-comet-217425.postman.co/workspace/Car-Hire-Management-System~921e4b92-5739-43d6-8f06-26c6a697943b/collection/21532671-3bc2fe70-fa3b-485a-b77e-a3e6d0e72e4d?action=share&creator=21532671)
___
### using ORMs VS direct access.

```
In summary, using an ORM tool can be beneficial in many cases, especially for rapid prototyping or when portability is important.
However, in some cases, direct access to the database may be preferred, especially in performance-critical applications.
Ultimately, the decision to use an ORM tool should be made based on the specific needs and requirements of the project.
```
---
# Installation

### Create `.env` file
```
FLASK_DEBUG=1
HOST="0.0.0.0"
PORT=80
DB_USER="root"
DB_PASS="USER_PASS"
DB_HOST="localhost"
DB_PORT="3306"
DB_NAME="MY_DATABASE"
GMAIL="YOUR_GMAIL"
GMAIL_PASS="YOUR_PASSWORD"
```
### change `USER_PASS` `YOUR_GMAIL` `YOUR_PASSWORD`
___
MySQL `CREATE DATABASE MY_DATABASE;`
___
### `pip install pipenv`
### `pipenv shell`
### `pipenv install`
### `python create_db.py `
### `python create_tables.py `
### `python run.py `
___
# Deployment
## (Waitress)
`waitress-serve --host 0.0.0.0 --port 80 --call wsgi:create_app`
___
## background task in deployment

## Using process manager
##### there are other better method but I'll use this for fast

#### Create a new file `/etc/systemd/system/daily-report.service` with the following contents:

```
[Unit]
Description=Daily report generator

[Service]
Type=simple
WorkingDirectory=/path_to_app/
ExecStart=/usr/bin/python /path_to_app/daily_report.py
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Enable and start the service:

```
sudo systemctl enable daily-report.service
sudo systemctl start daily-report.service
```
