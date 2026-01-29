from sqlalchemy.orm import Session
from app.models import Traveler
from typing import Optional, List


class TravelerRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, traveler_id: int) -> Optional[Traveler]:
        return self.db.query(Traveler).filter_by(id=traveler_id).first()

    def find_by_pesel(self, pesel: str) -> Optional[Traveler]:
        return self.db.query(Traveler).filter_by(pesel=pesel).first()
    
    def find_by_login(self, login: str) -> Optional[Traveler]:
        return self.db.query(Traveler).filter_by(login=login).first()
    
    def find_by_email(self, email: str) -> Optional[Traveler]:
        return self.db.query(Traveler).filter_by(email=email).first()
    
    def get_all(self) -> List[Traveler]:
        return self.db.query(Traveler).all()
    
    def create(self, traveler: Traveler) -> Traveler:
        self.db.add(traveler)
        self.db.flush()
        return traveler
    
    def update(self, traveler: Traveler) -> Traveler:
        self.db.flush()
        return traveler
    
    def delete(self, traveler: Traveler) -> None:
        self.db.delete(traveler)
