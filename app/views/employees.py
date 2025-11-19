from flask import Blueprint, request, jsonify, g
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from app.models import Employee

employees_bp = Blueprint("employees", __name__)

@employees_bp.route("/register_employee", methods=["POST"])
def create_employee():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    required = ["pesel", "first_name", "last_name", "email", "login", "password", "role", "consulate_id"]
    if not all(field in data for field in required):
        return jsonify({"error": f"Missing fields: {required}"}), 400

    hashed_password = generate_password_hash(data["password"])

    new_employee = Employee(
        pesel=data["pesel"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        email=data["email"],
        login=data["login"],
        password_hash=hashed_password,
        role=data["role"],
        consulate_id=data["consulate_id"],
        age=data.get("age"),
        phone_number=data.get("phone_number"),
        passport_number=data.get("passport_number"),
        id_card_number=data.get("id_card_number")
    )

    try:
        g.db.add(new_employee)
        g.db.commit()

        return jsonify({
            "pesel": new_employee.pesel,
            "email": new_employee.email,
            "login": new_employee.login,
            "role": new_employee.role,
            "consulate_id": new_employee.consulate_id
        }), 201

    except IntegrityError:
        g.db.rollback()
        return jsonify({"error": "Employee with this pesel or login already exists"}), 409

    except Exception as e:
        g.db.rollback()
        return jsonify({"error": str(e)}), 500
