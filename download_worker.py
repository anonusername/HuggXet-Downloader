"""
Download worker implementation using QThread for asynchronous downloads.
"""

import os
from pathlib import Path
from PySide6.QtCore import QThread, Signal, QMutex
from typing import Optional
from downloaders import HuggingFaceDownloader


class DownloadWorker(QThread):
    """
    Worker thread that handles asynchronous downloads from HuggingFace.
    
    Emits signals for:
    - Progress updates (percentage, bytes downloaded, speed)
    - Status changes (downloading, paused, completed, error)
    - Messages (info, warnings, errors)
    """
    
    # Signals
    progress_updated = Signal(int)  # Progress percentage (0-100)
    status_changed = Signal(str)  # Status string
    download_completed = Signal()  # Download finished successfully
    download_failed = Signal(str)  # Download failed with error message
    message_sent = Signal(str)  # Informational message
    
    def __init__(
        self,
        download_id: int,
        platform: str,
        url: str,
        local_dir: str,
        name: str = '',
        parent=None
    ):
        """
        Initialize download worker.
        
        Args:
            download_id: Unique identifier for this download
            platform: 'huggingface'
            url: Source URL to download from
            local_dir: Local directory to save files
            name: Optional friendly name for the download
            parent: Optional parent QObject
        """
        super().__init__(parent)
        
        self.download_id = download_id
        self.platform = platform.lower()
        self.url = url
        self.local_dir = local_dir
        self.name = name or url
        
        # State management
        self._mutex = QMutex()
        self._paused = False
        self._cancelled = False
        
        # Download tracking
        self.total_bytes = 0
        self.downloaded_bytes = 0
        
        # Initialize appropriate downloader
        self.downloader = None
        if self.platform == 'huggingface':
            self.downloader = HuggingFaceDownloader()
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    def run(self):
        """
        Main thread execution method.
        Called when thread starts.
        """
        try:
            self.status_changed.emit('Preparing')
            self.message_sent.emit(f"Starting download: {self.name}")
            
            # Parse URL and detect download type
            if self.platform == 'huggingface':
                self._download_huggingface()
            else:
                raise ValueError(f"Unsupported platform: {self.platform}")
            
            # Check if cancelled before completion
            if self._cancelled:
                self.status_changed.emit('Cancelled')
                return
            
            # Download completed successfully
            self.status_changed.emit('Completed')
            self.progress_updated.emit(100)
            self.download_completed.emit()
            self.message_sent.emit(f"Completed: {self.name}")
            
        except Exception as e:
            error_msg = f"Download failed: {str(e)}"
            self.status_changed.emit('Error')
            self.download_failed.emit(error_msg)
            self.message_sent.emit(error_msg)
    
    def _download_huggingface(self):
        """Handle HuggingFace download."""
        # Parse URL
        parsed = self.downloader.parse_url(self.url)
        repo_id = parsed.get('repo_id')
        filename = parsed.get('filename')
        revision = parsed.get('revision', 'main')
        
        if not repo_id:
            raise ValueError(f"Invalid HuggingFace URL: {self.url}")
        
        # Get size before download
        if filename:
            self.total_bytes = self.downloader.get_file_size(repo_id, filename, revision)
            self.message_sent.emit(f"Downloading file: {filename}")
            self.status_changed.emit('Downloading')
            
            # Download single file
            self.downloader.download_file(
                repo_id=repo_id,
                filename=filename,
                local_dir=self.local_dir,
                revision=revision,
                progress_callback=self._progress_callback
            )
        else:
            # Download entire repository
            self.total_bytes = self.downloader.get_repo_size(repo_id, revision)
            self.message_sent.emit(f"Downloading repository: {repo_id}")
            self.status_changed.emit('Downloading')
            
            self.downloader.download_repo(
                repo_id=repo_id,
                local_dir=self.local_dir,
                revision=revision,
                progress_callback=self._progress_callback
            )
    
    def _progress_callback(self, downloaded: int, total: int):
        """
        Called by downloader to report progress.
        
        Args:
            downloaded: Bytes downloaded so far
            total: Total bytes to download
        """
        # Check if paused
        while self._paused and not self._cancelled:
            self.msleep(100)  # Sleep 100ms while paused
        
        # Check if cancelled
        if self._cancelled:
            raise InterruptedError("Download cancelled")
        
        # Update progress
        self.downloaded_bytes = downloaded
        if total > 0:
            self.total_bytes = total
            percentage = int((downloaded / total) * 100)
            self.progress_updated.emit(percentage)
    
    def pause(self):
        """Pause the download."""
        self._mutex.lock()
        self._paused = True
        self._mutex.unlock()
        self.status_changed.emit('Paused')
        self.message_sent.emit(f"Paused: {self.name}")
    
    def resume(self):
        """Resume a paused download."""
        self._mutex.lock()
        self._paused = False
        self._mutex.unlock()
        self.status_changed.emit('Downloading')
        self.message_sent.emit(f"Resumed: {self.name}")
    
    def cancel(self):
        """Cancel the download."""
        self._mutex.lock()
        self._cancelled = True
        self._paused = False  # Unpause to allow cancellation
        self._mutex.unlock()
        self.message_sent.emit(f"Cancelling: {self.name}")
    
    def is_paused(self) -> bool:
        """Check if download is paused."""
        self._mutex.lock()
        paused = self._paused
        self._mutex.unlock()
        return paused
    
    def is_cancelled(self) -> bool:
        """Check if download is cancelled."""
        self._mutex.lock()
        cancelled = self._cancelled
        self._mutex.unlock()
        return cancelled
