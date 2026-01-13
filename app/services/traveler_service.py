from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from app.models import Traveler
from app.repositories.traveler_repository import TravelerRepository
from typing import Dict, Optional, List


class TravelerServiceError(Exception):
    pass


class TravelerNotFoundError(TravelerServiceError):
    pass


class TravelerAlreadyExistsError(TravelerServiceError):
    pass


class TravelerService:
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = TravelerRepository(db)
    
    def create_traveler(self, traveler_data: Dict) -> Dict:
        # Walidacja wymaganych pól
        required_fields = ["pesel", "first_name", "last_name", "email", "login", "password"]
        missing_fields = [field for field in required_fields if field not in traveler_data]
        if missing_fields:
            raise ValueError(f"Brakujące pola: {missing_fields}")
        
        # Sprawdzenie czy podróżny już istnieje
        if self.repository.find_by_pesel(traveler_data["pesel"]):
            raise TravelerAlreadyExistsError("Podróżny z tym numerem PESEL już istnieje")
        
        if self.repository.find_by_login(traveler_data["login"]):
            raise TravelerAlreadyExistsError("Podróżny z tym loginem już istnieje")
        
        # Utworzenie nowego podróżnego
        hashed_password = generate_password_hash(traveler_data["password"])
        new_traveler = Traveler(
            pesel=traveler_data["pesel"],
            first_name=traveler_data["first_name"],
            last_name=traveler_data["last_name"],
            email=traveler_data["email"],
            login=traveler_data["login"],
            password_hash=hashed_password,
            age=traveler_data.get("age"),
            phone_number=traveler_data.get("phone_number"),
            passport_number=traveler_data.get("passport_number"),
            id_card_number=traveler_data.get("id_card_number")
        )
        
        try:
            self.repository.create(new_traveler)
            self.db.commit()
            return {
                "pesel": new_traveler.pesel,
                "email": new_traveler.email,
                "login": new_traveler.login
            }
        except IntegrityError:
            self.db.rollback()
            raise TravelerAlreadyExistsError("Podróżny z tym numerem PESEL lub loginem już istnieje")
        except Exception as e:
            self.db.rollback()
            raise TravelerServiceError(f"Błąd podczas tworzenia podróżnego: {str(e)}")
    
    def get_traveler_by_pesel(self, pesel: str) -> Optional[Traveler]:
        return self.repository.find_by_pesel(pesel)
    
    def get_traveler_by_login(self, login: str) -> Optional[Traveler]:
        return self.repository.find_by_login(login)
    
    def get_all_travelers(self) -> List[Dict]:
        travelers = self.repository.get_all()
        return [
            {
                "pesel": t.pesel,
                "first_name": t.first_name,
                "last_name": t.last_name,
                "email": t.email,
                "login": t.login,
                "age": t.age
            }
            for t in travelers
        ]
