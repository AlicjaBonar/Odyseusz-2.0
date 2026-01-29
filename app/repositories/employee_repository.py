from sqlalchemy.orm import Session
from app.models import Employee
from typing import Optional, List


class EmployeeRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_id(self, employee_id: int) -> Optional[Employee]:
        return self.db.query(Employee).filter_by(id=employee_id).first()

    def find_by_login(self, login: str) -> Optional[Employee]:
        return self.db.query(Employee).filter_by(login=login).first()
    
    def find_by_pesel(self, pesel: str) -> Optional[Employee]:
        return self.db.query(Employee).filter_by(pesel=pesel).first()
    
    def find_by_email(self, email: str) -> Optional[Employee]:
        return self.db.query(Employee).filter_by(email=email).first()
    
    def get_all(self) -> List[Employee]:
        return self.db.query(Employee).all()
    
    def create(self, employee: Employee) -> Employee:
        self.db.add(employee)
        self.db.flush()
        return employee
    
    def update(self, employee: Employee) -> Employee:
        self.db.flush()
        return employee
    
    def delete(self, employee: Employee) -> None:
        self.db.delete(employee)
