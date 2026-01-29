from app.models import ConsularWarning
from app.database.database import SessionLocal

class WarningRepository:
    def get_all(self):
        with SessionLocal() as session:
            return session.query(ConsularWarning).all()

    def find_by_external_id(self, ext_id):
        with SessionLocal() as session:
            return session.query(ConsularWarning).filter_by(external_id=ext_id).first()

    def add(self, data):
        with SessionLocal() as session:
            new_w = ConsularWarning(**data)
            session.add(new_w)
            session.commit()

    def update(self, ext_id, data):
        with SessionLocal() as session:
            session.query(ConsularWarning).filter_by(external_id=ext_id).update(data)
            session.commit()

warning_repo = WarningRepository()