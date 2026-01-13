from flask import Blueprint, request, jsonify, g
from app.services.companion_service import (
    CompanionService,
    CompanionServiceError,
    CompanionNotFoundError,
    TravelerNotFoundError
)

companions_bp = Blueprint("companions", __name__)


# --- GET all companions ---
@companions_bp.route("/companions", methods=["GET"])
def get_all_companions():
    try:
        service = CompanionService(g.db)
        companions = service.get_all_companions()
        return jsonify(companions)
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# --- GET single companion ---
@companions_bp.route("/companions/<int:companion_id>", methods=["GET"])
def get_companion(companion_id):
    try:
        service = CompanionService(g.db)
        companion = service.get_companion_by_id(companion_id)
        if not companion:
            return jsonify({"error": "Companion not found"}), 404
        return jsonify(companion)
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# --- CREATE new companion ---
@companions_bp.route("/companions", methods=["POST"])
def create_companion():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        service = CompanionService(g.db)
        result = service.create_companion(data)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except TravelerNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except CompanionServiceError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# --- UPDATE companion ---
@companions_bp.route("/companions/<int:companion_id>", methods=["PUT"])
def update_companion(companion_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        service = CompanionService(g.db)
        result = service.update_companion(companion_id, data)
        return jsonify(result)
    except CompanionNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except TravelerNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except CompanionServiceError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# --- DELETE companion ---
@companions_bp.route("/companions/<int:companion_id>", methods=["DELETE"])
def delete_companion(companion_id):
    try:
        service = CompanionService(g.db)
        service.delete_companion(companion_id)
        return jsonify({"message": f"Companion {companion_id} deleted"})
    except CompanionNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# --- GET companions by traveler PESEL ---
@companions_bp.route("/travelers/<string:traveler_pesel>/companions", methods=["GET"])
def get_companions_by_traveler(traveler_pesel):
    try:
        service = CompanionService(g.db)
        result = service.get_companions_by_traveler_pesel(traveler_pesel)
        return jsonify(result)
    except TravelerNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
