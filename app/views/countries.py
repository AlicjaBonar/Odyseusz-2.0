from flask import Blueprint, jsonify, request, g
from app.models import Country, City
from sqlalchemy.exc import IntegrityError

countries_bp = Blueprint('countries', __name__)

@countries_bp.route("/countries", methods=["POST"])
def create_country():
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "Field 'name' is required"}), 400

    new_country = Country(name=data["name"])

    try:
        g.db.add(new_country)
        g.db.commit()
        return jsonify({"id": new_country.id, "name": new_country.name}), 201
    except IntegrityError:
        g.db.rollback()
        return jsonify({"error": "Country with this name already exists"}), 409
    except Exception as e:
        g.db.rollback()
        return jsonify({"error": str(e)}), 500


@countries_bp.route("/cities", methods=["POST"])
def create_city():
    data = request.get_json()
    if not data or "name" not in data or "country_id" not in data:
        return jsonify({"error": "Fields 'name' and 'country_id' are required"}), 400

    country = g.db.query(Country).filter_by(id=data["country_id"]).first()
    if not country:
        return jsonify({"error": "Country not found"}), 404

    new_city = City(name=data["name"], country=country)
    try:
        g.db.add(new_city)
        g.db.commit()
        return jsonify({"id": new_city.id, "name": new_city.name, "country_id": new_city.country_id}), 201
    except Exception as e:
        g.db.rollback()
        return jsonify({"error": str(e)}), 500


@countries_bp.route("/countries/<int:country_id>", methods=["GET"])
def get_country_with_cities(country_id):
    country = g.db.query(Country).filter_by(id=country_id).first()
    if not country:
        return jsonify({"error": "Country not found"}), 404

    cities = [{"id": c.id, "name": c.name} for c in country.cities]
    return jsonify({"id": country.id, "name": country.name, "cities": cities})

@countries_bp.route("/countries", methods=["GET"])
def get_all_countries():
    countries = g.db.query(Country).all()
    result = []
    for country in countries:
        result.append({
            "id": country.id,
            "name": country.name,
            "cities": [{"id": c.id, "name": c.name} for c in country.cities]
        })
        print("nazwa", country.name )
    return jsonify(result)

