"""
Repository dla Country - operacje na bazie danych
"""
from sqlalchemy.orm import Session
from app.models import Country
from typing import Optional, List


class CountryRepository:
    """Repository do zarządzania Country w bazie danych"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, country_id: int) -> Optional[Country]:
        """Znajdź kraj po ID"""
        return self.db.query(Country).filter_by(id=country_id).first()
    
    def find_by_name(self, name: str) -> Optional[Country]:
        """Znajdź kraj po nazwie"""
        return self.db.query(Country).filter_by(name=name).first()
    
    def get_all(self) -> List[Country]:
        """Pobierz wszystkie kraje"""
        return self.db.query(Country).all()
    
    def create(self, country: Country) -> Country:
        """Utwórz nowy kraj"""
        self.db.add(country)
        self.db.flush()
        return country
    
    def update(self, country: Country) -> Country:
        """Zaktualizuj kraj"""
        self.db.flush()
        return country
    
    def delete(self, country: Country) -> None:
        """Usuń kraj"""
        self.db.delete(country)
