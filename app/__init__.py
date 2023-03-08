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
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

load_dotenv()
FLASK_DEBUG = int(os.getenv('FLASK_DEBUG'))
print(FLASK_DEBUG)
if FLASK_DEBUG:
    app.config.from_object('app.config.DevelopmentConfig')
else:
    app.config.from_object('app.config.ProductionConfig')


# Database configuration
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASS'),
    'database': os.getenv('DB_NAME')
}

# Create a connection to the database
conn = mysql.connector.connect(**db_config)

# ORM + Login Manager is not part of the task, but I used them just to make it look like real project.
# like how we can get payment without login, asking customer for his id XD
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# from app.views.admin import base
from .views.user import base
