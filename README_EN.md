# 🌍 Endless Sky Automatic Translator (Advanced GUI Version)

This advanced application automatically translates Endless Sky game content from English to any target language using **intelligent and conservative logic** that preserves game functionality. Now featuring a **powerful multilingual GUI with granular file selection**.

## ✨ Features

### 🎯 Smart Translation
- **Real checkboxes** for intuitive file/folder selection
- **Intelligent filtering** that shows only translatable files
- **Safety-first approach** that hides dangerous files
- **Visual safety indicators** with color coding
- **Selective translation** of only visible content

### 🛡️ Guaranteed Safety
- **✅ GREEN**: Completely safe files (missions, dialogs)
- **⚙️ YELLOW**: Special files (ships, outfits) - descriptions only
- **🔒 HIDDEN**: Dangerous files are automatically excluded

### 🌐 Multilingual Interface
- **English** and **Spanish** interface languages
- **Easy language switching** in the configuration tab
- **Multiple target languages** supported for translation

### 📋 Supported File Types
- ✅ Missions and conversations
- ✅ Ship descriptions (safe parts only)
- ✅ Outfit/engine/weapon descriptions
- ✅ User interface text
- ✅ Communications and news
- ✅ Planet descriptions

## 🚀 Quick Start

### 1. Run the Application
```bash
python run_gui.py
```

### 2. Configure
1. Select your Endless Sky installation directory
2. Choose your preferred interface language (English/Spanish)
3. Select target language for translation

### 3. Select Files
1. Browse the smart file tree
2. Use checkboxes to select what to translate
3. Use quick selection buttons (Safe Only, Include Special, etc.)

### 4. Translate
1. Click "Start Translation"
2. Monitor progress in real-time
3. Review the translation log

## 📁 File Structure

```
traductor_automatico/
├── run_gui.py                      # 🚀 Main launcher
├── translator_gui_multilingual.py  # 🖥️ Enhanced multilingual GUI
├── translations.py                 # 🌐 Translation system
├── translator.py                   # 🔧 Core translation engine
├── BUILD_GUIDE_EN.md              # 🏗️ Build instructions (English)
├── BUILD_GUIDE.md                 # 🏗️ Build instructions (Spanish)
└── requirements.txt               # 📦 Python dependencies
```

## 🔧 Installation

### Prerequisites
- Python 3.6 or higher
- Internet connection for translation services

### Dependencies
```bash
pip install -r requirements.txt
```

### Required packages:
- `tkinter` (usually included with Python)
- `googletrans==4.0.0rc1`
- `requests`
- `pathlib`

## 🛡️ Safety Features

### Automatic File Filtering
The application automatically:
- **Hides dangerous files** that could break the game
- **Shows only safe content** for translation
- **Provides visual indicators** for file safety levels
- **Prevents accidental game-breaking changes**

### Smart Translation Logic
- **Missions**: Full translation of story content
- **Ships**: Only description fields (preserves technical data)
- **Outfits**: Only description fields (preserves stats)
- **UI**: Complete interface translation
- **Dialogs**: Full conversation translation

## 🌍 Supported Languages

### Interface Languages
- 🇺🇸 **English** - Full interface
- 🇪🇸 **Spanish** - Full interface

### Translation Target Languages
- 🇪🇸 Spanish
- 🇫🇷 French
- 🇩🇪 German
- 🇮🇹 Italian
- 🇵🇹 Portuguese
- 🇷🇺 Russian
- 🇨🇳 Chinese
- 🇯🇵 Japanese

## 🏗️ Building Executables

See `BUILD_GUIDE_EN.md` for detailed instructions on creating standalone executables.

### Quick Build (Windows)
```bash
python build_exe.py
```

### Quick Build (Linux)
```bash
./build_appimage.sh
```

## 🔍 How It Works

### 1. Directory Scanning
- Scans the Endless Sky `data/` directory
- Identifies translatable file patterns
- Filters out dangerous or system files
- Creates an organized, expandable file tree

### 2. Safe Selection
- Color-coded safety indicators
- Smart defaults for safe translation
- Expandable folder structure
- Individual file control

### 3. Translation Process
- Creates automatic backups
- Translates only selected content
- Preserves game mechanics and technical data
- Provides real-time progress feedback

## ⚙️ Configuration

The application saves your preferences in `translator_config.json`:
- Endless Sky directory path
- Interface language preference
- Target translation language
- File selection preferences

## 🔧 Troubleshooting

### Common Issues

#### "Directory not found"
- Ensure you've selected the correct Endless Sky installation folder
- Look for the folder containing `Endless Sky.exe` and a `data/` subfolder

#### "No translatable files found"
- Verify your Endless Sky installation is complete
- Check that the `data/` folder contains game files

#### "Translation service error"
- Check your internet connection
- Translation services may have temporary limitations

#### "Interface in wrong language"
- Use the language selector in the Configuration tab
- The interface will refresh automatically

### Performance Tips
- **Select specific files** instead of entire folders for faster translation
- **Use "Safe Only"** selection for guaranteed stability
- **Close other applications** during large translations

## 🤝 Contributing

### Adding Interface Languages
1. Edit `translations.py`
2. Add your language to the translation dictionary
3. Update the language selector in the GUI

### Improving Safety Filters
1. Edit the file filtering logic in `translator_gui_multilingual.py`
2. Test thoroughly with different Endless Sky versions
3. Ensure no game-breaking files are included

## 📄 License

This project is open source. Please respect the Endless Sky game's license and terms of use.

## ⚠️ Disclaimer

- **Always backup your game files** before translation
- **This tool modifies game n** - use at your own risk
- **Test translations** in a separate game installation first
- **The developers are not responsible** for any game corruption

## 🎮 About Endless Sky

Endless Sky is an open-source space exploration and combat game. Learn more at:
- Official website: https://endless-sky.github.io/
- GitHub repository: https://github.com/endless-sky/endless-sky

---

**Happy translating!** 🌟
