from app import app, db
from app.models import User

# create tables for ORM (user table only)
with app.app_context():
    db.create_all()

# this equal:
# CREATE TABLE user (
#     id INT PRIMARY KEY AUTO_INCREMENT,
#     username VARCHAR(255) NOT NULL UNIQUE,
#     password VARCHAR(255) NOT NULL,
# );
