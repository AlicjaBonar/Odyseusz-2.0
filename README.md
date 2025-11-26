# **Odyseusz 2.0 --- Projekt studencki (Inżynieria Oprogramowania)**

Odyseusz 2.0 to projekt realizowany w ramach przedmiotu **Inżynieria
Oprogramowania**.\
Celem projektu jest stworzenie ulepszonej, własnej wersji systemu
wspierającego zarządzanie studentami, mobilnością, zgłoszeniami lub
procesami uczelnianymi --- inspirowanej projektem *Odyseusz 2.0*.

Projekt ma charakter edukacyjny i służy doskonaleniu umiejętności w
zakresie:

-   architektury aplikacji,
-   pracy zespołowej,
-   dobrych praktyk programistycznych,
-   dokumentowania i testowania oprogramowania,
-   wykorzystania narzędzi Git / GitHub.

------------------------------------------------------------------------

## 🚀 **Uruchamianie projektu (lokalnie)**

### 1️⃣ Utwórz i aktywuj wirtualne środowisko

``` bash
python -m venv venv
venv\Scripts\activate        # Windows
# lub
source venv/bin/activate    # Linux/macOS
```

### 2️⃣ Zainstaluj wymagane biblioteki

``` bash
pip install -r requirements.txt
```

### 3️⃣ Utwórz bazę danych

``` bash
python create_database.py
```

### 4️⃣ Uruchom aplikację

``` bash
python run.py
```

------------------------------------------------------------------------

## 🧱 **Struktura projektu (przykładowa)**

    ├── app/
    │   ├── models/
    │   ├── routes/
    │   ├── static/
    │   ├── templates/
    │   └── ...
    ├── create_database.py
    ├── run.py
    ├── requirements.txt
    └── README.md

------------------------------------------------------------------------

## 🧪 **Testowanie**

``` bash
pytest
```

------------------------------------------------------------------------

## 📌 **Technologie / stack**

-   Python
-   Flask
-   SQLAlchemy / sqlite3
-   HTML / CSS / JS

------------------------------------------------------------------------

## 👥 **Autorzy (zespół projektowy)**

-   Alicja Bonar
-   Alicja Rembisz
-   Anna Kępowicz

------------------------------------------------------------------------

## 📄 **Licencja / informacje**

Projekt powstał wyłącznie do celów dydaktycznych w ramach zajęć
**Inżynieria Oprogramowania**.
