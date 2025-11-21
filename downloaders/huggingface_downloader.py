"""
HuggingFace Hub downloader implementation using huggingface_hub library.
"""

import os
from pathlib import Path
from typing import Optional, Callable
from huggingface_hub import hf_hub_download, snapshot_download, HfApi, hf_hub_url
from huggingface_hub.utils import RepositoryNotFoundError, HfHubHTTPError


class HuggingFaceDownloader:
    """
    Handles downloads from HuggingFace Hub.
    
    Supports:
    - Single file downloads: hf_hub_download()
    - Full repository downloads: snapshot_download()
    - Progress tracking via callbacks
    - File size detection before download
    """
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize HuggingFace downloader.
        
        Args:
            token: Optional HuggingFace API token for private repos.
                   If None, will use HF_TOKEN environment variable or
                   token from huggingface-cli login.
        """
        self.token = token
        self.api = HfApi(token=token)
    
    def parse_url(self, url: str) -> dict:
        """
        Parse a HuggingFace URL into components.
        
        Args:
            url: HuggingFace URL like:
                - https://huggingface.co/openai/gpt-oss-20b
                - https://huggingface.co/openai/gpt-oss-20b/blob/main/config.json
                - huggingface.co/openai/gpt-oss-20b
        
        Returns:
            dict with keys: repo_id, filename (optional), revision (optional)
        """
        # Remove protocol if present
        clean_url = url.replace('https://', '').replace('http://', '')
        clean_url = clean_url.replace('huggingface.co/', '')
        
        parts = clean_url.split('/')
        
        # Handle different URL formats
        result = {'repo_id': None, 'filename': None, 'revision': 'main'}
        
        if len(parts) >= 2:
            # Basic format: owner/repo
            result['repo_id'] = f"{parts[0]}/{parts[1]}"
            
            # Check for /blob/branch/path format
            if len(parts) > 2 and parts[2] in ['blob', 'resolve', 'tree']:
                if len(parts) > 3:
                    result['revision'] = parts[3]
                if len(parts) > 4:
                    result['filename'] = '/'.join(parts[4:])
            elif len(parts) > 2:
                # Assume rest is a file path
                result['filename'] = '/'.join(parts[2:])
        
        return result
    
    def get_repo_info(self, repo_id: str, revision: str = 'main') -> dict:
        """
        Get information about a repository.
        
        Args:
            repo_id: Repository ID (e.g., 'openai/gpt-oss-20b')
            revision: Git revision (branch, tag, or commit hash)
        
        Returns:
            dict with repo metadata
        """
        try:
            info = self.api.repo_info(repo_id=repo_id, revision=revision)
            return {
                'repo_id': info.id,
                'author': info.author,
                'sha': info.sha,
                'last_modified': info.lastModified,
                'private': info.private,
                'downloads': getattr(info, 'downloads', 0),
                'likes': getattr(info, 'likes', 0),
            }
        except (RepositoryNotFoundError, HfHubHTTPError) as e:
            raise ValueError(f"Repository not found or inaccessible: {repo_id}") from e
    
    def list_files(self, repo_id: str, revision: str = 'main', path: str = '') -> list:
        """
        List files in a repository.
        
        Args:
            repo_id: Repository ID
            revision: Git revision
            path: Optional subdirectory path
        
        Returns:
            List of file paths (relative to repo root)
        """
        try:
            files = self.api.list_repo_files(repo_id=repo_id, revision=revision)
            
            # Filter by path if specified
            if path:
                path = path.rstrip('/')
                files = [f for f in files if f.startswith(path)]
            
            return files
        except (RepositoryNotFoundError, HfHubHTTPError) as e:
            raise ValueError(f"Cannot list files in {repo_id}") from e
    
    def get_file_size(self, repo_id: str, filename: str, revision: str = 'main') -> int:
        """
        Get the size of a specific file without downloading.
        
        Args:
            repo_id: Repository ID
            filename: File path within repo
            revision: Git revision
        
        Returns:
            File size in bytes, or 0 if unknown
        """
        try:
            # Get repo tree info
            files = self.api.list_repo_tree(repo_id=repo_id, revision=revision, recursive=True)
            
            for file_info in files:
                if hasattr(file_info, 'path') and file_info.path == filename:
                    return getattr(file_info, 'size', 0)
            
            return 0
        except Exception:
            return 0
    
    def get_repo_size(self, repo_id: str, revision: str = 'main') -> int:
        """
        Calculate total size of all files in repository.
        
        Args:
            repo_id: Repository ID
            revision: Git revision
        
        Returns:
            Total size in bytes
        """
        try:
            files = self.api.list_repo_tree(repo_id=repo_id, revision=revision, recursive=True)
            total_size = sum(getattr(f, 'size', 0) for f in files)
            return total_size
        except Exception:
            return 0
    
    def download_file(
        self,
        repo_id: str,
        filename: str,
        local_dir: str,
        revision: str = 'main',
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> str:
        """
        Download a single file from HuggingFace Hub.
        
        Args:
            repo_id: Repository ID (e.g., 'openai/gpt-oss-20b')
            filename: File path within the repo
            local_dir: Local directory to save the file
            revision: Git revision (branch, tag, or commit)
            progress_callback: Optional callback(bytes_downloaded, total_bytes)
        
        Returns:
            Path to the downloaded file
        """
        try:
            # Create local directory if needed
            os.makedirs(local_dir, exist_ok=True)
            
            # Download file
            file_path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                revision=revision,
                local_dir=local_dir,
                token=self.token,
            )
            
            # Call progress callback if provided (100% after download completes)
            if progress_callback:
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                progress_callback(file_size, file_size)
            
            return file_path
        except Exception as e:
            raise RuntimeError(f"Failed to download {filename} from {repo_id}: {str(e)}") from e
    
    def download_repo(
        self,
        repo_id: str,
        local_dir: str,
        revision: str = 'main',
        allow_patterns: Optional[list] = None,
        ignore_patterns: Optional[list] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> str:
        """
        Download an entire repository from HuggingFace Hub.
        
        Args:
            repo_id: Repository ID
            local_dir: Local directory to save the repo
            revision: Git revision
            allow_patterns: Optional list of glob patterns to include
            ignore_patterns: Optional list of glob patterns to exclude
            progress_callback: Optional callback(bytes_downloaded, total_bytes)
        
        Returns:
            Path to the downloaded repository directory
        """
        try:
            # Create local directory if needed
            os.makedirs(local_dir, exist_ok=True)
            
            # Download entire repository
            repo_path = snapshot_download(
                repo_id=repo_id,
                revision=revision,
                local_dir=local_dir,
                allow_patterns=allow_patterns,
                ignore_patterns=ignore_patterns,
                token=self.token,
            )
            
            # Call progress callback if provided (100% after download completes)
            if progress_callback:
                # Calculate total size of downloaded files
                total_size = sum(
                    os.path.getsize(os.path.join(dirpath, filename))
                    for dirpath, _, filenames in os.walk(repo_path)
                    for filename in filenames
                )
                progress_callback(total_size, total_size)
            
            return repo_path
        except Exception as e:
            raise RuntimeError(f"Failed to download repository {repo_id}: {str(e)}") from e
