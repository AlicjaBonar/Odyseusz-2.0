from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from typing import Dict, Optional, List
from app.models import Notification, Traveler, Trip, Stage, Location, City, Evacuation, EvacuationStatus
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
        """
        Tworzy ewakuację i automatycznie wysyła powiadomienia do podróżnych
        przebywających w danym kraju lub mieście.
        """
        # 1. Walidacja pól wejściowych (dostosowana do Twojego API)
        required_fields = ["action_name", "event_description", "country_id", "start_date"]
        missing_fields = [field for field in required_fields if field not in evacuation_data]
        if missing_fields:
            raise ValueError(f"Brakujące pola: {missing_fields}")
        
        country_id = int(evacuation_data["country_id"])
        city_id = int(evacuation_data["city_id"]) if evacuation_data.get("city_id") else None
        event_description = evacuation_data["event_description"]
        action_name = evacuation_data["action_name"]
        
        # 2. Utworzenie obiektu ewakuacji (płaski model)
        new_evacuation = Evacuation(
            action_name=action_name,
            event_description=event_description,
            start_date=datetime.fromisoformat(evacuation_data["start_date"]),
            status=EvacuationStatus.PLANNED,
            country_id=country_id,
            city_id=city_id
        )
        self.db.add(new_evacuation)
        self.db.flush()  # Pobieramy ID dla celów zwrócenia w JSON
        
        # 3. Znalezienie podróżnych przebywających w zagrożonym obszarze
        current_time = datetime.now()
        
        # Budujemy bazowe zapytanie łączące podróżnych z ich aktualną lokalizacją
        query = self.db.query(Traveler).join(Trip).join(Stage).join(Location).join(City)
        
        # Filtrowanie po czasie (podróż musi trwać w tym momencie)
        query = query.filter(and_(Stage.start_date <= current_time, Stage.end_date >= current_time))
        
        # Filtrowanie po lokalizacji (miasto LUB cały kraj)
        if city_id:
            query = query.filter(City.id == city_id)
            location_name = self.db.query(City.name).filter(City.id == city_id).scalar() or "Twojej lokalizacji"
        else:
            query = query.filter(City.country_id == country_id)
            location_name = self.db.query(Country.name).filter(Country.id == country_id).scalar() or "Twojego kraju"
        
        affected_travelers = query.distinct(Traveler.pesel).all()
        
        # 4. Utworzenie powiadomień dla każdego znalezionego podróżnego
        notified_count = 0
        for traveler in affected_travelers:
            msg = f"ALERT EWAKUACYJNY: W {location_name} ogłoszono akcję: {action_name}. {event_description}. Prosimy o kontakt z konsulatem."
            
            notification = Notification(
                traveler_pesel=traveler.pesel,
                message=msg,
                created_at=current_time,
                is_read=False
            )
            self.db.add(notification)
            notified_count += 1
        
        # 5. Zapisanie wszystkich zmian w jednej transakcji
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Błąd bazy danych: {str(e)}")
        
        return {
            "message": "Ewakuacja utworzona i alarm wysłany",
            "affected_travelers_count": notified_count,
            "evacuation_id": new_evacuation.id,
            "location": location_name
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
