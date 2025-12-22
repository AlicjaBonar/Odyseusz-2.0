from flask import Blueprint, jsonify, request, g, render_template
from datetime import datetime

evacuations_bp = Blueprint('evacuations', __name__)

@evacuations_bp.route("/evacuation/all", methods=["GET"])
def get_evacuations():
    pass

@evacuations_bp.route("/evacuation/create", methods=["GET"])
def create_evacuation():
    return render_template("create_evacuation.html")

from flask import render_template
from datetime import datetime

class Evacuation:
    def __init__(self, id, action_name, event_description, start_date, end_date, status, country_id=None, city_id=None):
        self.id = id
        self.action_name = action_name
        self.event_description = event_description
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        self.country_id = country_id
        self.city_id = city_id

# Przykładowa ewakuacja "hardkodowana"
def get_evacuation_by_id(id):
    # Tutaj po prostu zwracamy przykładową ewakuację, ignorując id
    return Evacuation(
        id=1,
        action_name="Ewakuacja testowa",
        event_description="Symulacja ewakuacji w celu testów systemu.",
        start_date=datetime(2025, 12, 25, 14, 30),
        end_date=datetime(2025, 12, 26, 18, 0),
        status="PLANNED",
        country_id=2,   # np. Portugalia
        city_id=None    # brak miasta → ewakuacja kraju
    )

def get_all_countries():
    return [
        type('Country', (object,), {'id': 1, 'name': "Hiszpania"})(),
        type('Country', (object,), {'id': 2, 'name': "Portugalia"})(),
        type('Country', (object,), {'id': 3, 'name': "Włochy"})()
    ]

def get_all_cities():
    return [
        type('City', (object,), {'id': 1, 'name': "Paryż", 'country': type('Country', (object,), {'id': 1, 'name': "Francja"})()})(),
        type('City', (object,), {'id': 2, 'name': "Madryt", 'country': type('Country', (object,), {'id': 2, 'name': "Hiszpania"})()})(),
        type('City', (object,), {'id': 3, 'name': "Barcelona", 'country': type('Country', (object,), {'id': 2, 'name': "Hiszpania"})()})()
    ]

@evacuations_bp.route('/evacuations/<int:id>/edit')
def edit_evacuation(id):
    evacuation = get_evacuation_by_id(id)  # twoja funkcja pobierająca ewakuację

    # sformatuj daty na format odpowiedni dla <input type="datetime-local">
    if evacuation.start_date:
        evacuation.start_date_str = evacuation.start_date.strftime("%Y-%m-%dT%H:%M")
    else:
        evacuation.start_date_str = ""

    if evacuation.end_date:
        evacuation.end_date_str = evacuation.end_date.strftime("%Y-%m-%dT%H:%M")
    else:
        evacuation.end_date_str = ""

    evacuation_scope = "city" if evacuation.city_id else "country"

    return render_template(
        "edit_evacuation.html",
        evacuation=evacuation,
        evacuation_scope=evacuation_scope,
        countries=get_all_countries(),
        cities=get_all_cities()
    )


def get_all_evacuations():
    return [
        Evacuation(
            id=1,
            action_name="Ewakuacja Portugalia",
            event_description="Zagrożenie pożarowe – południe kraju",
            start_date=datetime(2025, 1, 10, 12, 0),
            end_date=None,
            status="IN_PROGRESS",
            country_id=2,
            city_id=None
        ),
        Evacuation(
            id=2,
            action_name="Ewakuacja Barcelona",
            event_description="Silne burze i ryzyko powodzi",
            start_date=datetime(2024, 12, 5, 8, 0),
            end_date=datetime(2024, 12, 6, 20, 0),
            status="COMPLETED",
            country_id=None,
            city_id=5
        )
    ]

@evacuations_bp.route('/evacuations')
def evacuation_list():
    evacuations = get_all_evacuations()

    for e in evacuations:
        # START
        if isinstance(e.start_date, str):
            e.start_date_str = e.start_date
        elif e.start_date:
            e.start_date_str = e.start_date.strftime("%d.%m.%Y %H:%M")
        else:
            e.start_date_str = "—"

        # END
        if isinstance(e.end_date, str):
            e.end_date_str = e.end_date
        elif e.end_date:
            e.end_date_str = e.end_date.strftime("%d.%m.%Y %H:%M")
        else:
            e.end_date_str = "Nieokreślona"

    return render_template(
        "evacuation_list.html",
        evacuations=evacuations
    )


@evacuations_bp.route('/evacuations/saved')
def evacuation_saved():
    evacuation_id=1
    return render_template(
            "evacuation_saved.html",
            evacuation_id=evacuation_id
        )

@evacuations_bp.route('/evacuations/deleted')
def evacuation_deleted():
    return render_template(
            "evacuation_deleted.html"
        )