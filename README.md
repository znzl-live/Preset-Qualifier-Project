# Preset Qualifier Project

A modular Python application for processing, analyzing, and qualifying VST presets using audio feature extraction and machine learning techniques.

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** (recommended 3.12)
- **REAPER** (for audio rendering)
- **VST Plugins** (Serum recommended)

### Installation

1. **Clone or download** this project
2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure REAPER** for Python integration (see detailed setup below)

### Usage

The workflow consists of three main steps:

1. **Clean & Prepare Data:**
   ```bash
   python scripts/clean_presets.py
   ```

2. **Setup REAPER Project & Render Audio:**
   - Open REAPER
   - Run the project setup script (manual step)
   - Render audio stems

3. **Analyze & Qualify:**
   ```bash
   python scripts/analyze_audio.py
   python scripts/sort_presets.py
   ```

## 📋 Detailed Workflow

### Step 1: Data Preparation

Place your raw VST presets (`.fxp`, `.serumpreset`) in `data/source_presets/`, then run:

```bash
python scripts/clean_presets.py
```

This creates:
- `data/clean_presets/` - Sanitized preset files
- `data/metadata.csv` - Preset metadata with categories

### Step 2: Audio Rendering (REAPER)

1. **Setup REAPER Project:**
   - Open REAPER
   - Go to `Actions > Show action list... > ReaScript: Load...`
   - Select and run `src/data_processing/project_setup.py`
   - This creates tracks, loads Serum, and adds MIDI notes

2. **Manual Preset Loading:**
   - Track 1: Load first preset
   - Track 2+: Click "next preset" arrow
   - Repeat for all tracks

3. **Render Audio:**
   - Select all tracks
   - `File > Render...`
   - Source: "Selected tracks (stems)"
   - Directory: `data/previews/`
   - Uncheck "Mute master" and "Create subdirectory"

### Step 3: Analysis & Qualification

```bash
# Analyze rendered audio
python scripts/analyze_audio.py

# Sort and rename presets by quality score
python scripts/sort_presets.py
```

Results are organized in `output/` with subfolders 1-5 (best to worst).

## ⚙️ Configuration

All settings are managed through `config/default.yaml`:

- **Paths:** Data directories, output locations
- **VST:** Plugin names and supported formats
- **Audio:** Sample rates, note assignments
- **Categories:** Preset type detection rules

## 🏛️ Architecture Overview

### Core Modules

- **`config/`** - Centralized configuration management
- **`data_processing/`** - Preset cleaning and categorization
- **`audio_analysis/`** - Feature extraction and diagnosis
- **`qualification/`** - Scoring and organization
- **`utils/`** - Logging and shared utilities

### Key Features

- **Modular Design:** Each component has a single responsibility
- **Configuration-Driven:** No hardcoded paths or settings
- **Error Handling:** Comprehensive logging and error recovery
- **Extensible:** Easy to add new analysis features or categories

## 🔧 Advanced Configuration

### Custom Categories

Edit `config/default.yaml` to add new preset categories:

```yaml
categories:
  MY_TYPE:
    keywords: ["my", "custom"]
    note: 60
    subcategory: "Custom"
    preview_length_ms: 5000
```

### Audio Features

The system extracts 10+ audio features:
- Tonalness & pitch detection
- Attack time analysis
- Spectral characteristics
- Dynamic range assessment
- Rhythmic density

## 🧪 Testing

Run tests with:
```bash
python -m pytest tests/
```

## 📚 API Reference

### Core Classes

- `PresetCleaner` - Handles preset file processing
- `AudioAnalyzer` - Extracts audio features
- `PresetSorter` - Organizes results by quality

### Utility Functions

- `setup_logging()` - Configures application logging
- `get_logger()` - Gets contextual logger instances

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- Built with librosa for audio analysis
- REAPER for audio rendering capabilities
- Inspired by audio production workflows
