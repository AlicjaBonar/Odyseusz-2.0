# sync_trigger.py
from datetime import datetime
import time
from app.services.warning_service import WarningService

service = WarningService()

def start_polling():
    print("Uruchomiono cykl pobierania (co 15 min)...")
    while True:
        # ZMIANA NAZWY PLIKU XML W RAZIE POTRZEBY
        success = service.run_import_cycle('external_data/warnings_v2.xml')
        print(f"[{datetime.now()}] Import status: {success}")
        time.sleep(900) # 15 minut

if __name__ == "__main__":
    start_polling()