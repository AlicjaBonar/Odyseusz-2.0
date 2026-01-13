from flask import Blueprint, request, jsonify, g
from app.services.stage_service import (
    StageService,
    StageServiceError,
    StageNotFoundError,
    TripNotFoundError,
    LocationNotFoundError
)

stages_bp = Blueprint("stages", __name__)


# --- GET all stages ---
@stages_bp.route("/stages", methods=["GET"])
def get_stages():
    try:
        service = StageService(g.db)
        stages = service.get_all_stages()
        return jsonify(stages)
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# --- GET single stage ---
@stages_bp.route("/stages/<int:stage_id>", methods=["GET"])
def get_stage(stage_id):
    try:
        service = StageService(g.db)
        stage = service.get_stage_by_id(stage_id)
        if not stage:
            return jsonify({"error": "Stage not found"}), 404
        return jsonify(stage)
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# --- CREATE new stage ---
@stages_bp.route("/stages", methods=["POST"])
def create_stage():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        service = StageService(g.db)
        result = service.create_stage(data)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except TripNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except LocationNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except StageServiceError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# --- UPDATE stage ---
@stages_bp.route("/stages/<int:stage_id>", methods=["PUT"])
def update_stage(stage_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        service = StageService(g.db)
        result = service.update_stage(stage_id, data)
        return jsonify(result)
    except StageNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except TripNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except LocationNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except StageServiceError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# --- DELETE stage ---
@stages_bp.route("/stages/<int:stage_id>", methods=["DELETE"])
def delete_stage(stage_id):
    try:
        service = StageService(g.db)
        service.delete_stage(stage_id)
        return jsonify({"message": f"Stage {stage_id} deleted"})
    except StageNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
