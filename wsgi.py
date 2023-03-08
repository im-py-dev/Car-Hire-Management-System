import schedule
from app import app as application
from daily_report import generate_daily_report


def create_app():
    schedule.every().minute.do(generate_daily_report)
    return application
