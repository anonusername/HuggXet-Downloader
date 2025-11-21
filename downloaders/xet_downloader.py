"""
XetHub downloader implementation using pyxet library.
"""

import os
from pathlib import Path
from typing import Optional, Callable
import pyxet
from pyxet import XetFS


class XetDownloader:
    """
    Handles downloads from XetHub using pyxet (fsspec-based).
    
    Supports:
    - Single file downloads using XetFS.get()
    - Full repository downloads using XetFS.get() with recursive=True
    - Progress tracking (basic)
    - File size detection before download
    """
    
    def __init__(self, username: Optional[str] = None, token: Optional[str] = None):
        """
        Initialize XetHub downloader.
        
        Args:
            username: Optional XetHub username for private repos
            token: Optional XetHub access token for private repos
                   If provided, will call pyxet.login()
        """
        self.username = username
        self.token = token
        
        # Authenticate if credentials provided
        if username and token:
            pyxet.login(username, token)
        
        # Create filesystem instance
        self.fs = XetFS()
    
    def parse_url(self, url: str) -> dict:
        """
        Parse a XetHub URL into components.
        
        Args:
            url: XetHub URL like:
                - xet://xethub.com:user/repo/main/file.csv
                - https://xethub.com/user/repo/blob/main/file.csv
                - xethub.com/user/repo
        
        Returns:
            dict with keys: endpoint, user, repo, branch, path
        """
        # Handle different URL formats
        clean_url = url.replace('https://', '').replace('http://', '')
        
        # Handle xet:// protocol
        if 'xet://' in url:
            clean_url = url.replace('xet://', '')
        
        # Default values
        result = {
            'endpoint': 'xethub.com',
            'user': None,
            'repo': None,
            'branch': 'main',
            'path': ''
        }
        
        # Parse endpoint if present (format: xethub.com:user/repo)
        if ':' in clean_url:
            endpoint, rest = clean_url.split(':', 1)
            result['endpoint'] = endpoint
            clean_url = rest
        else:
            # Remove domain if present
            clean_url = clean_url.replace('xethub.com/', '').replace('xethub.com', '')
        
        # Parse user/repo/branch/path
        parts = clean_url.strip('/').split('/')
        
        if len(parts) >= 1 and parts[0]:
            result['user'] = parts[0]
        if len(parts) >= 2:
            result['repo'] = parts[1]
        
        # Check for /blob/branch/path or /tree/branch/path format
        if len(parts) > 2 and parts[2] in ['blob', 'tree', 'resolve']:
            if len(parts) > 3:
                result['branch'] = parts[3]
            if len(parts) > 4:
                result['path'] = '/'.join(parts[4:])
        elif len(parts) > 2:
            # Assume third part is branch if it doesn't contain a dot (not a file)
            if '.' not in parts[2]:
                result['branch'] = parts[2]
                if len(parts) > 3:
                    result['path'] = '/'.join(parts[3:])
            else:
                # It's likely a file path, keep branch as 'main'
                result['path'] = '/'.join(parts[2:])
        
        return result
    
    def build_xet_path(self, user: str, repo: str, branch: str = 'main', path: str = '') -> str:
        """
        Build a valid xet:// path from components.
        
        Args:
            user: Repository user/owner
            repo: Repository name
            branch: Branch name (default: 'main')
            path: File path within repo (default: '')
        
        Returns:
            Full xet:// path string
        """
        base = f"{user}/{repo}/{branch}"
        if path:
            return f"{base}/{path.lstrip('/')}"
        return base
    
    def get_repo_info(self, user: str, repo: str, branch: str = 'main') -> dict:
        """
        Get information about a repository.
        
        Args:
            user: Repository owner
            repo: Repository name
            branch: Branch name
        
        Returns:
            dict with repo metadata
        """
        try:
            xet_path = self.build_xet_path(user, repo, branch)
            
            # Check if repo exists by trying to list it
            if not self.fs.is_repo(f"{user}/{repo}"):
                raise ValueError(f"Repository not found: {user}/{repo}")
            
            # Get branch info if available
            branch_info = self.fs.branch_info(xet_path)
            
            return {
                'user': user,
                'repo': repo,
                'branch': branch,
                'exists': True,
                'branch_info': branch_info
            }
        except Exception as e:
            raise ValueError(f"Repository not found or inaccessible: {user}/{repo}") from e
    
    def list_files(self, user: str, repo: str, branch: str = 'main', path: str = '') -> list:
        """
        List files in a repository.
        
        Args:
            user: Repository owner
            repo: Repository name
            branch: Branch name
            path: Optional subdirectory path
        
        Returns:
            List of file paths (relative to repo root)
        """
        try:
            xet_path = self.build_xet_path(user, repo, branch, path)
            
            # List files
            files = self.fs.ls(xet_path, detail=True)
            
            # Extract just the file paths
            file_list = []
            for item in files:
                if item.get('type') == 'file':
                    # Extract path relative to repo
                    name = item['name']
                    # Remove the base path to get relative path
                    base = f"{user}/{repo}/{branch}/"
                    if base in name:
                        relative_path = name.split(base, 1)[1]
                        file_list.append(relative_path)
            
            return file_list
        except Exception as e:
            raise ValueError(f"Cannot list files in {user}/{repo}/{branch}/{path}") from e
    
    def get_file_size(self, user: str, repo: str, filename: str, branch: str = 'main') -> int:
        """
        Get the size of a specific file without downloading.
        
        Args:
            user: Repository owner
            repo: Repository name
            filename: File path within repo
            branch: Branch name
        
        Returns:
            File size in bytes, or 0 if unknown
        """
        try:
            xet_path = self.build_xet_path(user, repo, branch, filename)
            
            # Get file info
            info = self.fs.info(xet_path)
            return info.get('size', 0)
        except Exception:
            return 0
    
    def get_repo_size(self, user: str, repo: str, branch: str = 'main') -> int:
        """
        Calculate total size of all files in repository.
        
        Args:
            user: Repository owner
            repo: Repository name
            branch: Branch name
        
        Returns:
            Total size in bytes
        """
        try:
            xet_path = self.build_xet_path(user, repo, branch)
            
            # List all files recursively
            files = self.fs.ls(xet_path, detail=True)
            
            total_size = 0
            for item in files:
                if item.get('type') == 'file':
                    total_size += item.get('size', 0)
            
            return total_size
        except Exception:
            return 0
    
    def download_file(
        self,
        user: str,
        repo: str,
        filename: str,
        local_dir: str,
        branch: str = 'main',
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> str:
        """
        Download a single file from XetHub.
        
        Args:
            user: Repository owner
            repo: Repository name
            filename: File path within the repo
            local_dir: Local directory to save the file
            branch: Branch name
            progress_callback: Optional callback(bytes_downloaded, total_bytes)
        
        Returns:
            Path to the downloaded file
        """
        try:
            # Create local directory if needed
            os.makedirs(local_dir, exist_ok=True)
            
            # Build xet path
            xet_path = self.build_xet_path(user, repo, branch, filename)
            
            # Determine local file path
            local_file = os.path.join(local_dir, os.path.basename(filename))
            
            # Download file using fsspec
            self.fs.get(xet_path, local_file)
            
            # Call progress callback if provided (100% after download completes)
            if progress_callback:
                file_size = os.path.getsize(local_file) if os.path.exists(local_file) else 0
                progress_callback(file_size, file_size)
            
            return local_file
        except Exception as e:
            raise RuntimeError(f"Failed to download {filename} from {user}/{repo}: {str(e)}") from e
    
    def download_repo(
        self,
        user: str,
        repo: str,
        local_dir: str,
        branch: str = 'main',
        path: str = '',
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> str:
        """
        Download an entire repository or subdirectory from XetHub.
        
        Args:
            user: Repository owner
            repo: Repository name
            local_dir: Local directory to save the repo
            branch: Branch name
            path: Optional subdirectory path to download
            progress_callback: Optional callback(bytes_downloaded, total_bytes)
        
        Returns:
            Path to the downloaded repository directory
        """
        try:
            # Create local directory if needed
            os.makedirs(local_dir, exist_ok=True)
            
            # Build xet path
            xet_path = self.build_xet_path(user, repo, branch, path)
            
            # Download entire directory recursively
            self.fs.get(xet_path, local_dir, recursive=True)
            
            # Call progress callback if provided (100% after download completes)
            if progress_callback:
                # Calculate total size of downloaded files
                total_size = sum(
                    os.path.getsize(os.path.join(dirpath, filename))
                    for dirpath, _, filenames in os.walk(local_dir)
                    for filename in filenames
                )
                progress_callback(total_size, total_size)
            
            return local_dir
        except Exception as e:
            raise RuntimeError(f"Failed to download repository {user}/{repo}: {str(e)}") from e
