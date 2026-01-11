"""
Service dla Companion - logika biznesowa
"""
from sqlalchemy.orm import Session
from typing import Dict, Optional, List
from app.models import Companion, Traveler
from app.repositories.companion_repository import CompanionRepository
from app.repositories.traveler_repository import TravelerRepository


class CompanionServiceError(Exception):
    pass


class CompanionNotFoundError(CompanionServiceError):
    pass


class TravelerNotFoundError(CompanionServiceError):
    pass


class CompanionService:
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = CompanionRepository(db)
        self.traveler_repository = TravelerRepository(db)
    
    def create_companion(self, companion_data: Dict) -> Dict:
        required_fields = ["pesel", "first_name", "last_name", "added_by_pesel"]
        missing_fields = [field for field in required_fields if field not in companion_data]
        if missing_fields:
            raise ValueError(f"Brakujące pola: {missing_fields}")
        
        # Sprawdzenie czy podróżny istnieje
        traveler = self.traveler_repository.find_by_pesel(companion_data["added_by_pesel"])
        if not traveler:
            raise TravelerNotFoundError("Podróżny nie został znaleziony")
        
        # Utworzenie companion
        companion = Companion(
            pesel=companion_data["pesel"],
            first_name=companion_data["first_name"],
            last_name=companion_data["last_name"],
            age=companion_data.get("age"),
            phone_number=companion_data.get("phone_number"),
            email=companion_data.get("email"),
            passport_number=companion_data.get("passport_number"),
            id_card_number=companion_data.get("id_card_number"),
            added_by_pesel=traveler.pesel
        )
        
        self.repository.create(companion)
        self.db.commit()
        self.db.refresh(companion)
        
        return self._companion_to_dict(companion)
    
    def get_companion_by_id(self, companion_id: int) -> Optional[Dict]:
        companion = self.repository.find_by_id(companion_id)
        if not companion:
            return None
        return self._companion_to_dict(companion)
    
    def get_all_companions(self) -> List[Dict]:
        companions = self.repository.get_all()
        return [self._companion_to_dict(c) for c in companions]
    
    def get_companions_by_traveler_pesel(self, traveler_pesel: str) -> Dict:
        traveler = self.traveler_repository.find_by_pesel(traveler_pesel)
        if not traveler:
            raise TravelerNotFoundError("Podróżny nie został znaleziony")
        
        companions = self.repository.find_by_traveler_pesel(traveler_pesel)
        return {
            "traveler_pesel": traveler_pesel,
            "companions": [self._companion_to_dict(c) for c in companions]
        }
    
    def update_companion(self, companion_id: int, companion_data: Dict) -> Dict:
        companion = self.repository.find_by_id(companion_id)
        if not companion:
            raise CompanionNotFoundError("Companion nie został znaleziony")
        
        # Aktualizacja pól
        updatable_fields = ["pesel", "first_name", "last_name", "age", "phone_number", 
                           "email", "passport_number", "id_card_number"]
        for field in updatable_fields:
            if field in companion_data:
                setattr(companion, field, companion_data[field])
        
        # Aktualizacja added_by_pesel jeśli podano
        if "added_by_pesel" in companion_data:
            traveler = self.traveler_repository.find_by_pesel(companion_data["added_by_pesel"])
            if not traveler:
                raise TravelerNotFoundError("Podróżny nie został znaleziony")
            companion.added_by_pesel = traveler.pesel
        
        self.repository.update(companion)
        self.db.commit()
        self.db.refresh(companion)
        
        return self._companion_to_dict(companion)
    
    def delete_companion(self, companion_id: int) -> None:
        companion = self.repository.find_by_id(companion_id)
        if not companion:
            raise CompanionNotFoundError("Companion nie został znaleziony")
        
        self.repository.delete(companion)
        self.db.commit()
    
    def _companion_to_dict(self, companion: Companion) -> Dict:
        return {
            "id": companion.id,
            "pesel": companion.pesel,
            "first_name": companion.first_name,
            "last_name": companion.last_name,
            "age": companion.age,
            "phone_number": companion.phone_number,
            "email": companion.email,
            "passport_number": companion.passport_number,
            "id_card_number": companion.id_card_number,
            "added_by_pesel": companion.added_by_pesel
        }
