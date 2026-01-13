# app/mock_data.py
import random
from datetime import datetime


# ============================================================================
# MOCK DANE DLA AUTORYZACJI I UŻYTKOWNIKÓW
# ============================================================================

# --- 1. MOCK ADMINISTRATORA ---
MOCK_ADMIN = {
    "login": "admin",
    "password": "admin",
    "data": {
        "first_name": "Administrator",
        "last_name": "Systemu",
        "pesel": "00000000000",
        "email": "admin@odyseusz.pl",
        "role": "admin", 
        "phone_number": "000000000",
        "age": 30
    }
}

# --- 2. MOCK ISTNIEJĄCEGO OBYWATELA (Jan Kowalski) ---
MOCK_EXISTING_CITIZEN = {
    "pesel": "11111111111",
    "first_name": "Jan",
    "last_name": "Kowalski",
    "email": "jan@example.com",
    "login": "jan.kowalski", 
    "password": "mock",
    "phone_number": "123456789",
    "age": "40"
}

# --- 3. GENERATOR NOWEGO OBYWATELA (Losowa Anna Nowak) ---
def get_new_mock_citizen():
    """Zwraca dane dla 'nowego' użytkownika z Węzła Krajowego"""
    # Generujemy losowy PESEL, żeby za każdym razem system myślał, że to ktoś nowy
    random_pesel = str(random.randint(10000000000, 99999999999))
    
    return {
        "first_name": "Anna",
        "last_name": "Nowak",
        "pesel": random_pesel,
        "source": "mobywatel" # Flaga, że przyszło z węzła
    }


# ============================================================================
# MOCK DANE DLA EWAKUACJI
# ============================================================================

def get_mock_evacuations():
    """
    Zwraca mockowane ewakuacje (używane jako fallback gdy baza jest pusta)
    
    Returns:
        Lista obiektów Evacuation (mock)
    """
    class Evacuation:
        def __init__(self, id, action_name, event_description, start_date, end_date, status, country_id=None, city_id=None):
            self.id = id
            self.action_name = action_name
            self.event_description = event_description
            self.start_date = start_date
            self.end_date = end_date
            self.status = status
            self.country_id = country_id
            self.city_id = city_id
    
    return [
        Evacuation(
            id=1,
            action_name="Ewakuacja Portugalia",
            event_description="Zagrożenie pożarowe – południe kraju",
            start_date=datetime(2025, 1, 10, 12, 0),
            end_date=None,
            status="IN_PROGRESS",
            country_id=2,
            city_id=None
        ),
        Evacuation(
            id=2,
            action_name="Ewakuacja Barcelona",
            event_description="Silne burze i ryzyko powodzi",
            start_date=datetime(2024, 12, 5, 8, 0),
            end_date=datetime(2024, 12, 6, 20, 0),
            status="COMPLETED",
            country_id=None,
            city_id=5
        )
    ]


# ============================================================================
# MOCK DANE DLA KRAJÓW I MIAST
# ============================================================================

def get_mock_countries():
    """
    Zwraca mockowane kraje (używane jako fallback gdy baza jest pusta)
    
    Returns:
        Lista obiektów Country (mock)
    """
    class Country:
        def __init__(self, id, name):
            self.id = id
            self.name = name
    
    return [
        Country(id=1, name="Hiszpania"),
        Country(id=2, name="Portugalia"),
        Country(id=3, name="Włochy")
    ]


def get_mock_cities():
    """
    Zwraca mockowane miasta (używane jako fallback gdy baza jest pusta)
    
    Returns:
        Lista obiektów City (mock)
    """
    class Country:
        def __init__(self, id, name):
            self.id = id
            self.name = name
    
    class City:
        def __init__(self, id, name, country):
            self.id = id
            self.name = name
            self.country = country
    
    return [
        City(id=1, name="Paryż", country=Country(id=1, name="Francja")),
        City(id=2, name="Madryt", country=Country(id=2, name="Hiszpania")),
        City(id=3, name="Barcelona", country=Country(id=2, name="Hiszpania"))
    ]