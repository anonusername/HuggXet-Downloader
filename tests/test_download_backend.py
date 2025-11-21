"""
Unit tests for DownloadBackend class.

Tests focus on backend logic, state management, and error handling.
Real download functionality is tested in test_integration_downloads.py.
"""
import pytest
from PySide6.QtCore import QCoreApplication
from main import DownloadBackend


@pytest.fixture
def app():
    """Create QCoreApplication instance for testing"""
    return QCoreApplication.instance() or QCoreApplication([])


@pytest.fixture
def backend(app, tmp_path, monkeypatch):
    """Create a DownloadBackend instance with temporary save file"""
    # Override save file location to use temporary directory
    def mock_get_save_file_path(self):
        return tmp_path / "test_downloads.json"
    
    monkeypatch.setattr('main.DownloadBackend._get_save_file_path', mock_get_save_file_path)
    return DownloadBackend()


def test_backend_initialization(app, tmp_path, monkeypatch):
    """Test backend is initialized with empty download list"""
    # Use temp directory to avoid loading existing saved downloads
    def mock_get_save_file_path(self):
        return tmp_path / "test_init_downloads.json"
    
    monkeypatch.setattr('main.DownloadBackend._get_save_file_path', mock_get_save_file_path)
    backend = DownloadBackend()
    
    assert backend.downloadsModel is not None
    assert backend.downloadsModel.rowCount() == 0  # Start with empty list
    assert backend.statusMessage in ["Ready", "Loaded 0 downloads"]


def test_backend_add_download(backend):
    """Test adding a download"""
    signal_emitted = False
    added_name = ""
    added_url = ""
    
    def on_download_added(name, url):
        nonlocal signal_emitted, added_name, added_url
        signal_emitted = True
        added_name = name
        added_url = url
    
    backend.downloadAdded.connect(on_download_added)
    
    backend.addDownload("new_file.bin", "https://huggingface.co/test/model")
    
    assert signal_emitted
    assert added_name == "new_file.bin"
    assert added_url == "https://huggingface.co/test/model"
    assert backend.downloadsModel.rowCount() == 1
    assert "Added: new_file.bin" in backend.statusMessage  # Status includes platform


def test_backend_remove_download(backend):
    """Test removing a download"""
    backend.addDownload("file.bin", "https://huggingface.co/test/model")
    
    signal_emitted = False
    removed_index = -1
    
    def on_download_removed(index):
        nonlocal signal_emitted, removed_index
        signal_emitted = True
        removed_index = index
    
    backend.downloadRemoved.connect(on_download_removed)
    
    backend.removeDownload(0)
    
    assert signal_emitted
    assert removed_index == 0
    assert backend.downloadsModel.rowCount() == 0
    assert "Removed:" in backend.statusMessage


def test_backend_start_download(backend):
    """Test starting a pending download"""
    backend.addDownload("file.bin", "https://huggingface.co/test/model")
    item = backend.downloadsModel.getItem(0)
    
    assert item.status == "Pending"
    
    backend.startDownload(0)
    
    # Status changes to Preparing when download worker starts
    assert item.status in ["Preparing", "Downloading"]
    assert "Starting:" in backend.statusMessage


def test_backend_pause_download(backend):
    """Test pausing a downloading item"""
    backend.addDownload("file.bin", "https://huggingface.co/test/file")
    item = backend.downloadsModel.getItem(0)
    item.status = "Downloading"
    
    backend.pauseDownload(0)
    
    assert item.status == "Paused"
    assert "Paused:" in backend.statusMessage


def test_backend_start_all(backend):
    """Test starting all pending/paused downloads"""
    backend.addDownload("file1.bin", "https://huggingface.co/test/1")
    backend.addDownload("file2.bin", "https://huggingface.co/test/2")
    backend.addDownload("file3.bin", "https://huggingface.co/test/3")
    
    # Set different statuses
    backend.downloadsModel.getItem(0).status = "Pending"
    backend.downloadsModel.getItem(1).status = "Paused"
    backend.downloadsModel.getItem(2).status = "Completed"
    
    backend.startAll()
    
    # Status changes to Preparing when download workers start
    assert backend.downloadsModel.getItem(0).status in ["Preparing", "Downloading"]
    assert backend.downloadsModel.getItem(1).status in ["Preparing", "Downloading"]
    assert backend.downloadsModel.getItem(2).status == "Completed"  # Should not change
    assert "Starting 2 downloads" in backend.statusMessage


def test_backend_pause_all(backend):
    """Test pausing all active downloads"""
    backend.addDownload("file1.bin", "https://huggingface.co/test/1")
    backend.addDownload("file2.bin", "https://huggingface.co/test/2")
    backend.addDownload("file3.bin", "https://huggingface.co/test/3")
    
    # Set different statuses
    backend.downloadsModel.getItem(0).status = "Downloading"
    backend.downloadsModel.getItem(1).status = "Downloading"
    backend.downloadsModel.getItem(2).status = "Pending"
    
    backend.pauseAll()
    
    assert backend.downloadsModel.getItem(0).status == "Paused"
    assert backend.downloadsModel.getItem(1).status == "Paused"
    assert backend.downloadsModel.getItem(2).status == "Pending"  # Should not change
    assert "Paused 2 downloads" in backend.statusMessage


def test_backend_clear_completed(backend):
    """Test clearing completed downloads"""
    backend.addDownload("file1.bin", "https://huggingface.co/test/1")
    backend.addDownload("file2.bin", "https://huggingface.co/test/2")
    backend.addDownload("file3.bin", "https://huggingface.co/test/3")
    backend.addDownload("file4.bin", "https://huggingface.co/test/4")
    
    # Set different statuses
    backend.downloadsModel.getItem(0).status = "Completed"
    backend.downloadsModel.getItem(1).status = "Downloading"
    backend.downloadsModel.getItem(2).status = "Completed"
    backend.downloadsModel.getItem(3).status = "Pending"
    
    backend.clearCompleted()
    
    assert backend.downloadsModel.rowCount() == 2
    assert backend.downloadsModel.getItem(0).name == "file2.bin"
    assert backend.downloadsModel.getItem(1).name == "file4.bin"
    assert "Cleared 2 completed downloads" in backend.statusMessage


def test_backend_status_message_property(backend):
    """Test status message property and signal"""
    signal_emitted = False
    new_message = ""
    
    def on_status_changed(msg):
        nonlocal signal_emitted, new_message
        signal_emitted = True
        new_message = msg
    
    backend.statusMessageChanged.connect(on_status_changed)
    
    backend.statusMessage = "Test message"
    
    assert signal_emitted
    assert new_message == "Test message"
    assert backend.statusMessage == "Test message"


def test_backend_start_download_invalid_status(backend):
    """Test that starting a completed download doesn't change status"""
    backend.addDownload("file.bin", "https://huggingface.co/test/file")
    item = backend.downloadsModel.getItem(0)
    item.status = "Completed"
    
    backend.startDownload(0)
    
    assert item.status == "Completed"  # Should remain Completed


def test_backend_pause_download_invalid_status(backend):
    """Test that pausing a pending download doesn't change status"""
    backend.addDownload("file.bin", "https://huggingface.co/test/file")
    item = backend.downloadsModel.getItem(0)
    item.status = "Pending"
    
    backend.pauseDownload(0)
    
    assert item.status == "Pending"  # Should remain Pending
