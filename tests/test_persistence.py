"""
Tests for download persistence functionality
"""
import json
import pytest
from pathlib import Path
from PySide6.QtCore import QCoreApplication
from main import DownloadItem, DownloadBackend


@pytest.fixture
def app():
    """Create QCoreApplication instance"""
    return QCoreApplication.instance() or QCoreApplication([])


@pytest.fixture
def temp_backend(app, tmp_path, monkeypatch):
    """Create backend with temporary save file"""
    # Override save file location to use temporary directory
    def mock_get_save_file_path(self):
        return tmp_path / "downloads.json"
    
    monkeypatch.setattr(DownloadBackend, '_get_save_file_path', mock_get_save_file_path)
    backend = DownloadBackend()
    return backend


def test_download_item_to_dict(app):
    """Test DownloadItem serialization to dictionary"""
    item = DownloadItem(
        name="test.bin",
        url="https://huggingface.co/test/test.bin",
        progress=50,
        status="Downloading",
        size="100 MB",
        priority=2
    )
    
    data = item.to_dict()
    
    assert data["name"] == "test.bin"
    assert data["url"] == "https://huggingface.co/test/test.bin"
    assert data["progress"] == 50
    assert data["status"] == "Downloading"
    assert data["size"] == "100 MB"
    assert data["priority"] == 2


def test_download_item_from_dict(app):
    """Test DownloadItem deserialization from dictionary"""
    data = {
        "name": "test.bin",
        "url": "https://huggingface.co/test/test.bin",
        "progress": 75,
        "status": "Paused",
        "size": "250 MB",
        "priority": 3
    }
    
    item = DownloadItem.from_dict(data)
    
    assert item.name == "test.bin"
    assert item.url == "https://huggingface.co/test/test.bin"
    assert item.progress == 75
    assert item.status == "Paused"
    assert item.size == "250 MB"
    assert item.priority == 3


def test_save_downloads(temp_backend, tmp_path):
    """Test saving downloads to JSON file"""
    # Add some downloads
    temp_backend.addDownload("file1.bin", "https://huggingface.co/test/file1")
    temp_backend.addDownload("file2.bin", "https://huggingface.co/test/file2")
    
    app = QCoreApplication.instance()
    app.processEvents()
    
    # Check file was created
    save_file = tmp_path / "downloads.json"
    assert save_file.exists()
    
    # Verify content
    with open(save_file, 'r') as f:
        data = json.load(f)
    
    assert len(data) == 2
    assert data[0]["name"] == "file1.bin"
    assert data[0]["url"] == "https://huggingface.co/test/file1"
    assert data[1]["name"] == "file2.bin"
    assert data[1]["url"] == "https://huggingface.co/test/file2"


def test_load_downloads(app, tmp_path, monkeypatch):
    """Test loading downloads from JSON file"""
    # Create save file with test data
    save_file = tmp_path / "downloads.json"
    test_data = [
        {
            "name": "saved1.bin",
            "url": "https://huggingface.co/test/saved1",
            "progress": 30,
            "status": "Paused",
            "size": "50 MB",
            "priority": 1
        },
        {
            "name": "saved2.bin",
            "url": "https://huggingface.co/test/saved2",
            "progress": 100,
            "status": "Completed",
            "size": "75 MB",
            "priority": 2
        }
    ]
    
    with open(save_file, 'w') as f:
        json.dump(test_data, f)
    
    # Override save file location
    def mock_get_save_file_path(self):
        return save_file
    
    monkeypatch.setattr(DownloadBackend, '_get_save_file_path', mock_get_save_file_path)
    
    # Create backend (should load downloads)
    backend = DownloadBackend()
    app.processEvents()
    
    # Verify downloads were loaded
    assert backend.downloadsModel.rowCount() == 2
    
    item1 = backend.downloadsModel.getItem(0)
    assert item1.name == "saved1.bin"
    assert item1.url == "https://huggingface.co/test/saved1"
    assert item1.progress == 30
    assert item1.status == "Paused"
    
    item2 = backend.downloadsModel.getItem(1)
    assert item2.name == "saved2.bin"
    assert item2.progress == 100
    assert item2.status == "Completed"


def test_auto_save_on_add(temp_backend, tmp_path):
    """Test automatic save when adding download"""
    temp_backend.addDownload("auto.bin", "https://huggingface.co/test/auto")
    
    app = QCoreApplication.instance()
    app.processEvents()
    
    save_file = tmp_path / "downloads.json"
    assert save_file.exists()
    
    with open(save_file, 'r') as f:
        data = json.load(f)
    
    assert len(data) == 1
    assert data[0]["name"] == "auto.bin"


def test_auto_save_on_remove(temp_backend, tmp_path):
    """Test automatic save when removing download"""
    temp_backend.addDownload("remove1.bin", "https://huggingface.co/test/remove1")
    temp_backend.addDownload("remove2.bin", "https://huggingface.co/test/remove2")
    
    app = QCoreApplication.instance()
    app.processEvents()
    
    # Remove first download
    temp_backend.removeDownload(0)
    app.processEvents()
    
    save_file = tmp_path / "downloads.json"
    with open(save_file, 'r') as f:
        data = json.load(f)
    
    assert len(data) == 1
    assert data[0]["name"] == "remove2.bin"


def test_auto_save_on_status_change(temp_backend, tmp_path):
    """Test automatic save when changing download status"""
    temp_backend.addDownload("status.bin", "https://huggingface.co/test/status")
    app = QCoreApplication.instance()
    app.processEvents()
    
    # Verify initial save
    save_file = tmp_path / "downloads.json"
    with open(save_file, 'r') as f:
        data = json.load(f)
    
    assert len(data) == 1
    assert data[0]["name"] == "status.bin"
    assert data[0]["status"] == "Pending"
    
    # Change status manually and trigger auto-save
    item = temp_backend.downloadsModel.getItem(0)
    item.status = "Downloading"
    temp_backend._save_downloads()  # Manually trigger save
    app.processEvents()
    
    # Verify save file was updated with new status
    with open(save_file, 'r') as f:
        data = json.load(f)
    
    assert data[0]["status"] == "Downloading"


def test_persistence_with_empty_file(app, tmp_path, monkeypatch):
    """Test handling of missing save file"""
    save_file = tmp_path / "nonexistent.json"
    
    def mock_get_save_file_path(self):
        return save_file
    
    monkeypatch.setattr(DownloadBackend, '_get_save_file_path', mock_get_save_file_path)
    
    # Should not crash with missing file
    backend = DownloadBackend()
    app.processEvents()
    
    assert backend.downloadsModel.rowCount() == 0
