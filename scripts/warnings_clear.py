import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import SessionLocal
from app.models import ConsularWarning, warning_location_association

def clear_consular_data():
    session = SessionLocal()
    try:
        print("Rozpoczynanie czyszczenia danych ostrzeżeń...")
        
        session.execute(warning_location_association.delete())
        
        num_deleted = session.query(ConsularWarning).delete()
        
        session.commit()
        print(f"Sukces! Usunięto {num_deleted} ostrzeżeń z bazy danych.")
        print("Teraz Twoja lista w aplikacji powinna być pusta.")
        
    except Exception as e:
        session.rollback()
        print(f"Wystąpił błąd podczas czyszczenia: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    clear_consular_data()