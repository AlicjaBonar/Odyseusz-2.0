from flask import Blueprint, render_template, request, g
from app.models import Trip

app_bp = Blueprint("app_bp", __name__)

@app_bp.route("/")
def index_page():
    return render_template("index.html")

@app_bp.route("/login_page")
def login_page():
    return render_template("login.html")

@app_bp.route("/register_traveler_page")
def register_traveler_page():
    return render_template("register_traveler.html")

@app_bp.route("/register_employee_page")
def register_employee_page():
    return render_template("register_employee.html")

@app_bp.route("/register_travel")
def register_travel_page():
    return render_template("register_travel.html")

@app_bp.route("/add_companions_to_travel")
def add_companions_to_travel_page():
    # Pobieramy tylko pesel z query parameters
    traveler_pesel = request.args.get("traveler_pesel")
    if not traveler_pesel:
        return "Brak traveler_pesel w URL", 400

    # Pobranie najnowszego tripu podróżnego
    latest_trip = g.db.query(Trip)\
        .filter_by(traveler_pesel=traveler_pesel)\
        .order_by(Trip.id.desc())\
        .first()
    print(traveler_pesel)
    if not latest_trip:
        return f"Nie znaleziono podróży dla podróżnego {traveler_pesel}", 404

    return render_template(
        "add_companions_to_travel.html",
        trip_id=latest_trip.id,
        traveler_pesel=traveler_pesel
    )
