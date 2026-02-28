from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # renter or customer

    # -----------------------
    # Set Password
    # -----------------------
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # -----------------------
    # Check Password
    # -----------------------
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)