from flask import Blueprint, render_template, request, g, flash, make_response, redirect, url_for

from app.database.database import SessionLocal
from app.models import Trip, Stage, Location, City, Country, TripStatus, Traveler, Notification
from flask_login import login_required, current_user
from sqlalchemy import or_, and_, cast, Date, func
from sqlalchemy.orm import joinedload
import csv
import io
from datetime import date, datetime

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


def get_filtered_trips(db, country, date_from, date_to, status):

    query = db.query(Trip).options(
        joinedload(Trip.traveler),
        joinedload(Trip.stages).joinedload(Stage.location).joinedload(Location.city).joinedload(City.country)
    ).join(Trip.stages).join(Stage.location).join(Location.city).join(City.country)

    if country:
        query = query.filter(Country.name.ilike(f"%{country}%"))

    if status:
        query = query.filter(Trip.status == status)

    if date_from and date_to:
        query = query.filter(
            and_(
                func.date(Stage.start_date) <= date_to,
                func.date(Stage.end_date) >= date_from
            )
        )

    return query.distinct().order_by(Trip.id.desc()).all()


@app_bp.route("/reports", methods=["GET", "POST"])
def reports_page():
    db = SessionLocal()
    trips = []
    show_modal = False

    filter_country = ""
    filter_date_from = ""
    filter_date_to = ""
    filter_status = ""

    if request.method == "POST":
        filter_country = request.form.get("country")
        filter_date_from = request.form.get("date_from")
        filter_date_to = request.form.get("date_to")
        filter_status = request.form.get("status")

        action = request.form.get("action")
        if action == "report":
            show_modal = True

        trips = get_filtered_trips(db, filter_country, filter_date_from, filter_date_to, filter_status)

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


@app_bp.route("/download_report_csv")
@login_required
def download_report_csv():
    filter_country = request.args.get("country", "")
    filter_date_from = request.args.get("date_from", "")
    filter_date_to = request.args.get("date_to", "")
    filter_status = request.args.get("status", "")

    db = SessionLocal
    trips = get_filtered_trips(db, filter_country, filter_date_from, filter_date_to, filter_status)
    db.close()

    si = io.StringIO()
    cw = csv.writer(si, delimiter=";")
    cw.writerow(["ID", "Podrozny", "Data rozpoczecia", "Data zakonczenia", "Status"])

    status_map = {
        'PLANNED': 'Planowana',
        'IN_PROGRESS': 'W trakcie',
        'COMPLETED': 'Zakończona',
        'CANCELLED': 'Anulowana'
    }

    for trip in trips:
        start_d = trip.stages[0].start_date.strftime('%Y-%m-%d') if trip.stages else ""
        end_d = trip.stages[-1].end_date.strftime('%Y-%m-%d') if trip.stages else ""
        stat_name = status_map.get(trip.status.name, trip.status.name)

        traveler_name = f"{trip.traveler.first_name} {trip.traveler.last_name}"

        cw.writerow([trip.id, traveler_name, start_d, end_d, stat_name])

    if (filter_country == "" and filter_status == ""):
        file_name = f"{filter_date_from}_{filter_date_to}.csv"
    elif (filter_country == ""):
        file_name = f"{filter_date_from}_{filter_date_to}_{filter_status}.csv"
    elif (filter_status == ""):
        file_name = f"{filter_country}_{filter_date_from}_{filter_date_to}.csv"
    else:
        file_name = f"{filter_country}_{filter_date_from}_{filter_date_to}_{filter_status}.csv"

    output = make_response(si.getvalue().encode('utf-8-sig'))
    output.headers["Content-Disposition"] = f"attachment; filename={file_name}"
    output.headers["Content-type"] = "text/csv"

    return output


@app_bp.route("/employee/send_push", methods=["GET", "POST"])
@login_required
def send_push_page():
    if request.method == "POST":
        message_body = request.form.get("message")
        target_type = request.form.get("target_type")
        target_country = request.form.get("country_name")

        db = SessionLocal()

        query = db.query(Traveler).filter(Traveler.pref_push == True)

        if target_type == "country" and target_country:
            today = date.today()
            query = query.join(Trip).join(Stage).join(Location).join(City).join(Country)
            query = query.filter(
                Trip.status == 'IN_PROGRESS',
                and_(Stage.start_date <= today, Stage.end_date >= today),
                Country.name.ilike(f"%{target_country}%")
            )

        recipients = query.distinct().all()

        count = 0
        for traveler in recipients:
            new_notification = Notification(
                traveler_pesel=traveler.pesel,
                message=message_body,

                is_read=False,
                created_at=datetime.now()
            )
            db.add(new_notification)
            count += 1

        db.commit()
        db.close()

        flash(f"Wysłano powiadomienie PUSH do {count} podróżnych.", "success")
        return redirect(url_for("app_bp.send_push_page"))

    return render_template("send_push.html")