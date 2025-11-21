# HuggXet-Downloader

A modern, cross-platform download manager for HuggingFace repositories. Built with PySide6 and QML, featuring a Material Design UI optimized for both desktop and touch interfaces.

## Features

- **HuggingFace Hub Support** - Download models, datasets, and files from HuggingFace
- **hf_xet Optimization** - Automatic chunk-based deduplication for faster downloads
- **Async Downloads** - Non-blocking downloads with real-time progress tracking
- **Material Design UI** - Modern dark-themed interface with smooth animations
- **Persistent Queue** - Download queue automatically saves and restores
- **Cross-Platform** - Windows, Linux, macOS support

## Supported URL Formats

### HuggingFace
```
https://huggingface.co/openai/gpt-oss-20b
https://huggingface.co/openai/gpt-oss-20b/blob/main/config.json
https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B/tree/main/examples
huggingface.co/username/model-name
```

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/anonusername/HuggXet-Downloader.git
cd HuggXet-Downloader
```

2. Create virtual environment:
```bash
python -m venv .venv
```

3. Activate virtual environment:
```bash
# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

```bash
python main.py
```

## Authentication

### HuggingFace (for private repositories)

**Option 1: Using huggingface-cli**
```bash
huggingface-cli login
```

**Option 2: Using environment variable**
```bash
export HF_TOKEN="your_token_here"
```

**Option 3: Using Python**
```python
from huggingface_hub import login
login(token="your_token_here")
```

Get your token from: https://huggingface.co/settings/tokens

## Usage

1. **Add Download**
   - Click the "➕ Add" button in the top right toolbar
   - **Download Name**: Enter a friendly name to identify this download (e.g., "Wan2.2-TI2V Model")
     - Must be at least 3 characters
     - Used to organize your download queue
   - **HuggingFace URL**: Paste the complete HuggingFace URL
     - Supports repository URLs: `https://huggingface.co/openai/gpt-oss-20b`
     - Supports directory URLs: `https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B/tree/main/examples`
     - Supports file URLs: `https://huggingface.co/bert-base/blob/main/config.json`
     - URL validation provides visual feedback (red border for invalid URLs)
   - Review the example URLs shown in the dialog for guidance
   - Click "OK" to add to queue

2. **Start Download**
   - Click the play button (▶) on any download item
   - Progress will update in real-time

3. **Pause/Resume**
   - Click the pause button (⏸) to pause
   - Click play (▶) again to resume

4. **Remove Download**
   - Click the trash icon (🗑) to remove from queue

5. **Batch Operations**
   - Use toolbar buttons to start all, pause all, or clear completed downloads

## Downloads Location

Downloaded files are saved to:
- **Windows**: `C:\Users\YourName\Downloads\{download-name}\`
- **Linux**: `~/Downloads/{download-name}/`
- **macOS**: `~/Downloads/{download-name}/`

## Building Executables

### Prerequisites

**Before building, ensure you have:**
1. Created virtual environment: `python -m venv .venv`
2. Installed dependencies: `pip install -r requirements.txt`
3. Installed PyInstaller: `pip install pyinstaller>=6.0.0`

### Using VS Code Tasks (Recommended)

Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS) and type "Run Task":

**Setup Tasks:**
- `Setup: Create Virtual Environment` - Create .venv
- `Setup: Install Dependencies` - Install requirements.txt
- `Setup: Install PyInstaller` - Install build tool

**Build Tasks:**
- `Build: Current Platform` - Build for your OS (default build task: `Ctrl+Shift+B`)
- `Build: Windows Executable` - Build .exe (Windows only)
- `Build: Linux Executable` - Build Linux binary (Linux only)
- `Build: macOS Executable` - Build macOS app (macOS only)

**Other Tasks:**
- `Run: Application` - Launch the app
- `Test: Unit Tests` - Run fast tests (default test task)
- `Test: Integration Tests` - Run network tests
- `Test: Coverage` - Run tests with coverage

### Manual Building

**Windows:**
```bash
.venv\Scripts\python.exe -m PyInstaller --distpath .venv/releases/windows --workpath .venv/build --clean HuggXet-Downloader.spec
```
Output: `.venv/releases/windows/HuggXet-Downloader.exe`

**Linux:**
```bash
.venv/bin/python -m PyInstaller --distpath .venv/releases/linux --workpath .venv/build --clean HuggXet-Downloader.spec
```
Output: `.venv/releases/linux/HuggXet-Downloader`

**macOS:**
```bash
.venv/bin/python -m PyInstaller --distpath .venv/releases/macos --workpath .venv/build --clean HuggXet-Downloader.spec
```
Output: `.venv/releases/macos/HuggXet-Downloader`

## Development

### Running Tests

**Unit Tests (fast, no network)**
```bash
python -m pytest -m "not integration"
```

**Integration Tests (requires network, downloads real files)**
```bash
python -m pytest -m integration
```

**All Tests**
```bash
python -m pytest
```

**Test Coverage (Unit Tests)**
```bash
python -m pytest --cov=. --cov-report=html --cov-report=term -m "not integration"
```

**Test Coverage (All Tests)**
```bash
python -m pytest --cov=. --cov-report=html --cov-report=term --cov-report=xml
```

After running with `--cov-report=html`, open `htmlcov/index.html` in your browser to see detailed coverage report.

See [SETUP.md](SETUP.md) for detailed development instructions.

## Architecture

- **Backend (Python)**
  - `main.py` - Application logic, models, and Qt integration
  - `download_worker.py` - Async download thread worker
  - `downloaders/` - Platform-specific download implementations
  
- **Frontend (QML)**
  - `qml/main.qml` - Main window and UI logic
  - `qml/DownloadListDelegate.qml` - List view item template
  - `qml/DownloadGridDelegate.qml` - Grid view item template

## Requirements

- Python 3.8+
- PySide6 6.6+
- huggingface_hub 1.1+ (includes hf_xet for optimized downloads)

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please read SETUP.md for development guidelines.
