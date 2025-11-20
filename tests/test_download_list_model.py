"""Unit tests for DownloadListModel class"""
import pytest
from PySide6.QtCore import QCoreApplication, Qt
from main import DownloadListModel, DownloadItem


@pytest.fixture
def app():
    """Create QCoreApplication instance for testing"""
    return QCoreApplication.instance() or QCoreApplication([])


@pytest.fixture
def model(app):
    """Create a DownloadListModel instance"""
    return DownloadListModel()


def test_model_initialization(model):
    """Test model is initialized empty"""
    assert model.rowCount() == 0


def test_model_add_item(model):
    """Test adding an item to the model"""
    item = DownloadItem(name="test.bin", url="https://test.com")
    model.addItem(item)
    
    assert model.rowCount() == 1


def test_model_add_multiple_items(model):
    """Test adding multiple items"""
    items = [
        DownloadItem(name=f"file{i}.bin", url=f"https://test.com/{i}")
        for i in range(5)
    ]
    
    for item in items:
        model.addItem(item)
    
    assert model.rowCount() == 5


def test_model_data_retrieval(model):
    """Test retrieving data from the model"""
    item = DownloadItem(
        name="test.bin",
        url="https://test.com",
        progress=50,
        status="Downloading",
        size="100 MB"
    )
    model.addItem(item)
    
    index = model.index(0, 0)
    
    assert model.data(index, DownloadListModel.NameRole) == "test.bin"
    assert model.data(index, DownloadListModel.UrlRole) == "https://test.com"
    assert model.data(index, DownloadListModel.ProgressRole) == 50
    assert model.data(index, DownloadListModel.StatusRole) == "Downloading"
    assert model.data(index, DownloadListModel.SizeRole) == "100 MB"


def test_model_role_names(model):
    """Test role names mapping"""
    roles = model.roleNames()
    
    assert roles[DownloadListModel.NameRole] == b'name'
    assert roles[DownloadListModel.UrlRole] == b'url'
    assert roles[DownloadListModel.ProgressRole] == b'progress'
    assert roles[DownloadListModel.StatusRole] == b'status'
    assert roles[DownloadListModel.SizeRole] == b'size'


def test_model_remove_item(model):
    """Test removing an item from the model"""
    item1 = DownloadItem(name="file1.bin")
    item2 = DownloadItem(name="file2.bin")
    model.addItem(item1)
    model.addItem(item2)
    
    assert model.rowCount() == 2
    
    result = model.removeItem(0)
    
    assert result is True
    assert model.rowCount() == 1
    assert model.data(model.index(0, 0), DownloadListModel.NameRole) == "file2.bin"


def test_model_remove_invalid_index(model):
    """Test removing an item with invalid index"""
    item = DownloadItem(name="file.bin")
    model.addItem(item)
    
    result = model.removeItem(5)
    
    assert result is False
    assert model.rowCount() == 1


def test_model_get_item(model):
    """Test getting an item by index"""
    item = DownloadItem(name="test.bin")
    model.addItem(item)
    
    retrieved_item = model.getItem(0)
    
    assert retrieved_item is not None
    assert retrieved_item.name == "test.bin"


def test_model_get_item_invalid_index(model):
    """Test getting an item with invalid index"""
    retrieved_item = model.getItem(10)
    
    assert retrieved_item is None


def test_model_item_change_notification(model, app):
    """Test that model is notified when item data changes"""
    item = DownloadItem(name="test.bin")
    model.addItem(item)
    
    signal_emitted = False
    
    def on_data_changed():
        nonlocal signal_emitted
        signal_emitted = True
    
    model.dataChanged.connect(on_data_changed)
    
    # Change item property
    item.progress = 75
    app.processEvents()
    
    assert signal_emitted


def test_model_data_invalid_index(model):
    """Test data retrieval with invalid index"""
    result = model.data(model.index(10, 0), DownloadListModel.NameRole)
    
    assert result is None
