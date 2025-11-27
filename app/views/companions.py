from flask import Blueprint, request, jsonify, g
from app.models import Companion, Traveler

companions_bp = Blueprint("companions", __name__)

# --- GET all companions ---
@companions_bp.route("/companions", methods=["GET"])
def get_all_companions():
    companions = g.db.query(Companion).all()
    result = []
    for c in companions:
        result.append({
            "id": c.id,
            "pesel": c.pesel,
            "first_name": c.first_name,
            "last_name": c.last_name,
            "age": c.age,
            "phone_number": c.phone_number,
            "email": c.email,
            "passport_number": c.passport_number,
            "id_card_number": c.id_card_number,
            "added_by_pesel": c.added_by_pesel
        })
    return jsonify(result)

# --- GET single companion ---
@companions_bp.route("/companions/<int:companion_id>", methods=["GET"])
def get_companion(companion_id):
    c = g.db.query(Companion).filter_by(id=companion_id).first()
    if not c:
        return jsonify({"error": "Companion not found"}), 404
    return jsonify({
        "id": c.id,
        "pesel": c.pesel,
        "first_name": c.first_name,
        "last_name": c.last_name,
        "age": c.age,
        "phone_number": c.phone_number,
        "email": c.email,
        "passport_number": c.passport_number,
        "id_card_number": c.id_card_number,
        "added_by_pesel": c.added_by_pesel
    })

# --- CREATE new companion ---
@companions_bp.route("/companions", methods=["POST"])
def create_companion():
    data = request.get_json()
    required_fields = ["pesel", "first_name", "last_name", "added_by_pesel"]
    if not all(f in data for f in required_fields):
        return jsonify({"error": f"Missing required fields: {required_fields}"}), 400

    traveler = g.db.query(Traveler).filter_by(pesel=data["added_by_pesel"]).first()
    if not traveler:
        return jsonify({"error": "Adding traveler not found"}), 404

    companion = Companion(
        pesel=data["pesel"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        age=data.get("age"),
        phone_number=data.get("phone_number"),
        email=data.get("email"),
        passport_number=data.get("passport_number"),
        id_card_number=data.get("id_card_number"),
        added_by_pesel=traveler.pesel
    )
    g.db.add(companion)
    g.db.commit()
    g.db.refresh(companion)

    return jsonify({
        "id": companion.id,
        "pesel": companion.pesel,
        "first_name": companion.first_name,
        "last_name": companion.last_name,
        "age": companion.age,
        "phone_number": companion.phone_number,
        "email": companion.email,
        "passport_number": companion.passport_number,
        "id_card_number": companion.id_card_number,
        "added_by_pesel": companion.added_by_pesel
    }), 201

# --- UPDATE companion ---
@companions_bp.route("/companions/<int:companion_id>", methods=["PUT"])
def update_companion(companion_id):
    companion = g.db.query(Companion).filter_by(id=companion_id).first()
    if not companion:
        return jsonify({"error": "Companion not found"}), 404

    data = request.get_json()
    for field in ["pesel", "first_name", "last_name", "age", "phone_number", "email", "passport_number", "id_card_number"]:
        if field in data:
            setattr(companion, field, data[field])

    if "added_by_pesel" in data:
        traveler = g.db.query(Traveler).filter_by(pesel=data["added_by_pesel"]).first()
        if not traveler:
            return jsonify({"error": "Adding traveler not found"}), 404
        companion.added_by_pesel = traveler.pesel

    g.db.commit()
    g.db.refresh(companion)

    return jsonify({
        "id": companion.id,
        "pesel": companion.pesel,
        "first_name": companion.first_name,
        "last_name": companion.last_name,
        "age": companion.age,
        "phone_number": companion.phone_number,
        "email": companion.email,
        "passport_number": companion.passport_number,
        "id_card_number": companion.id_card_number,
        "added_by_pesel": companion.added_by_pesel
    })

# --- DELETE companion ---
@companions_bp.route("/companions/<int:companion_id>", methods=["DELETE"])
def delete_companion(companion_id):
    companion = g.db.query(Companion).filter_by(id=companion_id).first()
    if not companion:
        return jsonify({"error": "Companion not found"}), 404

    g.db.delete(companion)
    g.db.commit()
    return jsonify({"message": f"Companion {companion_id} deleted"})

# --- GET companions by traveler PESEL ---
@companions_bp.route("/travelers/<string:traveler_pesel>/companions", methods=["GET"])
def get_companions_by_traveler(traveler_pesel):
    traveler = g.db.query(Traveler).filter_by(pesel=traveler_pesel).first()
    if not traveler:
        return jsonify({"error": "Traveler not found"}), 404

    companions = []
    for c in traveler.companions:
        companions.append({
            "id": c.id,
            "pesel": c.pesel,
            "first_name": c.first_name,
            "last_name": c.last_name,
            "age": c.age,
            "phone_number": c.phone_number,
            "email": c.email,
            "passport_number": c.passport_number,
            "id_card_number": c.id_card_number,
            "added_by_pesel": c.added_by_pesel
        })

    return jsonify({
        "traveler_pesel": traveler.pesel,
        "companions": companions
    })
