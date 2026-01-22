from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.database.database import Base  # Importujemy Base
from sqlalchemy import Boolean, Table
from datetime import datetime
from enum import Enum as PyEnum
from flask_login import UserMixin
import random

class TripStatus(PyEnum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELED = "canceled"


class EvacuationStatus(PyEnum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELED = "canceled"


trip_companion_association = Table(
    "trip_companion",
    Base.metadata,
    Column("trip_id", Integer, ForeignKey("trips.id"), primary_key=True),
    Column("companion_id", Integer, ForeignKey("companions.id"), primary_key=True)
)

class Country(Base):
    __tablename__ = "countries"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    consulates = relationship("Consulate", back_populates="country")
    cities = relationship("City", back_populates="country")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }

class Consulate(Base):
    __tablename__ = "consulates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    country_id = Column(Integer, ForeignKey("countries.id"))

    country = relationship("Country", back_populates="consulates")
    employees = relationship("Employee", back_populates="consulate")

class Employee(UserMixin, Base):
    __tablename__ = "employees"
    pesel = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    age = Column(Integer)
    phone_number = Column(String, unique=True)
    email = Column(String, unique=True, index=True)
    passport_number = Column(String, unique=True)
    id_card_number = Column(String, unique=True)
    role = Column(String, nullable=False)
    login = Column(String, primary_key=True)
    password_hash = Column(String, nullable=False)

    consulate_id = Column(Integer, ForeignKey("consulates.id"))

    consulate = relationship("Consulate", back_populates="employees")

    def get_id(self):
        return self.login

class City(Base):
    __tablename__ = "cities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    country_id = Column(Integer, ForeignKey("countries.id"))

    # Relationships
    country = relationship("Country", back_populates="cities")
    locations = relationship("Location", back_populates="city")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "country_id": self.country_id
        }

class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, nullable=False)

    city_id = Column(Integer, ForeignKey("cities.id"))

    # Relationships
    city = relationship("City", back_populates="locations")
    stages = relationship("Stage", back_populates="location")

class Companion(Base):
    __tablename__ = 'companions'
    id = Column(Integer, primary_key=True, index=True)
    pesel = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    age = Column(Integer)
    phone_number = Column(String)
    email = Column(String)
    passport_number = Column(String)
    id_card_number = Column(String)

    added_by_pesel = Column(String, ForeignKey('travelers.pesel'), nullable=False)
    added_by_traveler = relationship("Traveler", back_populates="companions")

    trips = relationship(
        "Trip",
        secondary=trip_companion_association,
        back_populates="companions"
    )

class Traveler(UserMixin, Base):
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
    pref_sms = Column(Boolean, default=False)
    pref_email = Column(Boolean, default=False)
    pref_push = Column(Boolean, default=True)

    trips = relationship("Trip", back_populates="traveler")
    companions = relationship("Companion", back_populates="added_by_traveler")

    def get_id(self):
        return self.pesel

class Evacuation(Base):
    __tablename__ = "evacuations"
    id = Column(Integer, primary_key=True, index=True)
    action_name = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(Enum(EvacuationStatus), nullable=False, default=EvacuationStatus.PLANNED)
    event_description = Column(String, nullable=True)
    trips = relationship("Trip", back_populates="evacuation")
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=True) # null, jeśli ewakuacja całego kraju

    def to_dict(self):
        return {
            "id": self.id,
            "action_name": self.action_name,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "status": self.status.value,
            "event_description": self.event_description,
            "country_id": self.country_id,
            "city_id": self.city_id
        }

class Trip(Base):
    __tablename__ = "trips"
    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(TripStatus), nullable=False, default=TripStatus.PLANNED)

    traveler_pesel = Column(String, ForeignKey("travelers.pesel"))
    evacuation_id = Column(Integer, ForeignKey("evacuations.id"), nullable=True)

    traveler = relationship("Traveler", back_populates="trips")
    evacuation = relationship("Evacuation", back_populates="trips")
    stages = relationship("Stage", back_populates="trip")

    companions = relationship(
        "Companion",
        secondary=trip_companion_association,
        back_populates="trips"
    )

class Stage(Base):
    __tablename__ = "stages"
    id = Column(Integer, primary_key=True, index=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

    trip_id = Column(Integer, ForeignKey("trips.id"))
    location_id = Column(Integer, ForeignKey("locations.id"))

    trip = relationship("Trip", back_populates="stages")
    location = relationship("Location", back_populates="stages")


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    traveler_pesel = Column(String, ForeignKey("travelers.pesel"))
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    is_read = Column(Boolean, default=False)

    # Relacja
    traveler = relationship("Traveler", backref="notifications")

