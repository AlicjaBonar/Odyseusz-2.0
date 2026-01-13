from flask import Blueprint, request, jsonify, g
from app.services.trip_service import (
    TripService,
    TripServiceError,
    TripNotFoundError,
    TravelerNotFoundError
)

trips_bp = Blueprint("trips", __name__)


# --- GET all trips ---
@trips_bp.route("/trips", methods=["GET"])
def get_all_trips():
    try:
        service = TripService(g.db)
        trips = service.get_all_trips()
        return jsonify(trips)
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# --- GET single trip ---
@trips_bp.route("/trips/<int:trip_id>", methods=["GET"])
def get_trip(trip_id):
    try:
        service = TripService(g.db)
        trip = service.get_trip_by_id(trip_id)
        if not trip:
            return jsonify({"error": "Trip not found"}), 404
        return jsonify(trip)
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# --- CREATE new trip ---
@trips_bp.route("/trips", methods=["POST"])
def create_trip():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        service = TripService(g.db)
        result = service.create_trip(data)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except TravelerNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except TripServiceError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# --- UPDATE trip ---
@trips_bp.route("/trips/<int:trip_id>", methods=["PUT"])
def update_trip(trip_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        service = TripService(g.db)
        result = service.update_trip(trip_id, data)
        return jsonify(result)
    except TripNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except TravelerNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except TripServiceError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# --- DELETE trip ---
@trips_bp.route("/trips/<int:trip_id>", methods=["DELETE"])
def delete_trip(trip_id):
    try:
        service = TripService(g.db)
        service.delete_trip(trip_id)
        return jsonify({"message": f"Trip {trip_id} deleted"})
    except TripNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# --- GET trips by pesel ---
@trips_bp.route("/travelers/<string:traveler_pesel>/trips", methods=["GET"])
def get_trips_by_pesel(traveler_pesel):
    try:
        service = TripService(g.db)
        result = service.get_trips_by_traveler_pesel(traveler_pesel)
        return jsonify(result)
    except TravelerNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@trips_bp.route("/trips/<int:trip_id>/companions", methods=["POST"])
def add_companions_to_trip(trip_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    companions_data = data.get("companions", [])
    traveler_pesel = data.get("traveler_pesel")

    try:
        service = TripService(g.db)
        result = service.add_companions_to_trip(trip_id, companions_data, traveler_pesel)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except TripNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except TravelerNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except TripServiceError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
