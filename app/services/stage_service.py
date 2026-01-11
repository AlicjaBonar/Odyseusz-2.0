from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Optional, List
from app.models import Stage, Trip, Location
from app.repositories.stage_repository import StageRepository


class StageServiceError(Exception):
    pass


class StageNotFoundError(StageServiceError):
    pass


class TripNotFoundError(StageServiceError):
    pass


class LocationNotFoundError(StageServiceError):
    pass


class StageService:
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = StageRepository(db)
    
    def create_stage(self, stage_data: Dict) -> Dict:
        required_fields = ["start_date", "end_date", "trip_id", "location_id"]
        missing_fields = [field for field in required_fields if field not in stage_data]
        if missing_fields:
            raise ValueError(f"Brakujące pola: {missing_fields}")
        
        # Parsowanie dat
        try:
            start_date = datetime.fromisoformat(stage_data["start_date"])
            end_date = datetime.fromisoformat(stage_data["end_date"])
        except ValueError:
            raise ValueError("Daty muszą być w formacie ISO")
        
        # Sprawdzenie czy podróż istnieje
        trip = self.db.query(Trip).filter_by(id=stage_data["trip_id"]).first()
        if not trip:
            raise TripNotFoundError("Podróż nie została znaleziona")
        
        # Sprawdzenie czy lokalizacja istnieje
        location = self.db.query(Location).filter_by(id=stage_data["location_id"]).first()
        if not location:
            raise LocationNotFoundError("Lokalizacja nie została znaleziona")
        
        # Utworzenie etapu
        stage = Stage(
            start_date=start_date,
            end_date=end_date,
            trip_id=stage_data["trip_id"],
            location_id=stage_data["location_id"]
        )
        
        self.repository.create(stage)
        self.db.commit()
        self.db.refresh(stage)
        
        return self._stage_to_dict(stage)
    
    def get_stage_by_id(self, stage_id: int) -> Optional[Dict]:
        stage = self.repository.find_by_id(stage_id)
        if not stage:
            return None
        return self._stage_to_dict(stage)
    
    def get_all_stages(self) -> List[Dict]:
        stages = self.repository.get_all()
        return [self._stage_to_dict(s) for s in stages]
    
    def update_stage(self, stage_id: int, stage_data: Dict) -> Dict:
        stage = self.repository.find_by_id(stage_id)
        if not stage:
            raise StageNotFoundError("Etap nie został znaleziony")
        
        if "start_date" in stage_data:
            try:
                stage.start_date = datetime.fromisoformat(stage_data["start_date"])
            except ValueError:
                raise ValueError("Data start_date musi być w formacie ISO")
        
        if "end_date" in stage_data:
            try:
                stage.end_date = datetime.fromisoformat(stage_data["end_date"])
            except ValueError:
                raise ValueError("Data end_date musi być w formacie ISO")
        
        if "trip_id" in stage_data:
            trip = self.db.query(Trip).filter_by(id=stage_data["trip_id"]).first()
            if not trip:
                raise TripNotFoundError("Podróż nie została znaleziona")
            stage.trip_id = stage_data["trip_id"]
        
        if "location_id" in stage_data:
            location = self.db.query(Location).filter_by(id=stage_data["location_id"]).first()
            if not location:
                raise LocationNotFoundError("Lokalizacja nie została znaleziona")
            stage.location_id = stage_data["location_id"]
        
        self.repository.update(stage)
        self.db.commit()
        self.db.refresh(stage)
        
        return self._stage_to_dict(stage)
    
    def delete_stage(self, stage_id: int) -> None:
        stage = self.repository.find_by_id(stage_id)
        if not stage:
            raise StageNotFoundError("Etap nie został znaleziony")
        
        self.repository.delete(stage)
        self.db.commit()
    
    def _stage_to_dict(self, stage: Stage) -> Dict:
        return {
            "id": stage.id,
            "start_date": stage.start_date.isoformat(),
            "end_date": stage.end_date.isoformat(),
            "trip_id": stage.trip_id,
            "location_id": stage.location_id
        }
