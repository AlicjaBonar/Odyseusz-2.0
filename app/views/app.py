from flask import Blueprint, render_template, request, g
from app.models import Trip
from flask_login import login_required, current_user

app_bp = Blueprint("app_bp", __name__)

@app_bp.route("/")
def index_page():
    return render_template("index.html")

@app_bp.route("/register_traveler_page")
def register_traveler_page():
    return render_template("register_traveler.html")

@app_bp.route("/register_employee_page")
def register_employee_page():
    return render_template("register_employee.html")

@login_required
@app_bp.route("/register_travel")
def register_travel_page():
    traveler = current_user
    return render_template("register_travel.html", traveler=traveler)

@login_required
@app_bp.route("/add_companions_to_travel")
def add_companions_to_travel_page():
    # Pobieramy tylko pesel z query parameters
    traveler = current_user
    traveler_pesel = traveler.pesel
    if not traveler_pesel:
        return "Brak traveler_pesel w URL", 400

    # Pobranie najnowszego tripu podróżnego
    latest_trip = g.db.query(Trip)\
        .filter_by(traveler_pesel=traveler_pesel)\
        .order_by(Trip.id.desc())\
        .first()
    if not latest_trip:
        return f"Nie znaleziono podróży dla podróżnego {traveler_pesel}", 404

    return render_template(
        "add_companions_to_travel.html",
        trip_id=latest_trip.id,
        traveler_pesel=traveler_pesel
    )

@app_bp.route("/thanks_for_registering_trip")
def thanks_register_travel_page():
    return render_template("thanks_for_registering_trip.html")

@app_bp.route("/traveler_dashboard")
@login_required  # chroni stronę, wymaga zalogowania
def traveler_dashboard():
    # current_user to obiekt Traveler lub Employee, w tym przypadku spodziewamy się Traveler
    traveler = current_user

    # przekazujemy do szablonu dashboard.html
    return render_template("dashboard.html", traveler=traveler)
    # return "<h1>Under Construction 🚧</h1><p>Panel podróżnego jest w trakcie tworzenia. Prosimy o cierpliwość.</p>"

@login_required
@app_bp.route("/travelers_trips")
def travelers_trips_page():
    traveler = current_user
    # Pobranie podróży podróżnego z bazy
    trips = g.db.query(Trip).filter(Trip.traveler_pesel == traveler.pesel).all()
    
    return render_template("travelers_trips.html", traveler=traveler, trips=trips)