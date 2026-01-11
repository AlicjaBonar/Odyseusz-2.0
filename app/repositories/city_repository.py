"""
Repository dla City - operacje na bazie danych
"""
from sqlalchemy.orm import Session
from app.models import City, Country
from typing import Optional, List


class CityRepository:
    """Repository do zarządzania City w bazie danych"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, city_id: int) -> Optional[City]:
        """Znajdź miasto po ID"""
        return self.db.query(City).filter_by(id=city_id).first()
    
    def find_by_name(self, name: str) -> Optional[City]:
        """Znajdź miasto po nazwie"""
        return self.db.query(City).filter_by(name=name).first()
    
    def find_by_country_id(self, country_id: int) -> List[City]:
        """Znajdź wszystkie miasta w kraju"""
        return self.db.query(City).filter_by(country_id=country_id).all()
    
    def get_all(self) -> List[City]:
        """Pobierz wszystkie miasta"""
        return self.db.query(City).all()
    
    def create(self, city: City) -> City:
        """Utwórz nowe miasto"""
        self.db.add(city)
        self.db.flush()
        return city
    
    def update(self, city: City) -> City:
        """Zaktualizuj miasto"""
        self.db.flush()
        return city
    
    def delete(self, city: City) -> None:
        """Usuń miasto"""
        self.db.delete(city)
