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

from app import app, bcrypt, db
from app.models import User, TelegramUser


def user_active(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        user = User.query.filter_by(username=request.form.get('username')).first() or current_user
        if request.method in EXEMPT_METHODS or current_app.config.get("LOGIN_DISABLED"):
            pass
        elif not current_user.is_authenticated or user.state == 0:
            return current_app.login_manager.unauthorized()
        try:
            return current_app.ensure_sync(func)(*args, **kwargs)
        except AttributeError:
            return func(*args, **kwargs)

    return decorated_view


def is_admin(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in EXEMPT_METHODS or current_app.config.get("LOGIN_DISABLED"):
            pass
        elif not current_user.is_authenticated or current_user.id != 1:
            return current_app.login_manager.unauthorized()
        try:
            return current_app.ensure_sync(func)(*args, **kwargs)
        except AttributeError:
            return func(*args, **kwargs)

    return decorated_view


def allow_one_time(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in EXEMPT_METHODS or current_app.config.get("LOGIN_DISABLED"):
            pass

        elif len(User.query.all()) == 0:
            try:
                return current_app.ensure_sync(func)(*args, **kwargs)
            except AttributeError:
                return func(*args, **kwargs)

        elif not current_user.is_authenticated or current_user.id != 1:
            return current_app.login_manager.unauthorized()
        try:
            return current_app.ensure_sync(func)(*args, **kwargs)
        except AttributeError:
            return func(*args, **kwargs)

    return decorated_view


def check_captcha():
    verify_url = app.config.get('VERIFY_URL')
    recaptcha_secret_key = app.config.get('RECAPTCHA_SECRET_KEY')
    try:
        secret_response = request.form['g-recaptcha-response']
        verify_response = requests.post(url=f'{verify_url}?secret={recaptcha_secret_key}&response={secret_response}').json()
        return verify_response['success'] and verify_response['score'] > 0.5
    except KeyError:
        return False
    except Exception:
        return False


def generate_hashed_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')


def clean_name(s: str):
    return s.title().replace('_', ' ')


def load_json(json_data: str) -> dict:
    return json.loads(json_data)


def user_state_icon(state: int):
    return '✅' if state else '❌'


def show_balance(balance: float, places: int = 2):
    return "{0:.2f}".format(float(balance))
