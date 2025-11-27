from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from flask_login import login_user
from app.models import Traveler, Employee
from app.database.database import SessionLocal

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    login_input = data.get("login")
    password = data.get("password")

    if not login_input or not password:
        return jsonify({"error": "Brak loginu lub hasła"}), 400

    db = SessionLocal()

    # Najpierw szukamy w Traveler
    user = db.query(Traveler).filter_by(login=login_input).first()
    role = "traveler"

    if not user:
        user = db.query(Employee).filter_by(login=login_input).first()
        role = "employee"

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Niepoprawne dane logowania"}), 401

    # logowanie przez Flask-Login
    login_user(user)

    # przygotowujemy redirect URL w zależności od roli
    redirect_url = "/traveler_dashboard" if role == "traveler" else "/employee_dashboard"

    return jsonify({
        "message": "Zalogowano pomyślnie",
        "redirect_url": redirect_url,
        "role": role
    })
