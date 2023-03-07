# from threading import Thread
import concurrent.futures
import json
import os
import signal
from functools import wraps
from typing import Any
import requests
from flask import request, current_app
from flask_login import current_user, logout_user
from flask_login.config import EXEMPT_METHODS
from app import app
from datetime import timedelta, date


def clean_name(s: str):
    return s.title().replace('_', ' ')


def load_json(json_data: str) -> dict:
    return json.loads(json_data)


def user_state_icon(state: int):
    return '✅' if state else '❌'


def show_balance(balance: float, places: int = 2):
    return "{0:.2f}".format(float(balance))


def valid_date(start_date, end_date):
    today = date.today()
    if start_date < today:
        return False

    if start_date < end_date <= start_date + timedelta(days=7):
        return True
    return False
