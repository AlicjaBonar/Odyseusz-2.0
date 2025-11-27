from flask import Blueprint, request, jsonify, g
from app.models import Stage, Trip, Location
from datetime import datetime

stages_bp = Blueprint("stages", __name__)

# --- GET all stages ---
@stages_bp.route("/stages", methods=["GET"])
def get_stages():
    stages = g.db.query(Stage).all()
    result = []
    for s in stages:
        result.append({
            "id": s.id,
            "start_date": s.start_date.isoformat(),
            "end_date": s.end_date.isoformat(),
            "trip_id": s.trip_id,
            "location_id": s.location_id
        })
    return jsonify(result)

# --- GET single stage ---
@stages_bp.route("/stages/<int:stage_id>", methods=["GET"])
def get_stage(stage_id):
    stage = g.db.query(Stage).filter_by(id=stage_id).first()
    if not stage:
        return jsonify({"error": "Stage not found"}), 404
    return jsonify({
        "id": stage.id,
        "start_date": stage.start_date.isoformat(),
        "end_date": stage.end_date.isoformat(),
        "trip_id": stage.trip_id,
        "location_id": stage.location_id
    })

# --- CREATE new stage ---
@stages_bp.route("/stages", methods=["POST"])
def create_stage():
    data = request.get_json()
    required_fields = ["start_date", "end_date", "trip_id", "location_id"]
    if not all(f in data for f in required_fields):
        return jsonify({"error": f"Missing fields: {required_fields}"}), 400

    try:
        start_date = datetime.fromisoformat(data["start_date"])
        end_date = datetime.fromisoformat(data["end_date"])
    except ValueError:
        return jsonify({"error": "Dates must be in ISO format"}), 400

    # check if trip exists
    trip = g.db.query(Trip).filter_by(id=data["trip_id"]).first()
    if not trip:
        return jsonify({"error": "Trip not found"}), 404

    # check if location exists
    location = g.db.query(Location).filter_by(id=data["location_id"]).first()
    if not location:
        return jsonify({"error": "Location not found"}), 404

    stage = Stage(
        start_date=start_date,
        end_date=end_date,
        trip_id=data["trip_id"],
        location_id=data["location_id"]
    )
    g.db.add(stage)
    g.db.commit()
    g.db.refresh(stage)

    return jsonify({
        "id": stage.id,
        "start_date": stage.start_date.isoformat(),
        "end_date": stage.end_date.isoformat(),
        "trip_id": stage.trip_id,
        "location_id": stage.location_id
    }), 201

# --- UPDATE stage ---
@stages_bp.route("/stages/<int:stage_id>", methods=["PUT"])
def update_stage(stage_id):
    stage = g.db.query(Stage).filter_by(id=stage_id).first()
    if not stage:
        return jsonify({"error": "Stage not found"}), 404

    data = request.get_json()
    if "start_date" in data:
        stage.start_date = datetime.fromisoformat(data["start_date"])
    if "end_date" in data:
        stage.end_date = datetime.fromisoformat(data["end_date"])
    if "trip_id" in data:
        trip = g.db.query(Trip).filter_by(id=data["trip_id"]).first()
        if not trip:
            return jsonify({"error": "Trip not found"}), 404
        stage.trip_id = data["trip_id"]
    if "location_id" in data:
        location = g.db.query(Location).filter_by(id=data["location_id"]).first()
        if not location:
            return jsonify({"error": "Location not found"}), 404
        stage.location_id = data["location_id"]

    g.db.commit()
    g.db.refresh(stage)
    return jsonify({
        "id": stage.id,
        "start_date": stage.start_date.isoformat(),
        "end_date": stage.end_date.isoformat(),
        "trip_id": stage.trip_id,
        "location_id": stage.location_id
    })

# --- DELETE stage ---
@stages_bp.route("/stages/<int:stage_id>", methods=["DELETE"])
def delete_stage(stage_id):
    stage = g.db.query(Stage).filter_by(id=stage_id).first()
    if not stage:
        return jsonify({"error": "Stage not found"}), 404

    g.db.delete(stage)
    g.db.commit()
    return jsonify({"message": f"Stage {stage_id} deleted"})
