import requests

#ID miasta do ewakuacji
CITY_ID = 1

URL = 'http://127.0.0.1:5000/evacuations'

payload = {
    "city_id": CITY_ID,
    "action_name": "Protesty społeczne",
    "description": "UWAGA: Zamieszki w centrum Paryża. Unikaj okolic Wieży Eiffla!"
}

print(f"--- Wysyłanie alarmu dla miasta ID: {CITY_ID} ---")

try:
    # Wysyłamy żądanie POST (tak jakby admin kliknął przycisk w formularzu)
    response = requests.post(URL, json=payload)

    if response.status_code == 201:
        print("SUKCES! Serwer odpowiedział:")
        print(response.json())
        print("\nTeraz zaloguj się jako Anna (login: anna, hasło: test) i sprawdź powiadomienia.")
    else:
        print("BŁĄD. Serwer odpowiedział:")
        print(response.status_code)
        print(response.text)

except Exception as e:
    print("Nie udało się połączyć z serwerem.")
    print(f"Błąd: {e}")
    print("Upewnij się, że plik run.py jest uruchomiony w drugim oknie!")