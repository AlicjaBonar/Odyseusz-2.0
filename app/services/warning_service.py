import xml.etree.ElementTree as ET
from datetime import datetime
from app.repositories.warning_repository import warning_repo
from app.models import ThreatLevel

class WarningService:
    def run_import_cycle(self, xml_path):
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
        except Exception as e:
            print(f"Błąd krytyczny pliku: {e}")
            return False

        for item in root.findall('warning'):
            id_tag = item.find('idZewnetrzne')
            nazwa_tag = item.find('nazwa')
            
            # Jeśli nie ma kluczowych pól, pomiń ten element 
            if id_tag is None or nazwa_tag is None:
                print("Pominięto element: Brak idZewnetrzne lub nazwy w XML")
                continue

            ext_id = id_tag.text
            
            # Mapowanie XML 
            warning_data = {
                "external_id": ext_id,
                "name": nazwa_tag.text,
                "content": item.find('tresc').text if item.find('tresc') is not None else "",
                "warning_type": item.find('typ').text if item.find('typ') is not None else "Inne",
                "threat_level": ThreatLevel[item.find('poziomZagrozenia').text] if item.find('poziomZagrozenia') is not None else ThreatLevel.LOW,
                "expiry_date": datetime.strptime(item.find('dataWaznosci').text, '%Y-%m-%d')
            }

            existing = warning_repo.find_by_external_id(ext_id)
            
            if existing is None:
                warning_repo.add(warning_data)
                print(f"Dodano nowe ostrzeżenie: {ext_id}")
            else:
                if existing.name != warning_data["name"] or existing.content != warning_data["content"]:
                    warning_repo.update(ext_id, warning_data)
                    print(f"Zaktualizowano ostrzeżenie: {ext_id}")
        
        return True