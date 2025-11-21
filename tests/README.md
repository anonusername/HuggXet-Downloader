# Test Suite for HuggXet-Downloader

This directory contains comprehensive unit tests for the HuggXet-Downloader application.

## Test Coverage

### test_download_item.py (8 tests)
Tests for the `DownloadItem` class:
- Initialization with parameters and default values
- Property setters (name, url, progress, status, size)
- Qt signal emissions on property changes
- Signal behavior optimization (no emission when value unchanged)

### test_download_list_model.py (11 tests)
Tests for the `DownloadListModel` class:
- Model initialization and row count
- Adding single and multiple items
- Data retrieval via Qt model indices
- Role names mapping
- Removing items (valid and invalid indices)
- Getting items by index
- Model update notifications on item changes
- Invalid index handling

### test_download_backend.py (11 tests)
Tests for the `DownloadBackend` class:
- Backend initialization with sample data
- Adding downloads with signal emissions
- Removing downloads
- Starting and pausing individual downloads
- Batch operations (start all, pause all, clear completed)
- Status message updates
- Signal behavior for various operations
- Edge cases (invalid statuses, etc.)

## Running Tests

### Run all tests:
```bash
pytest
```

### Run with verbose output:
```bash
pytest -v
```

### Run specific test file:
```bash
pytest tests/test_download_item.py -v
```

### Run with coverage:
```bash
pytest --cov=main --cov-report=html
```

### Run only specific test:
```bash
pytest tests/test_download_backend.py::test_backend_add_download -v
```

## Test Results

All tests pass successfully:
```
30 passed in 0.14s
```

## Dependencies

- `pytest>=7.4.0` - Testing framework
- `pytest-qt>=4.2.0` - Qt testing plugin
- `PySide6>=6.6.0` - Required for Qt components

## Writing New Tests

When adding new features to the application:

1. Create a test file in this directory following the `test_*.py` naming convention
2. Import necessary classes from `main.py`
3. Use fixtures for Qt application setup:

```python
import pytest
from PySide6.QtCore import QCoreApplication
from main import YourClass

@pytest.fixture
def app():
    return QCoreApplication.instance() or QCoreApplication([])

def test_your_feature(app):
    # Test implementation
    pass
```

4. Test both functionality and Qt signals
5. Use descriptive test names that explain the behavior being tested

## Continuous Integration

Tests should be run before:
- Committing changes
- Creating pull requests
- Deploying the application

Ensure all tests pass before merging code.
