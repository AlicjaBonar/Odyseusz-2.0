from sqlalchemy.orm import Session
from app.models import Companion, Traveler
from typing import Optional, List


class CompanionRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, companion_id: int) -> Optional[Companion]:
        return self.db.query(Companion).filter_by(id=companion_id).first()
    
    def find_by_traveler_pesel(self, traveler_pesel: str) -> List[Companion]:
        return self.db.query(Companion).filter_by(added_by_pesel=traveler_pesel).all()
    
    def get_all(self) -> List[Companion]:
        return self.db.query(Companion).all()
    
    def create(self, companion: Companion) -> Companion:
        self.db.add(companion)
        self.db.flush()
        return companion
    
    def update(self, companion: Companion) -> Companion:
        self.db.flush()
        return companion
    
    def delete(self, companion: Companion) -> None:
        self.db.delete(companion)
