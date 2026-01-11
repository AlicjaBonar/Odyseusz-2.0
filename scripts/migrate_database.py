"""
Uniwersalny skrypt migracji bazy danych
Dodaje brakujące kolumny do istniejących tabel
"""
import sqlite3
import os

DATABASE_NAME = "Database"


def migrate_database():
    """Wykonuje migracje bazy danych"""
    db_path = f"{DATABASE_NAME}.db"
    
    if not os.path.exists(db_path):
        print(f"Baza danych {db_path} nie istnieje. Uruchom najpierw create_database.py")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    migrations_applied = []
    
    try:
        # Sprawdź istniejące kolumny
        cursor.execute("PRAGMA table_info(travelers)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Migracja 1: Dodaj kolumny preferencji jeśli nie istnieją
        if 'pref_sms' not in columns:
            print("Migracja 1: Dodawanie kolumn preferencji...")
            cursor.execute("ALTER TABLE travelers ADD COLUMN pref_sms INTEGER DEFAULT 0")
            cursor.execute("ALTER TABLE travelers ADD COLUMN pref_email INTEGER DEFAULT 0")
            cursor.execute("ALTER TABLE travelers ADD COLUMN pref_push INTEGER DEFAULT 1")
            migrations_applied.append("preferences_columns")
            print("   ✅ Kolumny preferencji dodane")
        else:
            print("   ⏭️  Kolumny preferencji już istnieją")
        
        conn.commit()
        
        if migrations_applied:
            print(f"\n✅ Zastosowano {len(migrations_applied)} migracji:")
            for migration in migrations_applied:
                print(f"   - {migration}")
        else:
            print("\n✅ Baza danych jest aktualna - brak migracji do wykonania")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Błąd podczas migracji: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 50)
    print("Migracja bazy danych")
    print("=" * 50)
    migrate_database()
