"""
Service dla Country i City - logika biznesowa
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Dict, Optional, List
from app.models import Country, City
from app.repositories.country_repository import CountryRepository
from app.repositories.city_repository import CityRepository


class CountryServiceError(Exception):
    """Wyjątek bazowy dla błędów w CountryService"""
    pass


class CountryAlreadyExistsError(CountryServiceError):
    """Kraj już istnieje"""
    pass


class CountryNotFoundError(CountryServiceError):
    """Kraj nie został znaleziony"""
    pass


class CityServiceError(Exception):
    """Wyjątek bazowy dla błędów w CityService"""
    pass


class CityNotFoundError(CityServiceError):
    """Miasto nie zostało znalezione"""
    pass


class CountryService:
    """Service do zarządzania logiką biznesową krajów"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = CountryRepository(db)
    
    def create_country(self, country_data: Dict) -> Dict:
        """
        Utwórz nowy kraj
        
        Args:
            country_data: Słownik z danymi kraju:
                - name (wymagane)
        
        Returns:
            Dict z danymi utworzonego kraju
        """
        if not country_data or "name" not in country_data:
            raise ValueError("Field 'name' is required")
        
        # Sprawdzenie czy kraj już istnieje
        existing = self.repository.find_by_name(country_data["name"])
        if existing:
            raise CountryAlreadyExistsError("Kraj z tą nazwą już istnieje")
        
        # Utworzenie nowego kraju
        new_country = Country(name=country_data["name"])
        
        try:
            self.repository.create(new_country)
            self.db.commit()
            return {
                "id": new_country.id,
                "name": new_country.name
            }
        except IntegrityError:
            self.db.rollback()
            raise CountryAlreadyExistsError("Kraj z tą nazwą już istnieje")
        except Exception as e:
            self.db.rollback()
            raise CountryServiceError(f"Błąd podczas tworzenia kraju: {str(e)}")
    
    def get_country_by_id(self, country_id: int) -> Optional[Dict]:
        """Pobierz kraj po ID z miastami"""
        country = self.repository.find_by_id(country_id)
        if not country:
            return None
        
        return {
            "id": country.id,
            "name": country.name,
            "cities": [{"id": c.id, "name": c.name} for c in country.cities]
        }
    
    def get_all_countries(self) -> List[Dict]:
        """Pobierz wszystkie kraje z miastami"""
        countries = self.repository.get_all()
        return [
            {
                "id": country.id,
                "name": country.name,
                "cities": [{"id": c.id, "name": c.name} for c in country.cities]
            }
            for country in countries
        ]


class CityService:
    """Service do zarządzania logiką biznesową miast"""
    
    def __init__(self, db: Session):
        self.db = db
        self.city_repository = CityRepository(db)
        self.country_repository = CountryRepository(db)
    
    def create_city(self, city_data: Dict) -> Dict:
        """
        Utwórz nowe miasto
        
        Args:
            city_data: Słownik z danymi miasta:
                - name (wymagane)
                - country_id (wymagane)
        
        Returns:
            Dict z danymi utworzonego miasta
        """
        if not city_data or "name" not in city_data or "country_id" not in city_data:
            raise ValueError("Fields 'name' and 'country_id' are required")
        
        # Sprawdzenie czy kraj istnieje
        country = self.country_repository.find_by_id(city_data["country_id"])
        if not country:
            raise CountryNotFoundError("Kraj nie został znaleziony")
        
        # Utworzenie nowego miasta
        new_city = City(name=city_data["name"], country=country)
        
        try:
            self.city_repository.create(new_city)
            self.db.commit()
            return {
                "id": new_city.id,
                "name": new_city.name,
                "country_id": new_city.country_id
            }
        except Exception as e:
            self.db.rollback()
            raise CityServiceError(f"Błąd podczas tworzenia miasta: {str(e)}")
    
    def get_all_cities(self) -> List[Dict]:
        """Pobierz wszystkie miasta"""
        cities = self.city_repository.get_all()
        return [
            {
                "id": city.id,
                "name": city.name,
                "country_id": city.country_id
            }
            for city in cities
        ]
