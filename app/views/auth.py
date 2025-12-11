from flask import Blueprint, request, jsonify, redirect, url_for, render_template
from werkzeug.security import check_password_hash, generate_password_hash 
from flask_login import login_user, logout_user
from app.models import Traveler, Employee
from app.database.database import SessionLocal
from app.mock_data import *

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    login_input = data.get("login")
    password = data.get("password")

    if not login_input or not password:
        return jsonify({"error": "Brak loginu lub hasła"}), 400

    db = SessionLocal()

    try:
        # 1. Sprawdzamy Podrónego 
        user = db.query(Traveler).filter_by(login=login_input).first()
        role = "traveler"

        # 2. Jeśli nie znaleziono podróżnego, sprawdzamy Pracownika
        if not user:
            role = "employee"

            # --- SPECIAL CASE: MOCK ADMIN ---
            if login_input == MOCK_ADMIN["login"] and password == MOCK_ADMIN["password"]:
                user = db.query(Employee).filter_by(login=MOCK_ADMIN["login"]).first()
                
                # Jeśli fizycznie nie ma go w bazie, tworzymy go z danych mocka
                if not user:
                    user = Employee(
                        login=MOCK_ADMIN["login"],
                        password_hash=generate_password_hash(MOCK_ADMIN["password"]),
                        **MOCK_ADMIN["data"] # Rozpakowujemy resztę pól (imię, nazwisko, pesel...)
                    )
                    db.add(user)
                    db.commit()
                    db.refresh(user)
            
            else:
                user = db.query(Employee).filter_by(login=login_input).first()

        # 3. Weryfikacja hasła 
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Niepoprawne dane logowania"}), 401

        # 4. Logowanie w sesji
        login_user(user)

        # 5. Redirect w zależności od roli
        redirect_url = "/traveler_dashboard" if role == "traveler" else "/employee_dashboard"
        
        return jsonify({
            "message": "Zalogowano pomyślnie",
            "redirect_url": redirect_url,
            "role": role
        })
        
    finally:
        db.close()

@auth_bp.route("/login_page")
def login_page():
    return render_template("login.html")

@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for('auth.login_page'))