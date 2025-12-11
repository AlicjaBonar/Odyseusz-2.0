# app/mock_data.py
import random

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
    "login": "jan.kowalski", 
    "password": "mock",
    "email": "jan@example.com",
    "phone": "123456789"
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