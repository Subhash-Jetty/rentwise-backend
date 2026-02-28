from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models.user import User
from app import db

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# =========================================================
# REGISTER
# =========================================================
@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    # ------------------------
    # VALIDATION
    # ------------------------
    if not email or not password or not role:
        return jsonify({"error": "Missing fields"}), 400

    if role not in ["renter", "customer"]:
        return jsonify({"error": "Invalid role"}), 400

    # ------------------------
    # CHECK EXISTING USER
    # ------------------------
    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({"error": "User already exists"}), 409

    # ------------------------
    # CREATE USER
    # ------------------------
    new_user = User(
        email=email,
        role=role
    )

    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


# =========================================================
# LOGIN
# =========================================================
@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    # ------------------------
    # VALIDATION
    # ------------------------
    if not email or not password:
        return jsonify({"error": "Missing credentials"}), 400

    user = User.query.filter_by(email=email).first()

    # ------------------------
    # USER NOT FOUND
    # ------------------------
    if not user:
        return jsonify({
            "error": "User not found. Please register."
        }), 404

    # ------------------------
    # WRONG PASSWORD
    # ------------------------
    if not user.check_password(password):
        return jsonify({
            "error": "Incorrect password"
        }), 401

    # ------------------------
    # SUCCESS
    # ------------------------
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "access_token": access_token,
        "role": user.role,
        "message": "Login successful"
    }), 200