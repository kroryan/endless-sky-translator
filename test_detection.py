#!/usr/bin/env python3
"""
Script de prueba para verificar detección de archivos
"""
import os
from pathlib import Path

def is_file_translatable_test(filepath):
    """Versión de prueba de la función is_file_translatable"""
    filename = filepath.name.lower()
    
    # Lista específica de archivos que NUNCA deben aparecer
    excluded_files = [
        'fleets.txt', 'governments.txt', 'systems.txt', 'planets.txt',
        'map systems.txt', 'commodities.txt', 'persons.txt',
        'effects.txt', 'hazards.txt', 'formations.txt', 'stars.txt', 'series.txt',
        'derelicts.txt', 'minables.txt', 'start.txt', 'wormhole.txt', 'starts.txt',
        'globals.txt', 'gamerules.txt', 'harvesting.txt', 'categories.txt',
        'map beyond patir.txt'
    ]
    
    if filename in excluded_files:
        return False
    
    # Patrones que NUNCA deben aparecer (pero no 'variant' porque algunos archivos variant son útiles)
    excluded_patterns = ['derelict', 'formation', 'hazard', 'fleet', 'government', 'system', 'rating', 'swizzle']
    if any(pattern in filename for pattern in excluded_patterns):
        # Excepción: si contiene ship, outfit, weapon, engine sí queremos incluirlo
        equipment_exceptions = ['ship', 'outfit', 'weapon', 'engine', 'power']
        if not any(eq in filename for eq in equipment_exceptions):
            return False
    
    # Archivos que SÍ queremos mostrar (contenido seguro)
    safe_patterns = ['mission', 'conversation', 'dialog', 'hail', 'job', 'news', 'event', 'campaign', 'culture', 'intro', 'side']
    if any(pattern in filename for pattern in safe_patterns):
        return True
    
    # Archivos de equipamiento que SÍ queremos (contienen descripciones traducibles)
    equipment_patterns = ['ship', 'outfit', 'weapon', 'engine', 'power']
    if any(pattern in filename for pattern in equipment_patterns):
        return True
    
    # Archivos raíz permitidos
    root_files = ['map planets.txt', 'dialog phrases.txt']
    if filename in root_files:
        return True
    
    # Archivos UI permitidos
    ui_patterns = ['interface', 'tooltip', 'help', 'landing', 'flight']
    if any(pattern in filename for pattern in ui_patterns):
        return True
    
    # Archivos específicos de facciones que también queremos
    faction_patterns = ['sales', 'boarding', 'marauder', 'kestrel', 'name', 'critter', 'elenchus', 'nanobots', 'windjammer', 'indigenous', 'archaeology', 'tace mesa']
    if any(pattern in filename for pattern in faction_patterns):
        return True
    
    # Archivos que terminan en números seguidos de palabras (ej: "hai reveal 1 intro.txt")
    import re
    if re.search(r'\d+\s+\w+\.txt$', filename):
        return True
    
    # Archivos con nombres de facciones específicas
    faction_names = ['hai', 'korath', 'wanderer', 'remnant', 'pug', 'quarg', 'coalition', 'avgi', 'bunrodea', 'drak', 'gegno', 'iije', 'incipias', 'kahet', 'rulei', 'sheragi', 'successor', 'vyrmeid', 'aberrant', 'unfettered', 'heliarch', 'lunarium']
    if any(faction in filename for faction in faction_names):
        return True
    
    return False

def test_detection():
    """Probar la detección de archivos"""
    base_path = Path(r"d:\Program Files (x86)\Steam\steamapps\common\Endless Sky\data")
    
    ship_outfit_files = []
    
    # Buscar todos los archivos con ship, outfit, weapon, engine en el nombre
    for folder_path in base_path.iterdir():
        if folder_path.is_dir() and not folder_path.name.startswith('.'):
            for file_path in folder_path.glob("*.txt"):
                filename = file_path.name.lower()
                if any(pattern in filename for pattern in ['ship', 'outfit', 'weapon', 'engine', 'power']):
                    translatable = is_file_translatable_test(file_path)
                    ship_outfit_files.append((str(file_path), translatable))
    
    print("=== ARCHIVOS DE SHIPS/OUTFITS/WEAPONS/ENGINES ===")
    for file_path, translatable in sorted(ship_outfit_files):
        status = "✅ SÍ" if translatable else "❌ NO"
        print(f"{status} - {file_path}")
    
    print(f"\nTotal encontrados: {len(ship_outfit_files)}")
    print(f"Detectados como traducibles: {sum(1 for _, t in ship_outfit_files if t)}")

if __name__ == "__main__":
    test_detection()
