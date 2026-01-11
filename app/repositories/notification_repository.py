from sqlalchemy.orm import Session
from app.models import Notification
from typing import Optional, List


class NotificationRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, notification_id: int) -> Optional[Notification]:
        return self.db.query(Notification).filter_by(id=notification_id).first()
    
    def find_by_traveler_pesel(self, traveler_pesel: str) -> List[Notification]:
        return self.db.query(Notification).filter_by(traveler_pesel=traveler_pesel)\
            .order_by(Notification.created_at.desc()).all()
    
    def get_all(self) -> List[Notification]:
        return self.db.query(Notification).order_by(Notification.created_at.desc()).all()
    
    def create(self, notification: Notification) -> Notification:
        self.db.add(notification)
        self.db.flush()
        return notification
    
    def update(self, notification: Notification) -> Notification:
        self.db.flush()
        return notification
    
    def delete(self, notification: Notification) -> None:
        self.db.delete(notification)
