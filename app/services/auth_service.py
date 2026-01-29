from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash
from typing import Dict, Optional, Tuple
from app.models import Traveler, Employee
from app.repositories.traveler_repository import TravelerRepository
from app.repositories.employee_repository import EmployeeRepository
from app.mock_data import MOCK_ADMIN, MOCK_EXISTING_CITIZEN, get_new_mock_citizen


class AuthServiceError(Exception):
    pass


class InvalidCredentialsError(AuthServiceError):
    pass


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.traveler_repository = TravelerRepository(db)
        self.employee_repository = EmployeeRepository(db)
    
    def login(self, login: str, password: str) -> Tuple[object, str]:
        if not login or not password:
            raise ValueError("Brak loginu lub hasła")
        
        # 1. Sprawdzamy podróżnego
        user = self.traveler_repository.find_by_login(login)
        role = "traveler"
        
        # 2. Jeśli nie znaleziono podróżnego, sprawdzamy pracownika
        if not user:
            role = "employee"
            
            # SPECIAL CASE: MOCK ADMIN
            if login == MOCK_ADMIN["login"] and password == MOCK_ADMIN["password"]:
                user = self.employee_repository.find_by_login(MOCK_ADMIN["login"])
                
                if not user:
                    # Utwórz mock admina jeśli nie istnieje
                    user = Employee(
                        login=MOCK_ADMIN["login"],
                        password_hash=generate_password_hash(MOCK_ADMIN["password"]),
                        **MOCK_ADMIN["data"]
                    )
                    self.employee_repository.create(user)
                    self.db.commit()
                    self.db.refresh(user)
            else:
                user = self.employee_repository.find_by_login(login)
        
        # 3. Weryfikacja hasła
        if not user or not check_password_hash(user.password_hash, password):
            raise InvalidCredentialsError("Niepoprawne dane logowania")
        
        return user, role
    
    def mobywatel_callback(self, scenario: str) -> Tuple[Optional[Dict], Optional[object]]:
        if scenario == "existing":
            # SCENARIUSZ 1: Użytkownik już istnieje (Jan Kowalski)
            mock_data = MOCK_EXISTING_CITIZEN
            user = self.traveler_repository.find_by_pesel(mock_data["pesel"])
            
            if not user:
                # Utwórz użytkownika jeśli nie istnieje
                user = Traveler(
                    login=mock_data["login"],
                    password_hash=generate_password_hash(mock_data["password"]),
                    first_name=mock_data["first_name"],
                    last_name=mock_data["last_name"],
                    pesel=mock_data["pesel"],
                    email=mock_data["email"],
                    phone_number=mock_data["phone_number"]
                )
                self.traveler_repository.create(user)
                self.db.commit()
                self.db.refresh(user)
            
            return None, user
        
        elif scenario == "new":
            # SCENARIUSZ 2: Nowy użytkownik (Anna Nowak + losowy PESEL)
            mock_identity = get_new_mock_citizen()
            return mock_identity, None
        
        return None, None
    
    def complete_profile(self, identity: Dict, email: str, phone_number: str) -> object:
        if not identity:
            raise ValueError("Brak danych tożsamości")
        
        new_traveler = Traveler(
            login=f"mobywatel_{identity['pesel']}",
            password_hash=generate_password_hash("mobywatel_auth"),
            first_name=identity['first_name'],
            last_name=identity['last_name'],
            pesel=identity['pesel'],
            email=email,
            phone_number=phone_number
        )
        
        self.traveler_repository.create(new_traveler)
        self.db.commit()
        self.db.refresh(new_traveler)
        
        return new_traveler
