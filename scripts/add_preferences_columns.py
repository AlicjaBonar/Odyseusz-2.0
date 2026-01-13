"""
Skrypt migracji - dodaje kolumny preferencji do tabeli travelers
"""
import sqlite3
import sys
import os

# Nazwa bazy danych (zgodna z app/database/database.py)
DATABASE_NAME = "Database"


def add_preferences_columns():
    """Dodaje kolumny pref_sms, pref_email, pref_push do tabeli travelers"""
    db_path = f"{DATABASE_NAME}.db"
    
    if not os.path.exists(db_path):
        print(f"Baza danych {db_path} nie istnieje. Uruchom najpierw create_database.py")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Sprawdź czy kolumny już istnieją
        cursor.execute("PRAGMA table_info(travelers)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'pref_sms' in columns:
            print("Kolumny preferencji już istnieją w tabeli travelers.")
            return True
        
        # Dodaj kolumny preferencji
        print("Dodawanie kolumn preferencji do tabeli travelers...")
        
        cursor.execute("""
            ALTER TABLE travelers 
            ADD COLUMN pref_sms INTEGER DEFAULT 0
        """)
        
        cursor.execute("""
            ALTER TABLE travelers 
            ADD COLUMN pref_email INTEGER DEFAULT 0
        """)
        
        cursor.execute("""
            ALTER TABLE travelers 
            ADD COLUMN pref_push INTEGER DEFAULT 1
        """)
        
        conn.commit()
        print("✅ Kolumny preferencji zostały dodane pomyślnie!")
        print("   - pref_sms (domyślnie: False)")
        print("   - pref_email (domyślnie: False)")
        print("   - pref_push (domyślnie: True)")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Błąd podczas dodawania kolumn: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 50)
    print("Migracja: Dodawanie kolumn preferencji")
    print("=" * 50)
    
    success = add_preferences_columns()
    
    if success:
        print("\n✅ Migracja zakończona pomyślnie!")
    else:
        print("\n❌ Migracja nie powiodła się.")
        sys.exit(1)
