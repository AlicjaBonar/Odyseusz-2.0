from flask import Blueprint, request, jsonify, g
from app.services.employee_service import (
    EmployeeService,
    EmployeeServiceError,
    EmployeeAlreadyExistsError
)

employees_bp = Blueprint("employees", __name__)


@employees_bp.route("/register_employee", methods=["POST"])
def create_employee():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        service = EmployeeService(g.db)
        result = service.create_employee(data)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except EmployeeAlreadyExistsError as e:
        return jsonify({"error": str(e)}), 409
    except EmployeeServiceError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
