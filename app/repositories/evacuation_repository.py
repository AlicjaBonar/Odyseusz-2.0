from sqlalchemy.orm import Session
from app.models import Evacuation
from typing import Optional, List


class EvacuationRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, evacuation_id: int) -> Optional[Evacuation]:
        return self.db.query(Evacuation).filter_by(id=evacuation_id).first()
    
    def get_all(self) -> List[Evacuation]:
        return self.db.query(Evacuation).all()
    
    def create(self, evacuation: Evacuation) -> Evacuation:
        self.db.add(evacuation)
        self.db.flush()
        return evacuation
    
    def update(self, evacuation: Evacuation) -> Evacuation:
        self.db.flush()
        return evacuation
    
    def delete(self, evacuation: Evacuation) -> None:
        self.db.delete(evacuation)
