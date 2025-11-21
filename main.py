#!/usr/bin/env python3
"""
HuggXet-Downloader - Main application entry point
A modern touch-enabled download manager built with PySide6 and QML
"""
import sys
import os
import json
from pathlib import Path
from PySide6.QtCore import QObject, Signal, Slot, Property, QUrl, QAbstractListModel, QModelIndex, Qt, QStandardPaths
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QQmlContext
from download_worker import DownloadWorker
from downloaders import HuggingFaceDownloader


class DownloadItem(QObject):
    """Represents a single download item"""
    
    nameChanged = Signal()
    urlChanged = Signal()
    progressChanged = Signal()
    statusChanged = Signal()
    sizeChanged = Signal()
    priorityChanged = Signal()
    
    def __init__(self, name="", url="", progress=0, status="Pending", size="0 MB", priority=1, parent=None):
        super().__init__(parent)
        self._name = name
        self._url = url
        self._progress = progress
        self._status = status
        self._size = size
        self._priority = priority
    
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
    
    @Property(int, notify=priorityChanged)
    def priority(self):
        return self._priority
    
    @priority.setter
    def priority(self, value):
        if self._priority != value:
            self._priority = value
            self.priorityChanged.emit()
    
    def to_dict(self):
        """Convert download item to dictionary for JSON serialization"""
        return {
            "name": self._name,
            "url": self._url,
            "progress": self._progress,
            "status": self._status,
            "size": self._size,
            "priority": self._priority
        }
    
    @staticmethod
    def from_dict(data, parent=None):
        """Create download item from dictionary"""
        return DownloadItem(
            name=data.get("name", ""),
            url=data.get("url", ""),
            progress=data.get("progress", 0),
            status=data.get("status", "Pending"),
            size=data.get("size", "0 MB"),
            priority=data.get("priority", 1),
            parent=parent
        )


class DownloadListModel(QAbstractListModel):
    """Qt model for managing download items"""
    
    NameRole = Qt.UserRole + 1
    UrlRole = Qt.UserRole + 2
    ProgressRole = Qt.UserRole + 3
    StatusRole = Qt.UserRole + 4
    SizeRole = Qt.UserRole + 5
    PriorityRole = Qt.UserRole + 6
    
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
        elif role == self.PriorityRole:
            return item.priority
        
        return None
    
    def roleNames(self):
        return {
            self.NameRole: b'name',
            self.UrlRole: b'url',
            self.ProgressRole: b'progress',
            self.StatusRole: b'status',
            self.SizeRole: b'size',
            self.PriorityRole: b'priority'
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
        item.priorityChanged.connect(lambda: self._itemChanged(item))
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
        self._save_file = self._get_save_file_path()
        self._workers = {}  # Dictionary to track active download workers
        self._next_id = 1  # Counter for unique download IDs
        # Load saved downloads on startup
        self._load_downloads()
    
    def _get_save_file_path(self):
        """Get platform-appropriate save file location"""
        data_dir = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        Path(data_dir).mkdir(parents=True, exist_ok=True)
        return Path(data_dir) / "downloads.json"
    
    def _detect_platform(self, url: str) -> str:
        """
        Detect platform from URL.
        
        Args:
            url: URL to analyze
        
        Returns:
            'huggingface' or 'unknown'
        """
        url_lower = url.lower()
        
        if 'huggingface.co' in url_lower:
            return 'huggingface'
        else:
            return 'unknown'
    
    def _save_downloads(self):
        """Save downloads to JSON file"""
        try:
            downloads_data = []
            for i in range(self._model.rowCount()):
                item = self._model.getItem(i)
                if item:
                    downloads_data.append(item.to_dict())
            
            with open(self._save_file, 'w', encoding='utf-8') as f:
                json.dump(downloads_data, f, indent=2)
        except Exception as e:
            print(f"Error saving downloads: {e}")
    
    def _load_downloads(self):
        """Load downloads from JSON file"""
        try:
            if self._save_file.exists():
                with open(self._save_file, 'r', encoding='utf-8') as f:
                    downloads_data = json.load(f)
                
                for data in downloads_data:
                    item = DownloadItem.from_dict(data, parent=self._model)
                    self._model.addItem(item)
                
                if downloads_data:
                    self.downloadsChanged.emit()
                    self._status_message = f"Loaded {len(downloads_data)} downloads"
        except Exception as e:
            print(f"Error loading downloads: {e}")
    
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
        # Detect platform
        platform = self._detect_platform(url)
        
        if platform == 'unknown':
            self._status_message = f"Error: Unsupported URL format: {url}"
            self.statusMessageChanged.emit(self._status_message)
            return
        
        # Create download item
        new_item = DownloadItem(name, url, 0, "Pending", "Unknown")
        self._model.addItem(new_item)
        self.downloadsChanged.emit()
        self.downloadAdded.emit(name, url)
        self._status_message = f"Added: {name} ({platform})"
        self.statusMessageChanged.emit(self._status_message)
        self._save_downloads()
    
    @Slot(int)
    def removeDownload(self, index):
        """Remove a download from the queue"""
        item = self._model.getItem(index)
        if item:
            removed_name = item.name
            
            # Cancel and clean up worker if exists
            if index in self._workers:
                self._workers[index].cancel()
                self._workers[index].wait()  # Wait for thread to finish
                self._workers[index].deleteLater()
                del self._workers[index]
            
            self._model.removeItem(index)
            self.downloadsChanged.emit()
            self.downloadRemoved.emit(index)
            self._status_message = f"Removed: {removed_name}"
            self.statusMessageChanged.emit(self._status_message)
            self._save_downloads()
    
    @Slot(int)
    def startDownload(self, index):
        """Start or resume a download"""
        item = self._model.getItem(index)
        if not item:
            return
        
        # Check if worker already exists for this download
        if index in self._workers:
            worker = self._workers[index]
            if worker.is_paused():
                worker.resume()
                return
        
        # Only start new downloads or paused ones
        if item.status not in ["Pending", "Paused"]:
            return
        
        # Detect platform
        platform = self._detect_platform(item.url)
        if platform == 'unknown':
            item.status = "Error"
            self._status_message = f"Error: Unsupported URL for {item.name}"
            self.statusMessageChanged.emit(self._status_message)
            return
        
        # Get default download directory
        download_dir = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
        local_dir = Path(download_dir) / item.name
        
        # Create worker
        worker = DownloadWorker(
            download_id=self._next_id,
            platform=platform,
            url=item.url,
            local_dir=str(local_dir),
            name=item.name
        )
        self._next_id += 1
        
        # Connect signals
        worker.progress_updated.connect(lambda p: self._on_progress_updated(index, p))
        worker.status_changed.connect(lambda s: self._on_status_changed(index, s))
        worker.download_completed.connect(lambda: self._on_download_completed(index))
        worker.download_failed.connect(lambda e: self._on_download_failed(index, e))
        worker.message_sent.connect(lambda m: self._on_message_sent(m))
        
        # Store worker and start
        self._workers[index] = worker
        worker.start()
        
        item.status = "Preparing"
        self._status_message = f"Starting: {item.name}"
        self.statusMessageChanged.emit(self._status_message)
        self._save_downloads()
    
    @Slot(int)
    def pauseDownload(self, index):
        """Pause a download"""
        item = self._model.getItem(index)
        if not item or item.status != "Downloading":
            return
        
        # Pause worker if exists
        if index in self._workers:
            self._workers[index].pause()
        
        item.status = "Paused"
        self._status_message = f"Paused: {item.name}"
        self.statusMessageChanged.emit(self._status_message)
        self._save_downloads()
    
    def _on_progress_updated(self, index: int, percentage: int):
        """Handle progress update from worker"""
        item = self._model.getItem(index)
        if item:
            item.progress = percentage
    
    def _on_status_changed(self, index: int, status: str):
        """Handle status change from worker"""
        item = self._model.getItem(index)
        if item:
            item.status = status
            self._save_downloads()
    
    def _on_download_completed(self, index: int):
        """Handle download completion"""
        item = self._model.getItem(index)
        if item:
            item.status = "Completed"
            item.progress = 100
            self._status_message = f"Completed: {item.name}"
            self.statusMessageChanged.emit(self._status_message)
            self._save_downloads()
        
        # Clean up worker
        if index in self._workers:
            self._workers[index].deleteLater()
            del self._workers[index]
    
    def _on_download_failed(self, index: int, error: str):
        """Handle download failure"""
        item = self._model.getItem(index)
        if item:
            item.status = "Error"
            self._status_message = f"Error: {item.name} - {error}"
            self.statusMessageChanged.emit(self._status_message)
            self._save_downloads()
        
        # Clean up worker
        if index in self._workers:
            self._workers[index].deleteLater()
            del self._workers[index]
    
    def _on_message_sent(self, message: str):
        """Handle message from worker"""
        self._status_message = message
        self.statusMessageChanged.emit(message)
    
    @Slot()
    def startAll(self):
        """Start all pending/paused downloads"""
        count = 0
        for i in range(self._model.rowCount()):
            item = self._model.getItem(i)
            if item and item.status in ["Pending", "Paused"]:
                self.startDownload(i)
                count += 1
        
        if count > 0:
            self._status_message = f"Starting {count} downloads"
            self.statusMessageChanged.emit(self._status_message)
    
    @Slot()
    def pauseAll(self):
        """Pause all active downloads"""
        count = 0
        for i in range(self._model.rowCount()):
            item = self._model.getItem(i)
            if item and item.status == "Downloading":
                self.pauseDownload(i)
                count += 1
        
        if count > 0:
            self._status_message = f"Paused {count} downloads"
            self.statusMessageChanged.emit(self._status_message)
    
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
        
        if removed > 0:
            self._status_message = f"Cleared {removed} completed downloads"
            self.statusMessageChanged.emit(self._status_message)
            self._save_downloads()


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
    
    # Load main QML file - handle both development and bundled paths
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        qml_file = Path(sys._MEIPASS) / "qml" / "main.qml"
    else:
        # Running as script
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
