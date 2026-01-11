from sqlalchemy.orm import Session
from typing import Dict, Optional, List
from app.models import Evacuation, EvacuationArea, City, Country
from app.repositories.evacuation_repository import EvacuationRepository


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
        # Pobierz obszary ewakuacji
        areas = self.db.query(EvacuationArea).filter_by(evacuation_id=evacuation.id).all()
        cities = []
        countries = []
        
        for area in areas:
            city = self.db.query(City).filter_by(id=area.city_id).first()
            if city:
                cities.append({"id": city.id, "name": city.name})
                country = self.db.query(Country).filter_by(id=city.country_id).first()
                if country and country.id not in [c["id"] for c in countries]:
                    countries.append({"id": country.id, "name": country.name})
        
        return {
            "id": evacuation.id,
            "action_name": evacuation.action_name,
            "event_description": evacuation.event_description,
            "start_date": evacuation.start_date.isoformat() if evacuation.start_date else None,
            "end_date": evacuation.end_date.isoformat() if evacuation.end_date else None,
            "status": evacuation.status.value if evacuation.status else None,
            "cities": cities,
            "countries": countries
        }
