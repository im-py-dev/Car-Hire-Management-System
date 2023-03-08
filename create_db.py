from app import app, db
from app.models import User

# create tables for ORM (user table only)
with app.app_context():
    db.create_all()
