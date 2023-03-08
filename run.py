import os
from dotenv import load_dotenv
from app import app
import schedule
from daily_report import generate_daily_report

load_dotenv()
port = os.getenv('PORT') or 80
host = os.getenv('HOST') or "0.0.0.0"

if __name__ == "__main__":
    # Schedule the report to run every day at 8:00 AM
    # TODO not tested yet
    schedule.every().day.at('00:01').do(generate_daily_report)

    app.run(debug=app.debug, port=port, host=host)
