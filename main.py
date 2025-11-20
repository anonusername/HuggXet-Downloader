#!/usr/bin/env python3
"""
HuggXet-Downloader - Main application entry point
A modern touch-enabled download manager built with PySide6 and QML
"""
import sys
import os
from pathlib import Path
from PySide6.QtCore import QObject, Signal, Slot, Property, QUrl, QAbstractListModel, QModelIndex, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QQmlContext


class DownloadItem(QObject):
    """Represents a single download item"""
    
    nameChanged = Signal()
    urlChanged = Signal()
    progressChanged = Signal()
    statusChanged = Signal()
    sizeChanged = Signal()
    
    def __init__(self, name="", url="", progress=0, status="Pending", size="0 MB", parent=None):
        super().__init__(parent)
        self._name = name
        self._url = url
        self._progress = progress
        self._status = status
        self._size = size
    
    @Property(str, notify=nameChanged)
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        if self._name != value:
            self._name = value
            self.nameChanged.emit()
    
    @Property(str, notify=urlChanged)
    def url(self):
        return self._url
    
    @url.setter
    def url(self, value):
        if self._url != value:
            self._url = value
            self.urlChanged.emit()
    
    @Property(int, notify=progressChanged)
    def progress(self):
        return self._progress
    
    @progress.setter
    def progress(self, value):
        if self._progress != value:
            self._progress = value
            self.progressChanged.emit()
    
    @Property(str, notify=statusChanged)
    def status(self):
        return self._status
    
    @status.setter
    def status(self, value):
        if self._status != value:
            self._status = value
            self.statusChanged.emit()
    
    @Property(str, notify=sizeChanged)
    def size(self):
        return self._size
    
    @size.setter
    def size(self, value):
        if self._size != value:
            self._size = value
            self.sizeChanged.emit()


class DownloadListModel(QAbstractListModel):
    """Qt model for managing download items"""
    
    NameRole = Qt.UserRole + 1
    UrlRole = Qt.UserRole + 2
    ProgressRole = Qt.UserRole + 3
    StatusRole = Qt.UserRole + 4
    SizeRole = Qt.UserRole + 5
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
    
    def rowCount(self, parent=QModelIndex()):
        return len(self._items)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._items):
            return None
        
        item = self._items[index.row()]
        
        if role == self.NameRole:
            return item.name
        elif role == self.UrlRole:
            return item.url
        elif role == self.ProgressRole:
            return item.progress
        elif role == self.StatusRole:
            return item.status
        elif role == self.SizeRole:
            return item.size
        
        return None
    
    def roleNames(self):
        return {
            self.NameRole: b'name',
            self.UrlRole: b'url',
            self.ProgressRole: b'progress',
            self.StatusRole: b'status',
            self.SizeRole: b'size'
        }
    
    def addItem(self, item):
        """Add a new item to the model"""
        self.beginInsertRows(QModelIndex(), len(self._items), len(self._items))
        self._items.append(item)
        # Connect to item signals to update the view
        item.nameChanged.connect(lambda: self._itemChanged(item))
        item.urlChanged.connect(lambda: self._itemChanged(item))
        item.progressChanged.connect(lambda: self._itemChanged(item))
        item.statusChanged.connect(lambda: self._itemChanged(item))
        item.sizeChanged.connect(lambda: self._itemChanged(item))
        self.endInsertRows()
    
    def removeItem(self, index):
        """Remove an item from the model"""
        if 0 <= index < len(self._items):
            self.beginRemoveRows(QModelIndex(), index, index)
            del self._items[index]
            self.endRemoveRows()
            return True
        return False
    
    def getItem(self, index):
        """Get an item by index"""
        if 0 <= index < len(self._items):
            return self._items[index]
        return None
    
    def _itemChanged(self, item):
        """Called when an item's data changes"""
        try:
            index = self._items.index(item)
            model_index = self.createIndex(index, 0)
            self.dataChanged.emit(model_index, model_index, [])
        except ValueError:
            pass


class DownloadBackend(QObject):
    """Backend logic for managing downloads"""
    
    downloadsChanged = Signal()
    downloadAdded = Signal(str, str)
    downloadRemoved = Signal(int)
    statusMessageChanged = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = DownloadListModel(self)
        self._status_message = "Ready"
        self._init_sample_data()
    
    def _init_sample_data(self):
        """Initialize with sample download data"""
        sample_downloads = [
            DownloadItem("model-bert-base.bin", "https://huggingface.co/bert-base", 75, "Downloading", "420 MB"),
            DownloadItem("dataset-common-voice.tar.gz", "https://huggingface.co/datasets/mozilla", 30, "Downloading", "2.1 GB"),
            DownloadItem("tokenizer-gpt2.json", "https://huggingface.co/gpt2", 100, "Completed", "1.2 MB"),
            DownloadItem("config-xlnet.yaml", "https://huggingface.co/xlnet", 50, "Paused", "3.5 KB"),
            DownloadItem("weights-roberta-large.pt", "https://huggingface.co/roberta", 0, "Pending", "1.5 GB"),
            DownloadItem("vocab-t5-small.txt", "https://huggingface.co/t5-small", 100, "Completed", "890 KB"),
        ]
        for item in sample_downloads:
            self._model.addItem(item)
        self.downloadsChanged.emit()
    
    @Property(QObject, notify=downloadsChanged)
    def downloadsModel(self):
        return self._model
    
    @Property(str, notify=statusMessageChanged)
    def statusMessage(self):
        return self._status_message
    
    @statusMessage.setter
    def statusMessage(self, value):
        if self._status_message != value:
            self._status_message = value
            self.statusMessageChanged.emit(value)
    
    @Slot(str, str)
    def addDownload(self, name, url):
        """Add a new download to the queue"""
        new_item = DownloadItem(name, url, 0, "Pending", "Unknown")
        self._model.addItem(new_item)
        self.downloadsChanged.emit()
        self.downloadAdded.emit(name, url)
        self.statusMessage = f"Added: {name}"
    
    @Slot(int)
    def removeDownload(self, index):
        """Remove a download from the queue"""
        item = self._model.getItem(index)
        if item:
            removed_name = item.name
            self._model.removeItem(index)
            self.downloadsChanged.emit()
            self.downloadRemoved.emit(index)
            self.statusMessage = f"Removed: {removed_name}"
    
    @Slot(int)
    def startDownload(self, index):
        """Start or resume a download"""
        item = self._model.getItem(index)
        if item and item.status in ["Pending", "Paused"]:
            item.status = "Downloading"
            self.statusMessage = f"Started: {item.name}"
    
    @Slot(int)
    def pauseDownload(self, index):
        """Pause a download"""
        item = self._model.getItem(index)
        if item and item.status == "Downloading":
            item.status = "Paused"
            self.statusMessage = f"Paused: {item.name}"
    
    @Slot()
    def startAll(self):
        """Start all pending/paused downloads"""
        count = 0
        for i in range(self._model.rowCount()):
            item = self._model.getItem(i)
            if item and item.status in ["Pending", "Paused"]:
                item.status = "Downloading"
                count += 1
        self.statusMessage = f"Started {count} downloads"
    
    @Slot()
    def pauseAll(self):
        """Pause all active downloads"""
        count = 0
        for i in range(self._model.rowCount()):
            item = self._model.getItem(i)
            if item and item.status == "Downloading":
                item.status = "Paused"
                count += 1
        self.statusMessage = f"Paused {count} downloads"
    
    @Slot()
    def clearCompleted(self):
        """Remove all completed downloads"""
        i = 0
        removed = 0
        while i < self._model.rowCount():
            item = self._model.getItem(i)
            if item and item.status == "Completed":
                self._model.removeItem(i)
                removed += 1
            else:
                i += 1
        self.downloadsChanged.emit()
        self.statusMessage = f"Cleared {removed} completed downloads"


def main():
    """Main application entry point"""
    # Set up the application
    app = QGuiApplication(sys.argv)
    app.setOrganizationName("HuggXet")
    app.setOrganizationDomain("huggxet.io")
    app.setApplicationName("HuggXet Downloader")
    
    # Create QML engine
    engine = QQmlApplicationEngine()
    
    # Create backend
    backend = DownloadBackend()
    
    # Expose backend to QML via context properties
    context = engine.rootContext()
    context.setContextProperty("downloadBackend", backend)
    
    # Load main QML file
    qml_file = Path(__file__).parent / "qml" / "main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    
    # Check if QML loaded successfully
    if not engine.rootObjects():
        print("Error: Failed to load QML file")
        return -1
    
    # Run the application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
