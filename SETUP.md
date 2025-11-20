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

This will install PySide6 (Qt 6 for Python) and all necessary Qt modules.

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
2. Enter the file name
3. Enter the URL
4. Click **OK**

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
├── main.py                         # Python backend and entry point
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

## Development

### Adding Sample Data

Edit the `_init_sample_data()` method in `main.py` to add or modify sample downloads.

### Creating New Delegates

1. Create a new `.qml` file in the `qml/` directory
2. Import required modules (`QtQuick`, `QtQuick.Controls`, etc.)
3. Define required properties
4. Create the visual layout

## Dependencies

- **PySide6** (>=6.6.0) - Qt 6 for Python
  - Includes QtCore, QtGui, QtQml, QtQuick modules
  - Provides QML engine and Material Design components

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
