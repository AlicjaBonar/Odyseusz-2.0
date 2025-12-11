from flask import Blueprint, request, jsonify, redirect, url_for, render_template, session
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
                
                if not user:
                    user = Employee(
                        login=MOCK_ADMIN["login"],
                        password_hash=generate_password_hash(MOCK_ADMIN["password"]),
                        **MOCK_ADMIN["data"] 
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

# --- MOCK LOGOWANIA WĘZEŁ KRAJOWY / MOBYWATEL ---

@auth_bp.route("/login/mobywatel", methods=["GET"])
def mobywatel_login_page():
    return render_template("login_mobywatel.html")

@auth_bp.route("/login/mobywatel/callback", methods=["POST"])
def mobywatel_callback():
    scenario = request.form.get("scenario")
    db = SessionLocal()

    try:
        if scenario == "existing":
            # SCENARIUSZ 1: Użytkownik już istnieje (Jan Kowalski)
            mock_data = MOCK_EXISTING_CITIZEN
            user = db.query(Traveler).filter_by(pesel=mock_data["pesel"]).first()
            
            if not user:
                user = Traveler(
                    login=mock_data["login"],
                    password_hash=generate_password_hash(mock_data["password"]),
                    first_name=mock_data["first_name"],
                    last_name=mock_data["last_name"],
                    pesel=mock_data["pesel"],
                    email=mock_data["email"],
                    phone_number=mock_data["phone_number"]
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            
            login_user(user)
            return redirect("/traveler_dashboard")

        elif scenario == "new":
            # SCENARIUSZ 2: Nowy użytkownik (Anna Nowak + losowy PESEL)
            mock_identity = get_new_mock_citizen()
            
            session['pending_identity'] = mock_identity
            return redirect(url_for('auth.complete_profile_page'))

    finally:
        db.close()
    
    return redirect(url_for('auth.login_page'))

# --- POZOSTAŁE ROUTE'Y ---

@auth_bp.route("/complete-profile", methods=["GET", "POST"])
def complete_profile_page():
    identity = session.get('pending_identity')
    
    if not identity:
        return redirect(url_for('auth.login_page'))

    if request.method == "POST":
        email = request.form.get("email")
        phone_number = request.form.get("phone_number")
        
        db = SessionLocal()
        try:

            new_traveler = Traveler(
                login=f"mobywatel_{identity['pesel']}",
                password_hash=generate_password_hash("mobywatel_auth"),
                first_name=identity['first_name'],
                last_name=identity['last_name'],
                pesel=identity['pesel'],
                email=email,
                phone_number=phone_number
            )
            
            db.add(new_traveler)
            db.commit()
            db.refresh(new_traveler)
            
            session.pop('pending_identity', None)
            login_user(new_traveler)
            
            return redirect("/traveler_dashboard")
        except Exception as e:
            db.rollback()
            return f"Błąd bazy danych: {e}"
        finally:
            db.close()

    return render_template("complete_profile.html", identity=identity)