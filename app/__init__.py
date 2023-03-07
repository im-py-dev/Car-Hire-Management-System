import threading
import concurrent.futures
import os
import json
import signal
import requests
from dotenv import load_dotenv
from flask import Flask
# from flask_wtf import FlaskForm
# from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
# from flask_migrate import Migrate
import mysql.connector

app = Flask(__name__)

load_dotenv()
FLASK_DEBUG = int(os.getenv('FLASK_DEBUG'))

if FLASK_DEBUG:
    app.config.from_object('app.config.DevelopmentConfig')
else:
    app.config.from_object('app.config.ProductionConfig')


# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': os.getenv('SQL_PASSWORD'),
    'database': 'car_hire'
}

# Create a connection to the database
conn = mysql.connector.connect(**db_config)

# bcrypt = Bcrypt(app)
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'

# from app.views.admin import base, payments, translations, languages, deposits
# from app.views.user import base, translation
