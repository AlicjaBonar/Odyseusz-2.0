from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database.database import Base  # Importujemy Base


class Country(Base):
    __tablename__ = "countries"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    consulates = relationship("Consulate", back_populates="country")
    cities = relationship("City", back_populates="country")

class Consulate(Base):
    __tablename__ = "consulates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    country_id = Column(Integer, ForeignKey("countries.id"))

    country = relationship("Country", back_populates="consulates")
    employees = relationship("Employee", back_populates="consulate")

class Employee(Base):
    __tablename__ = "employees"
    pesel = Column(String, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    age = Column(Integer)
    phone_number = Column(String, unique=True)
    email = Column(String, unique=True, index=True)
    passport_number = Column(String, unique=True)
    id_card_number = Column(String, unique=True)
    role = Column(String, nullable=False)
    login = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    consulate_id = Column(Integer, ForeignKey("consulates.id"))

    consulate = relationship("Consulate", back_populates="employees")

class City(Base):
    __tablename__ = "cities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    country_id = Column(Integer, ForeignKey("countries.id"))

    # Relationships
    country = relationship("Country", back_populates="cities")
    locations = relationship("Location", back_populates="city")
    evacuation_areas = relationship("EvacuationArea", back_populates="city")

class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, nullable=False)

    city_id = Column(Integer, ForeignKey("cities.id"))

    # Relationships
    city = relationship("City", back_populates="locations")
    stages = relationship("Stage", back_populates="location")

class Traveler(Base):
    __tablename__ = "travelers"
    pesel = Column(String, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    age = Column(Integer)
    phone_number = Column(String, unique=True)
    email = Column(String, unique=True, index=True)
    passport_number = Column(String, unique=True)
    id_card_number = Column(String, unique=True)
    login = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    trips = relationship("Trip", back_populates="traveler")

class Evacuation(Base):
    __tablename__ = "evacuations"
    id = Column(Integer, primary_key=True, index=True)
    action_name = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    event_description = Column(String)

    trips = relationship("Trip", back_populates="evacuation")
    evacuation_areas = relationship("EvacuationArea", back_populates="evacuation")

class EvacuationArea(Base):
    __tablename__ = "evacuation_areas"
    id = Column(Integer, primary_key=True, index=True)

    evacuation_id = Column(Integer, ForeignKey("evacuations.id"))
    city_id = Column(Integer, ForeignKey("cities.id"))

    evacuation = relationship("Evacuation", back_populates="evacuation_areas")
    city = relationship("City", back_populates="evacuation_areas")

class Trip(Base):
    __tablename__ = "trips"
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String)

    traveler_pesel = Column(String, ForeignKey("travelers.pesel"))
    evacuation_id = Column(Integer, ForeignKey("evacuations.id"), nullable=True)

    traveler = relationship("Traveler", back_populates="trips")
    evacuation = relationship("Evacuation", back_populates="trips")
    stages = relationship("Stage", back_populates="trip")

class Stage(Base):
    __tablename__ = "stages"
    id = Column(Integer, primary_key=True, index=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

    trip_id = Column(Integer, ForeignKey("trips.id"))
    location_id = Column(Integer, ForeignKey("locations.id"))

    trip = relationship("Trip", back_populates="stages")
    location = relationship("Location", back_populates="stages")