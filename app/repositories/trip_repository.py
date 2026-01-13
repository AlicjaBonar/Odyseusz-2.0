from sqlalchemy.orm import Session
from app.models import Trip, Traveler
from typing import Optional, List


class TripRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, trip_id: int) -> Optional[Trip]:
        return self.db.query(Trip).filter_by(id=trip_id).first()
    
    def find_by_traveler_pesel(self, traveler_pesel: str) -> List[Trip]:
        return self.db.query(Trip).filter_by(traveler_pesel=traveler_pesel).all()
    
    def get_all(self) -> List[Trip]:
        return self.db.query(Trip).all()
    
    def create(self, trip: Trip) -> Trip:
        self.db.add(trip)
        self.db.flush()
        return trip
    
    def update(self, trip: Trip) -> Trip:
        self.db.flush()
        return trip
    
    def delete(self, trip: Trip) -> None:
        self.db.delete(trip)
