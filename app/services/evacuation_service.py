from sqlalchemy.orm import Session
from typing import Dict, Optional, List
from app.models import Evacuation, City, Country, EvacuationStatus
from app.repositories.evacuation_repository import EvacuationRepository
from datetime import datetime


class EvacuationServiceError(Exception):
    pass


class EvacuationNotFoundError(EvacuationServiceError):
    pass


class EvacuationService:
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = EvacuationRepository(db)
    
    def get_evacuation_by_id(self, evacuation_id: int) -> Optional[Dict]:
        evacuation = self.repository.find_by_id(evacuation_id)
        if not evacuation:
            return None
        return self._evacuation_to_dict(evacuation)
    
    def get_all_evacuations(self) -> List[Dict]:
        evacuations = self.repository.get_all()
        return [self._evacuation_to_dict(e) for e in evacuations]
    
    def _evacuation_to_dict(self, evacuation: Evacuation) -> Dict:
        return {
            "id": evacuation.id,
            "action_name": evacuation.action_name,
            "event_description": evacuation.event_description,
            "start_date": evacuation.start_date.isoformat() if evacuation.start_date else None,
            "end_date": evacuation.end_date.isoformat() if evacuation.end_date else None,
            "status": evacuation.status.value if evacuation.status else None,
            "city_id": evacuation.city_id,
            "country_id": evacuation.country_id,
        }
    
    def create_evacuation(self, data):
        # 1. Walidacja pól (Używamy 'event_description' zamiast 'description')
        required_fields = ["action_name", "event_description", "start_date"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            raise ValueError(f"Brakujące ważne pola: {missing_fields}")

        # 2. Tworzenie obiektu Evacuation
        new_evac = Evacuation(
            action_name=data.get("action_name"),
            start_date=datetime.fromisoformat(data.get("start_date")),
            # Zmienione na .get("event_description")
            event_description=data.get("event_description"), 
            end_date=datetime.fromisoformat(data.get("end_date")) if data.get("end_date") else None,
            status=EvacuationStatus.PLANNED,
            country_id=data.get("country_id"),
            city_id=data.get("city_id")
        )
        
        self.db.add(new_evac)
        self.db.flush()

        self.db.commit()
        self.db.refresh(new_evac)
        return new_evac.to_dict()
    
    def update_evacuation(self, evac_id, data):
        # 1. Pobranie istniejącej ewakuacji
        evac = self.db.query(Evacuation).get(evac_id)
        
        if not evac:
            raise ValueError(f"Ewakuacja o ID {evac_id} nie istnieje.")

        # 2. Aktualizacja pól tekstowych i liczbowych
        if "action_name" in data:
            evac.action_name = data["action_name"]
        
        if "event_description" in data:
            evac.event_description = data["event_description"]
            
        if "country_id" in data:
            evac.country_id = data["country_id"]
            
        if "city_id" in data:
            evac.city_id = data["city_id"]

        # 3. Aktualizacja statusu (jeśli przesyłasz go z frontendu)
        if "status" in data:
            # Zakładamy, że status przychodzi jako string, np. "planned"
            evac.status = EvacuationStatus(data["status"])

        # 4. Obsługa dat (parowanie z ISO format tak jak w create)
        if "start_date" in data and data["start_date"]:
            evac.start_date = datetime.fromisoformat(data["start_date"])
            
        if "end_date" in data:
            # Jeśli end_date jest w słowniku, ale jest nullem/pusty -> ustawiamy None
            evac.end_date = datetime.fromisoformat(data["end_date"]) if data["end_date"] else None

        # 5. Zapisanie zmian
        try:
            self.db.commit()
            self.db.refresh(evac)
            return evac.to_dict()
        except Exception as e:
            self.db.rollback()
            raise e
    
    def delete_evacuation(self, evac_id):
        """
        Usuwa ewakuację z bazy danych na podstawie jej ID.
        """
        # 1. Znalezienie rekordu
        evac = self.db.query(Evacuation).get(evac_id)
        
        if not evac:
            return False  # Zwracamy False, jeśli nie ma co usuwać

        try:
            # 2. Usunięcie obiektu
            self.db.delete(evac)
            
            # 3. Commit zmian
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e