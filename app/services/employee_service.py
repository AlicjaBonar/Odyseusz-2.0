from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from typing import Dict
from app.models import Employee
from app.repositories.employee_repository import EmployeeRepository


class EmployeeServiceError(Exception):
    pass


class EmployeeAlreadyExistsError(EmployeeServiceError):
    pass


class EmployeeService:
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = EmployeeRepository(db)
    
    def create_employee(self, employee_data: Dict) -> Dict:
        required_fields = ["pesel", "first_name", "last_name", "email", "login", 
                          "password", "role", "consulate_id"]
        missing_fields = [field for field in required_fields if field not in employee_data]
        if missing_fields:
            raise ValueError(f"Brakujące pola: {missing_fields}")
        
        # Sprawdzenie czy pracownik już istnieje
        if self.repository.find_by_pesel(employee_data["pesel"]):
            raise EmployeeAlreadyExistsError("Pracownik z tym numerem PESEL już istnieje")
        
        if self.repository.find_by_login(employee_data["login"]):
            raise EmployeeAlreadyExistsError("Pracownik z tym loginem już istnieje")
        
        # Utworzenie nowego pracownika
        hashed_password = generate_password_hash(employee_data["password"])
        new_employee = Employee(
            pesel=employee_data["pesel"],
            first_name=employee_data["first_name"],
            last_name=employee_data["last_name"],
            email=employee_data["email"],
            login=employee_data["login"],
            password_hash=hashed_password,
            role=employee_data["role"],
            consulate_id=employee_data["consulate_id"],
            age=employee_data.get("age"),
            phone_number=employee_data.get("phone_number"),
            passport_number=employee_data.get("passport_number"),
            id_card_number=employee_data.get("id_card_number")
        )
        
        try:
            self.repository.create(new_employee)
            self.db.commit()
            return {
                "pesel": new_employee.pesel,
                "email": new_employee.email,
                "login": new_employee.login,
                "role": new_employee.role,
                "consulate_id": new_employee.consulate_id
            }
        except IntegrityError:
            self.db.rollback()
            raise EmployeeAlreadyExistsError("Pracownik z tym numerem PESEL lub loginem już istnieje")
        except Exception as e:
            self.db.rollback()
            raise EmployeeServiceError(f"Błąd podczas tworzenia pracownika: {str(e)}")
