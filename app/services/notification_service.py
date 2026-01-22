from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from typing import Dict, Optional, List
from app.models import Notification, Traveler, Trip, Stage, Location, City, Evacuation
from app.repositories.notification_repository import NotificationRepository
from app.repositories.traveler_repository import TravelerRepository


class NotificationServiceError(Exception):
    pass


class NotificationNotFoundError(NotificationServiceError):
    pass


class TravelerNotFoundError(NotificationServiceError):
    pass


class NotificationService:
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = NotificationRepository(db)
        self.traveler_repository = TravelerRepository(db)
    
    def create_notification(self, notification_data: Dict) -> Dict:
        required_fields = ["traveler_pesel", "message"]
        missing_fields = [field for field in required_fields if field not in notification_data]
        if missing_fields:
            raise ValueError(f"Brakujące pola: {missing_fields}")
        
        # Sprawdzenie czy podróżny istnieje
        traveler = self.traveler_repository.find_by_pesel(notification_data["traveler_pesel"])
        if not traveler:
            raise TravelerNotFoundError("Podróżny nie został znaleziony")
        
        notification = Notification(
            traveler_pesel=notification_data["traveler_pesel"],
            message=notification_data["message"],
            created_at=datetime.now()
        )
        
        self.repository.create(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        return self._notification_to_dict(notification)
    
    def create_evacuation_notifications(self, evacuation_data: Dict) -> Dict:
        required_fields = ["city_id", "description"]
        missing_fields = [field for field in required_fields if field not in evacuation_data]
        if missing_fields:
            raise ValueError(f"Brakujące pola: {missing_fields}")
        
        city_id = int(evacuation_data["city_id"])
        description = evacuation_data["description"]
        action_name = evacuation_data.get("action_name", "Zagrożenie")
        
        # Utworzenie ewakuacji
        new_evacuation = Evacuation(
            action_name=action_name,
            event_description=description,
            start_date=datetime.now()
        )
        self.db.add(new_evacuation)
        self.db.flush()
        
        # Utworzenie obszaru ewakuacji
        # area = EvacuationArea(evacuation_id=new_evacuation.id, city_id=city_id)
        self.db.add(area)
        
        # Znajdź podróżnych w tym mieście
        current_time = datetime.now()
        affected_travelers = self.db.query(Traveler).join(Trip).join(Stage).join(Location).join(City)\
            .filter(City.id == city_id)\
            .filter(and_(Stage.start_date <= current_time, Stage.end_date >= current_time))\
            .all()
        
        # Pobierz nazwę miasta
        city_obj = self.db.query(City).filter(City.id == city_id).first()
        city_name = city_obj.name if city_obj else "Twojej lokalizacji"
        
        # Utworzenie powiadomień
        notified_count = 0
        for traveler in affected_travelers:
            msg = f"ALERT: W {city_name} wystąpiło zagrożenie: {description}. Postępuj zgodnie z instrukcjami."
            
            notification = Notification(
                traveler_pesel=traveler.pesel,
                message=msg,
                created_at=current_time
            )
            self.db.add(notification)
            notified_count += 1
        
        self.db.commit()
        
        return {
            "message": "Alarm ogłoszony pomyślnie",
            "affected_travelers_count": notified_count,
            "evacuation_id": new_evacuation.id
        }
    
    def get_notification_by_id(self, notification_id: int) -> Optional[Dict]:
        notification = self.repository.find_by_id(notification_id)
        if not notification:
            return None
        return self._notification_to_dict(notification)
    
    def get_all_notifications(self) -> List[Dict]:
        notifications = self.repository.get_all()
        return [self._notification_to_dict(n) for n in notifications]
    
    def get_notifications_by_traveler_pesel(self, traveler_pesel: str) -> List[Dict]:
        notifications = self.repository.find_by_traveler_pesel(traveler_pesel)
        return [self._notification_to_dict(n) for n in notifications]
    
    def mark_notification_read(self, notification_id: int) -> Dict:
        notification = self.repository.find_by_id(notification_id)
        if not notification:
            raise NotificationNotFoundError("Powiadomienie nie istnieje")
        
        notification.is_read = True
        self.repository.update(notification)
        self.db.commit()
        
        return {"success": True}
    
    def get_traveler_preferences(self, traveler_pesel: str) -> Dict:
        traveler = self.traveler_repository.find_by_pesel(traveler_pesel)
        if not traveler:
            raise TravelerNotFoundError("Podróżny nie został znaleziony")
        
        return {
            "sms": traveler.pref_sms,
            "email": traveler.pref_email,
            "push": traveler.pref_push
        }
    
    def update_traveler_preferences(self, traveler_pesel: str, preferences: Dict) -> Dict:
        traveler = self.traveler_repository.find_by_pesel(traveler_pesel)
        if not traveler:
            raise TravelerNotFoundError("Podróżny nie został znaleziony")
        
        traveler.pref_sms = preferences.get("sms", False)
        traveler.pref_email = preferences.get("email", False)
        traveler.pref_push = preferences.get("push", False)
        
        self.traveler_repository.update(traveler)
        self.db.commit()
        
        return {"message": "Zapisano preferencje"}
    
    def _notification_to_dict(self, notification: Notification) -> Dict:
        """Konwertuj obiekt Notification na słownik"""
        return {
            "id": notification.id,
            "traveler_pesel": notification.traveler_pesel,
            "message": notification.message,
            "is_read": notification.is_read,
            "created_at": notification.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
