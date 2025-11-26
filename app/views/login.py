from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models import Traveler, Employee
from werkzeug.security import check_password_hash


auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    login = data.get("login")
    password = data.get("password")

    if not login or not password:
        return jsonify({"error": "Missing login or password"}), 400

    db: Session = SessionLocal()

    user = db.query(Traveler).filter(Traveler.login == login).first()
    message = "Logged in as citizen (mock)"

    if not user:
        message = "Logged in as employee (mock)"
        user = db.query(Employee).filter(Employee.login == login).first()

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    if not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    
    return jsonify({
        "message": message,
        "pesel": user.pesel,
        "login": user.login,
        "role": getattr(user, "role", "citizen")
    })


