from datetime import datetime, timedelta
from app import create_app
from app.database.database import SessionLocal
from app.models import Country, City, Location, Traveler, Trip, Stage
from werkzeug.security import generate_password_hash

app = create_app()


def setup_real_data():
    session = SessionLocal()
    try:
        print("--- Rozpoczynam tworzenie danych: Anna Nowak w Paryżu ---")

        # 1. Tworzenie Kraju: Francja
        country = session.query(Country).filter_by(name="Francja").first()
        if not country:
            country = Country(name="Francja")
            session.add(country)
            session.commit()
            print(f"[OK] Dodano kraj: Francja (ID: {country.id})")
        else:
            print(f"[INFO] Francja już istnieje (ID: {country.id})")

        # 2. Tworzenie Miasta: Paryż
        city = session.query(City).filter_by(name="Paryż").first()
        if not city:
            city = City(name="Paryż", country_id=country.id)
            session.add(city)
            session.commit()
            print(f"[OK] Dodano miasto: Paryż (ID: {city.id})")
        else:
            print(f"[INFO] Paryż już istnieje (ID: {city.id})")

        # 3. Tworzenie Lokalizacji: Hotel Ritz
        location = session.query(Location).filter_by(address="Place Vendôme 15, Paryż").first()
        if not location:
            location = Location(address="Place Vendôme 15, Paryż", city_id=city.id)
            session.add(location)
            session.commit()

        # 4. Tworzenie Podróżnej: Anna Nowak
        pesel = "90010112345"
        traveler = session.query(Traveler).filter_by(pesel=pesel).first()
        if not traveler:
            traveler = Traveler(
                pesel=pesel,
                first_name="Anna",
                last_name="Nowak",
                login="anna",  # LOGIN
                password_hash=generate_password_hash("test"),  # HASŁO
                email="anna.nowak@example.com",
                age=30
            )
            session.add(traveler)
            session.commit()
            print(f"[OK] Utworzono podróżną: Anna Nowak")
        else:
            print(f"[INFO] Anna Nowak już istnieje w bazie.")

        # 5. Tworzenie Wycieczki i Etapu (tak, aby była tam TERAZ)
        now = datetime.now()
        start_date = now - timedelta(days=2)  # Przyjechała przedwczoraj
        end_date = now + timedelta(days=5)  # Wyjeżdża za 5 dni

        # Sprawdzamy czy ta wycieczka już jest, żeby nie dublować
        existing_trip = session.query(Trip).filter_by(traveler_pesel=pesel, status="IN_PTOGRESS").first()

        if not existing_trip:
            trip = Trip(status="IN_PROGRESS", traveler_pesel=pesel)
            session.add(trip)
            session.commit()

            stage = Stage(
                trip_id=trip.id,
                location_id=location.id,  # Paryż
                start_date=start_date,
                end_date=end_date
            )
            session.add(stage)
            session.commit()
            print(f"[OK] Utworzono podróż do Paryża (aktywna w tej chwili!)")
        else:
            print("[INFO] Anna Nowak ma już zaplanowaną podróż.")

        print("\n--- GOTOWE! DANE ZAŁADOWANE ---")
        print(f"ID MIESTA DO ATAKU (Paryż): {city.id}")  # To ID jest ważne dla skryptu alarmu!
        print(f"Dane logowania -> Login: 'anna', Hasło: 'test'")

    except Exception as e:
        print(f"Błąd: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    setup_real_data()