"""
Downloader module for HuggingFace platform.

This application uses the HuggingFace Hub API with hf_xet optimization
for faster downloads through chunk-based deduplication.
"""

from .huggingface_downloader import HuggingFaceDownloader

__all__ = ['HuggingFaceDownloader']

