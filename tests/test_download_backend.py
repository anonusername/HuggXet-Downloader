"""Unit tests for DownloadBackend class"""
import pytest
from PySide6.QtCore import QCoreApplication
from main import DownloadBackend


@pytest.fixture
def app():
    """Create QCoreApplication instance for testing"""
    return QCoreApplication.instance() or QCoreApplication([])


@pytest.fixture
def backend(app):
    """Create a DownloadBackend instance without sample data"""
    backend = DownloadBackend()
    # Clear sample data for clean testing
    while backend.downloadsModel.rowCount() > 0:
        backend.downloadsModel.removeItem(0)
    return backend


def test_backend_initialization(app):
    """Test backend is initialized with sample data"""
    backend = DownloadBackend()
    
    assert backend.downloadsModel is not None
    assert backend.downloadsModel.rowCount() == 6  # Sample data count
    assert backend.statusMessage == "Ready"


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
    
    backend.addDownload("new_file.bin", "https://example.com/file")
    
    assert signal_emitted
    assert added_name == "new_file.bin"
    assert added_url == "https://example.com/file"
    assert backend.downloadsModel.rowCount() == 1
    assert backend.statusMessage == "Added: new_file.bin"


def test_backend_remove_download(backend):
    """Test removing a download"""
    backend.addDownload("file.bin", "https://example.com/file")
    
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
    backend.addDownload("file.bin", "https://example.com/file")
    item = backend.downloadsModel.getItem(0)
    
    assert item.status == "Pending"
    
    backend.startDownload(0)
    
    assert item.status == "Downloading"
    assert "Started:" in backend.statusMessage


def test_backend_pause_download(backend):
    """Test pausing a downloading item"""
    backend.addDownload("file.bin", "https://example.com/file")
    item = backend.downloadsModel.getItem(0)
    item.status = "Downloading"
    
    backend.pauseDownload(0)
    
    assert item.status == "Paused"
    assert "Paused:" in backend.statusMessage


def test_backend_start_all(backend):
    """Test starting all pending/paused downloads"""
    backend.addDownload("file1.bin", "https://example.com/1")
    backend.addDownload("file2.bin", "https://example.com/2")
    backend.addDownload("file3.bin", "https://example.com/3")
    
    # Set different statuses
    backend.downloadsModel.getItem(0).status = "Pending"
    backend.downloadsModel.getItem(1).status = "Paused"
    backend.downloadsModel.getItem(2).status = "Completed"
    
    backend.startAll()
    
    assert backend.downloadsModel.getItem(0).status == "Downloading"
    assert backend.downloadsModel.getItem(1).status == "Downloading"
    assert backend.downloadsModel.getItem(2).status == "Completed"  # Should not change
    assert "Started 2 downloads" in backend.statusMessage


def test_backend_pause_all(backend):
    """Test pausing all active downloads"""
    backend.addDownload("file1.bin", "https://example.com/1")
    backend.addDownload("file2.bin", "https://example.com/2")
    backend.addDownload("file3.bin", "https://example.com/3")
    
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
    backend.addDownload("file1.bin", "https://example.com/1")
    backend.addDownload("file2.bin", "https://example.com/2")
    backend.addDownload("file3.bin", "https://example.com/3")
    backend.addDownload("file4.bin", "https://example.com/4")
    
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
    backend.addDownload("file.bin", "https://example.com/file")
    item = backend.downloadsModel.getItem(0)
    item.status = "Completed"
    
    backend.startDownload(0)
    
    assert item.status == "Completed"  # Should remain Completed


def test_backend_pause_download_invalid_status(backend):
    """Test that pausing a pending download doesn't change status"""
    backend.addDownload("file.bin", "https://example.com/file")
    item = backend.downloadsModel.getItem(0)
    item.status = "Pending"
    
    backend.pauseDownload(0)
    
    assert item.status == "Pending"  # Should remain Pending
