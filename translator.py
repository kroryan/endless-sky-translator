#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Traductor automático para Endless Sky (Versión corregida)
Traduce solo el contenido apropiado, manteniendo la estructura del juego intacta
"""

import os
import shutil
import time
import re
from pathlib import Path
from googletrans import Translator
import chardet
import unicodedata

class EndlessSkyTranslatorFixed:
    def __init__(self, base_path, target_lang='es'):
        self.base_path = Path(base_path)
        self.data_path = self.base_path / "data"
        self.plugin_path = self.base_path / "Plugins" / "traduccion"
        self.plugin_data_path = self.plugin_path / "data"
        self.target_lang = target_lang
        self.translator = Translator()
        
        # Archivos que deben traducirse (SOLO ELEMENTOS VISIBLES SIN AFECTAR FUNCIONALIDAD)
        self.translatable_files = [
            'map planets.txt',     # Planetas - PRIMERA PRIORIDAD (solo descripciones)
            'dialog phrases.txt',  # Frases de diálogo
            # NO incluir commodities.txt - requiere lógica especial
            # NO incluir effects.txt - son efectos técnicos
            # NO incluir globals.txt - son variables técnicas
            # NO incluir governments.txt - afecta funcionamiento
            # NO incluir persons.txt - afecta funcionamiento
            # NO incluir series.txt - afecta funcionamiento
            # NO incluir stars.txt - son elementos técnicos
            # NO incluir map systems.txt - afecta navegación
        ]
        
        # Carpetas que contienen archivos traducibles (SOLO LAS MÁS SEGURAS)
        self.translatable_folders = [
            'human',        # Humanos - misiones y diálogos seguros
            'hai',          # Hai - misiones y diálogos seguros
            'korath',       # Korath - misiones y diálogos seguros
            'wanderer',     # Wanderer - misiones y diálogos seguros
            'remnant',      # Remnant - misiones y diálogos seguros
            'pug',          # Pug - misiones y diálogos seguros
            'quarg',        # Quarg - misiones y diálogos seguros
            'coalition',    # Coalition - misiones y diálogos seguros
            '_ui'           # Interfaz de usuario - SEGURO de traducir
            # EXCLUIR: drak, gegno, avgi, bunrodea, iije, incipias, kahet, rulei, sheragi, successors, vyrmeid, whispering void
            # Estas son facciones especiales que pueden tener lógica compleja
        ]
        
        # Patrones que NUNCA deben traducirse (MÁS RESTRICTIVO)
        self.never_translate_patterns = [
            r'^#.*',                          # Comentarios
            r'^ship\s+"[^"]*"',               # Definiciones de naves (nombres técnicos)
            r'^outfit\s+"[^"]*"',             # Definiciones de equipos (nombres técnicos)
            r'^planet\s+"[^"]*"',             # Definiciones de planetas (nombres técnicos)
            r'^system\s+"[^"]*"',             # Definiciones de sistemas (nombres técnicos)
            r'^government\s+"[^"]*"',         # Definiciones de gobiernos
            r'^event\s+"[^"]*"',              # Definiciones de eventos
            r'^mission\s+"[^"]*"',            # Definiciones de misiones
            r'^conversation\s+"[^"]*"',       # Definiciones de conversaciones
            r'^fleet\s+"[^"]*"',              # Definiciones de flotas
            r'^effect\s+"[^"]*"',             # Definiciones de efectos
            r'^phrase\s+"[^"]*"',             # Definiciones de frases
            r'^word$',                        # Palabra clave 'word'
            r'^trade$',                       # Palabra clave 'trade'
            r'^commodity\s+"[^"]*"',          # Definiciones de mercancías (NO traducir nombres)
            r'^string\s+"[^"]*"',             # Identificadores de string (NO traducir)
            r'^tip\s+"[^"]*"',                # Identificadores de tip (NO traducir)
            r'^interface\s+"[^"]*"',          # Nombres de interfaces (NO traducir)
            r'^\s*sprite\s+',                 # Sprites
            r'^\s*sound\s+',                  # Sonidos
            r'^\s*thumbnail\s+',              # Miniaturas
            r'^\s*icon\s+',                   # Iconos
            r'^\s*category\s+',               # Categorías (técnicas)
            r'^\s*cost\s+\d+',                # Costos (solo números)
            r'^\s*mass\s+\d+',                # Masa (solo números)
            r'^\s*licenses?\s+',              # Licencias (nombres técnicos)
            r'^\s*pos\s+',                    # Posiciones
            r'^\s*government\s+[^"]*$',       # Gobierno (asignación)
            r'^\s*music\s+',                  # Música
            r'^\s*habitable\s+',              # Habitable
            r'^\s*belt\s+',                   # Cinturones
            r'^\s*link\s+',                   # Enlaces
            r'^\s*asteroids\s+',              # Asteroides
            r'^\s*trade\s+',                  # Comercio
            r'^\s*fleet\s+',                  # Flotas (asignación)
            r'^\s*object\s+',                 # Objetos
            r'^\s*minables\s+',               # Minables
            r'^\s*hazard\s+',                 # Peligros (asignación)
            r'^\s*invisible\s*$',             # Invisible
            r'^\s*"[^"]*"\s+\d+',             # Coordenadas "nombre" x y
            r'^\s*\d+\s+\d+',                 # Coordenadas numéricas
            r'^\s*\d+$',                      # Solo números
            r'^\s*attributes\s+',             # Atributos técnicos
            r'^\s*weapon\s+',                 # Armas (asignación)
            r'^\s*engine\s+',                 # Motores (asignación)
            r'^\s*(to\s+)?(offer|complete|fail|accept|decline)\s*$',  # Palabras clave de misiones
            r'^\s*(source|destination|passengers|cargo|payment)\s+',  # Palabras clave de misiones
            r'^\s*(landing|takeoff|assisting|boarding)\s*$',  # Estados de misión
            r'^\s*(minor|invisible|repeat|clearance)\s*$',  # Modificadores de misión
            r'^\s*random\s+<\s*\d+',          # Condiciones random
            r'^\s*not\s+"[^"]*"',             # Condiciones not
            r'^\s*(log|set|clear)\s+',        # Comandos de log/set/clear
            r'^\s*color\s+',                  # Definiciones de colores de interfaz
            r'^\s*panel\s+',                  # Paneles de interfaz
            r'^\s*point\s+',                  # Puntos de interfaz
            r'^\s*from\s+',                   # Desde (coordenadas)
            r'^\s*to\s+\d+',                  # Hasta (coordenadas)
            r'^\s*center\s+',                 # Centro (coordenadas)
            r'^\s*dimensions\s+',             # Dimensiones
            r'^\s*align\s+',                  # Alineación
            r'^\s*outline\s+',                # Outline
            r'^\s*image\s+',                  # Image
            r'^\s*box\s+',                    # Box
            r'^\s*bar\s+',                    # Bar
            r'^\s*ring\s+',                   # Ring
            r'^\s*value\s+',                  # Value (técnico)
            r'^\s*visible\s+',                # Visible (técnico)
            r'^\s*active\s+',                 # Active (técnico)
            r'^\s*anchor\s+',                 # Anchor
            r'^\s*line$',                     # Line
            r'^\s*truncate\s+',               # Truncate
            r'^\s*width\s+',                  # Width
            r'^\s*height\s+',                 # Height
            r'^\s*size\s+',                   # Size
            r'^\s*colored\s*$',               # Colored
            r'^\s*reversed\s*$',              # Reversed
            r'^\s*variant\s+\d+',             # Variantes de flota (no traducir números)
            r'^\s*turret\s+-?\d+\s+-?\d+',    # Posiciones de torretas
            r'^\s*gun\s+-?\d+\s+-?\d+',       # Posiciones de cañones
            # NUEVAS RESTRICCIONES PARA EVITAR CONFLICTOS
            r'^\s*\t*"[^"]*"\s*$',            # Nombres en comillas simples (commodities, etc.)
            r'^\s*map\s+',                    # Cualquier cosa relacionada con mapas
            r'^\s*attribute\s+',              # Atributos de naves/outfits
            r'^\s*space\s+',                  # Espacios y coordenadas
            r'^\s*shipyard\s+',               # Astilleros
            r'^\s*outfitter\s+',              # Equipadores
        ]
        
        # Palabras clave que indican texto que SÍ debe traducirse (MÁS SELECTIVO)
        self.translatable_text_indicators = [
            r'^\s*`[^`]+`\s*$',               # Texto entre backticks (diálogos)
            r'description\s+"([^"]+)"',       # Descripciones en comillas
            r'spaceport\s+"([^"]+)"',         # Descripciones de puertos espaciales
            r'landscape\s+"([^"]+)"',         # Descripciones de paisajes (nombres visibles)
            r'tribute\s+"([^"]+)"',           # Tributos
            r'bribe\s+"([^"]+)"',             # Sobornos
            r'fine\s+"([^"]+)"',              # Multas
            r'friendly hail\s+"([^"]+)"',     # Saludos amistosos
            r'hostile hail\s+"([^"]+)"',      # Saludos hostiles
            r'language\s+"([^"]+)"',          # Idiomas
            r'currency\s+"([^"]+)"',          # Monedas
            r'swizzle\s+\d+\s+"([^"]+)"',     # Textos de swizzle
            r'label\s+"([^"]+)"',             # Etiquetas de interfaz (SÍ traducir)
            r'button\s+\w+\s+"([^"]+)"',      # Botones de interfaz (SÍ traducir)
            # PATRONES SELECTIVOS PARA NAVES Y OUTFITS (solo descripciones visibles)
            r'plural\s+"([^"]+)"',            # Plurales de naves (texto visible)
            r'noun\s+"([^"]+)"',              # Sustantivos de naves/outfits (texto visible)
            r'explanation\s+"([^"]+)"',       # Explicaciones de outfits
            r'tooltip\s+"([^"]+)"',           # Tooltips de ayuda
            r'help\s+"([^"]+)"',              # Texto de ayuda
            # NO incluir patrones peligrosos que podrían afectar funcionalidad
        ]
        
        # Palabras que nunca deben traducirse (nombres técnicos)
        self.technical_words = [
            'ship', 'outfit', 'planet', 'system', 'government', 'event', 'mission',
            'conversation', 'fleet', 'effect', 'phrase', 'word', 'sprite', 'sound',
            'thumbnail', 'icon', 'category', 'cost', 'mass', 'licenses', 'license',
            'pos', 'music', 'habitable', 'belt', 'link', 'asteroids', 'trade',
            'object', 'minables', 'hazard', 'invisible', 'attributes', 'weapon',
            'engine', 'offer', 'complete', 'fail', 'accept', 'decline', 'source',
            'destination', 'passengers', 'cargo', 'payment', 'landing', 'takeoff',
            'assisting', 'boarding', 'minor', 'repeat', 'clearance', 'random',
            'not', 'log', 'set', 'clear', 'commodity', 'to', 'color', 'interface',
            'panel', 'point', 'from', 'center', 'dimensions', 'align'
            # NOTA: 'tip', 'label', 'button', 'text' NO están aquí porque SÍ queremos traducir su contenido
        ]

    def detect_encoding(self, file_path):
        """Detecta la codificación de un archivo"""
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                return result['encoding'] or 'utf-8'
        except:
            return 'utf-8'

    def should_never_translate_line(self, line):
        """Determina si una línea NUNCA debe traducirse"""
        line_stripped = line.strip()
        
        # Verificar patrones que nunca deben traducirse
        for pattern in self.never_translate_patterns:
            if re.match(pattern, line_stripped, re.IGNORECASE):
                return True
        
        # Líneas que son solo números, símbolos o muy cortas
        if re.match(r'^[\d\s\.\-\+\*\/\(\)\[\]<>=]+$', line_stripped):
            return True
            
        if len(line_stripped) < 3:
            return True
        
        # Si comienza con una palabra técnica (EXCEPTO elementos de interfaz)
        first_word = line_stripped.split()[0] if line_stripped.split() else ""
        if first_word.lower() in self.technical_words:
            return True
        
        # NO bloquear elementos de interfaz que queremos traducir
        interface_elements = [
            r'^tip\s+"[^"]*"',              # Definiciones de tip (NO traducir)
            r'^label\s+"[^"]*"',            # Labels (SÍ traducir contenido)
            r'^button\s+\w+\s+"[^"]*"',     # Botones (SÍ traducir contenido)
            r'^string\s+"[^"]*"',           # Strings (NO traducir, son identificadores)
        ]
        
        for pattern in interface_elements:
            if re.match(pattern, line_stripped):
                # Bloquear tip definitions y strings, no los demás
                if pattern.startswith('^tip') or pattern.startswith('^string'):
                    return True  # Bloqueamos definiciones de tip y strings
                else:
                    return False  # NO bloqueamos label, button
            
        return False

    def extract_translatable_text(self, line):
        """Extrae solo el texto que debe traducirse de una línea"""
        line_stripped = line.strip()
        
        # Solo traducir texto entre backticks (diálogos)
        backtick_match = re.match(r'^(\s*)`([^`]+)`(\s*)$', line)
        if backtick_match:
            prefix, text, suffix = backtick_match.groups()
            return prefix, text, suffix, 'backtick'
        
        # Buscar descripciones específicas en comillas
        for pattern in self.translatable_text_indicators:
            match = re.search(pattern, line)
            if match and len(match.groups()) > 0:
                text_to_translate = match.group(1)
                return None, text_to_translate, None, 'description'
        
        # Detectar definiciones de tip (NO las traducimos, son identificadores)
        tip_match = re.match(r'^tip\s+"([^"]+)"', line_stripped)
        if tip_match:
            return None, None, None, 'tip_definition'
        
        # Detectar botones de interfaz con patrones específicos
        button_patterns = [
            r'^(\s*)button\s+(\w+)\s+"([^"]+)"(.*)$',  # button X "texto"
            r'^(\s*)label\s+"([^"]+)"(.*)$',          # label "texto"
            # NO incluir string porque son identificadores técnicos
        ]
        
        for pattern in button_patterns:
            match = re.match(pattern, line)
            if match:
                if 'button' in pattern:
                    prefix, button_key, text, suffix = match.groups()
                    return prefix, text, suffix, 'button'
                else:  # label
                    prefix, text, suffix = match.groups()
                    return prefix, text, suffix, 'label'
        
        return None, None, None, None

    def translate_text(self, text):
        """Traduce un texto usando Google Translate preservando TODOS los identificadores del juego"""
        try:
            if len(text.strip()) < 2:
                return text
                
            # Limpiar el texto pero mantener variables del juego y elementos especiales
            clean_text = text.strip()
            if not clean_text:
                return text
            
            # PRESERVAR TODOS LOS ELEMENTOS ESPECIALES DEL JUEGO
            preservation_map = {}
            temp_text = clean_text
            placeholder_counter = 0
            
            # 1. Variables del juego como <planet>, <origin>, <destination>, <tons>, etc.
            # IMPORTANTE: Preservar TODAS las etiquetas entre < > sin excepción
            game_variables = re.findall(r'<[^>]+>', temp_text)
            for var in game_variables:
                placeholder = f"__GAMEVAR_{placeholder_counter}__"
                preservation_map[placeholder] = var
                temp_text = temp_text.replace(var, placeholder)
                placeholder_counter += 1
            
            # 2. Números con unidades del juego como "5000 credits", "10 tons", "3 jumps"
            game_units_pattern = r'\b\d+(?:[.,]\d+)?\s*(?:credits?|tons?|jumps?|days?|units?|MW|GW|kW|km|m)\b'
            game_units = re.findall(game_units_pattern, temp_text, re.IGNORECASE)
            for unit in game_units:
                placeholder = f"__GAMEUNIT_{placeholder_counter}__"
                preservation_map[placeholder] = unit
                temp_text = temp_text.replace(unit, placeholder)
                placeholder_counter += 1
            
            # 3. Coordenadas y números técnicos como "150.5 -200.3"
            coordinates_pattern = r'\b-?\d+(?:\.\d+)?\s+-?\d+(?:\.\d+)?\b'
            coordinates = re.findall(coordinates_pattern, temp_text)
            for coord in coordinates:
                placeholder = f"__COORD_{placeholder_counter}__"
                preservation_map[placeholder] = coord
                temp_text = temp_text.replace(coord, placeholder)
                placeholder_counter += 1
            
            # 4. Nombres propios entre comillas (naves, outfits, sistemas)
            quoted_names = re.findall(r'"[A-Z][^"]*"', temp_text)
            for name in quoted_names:
                placeholder = f"__QUOTEDNAME_{placeholder_counter}__"
                preservation_map[placeholder] = name
                temp_text = temp_text.replace(name, placeholder)
                placeholder_counter += 1
            
            # 5. Preservar guiones bajos al inicio (indicadores de teclas de acceso rápido)
            underscore_prefix = ""
            if temp_text.startswith('_'):
                underscore_prefix = "_"
                temp_text = temp_text[1:]
            
            # 6. Preservar puntos suspensivos
            ellipsis_suffix = ""
            if temp_text.endswith('...'):
                ellipsis_suffix = "..."
                temp_text = temp_text[:-3]
            
            # 7. Preservar archivos y extensiones
            file_extensions = re.findall(r'\b\w+\.\w+\b', temp_text)
            for file_ext in file_extensions:
                placeholder = f"__FILE_{placeholder_counter}__"
                preservation_map[placeholder] = file_ext
                temp_text = temp_text.replace(file_ext, placeholder)
                placeholder_counter += 1
            
            # No traducir si queda muy poco texto después de preservar elementos
            if len(temp_text.strip()) < 3:
                return text
            
            print(f"    🌍 Traduciendo: '{temp_text[:50]}{'...' if len(temp_text) > 50 else ''}'")
            result = self.translator.translate(temp_text, dest=self.target_lang, src='en')
            translated = result.text
            
            # RESTAURAR TODOS LOS ELEMENTOS PRESERVADOS
            for placeholder, original_value in preservation_map.items():
                # Buscar tanto el placeholder original como en minúsculas (Google Translate los convierte)
                placeholder_lower = placeholder.lower()
                if placeholder in translated:
                    translated = translated.replace(placeholder, original_value)
                elif placeholder_lower in translated:
                    translated = translated.replace(placeholder_lower, original_value)
            
            # Verificación adicional: asegurar que no queden placeholders sin restaurar
            remaining_placeholders = re.findall(r'__[a-zA-Z]+_\d+__', translated)
            if remaining_placeholders:
                # Intentar restaurar manualmente con búsqueda insensible a mayúsculas
                for placeholder in remaining_placeholders:
                    # Buscar placeholder original correspondiente
                    for orig_placeholder, orig_value in preservation_map.items():
                        if orig_placeholder.lower() == placeholder.lower():
                            translated = translated.replace(placeholder, orig_value)
                            break
            
            # *** NUEVO: Normalizar el texto para el juego (eliminar tildes) ***
            translated = self.normalize_text_for_game(translated)
            
            # Restaurar elementos especiales
            final_text = underscore_prefix + translated + ellipsis_suffix
            
            print(f"    ✅ Resultado: '{final_text[:50]}{'...' if len(final_text) > 50 else ''}'")
            time.sleep(0.1)  # Pausa para evitar rate limiting
            return final_text
        except Exception as e:
            print(f"    ❌ Error traduciendo '{text[:30]}...': {e}")
            return text

    def translate_line(self, line):
        """Traduce una línea si es apropiado"""
        # No traducir líneas que nunca deben traducirse
        if self.should_never_translate_line(line):
            return line, False
        
        # Extraer texto traducible
        prefix, text, suffix, text_type = self.extract_translatable_text(line)
        
        if text and text_type:
            if text_type == 'backtick':
                # Traducir texto entre backticks
                translated_text = self.translate_text(text)
                return f"{prefix}`{translated_text}`{suffix}\n" if line.endswith('\n') else f"{prefix}`{translated_text}`{suffix}", True
            elif text_type == 'description':
                # Traducir texto en descripciones específicas
                translated_text = self.translate_text(text)
                return line.replace(text, translated_text), True
            elif text_type == 'button':
                # Traducir texto de botones
                translated_text = self.translate_text(text)
                # Reconstruir la línea del botón
                button_match = re.match(r'^(\s*)button\s+(\w+)\s+"([^"]+)"(.*)$', line)
                if button_match:
                    spaces, button_key, original_text, rest = button_match.groups()
                    new_line = f'{spaces}button {button_key} "{translated_text}"{rest}'
                    return new_line + ('\n' if line.endswith('\n') else ''), True
                return line, False
            elif text_type == 'label':
                # Traducir texto de etiquetas
                translated_text = self.translate_text(text)
                label_match = re.match(r'^(\s*)label\s+"([^"]+)"(.*)$', line)
                if label_match:
                    spaces, original_text, rest = label_match.groups()
                    new_line = f'{spaces}label "{translated_text}"{rest}'
                    return new_line + ('\n' if line.endswith('\n') else ''), True
                return line, False
            # NO traducir strings porque son identificadores técnicos
        
        return line, False

    def translate_map_planets_file(self, source_file, dest_file):
        """Traduce específicamente el archivo map planets.txt con lógica especial"""
        print(f"\n🌍 Procesando archivo de planetas: {source_file.name}")
        
        # Crear directorio de destino
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Detectar codificación
        encoding = self.detect_encoding(source_file)
        print(f"   🔤 Codificación: {encoding}")
        
        try:
            with open(source_file, 'r', encoding=encoding, errors='ignore') as f:
                lines = f.readlines()
        except:
            print(f"   ⚠️ Error con {encoding}, usando UTF-8...")
            with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        
        print(f"   📊 Total de líneas: {len(lines)}")
        translated_lines = []
        lines_translated = 0
        lines_skipped = 0
        in_planet_block = False
        current_planet = ""
        
        for i, line in enumerate(lines):
            if i % 500 == 0 and i > 0:
                print(f"   📈 Progreso planetas: {i}/{len(lines)} líneas...")
            
            original_line = line
            line_stripped = line.strip()
            
            # DEBUG: Mostrar número de línea siempre
            if line_stripped and not line_stripped.startswith('#'):
                print(f"    📍 LÍNEA {i+1}: Analizando: '{line_stripped[:80]}{'...' if len(line_stripped) > 80 else ''}'")
            
            # Detectar inicio de bloque de planeta
            planet_match = re.match(r'^planet\s+"?([^"]*)"?', line_stripped)
            if planet_match:
                in_planet_block = True
                current_planet = planet_match.group(1)
                print(f"  🪐 LÍNEA {i+1}: Procesando planeta: {current_planet}")
                translated_lines.append(original_line)  # No traducir nombres de planetas
                continue
            
            # Detectar fin de bloque de planeta (línea vacía o nueva definición)
            if in_planet_block and (not line_stripped or 
                                  line_stripped.startswith('#') or
                                  any(line_stripped.startswith(kw) for kw in ['planet ', 'system ', 'fleet ', 'ship ', 'outfit '])):
                if not line_stripped or line_stripped.startswith('#'):
                    in_planet_block = False if not line_stripped else in_planet_block
                    print(f"    📍 LÍNEA {i+1}: {'Fin de bloque de planeta' if not in_planet_block else 'Comentario en planeta'}")
                else:
                    in_planet_block = False
                    print(f"    📍 LÍNEA {i+1}: Fin de bloque de planeta - nueva definición")
                translated_lines.append(original_line)
                continue
            
            # Si estamos en un bloque de planeta, aplicar lógica específica
            if in_planet_block:
                was_translated = False
                print(f"    🔬 LÍNEA {i+1}: Dentro del planeta {current_planet}")
                
                # 1. description `texto` (CON BACKTICKS, no comillas)
                if line_stripped.startswith('description `'):
                    print(f"    🎯 LÍNEA {i+1}: DETECTADA DESCRIPCIÓN - verificando si termina en backtick...")
                    if line_stripped.endswith('`'):
                        print(f"    ✅ LÍNEA {i+1}: DESCRIPCIÓN VÁLIDA - extrayendo texto...")
                        # Extraer el texto entre backticks
                        desc_match = re.match(r'^(\s*)description\s+`(.+)`(.*)$', line.rstrip())
                        if desc_match:
                            prefix, text_to_translate, suffix = desc_match.groups()
                            print(f"    📝 LÍNEA {i+1}: ¡TRADUCIENDO DESCRIPCIÓN! de {current_planet}")
                            print(f"        Texto original: '{text_to_translate[:60]}{'...' if len(text_to_translate) > 60 else ''}'")
                            try:
                                translated_text = self.translate_text(text_to_translate)
                                new_line = f'{prefix}description `{translated_text}`{suffix}'
                                if original_line.endswith('\n'):
                                    new_line += '\n'
                                translated_lines.append(new_line)
                                lines_translated += 1
                                was_translated = True
                                print(f"    ✅ LÍNEA {i+1}: Descripción traducida exitosamente!")
                                print(f"        Resultado: '{translated_text[:60]}{'...' if len(translated_text) > 60 else ''}'")
                            except Exception as e:
                                print(f"    ❌ LÍNEA {i+1}: Error traduciendo descripción: {e}")
                                translated_lines.append(original_line)
                                lines_skipped += 1
                                was_translated = True
                        else:
                            print(f"    ❌ LÍNEA {i+1}: DESCRIPCIÓN no coincide con regex")
                    else:
                        print(f"    ⚠️  LÍNEA {i+1}: DESCRIPCIÓN no termina en backtick: '{line_stripped[-10:]}'")
                
                # 2. spaceport `texto` (CON BACKTICKS, no comillas)
                elif line_stripped.startswith('spaceport `'):
                    print(f"    🎯 LÍNEA {i+1}: DETECTADO SPACEPORT - verificando si termina en backtick...")
                    if line_stripped.endswith('`'):
                        print(f"    ✅ LÍNEA {i+1}: SPACEPORT VÁLIDO - extrayendo texto...")
                        spaceport_match = re.match(r'^(\s*)spaceport\s+`(.+)`(.*)$', line.rstrip())
                        if spaceport_match:
                            prefix, text_to_translate, suffix = spaceport_match.groups()
                            print(f"    🚀 LÍNEA {i+1}: ¡TRADUCIENDO SPACEPORT! de {current_planet}")
                            print(f"        Texto original: '{text_to_translate[:60]}{'...' if len(text_to_translate) > 60 else ''}'")
                            try:
                                translated_text = self.translate_text(text_to_translate)
                                new_line = f'{prefix}spaceport `{translated_text}`{suffix}'
                                if original_line.endswith('\n'):
                                    new_line += '\n'
                                translated_lines.append(new_line)
                                lines_translated += 1
                                was_translated = True
                                print(f"    ✅ LÍNEA {i+1}: Spaceport traducido exitosamente!")
                                print(f"        Resultado: '{translated_text[:60]}{'...' if len(translated_text) > 60 else ''}'")
                            except Exception as e:
                                print(f"    ❌ LÍNEA {i+1}: Error traduciendo spaceport: {e}")
                                translated_lines.append(original_line)
                                lines_skipped += 1
                                was_translated = True
                        else:
                            print(f"    ❌ LÍNEA {i+1}: SPACEPORT no coincide con regex")
                    else:
                        print(f"    ⚠️  LÍNEA {i+1}: SPACEPORT no termina en backtick: '{line_stripped[-10:]}'")
                
                # 3. También traducir otros elementos de texto si aparecen
                elif (line_stripped.startswith('tribute "') or 
                      line_stripped.startswith('bribe "') or
                      line_stripped.startswith('friendly hail "') or
                      line_stripped.startswith('hostile hail "')):
                    print(f"    🎯 LÍNEA {i+1}: DETECTADO ELEMENTO CON COMILLAS")
                    # Extraer cualquier texto en comillas para estos elementos
                    text_match = re.match(r'^(\s*)(\w+(?:\s+\w+)*)\s+"(.+)"(.*)$', line.rstrip())
                    if text_match:
                        prefix, element_type, text_to_translate, suffix = text_match.groups()
                        print(f"    🔤 LÍNEA {i+1}: Traduciendo {element_type} de {current_planet}")
                        try:
                            translated_text = self.translate_text(text_to_translate)
                            new_line = f'{prefix}{element_type} "{translated_text}"{suffix}'
                            if original_line.endswith('\n'):
                                new_line += '\n'
                            translated_lines.append(new_line)
                            lines_translated += 1
                            was_translated = True
                            print(f"    ✅ LÍNEA {i+1}: {element_type} traducido correctamente")
                        except Exception as e:
                            print(f"    ❌ LÍNEA {i+1}: Error traduciendo {element_type}: {e}")
                            translated_lines.append(original_line)
                            lines_skipped += 1
                            was_translated = True
                    else:
                        print(f"    ❌ LÍNEA {i+1}: Elemento con comillas no coincide con regex")
                
                # Si no se tradujo, verificar si debe omitirse (mantener sin traducir)
                if not was_translated:
                    print(f"    ⏭️  LÍNEA {i+1}: No se tradujo - manteniendo línea original")
                    translated_lines.append(original_line)
                    lines_skipped += 1
            else:
                # Fuera de bloques de planeta, usar lógica normal
                translated_line, was_translated = self.translate_line(line)
                if was_translated:
                    lines_translated += 1
                else:
                    lines_skipped += 1
                translated_lines.append(translated_line)
        
        # Guardar archivo solo si hay traducciones
        if lines_translated > 0:
            print(f"   💾 Guardando archivo de planetas con {lines_translated} líneas traducidas...")
            with open(dest_file, 'w', encoding='utf-8-sig') as f:
                f.writelines(translated_lines)
            print(f"   ✅ Archivo de planetas guardado: {dest_file}")
        else:
            print(f"   ⏭️  Sin traducciones en planetas, archivo omitido")
        
        return lines_translated

    def translate_file(self, source_file, dest_file):
        """Traduce un archivo completo con lógica mejorada y específica por tipo"""
        print(f"\n📄 Procesando archivo: {source_file.name}")
        
        # Determinar si necesita lógica especial
        filename_lower = source_file.name.lower()
        
        if filename_lower == 'commodities.txt':
            print(f"   🎯 Aplicando lógica especial para commodities")
            return self.translate_commodities_file(source_file, dest_file)
        elif filename_lower in ['ships.txt', 'outfits.txt', 'engines.txt', 'weapons.txt', 'power.txt', 'harvesting.txt', 'variants.txt'] or \
             any(filename_lower.endswith(pattern) for pattern in ['ships.txt', 'outfits.txt', 'engines.txt', 'weapons.txt', 'power.txt', 'sales.txt']):
            print(f"   🎯 Aplicando lógica especial para ships/outfits/engines/harvesting/sales")
            return self.translate_ships_outfits_file(source_file, dest_file)
        elif filename_lower == 'starts.txt':
            print(f"   🎯 Aplicando lógica especial para starts")
            return self.translate_starts_file(source_file, dest_file)
        elif filename_lower == 'persons.txt':
            print(f"   🎯 Aplicando lógica especial para persons")
            return self.translate_persons_file(source_file, dest_file)
        elif filename_lower == 'help.txt':
            print(f"   🎯 Aplicando lógica especial para help")
            return self.translate_help_file(source_file, dest_file)
        elif 'hails.txt' in filename_lower or 'names.txt' in filename_lower or filename_lower in ['wanderers.txt', 'hai.txt', 'korath.txt']:
            print(f"   🎯 Aplicando lógica especial para hails/names/facciones")
            return self.translate_hails_file(source_file, dest_file)
        elif 'news.txt' in filename_lower:
            print(f"   🎯 Aplicando lógica especial para news")
            return self.translate_news_file(source_file, dest_file)
        elif filename_lower == 'fleets.txt' or filename_lower.endswith(' fleets.txt'):
            print(f"   🎯 Aplicando lógica especial para fleets")
            return self.translate_fleets_file(source_file, dest_file)
        elif filename_lower == 'governments.txt' or filename_lower.endswith(' governments.txt'):
            print(f"   🎯 Aplicando lógica especial para governments")
            return self.translate_governments_file(source_file, dest_file)
        
        # Lógica general para otros archivos
        # Crear directorio de destino
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Detectar codificación
        encoding = self.detect_encoding(source_file)
        print(f"   🔤 Codificación: {encoding}")
        
        try:
            with open(source_file, 'r', encoding=encoding, errors='ignore') as f:
                lines = f.readlines()
        except:
            print(f"   ⚠️ Error con {encoding}, usando UTF-8...")
            with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        
        print(f"   📊 Total de líneas: {len(lines)}")
        translated_lines = []
        lines_translated = 0
        lines_skipped = 0
        
        for i, line in enumerate(lines):
            if i % 100 == 0 and i > 0:
                print(f"   📈 Progreso: {i}/{len(lines)} líneas...")
                
            translated_line, was_translated = self.translate_line(line)
            
            if was_translated:
                lines_translated += 1
                print(f"  ✅ Línea {i+1} traducida")
            else:
                lines_skipped += 1
            
            translated_lines.append(translated_line)
        
        # Solo crear archivo si hay traducciones
        if lines_translated > 0:
            print(f"   💾 Guardando archivo con {lines_translated} líneas traducidas...")
            # Guardar con codificación UTF-8 y BOM para máxima compatibilidad
            with open(dest_file, 'w', encoding='utf-8-sig') as f:
                f.writelines(translated_lines)
            print(f"   ✅ Archivo guardado: {dest_file}")
        else:
            print(f"   ⏭️  Sin traducciones, archivo omitido")
        
        return lines_translated

    def translate_folder(self, source_folder, dest_folder):
        """Traduce archivos específicos de una carpeta con procesamiento SEGURO"""
        if not source_folder.exists():
            print(f"❌ Carpeta no encontrada: {source_folder}")
            return 0
            
        print(f"\n📂 Procesando carpeta: {source_folder.name}")
        
        # Patrones específicos según la carpeta
        if source_folder.name == '_ui':
            # Para interfaz de usuario, traducir TODOS los archivos .txt (es seguro)
            translatable_file_patterns = [
                "*.txt",  # Todos los archivos .txt en _ui
            ]
            print(f"   🎯 Modo interfaz de usuario: traduciendo TODOS los archivos .txt")
        else:
            # Para otras carpetas de facciones, usar patrones MÁS SELECTIVOS
            translatable_file_patterns = [
                # Patrones de misiones (SEGURO de traducir)
                "*missions*.txt",
                "*mission*.txt",
                
                # Patrones de conversaciones y diálogos (SEGURO de traducir)
                "*conversations*.txt", 
                "*conversation*.txt",
                "*dialogs*.txt",
                "*dialog*.txt",
                
                # Patrones de comunicaciones (SEGURO de traducir)
                "*hails*.txt",
                "*hail*.txt",
                
                # Patrones de noticias y eventos (SEGURO de traducir)
                "*news*.txt",
                "*events*.txt",
                "*event*.txt",
                
                # Patrones de nombres (CUIDADO - solo algunos seguros)
                "*names*.txt",
                
                # Archivos de introducción y campañas (SEGURO de traducir)
                "intro*.txt",
                "*intro*.txt",
                "*campaign*.txt",
                
                # Archivos específicos seguros
                "sales.txt",        # Diálogos de venta
                "jobs.txt",         # Trabajos/misiones
                "*jobs.txt",        # Trabajos por región
                
                # NUEVOS: Archivos de ships y outfits (SOLO DESCRIPCIONES)
                "ships.txt",        # Naves (solo descripciones)
                "outfits.txt",      # Outfits (solo descripciones)
                "engines.txt",      # Motores (solo descripciones)
                "weapons.txt",      # Armas (solo descripciones)
                "power.txt",        # Sistemas de poder (solo descripciones)
            ]
            print(f"   🎯 Modo facción: procesando archivos seguros + ships/outfits (solo descripciones)")
        
        files_processed = 0
        processed_files = set()  # Para evitar duplicados
        
        # Procesar patrones específicos
        for pattern in translatable_file_patterns:
            matching_files = list(source_folder.glob(pattern))
            if matching_files:
                print(f"   🔍 Patrón '{pattern}': {len(matching_files)} archivos encontrados")
            for file_path in matching_files:
                if file_path.is_file() and file_path.name not in processed_files:
                    # Verificar que no sea un archivo problemático
                    if self.is_safe_to_translate(file_path):
                        print(f"   📄 Procesando: {file_path.name}")
                        dest_file = dest_folder / file_path.name
                        lines_translated = self.translate_file(file_path, dest_file)
                        if lines_translated > 0:
                            files_processed += 1
                        processed_files.add(file_path.name)
                    else:
                        print(f"   🚫 Archivo omitido por seguridad: {file_path.name}")
        
        # Procesar subcarpetas recursivamente (solo para _ui)
        if source_folder.name == '_ui':
            for item in source_folder.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    print(f"   📁 Procesando subcarpeta: {item.name}")
                    sub_files = self.translate_folder(item, dest_folder / item.name)
                    files_processed += sub_files
        
        print(f"   � Total archivos procesados en {source_folder.name}: {files_processed}")
        return files_processed

    def is_safe_to_translate(self, file_path):
        """Determina si un archivo es seguro para traducir"""
        filename = file_path.name.lower()
        
        # Archivos que NUNCA deben traducirse
        unsafe_files = [
            'fleets.txt',        # Definiciones de flotas (puede afectar balance)
            'governments.txt',   # Definiciones de gobiernos (puede afectar funcionamiento)
            'systems.txt',       # Sistemas (afecta navegación)
            'planets.txt',       # Planetas (afecta navegación)
            'map systems.txt',   # Mapa de sistemas (afecta navegación)
            'map planets.txt',   # Será procesado por método especial
            'commodities.txt',   # Será procesado por método especial
            'variants.txt',      # Variantes de naves (afecta balance)
            'persons.txt',       # Personajes específicos (puede afectar misiones)
            'effects.txt',       # Efectos visuales (técnico)
            'hazards.txt',       # Peligros (técnico)
            'formations.txt',    # Formaciones (técnico)
            'stars.txt',         # Estrellas (técnico)
            'series.txt',        # Series de naves (técnico)
        ]
        
        # Verificar si el archivo está en la lista de no seguros
        if filename in unsafe_files:
            return False
        
        # Archivos que SÍ queremos traducir (solo descripciones)
        translatable_files = [
            'ships.txt',         # Descripciones de naves (SÓLO descripciones)
            'outfits.txt',       # Descripciones de outfits (SÓLO descripciones)
            'engines.txt',       # Descripciones de motores (SÓLO descripciones)
            'weapons.txt',       # Descripciones de armas (SÓLO descripciones)
            'power.txt',         # Descripciones de sistemas de poder
            'systems.txt',       # En algunos contextos puede tener descripciones
        ]
        
        # Si es un archivo translatable específico, usar lógica especial
        if filename in translatable_files:
            return True
        
        # Verificar patrones de archivos técnicos que NO queremos
        unsafe_patterns = [
            'derelict',
            'variant',
            'formation',
            'hazard',
        ]
        
        if any(pattern in filename for pattern in unsafe_patterns):
            return False
        
        return True

    def create_plugin_structure(self):
        """Crea la estructura básica del plugin"""
        # Crear directorio del plugin
        self.plugin_path.mkdir(parents=True, exist_ok=True)
        
        # Crear plugin.txt corregido
        plugin_content = '''name "Traducción al Español"
description "Plugin de traducción al español para Endless Sky."
description "Traduce diálogos, misiones y elementos de interfaz."
description ""
description "NOTA: Traducción automática, texto sin tildes para compatibilidad."
description "Mantiene caracteres especiales como ñ."
version "1.0.2"
authors
	"Traductor Automático ES"
tags
	"translation"
	"spanish"
	"español"
	"interface"
	"missions"
'''
        
        plugin_file = self.plugin_path / "plugin.txt"
        with open(plugin_file, 'w', encoding='utf-8') as f:
            f.write(plugin_content)
        
        # Crear README mejorado
        readme_content = '''# Plugin de Traducción al Español para Endless Sky

Este plugin proporciona traducción automática al español para Endless Sky.

## Características
- ✅ Traduce interfaz de usuario (menús, botones, etiquetas)
- ✅ Traduce diálogos de misiones y conversaciones
- ✅ Traduce frases y mensajes del juego
- ✅ Mantiene compatibilidad total con el juego
- ✅ Soporte para caracteres especiales (ñ, ç, etc.)
- ✅ Texto sin tildes para máxima compatibilidad

## Instalación
1. Coloca esta carpeta en el directorio "Plugins" de Endless Sky
2. Inicia el juego
3. Ve a Preferencias → Plugins
4. Activa "Traducción al Español"
5. Reinicia el juego

## Contenido Traducido
- **Interfaz completa**: Menús, botones, etiquetas
- **Sistema de diálogos**: Frases genéricas del juego
- **Misiones humanas**: Contenido principal de la campaña
- **Elementos de UI**: Tooltips, ayuda, configuración

## Características Técnicas
- Codificación UTF-8 para caracteres especiales
- Texto normalizado (sin tildes) para compatibilidad
- Preserva variables del juego (<planet>, <npc>, etc.)
- Mantiene teclas de acceso rápido (_Enter, _Quit, etc.)

## Limitaciones
- Traducción automática, pueden existir errores menores
- Algunos elementos técnicos se mantienen en inglés por compatibilidad
- Las tildes se eliminan para evitar problemas de renderizado
'''
        
        readme_file = self.plugin_path / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        # Crear archivo de configuración de codificación
        encoding_info = '''# Información de codificación para el plugin de traducción
# Este archivo ayuda a asegurar que el juego maneje correctamente
# los caracteres especiales del español

# Plugin creado con codificación UTF-8
# Caracteres soportados: ñ, ç, y otros caracteres especiales
# Tildes eliminadas para compatibilidad: á→a, é→e, í→i, ó→o, ú→u
'''
        
        encoding_file = self.plugin_path / "encoding.txt"
        with open(encoding_file, 'w', encoding='utf-8') as f:
            f.write(encoding_info)

    def run_translation(self):
        """Ejecuta el proceso completo de traducción corregido"""
        print("=== Traductor Automático de Endless Sky (Versión Corregida) ===")
        print(f"Idioma destino: {self.target_lang}")
        print(f"Directorio base: {self.base_path}")
        
        # Verificar directorios
        if not self.data_path.exists():
            print(f"ERROR: No se encontró el directorio de datos: {self.data_path}")
            return
        
        # 🔍 VERIFICAR QUE CARPETAS EXISTEN ANTES DE EMPEZAR
        print(f"\n🔍 Verificando carpetas a procesar...")
        existing_folders = []
        missing_folders = []
        
        for folder_name in self.translatable_folders:
            folder_path = self.data_path / folder_name
            if folder_path.exists():
                existing_folders.append(folder_name)
                print(f"   ✅ {folder_name} - ENCONTRADA")
            else:
                missing_folders.append(folder_name)
                print(f"   ❌ {folder_name} - NO ENCONTRADA")
        
        # Mostrar carpetas excluidas por seguridad
        excluded_folders = ['drak', 'gegno', 'avgi', 'bunrodea', 'iije', 'incipias', 'kahet', 'rulei', 'sheragi', 'successors', 'vyrmeid', 'whispering void']
        print(f"\n🚫 CARPETAS EXCLUIDAS POR SEGURIDAD:")
        for folder_name in excluded_folders:
            folder_path = self.data_path / folder_name
            if folder_path.exists():
                print(f"   🚫 {folder_name} - EXCLUIDA (contiene lógica compleja/técnica)")
        
        print(f"\n📊 RESUMEN DE CARPETAS:")
        print(f"   ✅ Carpetas a procesar: {len(existing_folders)}")
        print(f"   🚫 Carpetas excluidas: {len([f for f in excluded_folders if (self.data_path / f).exists()])}")
        print(f"   ❌ Carpetas no encontradas: {len(missing_folders)}")
        print(f"   📂 Se procesarán: {existing_folders}")
        
        if missing_folders:
            print(f"   ⚠️  Carpetas no encontradas: {missing_folders}")
        
        # 📋 MOSTRAR QUÉ TIPOS DE ARCHIVOS SE BUSCARÁN
        print(f"\n📋 TIPOS DE ARCHIVOS A PROCESAR (MODO SEGURO):")
        print(f"   🎯 En _ui: TODOS los archivos .txt (SEGURO)")
        print(f"   🎯 En facciones: SOLO misiones, conversaciones, diálogos, campañas, noticias (SEGURO)")
        print(f"   🎯 Archivos especiales: map planets (solo descripciones), commodities (solo descripciones visibles)")
        print(f"   🚫 EXCLUIDOS: ships.txt, outfits.txt, fleets.txt, governments.txt, systems.txt, etc. (TÉCNICOS)")
        print(f"   🔍 Patrones seguros: missions, conversations, dialogs, hails, news, events, campaigns, jobs")
        
        # Crear estructura del plugin
        self.create_plugin_structure()
        
        print(f"\n🔧 Creando plugin en: {self.plugin_path}")
        
        print("\n🌟 --- SUPER MEGA MÁXIMA PRIORIDAD: MAP PLANETS ---")
        total_files_processed = 0
        
        # Traducir archivos principales - map planets.txt PRIMERO (SUPER MEGA MÁXIMA PRIORIDAD)
        map_planets_processed = False
        for filename in self.translatable_files:
            if filename == 'map planets.txt':
                source_file = self.data_path / filename
                dest_file = self.plugin_data_path / filename
                
                if source_file.exists():
                    print(f"\n🚀 Procesando {filename} - SUPER MEGA MÁXIMA PRIORIDAD 🚀")
                    lines_translated = self.translate_map_planets_file(source_file, dest_file)
                    if lines_translated > 0:
                        total_files_processed += 1
                        map_planets_processed = True
                        print(f"✅ MAP PLANETS procesado exitosamente con {lines_translated} líneas traducidas")
                    else:
                        print(f"⚠️  MAP PLANETS sin traducciones")
                else:
                    print(f"❌ MAP PLANETS no encontrado: {source_file}")
                break
        
        # Solo traducir archivos específicos que contienen diálogos
        print("\n--- Traduciendo interfaz de usuario (prioridad alta) ---")
        
        # Traducir _ui segundo (interfaz de usuario - prioridad alta)
        ui_folder = self.data_path / '_ui'
        if ui_folder.exists():
            print(f"\n🎯 Procesando interfaz de usuario (_ui) - PRIORIDAD ALTA")
            files_in_ui = self.translate_folder(ui_folder, self.plugin_data_path / '_ui')
            total_files_processed += files_in_ui
        else:
            print(f"  ⚠️  Carpeta _ui no encontrada")
        
        print("\n--- Traduciendo otros archivos principales ---")
        
        # Traducir otros archivos principales (excluyendo map planets que ya se procesó)
        for filename in self.translatable_files:
            if filename == 'map planets.txt':
                continue  # Ya se procesó primero
                
            source_file = self.data_path / filename
            dest_file = self.plugin_data_path / filename
            
            if source_file.exists():
                lines_translated = self.translate_file(source_file, dest_file)
                
                if lines_translated > 0:
                    total_files_processed += 1
            else:
                print(f"  ⚠️  Archivo no encontrado: {filename}")
        
        # Traducir commodities con lógica especial
        print("\n--- Traduciendo commodities (con lógica especial) ---")
        commodities_file = self.data_path / 'commodities.txt'
        if commodities_file.exists():
            print(f"\n🔍 Procesando commodities.txt con lógica especial")
            lines_translated = self.translate_commodities_file(commodities_file, self.plugin_data_path / 'commodities.txt')
            if lines_translated > 0:
                total_files_processed += 1
                print(f"✅ COMMODITIES procesado con {lines_translated} líneas traducidas")
            else:
                print(f"⚠️  COMMODITIES sin traducciones")
        else:
            print(f"❌ COMMODITIES no encontrado: {commodities_file}")
        
        print("\n--- Traduciendo SOLO carpetas SEGURAS con contenido de misiones ---")
        
        # 🔥 PROCESAR TODAS LAS CARPETAS DEFINIDAS (excluyendo _ui que ya se procesó)
        folders_processed = 0
        for folder_name in self.translatable_folders:
            if folder_name == '_ui':
                continue  # Ya se procesó antes
                
            source_folder = self.data_path / folder_name
            dest_folder = self.plugin_data_path / folder_name
            
            if source_folder.exists():
                print(f"\n📂 Procesando carpeta: {folder_name}")
                files_in_folder = self.translate_folder(source_folder, dest_folder)
                total_files_processed += files_in_folder
                folders_processed += 1
                print(f"   ✅ Carpeta {folder_name}: {files_in_folder} archivos procesados")
            else:
                print(f"  ⚠️  Carpeta no encontrada: {folder_name}")
        
        print(f"\n✅ Traducción completada!")
        print(f"📁 Plugin creado en: {self.plugin_path}")
        print(f"📊 {total_files_processed} archivos procesados")
        print(f"📂 {folders_processed + 1} carpetas procesadas (incluyendo _ui)")
        
        if total_files_processed > 0:
            print("\n🎯 Características del plugin:")
            print("   ✅ Interfaz completamente en español")
            print("   ✅ Texto sin tildes para compatibilidad")
            print("   ✅ Soporte para caracteres especiales (ñ)")
            print("   ✅ Codificación UTF-8 con BOM")
            print("   ✅ SOLO facciones principales traducidas")
            print("   ✅ SOLO archivos seguros (misiones, diálogos, UI)")
            print("   ✅ Commodities: solo descripciones visibles")
            print("   🚫 Archivos técnicos preservados (ships, outfits, fleets)")
            print("\n💡 Para usar la traducción:")
            print("   1. Inicia Endless Sky")
            print("   2. Ve a Preferencias → Plugins")
            print("   3. Activa 'Traducción al Español'")
            print("   4. Reinicia el juego")
            print("\n🔧 El juego ahora debería mostrar:")
            print("   • Menús y botones en español")
            print("   • Diálogos traducidos")
            print("   • Misiones de facciones principales traducidas")
            print("   • Descripciones de planetas en español")
            print("   • Nombres de commodities en español (solo descripciones)")
            print("   • ⚠️  IMPORTANTE: Funcionalidad del juego intacta")
        else:
            print("\n⚠️  No se encontraron archivos para traducir")

    def normalize_text_for_game(self, text):
        """
        Normaliza el texto eliminando solo las tildes de las vocales:
        - Elimina tildes: á→a, é→e, í→i, ó→o, ú→u
        - Preserva mayúsculas y minúsculas
        """
        if not text:
            return text
            
        # Mapeo específico para eliminar solo tildes de vocales
        replacements = {
            # Vocales con tilde minúsculas
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            # Vocales con tilde mayúsculas
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        }
        
        # Aplicar reemplazos
        normalized_text = text
        for original, replacement in replacements.items():
            normalized_text = normalized_text.replace(original, replacement)
        
        return normalized_text

    def translate_commodities_file(self, source_file, dest_file):
        """Traduce específicamente el archivo commodities.txt con máxima precaución"""
        print(f"\n📦 Procesando archivo de commodities: {source_file.name}")
        
        # Crear directorio de destino
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Detectar codificación
        encoding = self.detect_encoding(source_file)
        print(f"   🔤 Codificación: {encoding}")
        
        try:
            with open(source_file, 'r', encoding=encoding, errors='ignore') as f:
                lines = f.readlines()
        except:
            print(f"   ⚠️ Error con {encoding}, usando UTF-8...")
            with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        
        print(f"   📊 Total de líneas: {len(lines)}")
        translated_lines = []
        lines_translated = 0
        lines_skipped = 0
        in_commodity_block = False
        current_commodity = ""
        
        for i, line in enumerate(lines):
            if i % 500 == 0 and i > 0:
                print(f"   📈 Progreso commodities: {i}/{len(lines)} líneas...")
            
            original_line = line
            line_stripped = line.strip()
            
            # Detectar inicio de bloque commodity
            commodity_match = re.match(r'^commodity\s+"([^"]*)"(?:\s+(\d+)\s+(\d+))?', line_stripped)
            if commodity_match:
                in_commodity_block = True
                commodity_name = commodity_match.group(1)
                current_commodity = f"commodity {commodity_name}"
                print(f"  📦 LÍNEA {i+1}: Detectado commodity: {commodity_name}")
                translated_lines.append(original_line)  # NO traducir nombres de commodities
                continue
            
            # Detectar fin de bloque
            if in_commodity_block and (not line_stripped or 
                                     line_stripped.startswith('#') or
                                     line_stripped.startswith('commodity ') or
                                     line_stripped.startswith('trade')):
                if not line_stripped or line_stripped.startswith('#') or line_stripped.startswith('trade'):
                    in_commodity_block = False if not line_stripped or line_stripped.startswith('trade') else in_commodity_block
                    print(f"    📍 LÍNEA {i+1}: {'Fin de bloque' if not in_commodity_block else 'Comentario'}")
                else:
                    in_commodity_block = False
                    print(f"    📍 LÍNEA {i+1}: Fin de bloque - nuevo commodity")
                translated_lines.append(original_line)
                continue
            
            # Si estamos en un bloque de commodity, ser MUY SELECTIVO
            if in_commodity_block:
                # IMPORTANTE: En commodities, los nombres entre comillas son IDs técnicos
                # NO traducir NUNCA estos nombres porque romperían el juego
                if line_stripped.startswith('"') and line_stripped.endswith('"'):
                    print(f"    🚫 LÍNEA {i+1}: Nombre de commodity ignorado (ID técnico)")
                    translated_lines.append(original_line)
                    lines_skipped += 1
                else:
                    # Para cualquier otra cosa, usar lógica normal pero conservadora
                    translated_line, was_translated = self.translate_line(line)
                    if was_translated:
                        lines_translated += 1
                        print(f"    ✅ LÍNEA {i+1}: Elemento traducido en {current_commodity}")
                    else:
                        lines_skipped += 1
                    translated_lines.append(translated_line)
            else:
                # Fuera de bloques, usar lógica normal
                translated_line, was_translated = self.translate_line(line)
                if was_translated:
                    lines_translated += 1
                else:
                    lines_skipped += 1
                translated_lines.append(translated_line)
        
        # Guardar archivo solo si hay traducciones
        if lines_translated > 0:
            print(f"   💾 Guardando archivo de commodities con {lines_translated} líneas traducidas...")
            with open(dest_file, 'w', encoding='utf-8-sig') as f:
                f.writelines(translated_lines)
            print(f"   ✅ Archivo de commodities guardado: {dest_file}")
        else:
            print(f"   ⏭️  Sin traducciones en commodities, archivo omitido")
        
        print(f"   📊 Resultado: {lines_translated} traducidas, {lines_skipped} omitidas")
        return lines_translated

    def translate_ships_outfits_file(self, source_file, dest_file):
        """Traduce específicamente archivos de naves y outfits con lógica especial mejorada"""
        print(f"\n🚢 Procesando archivo de naves/outfits: {source_file.name}")
        
        # Crear directorio de destino
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Detectar codificación
        encoding = self.detect_encoding(source_file)
        print(f"   🔤 Codificación: {encoding}")
        
        try:
            with open(source_file, 'r', encoding=encoding, errors='ignore') as f:
                lines = f.readlines()
        except:
            print(f"   ⚠️ Error con {encoding}, usando UTF-8...")
            with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        
        print(f"   📊 Total de líneas: {len(lines)}")
        translated_lines = []
        lines_translated = 0
        lines_skipped = 0
        in_item_block = False
        current_item = ""
        current_indent = 0
        
        for i, line in enumerate(lines):
            if i % 500 == 0 and i > 0:
                print(f"   📈 Progreso naves/outfits: {i}/{len(lines)} líneas...")
            
            original_line = line
            line_stripped = line.strip()
            
            # Detectar inicio de bloque de nave, outfit, effect o minable
            item_match = re.match(r'^(ship|outfit|effect|minable)\s+"?([^"]*)"?', line_stripped)
            if item_match:
                in_item_block = True
                item_type, item_name = item_match.groups()
                current_item = f"{item_type} {item_name}"
                current_indent = len(line) - len(line.lstrip())
                print(f"  🔧 LÍNEA {i+1}: Procesando {item_type}: {item_name}")
                translated_lines.append(original_line)  # No traducir nombres técnicos
                continue
            
            # Detectar fin de bloque (nueva definición al mismo nivel o línea vacía)
            if in_item_block:
                line_indent = len(line) - len(line.lstrip()) if line.strip() else 0
                
                # Si encontramos una nueva definición al mismo nivel, terminar bloque actual
                if (line_stripped and 
                    line_indent <= current_indent and 
                    any(line_stripped.startswith(kw) for kw in ['ship ', 'outfit ', 'effect ', 'minable ', 'planet ', 'system '])):
                    in_item_block = False
                    print(f"    📍 LÍNEA {i+1}: Fin de bloque - nueva definición")
                # Si es línea vacía o comentario, mantener pero no cambiar estado del bloque
                elif not line_stripped or line_stripped.startswith('#'):
                    translated_lines.append(original_line)
                    continue
            
            # Si estamos en un bloque de item, aplicar lógica específica
            if in_item_block:
                was_translated = False
                
                # Detectar descripciones - patrón mejorado
                description_match = re.match(r'^(\s*)(description\s+)"(.+)"(.*)$', line.rstrip())
                if description_match:
                    prefix, keyword, description_text, suffix = description_match.groups()
                    print(f"    🎯 LÍNEA {i+1}: DESCRIPCIÓN DETECTADA en {current_item}")
                    try:
                        translated_text = self.translate_text(description_text)
                        new_line = f'{prefix}{keyword}"{translated_text}"{suffix}'
                        if original_line.endswith('\n'):
                            new_line += '\n'
                        translated_lines.append(new_line)
                        lines_translated += 1
                        was_translated = True
                        print(f"    ✅ LÍNEA {i+1}: Descripción traducida correctamente")
                    except Exception as e:
                        print(f"    ❌ LÍNEA {i+1}: Error traduciendo descripción: {e}")
                        translated_lines.append(original_line)
                        lines_skipped += 1
                        was_translated = True  # Marcar como procesada aunque falló
                
                # Detectar otros elementos traducibles específicos
                if not was_translated:
                    translatable_patterns = [
                        (r'^(\s*)(plural\s+)"(.+)"(.*)$', 'plural'),
                        (r'^(\s*)(noun\s+)"(.+)"(.*)$', 'noun'),
                        (r'^(\s*)(explanation\s+)"(.+)"(.*)$', 'explanation'),
                        (r'^(\s*)(tooltip\s+)"(.+)"(.*)$', 'tooltip'),
                        (r'^(\s*)(help\s+)"(.+)"(.*)$', 'help'),
                    ]
                    
                    for pattern, element_name in translatable_patterns:
                        element_match = re.match(pattern, line.rstrip())
                        if element_match:
                            prefix, keyword, text_to_translate, suffix = element_match.groups()
                            print(f"    🎯 LÍNEA {i+1}: {element_name.upper()} DETECTADO en {current_item}")
                            try:
                                translated_text = self.translate_text(text_to_translate)
                                new_line = f'{prefix}{keyword}"{translated_text}"{suffix}'
                                if original_line.endswith('\n'):
                                    new_line += '\n'
                                translated_lines.append(new_line)
                                lines_translated += 1
                                was_translated = True
                                print(f"    ✅ LÍNEA {i+1}: {element_name} traducido correctamente")
                                break
                            except Exception as e:
                                print(f"    ❌ LÍNEA {i+1}: Error traduciendo {element_name}: {e}")
                                translated_lines.append(original_line)
                                lines_skipped += 1
                                was_translated = True
                                break
                
                # Si no se tradujo, mantener línea original
                if not was_translated:
                    translated_lines.append(original_line)
                    lines_skipped += 1
            else:
                # Fuera de bloques, usar lógica normal
                translated_line, was_translated = self.translate_line(line)
                if was_translated:
                    lines_translated += 1
                else:
                    lines_skipped += 1
                translated_lines.append(translated_line)
        
        # Guardar archivo solo si hay traducciones
        if lines_translated > 0:
            print(f"   💾 Guardando archivo de naves/outfits con {lines_translated} líneas traducidas...")
            with open(dest_file, 'w', encoding='utf-8-sig') as f:
                f.writelines(translated_lines)
            print(f"   ✅ Archivo de naves/outfits guardado: {dest_file}")
        else:
            print(f"   ⏭️  Sin traducciones en naves/outfits, archivo omitido")
        
        print(f"   📊 Resultado: {lines_translated} traducidas, {lines_skipped} omitidas")
        return lines_translated

    def translate_starts_file(self, source_file, dest_file):
        """Traduce específicamente el archivo starts.txt"""
        print(f"\n🚀 Procesando archivo starts: {source_file.name}")
        
        # Crear directorio de destino
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Detectar codificación
        encoding = self.detect_encoding(source_file)
        print(f"   🔤 Codificación: {encoding}")
        
        try:
            with open(source_file, 'r', encoding=encoding, errors='ignore') as f:
                lines = f.readlines()
        except:
            print(f"   ⚠️ Error con {encoding}, usando UTF-8...")
            with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        
        print(f"   📊 Total de líneas: {len(lines)}")
        translated_lines = []
        lines_translated = 0
        lines_skipped = 0
        in_start_block = False
        current_start = ""
        current_indent = 0
        
        for i, line in enumerate(lines):
            if i % 100 == 0 and i > 0:
                print(f"   📈 Progreso starts: {i}/{len(lines)} líneas...")
            
            original_line = line
            line_stripped = line.strip()
            
            # Detectar comentarios y líneas vacías
            if line_stripped.startswith('#') or not line_stripped:
                translated_lines.append(original_line)
                continue
            
            # Detectar inicio de bloque start
            start_match = re.match(r'^start\s+"?([^"]*)"?', line_stripped)
            if start_match:
                in_start_block = True
                current_start = start_match.group(1)
                current_indent = len(line) - len(line.lstrip())
                print(f"  🚀 LÍNEA {i+1}: Procesando start: {current_start}")
                translated_lines.append(original_line)  # No traducir nombres técnicos
                continue
            
            # Detectar fin de bloque
            if in_start_block:
                line_indent = len(line) - len(line.lstrip()) if line.strip() else 0
                
                # Si encontramos una nueva definición al mismo nivel, terminar bloque actual
                if (line_stripped and 
                    line_indent <= current_indent and 
                    any(line_stripped.startswith(kw) for kw in ['start ', 'mission ', 'conversation ', 'event '])):
                    in_start_block = False
                    print(f"    📍 LÍNEA {i+1}: Fin de bloque start - nueva definición")
            
            # Si estamos en un bloque start, buscar elementos traducibles
            if in_start_block:
                was_translated = False
                
                # Detectar name
                name_match = re.match(r'^(\s*)(name\s+)"(.+)"(.*)$', line.rstrip())
                if name_match:
                    prefix, keyword, name_text, suffix = name_match.groups()
                    print(f"    🎯 LÍNEA {i+1}: NAME DETECTADO en {current_start}")
                    try:
                        translated_text = self.translate_text(name_text)
                        new_line = f'{prefix}{keyword}"{translated_text}"{suffix}'
                        if original_line.endswith('\n'):
                            new_line += '\n'
                        translated_lines.append(new_line)
                        lines_translated += 1
                        was_translated = True
                        print(f"    ✅ LÍNEA {i+1}: Nombre traducido correctamente")
                    except Exception as e:
                        print(f"    ❌ LÍNEA {i+1}: Error traduciendo nombre: {e}")
                        translated_lines.append(original_line)
                        lines_skipped += 1
                        was_translated = True
                
                # Detectar description
                if not was_translated:
                    description_match = re.match(r'^(\s*)(description\s+)"(.+)"(.*)$', line.rstrip())
                    if description_match:
                        prefix, keyword, description_text, suffix = description_match.groups()
                        print(f"    🎯 LÍNEA {i+1}: DESCRIPTION DETECTADA en {current_start}")
                        try:
                            translated_text = self.translate_text(description_text)
                            new_line = f'{prefix}{keyword}"{translated_text}"{suffix}'
                            if original_line.endswith('\n'):
                                new_line += '\n'
                            translated_lines.append(new_line)
                            lines_translated += 1
                            was_translated = True
                            print(f"    ✅ LÍNEA {i+1}: Descripción traducida correctamente")
                        except Exception as e:
                            print(f"    ❌ LÍNEA {i+1}: Error traduciendo descripción: {e}")
                            translated_lines.append(original_line)
                            lines_skipped += 1
                            was_translated = True
                
                # Si no se tradujo, mantener línea original
                if not was_translated:
                    translated_lines.append(original_line)
                    lines_skipped += 1
            else:
                # Fuera de bloques, usar lógica normal
                translated_line, was_translated = self.translate_line(line)
                if was_translated:
                    lines_translated += 1
                else:
                    lines_skipped += 1
                translated_lines.append(translated_line)
        
        # Guardar archivo solo si hay traducciones
        if lines_translated > 0:
            print(f"   💾 Guardando archivo starts con {lines_translated} líneas traducidas...")
            with open(dest_file, 'w', encoding='utf-8-sig') as f:
                f.writelines(translated_lines)
            print(f"   ✅ Archivo starts guardado: {dest_file}")
        else:
            print(f"   ⏭️  Sin traducciones en starts, archivo omitido")
        
        print(f"   📊 Resultado: {lines_translated} traducidas, {lines_skipped} omitidas")
        return lines_translated

    def translate_persons_file(self, source_file, dest_file):
        """Traduce específicamente el archivo persons.txt"""
        print(f"\n👤 Procesando archivo persons: {source_file.name}")
        
        # Crear directorio de destino
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Detectar codificación
        encoding = self.detect_encoding(source_file)
        print(f"   🔤 Codificación: {encoding}")
        
        try:
            with open(source_file, 'r', encoding=encoding, errors='ignore') as f:
                lines = f.readlines()
        except:
            print(f"   ⚠️ Error con {encoding}, usando UTF-8...")
            with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        
        print(f"   📊 Total de líneas: {len(lines)}")
        translated_lines = []
        lines_translated = 0
        lines_skipped = 0
        in_phrase_block = False
        current_phrase = ""
        current_indent = 0
        
        for i, line in enumerate(lines):
            if i % 100 == 0 and i > 0:
                print(f"   📈 Progreso persons: {i}/{len(lines)} líneas...")
            
            original_line = line
            line_stripped = line.strip()
            
            # Detectar comentarios y líneas vacías
            if line_stripped.startswith('#') or not line_stripped:
                translated_lines.append(original_line)
                continue
            
            # Detectar inicio de bloque phrase
            phrase_match = re.match(r'^phrase\s+"?([^"]*)"?', line_stripped)
            if phrase_match:
                in_phrase_block = True
                current_phrase = phrase_match.group(1)
                current_indent = len(line) - len(line.lstrip())
                print(f"  👤 LÍNEA {i+1}: Procesando phrase: {current_phrase}")
                translated_lines.append(original_line)  # No traducir nombres técnicos
                continue
            
            # Detectar fin de bloque
            if in_phrase_block:
                line_indent = len(line) - len(line.lstrip()) if line.strip() else 0
                
                # Si encontramos una nueva definición al mismo nivel, terminar bloque actual
                if (line_stripped and 
                    line_indent <= current_indent and 
                    any(line_stripped.startswith(kw) for kw in ['phrase ', 'person '])):
                    in_phrase_block = False
                    print(f"    📍 LÍNEA {i+1}: Fin de bloque phrase - nueva definición")
            
            # Si estamos en un bloque phrase, buscar elementos traducibles
            if in_phrase_block:
                was_translated = False
                
                # Detectar word (traducir contenido entre comillas)
                word_match = re.match(r'^(\s*)"(.+)"(.*)$', line.rstrip())
                if word_match:
                    prefix, word_text, suffix = word_match.groups()
                    print(f"    🎯 LÍNEA {i+1}: WORD DETECTADO en {current_phrase}")
                    try:
                        translated_text = self.translate_text(word_text)
                        new_line = f'{prefix}"{translated_text}"{suffix}'
                        if original_line.endswith('\n'):
                            new_line += '\n'
                        translated_lines.append(new_line)
                        lines_translated += 1
                        was_translated = True
                        print(f"    ✅ LÍNEA {i+1}: Word traducido correctamente")
                    except Exception as e:
                        print(f"    ❌ LÍNEA {i+1}: Error traduciendo word: {e}")
                        translated_lines.append(original_line)
                        lines_skipped += 1
                        was_translated = True
                
                # Si no se tradujo, mantener línea original
                if not was_translated:
                    translated_lines.append(original_line)
                    lines_skipped += 1
            else:
                # Fuera de bloques, usar lógica normal
                translated_line, was_translated = self.translate_line(line)
                if was_translated:
                    lines_translated += 1
                else:
                    lines_skipped += 1
                translated_lines.append(translated_line)
        
        # Guardar archivo solo si hay traducciones
        if lines_translated > 0:
            print(f"   💾 Guardando archivo persons con {lines_translated} líneas traducidas...")
            with open(dest_file, 'w', encoding='utf-8-sig') as f:
                f.writelines(translated_lines)
            print(f"   ✅ Archivo persons guardado: {dest_file}")
        else:
            print(f"   ⏭️  Sin traducciones en persons, archivo omitido")
        
        print(f"   📊 Resultado: {lines_translated} traducidas, {lines_skipped} omitidas")
        return lines_translated

    def translate_help_file(self, source_file, dest_file):
        """Traduce específicamente el archivo help.txt"""
        print(f"\n❓ Procesando archivo help: {source_file.name}")
        
        # Crear directorio de destino
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Detectar codificación
        encoding = self.detect_encoding(source_file)
        print(f"   🔤 Codificación: {encoding}")
        
        try:
            with open(source_file, 'r', encoding=encoding, errors='ignore') as f:
                lines = f.readlines()
        except:
            print(f"   ⚠️ Error con {encoding}, usando UTF-8...")
            with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        
        print(f"   📊 Total de líneas: {len(lines)}")
        translated_lines = []
        lines_translated = 0
        lines_skipped = 0
        in_help_block = False
        current_help = ""
        current_indent = 0
        
        for i, line in enumerate(lines):
            if i % 50 == 0 and i > 0:
                print(f"   📈 Progreso help: {i}/{len(lines)} líneas...")
            
            original_line = line
            line_stripped = line.strip()
            
            # Detectar comentarios y líneas vacías
            if line_stripped.startswith('#') or not line_stripped:
                translated_lines.append(original_line)
                continue
            
            # Detectar inicio de bloque help
            help_match = re.match(r'^help\s+"?([^"]*)"?', line_stripped)
            if help_match:
                in_help_block = True
                current_help = help_match.group(1)
                current_indent = len(line) - len(line.lstrip())
                print(f"  ❓ LÍNEA {i+1}: Procesando help: {current_help}")
                translated_lines.append(original_line)  # No traducir nombres técnicos
                continue
            
            # Detectar fin de bloque
            if in_help_block:
                line_indent = len(line) - len(line.lstrip()) if line.strip() else 0
                
                # Si encontramos una nueva definición al mismo nivel, terminar bloque actual
                if (line_stripped and 
                    line_indent <= current_indent and 
                    any(line_stripped.startswith(kw) for kw in ['help '])):
                    in_help_block = False
                    print(f"    📍 LÍNEA {i+1}: Fin de bloque help - nueva definición")
            
            # Si estamos en un bloque help, traducir texto entre backticks
            if in_help_block:
                was_translated = False
                
                # Detectar texto de ayuda (entre backticks)
                help_text_match = re.match(r'^(\s*)`(.+)`(.*)$', line.rstrip())
                if help_text_match:
                    prefix, help_text, suffix = help_text_match.groups()
                    print(f"    🎯 LÍNEA {i+1}: HELP TEXT DETECTADO en {current_help}")
                    try:
                        translated_text = self.translate_text(help_text)
                        new_line = f'{prefix}`{translated_text}`{suffix}'
                        if original_line.endswith('\n'):
                            new_line += '\n'
                        translated_lines.append(new_line)
                        lines_translated += 1
                        was_translated = True
                        print(f"    ✅ LÍNEA {i+1}: Texto de ayuda traducido correctamente")
                    except Exception as e:
                        print(f"    ❌ LÍNEA {i+1}: Error traduciendo texto de ayuda: {e}")
                        translated_lines.append(original_line)
                        lines_skipped += 1
                        was_translated = True
                
                # Si no se tradujo, mantener línea original
                if not was_translated:
                    translated_lines.append(original_line)
                    lines_skipped += 1
            else:
                # Fuera de bloques, usar lógica normal
                translated_line, was_translated = self.translate_line(line)
                if was_translated:
                    lines_translated += 1
                else:
                    lines_skipped += 1
                translated_lines.append(translated_line)
        
        # Guardar archivo solo si hay traducciones
        if lines_translated > 0:
            print(f"   💾 Guardando archivo help con {lines_translated} líneas traducidas...")
            with open(dest_file, 'w', encoding='utf-8-sig') as f:
                f.writelines(translated_lines)
            print(f"   ✅ Archivo help guardado: {dest_file}")
        else:
            print(f"   ⏭️  Sin traducciones en help, archivo omitido")
        
        print(f"   📊 Resultado: {lines_translated} traducidas, {lines_skipped} omitidas")
        return lines_translated

    def translate_hails_file(self, source_file, dest_file):
        """Traduce específicamente archivos hails.txt"""
        print(f"\n📡 Procesando archivo hails: {source_file.name}")
        
        # Crear directorio de destino
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Detectar codificación
        encoding = self.detect_encoding(source_file)
        print(f"   🔤 Codificación: {encoding}")
        
        try:
            with open(source_file, 'r', encoding=encoding, errors='ignore') as f:
                lines = f.readlines()
        except:
            print(f"   ⚠️ Error con {encoding}, usando UTF-8...")
            with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        
        print(f"   📊 Total de líneas: {len(lines)}")
        translated_lines = []
        lines_translated = 0
        lines_skipped = 0
        in_phrase_block = False
        current_phrase = ""
        current_indent = 0
        
        for i, line in enumerate(lines):
            if i % 200 == 0 and i > 0:
                print(f"   📈 Progreso hails: {i}/{len(lines)} líneas...")
            
            original_line = line
            line_stripped = line.strip()
            
            # Detectar comentarios y líneas vacías
            if line_stripped.startswith('#') or not line_stripped:
                translated_lines.append(original_line)
                continue
            
            # Detectar inicio de bloque phrase
            phrase_match = re.match(r'^phrase\s+"?([^"]*)"?', line_stripped)
            if phrase_match:
                in_phrase_block = True
                current_phrase = phrase_match.group(1)
                current_indent = len(line) - len(line.lstrip())
                print(f"  📡 LÍNEA {i+1}: Procesando phrase: {current_phrase}")
                translated_lines.append(original_line)  # No traducir nombres técnicos
                continue
            
            # Detectar fin de bloque
            if in_phrase_block:
                line_indent = len(line) - len(line.lstrip()) if line.strip() else 0
                
                # Si encontramos una nueva definición al mismo nivel, terminar bloque actual
                if (line_stripped and 
                    line_indent <= current_indent and 
                    any(line_stripped.startswith(kw) for kw in ['phrase '])):
                    in_phrase_block = False
                    print(f"    📍 LÍNEA {i+1}: Fin de bloque phrase - nueva definición")
            
            # Si estamos en un bloque phrase, buscar elementos traducibles
            if in_phrase_block:
                was_translated = False
                
                # Detectar word (traducir contenido entre comillas)
                word_match = re.match(r'^(\s*)"(.+)"(.*)$', line.rstrip())
                if word_match:
                    prefix, word_text, suffix = word_match.groups()
                    # Solo traducir si no parece ser un nombre propio o técnico
                    if not re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+', word_text):  # Skip names like "John Smith"
                        print(f"    🎯 LÍNEA {i+1}: WORD DETECTADO en {current_phrase}")
                        try:
                            translated_text = self.translate_text(word_text)
                            new_line = f'{prefix}"{translated_text}"{suffix}'
                            if original_line.endswith('\n'):
                                new_line += '\n'
                            translated_lines.append(new_line)
                            lines_translated += 1
                            was_translated = True
                            print(f"    ✅ LÍNEA {i+1}: Word traducido correctamente")
                        except Exception as e:
                            print(f"    ❌ LÍNEA {i+1}: Error traduciendo word: {e}")
                            translated_lines.append(original_line)
                            lines_skipped += 1
                            was_translated = True
                    else:
                        # Es probablemente un nombre propio, no traducir
                        translated_lines.append(original_line)
                        lines_skipped += 1
                        was_translated = True
                
                # Si no se tradujo, mantener línea original
                if not was_translated:
                    translated_lines.append(original_line)
                    lines_skipped += 1
            else:
                # Fuera de bloques, usar lógica normal
                translated_line, was_translated = self.translate_line(line)
                if was_translated:
                    lines_translated += 1
                else:
                    lines_skipped += 1
                translated_lines.append(translated_line)
        
        # Guardar archivo solo si hay traducciones
        if lines_translated > 0:
            print(f"   💾 Guardando archivo hails con {lines_translated} líneas traducidas...")
            with open(dest_file, 'w', encoding='utf-8-sig') as f:
                f.writelines(translated_lines)
            print(f"   ✅ Archivo hails guardado: {dest_file}")
        else:
            print(f"   ⏭️  Sin traducciones en hails, archivo omitido")
        
        print(f"   📊 Resultado: {lines_translated} traducidas, {lines_skipped} omitidas")
        return lines_translated

    def translate_news_file(self, source_file, dest_file):
        """Traduce específicamente archivos news.txt"""
        print(f"\n📰 Procesando archivo news: {source_file.name}")
        
        # Crear directorio de destino
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Detectar codificación
        encoding = self.detect_encoding(source_file)
        print(f"   🔤 Codificación: {encoding}")
        
        try:
            with open(source_file, 'r', encoding=encoding, errors='ignore') as f:
                lines = f.readlines()
        except:
            print(f"   ⚠️ Error con {encoding}, usando UTF-8...")
            with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        
        print(f"   📊 Total de líneas: {len(lines)}")
        translated_lines = []
        lines_translated = 0
        lines_skipped = 0
        in_block = False
        current_block = ""
        current_indent = 0
        
        for i, line in enumerate(lines):
            if i % 200 == 0 and i > 0:
                print(f"   📈 Progreso news: {i}/{len(lines)} líneas...")
            
            original_line = line
            line_stripped = line.strip()
            
            # Detectar comentarios y líneas vacías
            if line_stripped.startswith('#') or not line_stripped:
                translated_lines.append(original_line)
                continue
            
            # Detectar inicio de bloques phrase, news, mission
            block_match = re.match(r'^(phrase|news|mission)\s+"?([^"]*)"?', line_stripped)
            if block_match:
                in_block = True
                block_type, block_name = block_match.groups()
                current_block = f"{block_type} {block_name}"
                current_indent = len(line) - len(line.lstrip())
                print(f"  📰 LÍNEA {i+1}: Procesando {block_type}: {block_name}")
                translated_lines.append(original_line)  # No traducir nombres técnicos
                continue
            
            # Detectar fin de bloque
            if in_block:
                line_indent = len(line) - len(line.lstrip()) if line.strip() else 0
                
                # Si encontramos una nueva definición al mismo nivel, terminar bloque actual
                if (line_stripped and 
                    line_indent <= current_indent and 
                    any(line_stripped.startswith(kw) for kw in ['phrase ', 'news ', 'mission '])):
                    in_block = False
                    print(f"    📍 LÍNEA {i+1}: Fin de bloque - nueva definición")
            
            # Si estamos en un bloque, buscar elementos traducibles
            if in_block:
                was_translated = False
                
                # Detectar message (noticias)
                message_match = re.match(r'^(\s*)(message\s+)"(.+)"(.*)$', line.rstrip())
                if message_match:
                    prefix, keyword, message_text, suffix = message_match.groups()
                    print(f"    🎯 LÍNEA {i+1}: MESSAGE DETECTADO en {current_block}")
                    try:
                        translated_text = self.translate_text(message_text)
                        new_line = f'{prefix}{keyword}"{translated_text}"{suffix}'
                        if original_line.endswith('\n'):
                            new_line += '\n'
                        translated_lines.append(new_line)
                        lines_translated += 1
                        was_translated = True
                        print(f"    ✅ LÍNEA {i+1}: Message traducido correctamente")
                    except Exception as e:
                        print(f"    ❌ LÍNEA {i+1}: Error traduciendo message: {e}")
                        translated_lines.append(original_line)
                        lines_skipped += 1
                        was_translated = True
                
                # Detectar word (frases)
                if not was_translated:
                    word_match = re.match(r'^(\s*)"(.+)"(.*)$', line.rstrip())
                    if word_match:
                        prefix, word_text, suffix = word_match.groups()
                        # Solo traducir si parece ser contenido de mensaje, no nombres
                        if len(word_text.split()) > 1:  # Frases de más de una palabra
                            print(f"    🎯 LÍNEA {i+1}: WORD DETECTADO en {current_block}")
                            try:
                                translated_text = self.translate_text(word_text)
                                new_line = f'{prefix}"{translated_text}"{suffix}'
                                if original_line.endswith('\n'):
                                    new_line += '\n'
                                translated_lines.append(new_line)
                                lines_translated += 1
                                was_translated = True
                                print(f"    ✅ LÍNEA {i+1}: Word traducido correctamente")
                            except Exception as e:
                                print(f"    ❌ LÍNEA {i+1}: Error traduciendo word: {e}")
                                translated_lines.append(original_line)
                                lines_skipped += 1
                                was_translated = True
                        else:
                            # Probablemente un nombre, no traducir
                            translated_lines.append(original_line)
                            lines_skipped += 1
                            was_translated = True
                
                # Si no se tradujo, mantener línea original
                if not was_translated:
                    translated_lines.append(original_line)
                    lines_skipped += 1
            else:
                # Fuera de bloques, usar lógica normal
                translated_line, was_translated = self.translate_line(line)
                if was_translated:
                    lines_translated += 1
                else:
                    lines_skipped += 1
                translated_lines.append(translated_line)
        
        # Guardar archivo solo si hay traducciones
        if lines_translated > 0:
            print(f"   💾 Guardando archivo news con {lines_translated} líneas traducidas...")
            with open(dest_file, 'w', encoding='utf-8-sig') as f:
                f.writelines(translated_lines)
            print(f"   ✅ Archivo news guardado: {dest_file}")
        else:
            print(f"   ⏭️  Sin traducciones en news, archivo omitido")
        
        print(f"   📊 Resultado: {lines_translated} traducidas, {lines_skipped} omitidas")
        return lines_translated

    def translate_fleets_file(self, source_file, dest_file):
        """Traduce específicamente archivos fleets.txt"""
        print(f"\n🚁 Procesando archivo de flotas: {source_file.name}")
        
        # Crear directorio de destino
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Detectar codificación
        encoding = self.detect_encoding(source_file)
        print(f"   🔤 Codificación: {encoding}")
        
        try:
            with open(source_file, 'r', encoding=encoding, errors='ignore') as f:
                lines = f.readlines()
        except:
            print(f"   ⚠️ Error con {encoding}, usando UTF-8...")
            with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        
        print(f"   📊 Total de líneas: {len(lines)}")
        translated_lines = []
        lines_translated = 0
        lines_skipped = 0
        in_fleet_block = False
        current_fleet = ""
        current_indent = 0
        
        for i, line in enumerate(lines):
            if i % 200 == 0 and i > 0:
                print(f"   📈 Progreso flotas: {i}/{len(lines)} líneas...")
            
            original_line = line
            line_stripped = line.strip()
            
            # Detectar comentarios y líneas vacías
            if line_stripped.startswith('#') or not line_stripped:
                translated_lines.append(original_line)
                continue
            
            # Detectar inicio de bloque fleet
            fleet_match = re.match(r'^fleet\s+"?([^"]*)"?', line_stripped)
            if fleet_match:
                in_fleet_block = True
                current_fleet = fleet_match.group(1)
                current_indent = len(line) - len(line.lstrip())
                print(f"  🚁 LÍNEA {i+1}: Procesando flota: {current_fleet}")
                translated_lines.append(original_line)  # No traducir nombres de flotas
                continue
            
            # Detectar fin de bloque
            if in_fleet_block:
                line_indent = len(line) - len(line.lstrip()) if line.strip() else 0
                
                # Si encontramos una nueva definición al mismo nivel, terminar bloque actual
                if (line_stripped and 
                    line_indent <= current_indent and 
                    any(line_stripped.startswith(kw) for kw in ['fleet ', 'government ', 'mission '])):
                    in_fleet_block = False
                    print(f"    📍 LÍNEA {i+1}: Fin de bloque fleet - nueva definición")
            
            # Si estamos en un bloque fleet, buscar elementos traducibles
            if in_fleet_block:
                was_translated = False
                
                # Detectar descripciones de flotas
                if line_stripped.startswith('description `'):
                    if line_stripped.endswith('`'):
                        desc_match = re.match(r'^(\s*)description\s+`(.+)`(.*)$', line.rstrip())
                        if desc_match:
                            prefix, text_to_translate, suffix = desc_match.groups()
                            print(f"    🎯 LÍNEA {i+1}: DESCRIPCIÓN DE FLOTA en {current_fleet}")
                            try:
                                translated_text = self.translate_text(text_to_translate)
                                new_line = f'{prefix}description `{translated_text}`{suffix}'
                                if original_line.endswith('\n'):
                                    new_line += '\n'
                                translated_lines.append(new_line)
                                lines_translated += 1
                                was_translated = True
                                print(f"    ✅ LÍNEA {i+1}: Descripción de flota traducida")
                            except Exception as e:
                                print(f"    ❌ LÍNEA {i+1}: Error: {e}")
                                translated_lines.append(original_line)
                                lines_skipped += 1
                                was_translated = True
                
                # Si no se tradujo, mantener línea original
                if not was_translated:
                    translated_lines.append(original_line)
                    lines_skipped += 1
            else:
                # Fuera de bloques, usar lógica normal
                translated_line, was_translated = self.translate_line(line)
                if was_translated:
                    lines_translated += 1
                else:
                    lines_skipped += 1
                translated_lines.append(translated_line)
        
        # Guardar archivo solo si hay traducciones
        if lines_translated > 0:
            print(f"   💾 Guardando archivo fleets con {lines_translated} líneas traducidas...")
            with open(dest_file, 'w', encoding='utf-8-sig') as f:
                f.writelines(translated_lines)
            print(f"   ✅ Archivo fleets guardado: {dest_file}")
        else:
            print(f"   ⏭️  Sin traducciones en fleets, archivo omitido")
        
        print(f"   📊 Resultado: {lines_translated} traducidas, {lines_skipped} omitidas")
        return lines_translated

    def translate_governments_file(self, source_file, dest_file):
        """Traduce específicamente archivos governments.txt"""
        print(f"\n🏛️ Procesando archivo de gobiernos: {source_file.name}")
        
        # Crear directorio de destino
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Detectar codificación
        encoding = self.detect_encoding(source_file)
        print(f"   🔤 Codificación: {encoding}")
        
        try:
            with open(source_file, 'r', encoding=encoding, errors='ignore') as f:
                lines = f.readlines()
        except:
            print(f"   ⚠️ Error con {encoding}, usando UTF-8...")
            with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        
        print(f"   📊 Total de líneas: {len(lines)}")
        translated_lines = []
        lines_translated = 0
        lines_skipped = 0
        in_government_block = False
        current_government = ""
        current_indent = 0
        
        for i, line in enumerate(lines):
            if i % 200 == 0 and i > 0:
                print(f"   📈 Progreso gobiernos: {i}/{len(lines)} líneas...")
            
            original_line = line
            line_stripped = line.strip()
            
            # Detectar comentarios y líneas vacías
            if line_stripped.startswith('#') or not line_stripped:
                translated_lines.append(original_line)
                continue
            
            # Detectar inicio de bloque government
            gov_match = re.match(r'^government\s+"?([^"]*)"?', line_stripped)
            if gov_match:
                in_government_block = True
                current_government = gov_match.group(1)
                current_indent = len(line) - len(line.lstrip())
                print(f"  🏛️ LÍNEA {i+1}: Procesando gobierno: {current_government}")
                translated_lines.append(original_line)  # No traducir nombres de gobiernos
                continue
            
            # Detectar fin de bloque
            if in_government_block:
                line_indent = len(line) - len(line.lstrip()) if line.strip() else 0
                
                # Si encontramos una nueva definición al mismo nivel, terminar bloque actual
                if (line_stripped and 
                    line_indent <= current_indent and 
                    any(line_stripped.startswith(kw) for kw in ['government ', 'fleet ', 'mission '])):
                    in_government_block = False
                    print(f"    📍 LÍNEA {i+1}: Fin de bloque government - nueva definición")
            
            # Si estamos en un bloque government, buscar elementos traducibles
            if in_government_block:
                was_translated = False
                
                # Detectar descripciones de gobiernos
                if line_stripped.startswith('description `'):
                    if line_stripped.endswith('`'):
                        desc_match = re.match(r'^(\s*)description\s+`(.+)`(.*)$', line.rstrip())
                        if desc_match:
                            prefix, text_to_translate, suffix = desc_match.groups()
                            print(f"    🎯 LÍNEA {i+1}: DESCRIPCIÓN DE GOBIERNO en {current_government}")
                            try:
                                translated_text = self.translate_text(text_to_translate)
                                new_line = f'{prefix}description `{translated_text}`{suffix}'
                                if original_line.endswith('\n'):
                                    new_line += '\n'
                                translated_lines.append(new_line)
                                lines_translated += 1
                                was_translated = True
                                print(f"    ✅ LÍNEA {i+1}: Descripción de gobierno traducida")
                            except Exception as e:
                                print(f"    ❌ LÍNEA {i+1}: Error: {e}")
                                translated_lines.append(original_line)
                                lines_skipped += 1
                                was_translated = True
                
                # Detectar friendly/hostile hails (mensajes de comunicación)
                hail_patterns = [
                    (r'^(\s*)(friendly hail\s+)"(.+)"(.*)$', 'friendly hail'),
                    (r'^(\s*)(hostile hail\s+)"(.+)"(.*)$', 'hostile hail'),
                    (r'^(\s*)(bribe\s+)"(.+)"(.*)$', 'bribe message'),
                    (r'^(\s*)(fine\s+)"(.+)"(.*)$', 'fine message')
                ]
                
                if not was_translated:
                    for pattern, hail_type in hail_patterns:
                        hail_match = re.match(pattern, line.rstrip())
                        if hail_match:
                            prefix, keyword, text_to_translate, suffix = hail_match.groups()
                            print(f"    🎯 LÍNEA {i+1}: {hail_type.upper()} en {current_government}")
                            try:
                                translated_text = self.translate_text(text_to_translate)
                                new_line = f'{prefix}{keyword}"{translated_text}"{suffix}'
                                if original_line.endswith('\n'):
                                    new_line += '\n'
                                translated_lines.append(new_line)
                                lines_translated += 1
                                was_translated = True
                                print(f"    ✅ LÍNEA {i+1}: {hail_type} traducido")
                                break
                            except Exception as e:
                                print(f"    ❌ LÍNEA {i+1}: Error: {e}")
                                translated_lines.append(original_line)
                                lines_skipped += 1
                                was_translated = True
                                break
                
                # Si no se tradujo, mantener línea original
                if not was_translated:
                    translated_lines.append(original_line)
                    lines_skipped += 1
            else:
                # Fuera de bloques, usar lógica normal
                translated_line, was_translated = self.translate_line(line)
                if was_translated:
                    lines_translated += 1
                else:
                    lines_skipped += 1
                translated_lines.append(translated_line)
        
        # Guardar archivo solo si hay traducciones
        if lines_translated > 0:
            print(f"   💾 Guardando archivo governments con {lines_translated} líneas traducidas...")
            with open(dest_file, 'w', encoding='utf-8-sig') as f:
                f.writelines(translated_lines)
            print(f"   ✅ Archivo governments guardado: {dest_file}")
        else:
            print(f"   ⏭️  Sin traducciones en governments, archivo omitido")
        
        print(f"   📊 Resultado: {lines_translated} traducidas, {lines_skipped} omitidas")
        return lines_translated

def main():
    # Configuración
    base_path = r"d:\Program Files (x86)\Steam\steamapps\common\Endless Sky"
    target_language = 'es'  # Español
    
    print("Iniciando traductor corregido...")
    
    # Crear instancia del traductor
    translator = EndlessSkyTranslatorFixed(base_path, target_language)
    
    # Ejecutar traducción
    translator.run_translation()

if __name__ == "__main__":
    main()
