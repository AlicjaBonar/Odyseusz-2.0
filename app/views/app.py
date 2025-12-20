from flask import Blueprint, render_template, request, g, flash

from app.database.database import SessionLocal
from app.models import Trip, Stage, Location, City, Country, TripStatus
from flask_login import login_required, current_user
from sqlalchemy import or_, and_, cast, Date, func
from sqlalchemy.orm import joinedload

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

@app_bp.route("/warning_list_page")
def warning_list_page():
    return render_template("warning_list.html")

@app_bp.route("/warning_edit_page")
def warning_edit_page():
    return render_template("edit_warning.html")

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


@app_bp.route("/employee_dashboard")
@login_required
def employee_dashboard():
    employee = current_user

    return render_template("employee_dashboard.html", employee=employee)

@login_required
@app_bp.route("/travelers_trips")
def travelers_trips_page():
    traveler = current_user
    # Pobranie podróży podróżnego z bazy
    trips = g.db.query(Trip).filter(Trip.traveler_pesel == traveler.pesel).all()
    
    return render_template("travelers_trips.html", traveler=traveler, trips=trips)



@app_bp.route("/reports", methods=["GET", "POST"])
def reports_page():
    db = SessionLocal()
    trips = []
    show_modal = False

    filter_country = ""
    filter_date_from = ""
    filter_date_to = ""
    filter_status = ""

    query = db.query(Trip).options(
        joinedload(Trip.traveler),
        joinedload(Trip.stages).joinedload(Stage.location).joinedload(Location.city).joinedload(City.country)
    )

    query = query.join(Trip.stages).join(Stage.location).join(Location.city).join(City.country)

    if request.method == "POST":
        filter_country = request.form.get("country")
        filter_date_from = request.form.get("date_from")
        filter_date_to = request.form.get("date_to")
        filter_status = request.form.get("status")

        action = request.form.get("action")

        if action == "report":
            show_modal = True

        if filter_country:
            query = query.filter(Country.name.ilike(f"%{filter_country}%"))

        if filter_status:
            query = query.filter(Trip.status == filter_status)

        if filter_date_from and filter_date_to:
            query = query.filter(
                and_(
                    func.date(Stage.start_date) <= filter_date_to,
                    func.date(Stage.end_date) >= filter_date_from
                )
            )

        trips = query.distinct().order_by(Trip.id.desc()).all()

    db.close()

    return render_template(
        "reports.html",
        trips=trips,
        show_modal=show_modal,
        f_country=filter_country,
        f_date_from=filter_date_from,
        f_date_to=filter_date_to,
        f_status=filter_status
    )