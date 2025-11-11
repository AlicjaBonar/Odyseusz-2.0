from flask import Blueprint, jsonify, request, g
from app.models import Trip, Traveler, Evacuation

trips_bp = Blueprint('trips', __name__)

@trips_bp.route("/trips", methods=["POST"])
def create_trip():
    data = request.get_json()
    if not data or "status" not in data or "traveler_pesel" not in data:
        return jsonify({"error": "Fields 'status' and 'traveler_pesel' are required"}), 400

    traveler = g.db.query(Traveler).filter_by(pesel=data["traveler_pesel"]).first()
    if not traveler:
        return jsonify({"error": "Traveler not found"}), 404

    evacuation_id = data.get("evacuation_id")
    if evacuation_id:
        evacuation = g.db.query(Evacuation).filter_by(id=evacuation_id).first()
        if not evacuation:
            return jsonify({"error": "Evacuation not found"}), 404

    new_trip = Trip(status=data["status"], traveler=traveler, evacuation_id=evacuation_id)

    try:
        g.db.add(new_trip)
        g.db.commit()
        return jsonify({
            "id": new_trip.id,
            "status": new_trip.status,
            "traveler_pesel": new_trip.traveler_pesel,
            "evacuation_id": new_trip.evacuation_id
        }), 201
    except Exception as e:
        g.db.rollback()
        return jsonify({"error": str(e)}), 500


@trips_bp.route("/travelers/<string:traveler_pesel>/trips", methods=["GET"])
def get_traveler_trips(traveler_pesel):
    traveler = g.db.query(Traveler).filter_by(pesel=traveler_pesel).first()
    if not traveler:
        return jsonify({"error": "Traveler not found"}), 404

    trips = [{"id": t.id, "status": t.status, "evacuation_id": t.evacuation_id} for t in traveler.trips]
    return jsonify({"pesel": traveler.pesel, "trips": trips})
