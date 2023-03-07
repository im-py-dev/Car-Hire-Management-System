import concurrent.futures
import json
import os
import signal

from flask_login import login_user, logout_user, login_required, current_user
from flask import render_template, redirect, url_for, request, flash, send_file, jsonify
from app import app
from app.utils import check_captcha, user_active, clean_name, load_json, user_state_icon, show_balance
# Import database connection object
from app import conn


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
        name = request.json['name']
        email = request.json['email']
        cursor = conn.cursor()
        query = "INSERT INTO customers (name, email) VALUES (%s, %s)"
        values = (name, email)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
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
    conn.close()
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
    conn.close()
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
    conn.close()
    return jsonify(customer), 200


@app.errorhandler(404)
def page_not_found(e):
    print(e)
    return render_template('404.html'), 404
