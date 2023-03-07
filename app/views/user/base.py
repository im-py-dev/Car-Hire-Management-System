import concurrent.futures
import json
import os
import signal
from datetime import datetime

from flask_login import login_user, logout_user, login_required, current_user, LoginManager, UserMixin
from flask import render_template, redirect, url_for, request, flash, send_file, jsonify, abort
from app import app, login_manager, conn, db
from app.models import User
from app.utils import clean_name, load_json, user_state_icon, show_balance, valid_date
from werkzeug.security import generate_password_hash, check_password_hash
# Import database connection object


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=['GET'])
def home():
    return render_template('base.html'), 200


# Endpoint to add a new customer
@app.route('/customers', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'GET':
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM customers"
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return render_template('customers.html', customers=rows), 200

    elif request.method == 'POST':
        cursor = conn.cursor()
        name = request.form['name']
        email = request.form['email']
        query = "INSERT INTO customers (name, email) VALUES (%s, %s)"
        values = (name, email)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        return jsonify({"message": "Customer added successfully"}), 201


# Endpoint to update a customer
@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    name = request.json['name']
    email = request.json['email']
    balance = request.json['balance']
    cursor = conn.cursor()
    query = "UPDATE customers SET name = %s, email = %s , balance = %s WHERE id = %s"
    values = (name, email, balance, id)
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    return jsonify({"message": "Customer updated successfully"}), 200


# Endpoint to delete a customer
@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    cursor = conn.cursor()
    query = "DELETE FROM customers WHERE id = %s"
    values = (id,)
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    return jsonify({"message": "Customer deleted successfully"}), 200


# Endpoint to get a customer by ID
@app.route('/customers/<int:id>', methods=['GET'])
def get_customer(id):
    cursor = conn.cursor()
    query = "SELECT * FROM customers WHERE id = %s"
    values = (id,)
    cursor.execute(query, values)
    row = cursor.fetchone()
    if row is None:
        return jsonify({"message": "Customer not found"}), 404
    customer = {
        "id": row[0],
        "name": row[1],
        "email": row[2],
        "balance": float(row[3])
    }
    cursor.close()
    return jsonify(customer), 200


@app.route('/vehicles')
def view_vehicles():
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM vehicles"
    cursor.execute(query)
    vehicles = cursor.fetchall()
    cursor.close()
    return render_template('vehicles.html', vehicles=vehicles)


@app.route('/availability', methods=['GET', 'POST'])
def vehicle_availability():
    if request.method == 'POST':
        start_date_str = request.form['start_date']
        end_date_str = request.form['end_date']
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        if not valid_date(start_date, end_date):
            context = {
                'vehicles': [],
                'start_date': start_date_str,
                'end_date': end_date_str,
                'error': "Please enter valid date",
            }
            print(context)
            return render_template('availability.html', **context), 200

        cursor = conn.cursor(dictionary=True)
        query = """SELECT * FROM vehicles WHERE id NOT IN (
                    SELECT DISTINCT(vehicle_id) FROM bookings 
                    WHERE start_date <= %s AND end_date >= %s
                    )"""
        cursor.execute(query, (end_date, start_date))
        rows = cursor.fetchall()
        cursor.close()
        context = {
            'vehicles': rows,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'error': "" if rows else "No vehicles available",
        }
        return render_template('availability.html', **context), 200

    else:
        return render_template('availability.html'), 200


@app.route('/bookings/create/<int:vehicle_id>', methods=['GET', 'POST'])
def create_booking(vehicle_id):
    if request.method == 'GET':
        # Retrieve vehicle information
        start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()

        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM vehicles WHERE id=%s"
        values = (vehicle_id,)
        cursor.execute(query, values)
        vehicle = cursor.fetchone()
        cursor.close()

        # Render the booking form
        return render_template('create_booking.html', vehicle=vehicle, start_date=start_date, end_date=end_date)

    elif request.method == 'POST':
        # Retrieve booking data from the form
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        # customer_name = request.form['customer_name']
        # customer_email = request.form['customer_email']

        # it should be customer id, anyway it is just a task
        customer_id = current_user.id

        # Convert dates to datetime objects
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        # Check if the booking is valid
        if not valid_date(start_date, end_date):
            return jsonify({"error": "Invalid booking period"}), 400

        # First, get the daily_rate from the vehicles table
        cursor = conn.cursor()
        query = "SELECT daily_rate FROM vehicles WHERE id = %s"
        values = (vehicle_id,)
        cursor.execute(query, values)
        result = cursor.fetchone()[0]
        daily_rate = result

        # Calculate the amount to be paid
        delta = end_date - start_date
        num_days = delta.days
        amount_paid = num_days * daily_rate

        # Retrieve customer balance from database
        query = "SELECT balance FROM customers WHERE id = %s"
        values = (customer_id,)
        cursor.execute(query, values)
        result = cursor.fetchone()[0]
        user_balance = result

        # Calculate new balance after subtracting amount paid
        new_balance = user_balance - amount_paid
        print("new_balance = user_balance - amount_paid")
        print(f"{new_balance} = {user_balance} - {amount_paid}")
        if new_balance < 0:
            return "There is not enough balance"

        # Update customer balance in the database
        query = "UPDATE customers SET balance = %s WHERE id = %s"
        values = (new_balance, customer_id)
        cursor.execute(query, values)

        # Insert the new booking into the database
        query = "INSERT INTO bookings (customer_id, vehicle_id, start_date, end_date, amount_paid) VALUES (%s, %s, %s, %s, %s)"
        values = (customer_id, vehicle_id, start_date, end_date, amount_paid)
        cursor.execute(query, values)
        # Now we can commit the changes.
        conn.commit()
        cursor.close()

        # Redirect to the vehicle's page with a success message
        return 'booking Created.'


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "User already exists"
        else:
            # Create new user
            new_user = User(username=username, password=generate_password_hash(password, method='sha256'))
            # Add new user to database
            db.session.add(new_user)
            db.session.commit()

            # create customer
            cursor = conn.cursor()
            name = request.form['name']
            email = request.form['email']
            query = "INSERT INTO customers (name, email) VALUES (%s, %s)"
            values = (name, email)
            cursor.execute(query, values)
            conn.commit()
            cursor.close()

            return redirect(url_for('login'))
    else:
        return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']
        # Find user by username
        user = User.query.filter_by(username=username).first()
        if user:
            # Check password hash
            if check_password_hash(user.password, password):
                # Log user in and redirect to homepage
                login_user(user)
                return redirect(url_for('home'))
        # If user doesn't exist or password is incorrect, show error message
        return render_template('login.html', error='Invalid username or password')
    else:
        # If user is already logged in, redirect to homepage
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        return render_template('login.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
