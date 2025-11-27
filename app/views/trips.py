from flask import Blueprint, request, jsonify, g
from datetime import datetime
from app.models import Trip, Traveler, Stage, Location, Evacuation, TripStatus  # TripStatus = Enum

trips_bp = Blueprint("trips", __name__)

# --- GET all trips ---
@trips_bp.route("/trips", methods=["GET"])
def get_all_trips():
    trips = g.db.query(Trip).all()
    result = []
    for t in trips:
        result.append({
            "id": t.id,
            "status": t.status.value,
            "traveler_pesel": t.traveler_pesel,
            "evacuation_id": t.evacuation_id,
            "stages": [{
                "id": s.id,
                "start_date": s.start_date.isoformat(),
                "end_date": s.end_date.isoformat(),
                "location_id": s.location_id
            } for s in t.stages],
            "companions": [{
                "id": c.id,
                "pesel": c.pesel,
                "first_name": c.first_name,
                "last_name": c.last_name
            } for c in t.companions]
        })
    return jsonify(result)

# --- GET single trip ---
@trips_bp.route("/trips/<int:trip_id>", methods=["GET"])
def get_trip(trip_id):
    trip = g.db.query(Trip).filter_by(id=trip_id).first()
    if not trip:
        return jsonify({"error": "Trip not found"}), 404
    return jsonify({
        "id": trip.id,
        "status": trip.status.value,
        "traveler_pesel": trip.traveler_pesel,
        "evacuation_id": trip.evacuation_id,
        "stages": [{"id": s.id,
                    "start_date": s.start_date.isoformat(),
                    "end_date": s.end_date.isoformat(),
                    "location_id": s.location_id} for s in trip.stages],
        "companions": [{
                "id": c.id,
                "pesel": c.pesel,
                "first_name": c.first_name,
                "last_name": c.last_name
            } for c in trip.companions]
    })

# --- CREATE new trip ---
@trips_bp.route("/trips", methods=["POST"])
def create_trip():
    data = request.get_json()
    required_fields = ["status", "traveler_pesel"]
    if not all(f in data for f in required_fields):
        return jsonify({"error": f"Missing required fields: {required_fields}"}), 400

    # Walidacja statusu Enum
    try:
        status_enum = TripStatus(data["status"])
    except ValueError:
        return jsonify({"error": f"Invalid status. Must be one of {[s.value for s in TripStatus]}"}), 400

    traveler = g.db.query(Traveler).filter_by(pesel=data["traveler_pesel"]).first()
    if not traveler:
        return jsonify({"error": "Traveler not found"}), 404

    trip = Trip(
        status=status_enum,
        traveler=traveler
    )
    g.db.add(trip)
    g.db.flush()  # aby trip.id było dostępne przed commit

    # Dodajemy etapy
    stages_data = data.get("stages", [])
    for s in stages_data:
        try:
            start_date = datetime.fromisoformat(s["start_date"])
            end_date = datetime.fromisoformat(s["end_date"])
            location_id = s["location_id"]
        except (KeyError, ValueError):
            continue

        location = g.db.query(Location).filter_by(id=location_id).first()
        if not location:
            continue

        stage = Stage(
            start_date=start_date,
            end_date=end_date,
            trip_id=trip.id,
            location_id=location_id
        )
        g.db.add(stage)

    # Dodajemy companionów jeśli podano
    companion_ids = data.get("companions", [])
    for cid in companion_ids:
        companion = g.db.query(Companion).filter_by(id=cid).first()
        if companion:
            trip.companions.append(companion)

    g.db.commit()
    g.db.refresh(trip)

    return jsonify({
        "id": trip.id,
        "status": trip.status.value,
        "traveler_pesel": trip.traveler_pesel,
        "stages": [{
            "id": st.id,
            "start_date": st.start_date.isoformat(),
            "end_date": st.end_date.isoformat(),
            "location_id": st.location_id
        } for st in trip.stages],
        "companions": [{
            "id": c.id,
            "pesel": c.pesel,
            "first_name": c.first_name,
            "last_name": c.last_name
        } for c in trip.companions]
    }), 201

# --- UPDATE trip ---
@trips_bp.route("/trips/<int:trip_id>", methods=["PUT"])
def update_trip(trip_id):
    trip = g.db.query(Trip).filter_by(id=trip_id).first()
    if not trip:
        return jsonify({"error": "Trip not found"}), 404

    data = request.get_json()
    if "status" in data:
        try:
            trip.status = TripStatus(data["status"])
        except ValueError:
            return jsonify({"error": f"Invalid status. Must be one of {[s.value for s in TripStatus]}"}), 400

    if "traveler_pesel" in data:
        traveler = g.db.query(Traveler).filter_by(pesel=data["traveler_pesel"]).first()
        if not traveler:
            return jsonify({"error": "Traveler not found"}), 404
        trip.traveler_pesel = data["traveler_pesel"]

    if "evacuation_id" in data:
        evacuation_id = data["evacuation_id"]
        if evacuation_id:
            evacuation = g.db.query(Evacuation).filter_by(id=evacuation_id).first()
            if not evacuation:
                return jsonify({"error": "Evacuation not found"}), 404
            trip.evacuation_id = evacuation_id
        else:
            trip.evacuation_id = None

    g.db.commit()
    g.db.refresh(trip)

    return jsonify({
        "id": trip.id,
        "status": trip.status.value,
        "traveler_pesel": trip.traveler_pesel,
        "evacuation_id": trip.evacuation_id
    })

# --- DELETE trip ---
@trips_bp.route("/trips/<int:trip_id>", methods=["DELETE"])
def delete_trip(trip_id):
    trip = g.db.query(Trip).filter_by(id=trip_id).first()
    if not trip:
        return jsonify({"error": "Trip not found"}), 404

    g.db.delete(trip)
    g.db.commit()
    return jsonify({"message": f"Trip {trip_id} deleted"})

# --- GET trips by pesel ---
@trips_bp.route("/travelers/<string:traveler_pesel>/trips", methods=["GET"])
def get_trips_by_pesel(traveler_pesel):
    traveler = g.db.query(Traveler).filter_by(pesel=traveler_pesel).first()
    if not traveler:
        return jsonify({"error": "Traveler not found"}), 404

    trips = []
    for t in traveler.trips:
        trips.append({
            "id": t.id,
            "status": t.status.value,
            "evacuation_id": t.evacuation_id,
            "stages": [{
                "id": s.id,
                "start_date": s.start_date.isoformat(),
                "end_date": s.end_date.isoformat(),
                "location_id": s.location_id
            } for s in t.stages],
            "companions": [{
                "id": c.id,
                "pesel": c.pesel,
                "first_name": c.first_name,
                "last_name": c.last_name
            } for c in t.companions]
        })

    return jsonify({
        "traveler_pesel": traveler.pesel,
        "trips": trips
    })
