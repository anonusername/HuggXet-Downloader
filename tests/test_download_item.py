"""Unit tests for DownloadItem class"""
import pytest
from PySide6.QtCore import QCoreApplication
from main import DownloadItem


@pytest.fixture
def app():
    """Create QCoreApplication instance for testing"""
    return QCoreApplication.instance() or QCoreApplication([])


def test_download_item_initialization(app):
    """Test DownloadItem is initialized with correct values"""
    item = DownloadItem(
        name="test_file.bin",
        url="https://example.com/test",
        progress=50,
        status="Downloading",
        size="100 MB"
    )
    
    assert item.name == "test_file.bin"
    assert item.url == "https://example.com/test"
    assert item.progress == 50
    assert item.status == "Downloading"
    assert item.size == "100 MB"


def test_download_item_default_values(app):
    """Test DownloadItem default values"""
    item = DownloadItem()
    
    assert item.name == ""
    assert item.url == ""
    assert item.progress == 0
    assert item.status == "Pending"
    assert item.size == "0 MB"


def test_download_item_name_setter(app):
    """Test DownloadItem name property setter"""
    item = DownloadItem()
    signal_emitted = False
    
    def on_name_changed():
        nonlocal signal_emitted
        signal_emitted = True
    
    item.nameChanged.connect(on_name_changed)
    item.name = "new_file.bin"
    
    assert item.name == "new_file.bin"
    assert signal_emitted


def test_download_item_url_setter(app):
    """Test DownloadItem url property setter"""
    item = DownloadItem()
    signal_emitted = False
    
    def on_url_changed():
        nonlocal signal_emitted
        signal_emitted = True
    
    item.urlChanged.connect(on_url_changed)
    item.url = "https://newurl.com"
    
    assert item.url == "https://newurl.com"
    assert signal_emitted


def test_download_item_progress_setter(app):
    """Test DownloadItem progress property setter"""
    item = DownloadItem()
    signal_emitted = False
    
    def on_progress_changed():
        nonlocal signal_emitted
        signal_emitted = True
    
    item.progressChanged.connect(on_progress_changed)
    item.progress = 75
    
    assert item.progress == 75
    assert signal_emitted


def test_download_item_status_setter(app):
    """Test DownloadItem status property setter"""
    item = DownloadItem()
    signal_emitted = False
    
    def on_status_changed():
        nonlocal signal_emitted
        signal_emitted = True
    
    item.statusChanged.connect(on_status_changed)
    item.status = "Completed"
    
    assert item.status == "Completed"
    assert signal_emitted


def test_download_item_size_setter(app):
    """Test DownloadItem size property setter"""
    item = DownloadItem()
    signal_emitted = False
    
    def on_size_changed():
        nonlocal signal_emitted
        signal_emitted = True
    
    item.sizeChanged.connect(on_size_changed)
    item.size = "500 MB"
    
    assert item.size == "500 MB"
    assert signal_emitted


def test_download_item_no_signal_when_same_value(app):
    """Test that signals are not emitted when setting the same value"""
    item = DownloadItem(name="test.bin")
    signal_count = 0
    
    def on_name_changed():
        nonlocal signal_count
        signal_count += 1
    
    item.nameChanged.connect(on_name_changed)
    item.name = "test.bin"  # Same value
    
    assert signal_count == 0
