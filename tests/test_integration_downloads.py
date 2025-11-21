"""
Integration tests for real HuggingFace Hub downloads.

These tests perform actual downloads from HuggingFace Hub.
Run with: pytest -m integration

WARNING: These tests require network access and may take time depending
on file sizes and network speed.
"""

import os
import shutil
import tempfile
import pytest
from pathlib import Path
from PySide6.QtCore import QCoreApplication
from downloaders.huggingface_downloader import HuggingFaceDownloader


# Test repository: Wan-AI/Wan2.2-TI2V-5B
# Test file: examples/i2v_input.JPG
TEST_REPO = "Wan-AI/Wan2.2-TI2V-5B"
TEST_FILE = "examples/i2v_input.JPG"
TEST_REVISION = "main"


@pytest.fixture
def temp_download_dir():
    """Create a temporary directory for downloads."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup after test
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def downloader():
    """Create a HuggingFaceDownloader instance."""
    return HuggingFaceDownloader()


@pytest.mark.integration
class TestHuggingFaceIntegration:
    """Integration tests using real HuggingFace Hub API."""
    
    def test_parse_url_with_tree_structure(self, downloader):
        """Test parsing HuggingFace URL with tree/main/path structure."""
        url = f"https://huggingface.co/{TEST_REPO}/tree/{TEST_REVISION}/examples"
        parsed = downloader.parse_url(url)
        
        assert parsed['repo_id'] == TEST_REPO
        assert parsed['revision'] == TEST_REVISION
        assert parsed['filename'] == 'examples'
    
    def test_parse_url_with_blob_file(self, downloader):
        """Test parsing HuggingFace URL with blob/main/file structure."""
        url = f"https://huggingface.co/{TEST_REPO}/blob/{TEST_REVISION}/{TEST_FILE}"
        parsed = downloader.parse_url(url)
        
        assert parsed['repo_id'] == TEST_REPO
        assert parsed['revision'] == TEST_REVISION
        assert parsed['filename'] == TEST_FILE
    
    def test_get_repo_info(self, downloader):
        """Test getting repository information from HuggingFace."""
        repo_info = downloader.get_repo_info(TEST_REPO)
        
        assert repo_info is not None
        assert isinstance(repo_info, dict)
        assert 'repo_id' in repo_info
        assert TEST_REPO in repo_info['repo_id']
        assert 'author' in repo_info
    
    def test_list_files_in_directory(self, downloader):
        """Test listing files in a repository directory."""
        # List files in examples/ directory
        files = downloader.list_files(TEST_REPO, TEST_REVISION, 'examples')
        
        assert isinstance(files, list)
        assert len(files) > 0
        # Should contain our test file
        assert any(TEST_FILE in f for f in files)
    
    def test_get_file_size(self, downloader):
        """Test getting file size before download."""
        size = downloader.get_file_size(TEST_REPO, TEST_FILE, TEST_REVISION)
        
        assert size > 0
        # JPG files are typically at least 1KB
        assert size > 1024
    
    def test_download_single_file_cached(self, downloader, temp_download_dir):
        """Test downloading a single file using HuggingFace Hub cache."""
        # Track progress calls
        progress_calls = []
        
        def progress_callback(downloaded, total):
            progress_calls.append((downloaded, total))
        
        # Download file to temp directory
        local_path = downloader.download_file(
            repo_id=TEST_REPO,
            filename=TEST_FILE,
            local_dir=temp_download_dir,
            revision=TEST_REVISION,
            progress_callback=progress_callback
        )
        
        # Verify download
        assert local_path is not None
        assert os.path.exists(local_path)
        assert os.path.getsize(local_path) > 0
        
        # Verify progress callback was called
        assert len(progress_calls) > 0
        # Last call should have downloaded == total
        if progress_calls:
            last_downloaded, last_total = progress_calls[-1]
            assert last_downloaded == last_total
    
    def test_download_single_file_to_local_dir(self, downloader, temp_download_dir):
        """Test downloading a single file to a specific local directory."""
        progress_calls = []
        
        def progress_callback(downloaded, total):
            progress_calls.append((downloaded, total))
        
        # Download to specific directory
        local_path = downloader.download_file(
            repo_id=TEST_REPO,
            filename=TEST_FILE,
            revision=TEST_REVISION,
            local_dir=temp_download_dir,
            progress_callback=progress_callback
        )
        
        # Verify download
        assert local_path is not None
        assert os.path.exists(local_path)
        assert local_path.startswith(temp_download_dir)
        
        # Verify file structure maintained
        expected_path = os.path.join(temp_download_dir, TEST_FILE)
        assert os.path.exists(expected_path)
        assert os.path.getsize(expected_path) > 0
        
        # Verify progress tracking
        assert len(progress_calls) > 0
    
    def test_download_directory_cached(self, downloader, temp_download_dir):
        """Test downloading a directory using HuggingFace Hub cache."""
        progress_calls = []
        
        def progress_callback(downloaded, total):
            progress_calls.append((downloaded, total))
        
        # Download examples/ directory to temp_download_dir
        local_path = downloader.download_repo(
            repo_id=TEST_REPO,
            local_dir=temp_download_dir,
            revision=TEST_REVISION,
            allow_patterns=["examples/*"],  # Only download examples directory
            progress_callback=progress_callback
        )
        
        # Verify download
        assert local_path is not None
        assert os.path.exists(local_path)
        
        # Verify our test file is in the downloaded directory
        test_file_path = os.path.join(local_path, TEST_FILE)
        assert os.path.exists(test_file_path)
        assert os.path.getsize(test_file_path) > 0
        
        # Verify progress callback was called
        assert len(progress_calls) > 0
    
    def test_download_directory_to_local_dir(self, downloader, temp_download_dir):
        """Test downloading a directory to a specific local directory."""
        progress_calls = []
        
        def progress_callback(downloaded, total):
            progress_calls.append((downloaded, total))
        
        # Download examples/ directory to local_dir
        local_path = downloader.download_repo(
            repo_id=TEST_REPO,
            revision=TEST_REVISION,
            local_dir=temp_download_dir,
            allow_patterns=["examples/*"],
            progress_callback=progress_callback
        )
        
        # Verify download
        assert local_path == temp_download_dir
        assert os.path.exists(local_path)
        
        # Verify file structure maintained
        test_file_path = os.path.join(temp_download_dir, TEST_FILE)
        assert os.path.exists(test_file_path)
        assert os.path.getsize(test_file_path) > 0
        
        # Verify progress tracking
        assert len(progress_calls) > 0
    
    def test_error_handling_invalid_repo(self, downloader):
        """Test error handling for non-existent repository."""
        with pytest.raises(ValueError, match="Repository not found"):
            downloader.get_repo_info("invalid-user/nonexistent-repo-12345")
    
    def test_error_handling_invalid_file(self, downloader, temp_download_dir):
        """Test error handling for non-existent file."""
        with pytest.raises(RuntimeError, match="Failed to download"):
            downloader.download_file(
                repo_id=TEST_REPO,
                filename="nonexistent-file-12345.txt",
                local_dir=temp_download_dir,
                revision=TEST_REVISION
            )
    
    def test_error_handling_invalid_revision(self, downloader, temp_download_dir):
        """Test error handling for non-existent revision."""
        # Using download_file with invalid revision should raise an error
        with pytest.raises(RuntimeError, match="Failed to download"):
            downloader.download_file(
                repo_id=TEST_REPO,
                filename=TEST_FILE,
                local_dir=temp_download_dir,
                revision="nonexistent-branch-12345"
            )


@pytest.mark.integration
class TestHuggingFaceWithHfXet:
    """
    Integration tests for HuggingFace Hub with hf_xet optimization.
    
    Note: hf_xet is automatically used by huggingface_hub >= 0.32.0 if installed.
    These tests verify downloads work with the Xet storage backend.
    """
    
    def test_download_with_xet_backend(self, temp_download_dir):
        """Test that downloads work with hf_xet backend (if available)."""
        downloader = HuggingFaceDownloader()
        
        # Download using the standard API (will use hf_xet if available)
        local_path = downloader.download_file(
            repo_id=TEST_REPO,
            filename=TEST_FILE,
            revision=TEST_REVISION,
            local_dir=temp_download_dir
        )
        
        # Verify download succeeded regardless of backend
        assert local_path is not None
        assert os.path.exists(local_path)
        assert os.path.getsize(local_path) > 0
    
    def test_large_file_download_with_progress(self, temp_download_dir):
        """Test downloading and tracking progress on a file."""
        downloader = HuggingFaceDownloader()
        progress_updates = []
        
        def track_progress(downloaded, total):
            if total > 0:
                percent = (downloaded / total) * 100
                progress_updates.append(percent)
        
        # Download the test file
        local_path = downloader.download_file(
            repo_id=TEST_REPO,
            filename=TEST_FILE,
            revision=TEST_REVISION,
            local_dir=temp_download_dir,
            progress_callback=track_progress
        )
        
        # Verify download
        assert os.path.exists(local_path)
        
        # Verify progress tracking worked
        assert len(progress_updates) > 0
        # Progress should reach 100%
        assert any(p >= 99.0 for p in progress_updates)


@pytest.mark.integration
class TestDownloadURLFormats:
    """Test various URL formats for HuggingFace."""
    
    @pytest.fixture
    def downloader(self):
        return HuggingFaceDownloader()
    
    def test_url_format_basic_repo(self, downloader):
        """Test: https://huggingface.co/user/repo"""
        url = f"https://huggingface.co/{TEST_REPO}"
        parsed = downloader.parse_url(url)
        
        assert parsed['repo_id'] == TEST_REPO
        assert parsed.get('filename') is None or parsed.get('filename') == ''
    
    def test_url_format_blob_main(self, downloader):
        """Test: https://huggingface.co/user/repo/blob/main/file.ext"""
        url = f"https://huggingface.co/{TEST_REPO}/blob/main/{TEST_FILE}"
        parsed = downloader.parse_url(url)
        
        assert parsed['repo_id'] == TEST_REPO
        assert parsed['filename'] == TEST_FILE
        assert parsed['revision'] == 'main'
    
    def test_url_format_tree_main(self, downloader):
        """Test: https://huggingface.co/user/repo/tree/main/directory"""
        url = f"https://huggingface.co/{TEST_REPO}/tree/main/examples"
        parsed = downloader.parse_url(url)
        
        assert parsed['repo_id'] == TEST_REPO
        assert parsed['filename'] == 'examples'
        assert parsed['revision'] == 'main'
    
    def test_url_format_without_protocol(self, downloader):
        """Test: huggingface.co/user/repo/blob/main/file.ext"""
        url = f"huggingface.co/{TEST_REPO}/blob/main/{TEST_FILE}"
        parsed = downloader.parse_url(url)
        
        assert parsed['repo_id'] == TEST_REPO
        assert parsed['filename'] == TEST_FILE
