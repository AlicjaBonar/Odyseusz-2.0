from flask import Flask, jsonify, request, g
from app.database.database import SessionLocal, engine, Base
from app.models import (
    Country, Consulate, Employee, City, Location,
    Traveler, Evacuation, EvacuationArea, Trip, Stage
)
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
import sys

app = Flask(__name__)

try:
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully (if they didn't exist).")
except Exception as e:
    print(f"Error creating tables: {e}", file=sys.stderr)


# Otwieramy sesję bazy danych przed każdym żądaniem
@app.before_request
def create_session():
    g.db = SessionLocal()


# Zamykanie sesji po zakończeniu żądania
@app.teardown_request
def shutdown_session(exception=None):
    SessionLocal.remove()



@app.route("/travelers", methods=["POST"])
def create_traveler():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    required_fields = ["pesel", "first_name", "last_name", "email", "login", "password"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": f"Missing fields. Required: {required_fields}"}), 400

    # Haszujemy hasło
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
        }), 201  # 201 Created
    except IntegrityError:
        g.db.rollback()
        return jsonify(
            {"error": "Traveler with this pesel, email, login, phone, passport, or id card already exists."}), 409
    except Exception as e:
        g.db.rollback()
        return jsonify({"error": f"An error occurred: {e}"}), 500


@app.route("/travelers", methods=["GET"])
def get_travelers():
    travelers = g.db.query(Traveler).all()

    result = [
        {
            "pesel": p.pesel,
            "first_name": p.first_name,
            "last_name": p.last_name,
            "email": p.email,
            "login": p.login,
            "age": p.age
            # Nigdy nie zwracamy hasła!
        } for p in travelers
    ]
    return jsonify(result)



@app.route("/countries", methods=["POST"])
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
        return jsonify({"error": f"An error occurred: {e}"}), 500


@app.route("/cities", methods=["POST"])
def create_city():
    data = request.get_json()
    if not data or "name" not in data or "country_id" not in data:
        return jsonify({"error": "Fields 'name' and 'country_id' are required"}), 400

    country = g.db.query(Country).filter_by(id=data["country_id"]).first()
    if not country:
        return jsonify({"error": "Country with the given id does not exist"}), 404

    new_city = City(
        name=data["name"],
        country=country
    )

    try:
        g.db.add(new_city)
        g.db.commit()
        return jsonify({
            "id": new_city.id,
            "name": new_city.name,
            "country_id": new_city.country_id
        }), 201
    except Exception as e:
        g.db.rollback()
        return jsonify({"error": f"An error occurred: {e}"}), 500


@app.route("/countries/<int:country_id>", methods=["GET"])
def get_country_with_cities(country_id):
    country = g.db.query(Country).filter_by(id=country_id).first()

    if not country:
        return jsonify({"error": "Country not found"}), 404

    city_list = [
        {"id": city.id, "name": city.name} for city in country.cities
    ]

    return jsonify({
        "id": country.id,
        "name": country.name,
        "cities": city_list  # Zwracamy listę miast
    })



@app.route("/trips", methods=["POST"])
def create_trip():
    data = request.get_json()
    if not data or "status" not in data or "traveler_pesel" not in data:
        return jsonify({"error": "Fields 'status' and 'traveler_pesel' are required"}), 400

    traveler = g.db.query(Traveler).filter_by(pesel=data["traveler_pesel"]).first()
    if not traveler:
        return jsonify({"error": "Traveler with the given pesel does not exist"}), 404

    evacuation_id = data.get("evacuation_id")
    if evacuation_id:
        evacuation = g.db.query(Evacuation).filter_by(id=evacuation_id).first()
        if not evacuation:
            return jsonify({"error": "Evacuation with the given id does not exist"}), 404

    new_trip = Trip(
        status=data["status"],
        traveler=traveler,  # Używamy relacji
        evacuation_id=evacuation_id
    )

    try:
        g.db.add(new_trip)
        g.db.commit()
        return jsonify({
            "id": new_trip.id,
            "status": new_trip.status,
            "traveler_pesel": new_trip.traveler_pesel,
            "evacuation_id": new_trip.evacuation_id
        }), 201
    except Exception as e:
        g.db.rollback()
        return jsonify({"error": f"An error occurred: {e}"}), 500


@app.route("/travelers/<string:traveler_pesel>/trips", methods=["GET"])
def get_traveler_trips(traveler_pesel):
    traveler = g.db.query(Traveler).filter_by(pesel=traveler_pesel).first()

    if not traveler:
        return jsonify({"error": "Traveler not found"}), 404

    trip_list = [
        {
            "id": trip.id,
            "status": trip.status,
            "evacuation_id": trip.evacuation_id
        }
        for trip in traveler.trips
    ]

    return jsonify({
        "pesel": traveler.pesel,
        "first_name": traveler.first_name,
        "last_name": traveler.last_name,
        "trips": trip_list
    })



if __name__ == "__main__":
    app.run(debug=True)