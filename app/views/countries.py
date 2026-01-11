from flask import Blueprint, jsonify, request, g
from app.services.country_service import (
    CountryService,
    CityService,
    CountryServiceError,
    CountryAlreadyExistsError,
    CountryNotFoundError,
    CityServiceError
)

countries_bp = Blueprint('countries', __name__)


@countries_bp.route("/countries", methods=["POST"])
def create_country():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        service = CountryService(g.db)
        result = service.create_country(data)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except CountryAlreadyExistsError as e:
        return jsonify({"error": str(e)}), 409
    except CountryServiceError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@countries_bp.route("/cities", methods=["POST"])
def create_city():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        service = CityService(g.db)
        result = service.create_city(data)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except CountryNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except CityServiceError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@countries_bp.route("/countries/<int:country_id>", methods=["GET"])
def get_country_with_cities(country_id):
    try:
        service = CountryService(g.db)
        country = service.get_country_by_id(country_id)
        if not country:
            return jsonify({"error": "Country not found"}), 404
        return jsonify(country)
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@countries_bp.route("/countries", methods=["GET"])
def get_all_countries():
    try:
        service = CountryService(g.db)
        countries = service.get_all_countries()
        return jsonify(countries)
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

