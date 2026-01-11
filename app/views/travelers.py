from flask import Blueprint, jsonify, request, g
from app.services.traveler_service import (
    TravelerService,
    TravelerServiceError,
    TravelerAlreadyExistsError
)

travelers_bp = Blueprint('travelers', __name__)


@travelers_bp.route("/register", methods=["POST"])
def create_traveler():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        # Używamy serwisu do utworzenia podróżnego
        service = TravelerService(g.db)
        result = service.create_traveler(data)
        return jsonify(result), 201
    
    except TravelerAlreadyExistsError as e:
        return jsonify({"error": str(e)}), 409
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except TravelerServiceError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@travelers_bp.route("/travelers", methods=["GET"])
def get_travelers():
    try:
        service = TravelerService(g.db)
        travelers = service.get_all_travelers()
        return jsonify(travelers)
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
