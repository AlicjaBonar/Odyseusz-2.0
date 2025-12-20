# app/views/notifications.py
from flask import Blueprint, request, jsonify, g, render_template, url_for
from sqlalchemy import and_
from datetime import datetime
from app.models import Evacuation, EvacuationArea, City, Traveler, Trip, Stage, Location, Notification
from flask_login import login_required, current_user

# Tworzymy Blueprint
notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/notifications/all', methods=['GET'])
def get_all_notifications():
    """
    Zwraca wszystkie powiadomienia w systemie.
    """
    db = g.db  # scoped_session ze 'before_request'

    notifications = db.query(Notification).order_by(Notification.created_at.desc()).all()

    result = []
    for n in notifications:
        result.append({
            "id": n.id,
            "traveler_pesel": n.traveler_pesel,  # lub login/pesel, jeśli wolisz
            "message": n.message,
            "is_read": n.is_read,
            "created_at": n.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    # Relacja
    return jsonify(result), 200

# --- ENDPOINT 1: Admin ogłasza ewakuację (Backend) ---
@notifications_bp.route('/evacuations', methods=['POST'])
def create_evacuation():
    data = request.get_json()
    city_id = int(data.get('city_id'))
    description = data.get('description')
    action_name = data.get('action_name', 'Zagrożenie')

    new_evacuation = Evacuation(
        action_name=action_name,
        event_description=description,
        start_date=datetime.now()
    )
    g.db.add(new_evacuation)
    g.db.flush()  # Pobieramy ID

    area = EvacuationArea(evacuation_id=new_evacuation.id, city_id=city_id)
    g.db.add(area)

    # 2. LOGIKA: Znajdź ludzi w tym mieście
    current_time = datetime.now()

    # Szukamy Travelerów, którzy mają aktywny Stage w tym City
    affected_travelers = g.db.query(Traveler).join(Trip).join(Stage).join(Location).join(City) \
        .filter(City.id == city_id) \
        .filter(and_(Stage.start_date <= current_time, Stage.end_date >= current_time)) \
        .all()

    notified_count = 0

    # 3. Wyślij (utwórz) powiadomienia
    city_obj = g.db.query(City).filter(City.id == city_id).first()
    city_name = city_obj.name if city_obj else "Twojej lokalizacji"

    for traveler in affected_travelers:
        msg = f"ALERT: W {city_name} wystąpiło zagrożenie: {description}. Postępuj zgodnie z instrukcjami."

        notification = Notification(
            traveler_pesel=traveler.pesel,
            message=msg,
            created_at=current_time
        )
        g.db.add(notification)
        notified_count += 1

    g.db.commit()

    return jsonify({
        "message": "Alarm ogłoszony pomyślnie",
        "affected_travelers_count": notified_count
    }), 201


# --- ENDPOINT 2: Podróżny pobiera swoje powiadomienia (API JSON) ---
@notifications_bp.route('/travelers/<pesel>/notifications', methods=['GET'])
def get_notifications(pesel):
    notifs = g.db.query(Notification) \
        .filter(Notification.traveler_pesel == pesel) \
        .order_by(Notification.created_at.desc()) \
        .all()

    results = [{
        "id": n.id,
        "message": n.message,
        "created_at": n.created_at.strftime("%Y-%m-%d %H:%M"),
        "is_read": n.is_read
    } for n in notifs]

    return jsonify(results)


# --- ENDPOINT 3: Dashboard Podróżnego (Widok HTML) ---
@notifications_bp.route('/dashboard/<pesel>')
def traveler_dashboard(pesel):
    # Pobieramy dane podróżnego z bazy
    traveler = g.db.query(Traveler).filter(Traveler.pesel == pesel).first()

    if not traveler:
        return "Błąd: Nie znaleziono podróżnego", 404

    return render_template('dashboard.html', traveler=traveler)


# --- ENDPOINT 4: Widok strony powiadomień (Widok HTML) ---

@notifications_bp.route('/notifications_page')
@login_required
def notifications_page():
    # Pobieramy dane podróżnego na podstawie PESELu
    traveler = current_user

    if not traveler:
        return "Nie znaleziono użytkownika", 404

    return render_template('notifications.html', traveler=traveler)


#kolejny endpoint to zmiany statusu wiadomości na przeczytany
@notifications_bp.route('/notifications/<int:notification_id>/mark_read', methods=['POST'])
def mark_notification_read(notification_id):
    notification = g.db.query(Notification).filter(Notification.id == notification_id).first()

    if not notification:
        return jsonify({"error": "Powiadomienie nie istnieje"}), 404

    notification.is_read = True
    g.db.commit()

    return jsonify({"success": True}), 200




#pobieranie preferencji powiadomień
@notifications_bp.route('/travelers/<pesel>/preferences', methods=['GET'])
def get_preferences(pesel):
    traveler = g.db.query(Traveler).filter(Traveler.pesel == pesel).first()
    if not traveler:
        return jsonify({"error": "Nie znaleziono podróżnego"}), 404

    return jsonify({
        "sms": traveler.pref_sms,
        "email": traveler.pref_email,
        "push": traveler.pref_push
    })


#zapisywanie nowych preferencji
@notifications_bp.route('/travelers/<pesel>/preferences', methods=['POST'])
def save_preferences(pesel):
    data = request.get_json()
    traveler = g.db.query(Traveler).filter(Traveler.pesel == pesel).first()

    if not traveler:
        return jsonify({"error": "Nie znaleziono podróżnego"}), 404

    traveler.pref_sms = data.get('sms', False)
    traveler.pref_email = data.get('email', False)
    traveler.pref_push = data.get('push', False)

    g.db.commit()

    return jsonify({"message": "Zapisano preferencje"}), 200