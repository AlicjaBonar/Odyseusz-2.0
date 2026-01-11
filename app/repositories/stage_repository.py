from sqlalchemy.orm import Session
from app.models import Stage
from typing import Optional, List


class StageRepository:

    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, stage_id: int) -> Optional[Stage]:
        return self.db.query(Stage).filter_by(id=stage_id).first()
    
    def find_by_trip_id(self, trip_id: int) -> List[Stage]:
        return self.db.query(Stage).filter_by(trip_id=trip_id).all()
    
    def get_all(self) -> List[Stage]:
        return self.db.query(Stage).all()
    
    def create(self, stage: Stage) -> Stage:
        self.db.add(stage)
        self.db.flush()
        return stage
    
    def update(self, stage: Stage) -> Stage:
        self.db.flush()
        return stage
    
    def delete(self, stage: Stage) -> None:
        self.db.delete(stage)
