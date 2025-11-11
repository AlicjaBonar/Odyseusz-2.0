from flask import Blueprint, jsonify, request, g
from app.models import Traveler
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

travelers_bp = Blueprint('travelers', __name__)

@travelers_bp.route("/travelers", methods=["POST"])
def create_traveler():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    required = ["pesel", "first_name", "last_name", "email", "login", "password"]
    if not all(field in data for field in required):
        return jsonify({"error": f"Missing fields: {required}"}), 400

    hashed_password = generate_password_hash(data["password"])
    new_traveler = Traveler(
        pesel=data["pesel"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        email=data["email"],
        login=data["login"],
        password_hash=hashed_password,
        age=data.get("age"),
        phone_number=data.get("phone_number"),
        passport_number=data.get("passport_number"),
        id_card_number=data.get("id_card_number")
    )

    try:
        g.db.add(new_traveler)
        g.db.commit()
        return jsonify({
            "pesel": new_traveler.pesel,
            "email": new_traveler.email,
            "login": new_traveler.login
        }), 201
    except IntegrityError:
        g.db.rollback()
        return jsonify({"error": "Traveler with this pesel or login already exists"}), 409
    except Exception as e:
        g.db.rollback()
        return jsonify({"error": str(e)}), 500


@travelers_bp.route("/travelers", methods=["GET"])
def get_travelers():
    travelers = g.db.query(Traveler).all()
    return jsonify([
        {
            "pesel": t.pesel,
            "first_name": t.first_name,
            "last_name": t.last_name,
            "email": t.email,
            "login": t.login,
            "age": t.age
        } for t in travelers
    ])
