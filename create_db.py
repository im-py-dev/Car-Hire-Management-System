from app import app, db
from app.models import User

# create tables
with app.app_context():
    db.create_all()
