# app/views/notifications.py
from flask import Blueprint, request, jsonify, g, render_template
from app.services.notification_service import (
    NotificationService,
    NotificationServiceError,
    NotificationNotFoundError,
    TravelerNotFoundError
)
from app.services.traveler_service import TravelerService
from app.models import Traveler
from flask_login import login_required, current_user

# Tworzymy Blueprint
notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('/notifications/all', methods=['GET'])
def get_all_notifications():
    try:
        service = NotificationService(g.db)
        notifications = service.get_all_notifications()
        return jsonify(notifications), 200
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# --- ENDPOINT 1: Admin ogłasza ewakuację (Backend) ---
@notifications_bp.route('/evacuations', methods=['POST'])
def create_evacuation():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        service = NotificationService(g.db)
        result = service.create_evacuation_notifications(data)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except NotificationServiceError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# --- ENDPOINT 2: Podróżny pobiera swoje powiadomienia (API JSON) ---
@notifications_bp.route('/travelers/<pesel>/notifications', methods=['GET'])
def get_notifications(pesel):
    try:
        service = NotificationService(g.db)
        notifications = service.get_notifications_by_traveler_pesel(pesel)
        # Format dla kompatybilności z frontendem
        results = [{
            "id": n["id"],
            "message": n["message"],
            "created_at": n["created_at"][:16],  # Format: YYYY-MM-DD HH:MM
            "is_read": n["is_read"]
        } for n in notifications]
        return jsonify(results)
    except TravelerNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# --- ENDPOINT 3: Dashboard Podróżnego (Widok HTML) ---
@notifications_bp.route('/dashboard/<pesel>')
def traveler_dashboard(pesel):
    try:
        service = TravelerService(g.db)
        traveler = service.get_traveler_by_pesel(pesel)
        if not traveler:
            return "Błąd: Nie znaleziono podróżnego", 404
        return render_template('dashboard.html', traveler=traveler)
    except Exception as e:
        return f"Błąd: {str(e)}", 500


# --- ENDPOINT 4: Widok strony powiadomień (Widok HTML) ---
@notifications_bp.route('/notifications_page')
@login_required
def notifications_page():
    traveler = current_user
    if not traveler:
        return "Nie znaleziono użytkownika", 404
    return render_template('notifications.html', traveler=traveler)


# Zmiana statusu wiadomości na przeczytany
@notifications_bp.route('/notifications/<int:notification_id>/mark_read', methods=['POST'])
def mark_notification_read(notification_id):
    try:
        service = NotificationService(g.db)
        result = service.mark_notification_read(notification_id)
        return jsonify(result), 200
    except NotificationNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# Pobieranie preferencji powiadomień
@notifications_bp.route('/travelers/<pesel>/preferences', methods=['GET'])
def get_preferences(pesel):
    try:
        service = NotificationService(g.db)
        preferences = service.get_traveler_preferences(pesel)
        return jsonify(preferences)
    except TravelerNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# Zapisywanie nowych preferencji
@notifications_bp.route('/travelers/<pesel>/preferences', methods=['POST'])
def save_preferences(pesel):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        service = NotificationService(g.db)
        result = service.update_traveler_preferences(pesel, data)
        return jsonify(result), 200
    except TravelerNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500