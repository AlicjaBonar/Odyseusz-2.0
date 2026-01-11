from flask import Blueprint, request, jsonify, redirect, url_for, render_template, session, g
from flask_login import login_user, logout_user
from app.services.auth_service import (
    AuthService,
    AuthServiceError,
    InvalidCredentialsError
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    login_input = data.get("login")
    password = data.get("password")

    if not login_input or not password:
        return jsonify({"error": "Brak loginu lub hasła"}), 400

    try:
        service = AuthService(g.db)
        user, role = service.login(login_input, password)
        
        # Logowanie w sesji Flask-Login
        login_user(user)
        
        # Redirect w zależności od roli
        redirect_url = "/traveler_dashboard" if role == "traveler" else "/employee_dashboard"
        
        return jsonify({
            "message": "Zalogowano pomyślnie",
            "redirect_url": redirect_url,
            "role": role
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except InvalidCredentialsError as e:
        return jsonify({"error": str(e)}), 401
    except AuthServiceError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


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
    
    try:
        service = AuthService(g.db)
        identity, user = service.mobywatel_callback(scenario)
        
        if scenario == "existing":
            # Użytkownik już istnieje - zaloguj
            if user:
                login_user(user)
                return redirect("/traveler_dashboard")
        
        elif scenario == "new":
            # Nowy użytkownik - zapisz tożsamość w sesji
            if identity:
                session['pending_identity'] = identity
                return redirect(url_for('auth.complete_profile_page'))
    
    except Exception as e:
        return f"Błąd: {str(e)}", 500
    
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
        
        try:
            service = AuthService(g.db)
            new_traveler = service.complete_profile(identity, email, phone_number)
            
            session.pop('pending_identity', None)
            login_user(new_traveler)
            
            return redirect("/traveler_dashboard")
        except Exception as e:
            return f"Błąd bazy danych: {e}", 500

    return render_template("complete_profile.html", identity=identity)