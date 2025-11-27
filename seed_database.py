from sqlalchemy.orm import Session
from app.database.database import SessionLocal, Base, engine
from app.models import Country, City, Location

# Tworzymy tabele jeśli jeszcze nie istnieją
Base.metadata.create_all(bind=engine)

# Otwieramy sesję
db: Session = SessionLocal()

try:
    # --- KRAJE ---
    poland = Country(name="Polska")
    germany = Country(name="Niemcy")
    france = Country(name="Francja")

    db.add_all([poland, germany, france])
    db.commit()
    db.refresh(poland)
    db.refresh(germany)
    db.refresh(france)

    # --- MIASTA ---
    warsaw = City(name="Warszawa", country=poland)
    krakow = City(name="Kraków", country=poland)
    berlin = City(name="Berlin", country=germany)
    munich = City(name="Monachium", country=germany)
    paris = City(name="Paryż", country=france)
    lyon = City(name="Lyon", country=france)

    db.add_all([warsaw, krakow, berlin, munich, paris, lyon])
    db.commit()
    db.refresh(warsaw)
    db.refresh(berlin)

    # --- LOKALIZACJE ---
    loc1 = Location(address="ul. Marszałkowska 1", city=warsaw)
    loc2 = Location(address="ul. Floriańska 10", city=krakow)
    loc3 = Location(address="Unter den Linden 5", city=berlin)
    loc4 = Location(address="Marienplatz 1", city=munich)
    loc5 = Location(address="Champs-Élysées 50", city=paris)
    loc6 = Location(address="Rue de la République 12", city=lyon)

    db.add_all([loc1, loc2, loc3, loc4, loc5, loc6])
    db.commit()

    print("Dane zostały dodane do bazy!")
except Exception as e:
    db.rollback()
    print("Wystąpił błąd:", e)
finally:
    db.close()