# Endless Sky Automatic Translator (Advanced GUI Version)

This advanced script automatically translates Endless Sky game content from English to Spanish using **intelligent and conservative logic** that preserves game functionality. Now featuring a **powerful GUI with granular file selection**.

## 🎯 Conservative Approach

The script uses a **conservative and selective** approach to avoid breaking the game:

### ✅ What IS translated:
- **User Interface** (`_ui/`): Menus, buttons, labels
- **Dialogues and missions**: Player-visible text
- **Conversations**: NPC interactions
- **News and events**: Narrative information
- **Planet descriptions**: Only descriptive text (map planets.txt)
- **Ship descriptions**: Only visible descriptions in ships.txt
- **Outfit descriptions**: Only visible descriptions in outfits.txt, engines.txt, weapons.txt
- **Main campaigns**: Safe faction storylines

### 🚫 What is NOT translated:
- **Technical names** of ships, outfits, planets, systems
- **Configuration files** with complex logic (fleets.txt, governments.txt)
- **Coordinates and parameters** technical data
- **IDs and references** internal to the game
- **Complex factions** with special logic
- **Balance and mechanics** files

## 🛡️ Safety Features

- **Preserves functionality**: Does not modify technical elements
- **Maintains compatibility**: With mods and updates
- **Safe encoding**: UTF-8 with BOM for maximum compatibility
- **Intelligent filtering**: Only shows translatable files
- **Granular control**: Select individual files or entire folders

## ✨ NEW! Advanced GUI Features

### 🎮 Granular File Selection
- **📂 Expandable folders** with individual file checkboxes
- **☑️ Real checkboxes** for precise control
- **🔗 Smart folder selection** (selecting folder = all files)
- **🎯 Individual file selection** within folders
- **📊 Real-time selection counter**

### 🛡️ Visual Safety Indicators
- **✅ GREEN**: Completely safe files (missions, dialogues)
- **⚙️ YELLOW**: Special files with custom logic (ships, outfits)
- **🌟 BLUE**: Special root files (map planets.txt)
- **⚠️ GRAY**: Files requiring review

### ⚡ Smart Selection Tools
- **☑️ Select All** - Mark all available elements
- **☐ Deselect All** - Clear all selections
- **🛡️ Safe Only** - Select only green (completely safe) files
- **⚙️ Include Special** - Select safe + special files
- **📂 Expand All** - Open all folder views
- **📁 Collapse All** - Close all folder views

## 📋 Requirements

- **Python 3.6 or higher**
- **Internet connection** (for Google Translate API)
- **Endless Sky game installed** (Steam, GOG, or manual installation)

## 🚀 Installation and Usage

### Option 1: Advanced GUI (Recommended) 🎨

1. **Double-click** `Ejecutar_GUI.bat` or run `python run_gui.py`
2. **📁 Browse**: Select your Endless Sky installation directory
3. **🔄 Update**: Scan for translatable files
4. **📂 Expand**: Open folders to see individual files
5. **☑️ Select**: Choose specific files or entire folders
   - **Folder checkbox** = Selects ALL files in that folder
   - **File checkbox** = Selects ONLY that specific file
6. **🚀 Translate**: Start the translation process
7. **📊 Monitor**: Watch progress and logs in real-time

#### 🎯 Usage Examples:
- **Translate everything safe**: Click "🛡️ Safe Only" → "🚀 Translate"
- **Translate one faction**: Expand "human" folder → Check folder checkbox
- **Translate only missions**: Expand folders → Select only "*missions.txt" files
- **Custom mix**: Select some folders + individual files from others

### Option 2: Command Line

```bash
# Install dependencies
pip install googletrans==4.0.0rc1 chardet

# Run the translator
python translator.py
```

## 🎨 Graphical Interface Features

- **📁 Directory Selection**: Browse and select your Endless Sky installation
- **🌍 Language Selection**: Choose target language (Spanish, French, German, etc.)
- **📋 File Selection**: Visual tree to select specific folders and files
- **🛡️ Safety Indicators**: Color-coded safety levels for each file
- **📊 Real-time Progress**: Live translation progress and detailed logging
- **💾 Configuration Saving**: Save and load your preferences

### First-Time Setup
If this is your first time using the translator, you may need to:
1. **Install Python** from [python.org](https://python.org) if not already installed
2. **Verify pip is working** by running `pip --version`
3. **Consider using a virtual environment** (optional but recommended):
   ```bash
   python -m venv translator_env
   # Windows:
   translator_env\Scripts\activate
   # macOS/Linux:
   source translator_env/bin/activate
   ```

## 🛠️ Configuration

### Changing Endless Sky Directory
By default, the script looks for Endless Sky in the standard Steam installation directory:
```
d:\Program Files (x86)\Steam\steamapps\common\Endless Sky
```

To change this, edit the `base_path` variable in `translator.py`:

```python
def main():
    # Change this path to your Endless Sky installation
    base_path = r"C:\Your\Custom\Path\To\Endless Sky"
    target_language = 'es'  # Your desired language
```

**Common Endless Sky Locations:**
- **Steam (Windows)**: `C:\Program Files (x86)\Steam\steamapps\common\Endless Sky`
- **Steam (macOS)**: `~/Library/Application Support/Steam/steamapps/common/Endless Sky`
- **Steam (Linux)**: `~/.steam/steam/steamapps/common/Endless Sky`
- **GOG (Windows)**: `C:\GOG Games\Endless Sky`
- **Manual Installation**: Wherever you extracted the game files

### Changing Target Language
The translator supports any language supported by Google Translate. Edit the `target_language` variable:

```python
target_language = 'es'  # Spanish
target_language = 'fr'  # French
target_language = 'de'  # German
target_language = 'it'  # Italian
target_language = 'pt'  # Portuguese
target_language = 'ru'  # Russian
target_language = 'ja'  # Japanese
target_language = 'ko'  # Korean
target_language = 'zh'  # Chinese
# ... and many more
```

## 🧠 How It Works

### Intelligent Content Analysis
The translator uses sophisticated pattern matching to determine what should and shouldn't be translated:

1. **Preserves Technical Elements**:
   - Ship, outfit, planet, and system names
   - Coordinates and numerical data
   - File paths and technical identifiers
   - Game variables and placeholders (like `<planet>`, `<npc>`)

2. **Translates Player Content**:
   - Dialog text (marked with backticks: `` `Hello, captain!` ``)
   - Planet descriptions and spaceport descriptions
   - Mission briefings and conversations
   - UI labels and button text
   - Help tooltips and interface elements

3. **Smart Text Processing**:
   - Preserves keyboard shortcuts (like `_Enter`, `_Quit`)
   - Maintains game variables within text
   - Handles special characters properly
   - Removes accents for game compatibility when needed

### File Processing Strategy

The translator processes files in a specific order:

1. **Priority Files** (processed first):
   - `map planets.txt` - Planet descriptions and names
   - `dialog phrases.txt` - Generic dialog phrases

2. **Faction Folders** (processed by importance):
   - `human/` - Main human storyline content
   - `hai/`, `korath/`, `wanderer/`, `remnant/` - Major alien races
   - `pug/`, `quarg/`, `coalition/` - Other significant factions
   - All other faction folders

3. **UI Elements**:
   - `_ui/` folder - Interface translations

### Plugin Structure Creation
The translator creates a complete Endless Sky plugin with:
- Proper `plugin.txt` metadata file
- Organized data structure matching the original game
- UTF-8 encoding for international characters
- Version tracking and authorship information

## 📁 Files and Folders Translated

### Core Game Files
- **`map planets.txt`** - Planet descriptions, spaceport descriptions, and visible planet attributes
- **`dialog phrases.txt`** - Generic phrases used throughout the game

### Faction Content Folders
Each faction folder contains missions, conversations, and storylines:
- **`human/`** - Main human storyline, Free Worlds, Republic, etc.
- **`hai/`** - Hai alien race content
- **`korath/`** - Korath alien race content  
- **`wanderer/`** - Wanderer alien race content
- **`remnant/`** - Remnant alien race content
- **`pug/`** - Pug alien race content
- **`quarg/`** - Quarg alien race content
- **`coalition/`** - Coalition alien race content
- **Other factions**: `drak/`, `gegno/`, `avgi/`, `bunrodea/`, `iije/`, `incipias/`, `kahet/`, `rulei/`, `sheragi/`, `successors/`, `vyrmeid/`, `whispering void/`

### UI Elements
- **`_ui/`** - Interface elements, menus, buttons, and tooltips

## 🎮 Using the Translation in Game

After running the translator:

1. **Start Endless Sky**
2. **Go to Preferences → Plugins**
3. **Enable "Traducción al Español"** (or your target language)
4. **Restart the game**
5. **Enjoy the translated content!**

The translation appears as a plugin, so you can easily:
- **Enable/disable** it without affecting the base game
- **Keep the original English** files intact
- **Update or modify** the translation by re-running the script

## ⚡ Performance and Limitations

### Translation Quality
- **Automatic translation** may not be perfect for context-specific terms
- **Game-specific terminology** might need manual adjustment
- **Cultural references** may not translate well

### Technical Limitations
- **Google Translate rate limits** - the script includes delays to prevent being blocked
- **Internet required** - translation happens online
- **Large files** may take considerable time to process

### Encoding Considerations
- **Accents removed** from final output for maximum game compatibility
- **Special characters** like ñ, ç are preserved when safe
- **UTF-8 encoding** used throughout for international support

## 🔧 Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'googletrans'"**
- Solution: Run `pip install -r requirements.txt`

**"FileNotFoundError: Could not find Endless Sky directory"**
- Solution: Edit the `base_path` in `translator.py` to point to your installation

**"Translation failed" errors**
- Solution: Check internet connection, Google Translate may be temporarily unavailable

**Game doesn't show translated text**
- Solution: Ensure the plugin is enabled in Preferences → Plugins and restart the game

### Advanced Configuration

**Modifying Translation Patterns**:
The script uses regex patterns to identify translatable content. Advanced users can modify:
- `translatable_text_indicators` - patterns for content that should be translated
- `never_translate_patterns` - patterns for content that should never be translated

**Custom Text Processing**:
The `normalize_text_for_game()` function handles accent removal and character normalization. You can modify this for your language's specific needs.

## 📊 Technical Details

### Dependencies
- **`googletrans==3.1.0a0`** - Google Translate API wrapper
- **`deep-translator==1.11.4`** - Alternative translation backend
- **`requests>=2.25.0`** - HTTP requests for translation services
- **`chardet>=4.0.0`** - Character encoding detection

### File Handling
- **Automatic encoding detection** using chardet
- **UTF-8 output** with fallback handling
- **Path normalization** for cross-platform compatibility
- **Atomic file operations** to prevent corruption

### Memory Management
- **Streaming file processing** for large files
- **Garbage collection** between major operations
- **Error recovery** to continue processing after failures

## 🤝 Contributing

Want to improve the translator? Consider:
- **Adding new language-specific text processing rules**
- **Improving pattern matching for better content detection**
- **Adding support for additional file types**
- **Creating language-specific character handling**

## 📄 License and Credits

This translator is provided as-is for the Endless Sky community. Please respect:
- **Endless Sky's open-source license**
- **Google Translate's terms of service**
- **Rate limiting** to avoid overloading translation services

---

**Happy translating! May your Endless Sky adventures be accessible to players worldwide! 🌟**
