import csv
import datetime
import os
from app import conn


def generate_daily_report(now=False):
    # Get current date
    today = datetime.date.today()
    # to make sure all reports included, we create for yesterday
    yesterday = today - datetime.timedelta(days=1)
    used_day = today if now else yesterday
    # Query the database to get all bookings for the current day
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM bookings WHERE start_date <= %s"
    values = (used_day,)
    cursor.execute(query, values)
    bookings = cursor.fetchall()
    cursor.close()

    # Open a new file for writing in CSV format
    filename = f"{used_day.strftime('%Y-%m-%d')}_bookings_report.csv"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(current_dir, "reports", filename)
    with open(filepath, 'w', newline='') as csvfile:
        # Create a CSV writer object
        writer = csv.writer(csvfile)

        # Write the header row
        writer.writerow(['Booking ID', 'Customer ID', 'Vehicle ID', 'Start Date', 'End Date', 'Amount Paid'])

        # Loop over the bookings and write each one to the CSV file as a new row
        for booking in bookings:
            writer.writerow([
                booking['id'], booking['customer_id'], booking['vehicle_id'], booking['start_date'],
                booking['end_date'], booking['amount_paid']])

    # Close the file
    csvfile.close()

    print(f"Daily report generated: {filepath}")
    return filepath
