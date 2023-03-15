# from threading import Thread
import json
import os
import signal
import concurrent.futures
from functools import wraps
from typing import Any
import requests
from flask import request, current_app, abort
from flask_login import current_user, logout_user
from flask_login.config import EXEMPT_METHODS
from app import app
from datetime import timedelta, date
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_booking_email(customer_email, start_date, end_date, amount_paid, car_model):
    # Email configuration
    MY_ADDRESS = os.getenv('GMAIL')
    MY_PASSWORD = os.getenv('GMAIL_PASS')

    # Create message
    msg = MIMEMultipart()
    msg['From'] = MY_ADDRESS
    msg['To'] = customer_email
    msg['Subject'] = 'Booking Confirmation'

    # Add body to message
    body = f'Your booking for {car_model} from {start_date} to {end_date} has been confirmed. Amount paid: {amount_paid}'
    msg.attach(MIMEText(body, 'plain'))

    # Connect to Gmail server and send email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(MY_ADDRESS, MY_PASSWORD)
        text = msg.as_string()
        server.sendmail(MY_ADDRESS, customer_email, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as r:
        print("Error sending email.", r)


def clean_name(s: str):
    return s.title().replace('_', ' ')


def load_json(json_data: str) -> dict:
    return json.loads(json_data)


def user_state_icon(state: int):
    return '✅' if state else '❌'


def show_balance(balance: float, places: int = 2) -> str:
    return "{0:.2f}".format(float(balance))


def valid_date(start_date, end_date) -> bool:
    """Return True if the date range is valid"""
    # we can't rent car starting from yesterday :)
    today = date.today()
    if start_date < today:
        return False

    # 5. Potential or existing customers can book a vehicle up to 7 days in advance depending on availability
    if start_date > today + timedelta(days=7):
        print(f"{start_date} > {today} + {timedelta(days=7)}")
        return False

    # date range is real and not more then 7 days (included)
    if start_date < end_date <= start_date + timedelta(days=7):
        return True
    return False


def valid_booking(cursor, start_date, end_date, vehicle_id) -> bool:
    """
    This function takes a start date and an end date as input and checks if the given date range is valid for renting a car.
    The function returns `True` if the date range is valid and `False` otherwise.

    The function checks three conditions to determine if the date range is valid:
    1. The start date must not be earlier than the current date (we can't rent a car starting from tomorrow).
    2. The start date must not be more than 7 days in advance (potential or existing customers can book a vehicle up to 7 days in advance depending on availability).
    3. The date range must not exceed 7 days (included).
    """
    query = """SELECT * FROM bookings WHERE vehicle_id = %s"""
    values = (vehicle_id,)
    cursor.execute(query, values)
    bookings = cursor.fetchall()

    # Loop through all bookings to check if the given date range is allowed to rent the car
    for booking in bookings:
        exist_start = booking['start_date']
        exist_end = booking['end_date']
        bad_conditions = [
            # Check if the start date is within an existing booking period
            exist_start <= start_date < exist_end,
            # Check if the end date is within an existing booking period
            exist_start < end_date <= exist_end,
            # Check if the existing booking period is within the given date range
            start_date <= exist_start < end_date,
            start_date < exist_end <= end_date
        ]
        print(bad_conditions)
        print(f"{exist_start} <= {start_date} <= {exist_end}")
        print(f"{exist_start} <= {end_date} <= {exist_end}")
        print(f"{start_date} <= {exist_start} <= {end_date}")
        print(f"{start_date} <= {exist_end} <= {end_date}")
        if any(bad_conditions):
            return False

    # If none of the above conditions are met, the rental period is available
    return True


def allowed_booking(cursor, start_date, end_date) -> list:
    """
    This function takes a start and end date and returns a list of all vehicles from the vehicles table that can be rented for the given date range.
    by calling the valid_booking() function on each vehicle and checking if it returns True for the given date range.

    The function returns a list of allowed vehicles.
    """
    allowed_vehicles = []
    query = """SELECT * FROM vehicles"""
    cursor.execute(query)
    vehicles = cursor.fetchall()
    for vehicle in vehicles:
        if valid_booking(cursor, start_date, end_date, vehicle['id']):
            allowed_vehicles.append(vehicle)
    return allowed_vehicles


def is_admin(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()

        if not current_user.id == 1:
        #     TODO complete it
        # if not current_user.is_admin:
            abort(403)

        try:
            # current_app.ensure_sync available in Flask >= 2.0
            return current_app.ensure_sync(func)(*args, **kwargs)
        except AttributeError:  # pragma: no cover
            return func(*args, **kwargs)

    return decorated_view
