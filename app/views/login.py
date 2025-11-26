from flask import Blueprint, request, jsonify, url_for
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
    is_traveler = True
    message = "Logged in as citizen (mock)"

    if not user:
        message = "Logged in as employee (mock)"
        user = db.query(Employee).filter(Employee.login == login).first()

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    if not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    redirect_url = None

    if is_traveler:
        # Generujemy link do dashboardu zdefiniowanego w routes.py
        # 'notifications' to nazwa blueprintu z routes.py, 'traveler_dashboard' to nazwa funkcji
        redirect_url = url_for('notifications.traveler_dashboard', pesel=user.pesel)
    else:
        # Opcjonalnie: Przekierowanie dla pracownika (jeśli masz taki widok)
        redirect_url = "/register_employee_page"  # Tymczasowo lub inny widok

    return jsonify({
        "message": "Logged in successfully",
        "redirect_url": redirect_url,  # <--- To jest kluczowe dla JavaScriptu
        "pesel": user.pesel,
        "role": getattr(user, "role", "citizen")
    })


