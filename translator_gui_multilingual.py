#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Multilingual GUI for Endless Sky Translator
GUI with real checkboxes/ticks, precise filtering of translatable files and intuitive selection
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

# Import the main translator
try:
    from translator import EndlessSkyTranslatorFixed
    from translations import translator as t
except ImportError:
    # If running from another directory
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from translator import EndlessSkyTranslatorFixed
    from translations import translator as t

class FileItem:
    """Represents a file or folder with checkbox state"""
    def __init__(self, name, path, item_type, status, translatable=True, parent=None):
        self.name = name
        self.path = path
        self.item_type = item_type  # 'file', 'folder', 'root'
        self.status = status        # Safety status
        self.translatable = translatable
        self.selected = tk.BooleanVar()
        self.parent = parent        # For files inside folders
        self.files = []            # For folders, list of files
        self.expanded = False      # If folder is expanded

class TranslatorGUIImproved:
    def __init__(self, root):
        self.root = root
        self.root.title(t.get('window_title'))
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Variables
        self.endless_sky_path = tk.StringVar()
        self.target_language = tk.StringVar(value='es')
        self.gui_language = tk.StringVar(value='en')  # GUI language
        self.translator = None
        self.translation_thread = None
        self.translation_queue = queue.Queue()
        self.is_translating = False
        
        # List of elements (files and folders) with checkboxes
        self.all_items = []  # Flat list of all elements for easy searches
        
        # Default configuration
        self.config_file = "translator_config.json"
        self.load_config()
        
        # Create interface
        self.create_widgets()
        self.scan_translatable_items()
        
        # Start message queue checking
        self.check_queue()
    
    def change_gui_language(self, language_code):
        """Change GUI language and refresh interface"""
        t.set_language(language_code)
        self.gui_language.set(language_code)
        self.refresh_interface()
    
    def refresh_interface(self):
        """Refresh all interface text with current language"""
        self.root.title(t.get('window_title'))
        
        # Update notebook tabs
        self.notebook.tab(0, text=t.get('config_tab'))
        self.notebook.tab(1, text=t.get('selection_tab'))
        self.notebook.tab(2, text=t.get('translation_tab'))
        
        # Recreate widgets with new language
        self.create_widgets()
        self.scan_translatable_items()
    
    def create_widgets(self):
        """Creates all interface widgets"""
        
        # Clear existing widgets
        for widget in self.root.winfo_children():
            if widget != self.notebook:
                widget.destroy()
        
        # Main frame with notebook
        if not hasattr(self, 'notebook'):
            self.notebook = ttk.Notebook(self.root)
            self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Tab 1: Configuration
            self.config_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.config_frame, text=t.get('config_tab'))
            
            # Tab 2: File selection with checkboxes
            self.selection_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.selection_frame, text=t.get('selection_tab'))
            
            # Tab 3: Translation and Progress
            self.progress_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.progress_frame, text=t.get('translation_tab'))
        else:
            # Clear existing tab content
            for widget in self.config_frame.winfo_children():
                widget.destroy()
            for widget in self.selection_frame.winfo_children():
                widget.destroy()
            for widget in self.progress_frame.winfo_children():
                widget.destroy()
        
        self.create_config_tab()
        self.create_selection_tab()
        self.create_progress_tab()
    
    def create_config_tab(self):
        """Creates the configuration tab"""
        
        # Language selector at the top
        lang_selector_frame = ttk.Frame(self.config_frame)
        lang_selector_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(lang_selector_frame, text="🌐 Interface Language:").pack(side=tk.LEFT)
        
        lang_combo = ttk.Combobox(lang_selector_frame, textvariable=self.gui_language,
                                 values=['en - English', 'es - Español'], state="readonly", width=15)
        lang_combo.pack(side=tk.LEFT, padx=10)
        lang_combo.bind('<<ComboboxSelected>>', self.on_gui_language_change)
        
        # Set current value
        current_lang = self.gui_language.get()
        if current_lang == 'en':
            lang_combo.set('en - English')
        else:
            lang_combo.set('es - Español')
        
        # Title
        title_label = tk.Label(self.config_frame, text=t.get('config_title'), 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Frame for Endless Sky directory
        dir_frame = ttk.LabelFrame(self.config_frame, text=t.get('endless_sky_dir'), padding=10)
        dir_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(dir_frame, text=t.get('select_directory')).pack(anchor=tk.W)
        
        dir_input_frame = ttk.Frame(dir_frame)
        dir_input_frame.pack(fill=tk.X, pady=5)
        
        self.dir_entry = ttk.Entry(dir_input_frame, textvariable=self.endless_sky_path, width=60)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(dir_input_frame, text=t.get('browse_button'), command=self.browse_directory).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Frame for language
        lang_frame = ttk.LabelFrame(self.config_frame, text=t.get('target_language'), padding=10)
        lang_frame.pack(fill=tk.X, padx=20, pady=10)
        
        languages = [
            ('es', t.get('languages.es')),
            ('fr', t.get('languages.fr')),
            ('de', t.get('languages.de')),
            ('it', t.get('languages.it')),
            ('pt', t.get('languages.pt')),
            ('ru', t.get('languages.ru')),
            ('zh', t.get('languages.zh')),
            ('ja', t.get('languages.ja'))
        ]
        
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.target_language, 
                                 values=[f"{code} - {name}" for code, name in languages],
                                 state="readonly")
        lang_combo.set(f"es - {t.get('languages.es')}")
        lang_combo.pack(anchor=tk.W)
        
        # Information
        info_frame = ttk.LabelFrame(self.config_frame, text=t.get('information'), padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        info_label = tk.Label(info_frame, text=t.get('info_text'), justify=tk.LEFT, 
                             font=("Courier", 9), bg="lightyellow")
        info_label.pack(fill=tk.BOTH, expand=True)
    
    def on_gui_language_change(self, event=None):
        """Handle GUI language change"""
        selected = event.widget.get()
        if selected.startswith('en'):
            self.change_gui_language('en')
        elif selected.startswith('es'):
            self.change_gui_language('es')
    
    def create_selection_tab(self):
        """Creates the selection tab with real checkboxes and expandable structure"""
        
        # Title
        title_label = tk.Label(self.selection_frame, text=t.get('selection_title'), 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Mass selection buttons frame
        button_frame = ttk.Frame(self.selection_frame)
        button_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Button(button_frame, text=t.get('select_all'), 
                  command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=t.get('deselect_all'), 
                  command=self.deselect_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=t.get('safe_only'), 
                  command=self.select_safe_only).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=t.get('include_special'), 
                  command=self.select_with_special).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=t.get('expand_all'), 
                  command=self.expand_all_folders).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=t.get('collapse_all'), 
                  command=self.collapse_all_folders).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=t.get('refresh'), 
                  command=self.scan_translatable_items).pack(side=tk.RIGHT, padx=5)
        
        # Main frame with expandable structure
        main_frame = ttk.Frame(self.selection_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create frame with scroll for entire structure
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
        
        # Selection information
        info_frame = ttk.Frame(self.selection_frame)
        info_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.selection_info = tk.Label(info_frame, text=t.get('scan_directory'), 
                                      font=("Arial", 10), fg="blue")
        self.selection_info.pack()
    
    def create_progress_tab(self):
        """Creates the progress and translation tab"""
        
        # Title
        title_label = tk.Label(self.progress_frame, text=t.get('translation_title'), 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Status frame
        status_frame = ttk.LabelFrame(self.progress_frame, text=t.get('current_status'), padding=10)
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.status_label = tk.Label(status_frame, text=t.get('ready_to_translate'), 
                                    font=("Arial", 12, "bold"), fg="blue")
        self.status_label.pack()
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(status_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Log frame
        log_frame = ttk.LabelFrame(self.progress_frame, text=t.get('translation_log'), padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, font=("Courier", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Control buttons
        control_frame = ttk.Frame(self.progress_frame)
        control_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.start_button = ttk.Button(control_frame, text=t.get('start_translation'), 
                                      command=self.start_translation, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text=t.get('stop_translation'), 
                                     command=self.stop_translation, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text=t.get('clear_log'), 
                  command=self.clear_log).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text=t.get('save_config'), 
                  command=self.save_config).pack(side=tk.RIGHT, padx=5)
    
    def browse_directory(self):
        """Opens a dialog to select the Endless Sky directory"""
        directory = filedialog.askdirectory(
            title="Select Endless Sky directory",
            initialdir=self.endless_sky_path.get() if self.endless_sky_path.get() else "C:\\"
        )
        if directory:
            self.endless_sky_path.set(directory)
            self.scan_translatable_items()
    
    def get_file_safety_info(self, filename):
        """Determines file safety information"""
        filename_lower = filename.lower()
        
        # Completely safe files (green)
        safe_patterns = ['mission', 'conversation', 'dialog', 'hail', 'job', 'news', 'event', 'campaign']
        if any(pattern in filename_lower for pattern in safe_patterns):
            return ("✅", "green", t.get('safety_descriptions.completely_safe'))
        
        # Special files with particular logic (yellow)
        special_files = ['ships.txt', 'outfits.txt', 'engines.txt', 'weapons.txt', 'power.txt']
        if filename_lower in special_files:
            return ("⚙️", "orange", t.get('safety_descriptions.descriptions_only'))
        
        # Special root files
        if filename_lower in ['map planets.txt', 'dialog phrases.txt']:
            return ("🌟", "blue", t.get('safety_descriptions.special_file'))
        
        # Default, review
        return ("⚠️", "gray", t.get('safety_descriptions.requires_review'))
    
    def is_file_translatable(self, filepath):
        """Determines if a file should really be shown as translatable"""
        filename = filepath.name.lower()
        
        # Specific list of files that should NEVER appear
        excluded_files = [
            'fleets.txt', 'governments.txt', 'systems.txt', 'planets.txt',
            'map systems.txt', 'commodities.txt', 'variants.txt', 'persons.txt',
            'effects.txt', 'hazards.txt', 'formations.txt', 'stars.txt', 'series.txt',
            'derelicts.txt', 'minables.txt', 'start.txt', 'wormhole.txt'
        ]
        
        if filename in excluded_files:
            return False
        
        # Patterns that should NEVER appear
        excluded_patterns = ['derelict', 'variant', 'formation', 'hazard', 'fleet', 'government', 'system']
        if any(pattern in filename for pattern in excluded_patterns):
            return False
        
        # Files we DO want to show
        safe_patterns = ['mission', 'conversation', 'dialog', 'hail', 'job', 'news', 'event', 'campaign']
        if any(pattern in filename for pattern in safe_patterns):
            return True
        
        # Special files we DO want (only with special logic)
        special_files = ['ships.txt', 'outfits.txt', 'engines.txt', 'weapons.txt', 'power.txt']
        if filename in special_files:
            return True
        
        # Allowed root files
        root_files = ['map planets.txt', 'dialog phrases.txt']
        if filename in root_files:
            return True
        
        # If we get here, probably not safe to show the file
        return False
    
    def scan_translatable_items(self):
        """Scans and creates expandable structure with folders and individual files"""
        # Clear current structure
        for widget in self.main_scrollable_frame.winfo_children():
            widget.destroy()
        
        self.all_items.clear()
        
        base_path = self.endless_sky_path.get()
        if not base_path or not os.path.exists(base_path):
            self.selection_info.config(text=t.get('status_messages.invalid_directory'), fg="red")
            return
        
        data_path = Path(base_path) / "data"
        if not data_path.exists():
            self.selection_info.config(text=t.get('status_messages.data_folder_not_found'), fg="red")
            return
        
        total_items = 0
        
        # 1. Create root files section
        root_section = ttk.LabelFrame(self.main_scrollable_frame, text=t.get('root_files'), padding=5)
        root_section.pack(fill=tk.X, padx=5, pady=2)
        
        root_files = ['map planets.txt', 'dialog phrases.txt']
        for filename in root_files:
            file_path = data_path / filename
            if file_path.exists():
                safety_icon, color, description = self.get_file_safety_info(filename)
                item = FileItem(filename, file_path, 'file', safety_icon, True)
                self.all_items.append(item)
                self.create_file_checkbox_in_frame(root_section, item, color, description)
                total_items += 1
        
        # 2. Create folder sections with expandable files
        translatable_folders = [
            'human', 'hai', 'korath', 'wanderer', 'remnant', 'pug', 'quarg', 'coalition', '_ui'
        ]
        
        for folder_name in translatable_folders:
            folder_path = data_path / folder_name
            if folder_path.exists():
                # Scan translatable files in folder
                translatable_files = []
                for file_path in folder_path.glob("*.txt"):
                    if self.is_file_translatable(file_path):
                        translatable_files.append(file_path.name)
                
                if translatable_files:  # Only create section if there are translatable files
                    folder_item = FileItem(folder_name, folder_path, 'folder', self.get_folder_status(folder_name))
                    folder_item.files = translatable_files
                    self.all_items.append(folder_item)
                    
                    # Create expandable section for folder
                    self.create_folder_section(folder_item, folder_path)
                    total_items += 1 + len(translatable_files)
        
        # Update selection information
        self.selection_info.config(
            text=t.get('status_messages.files_found', count=total_items),
            fg="green"
        )
    
    # Continue with remaining methods...
    def get_folder_status(self, folder_name):
        """Get status icon for folder"""
        if folder_name in ['_ui']:
            return "🎨"
        elif folder_name in ['human']:
            return "👥"
        else:
            return "📁"
    
    def create_folder_section(self, folder_item, folder_path):
        """Creates an expandable section for a folder"""
        folder_frame = ttk.LabelFrame(self.main_scrollable_frame, 
                                     text=f"{folder_item.status} {folder_item.name}", padding=5)
        folder_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Folder checkbox and expand button
        header_frame = ttk.Frame(folder_frame)
        header_frame.pack(fill=tk.X)
        
        # Folder checkbox
        folder_checkbox = ttk.Checkbutton(header_frame, variable=folder_item.selected,
                                         command=lambda: self.on_folder_selection_change(folder_item))
        folder_checkbox.pack(side=tk.LEFT)
        
        # Expand/collapse button
        expand_button = ttk.Button(header_frame, text="▶", width=3,
                                  command=lambda: self.toggle_folder_expansion(folder_item, folder_frame, expand_button))
        expand_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(header_frame, text=f"({len(folder_item.files)} files)", 
                 font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        
        # Container for files (initially hidden)
        files_container = ttk.Frame(folder_frame)
        folder_item.files_container = files_container
        folder_item.expand_button = expand_button
        
        # Create file items for this folder
        for filename in folder_item.files:
            file_path = folder_path / filename
            safety_icon, color, description = self.get_file_safety_info(filename)
            file_item = FileItem(filename, file_path, 'file', safety_icon, True, folder_item)
            folder_item.files.append(file_item)  # Add to folder's file list
            self.all_items.append(file_item)  # Add to global list
    
    def toggle_folder_expansion(self, folder_item, folder_frame, expand_button):
        """Toggles folder expansion state"""
        if folder_item.expanded:
            # Collapse
            folder_item.files_container.pack_forget()
            expand_button.config(text="▶")
            folder_item.expanded = False
        else:
            # Expand
            folder_item.files_container.pack(fill=tk.X, padx=20, pady=5)
            
            # Clear and recreate file checkboxes
            for widget in folder_item.files_container.winfo_children():
                widget.destroy()
            
            for file_item in folder_item.files:
                if isinstance(file_item, FileItem):  # Make sure it's a FileItem, not string
                    safety_icon, color, description = self.get_file_safety_info(file_item.name)
                    self.create_file_checkbox_in_frame(folder_item.files_container, file_item, color, description)
            
            expand_button.config(text="▼")
            folder_item.expanded = True
    
    def create_file_checkbox_in_frame(self, parent_frame, file_item, color, description):
        """Creates a checkbox for a file in the specified frame"""
        file_frame = ttk.Frame(parent_frame)
        file_frame.pack(fill=tk.X, pady=1)
        
        checkbox = ttk.Checkbutton(file_frame, variable=file_item.selected)
        checkbox.pack(side=tk.LEFT)
        
        # Icon and name
        label = tk.Label(file_frame, text=f"{file_item.status} {file_item.name}", 
                        fg=color, font=("Arial", 9))
        label.pack(side=tk.LEFT, padx=5)
        
        # Description
        desc_label = tk.Label(file_frame, text=f"({description})", 
                             fg="gray", font=("Arial", 8))
        desc_label.pack(side=tk.LEFT, padx=5)
    
    def on_folder_selection_change(self, folder_item):
        """Handles folder selection change"""
        # When folder is selected/deselected, update all its files
        for file_item in folder_item.files:
            if isinstance(file_item, FileItem):
                file_item.selected.set(folder_item.selected.get())
    
    def select_all(self):
        """Selects all items"""
        for item in self.all_items:
            item.selected.set(True)
    
    def deselect_all(self):
        """Deselects all items"""
        for item in self.all_items:
            item.selected.set(False)
    
    def select_safe_only(self):
        """Selects only completely safe files"""
        for item in self.all_items:
            if item.status == "✅":  # Only green/safe files
                item.selected.set(True)
            else:
                item.selected.set(False)
    
    def select_with_special(self):
        """Selects safe files and special files"""
        for item in self.all_items:
            if item.status in ["✅", "⚙️", "🌟"]:  # Safe, special, and root special
                item.selected.set(True)
            else:
                item.selected.set(False)
    
    def expand_all_folders(self):
        """Expands all folders"""
        for item in self.all_items:
            if item.item_type == 'folder' and hasattr(item, 'expand_button'):
                if not item.expanded:
                    item.expand_button.invoke()
    
    def collapse_all_folders(self):
        """Collapses all folders"""
        for item in self.all_items:
            if item.item_type == 'folder' and hasattr(item, 'expand_button'):
                if item.expanded:
                    item.expand_button.invoke()
    
    def start_translation(self):
        """Starts the translation process"""
        if not self.endless_sky_path.get():
            messagebox.showerror("Error", t.get('error_messages.invalid_directory'))
            return
        
        # Get selected files
        selected_files = []
        for item in self.all_items:
            if item.selected.get() and item.item_type == 'file':
                selected_files.append(str(item.path))
        
        if not selected_files:
            messagebox.showwarning("Warning", t.get('error_messages.no_files_selected'))
            return
        
        # Configure UI for translation
        self.is_translating = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.status_label.config(text=t.get('status_messages.preparing_translation'), fg="orange")
        
        # Get target language code
        target_lang = self.target_language.get().split(' - ')[0]
        
        # Start translation in separate thread
        self.translation_thread = threading.Thread(
            target=self.run_translation,
            args=(selected_files, target_lang)
        )
        self.translation_thread.daemon = True
        self.translation_thread.start()
    
    def run_translation(self, selected_files, target_language):
        """Runs translation in background thread"""
        try:
            # Initialize translator
            self.translator = EndlessSkyTranslatorFixed(self.endless_sky_path.get(), target_language)
            
            total_files = len(selected_files)
            
            for i, file_path in enumerate(selected_files):
                if not self.is_translating:
                    break
                
                # Update progress
                progress = (i / total_files) * 100
                self.translation_queue.put(('progress', progress))
                self.translation_queue.put(('status', t.get('status_messages.translating_file', file=os.path.basename(file_path))))
                self.translation_queue.put(('log', f"📝 {t.get('status_messages.translating_file', file=os.path.basename(file_path))}"))
                
                # Translate file
                result = self.translator.translate_file(file_path)
                if result:
                    self.translation_queue.put(('log', f"✅ {os.path.basename(file_path)} - OK"))
                else:
                    self.translation_queue.put(('log', f"❌ {os.path.basename(file_path)} - Error"))
            
            if self.is_translating:
                self.translation_queue.put(('complete', t.get('status_messages.translation_completed')))
            else:
                self.translation_queue.put(('stopped', t.get('status_messages.translation_stopped')))
                
        except Exception as e:
            self.translation_queue.put(('error', t.get('status_messages.translation_error', error=str(e))))
    
    def stop_translation(self):
        """Stops the translation process"""
        self.is_translating = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
    
    def check_queue(self):
        """Checks for messages from translation thread"""
        try:
            while True:
                message_type, message = self.translation_queue.get_nowait()
                
                if message_type == 'progress':
                    self.progress_bar['value'] = message
                elif message_type == 'status':
                    self.status_label.config(text=message, fg="orange")
                elif message_type == 'log':
                    self.log_text.insert(tk.END, message + "\n")
                    self.log_text.see(tk.END)
                elif message_type == 'complete':
                    self.status_label.config(text=message, fg="green")
                    self.stop_translation()
                    self.progress_bar['value'] = 100
                elif message_type == 'stopped':
                    self.status_label.config(text=message, fg="red")
                    self.stop_translation()
                elif message_type == 'error':
                    self.status_label.config(text=message, fg="red")
                    self.stop_translation()
                    messagebox.showerror("Error", message)
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_queue)
    
    def clear_log(self):
        """Clears the translation log"""
        self.log_text.delete(1.0, tk.END)
    
    def save_config(self):
        """Saves current configuration"""
        try:
            config = {
                'endless_sky_path': self.endless_sky_path.get(),
                'target_language': self.target_language.get(),
                'gui_language': self.gui_language.get()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Success", t.get('error_messages.config_save_success'))
        except Exception as e:
            messagebox.showerror("Error", t.get('error_messages.config_save_error', error=str(e)))
    
    def load_config(self):
        """Loads saved configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.endless_sky_path.set(config.get('endless_sky_path', ''))
                self.target_language.set(config.get('target_language', 'es'))
                gui_lang = config.get('gui_language', 'en')
                self.gui_language.set(gui_lang)
                t.set_language(gui_lang)
        except Exception as e:
            print(f"Error loading config: {e}")

def main():
    """Main function to run the application"""
    root = tk.Tk()
    
    # Configure style
    style = ttk.Style()
    if "clam" in style.theme_names():
        style.theme_use("clam")
    
    app = TranslatorGUIImproved(root)
    root.mainloop()

if __name__ == "__main__":
    main()
