# reset_db.py
from app.database.database import engine, Base
from app.models import *

def reset_database():
    print("Usuwanie wszystkich tabel...")
    Base.metadata.drop_all(bind=engine)
    
    print("Tworzenie tabel na nowo...")
    Base.metadata.create_all(bind=engine)
    
    print("Baza danych została wyczyszczona i jest gotowa do pracy.")

if __name__ == "__main__":
    # Pytanie bezpieczeństwa, żeby nie kliknąć przez przypadek
    confirm = input("Czy na pewno chcesz wyczyścić CAŁĄ bazę danych? (t/n): ")
    if confirm.lower() == 't':
        reset_database()
    else:
        print("Anulowano.")