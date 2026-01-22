from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Optional, List
from app.models import Trip, Traveler, Stage, Location, Companion, TripStatus
from app.repositories.trip_repository import TripRepository
from app.repositories.traveler_repository import TravelerRepository


class TripServiceError(Exception):
    pass


class TripNotFoundError(TripServiceError):
    pass


class TravelerNotFoundError(TripServiceError):
    pass


class TripService:
    
    def __init__(self, db: Session):
        self.db = db
        self.trip_repository = TripRepository(db)
        self.traveler_repository = TravelerRepository(db)
    
    def create_trip(self, trip_data: Dict) -> Dict:
        required_fields = ["status", "traveler_pesel"]
        missing_fields = [field for field in required_fields if field not in trip_data]
        if missing_fields:
            raise ValueError(f"Brakujące pola: {missing_fields}")
        
        # Walidacja statusu
        try:
            status_enum = TripStatus(trip_data["status"])
        except ValueError:
            raise ValueError(f"Nieprawidłowy status. Musi być jednym z: {[s.value for s in TripStatus]}")
        
        # Sprawdzenie czy podróżny istnieje
        traveler = self.traveler_repository.find_by_pesel(trip_data["traveler_pesel"])
        if not traveler:
            raise TravelerNotFoundError("Podróżny nie został znaleziony")
        
        # Utworzenie podróży
        trip = Trip(
            status=status_enum,
            traveler=traveler
        )
        # Zakładam, że repozytorium dodaje obiekt do sesji (self.db.add(trip))
        self.trip_repository.create(trip)
        
        # Aby mieć trip.id do powiązania etapów, jeśli repozytorium tego nie robi automatycznie:
        self.db.flush() 

        # Dodanie etapów
        stages_data = trip_data.get("stages", [])
        for stage_data in stages_data:
            try:
                start_date = datetime.fromisoformat(stage_data["start_date"])
                end_date = datetime.fromisoformat(stage_data["end_date"])
                
                # NOWA LOGIKA: Pobieramy city_id i address zamiast location_id
                city_id = stage_data.get("city_id")
                address = stage_data.get("address")
                
                if not city_id or not address:
                    continue # Lub rzuć błędem walidacji

                # 1. Szukamy czy taka lokalizacja już istnieje w tym mieście
                location = self.db.query(Location).filter_by(
                    city_id=city_id, 
                    address=address
                ).first()

                # 2. Jeśli nie istnieje, tworzymy nową
                if not location:
                    location = Location(
                        address=address,
                        city_id=city_id
                    )
                    self.db.add(location)
                    self.db.flush()  # Pobieramy ID nowej lokalizacji przed utworzeniem etapu

                # 3. Tworzymy etap korzystając z id (istniejącego lub nowo utworzonego)
                stage = Stage(
                    start_date=start_date,
                    end_date=end_date,
                    trip_id=trip.id,
                    location_id=location.id
                )
                self.db.add(stage)

            except (KeyError, ValueError) as e:
                # Tutaj warto byłoby logować błąd parsowania daty
                continue
        
        # Dodanie companionów (bez zmian)
        companion_ids = trip_data.get("companions", [])
        for companion_id in companion_ids:
            companion = self.db.query(Companion).filter_by(id=companion_id).first()
            if companion:
                trip.companions.append(companion)
        
        try:
            self.db.commit()
            self.db.refresh(trip)
        except Exception as e:
            self.db.rollback()
            raise TripServiceError(f"Błąd zapisu podróży: {str(e)}")
        
        return self._trip_to_dict(trip)
    
    def get_trip_by_id(self, trip_id: int) -> Optional[Dict]:
        trip = self.trip_repository.find_by_id(trip_id)
        if not trip:
            return None
        return self._trip_to_dict(trip)
    
    def get_all_trips(self) -> List[Dict]:
        trips = self.trip_repository.get_all()
        return [self._trip_to_dict(trip) for trip in trips]
    
    def get_trips_by_traveler_pesel(self, traveler_pesel: str) -> Dict:
        traveler = self.traveler_repository.find_by_pesel(traveler_pesel)
        if not traveler:
            raise TravelerNotFoundError("Podróżny nie został znaleziony")
        
        trips = self.trip_repository.find_by_traveler_pesel(traveler_pesel)
        return {
            "traveler_pesel": traveler_pesel,
            "trips": [self._trip_to_dict(trip) for trip in trips]
        }
    
    def update_trip(self, trip_id: int, trip_data: Dict) -> Dict:
        trip = self.trip_repository.find_by_id(trip_id)
        if not trip:
            raise TripNotFoundError("Podróż nie została znaleziona")
        
        if "status" in trip_data:
            try:
                trip.status = TripStatus(trip_data["status"])
            except ValueError:
                raise ValueError(f"Nieprawidłowy status. Musi być jednym z: {[s.value for s in TripStatus]}")
        
        if "traveler_pesel" in trip_data:
            traveler = self.traveler_repository.find_by_pesel(trip_data["traveler_pesel"])
            if not traveler:
                raise TravelerNotFoundError("Podróżny nie został znaleziony")
            trip.traveler_pesel = trip_data["traveler_pesel"]
        
        if "evacuation_id" in trip_data:
            evacuation_id = trip_data["evacuation_id"]
            if evacuation_id:
                from app.models import Evacuation
                evacuation = self.db.query(Evacuation).filter_by(id=evacuation_id).first()
                if not evacuation:
                    raise TripServiceError("Ewakuacja nie została znaleziona")
                trip.evacuation_id = evacuation_id
            else:
                trip.evacuation_id = None
        
        self.trip_repository.update(trip)
        self.db.commit()
        self.db.refresh(trip)
        
        return self._trip_to_dict(trip)
    
    def delete_trip(self, trip_id: int) -> None:
        trip = self.trip_repository.find_by_id(trip_id)
        if not trip:
            raise TripNotFoundError("Podróż nie została znaleziona")
        
        self.trip_repository.delete(trip)
        self.db.commit()
    
    def add_companions_to_trip(self, trip_id: int, companions_data: List[Dict], traveler_pesel: str) -> Dict:
        if not companions_data:
            raise ValueError("Brak companionów do dodania")
        
        if not traveler_pesel:
            raise ValueError("Brak traveler_pesel")
        
        # Sprawdzenie czy podróż istnieje
        trip = self.trip_repository.find_by_id(trip_id)
        if not trip:
            raise TripNotFoundError("Podróż nie została znaleziona")
        
        # Sprawdzenie czy podróżny istnieje
        traveler = self.traveler_repository.find_by_pesel(traveler_pesel)
        if not traveler:
            raise TravelerNotFoundError("Podróżny nie został znaleziony")
        
        saved_companions = []
        
        for comp_data in companions_data:
            companion = Companion(
                pesel=comp_data.get("pesel"),
                first_name=comp_data.get("first_name"),
                last_name=comp_data.get("last_name"),
                age=comp_data.get("age"),
                phone_number=comp_data.get("phone_number"),
                email=comp_data.get("email"),
                added_by_pesel=traveler_pesel
            )
            
            self.db.add(companion)
            self.db.flush()  # żeby companion miał ID
            
            trip.companions.append(companion)
            
            saved_companions.append({
                "id": companion.id,
                "first_name": companion.first_name,
                "last_name": companion.last_name
            })
        
        self.db.commit()
        
        return {
            "message": f"Dodano {len(saved_companions)} companionów do podróży",
            "companions": saved_companions
        }
    
    def _trip_to_dict(self, trip: Trip) -> Dict:
        return {
            "id": trip.id,
            "status": trip.status.value,
            "traveler_pesel": trip.traveler_pesel,
            "evacuation_id": trip.evacuation_id,
            "stages": [{
                "id": s.id,
                "start_date": s.start_date.isoformat(),
                "end_date": s.end_date.isoformat(),
                "location_id": s.location_id
            } for s in trip.stages],
            "companions": [{
                "id": c.id,
                "pesel": c.pesel,
                "first_name": c.first_name,
                "last_name": c.last_name
            } for c in trip.companions]
        }
