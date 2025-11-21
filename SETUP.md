# HuggXet-Downloader Setup and Usage Guide

## Overview

A modern cross-platform download manager built with **PySide6** and **QML**, featuring a touch-enabled interface with Material Design styling. This application demonstrates best practices for building declarative UIs with Python backend logic.

## Features

- 🎨 **Modern Material Design** - Dark theme with beautiful animations
- 📱 **Touch-Enabled** - Optimized for both mouse and touch interactions
- 🔄 **Dual View Modes** - Switch between List and Grid views
- ⚡ **Smooth Animations** - PropertyAnimation throughout the UI
- 🏗️ **Clean Architecture** - Separated Python backend from QML frontend
- 📊 **Live Updates** - Reactive UI with Qt signal/slot mechanism

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/anonusername/HuggXet-Downloader.git
cd HuggXet-Downloader
```

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
```

### 3. Activate Virtual Environment

**Linux/macOS:**
```bash
source .venv/bin/activate
```

**Windows:**
```cmd
.venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- **PySide6** (>=6.6.0) - Qt 6 for Python and all necessary Qt modules
- **pytest** (>=7.4.0) - Testing framework
- **pytest-qt** (>=4.2.0) - Pytest plugin for Qt applications

## Running the Application

Once the virtual environment is activated and dependencies are installed:

```bash
python main.py
```

Or make it executable and run directly:

```bash
chmod +x main.py
./main.py
```

## Testing

### Running Unit Tests

The project includes comprehensive unit tests using pytest. To run all tests:

```bash
pytest
```

For verbose output with detailed test results:

```bash
pytest -v
```

To run specific test files:

```bash
pytest tests/test_download_item.py
pytest tests/test_download_list_model.py
pytest tests/test_download_backend.py
```

To see test coverage:

```bash
pytest --cov=main --cov-report=html
```

### Test Structure

The test suite includes:

- **test_download_item.py** - Tests for DownloadItem class
  - Property initialization and default values
  - Property setters and Qt signal emissions
  - Signal behavior when values don't change

- **test_download_list_model.py** - Tests for DownloadListModel
  - Model initialization and data management
  - Adding/removing items
  - Data retrieval and role names
  - Qt model signals and notifications

- **test_download_backend.py** - Tests for DownloadBackend
  - Download lifecycle (add, start, pause, remove)
  - Batch operations (start all, pause all, clear completed)
  - Status message updates
  - Signal emissions

### Writing New Tests

When adding new features, create corresponding tests:

1. Create test file in `tests/` directory following `test_*.py` naming
2. Import required classes from `main.py`
3. Use pytest fixtures for Qt application setup
4. Test both functionality and Qt signal emissions
5. Use descriptive test names that explain what is being tested

Example test structure:

```python
import pytest
from PySide6.QtCore import QCoreApplication
from main import YourClass

@pytest.fixture
def app():
    return QCoreApplication.instance() or QCoreApplication([])

def test_your_feature(app):
    # Arrange
    obj = YourClass()
    
    # Act
    result = obj.method()
    
    # Assert
    assert result == expected_value
```

### Continuous Integration

Tests should be run before committing changes:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run only fast tests (exclude slow markers)
pytest -m "not slow"
```

### Using VS Code Tasks

VS Code tasks are configured in `.vscode/tasks.json` for common operations:

**Access tasks:** `Ctrl+Shift+P` → "Tasks: Run Task"

**Quick shortcuts:**
- `Ctrl+Shift+B` - Default build task (Build: Current Platform)
- `Ctrl+Shift+T` - Default test task (Test: Unit Tests)

**Available tasks:**
- **Setup tasks** - Create venv, install dependencies, install PyInstaller
- **Run task** - Launch the application
- **Test tasks** - Unit tests, integration tests, coverage
- **Build tasks** - Platform-specific executable builds

## Usage

### Interface Overview

- **Toolbar** (Top)
  - View toggle buttons (List/Grid)
  - Start All - Resume all paused/pending downloads
  - Pause All - Pause all active downloads
  - Clear - Remove completed downloads
  - Add - Add a new download

- **Main Area** (Center)
  - Displays downloads in selected view mode
  - Click items to see hover effects
  - Use ▶/⏸ buttons to control individual downloads
  - Use 🗑 button to remove downloads

- **Status Bar** (Bottom)
  - Shows total download count
  - Displays status messages for recent actions

### Adding a Download

1. Click the **➕ Add** button in the toolbar
2. Fill in the dialog fields:

   **Download Name Field:**
   - Enter a descriptive name for your download (e.g., "Wan2.2-TI2V Model")
   - Minimum 3 characters required
   - Field border turns red if name is too short
   - This name appears in your download queue for easy identification

   **HuggingFace URL Field:**
   - Paste the complete URL from HuggingFace Hub
   - Accepted formats:
     - Repository: `https://huggingface.co/openai/gpt-oss-20b`
     - Directory: `https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B/tree/main/examples`
     - File: `https://huggingface.co/bert-base/blob/main/config.json`
   - Field border turns red if URL is invalid (must contain "huggingface.co" or "hf.co")
   - Example URLs are shown at the bottom of the dialog

3. Click **OK** to add to queue, or **Cancel** to discard

### Switching Views

Click the **List** or **Grid** buttons in the toolbar to switch between view modes. The transition is animated smoothly.

### Controlling Downloads

- **▶ Start** - Start or resume a download
- **⏸ Pause** - Pause an active download
- **🗑 Remove** - Delete the download from the list

## Project Structure

```
HuggXet-Downloader/
├── .venv/                          # Python virtual environment (ignored by git)
├── qml/                            # QML frontend components
│   ├── main.qml                    # Main application window
│   ├── DownloadListDelegate.qml    # List view item template
│   └── DownloadGridDelegate.qml    # Grid view item template
├── tests/                          # Unit tests
│   ├── __init__.py                 # Test package marker
│   ├── test_download_item.py       # DownloadItem tests
│   ├── test_download_list_model.py # DownloadListModel tests
│   └── test_download_backend.py    # DownloadBackend tests
├── main.py                         # Python backend and entry point
├── pytest.ini                      # Pytest configuration
├── requirements.txt                # Python dependencies
├── SETUP.md                        # This file
├── README.md                       # Project description
├── LICENSE                         # License information
└── .gitignore                      # Git ignore patterns
```

## Architecture

### Python Backend (`main.py`)

- **DownloadItem** - QObject representing a single download with Qt Properties
- **DownloadListModel** - QAbstractListModel for efficient Qt model integration
- **DownloadBackend** - Main backend class with @Slot methods for QML interaction
- Uses **QQmlApplicationEngine** to load and run the QML interface

### QML Frontend (`qml/`)

- **main.qml** - ApplicationWindow with Material Design styling
- **DownloadListDelegate.qml** - Template for list view items
- **DownloadGridDelegate.qml** - Template for grid view items
- Uses **QtQuick.Controls** for UI components
- Uses **QtQuick.Layouts** for responsive layouts

### Communication

- Python exposes `downloadBackend` via QQmlContext
- QML calls Python methods using signal/slot mechanism
- Data flows from Python model to QML views via Qt's property system

## Customization

### Changing the Theme

Edit `qml/main.qml`:

```qml
Material.theme: Material.Dark  // or Material.Light
Material.accent: Material.Purple  // Change accent color
Material.primary: Material.DeepPurple  // Change primary color
```

Available colors: Red, Pink, Purple, DeepPurple, Indigo, Blue, LightBlue, Cyan, Teal, Green, LightGreen, Lime, Yellow, Amber, Orange, DeepOrange, Brown, Grey, BlueGrey

### Adding New Features

1. Add Python methods in `DownloadBackend` class with `@Slot()` decorator
2. Call these methods from QML using `downloadBackend.methodName()`
3. Update UI bindings to reflect backend changes

## Troubleshooting

### "Module not found" Error

Make sure the virtual environment is activated:
```bash
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate  # Windows
```

### QML Errors

Check that all QML files are in the `qml/` directory and properly formatted.

### Display Issues on Linux

If running headless or via SSH, you may need X11 forwarding or Xvfb:
```bash
xvfb-run python main.py
```

## Building Executables

### Prerequisites

Before building executables, ensure:

1. **Virtual environment exists:**
   ```bash
   python -m venv .venv
   ```

2. **Dependencies installed:**
   ```bash
   # Activate venv first
   pip install -r requirements.txt
   ```

3. **PyInstaller installed:**
   ```bash
   pip install pyinstaller>=6.0.0
   ```

### Using VS Code Build Tasks

**Keyboard shortcuts:**
- `Ctrl+Shift+B` (Windows/Linux) or `Cmd+Shift+B` (macOS) - Build for current platform
- Or: `Ctrl+Shift+P` → "Tasks: Run Build Task"

**Platform-specific builds:**
1. Open Command Palette: `Ctrl+Shift+P` (or `Cmd+Shift+P`)
2. Type "Tasks: Run Task"
3. Select:
   - `Build: Windows Executable` (Windows only)
   - `Build: Linux Executable` (Linux only)
   - `Build: macOS Executable` (macOS only)
   - `Build: Current Platform` (auto-detects OS)

**Output locations:**
- Windows: `.venv/releases/windows/HuggXet-Downloader.exe`
- Linux: `.venv/releases/linux/HuggXet-Downloader`
- macOS: `.venv/releases/macos/HuggXet-Downloader`

### Manual Building

**Windows:**
```cmd
.venv\Scripts\python.exe -m PyInstaller --distpath .venv/releases/windows --workpath .venv/build --clean HuggXet-Downloader.spec
```

**Linux:**
```bash
.venv/bin/python -m PyInstaller --distpath .venv/releases/linux --workpath .venv/build --clean HuggXet-Downloader.spec
```

**macOS:**
```bash
.venv/bin/python -m PyInstaller --distpath .venv/releases/macos --workpath .venv/build --clean HuggXet-Downloader.spec
```

### Build Artifacts

All build outputs are placed inside `.venv/` to keep the repository clean:
- `.venv/build/` - PyInstaller intermediate files
- `.venv/releases/{platform}/` - Final executables

These directories are ignored by git (see `.gitignore`).

### Troubleshooting Builds

**Error: "Virtual environment not found"**
- Run `Setup: Create Virtual Environment` task first
- Or manually: `python -m venv .venv`

**Error: "PyInstaller not found"**
- Run `Setup: Install PyInstaller` task
- Or manually: `pip install pyinstaller>=6.0.0`

**Error: "No module named 'PySide6'"**
- Run `Setup: Install Dependencies` task
- Or manually: `pip install -r requirements.txt`

## Development

### Adding Sample Data

Edit the `_init_sample_data()` method in `main.py` to add or modify sample downloads.

### Creating New Delegates

1. Create a new `.qml` file in the `qml/` directory
2. Import required modules (`QtQuick`, `QtQuick.Controls`, etc.)
3. Define required properties
4. Create the visual layout

## Dependencies

### Runtime Dependencies
- **PySide6** (>=6.6.0) - Qt 6 for Python
  - Includes QtCore, QtGui, QtQml, QtQuick modules
  - Provides QML engine and Material Design components

### Development Dependencies
- **pytest** (>=7.4.0) - Testing framework for Python
  - Provides fixtures, assertions, and test discovery
- **pytest-qt** (>=4.2.0) - Pytest plugin for Qt/PySide6
  - Enables testing of Qt signals, slots, and QML components
  - Provides Qt application fixtures for tests

## License

See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Resources

- [PySide6 Documentation](https://doc.qt.io/qtforpython/)
- [QML Documentation](https://doc.qt.io/qt-6/qmlapplications.html)
- [Qt Quick Controls](https://doc.qt.io/qt-6/qtquickcontrols-index.html)
- [Material Design](https://material.io/design)
