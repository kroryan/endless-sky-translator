#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interfaz Gráfica Mejorada para el Traductor de Endless Sky
GUI con checkboxes/ticks reales, filtrado preciso de archivos traducibles y selección intuitiva
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import os
import sys
from pathlib import Path
import json
import time
import re

# Importar el traductor principal y sistema de traducciones
try:
    from translator import EndlessSkyTranslatorFixed
    from translations import TranslationManager
except ImportError:
    # Si estamos ejecutando desde otro directorio
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from translator import EndlessSkyTranslatorFixed
    from translations import TranslationManager

class FileItem:
    """Representa un archivo o carpeta con estado de checkbox"""
    def __init__(self, name, path, item_type, status, translatable=True, parent=None):
        self.name = name
        self.path = path
        self.item_type = item_type  # 'file', 'folder', 'root'
        self.status = status        # Estado de seguridad
        self.translatable = translatable
        self.selected = tk.BooleanVar()
        self.parent = parent        # Para archivos dentro de carpetas
        self.files = []            # Para carpetas, lista de archivos
        self.expanded = False      # Si la carpeta está expandida

class TranslatorGUIImproved:
    def __init__(self, root):
        self.root = root
        # Initialize translation manager
        self.translation_manager = TranslationManager('en')  # Default to English
        
        self.root.title(self.translation_manager.get('window_title'))
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Variables
        self.endless_sky_path = tk.StringVar()
        self.target_language = tk.StringVar(value='es')
        self.translator = None
        self.translation_thread = None
        self.translation_queue = queue.Queue()
        self.is_translating = False
        
        # Lista de elementos (archivos y carpetas) con checkboxes
        self.all_items = []  # Lista plana de todos los elementos para facilitar búsquedas
        
        # Configuración por defecto
        self.config_file = "translator_config.json"
        self.load_config()
        
        # Crear interfaz
        self.create_widgets()
        self.scan_translatable_items()
        
        # Iniciar verificación de cola de mensajes
        self.check_queue()
    
    def create_widgets(self):
        """Creates all interface widgets"""
        
        # Main frame with notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Configuration
        self.config_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.config_frame, text=self.translation_manager.get('config_tab'))
        
        # Tab 2: File selection with checkboxes
        self.selection_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.selection_frame, text=self.translation_manager.get('selection_tab'))
        
        # Tab 3: Translation and Progress
        self.progress_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.progress_frame, text=self.translation_manager.get('translation_tab'))
        
        self.create_config_tab()
        self.create_selection_tab()
        self.create_progress_tab()
    
    def create_config_tab(self):
        """Creates the configuration tab"""
        
        # Title
        title_label = tk.Label(self.config_frame, text=self.translation_manager.get('config_title'), 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Frame for Endless Sky directory
        dir_frame = ttk.LabelFrame(self.config_frame, text=self.translation_manager.get('endless_sky_dir'), padding=10)
        dir_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(dir_frame, text=self.translation_manager.get('select_directory')).pack(anchor=tk.W)
        
        dir_input_frame = ttk.Frame(dir_frame)
        dir_input_frame.pack(fill=tk.X, pady=5)
        
        self.dir_entry = ttk.Entry(dir_input_frame, textvariable=self.endless_sky_path, width=60)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(dir_input_frame, text=self.translation_manager.get('browse_button'), 
                  command=self.browse_directory).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Frame for language
        lang_frame = ttk.LabelFrame(self.config_frame, text=self.translation_manager.get('target_language'), padding=10)
        lang_frame.pack(fill=tk.X, padx=20, pady=10)
        
        languages = [
            ('es', 'Español'),
            ('fr', 'Francés'),
            ('de', 'Alemán'),
            ('it', 'Italiano'),
            ('pt', 'Portugués'),
            ('ru', 'Ruso'),
            ('zh', 'Chino'),
            ('ja', 'Japonés')
        ]
        
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.target_language, 
                                 values=[f"{code} - {name}" for code, name in languages],
                                 state="readonly")
        lang_combo.set("es - Español")
        lang_combo.pack(anchor=tk.W)
        
        # Información
        info_frame = ttk.LabelFrame(self.config_frame, text="ℹ️ Información", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        info_text = """
🎯 CARACTERÍSTICAS DE LA VERSIÓN MEJORADA:
• ☑️ Checkboxes reales para seleccionar archivos/carpetas
• 🎯 Solo muestra archivos REALMENTE traducibles
• 🛡️ Filtrado inteligente que evita archivos peligrosos
• 📊 Indicadores visuales de seguridad por colores
• 🚀 Traducción selectiva solo de contenido visible

🛡️ SEGURIDAD GARANTIZADA:
• ✅ VERDE: Archivos completamente seguros (misiones, diálogos)
• ⚙️ AMARILLO: Archivos especiales (ships, outfits) - solo descripciones  
• 🔒 NO SE MUESTRAN: Archivos peligrosos están ocultos

📋 ARCHIVOS QUE SE TRADUCEN:
• ✅ Misiones y conversaciones (missions, conversations)
• ✅ Descripciones de naves (ships.txt solo descripciones)
• ✅ Descripciones de outfits/engines/weapons (solo descriptions)
• ✅ Interfaz de usuario (_ui)
• ✅ Comunicaciones y noticias (hail, news)
• ✅ Diálogos de planetas (map planets.txt solo descripciones)

❌ NUNCA SE TRADUCEN:
• Nombres técnicos de naves, outfits o sistemas
• Archivos que afectan el gameplay (fleets, governments)
• Coordenadas, efectos y datos técnicos
        """
        
        info_label = tk.Label(info_frame, text=info_text, justify=tk.LEFT, 
                             font=("Courier", 9), bg="lightyellow")
        info_label.pack(fill=tk.BOTH, expand=True)
    
    def create_selection_tab(self):
        """Crea la pestaña de selección con checkboxes reales y estructura expandible"""
        
        # Título
        title_label = tk.Label(self.selection_frame, text="☑️ Selección Granular de Archivos", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Frame de botones de selección masiva
        button_frame = ttk.Frame(self.selection_frame)
        button_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Button(button_frame, text="☑️ Seleccionar Todo", 
                  command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="☐ Deseleccionar Todo", 
                  command=self.deselect_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🛡️ Solo Seguros", 
                  command=self.select_safe_only).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="⚙️ Incluir Especiales", 
                  command=self.select_with_special).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="� Expandir Todo", 
                  command=self.expand_all_folders).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📁 Contraer Todo", 
                  command=self.collapse_all_folders).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Actualizar", 
                  command=self.scan_translatable_items).pack(side=tk.RIGHT, padx=5)
        
        # Frame principal con estructura expandible
        main_frame = ttk.Frame(self.selection_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Crear frame con scroll para toda la estructura
        self.main_canvas = tk.Canvas(main_frame)
        self.main_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.main_canvas.yview)
        self.main_scrollable_frame = ttk.Frame(self.main_canvas)
        
        self.main_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        
        self.main_canvas.create_window((0, 0), window=self.main_scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)
        
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.main_scrollbar.pack(side="right", fill="y")
        
        # Información de selección
        info_frame = ttk.Frame(self.selection_frame)
        info_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.selection_info = tk.Label(info_frame, text="Escanea el directorio para ver archivos traducibles", 
                                      font=("Arial", 10), fg="blue")
        self.selection_info.pack()
    
    def create_progress_tab(self):
        """Crea la pestaña de progreso y traducción"""
        
        # Título
        title_label = tk.Label(self.progress_frame, text="🚀 Proceso de Traducción", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Frame de estado
        status_frame = ttk.LabelFrame(self.progress_frame, text="📊 Estado Actual", padding=10)
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.status_label = tk.Label(status_frame, text="⏸️ Listo para traducir", 
                                    font=("Arial", 12, "bold"), fg="blue")
        self.status_label.pack()
        
        # Barra de progreso
        self.progress_bar = ttk.Progressbar(status_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Frame de log
        log_frame = ttk.LabelFrame(self.progress_frame, text="📝 Log de Traducción", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, font=("Courier", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Botones de control
        control_frame = ttk.Frame(self.progress_frame)
        control_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.start_button = ttk.Button(control_frame, text="🚀 Iniciar Traducción", 
                                      command=self.start_translation, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="⏹️ Detener", 
                                     command=self.stop_translation, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="🗑️ Limpiar Log", 
                  command=self.clear_log).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="💾 Guardar Config", 
                  command=self.save_config).pack(side=tk.RIGHT, padx=5)
    
    def browse_directory(self):
        """Abre un diálogo para seleccionar el directorio de Endless Sky"""
        directory = filedialog.askdirectory(
            title="Seleccionar directorio de Endless Sky",
            initialdir=self.endless_sky_path.get() if self.endless_sky_path.get() else "C:\\"
        )
        if directory:
            self.endless_sky_path.set(directory)
            self.scan_translatable_items()
    
    def get_file_safety_info(self, filename):
        """Determina la información de seguridad de un archivo"""
        filename_lower = filename.lower()
        
        # Archivos completamente seguros (verde)
        safe_patterns = ['mission', 'conversation', 'dialog', 'hail', 'job', 'news', 'event', 'campaign', 'start', 'culture', 'help', 'boarding', 'names', 'phrase']
        if any(pattern in filename_lower for pattern in safe_patterns):
            return ("✅", "green", "Completamente seguro")
        
        # Archivos especiales con lógica particular (amarillo)
        special_files = ['ships.txt', 'outfits.txt', 'engines.txt', 'weapons.txt', 'power.txt', 'harvesting.txt', 'variants.txt']
        if filename_lower in special_files:
            return ("⚙️", "orange", "Solo descripciones")
        
        # Archivos raíz especiales
        if filename_lower in ['map planets.txt', 'dialog phrases.txt', 'starts.txt', 'persons.txt']:
            return ("🌟", "blue", "Archivo especial")
        
        # Archivos de facciones con frases/nombres (también seguros)
        if any(faction in filename_lower for faction in ['wanderers.txt', 'hai.txt', 'korath.txt']):
            return ("👥", "cyan", "Nombres de facción")
        
        # Archivos específicos de facciones seguros por patrón
        safe_faction_patterns = ['prologue', 'epilogue', 'middle', 'checkmate', 'reconciliation', 'reactions', 'side plots', 'war jobs']
        if any(pattern in filename_lower for pattern in safe_faction_patterns):
            return ("📖", "green", "Historia/campañas")
        
        # Archivos de trabajos por ubicación
        location_patterns = ['north', 'south', 'earth', 'belt', 'frontier', 'rim', 'paradise', 'syndicate', 'pirate', 'deep']
        if any(pattern in filename_lower for pattern in location_patterns) and 'job' in filename_lower:
            return ("💼", "blue", "Trabajos por región")
        
        # Archivos de personajes (frases traducibles)
        if filename_lower == 'persons.txt':
            return ("👤", "purple", "Frases de personajes")
        
        # Por defecto, revisar
        return ("⚠️", "gray", "Requiere revisión")
    
    def is_file_translatable(self, filepath):
        """Determina si un archivo realmente debe mostrarse como traducible"""
        filename = filepath.name.lower()
        
        # Lista específica de archivos que NUNCA deben aparecer
        excluded_files = [
            'fleets.txt', 'governments.txt', 'systems.txt', 'planets.txt',
            'map systems.txt', 'commodities.txt',
            'effects.txt', 'hazards.txt', 'formations.txt', 'stars.txt', 'series.txt',
            'derelicts.txt', 'minables.txt', 'wormhole.txt',
            'globals.txt', 'gamerules.txt', 'categories.txt',
            'map beyond patir.txt'
        ]
        
        if filename in excluded_files:
            return False
        
        # Patrones que NUNCA deben aparecer (pero no 'variant' porque algunos archivos variant son útiles)
        excluded_patterns = ['derelict', 'formation', 'hazard', 'fleet', 'government', 'system', 'rating', 'swizzle']
        if any(pattern in filename for pattern in excluded_patterns):
            # Excepción: si contiene ship, outfit, weapon, engine, harvesting sí queremos incluirlo
            equipment_exceptions = ['ship', 'outfit', 'weapon', 'engine', 'power', 'harvesting']
            if not any(eq in filename for eq in equipment_exceptions):
                return False
        
        # Archivos que SÍ queremos mostrar (contenido seguro)
        safe_patterns = ['mission', 'conversation', 'dialog', 'hail', 'job', 'news', 'event', 'campaign', 'culture', 'intro', 'side', 'start', 'harvesting', 'persons', 'help', 'boarding', 'names', 'phrase']
        if any(pattern in filename for pattern in safe_patterns):
            return True
        
        # Archivos de equipamiento que SÍ queremos (contienen descripciones traducibles)
        equipment_patterns = ['ship', 'outfit', 'weapon', 'engine', 'power']
        if any(pattern in filename for pattern in equipment_patterns):
            return True
        
        # Archivos raíz permitidos especiales
        root_files = ['map planets.txt', 'dialog phrases.txt', 'starts.txt', 'harvesting.txt', 'persons.txt']
        if filename in root_files:
            return True
        
        # Archivos UI permitidos
        ui_patterns = ['interface', 'tooltip', 'help', 'landing', 'flight']
        if any(pattern in filename for pattern in ui_patterns):
            return True
        
        # Archivos de trabajos por ubicación geográfica
        location_patterns = ['north', 'south', 'earth', 'belt', 'frontier', 'rim', 'paradise', 'syndicate', 'pirate', 'deep']
        if any(pattern in filename for pattern in location_patterns) and 'job' in filename:
            return True
        
        # Archivos específicos de facciones que también queremos
        faction_patterns = ['sales', 'boarding', 'marauder', 'kestrel', 'name', 'critter', 'elenchus', 'nanobots', 'windjammer', 'indigenous', 'archaeology', 'tace mesa', 'variant', 'prologue', 'epilogue', 'middle', 'checkmate', 'reconciliation', 'reactions', 'plots', 'reveal', 'war', 'reveal']
        if any(pattern in filename for pattern in faction_patterns):
            return True
        
        # Archivos que terminan en números seguidos de palabras (ej: "hai reveal 1 intro.txt")
        import re
        if re.search(r'\d+\s+\w+\.txt$', filename):
            return True
        
        # Archivos con nombres de facciones específicas
        faction_names = ['hai', 'korath', 'wanderer', 'remnant', 'pug', 'quarg', 'coalition', 'avgi', 'bunrodea', 'drak', 'gegno', 'iije', 'incipias', 'kahet', 'rulei', 'sheragi', 'successor', 'vyrmeid', 'aberrant', 'unfettered', 'heliarch', 'lunarium', 'wanderers']
        if any(faction in filename for faction in faction_names):
            return True
        
        # Si llegamos aquí, probablemente no es seguro mostrar el archivo
        return False
    
    def scan_translatable_items(self):
        """Scans and creates expandable structure with folders and individual files"""
        # Clear current structure
        for widget in self.main_scrollable_frame.winfo_children():
            widget.destroy()
        
        self.all_items.clear()
        
        base_path = self.endless_sky_path.get()
        if not base_path or not os.path.exists(base_path):
            self.selection_info.config(text="⚠️ Select a valid Endless Sky directory", fg="red")
            return
        
        data_path = Path(base_path) / "data"
        if not data_path.exists():
            self.selection_info.config(text="❌ 'data' folder not found in directory", fg="red")
            return
        
        total_items = 0
        
        # 1. Create root files section
        root_section = ttk.LabelFrame(self.main_scrollable_frame, text="📁 Root Files", padding=5)
        root_section.pack(fill=tk.X, padx=5, pady=2)
        
        # Scan ALL .txt files in data root directory
        root_files = []
        for file_path in data_path.glob("*.txt"):
            if self.is_file_translatable(file_path):
                root_files.append(file_path.name)
        
        for filename in sorted(root_files):
            file_path = data_path / filename
            if file_path.exists():
                safety_icon, color, description = self.get_file_safety_info(filename)
                item = FileItem(filename, file_path, 'file', safety_icon, True)
                self.all_items.append(item)
                self.create_file_checkbox_in_frame(root_section, item, color, description)
                total_items += 1
        
        # 2. Scan ALL subdirectories dynamically
        for folder_path in sorted(data_path.iterdir()):
            if folder_path.is_dir() and not folder_path.name.startswith('.'):
                # Scan translatable files in the folder
                translatable_files = []
                for file_path in folder_path.glob("*.txt"):
                    if self.is_file_translatable(file_path):
                        translatable_files.append(file_path.name)
                
                if translatable_files:  # Only create section if there are translatable files
                    folder_item = FileItem(folder_path.name, folder_path, 'folder', self.get_folder_status(folder_path.name))
                    folder_item.files = translatable_files
                    self.all_items.append(folder_item)
                    
                    # Create expandable section for the folder
                    self.create_folder_section(folder_item, folder_path)
                    total_items += 1 + len(translatable_files)
        
        # Update selection information
        self.selection_info.config(
            text=f"✅ Found {total_items} translatable elements (folders and individual files)",
            fg="green"
        )
        
        if total_items == 0:
            self.selection_info.config(text="⚠️ No translatable files found in this directory", fg="orange")
    
    def create_folder_section(self, folder_item, folder_path):
        """Crea una sección expandible para una carpeta"""
        # Frame principal de la carpeta
        folder_frame = ttk.LabelFrame(self.main_scrollable_frame, 
                                     text=f"📂 {folder_item.name} ({len(folder_item.files)} archivos)", 
                                     padding=5)
        folder_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Frame superior con checkbox de carpeta y botón expandir
        header_frame = ttk.Frame(folder_frame)
        header_frame.pack(fill=tk.X)
        
        # Checkbox principal de la carpeta
        folder_checkbox = ttk.Checkbutton(
            header_frame,
            text=f"{folder_item.status} Seleccionar toda la carpeta",
            variable=folder_item.selected,
            command=lambda: self.on_folder_toggle(folder_item)
        )
        folder_checkbox.pack(side=tk.LEFT)
        
        # Botón para expandir/contraer
        expand_button = ttk.Button(
            header_frame,
            text="📂 Expandir",
            command=lambda: self.toggle_folder_expansion(folder_item, files_frame, expand_button)
        )
        expand_button.pack(side=tk.RIGHT)
        
        # Frame para archivos (inicialmente oculto)
        files_frame = ttk.Frame(folder_frame)
        # No hacer pack() todavía - se hace en toggle_folder_expansion
        
        # Crear checkboxes de archivos individuales
        folder_item.file_objects = []  # Lista de objetos FileItem
        for filename in folder_item.files:
            file_path = folder_path / filename
            safety_icon, color, description = self.get_file_safety_info(filename)
            file_item = FileItem(filename, file_path, 'file', safety_icon, True, parent=folder_item)
            folder_item.file_objects.append(file_item)
            self.all_items.append(file_item)
            
            self.create_file_checkbox_in_frame(files_frame, file_item, color, description, indent=True)
        
        # Guardar referencias para la expansión
        folder_item.files_frame = files_frame
        folder_item.expand_button = expand_button
    
    def create_file_checkbox_in_frame(self, parent_frame, item, color, description, indent=False):
        """Crea un checkbox para un archivo en el frame especificado"""
        file_frame = ttk.Frame(parent_frame)
        file_frame.pack(fill=tk.X, padx=(20 if indent else 0, 0), pady=1)
        
        # Checkbox con color
        checkbox = ttk.Checkbutton(
            file_frame,
            text=f"{item.status} {item.name}",
            variable=item.selected,
            command=lambda: self.on_file_toggle(item)
        )
        checkbox.pack(anchor=tk.W)
        
        # Label con descripción
        desc_label = tk.Label(file_frame, text=f"  └─ {description}", font=("Arial", 8), fg=color)
        desc_label.pack(anchor=tk.W)
        
        # Tooltip con información
        self.create_tooltip(checkbox, f"Archivo: {item.name}\\nTipo: {description}\\nSeguridad: {item.status}")
    
    def toggle_folder_expansion(self, folder_item, files_frame, expand_button):
        """Alterna la expansión de una carpeta"""
        if folder_item.expanded:
            # Contraer
            files_frame.pack_forget()
            expand_button.config(text="📂 Expandir")
            folder_item.expanded = False
        else:
            # Expandir
            files_frame.pack(fill=tk.X, pady=(5, 0))
            expand_button.config(text="📁 Contraer")
            folder_item.expanded = True
    
    def expand_all_folders(self):
        """Expande todas las carpetas"""
        for item in self.all_items:
            if item.item_type == 'folder' and hasattr(item, 'files_frame'):
                if not item.expanded:
                    self.toggle_folder_expansion(item, item.files_frame, item.expand_button)
    
    def collapse_all_folders(self):
        """Contrae todas las carpetas"""
        for item in self.all_items:
            if item.item_type == 'folder' and hasattr(item, 'files_frame'):
                if item.expanded:
                    self.toggle_folder_expansion(item, item.files_frame, item.expand_button)
    
    def on_folder_toggle(self, folder_item):
        """Maneja el toggle de una carpeta (seleccionar/deseleccionar todos sus archivos)"""
        folder_selected = folder_item.selected.get()
        
        # Seleccionar/deseleccionar todos los archivos de la carpeta
        if hasattr(folder_item, 'file_objects'):
            for file_item in folder_item.file_objects:
                file_item.selected.set(folder_selected)
        
        self.update_selection_count()
    
    def on_file_toggle(self, file_item):
        """Maneja el toggle de un archivo individual"""
        # Si el archivo tiene una carpeta padre, verificar si todos los archivos están seleccionados
        if hasattr(file_item, 'parent') and file_item.parent and hasattr(file_item.parent, 'file_objects'):
            parent = file_item.parent
            all_files_selected = True
            any_file_selected = False
            
            for file_obj in parent.file_objects:
                if file_obj.selected.get():
                    any_file_selected = True
                else:
                    all_files_selected = False
            
            # Actualizar el estado del checkbox de la carpeta
            if all_files_selected:
                parent.selected.set(True)
            elif not any_file_selected:
                parent.selected.set(False)
            # Si algunos están seleccionados pero no todos, dejar el estado actual
        
        self.update_selection_count()
    
    def update_selection_count(self):
        """Actualiza el contador de elementos seleccionados"""
        selected_folders = sum(1 for item in self.all_items if item.item_type == 'folder' and item.selected.get())
        selected_files = sum(1 for item in self.all_items if item.item_type == 'file' and item.selected.get())
        total_selected = selected_folders + selected_files
        
        if total_selected > 0:
            self.selection_info.config(
                text=f"☑️ Seleccionados: {selected_folders} carpetas y {selected_files} archivos ({total_selected} total)",
                fg="blue"
            )
        else:
            total_items = len(self.all_items)
            self.selection_info.config(
                text=f"☐ Ningún elemento seleccionado ({total_items} disponibles)",
                fg="gray"
            )
    
    def select_all(self):
        """Selecciona todos los elementos"""
        for item in self.all_items:
            item.selected.set(True)
        self.update_selection_count()
    
    def deselect_all(self):
        """Deselecciona todos los elementos"""
        for item in self.all_items:
            item.selected.set(False)
        self.update_selection_count()
    
    def select_safe_only(self):
        """Selecciona solo elementos completamente seguros"""
        for item in self.all_items:
            # Solo seleccionar los que tienen indicador verde (✅)
            if item.status == "✅":
                item.selected.set(True)
            else:
                item.selected.set(False)
        self.update_selection_count()
    
    def select_with_special(self):
        """Selecciona elementos seguros y especiales"""
        for item in self.all_items:
            # Seleccionar verdes (✅) y especiales (⚙️, 🌟)
            if item.status in ["✅", "⚙️", "🌟"]:
                item.selected.set(True)
            else:
                item.selected.set(False)
        self.update_selection_count()
    
    def start_translation(self):
        """Inicia el proceso de traducción"""
        if self.is_translating:
            return
        
        base_path = self.endless_sky_path.get()
        if not base_path or not os.path.exists(base_path):
            messagebox.showerror("Error", "Por favor selecciona un directorio válido de Endless Sky")
            return
        
        # Obtener elementos seleccionados
        selected_folders = []
        selected_files = []
        
        for item in self.all_items:
            if item.selected.get():
                if item.item_type == 'folder':
                    selected_folders.append(item.name)
                elif item.item_type == 'file':
                    # Para archivos individuales, verificar si son archivos raíz o de carpeta
                    if hasattr(item, 'parent') and item.parent:
                        # Es un archivo dentro de una carpeta
                        # Solo agregarlo si la carpeta padre NO está seleccionada
                        if not item.parent.selected.get():
                            # Crear entrada especial para archivos individuales de carpetas
                            folder_file_key = f"{item.parent.name}/{item.name}"
                            selected_files.append(folder_file_key)
                    else:
                        # Es un archivo raíz
                        selected_files.append(item.name)
        
        if not selected_folders and not selected_files:
            messagebox.showwarning("Advertencia", "Por favor selecciona al menos una carpeta o archivo para traducir")
            return
        
        # Confirmar traducción
        total_selected = len(selected_folders) + len(selected_files)
        confirm_msg = f"¿Iniciar traducción de {total_selected} elementos?\\n\\n"
        confirm_msg += f"Carpetas: {', '.join(selected_folders) if selected_folders else 'Ninguna'}\\n"
        confirm_msg += f"Archivos: {', '.join(selected_files) if selected_files else 'Ninguno'}"
        
        if not messagebox.askyesno("Confirmar Traducción", confirm_msg):
            return
        
        # Configurar UI para traducción
        self.is_translating = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.status_label.config(text="🚀 Iniciando traducción...", fg="orange")
        self.progress_bar.config(value=0)
        
        # Obtener idioma
        lang_selection = self.target_language.get()
        target_lang = lang_selection.split(' - ')[0] if ' - ' in lang_selection else 'es'
        
        # Limpiar log
        self.log_text.delete(1.0, tk.END)
        self.log_message_colored(f"🚀 Iniciando traducción a {target_lang}")
        self.log_message_colored(f"📁 Directorio base: {base_path}")
        self.log_message_colored(f"📂 Carpetas seleccionadas: {selected_folders}")
        self.log_message_colored(f"📄 Archivos seleccionados: {selected_files}")
        
        # Debug: mostrar rutas completas para verificar
        for folder in selected_folders:
            folder_path = Path(base_path) / "data" / folder
            self.log_message_colored(f"🔍 Carpeta a procesar: {folder_path} (existe: {folder_path.exists()})")
        
        for file_entry in selected_files:
            if "/" in file_entry:
                folder_name, filename = file_entry.split("/", 1)
                file_path = Path(base_path) / "data" / folder_name / filename
            else:
                file_path = Path(base_path) / "data" / file_entry
            self.log_message_colored(f"🔍 Archivo a procesar: {file_path} (existe: {file_path.exists()})")
        
        # Iniciar traducción en hilo separado
        self.translation_thread = threading.Thread(
            target=self.run_translation,
            args=(base_path, target_lang, selected_folders, selected_files)
        )
        self.translation_thread.daemon = True
        self.translation_thread.start()
    
    def run_translation(self, base_path, target_lang, selected_folders, selected_files):
        """Ejecuta la traducción en un hilo separado"""
        try:
            # Crear instancia del traductor personalizada
            translator = CustomTranslatorImproved(base_path, target_lang, self.translation_queue)
            
            # Ejecutar traducción con selecciones específicas
            translator.run_custom_translation(selected_folders, selected_files)
            
            self.translation_queue.put(("status", "✅ Traducción completada exitosamente!", "green"))
            self.translation_queue.put(("progress", 100))
            
        except Exception as e:
            error_msg = f"❌ Error durante la traducción: {str(e)}"
            self.translation_queue.put(("status", error_msg, "red"))
            self.translation_queue.put(("log", error_msg))
        finally:
            self.translation_queue.put(("finished", None, None))
    
    def stop_translation(self):
        """Detiene la traducción"""
        if self.translation_thread and self.translation_thread.is_alive():
            self.log_message("⏹️ Deteniendo traducción...")
        self.translation_finished()
    
    def translation_finished(self):
        """Limpia la UI cuando termina la traducción"""
        self.is_translating = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
    
    def check_queue(self):
        """Verifica la cola de mensajes del hilo de traducción"""
        try:
            while True:
                queue_item = self.translation_queue.get_nowait()
                
                # Verificar el formato del mensaje
                if len(queue_item) == 3:
                    msg_type, message, color = queue_item
                elif len(queue_item) == 2:
                    msg_type, message = queue_item
                    color = None
                else:
                    continue
                
                if msg_type == "log":
                    self.log_message_colored(message)
                elif msg_type == "status":
                    self.status_label.config(text=message, fg=color if color else "blue")
                elif msg_type == "progress":
                    self.progress_bar.config(value=message)
                elif msg_type == "finished":
                    self.translation_finished()
                    
        except queue.Empty:
            pass
        
        # Programar siguiente verificación
        self.root.after(100, self.check_queue)
    
    def log_message(self, message):
        """Añade un mensaje al log sin formato"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def log_message_colored(self, message):
        """Añade un mensaje al log con colores según el contenido"""
        # Configurar etiquetas de colores si no existen
        if not hasattr(self, 'log_colors_configured'):
            self.log_text.tag_configure("success", foreground="green")
            self.log_text.tag_configure("error", foreground="red")
            self.log_text.tag_configure("warning", foreground="orange")
            self.log_text.tag_configure("info", foreground="blue")
            self.log_text.tag_configure("processing", foreground="purple")
            self.log_colors_configured = True
        
        # Determinar color según el contenido del mensaje
        color_tag = None
        if message.startswith("✅") or "líneas traducidas" in message:
            color_tag = "success"
        elif message.startswith("❌") or "Error" in message:
            color_tag = "error"
        elif message.startswith("⚠️") or "Sin traducciones" in message:
            color_tag = "warning"
        elif message.startswith("🚀") or message.startswith("🔧") or message.startswith("💡"):
            color_tag = "info"
        elif message.startswith("📄") or message.startswith("📂"):
            color_tag = "processing"
        
        # Insertar el mensaje con color
        start_pos = self.log_text.index(tk.END)
        self.log_text.insert(tk.END, f"{message}\n")
        
        if color_tag:
            end_pos = self.log_text.index(tk.END + "-1c")
            self.log_text.tag_add(color_tag, start_pos, end_pos)
        
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Limpia el log"""
        self.log_text.delete(1.0, tk.END)
    
    def save_config(self):
        """Guarda la configuración actual"""
        config = {
            'endless_sky_path': self.endless_sky_path.get(),
            'target_language': self.target_language.get()
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            messagebox.showinfo("Éxito", "Configuración guardada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar configuración: {e}")
    
    def load_config(self):
        """Carga la configuración guardada"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                self.endless_sky_path.set(config.get('endless_sky_path', ''))
                self.target_language.set(config.get('target_language', 'es'))
        except Exception:
            # Si hay error cargando, usar valores por defecto
            pass
    
    def get_folder_status(self, folder_name):
        """Obtiene el estado de una carpeta"""
        safe_folders = ['human', 'hai', 'korath', 'wanderer', 'remnant', 'pug', 'quarg', 'coalition', '_ui']
        return "✅" if folder_name in safe_folders else "⚠️"
    
    def create_tooltip(self, widget, text):
        """Crea un tooltip para un widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=text, background="lightyellow", 
                           relief="solid", borderwidth=1, font=("Arial", 9))
            label.pack()
            
            def hide_tooltip():
                tooltip.destroy()
            
            tooltip.after(3000, hide_tooltip)  # Auto-hide after 3 seconds
        
        widget.bind("<Enter>", show_tooltip)

    # ...existing code...
    
class CustomTranslatorImproved(EndlessSkyTranslatorFixed):
    """Traductor personalizado mejorado que envía mensajes a la GUI"""
    
    def __init__(self, base_path, target_lang, message_queue):
        super().__init__(base_path, target_lang)
        self.message_queue = message_queue
    
    def log_message(self, message):
        """Envía mensaje a la GUI"""
        self.message_queue.put(("log", message, None))
        print(message)  # También imprimir en consola
    
    def translate_text(self, text):
        """Traduce un texto usando Google Translate preservando TODOS los identificadores del juego"""
        if not text or len(text.strip()) < 2:
            return text
        
        try:
            clean_text = text.strip()
            if not clean_text:
                return text
            
            # PRESERVAR TODOS LOS ELEMENTOS ESPECIALES DEL JUEGO
            preservation_map = {}
            temp_text = clean_text
            placeholder_counter = 0
            
            # 1. Variables del juego como <planet>, <origin>, <destination>, <tons>, etc.
            # IMPORTANTE: Preservar TODAS las etiquetas entre < >
            game_variables = re.findall(r'<[^>]+>', temp_text)
            if game_variables:
                self.log_message(f"    🔒 Preservando {len(game_variables)} etiqueta(s): {game_variables}")
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
            
            self.log_message(f"    🌍 Traduciendo: '{temp_text[:50]}{'...' if len(temp_text) > 50 else ''}'")
            time.sleep(0.1)
            
            translated = self.translator.translate(temp_text, dest=self.target_lang)
            result_text = translated.text if hasattr(translated, 'text') else str(translated)
            
            # RESTAURAR TODOS LOS ELEMENTOS PRESERVADOS
            tags_restored = 0
            for placeholder, original_value in preservation_map.items():
                # Buscar tanto el placeholder original como en minúsculas (Google Translate los convierte)
                placeholder_lower = placeholder.lower()
                if placeholder in result_text:
                    result_text = result_text.replace(placeholder, original_value)
                    tags_restored += 1
                elif placeholder_lower in result_text:
                    result_text = result_text.replace(placeholder_lower, original_value)
                    tags_restored += 1
            
            # Verificación adicional: asegurar que no queden placeholders sin restaurar
            remaining_placeholders = re.findall(r'__[a-zA-Z]+_\d+__', result_text)
            if remaining_placeholders:
                # Intentar restaurar manualmente con búsqueda insensible a mayúsculas
                for placeholder in remaining_placeholders:
                    # Buscar placeholder original correspondiente
                    for orig_placeholder, orig_value in preservation_map.items():
                        if orig_placeholder.lower() == placeholder.lower():
                            result_text = result_text.replace(placeholder, orig_value)
                            tags_restored += 1
                            break
            
            # Mostrar resultado de restauración si hay etiquetas
            if preservation_map:
                final_tags = re.findall(r'<[^>]*>', result_text)
                if final_tags:
                    self.log_message(f"    ✅ {len(final_tags)} etiqueta(s) preservada(s): {final_tags}")
                else:
                    self.log_message(f"    ⚠️ Se perdieron algunas etiquetas durante la traducción")
            
            # Normalizar el texto para el juego (eliminar tildes)
            result_text = self.normalize_text_for_game(result_text)
            
            # Restaurar elementos especiales
            final_text = underscore_prefix + result_text + ellipsis_suffix
            
            self.log_message(f"    ✅ Resultado: '{final_text[:50]}{'...' if len(final_text) > 50 else ''}'")
            return final_text
            
        except Exception as e:
            self.log_message(f"    ❌ Error traduciendo '{text[:30]}...': {e}")
            return text
    
    def translate_map_planets_file(self, source_file, dest_file):
        """Sobrescribir para redirigir logs a GUI"""
        import time
        
        self.log_message(f"\n🌍 Procesando archivo de planetas: {source_file.name}")
        
        # Asegurar que el directorio de destino existe
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Detectar codificación
        encoding = self.detect_encoding(source_file)
        self.log_message(f"   🔤 Codificación: {encoding}")
        
        try:
            with open(source_file, 'r', encoding=encoding) as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            self.log_message(f"   ⚠️ Error con {encoding}, usando UTF-8...")
            encoding = 'utf-8'
            with open(source_file, 'r', encoding=encoding, errors='ignore') as f:
                lines = f.readlines()
        
        self.log_message(f"   📊 Total de líneas: {len(lines)}")
        
        translated_lines = []
        current_planet = None
        in_planet_block = False
        translations_made = 0
        
        for i, line in enumerate(lines):
            # Mostrar progreso cada 20 líneas
            if i % 20 == 0:
                self.log_message(f"   📈 Progreso planetas: {i}/{len(lines)} líneas...")
            
            line_stripped = line.strip()
            
            if i < 10 or line_stripped.startswith('planet') or 'description' in line_stripped.lower() or i % 50 == 0:
                self.log_message(f"    📍 LÍNEA {i+1}: Analizando: '{line_stripped[:80]}{'...' if len(line_stripped) > 80 else ''}'")
            
            # Detectar definición de planeta
            planet_match = re.match(r'^planet\s+"([^"]*)"', line_stripped)
            if planet_match:
                current_planet = planet_match.group(1)
                in_planet_block = True
                self.log_message(f"  🪐 LÍNEA {i+1}: Procesando planeta: {current_planet}")
                translated_lines.append(line)
                continue
            
            # Verificar si es comentario o fin de bloque
            if line_stripped.startswith('#') or line_stripped == '':
                if in_planet_block:
                    self.log_message(f"    📍 LÍNEA {i+1}: {'Fin de bloque de planeta' if not in_planet_block else 'Comentario en planeta'}")
                translated_lines.append(line)
                continue
                
            # Detectar nueva definición (fin del bloque anterior)
            if re.match(r'^(ship|outfit|planet|system|government|event)\s+', line_stripped):
                self.log_message(f"    📍 LÍNEA {i+1}: Fin de bloque de planeta - nueva definición")
                in_planet_block = False
                current_planet = None
                translated_lines.append(line)
                continue
            
            # Si estamos dentro de un bloque de planeta
            if in_planet_block and current_planet:
                self.log_message(f"    🔬 LÍNEA {i+1}: Dentro del planeta {current_planet}")
                
                # Buscar description
                if line_stripped.startswith('description'):
                    self.log_message(f"    🎯 LÍNEA {i+1}: DETECTADA DESCRIPCIÓN - verificando si termina en backtick...")
                    if line_stripped.endswith('`'):
                        self.log_message(f"    ✅ LÍNEA {i+1}: DESCRIPCIÓN VÁLIDA - extrayendo texto...")
                        
                        # Extraer el texto entre backticks
                        match = re.match(r'^(\s*description\s+`)(.*)`(\s*)$', line)
                        if match:
                            prefix, text_to_translate, suffix = match.groups()
                            self.log_message(f"    📝 LÍNEA {i+1}: ¡TRADUCIENDO DESCRIPCIÓN! de {current_planet}")
                            self.log_message(f"        Texto original: '{text_to_translate[:60]}{'...' if len(text_to_translate) > 60 else ''}'")
                            
                            try:
                                # Traducir usando el método de la clase base
                                translated_text = self.translate_text(text_to_translate)
                                if translated_text != text_to_translate:
                                    line = f"{prefix}{translated_text}`{suffix}\n"
                                    translations_made += 1
                                    self.log_message(f"    ✅ LÍNEA {i+1}: Descripción traducida exitosamente!")
                                    self.log_message(f"        Resultado: '{translated_text[:60]}{'...' if len(translated_text) > 60 else ''}'")
                                
                            except Exception as e:
                                self.log_message(f"    ❌ LÍNEA {i+1}: Error traduciendo descripción: {e}")
                                # Mantener línea original en caso de error
                        else:
                            # La regex no coincide, mantener línea original
                            self.log_message(f"    ❌ LÍNEA {i+1}: DESCRIPCIÓN no coincide con regex")
                    else:
                        # Description sin backtick al final, o línea incompleta
                        pass
            
            translated_lines.append(line)
        
        # Escribir archivo traducido
        with open(dest_file, 'w', encoding='utf-8') as f:
            f.writelines(translated_lines)
        
        self.log_message(f"✅ Planetas completado: {translations_made} descripciones traducidas")
        return translations_made
    
    def translate_file(self, source_file, dest_file):
        """Sobrescribir para redirigir logs a GUI"""
        self.log_message(f"\n📄 Procesando archivo: {source_file.name}")
        
        # Determinar si necesita lógica especial
        filename_lower = source_file.name.lower()
        
        if filename_lower == 'commodities.txt':
            self.log_message(f"   🎯 Aplicando lógica especial para commodities")
            return self.translate_commodities_file(source_file, dest_file)
        elif filename_lower in ['ships.txt', 'outfits.txt', 'engines.txt', 'weapons.txt', 'power.txt']:
            self.log_message(f"   🎯 Aplicando lógica especial para ships/outfits/engines")
            return self.translate_ships_outfits_file(source_file, dest_file)
        
        # Lógica general para otros archivos
        # Crear directorio de destino
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Detectar codificación
        encoding = self.detect_encoding(source_file)
        self.log_message(f"   🔤 Codificación: {encoding}")
        
        try:
            with open(source_file, 'r', encoding=encoding, errors='ignore') as f:
                lines = f.readlines()
        except:
            self.log_message(f"   ⚠️ Error con {encoding}, usando UTF-8...")
            with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        
        self.log_message(f"   📊 Total de líneas: {len(lines)}")
        translated_lines = []
        lines_translated = 0
        lines_skipped = 0
        
        for i, line in enumerate(lines):
            if i % 100 == 0 and i > 0:
                self.log_message(f"   📈 Progreso: {i}/{len(lines)} líneas...")
                
            translated_line, was_translated = self.translate_line(line)
            
            if was_translated:
                lines_translated += 1
                self.log_message(f"  ✅ Línea {i+1} traducida")
            else:
                lines_skipped += 1
            
            translated_lines.append(translated_line)
        
        # Solo crear archivo si hay traducciones
        if lines_translated > 0:
            self.log_message(f"   💾 Guardando archivo con {lines_translated} líneas traducidas...")
            # Guardar con codificación UTF-8 y BOM para máxima compatibilidad
            with open(dest_file, 'w', encoding='utf-8-sig') as f:
                f.writelines(translated_lines)
            self.log_message(f"   ✅ Archivo guardado: {dest_file}")
        else:
            self.log_message(f"   ⏭️  Sin traducciones, archivo omitido")
        
        return lines_translated

    def translate_line(self, line):
        """Sobrescribir para redirigir logs a GUI"""
        original_line = line
        line_stripped = line.strip()
        
        # Verificar si la línea nunca debe traducirse
        if self.should_never_translate_line(line):
            return line, False
        
        # Extraer texto traducible
        result = self.extract_translatable_text(line)
        if result is None:
            return line, False
        
        prefix, text_to_translate, suffix, text_type = result
        
        if not text_to_translate or len(text_to_translate.strip()) < 2:
            return line, False
        
        # Traducir el texto
        translated_text = self.translate_text(text_to_translate)
        if translated_text == text_to_translate:
            return line, False  # No se tradujo
        
        # Reconstruir la línea según el tipo
        if text_type == 'backtick':
            # Para texto entre backticks
            new_line = f"{prefix}`{translated_text}`{suffix}\n"
        elif text_type == 'description':
            # Para descripciones en comillas, reemplazar solo el contenido
            new_line = line.replace(f'"{text_to_translate}"', f'"{translated_text}"')
        else:
            # Fallback
            new_line = line.replace(text_to_translate, translated_text)
        
        return new_line, True
    
    def run_custom_translation(self, selected_folders, selected_files):
        """Ejecuta traducción personalizada basada en selecciones"""
        self.log_message("=== Traductor Mejorado de Endless Sky ===")
        self.log_message(f"Idioma destino: {self.target_lang}")
        
        # Crear estructura del plugin
        self.create_plugin_structure()
        self.log_message(f"🔧 Plugin creado en: {self.plugin_path}")
        
        total_files_processed = 0
        progress_step = 0
        total_steps = len(selected_folders) + len(selected_files)
        
        # Procesar archivos individuales seleccionados
        for file_entry in selected_files:
            progress_step += 1
            progress = (progress_step / total_steps) * 100 if total_steps > 0 else 0
            self.message_queue.put(("progress", progress))
            
            # Verificar si es archivo raíz o archivo de carpeta
            if "/" in file_entry:
                # Es archivo dentro de carpeta: "carpeta/archivo.txt"
                folder_name, filename = file_entry.split("/", 1)
                source_file = self.data_path / folder_name / filename
                dest_file = self.plugin_data_path / folder_name / filename
                
                # Crear directorio de carpeta si no existe
                dest_file.parent.mkdir(parents=True, exist_ok=True)
            else:
                # Es archivo raíz
                filename = file_entry
                source_file = self.data_path / filename
                dest_file = self.plugin_data_path / filename
            
            if source_file.exists():
                self.log_message(f"\n📄 Procesando archivo: {source_file.name}")
                lines_translated = self.translate_file(source_file, dest_file)
                if lines_translated > 0:
                    total_files_processed += 1
                    self.log_message(f"✅ {source_file.name}: {lines_translated} líneas traducidas")
                else:
                    self.log_message(f"⏭️ {source_file.name}: Sin traducciones")
            else:
                self.log_message(f"❌ Archivo no encontrado: {source_file}")
        
        # Procesar carpetas seleccionadas
        for folder_name in selected_folders:
            progress_step += 1
            progress = (progress_step / total_steps) * 100 if total_steps > 0 else 0
            self.message_queue.put(("progress", progress))
            
            source_folder = self.data_path / folder_name
            dest_folder = self.plugin_data_path / folder_name
            
            if source_folder.exists():
                self.log_message(f"\n📂 Procesando carpeta: {folder_name}")
                files_in_folder = self.translate_folder_selective(source_folder, dest_folder)
                total_files_processed += files_in_folder
                self.log_message(f"✅ Carpeta {folder_name}: {files_in_folder} archivos procesados")
            else:
                self.log_message(f"❌ Carpeta no encontrada: {folder_name}")
        
        self.log_message(f"\n✅ Traducción completada!")
        self.log_message(f"📊 {total_files_processed} archivos procesados en total")
        
        if total_files_processed > 0:
            self.log_message(f"\n💡 Para usar la traducción:")
            self.log_message(f"   1. Inicia Endless Sky")
            self.log_message(f"   2. Ve a Preferencias → Plugins")
            self.log_message(f"   3. Activa 'Traducción al Español'")
            self.log_message(f"   4. Reinicia el juego")
        else:
            self.log_message(f"\n⚠️ No se procesaron archivos. Verifica tu selección.")
    
    def translate_folder_selective(self, source_folder, dest_folder):
        """Traduce una carpeta usando solo archivos seguros"""
        files_processed = 0
        
        # Crear carpeta de destino
        dest_folder.mkdir(parents=True, exist_ok=True)
        
        # Buscar archivos .txt en la carpeta
        for file_path in source_folder.glob("*.txt"):
            if self.is_file_safe_for_gui(file_path):
                dest_file = dest_folder / file_path.name
                lines_translated = self.translate_file(file_path, dest_file)
                if lines_translated > 0:
                    files_processed += 1
                    self.log_message(f"  ✅ {file_path.name}: {lines_translated} líneas")
                else:
                    self.log_message(f"  ⏭️ {file_path.name}: Sin traducciones")
            else:
                self.log_message(f"  ⏭️ {file_path.name}: Archivo omitido (no seguro)")
        
        return files_processed
    
    def is_file_safe_for_gui(self, file_path):
        """Versión de seguridad para GUI que coincide con el filtro de archivos"""
        filename = file_path.name.lower()
        
        # Lista específica de archivos que NUNCA deben procesarse
        excluded_files = [
            'fleets.txt', 'governments.txt', 'systems.txt', 'planets.txt',
            'map systems.txt', 'commodities.txt', 'variants.txt', 'persons.txt',
            'effects.txt', 'hazards.txt', 'formations.txt', 'stars.txt', 'series.txt',
            'derelicts.txt', 'minables.txt', 'start.txt', 'wormhole.txt'
        ]
        
        if filename in excluded_files:
            return False
        
        # Patrones que NUNCA deben procesarse
        excluded_patterns = ['derelict', 'variant', 'formation', 'hazard', 'fleet', 'government', 'system']
        if any(pattern in filename for pattern in excluded_patterns):
            return False
        
        # Archivos que SÍ queremos procesar
        safe_patterns = ['mission', 'conversation', 'dialog', 'hail', 'job', 'news', 'event', 'campaign']
        if any(pattern in filename for pattern in safe_patterns):
            return True
        
        # Archivos especiales que SÍ queremos (solo con lógica especial)
        special_files = ['ships.txt', 'outfits.txt', 'engines.txt', 'weapons.txt', 'power.txt']
        if filename in special_files:
            return True
        
        # Si llegamos aquí, probablemente no es seguro procesar el archivo
        return False

    def translate_commodities_file(self, source_file, dest_file):
        """Sobrescribir para redirigir logs a GUI"""
        self.log_message(f"\n📦 Procesando archivo de commodities: {source_file.name}")
        
        # Crear directorio de destino
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Detectar codificación
        encoding = self.detect_encoding(source_file)
        self.log_message(f"   🔤 Codificación: {encoding}")
        
        try:
            with open(source_file, 'r', encoding=encoding, errors='ignore') as f:
                lines = f.readlines()
        except:
            self.log_message(f"   ⚠️ Error con {encoding}, usando UTF-8...")
            with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        
        self.log_message(f"   📊 Total de líneas: {len(lines)}")
        translated_lines = []
        lines_translated = 0
        lines_skipped = 0
        in_commodity_block = False
        current_commodity = ""
        
        for i, line in enumerate(lines):
            if i % 500 == 0 and i > 0:
                self.log_message(f"   📈 Progreso commodities: {i}/{len(lines)} líneas...")
            
            original_line = line
            line_stripped = line.strip()
            
            # Detectar inicio de bloque commodity
            commodity_match = re.match(r'^commodity\s+"([^"]*)"(?:\s+(\d+)\s+(\d+))?', line_stripped)
            if commodity_match:
                in_commodity_block = True
                commodity_name = commodity_match.group(1)
                current_commodity = f"commodity {commodity_name}"
                self.log_message(f"  📦 LÍNEA {i+1}: Detectado commodity: {commodity_name}")
                translated_lines.append(original_line)  # NO traducir nombres de commodities
                continue
            
            # Detectar fin de bloque
            if in_commodity_block and (not line_stripped or 
                                     line_stripped.startswith('#') or
                                     re.match(r'^(commodity|planet|ship|outfit|system)\s+', line_stripped)):
                in_commodity_block = False
                self.log_message(f"  📍 LÍNEA {i+1}: Fin de bloque commodity")
            
            # Si estamos en un bloque commodity
            if in_commodity_block:
                was_translated = False
                
                # Solo traducir elementos seguros dentro de commodities
                # Como descripción (pero no nombres ni valores)
                if line_stripped.startswith('description'):
                    desc_match = re.match(r'^(\s*description\s+)"(.+)"(.*)$', line.rstrip())
                    if desc_match:
                        prefix, description_text, suffix = desc_match.groups()
                        self.log_message(f"    🎯 LÍNEA {i+1}: DESCRIPCIÓN COMMODITY - {current_commodity}")
                        try:
                            translated_text = self.translate_text(description_text)
                            if translated_text != description_text:
                                line = f'{prefix}"{translated_text}"{suffix}\n'
                                was_translated = True
                                lines_translated += 1
                                self.log_message(f"    ✅ LÍNEA {i+1}: Descripción traducida!")
                        except Exception as e:
                            self.log_message(f"    ❌ LÍNEA {i+1}: Error: {e}")
                
                if was_translated:
                    translated_lines.append(line)
                else:
                    translated_lines.append(original_line)
                    lines_skipped += 1
            else:
                translated_lines.append(original_line)
                lines_skipped += 1
        
        # Solo guardar si hay traducciones
        if lines_translated > 0:
            self.log_message(f"   💾 Guardando commodities con {lines_translated} líneas traducidas...")
            with open(dest_file, 'w', encoding='utf-8-sig') as f:
                f.writelines(translated_lines)
            self.log_message(f"   ✅ Commodities guardado: {dest_file}")
        else:
            self.log_message(f"   ⏭️ Sin traducciones en commodities, archivo omitido")
        
        return lines_translated

    def translate_ships_outfits_file(self, source_file, dest_file):
        """Traduce ships/outfits/engines FORZANDO SOBRESCRITURA COMPLETA"""
        self.log_message(f"\n🚢 Procesando archivo de naves/outfits: {source_file.name}")
        
        # Crear directorio de destino
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Detectar codificación
        encoding = self.detect_encoding(source_file)
        self.log_message(f"   🔤 Codificación: {encoding}")
        
        try:
            with open(source_file, 'r', encoding=encoding, errors='ignore') as f:
                lines = f.readlines()
        except:
            self.log_message(f"   ⚠️ Error con {encoding}, usando UTF-8...")
            with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        
        self.log_message(f"   📊 Total de líneas: {len(lines)}")
        
        # *** NUEVA ESTRATEGIA: Solo guardar elementos que REALMENTE se traducen ***
        translated_items = []  # Lista de elementos traducidos completamente
        lines_translated = 0
        in_item_block = False
        current_item_lines = []
        current_item_name = ""
        current_item_type = ""
        current_indent = 0
        item_has_translations = False
        
        for i, line in enumerate(lines):
            if i % 100 == 0 and i > 0:
                self.log_message(f"   📈 Progreso naves/outfits: {i}/{len(lines)} líneas...")
            
            original_line = line
            line_stripped = line.strip()
            
            # Saltar comentarios de copyright al inicio
            if line_stripped.startswith('#') and i < 20:
                continue
            
            # Detectar inicio de bloque de nave, outfit o effect
            item_match = re.match(r'^(ship|outfit|effect)\s+"?([^"]*)"?', line_stripped)
            if item_match:
                # Si estábamos procesando un item anterior y tenía traducciones, guardarlo
                if in_item_block and item_has_translations and current_item_lines:
                    self.log_message(f"    💾 Guardando {current_item_type} traducido: {current_item_name}")
                    translated_items.extend(current_item_lines)
                
                # Iniciar nuevo item
                in_item_block = True
                current_item_type, current_item_name = item_match.groups()
                current_indent = len(line) - len(line.lstrip())
                current_item_lines = [original_line]
                item_has_translations = False
                self.log_message(f"  🔧 LÍNEA {i+1}: Procesando {current_item_type}: {current_item_name}")
                continue
            
            # Detectar fin de bloque
            if in_item_block:
                line_indent = len(line) - len(line.lstrip()) if line.strip() else 0
                
                # Si encontramos una nueva definición al mismo nivel, terminar bloque actual
                if (line_stripped and 
                    line_indent <= current_indent and 
                    any(line_stripped.startswith(kw) for kw in ['ship ', 'outfit ', 'effect ', 'planet ', 'system '])):
                    
                    # Guardar item anterior si tenía traducciones
                    if item_has_translations and current_item_lines:
                        self.log_message(f"    � Guardando {current_item_type} traducido: {current_item_name}")
                        translated_items.extend(current_item_lines)
                    
                    in_item_block = False
                    current_item_lines = []
                    item_has_translations = False
                    
                    # Procesar esta línea como nueva definición
                    continue
                
                # Si es línea vacía o comentario, añadir a las líneas del item actual
                elif not line_stripped or line_stripped.startswith('#'):
                    current_item_lines.append(original_line)
                    continue
            
            # LÓGICA DE REEMPLAZO: Si estamos en un bloque de item, traducir líneas específicas
            if in_item_block:
                translated_line = original_line  # Por defecto, mantener original
                was_translated = False
                
                # 1. DESCRIPCIÓN: Reemplazar texto entre comillas
                description_match = re.match(r'^(\s*description\s+)"(.+)"(.*)$', line.rstrip())
                if description_match:
                    prefix, description_text, suffix = description_match.groups()
                    self.log_message(f"    🎯 LÍNEA {i+1}: DESCRIPCIÓN DETECTADA en {current_item_type} {current_item_name}")
                    self.log_message(f"    🌍 Traduciendo: '{description_text[:50]}{'...' if len(description_text) > 50 else ''}'")
                    try:
                        translated_text = self.translate_text(description_text)
                        if translated_text != description_text:
                            translated_line = f'{prefix}"{translated_text}"{suffix}\n'
                            was_translated = True
                            item_has_translations = True
                            lines_translated += 1
                            self.log_message(f"    ✅ LÍNEA {i+1}: Descripción traducida correctamente")
                    except Exception as e:
                        self.log_message(f"    ❌ LÍNEA {i+1}: Error: {e}")
                
                # 2. PLURAL: Reemplazar nombres plurales
                elif re.match(r'^\s*plural\s+"(.+)"', line_stripped):
                    plural_match = re.match(r'^(\s*plural\s+)"(.+)"(.*)$', line.rstrip())
                    if plural_match:
                        prefix, plural_text, suffix = plural_match.groups()
                        self.log_message(f"    🎯 LÍNEA {i+1}: PLURAL DETECTADO en {current_item_type} {current_item_name}")
                        self.log_message(f"    🌍 Traduciendo: '{plural_text}'")
                        try:
                            translated_text = self.translate_text(plural_text)
                            if translated_text != plural_text:
                                translated_line = f'{prefix}"{translated_text}"{suffix}\n'
                                was_translated = True
                                item_has_translations = True
                                lines_translated += 1
                                self.log_message(f"    ✅ LÍNEA {i+1}: plural traducido correctamente")
                        except Exception as e:
                            self.log_message(f"    ❌ LÍNEA {i+1}: Error en plural: {e}")
                
                # 3. NOUN: Reemplazar sustantivos
                elif re.match(r'^\s*noun\s+"(.+)"', line_stripped):
                    noun_match = re.match(r'^(\s*noun\s+)"(.+)"(.*)$', line.rstrip())
                    if noun_match:
                        prefix, noun_text, suffix = noun_match.groups()
                        self.log_message(f"    🎯 LÍNEA {i+1}: SUSTANTIVO DETECTADO en {current_item_type} {current_item_name}")
                        self.log_message(f"    🌍 Traduciendo: '{noun_text}'")
                        try:
                            translated_text = self.translate_text(noun_text)
                            if translated_text != noun_text:
                                translated_line = f'{prefix}"{translated_text}"{suffix}\n'
                                was_translated = True
                                item_has_translations = True
                                lines_translated += 1
                                self.log_message(f"    ✅ LÍNEA {i+1}: sustantivo traducido correctamente")
                        except Exception as e:
                            self.log_message(f"    ❌ LÍNEA {i+1}: Error en sustantivo: {e}")
                
                # 4. EXPLANATION: Reemplazar explicaciones
                elif re.match(r'^\s*explanation\s+"(.+)"', line_stripped):
                    explanation_match = re.match(r'^(\s*explanation\s+)"(.+)"(.*)$', line.rstrip())
                    if explanation_match:
                        prefix, explanation_text, suffix = explanation_match.groups()
                        self.log_message(f"    🎯 LÍNEA {i+1}: EXPLICACIÓN DETECTADA en {current_item_type} {current_item_name}")
                        self.log_message(f"    🌍 Traduciendo: '{explanation_text[:50]}{'...' if len(explanation_text) > 50 else ''}'")
                        try:
                            translated_text = self.translate_text(explanation_text)
                            if translated_text != explanation_text:
                                translated_line = f'{prefix}"{translated_text}"{suffix}\n'
                                was_translated = True
                                item_has_translations = True
                                lines_translated += 1
                                self.log_message(f"    ✅ LÍNEA {i+1}: explicación traducida correctamente")
                        except Exception as e:
                            self.log_message(f"    ❌ LÍNEA {i+1}: Error en explicación: {e}")
                
                # Añadir la línea (original o traducida) al item actual
                current_item_lines.append(translated_line)
            else:
                # Fuera de bloque, ignorar líneas
                pass
        
        # No olvidar el último item si tenía traducciones
        if in_item_block and item_has_translations and current_item_lines:
            self.log_message(f"    💾 Guardando último {current_item_type} traducido: {current_item_name}")
            translated_items.extend(current_item_lines)
        
        # Solo guardar archivo si hay elementos traducidos
        if translated_items:
            self.log_message(f"   💾 Guardando archivo SOLO con elementos traducidos: {lines_translated} líneas")
            
            # Crear contenido final con header y elementos traducidos
            final_content = []
            final_content.append("# Plugin translation - SOLO elementos traducidos para forzar sobrescritura\n")
            final_content.append("# Este archivo contiene ÚNICAMENTE elementos con traducciones\n")
            final_content.append("\n")
            final_content.extend(translated_items)
            
            with open(dest_file, 'w', encoding='utf-8-sig') as f:
                f.writelines(final_content)
            self.log_message(f"   ✅ Archivo ships/outfits guardado SOLO con traducciones: {dest_file}")
        else:
            self.log_message(f"   ⏭️ Sin traducciones encontradas, no se crea archivo")
        
        return lines_translated
def main():
    """Función principal para ejecutar la GUI mejorada"""
    root = tk.Tk()
    
    # Configurar estilo
    style = ttk.Style()
    style.theme_use('clam')  # Usar tema más moderno
    
    # Crear y ejecutar aplicación
    app = TranslatorGUIImproved(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\\nSaliendo...")


if __name__ == "__main__":
    main()
