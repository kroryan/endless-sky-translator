#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Translation system for Endless Sky Translator GUI
Multi-language support for the application interface
"""

import json
import os
from typing import Dict, Any

class TranslationManager:
    """Manages translations for the GUI application"""
    
    def __init__(self, default_language='en'):
        self.current_language = default_language
        self.translations = {}
        self.load_translations()
    
    def load_translations(self):
        """Load all available translations"""
        self.translations = {
            'en': {
                # Window titles and main sections
                'window_title': 'Endless Sky Translator - Enhanced Interface',
                'config_tab': '📁 Configuration',
                'selection_tab': '☑️ File Selection',
                'translation_tab': '🚀 Translation',
                
                # Configuration tab
                'config_title': '🌍 Translator Configuration',
                'endless_sky_dir': 'Endless Sky Directory',
                'select_directory': 'Select the Endless Sky installation directory:',
                'browse_button': '📁 Browse',
                'target_language': 'Target Language',
                'information': 'ℹ️ Information',
                
                # Language options
                'languages': {
                    'es': 'Spanish',
                    'fr': 'French', 
                    'de': 'German',
                    'it': 'Italian',
                    'pt': 'Portuguese',
                    'ru': 'Russian',
                    'zh': 'Chinese',
                    'ja': 'Japanese'
                },
                
                # Information text
                'info_text': '''
🎯 ENHANCED VERSION FEATURES:
• ☑️ Real checkboxes for selecting files/folders
• 🎯 Shows only ACTUALLY translatable files
• 🛡️ Smart filtering that avoids dangerous files
• 📊 Visual safety indicators by colors
• 🚀 Selective translation of visible content only

🛡️ GUARANTEED SAFETY:
• ✅ GREEN: Completely safe files (missions, dialogs)
• ⚙️ YELLOW: Special files (ships, outfits) - descriptions only
• 🔒 NOT SHOWN: Dangerous files are hidden

📋 FILES THAT GET TRANSLATED:
• ✅ Missions and conversations (missions, conversations)
• ✅ Ship descriptions (ships.txt descriptions only)
• ✅ Outfit/engine/weapon descriptions (descriptions only)
• ✅ User interface (_ui)
• ✅ Communications and news (hail, news)
• ✅ Planet dialogs (map planets.txt descriptions only)

❌ NEVER TRANSLATED:
• Technical names of ships, outfits or systems
• Files affecting gameplay (fleets, governments)
• Coordinates, effects and technical data
                ''',
                
                # Selection tab
                'selection_title': '☑️ Granular File Selection',
                'select_all': '☑️ Select All',
                'deselect_all': '☐ Deselect All',
                'safe_only': '🛡️ Safe Only',
                'include_special': '⚙️ Include Special',
                'expand_all': '📂 Expand All',
                'collapse_all': '📁 Collapse All',
                'refresh': '🔄 Refresh',
                'scan_directory': 'Scan directory to see translatable files',
                'root_files': '📁 Root Files',
                
                # Translation tab
                'translation_title': '🚀 Translation Process',
                'current_status': '📊 Current Status',
                'ready_to_translate': '⏸️ Ready to translate',
                'translation_log': '📝 Translation Log',
                'start_translation': '🚀 Start Translation',
                'stop_translation': '⏹️ Stop',
                'clear_log': '🗑️ Clear Log',
                'save_config': '💾 Save Config',
                
                # Status messages
                'status_messages': {
                    'invalid_directory': '⚠️ Select a valid Endless Sky directory',
                    'data_folder_not_found': '❌ Data folder not found in directory',
                    'files_found': '✅ Found {count} translatable elements (folders and individual files)',
                    'translation_completed': '✅ Translation completed successfully!',
                    'translation_error': '❌ Translation error: {error}',
                    'translation_stopped': '⏹️ Translation stopped by user',
                    'translating_file': '📝 Translating: {file}',
                    'preparing_translation': '🔄 Preparing translation...',
                    'creating_backup': '💾 Creating backup...',
                    'translation_in_progress': '🚀 Translation in progress...'
                },
                
                # Error messages
                'error_messages': {
                    'invalid_directory': 'Please select a valid Endless Sky directory',
                    'no_files_selected': 'Please select at least one folder or file to translate',
                    'config_save_success': 'Configuration saved successfully',
                    'config_save_error': 'Error saving configuration: {error}',
                    'translation_error': 'Translation error: {error}'
                },
                
                # Safety descriptions
                'safety_descriptions': {
                    'completely_safe': 'Completely safe',
                    'descriptions_only': 'Descriptions only',
                    'special_file': 'Special file',
                    'requires_review': 'Requires review'
                }
            },
            
            'es': {
                # Window titles and main sections
                'window_title': 'Traductor de Endless Sky - Interfaz Mejorada',
                'config_tab': '📁 Configuración',
                'selection_tab': '☑️ Selección de Archivos',
                'translation_tab': '🚀 Traducción',
                
                # Configuration tab
                'config_title': '🌍 Configuración del Traductor',
                'endless_sky_dir': 'Directorio de Endless Sky',
                'select_directory': 'Selecciona el directorio de instalación de Endless Sky:',
                'browse_button': '📁 Buscar',
                'target_language': 'Idioma de Destino',
                'information': 'ℹ️ Información',
                
                # Language options
                'languages': {
                    'es': 'Español',
                    'fr': 'Francés',
                    'de': 'Alemán',
                    'it': 'Italiano',
                    'pt': 'Portugués',
                    'ru': 'Ruso',
                    'zh': 'Chino',
                    'ja': 'Japonés'
                },
                
                # Information text
                'info_text': '''
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
                ''',
                
                # Selection tab
                'selection_title': '☑️ Selección Granular de Archivos',
                'select_all': '☑️ Seleccionar Todo',
                'deselect_all': '☐ Deseleccionar Todo',
                'safe_only': '🛡️ Solo Seguros',
                'include_special': '⚙️ Incluir Especiales',
                'expand_all': '📂 Expandir Todo',
                'collapse_all': '📁 Contraer Todo',
                'refresh': '🔄 Actualizar',
                'scan_directory': 'Escanea el directorio para ver archivos traducibles',
                'root_files': '📁 Archivos Raíz',
                
                # Translation tab
                'translation_title': '🚀 Proceso de Traducción',
                'current_status': '📊 Estado Actual',
                'ready_to_translate': '⏸️ Listo para traducir',
                'translation_log': '📝 Log de Traducción',
                'start_translation': '🚀 Iniciar Traducción',
                'stop_translation': '⏹️ Detener',
                'clear_log': '🗑️ Limpiar Log',
                'save_config': '💾 Guardar Config',
                
                # Status messages
                'status_messages': {
                    'invalid_directory': '⚠️ Selecciona un directorio válido de Endless Sky',
                    'data_folder_not_found': '❌ No se encontró la carpeta data en el directorio',
                    'files_found': '✅ Encontrados {count} elementos traducibles (carpetas y archivos individuales)',
                    'translation_completed': '✅ ¡Traducción completada con éxito!',
                    'translation_error': '❌ Error de traducción: {error}',
                    'translation_stopped': '⏹️ Traducción detenida por el usuario',
                    'translating_file': '📝 Traduciendo: {file}',
                    'preparing_translation': '🔄 Preparando traducción...',
                    'creating_backup': '💾 Creando respaldo...',
                    'translation_in_progress': '🚀 Traducción en progreso...'
                },
                
                # Error messages
                'error_messages': {
                    'invalid_directory': 'Por favor selecciona un directorio válido de Endless Sky',
                    'no_files_selected': 'Por favor selecciona al menos una carpeta o archivo para traducir',
                    'config_save_success': 'Configuración guardada correctamente',
                    'config_save_error': 'Error al guardar configuración: {error}',
                    'translation_error': 'Error de traducción: {error}'
                },
                
                # Safety descriptions
                'safety_descriptions': {
                    'completely_safe': 'Completamente seguro',
                    'descriptions_only': 'Solo descripciones',
                    'special_file': 'Archivo especial',
                    'requires_review': 'Requiere revisión'
                }
            }
        }
    
    def set_language(self, language_code):
        """Set the current language"""
        if language_code in self.translations:
            self.current_language = language_code
    
    def get(self, key, **kwargs):
        """Get translated text for the current language"""
        keys = key.split('.')
        value = self.translations.get(self.current_language, self.translations['en'])
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, key)
            else:
                return key
        
        # Format with provided kwargs if needed
        if isinstance(value, str) and kwargs:
            try:
                return value.format(**kwargs)
            except:
                return value
        
        return value
    
    def get_available_languages(self):
        """Get list of available languages"""
        return list(self.translations.keys())
    
    def get_language_name(self, code):
        """Get the display name for a language"""
        return self.get(f'languages.{code}')

# Global translation manager instance
translator = TranslationManager()
