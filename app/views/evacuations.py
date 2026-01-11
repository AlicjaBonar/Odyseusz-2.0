from flask import Blueprint, jsonify, request, g, render_template
from datetime import datetime
from app.services.evacuation_service import EvacuationService
from app.models import Country, City
from app.mock_data import get_mock_evacuations, get_mock_countries, get_mock_cities

evacuations_bp = Blueprint('evacuations', __name__)


@evacuations_bp.route("/evacuation/all", methods=["GET"])
def get_evacuations():
    try:
        service = EvacuationService(g.db)
        evacuations = service.get_all_evacuations()
        return jsonify(evacuations)
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@evacuations_bp.route("/evacuation/create", methods=["GET"])
def create_evacuation():
    return render_template("create_evacuation.html")


@evacuations_bp.route('/evacuations/<int:id>/edit')
def edit_evacuation(id):
    try:
        service = EvacuationService(g.db)
        evacuation = service.get_evacuation_by_id(id)
        
        if not evacuation:
            return "Ewakuacja nie została znaleziona", 404
        
        # Formatowanie dat dla input datetime-local
        if evacuation.get("start_date"):
            evacuation["start_date_str"] = datetime.fromisoformat(evacuation["start_date"]).strftime("%Y-%m-%dT%H:%M")
        else:
            evacuation["start_date_str"] = ""
        
        if evacuation.get("end_date"):
            evacuation["end_date_str"] = datetime.fromisoformat(evacuation["end_date"]).strftime("%Y-%m-%dT%H:%M")
        else:
            evacuation["end_date_str"] = ""
        
        # Określenie zakresu ewakuacji
        evacuation_scope = "city" if evacuation.get("cities") else "country"
        
        # Pobranie krajów i miast z bazy (lub mock danych jeśli baza pusta)
        countries = g.db.query(Country).all()
        cities = g.db.query(City).all()
        
        # Jeśli baza pusta, użyj mock danych
        if not countries:
            countries = get_mock_countries()
        if not cities:
            cities = get_mock_cities()
        
        return render_template(
            "edit_evacuation.html",
            evacuation=evacuation,
            evacuation_scope=evacuation_scope,
            countries=countries,
            cities=cities
        )
    except Exception as e:
        return f"Błąd: {str(e)}", 500


@evacuations_bp.route('/evacuations')
def evacuation_list():
    try:
        service = EvacuationService(g.db)
        evacuations = service.get_all_evacuations()
        
        # Formatowanie dat dla wyświetlenia
        for e in evacuations:
            if isinstance(e.get("start_date"), str):
                try:
                    start_dt = datetime.fromisoformat(e["start_date"])
                    e["start_date_str"] = start_dt.strftime("%d.%m.%Y %H:%M")
                except:
                    e["start_date_str"] = e.get("start_date", "—")
            elif e.get("start_date"):
                e["start_date_str"] = datetime.fromisoformat(e["start_date"]).strftime("%d.%m.%Y %H:%M")
            else:
                e["start_date_str"] = "—"
            
            if isinstance(e.get("end_date"), str):
                try:
                    end_dt = datetime.fromisoformat(e["end_date"])
                    e["end_date_str"] = end_dt.strftime("%d.%m.%Y %H:%M")
                except:
                    e["end_date_str"] = e.get("end_date", "Nieokreślona")
            elif e.get("end_date"):
                e["end_date_str"] = datetime.fromisoformat(e["end_date"]).strftime("%d.%m.%Y %H:%M")
            else:
                e["end_date_str"] = "Nieokreślona"
        
        return render_template("evacuation_list.html", evacuations=evacuations)
    except Exception as e:
        # Fallback do mock danych jeśli błąd
        evacuations = get_mock_evacuations()
        for e in evacuations:
            if isinstance(e.start_date, str):
                e.start_date_str = e.start_date
            elif e.start_date:
                e.start_date_str = e.start_date.strftime("%d.%m.%Y %H:%M")
            else:
                e.start_date_str = "—"
            
            if isinstance(e.end_date, str):
                e.end_date_str = e.end_date
            elif e.end_date:
                e.end_date_str = e.end_date.strftime("%d.%m.%Y %H:%M")
            else:
                e.end_date_str = "Nieokreślona"
        
        return render_template("evacuation_list.html", evacuations=evacuations)


@evacuations_bp.route('/evacuations/saved')
def evacuation_saved():
    evacuation_id = 1
    return render_template("evacuation_saved.html", evacuation_id=evacuation_id)


@evacuations_bp.route('/evacuations/deleted')
def evacuation_deleted():
    return render_template("evacuation_deleted.html")