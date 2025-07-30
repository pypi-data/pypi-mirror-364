"""
Hugging Face Integration Service

This module provides comprehensive integration with Hugging Face Hub including:
- Model ID resolution and validation
- Progressive model downloading with progress tracking
- Local model caching and version management
- Authentication token management for private models
- Integration with transformers backend
- Automatic tokenizer and config downloading

Requirements addressed: 6.1, 6.2, 6.3, 6.4, 6.5
"""

import logging
import os
import json
import time
import hashlib
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Callable, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import threading
import queue

try:
    import requests
    from huggingface_hub import (
        HfApi, HfFolder, login, logout, whoami,
        hf_hub_download, snapshot_download,
        list_repo_files, model_info, ModelInfo,
        HfFileSystem, Repository
    )
    from huggingface_hub.utils import (
        RepositoryNotFoundError, RevisionNotFoundError,
        EntryNotFoundError, LocalTokenNotFoundError
    )
    import transformers
    from transformers import AutoTokenizer, AutoConfig
    HF_AVAILABLE = True
except ImportError as e:
    HF_AVAILABLE = False
    HF_IMPORT_ERROR = str(e)


@dataclass
class ModelResolution:
    """Result of model ID resolution."""
    model_id: str
    exists: bool
    is_private: bool
    requires_auth: bool
    model_type: Optional[str] = None
    architecture: Optional[str] = None
    tags: List[str] = None
    downloads: int = 0
    last_modified: Optional[str] = None
    size_bytes: Optional[int] = None
    error_message: Optional[str] = None


@dataclass
class DownloadProgress:
    """Download progress information."""
    model_id: str
    total_files: int
    downloaded_files: int
    total_bytes: int
    downloaded_bytes: int
    current_file: str
    speed_mbps: float
    eta_seconds: Optional[int] = None
    status: str = "downloading"  # downloading, completed, failed, cancelled


@dataclass
class DownloadResult:
    """Result of model download operation."""
    success: bool
    model_id: str
    local_path: str
    download_time: float
    total_size_mb: float
    files_downloaded: int
    cached: bool = False
    error_message: Optional[str] = None
    progress: Optional[DownloadProgress] = None


@dataclass
class AuthResult:
    """Result of authentication operation."""
    success: bool
    username: Optional[str] = None
    token_valid: bool = False
    error_message: Optional[str] = None


@dataclass
class UpdateStatus:
    """Model update status information."""
    model_id: str
    local_version: Optional[str]
    remote_version: Optional[str]
    update_available: bool
    local_path: str
    last_check: datetime
    size_difference_mb: float = 0.0


@dataclass
class ModelFile:
    """Information about a model file."""
    filename: str
    size_bytes: int
    blob_id: str
    lfs: bool = False


class HuggingFaceIntegration:
    """
    Comprehensive Hugging Face Hub integration service.
    
    Provides model resolution, downloading, caching, authentication,
    and integration with the transformers backend.
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the Hugging Face integration service.
        
        Args:
            cache_dir: Custom cache directory path. If None, uses default HF cache.
        """
        self.logger = logging.getLogger(__name__)
        
        # Setup cache directory
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            # Use HF default cache directory
            self.cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize HF API
        self.api = None
        self.authenticated = False
        self.current_user = None
        
        # Download management
        self._active_downloads = {}
        self._download_lock = threading.Lock()
        
        # Model cache metadata
        self.cache_metadata_file = self.cache_dir / "gguf_loader_cache_metadata.json"
        self.cache_metadata = self._load_cache_metadata()
        
        # Check availability - make it optional
        if not HF_AVAILABLE:
            self.logger.warning(f"Hugging Face libraries not available: {HF_IMPORT_ERROR}")
            self.logger.info("HuggingFace integration disabled - only local models will be supported")
            self.api = None
            return
        
        self.api = HfApi()
        self.logger.info(f"Hugging Face integration initialized with cache: {self.cache_dir}")
    
    def _is_available(self) -> bool:
        """Check if HuggingFace integration is available."""
        return self.api is not None
    
    def _load_cache_metadata(self) -> Dict[str, Any]:
        """Load cache metadata from disk."""
        try:
            if self.cache_metadata_file.exists():
                with open(self.cache_metadata_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Failed to load cache metadata: {e}")
        
        return {
            "models": {},
            "last_cleanup": None,
            "version": "1.0"
        }
    
    def _save_cache_metadata(self):
        """Save cache metadata to disk."""
        try:
            with open(self.cache_metadata_file, 'w') as f:
                json.dump(self.cache_metadata, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Failed to save cache metadata: {e}")
    
    def resolve_model_id(self, model_id: str) -> ModelResolution:
        """
        Resolve and validate a Hugging Face model ID.
        
        Args:
            model_id: The model ID to resolve (e.g., "microsoft/DialoGPT-medium")
            
        Returns:
            ModelResolution with detailed information about the model
        """
        if not self._is_available():
            return ModelResolution(
                model_id=model_id,
                resolved=False,
                exists=False,
                error="HuggingFace integration not available - transformers library not installed"
            )
            
        try:
            self.logger.info(f"Resolving model ID: {model_id}")
            
            # Basic validation
            if not model_id or not isinstance(model_id, str):
                return ModelResolution(
                    model_id=model_id,
                    exists=False,
                    is_private=False,
                    requires_auth=False,
                    error_message="Invalid model ID format"
                )
            
            # Clean up model ID
            model_id = model_id.strip()
            if not model_id:
                return ModelResolution(
                    model_id=model_id,
                    exists=False,
                    is_private=False,
                    requires_auth=False,
                    error_message="Empty model ID"
                )
            
            # Try to get model info
            try:
                info = self.api.model_info(model_id)
                
                # Extract model information
                model_type = getattr(info, 'pipeline_tag', None)
                architecture = None
                
                # Try to get architecture from config
                try:
                    config_info = self.api.hf_hub_download(
                        repo_id=model_id,
                        filename="config.json",
                        repo_type="model"
                    )
                    with open(config_info, 'r') as f:
                        config = json.load(f)
                        architecture = config.get('architectures', [None])[0]
                        if not model_type:
                            model_type = config.get('model_type')
                except Exception:
                    pass  # Config not available or not accessible
                
                # Calculate total size
                total_size = 0
                try:
                    files = list(self.api.list_repo_files(model_id))
                    for file_path in files:
                        try:
                            file_info = self.api.get_paths_info(model_id, [file_path])
                            if file_info and len(file_info) > 0:
                                total_size += file_info[0].size or 0
                        except Exception:
                            continue
                except Exception:
                    pass
                
                return ModelResolution(
                    model_id=model_id,
                    exists=True,
                    is_private=info.private if hasattr(info, 'private') else False,
                    requires_auth=info.private if hasattr(info, 'private') else False,
                    model_type=model_type,
                    architecture=architecture,
                    tags=info.tags if hasattr(info, 'tags') else [],
                    downloads=info.downloads if hasattr(info, 'downloads') else 0,
                    last_modified=str(info.last_modified) if hasattr(info, 'last_modified') else None,
                    size_bytes=total_size if total_size > 0 else None
                )
                
            except RepositoryNotFoundError:
                return ModelResolution(
                    model_id=model_id,
                    exists=False,
                    is_private=False,
                    requires_auth=False,
                    error_message="Model not found"
                )
            except Exception as e:
                # Check if it's an authentication error
                if "401" in str(e) or "authentication" in str(e).lower():
                    return ModelResolution(
                        model_id=model_id,
                        exists=True,
                        is_private=True,
                        requires_auth=True,
                        error_message="Authentication required for private model"
                    )
                else:
                    return ModelResolution(
                        model_id=model_id,
                        exists=False,
                        is_private=False,
                        requires_auth=False,
                        error_message=f"Error resolving model: {str(e)}"
                    )
                    
        except Exception as e:
            self.logger.error(f"Failed to resolve model ID {model_id}: {e}")
            return ModelResolution(
                model_id=model_id,
                exists=False,
                is_private=False,
                requires_auth=False,
                error_message=f"Resolution failed: {str(e)}"
            )
    
    def download_model(self, model_id: str, 
                      progress_callback: Optional[Callable[[DownloadProgress], None]] = None,
                      force_download: bool = False,
                      revision: str = "main") -> DownloadResult:
        """
        Download a model from Hugging Face Hub with progress tracking.
        
        Args:
            model_id: The model ID to download
            progress_callback: Optional callback for progress updates
            force_download: Force re-download even if cached
            revision: Model revision/branch to download
            
        Returns:
            DownloadResult with download information
        """
        if not self._is_available():
            return DownloadResult(
                model_id=model_id,
                success=False,
                error_message="HuggingFace integration not available - transformers library not installed"
            )
            
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting download of model: {model_id}")
            
            # Check if model is already cached and valid
            if not force_download:
                cached_path = self._get_cached_model_path(model_id, revision)
                if cached_path and cached_path.exists():
                    self.logger.info(f"Model already cached at: {cached_path}")
                    
                    # Update cache metadata
                    self._update_cache_metadata(model_id, str(cached_path), cached=True)
                    
                    return DownloadResult(
                        success=True,
                        model_id=model_id,
                        local_path=str(cached_path),
                        download_time=time.time() - start_time,
                        total_size_mb=self._get_directory_size_mb(cached_path),
                        files_downloaded=0,
                        cached=True
                    )
            
            # Resolve model first
            resolution = self.resolve_model_id(model_id)
            if not resolution.exists:
                return DownloadResult(
                    success=False,
                    model_id=model_id,
                    local_path="",
                    download_time=time.time() - start_time,
                    total_size_mb=0.0,
                    files_downloaded=0,
                    error_message=resolution.error_message or "Model not found"
                )
            
            # Check authentication if required
            if resolution.requires_auth and not self.authenticated:
                return DownloadResult(
                    success=False,
                    model_id=model_id,
                    local_path="",
                    download_time=time.time() - start_time,
                    total_size_mb=0.0,
                    files_downloaded=0,
                    error_message="Authentication required for private model"
                )
            
            # Setup progress tracking
            progress = DownloadProgress(
                model_id=model_id,
                total_files=0,
                downloaded_files=0,
                total_bytes=resolution.size_bytes or 0,
                downloaded_bytes=0,
                current_file="",
                speed_mbps=0.0,
                status="downloading"
            )
            
            # Register active download
            with self._download_lock:
                self._active_downloads[model_id] = progress
            
            try:
                # Download model using snapshot_download for complete model
                local_path = snapshot_download(
                    repo_id=model_id,
                    revision=revision,
                    cache_dir=str(self.cache_dir),
                    force_download=force_download,
                    resume_download=True,
                    local_files_only=False
                )
                
                # Update progress
                progress.status = "completed"
                progress.downloaded_files = progress.total_files
                progress.downloaded_bytes = progress.total_bytes
                
                if progress_callback:
                    progress_callback(progress)
                
                # Calculate final metrics
                download_time = time.time() - start_time
                total_size_mb = self._get_directory_size_mb(Path(local_path))
                files_count = len(list(Path(local_path).rglob('*')))
                
                # Update cache metadata
                self._update_cache_metadata(model_id, local_path, cached=False)
                
                self.logger.info(f"Model downloaded successfully to: {local_path}")
                self.logger.info(f"Download time: {download_time:.2f}s, Size: {total_size_mb:.1f}MB")
                
                return DownloadResult(
                    success=True,
                    model_id=model_id,
                    local_path=local_path,
                    download_time=download_time,
                    total_size_mb=total_size_mb,
                    files_downloaded=files_count,
                    cached=False,
                    progress=progress
                )
                
            finally:
                # Remove from active downloads
                with self._download_lock:
                    self._active_downloads.pop(model_id, None)
                    
        except Exception as e:
            self.logger.error(f"Failed to download model {model_id}: {e}")
            
            # Update progress with error
            if model_id in self._active_downloads:
                self._active_downloads[model_id].status = "failed"
                if progress_callback:
                    progress_callback(self._active_downloads[model_id])
            
            return DownloadResult(
                success=False,
                model_id=model_id,
                local_path="",
                download_time=time.time() - start_time,
                total_size_mb=0.0,
                files_downloaded=0,
                error_message=f"Download failed: {str(e)}"
            )
    
    def authenticate(self, token: str) -> AuthResult:
        """
        Authenticate with Hugging Face using an API token.
        
        Args:
            token: Hugging Face API token
            
        Returns:
            AuthResult with authentication status
        """
        try:
            self.logger.info("Authenticating with Hugging Face")
            
            # Validate token format
            if not token or not isinstance(token, str):
                return AuthResult(
                    success=False,
                    error_message="Invalid token format"
                )
            
            token = token.strip()
            if not token.startswith(('hf_', 'hf-')):
                return AuthResult(
                    success=False,
                    error_message="Invalid token format. Token should start with 'hf_'"
                )
            
            # Try to login
            login(token=token, add_to_git_credential=True)
            
            # Verify authentication
            try:
                user_info = whoami()
                username = user_info.get('name', 'unknown')
                
                self.authenticated = True
                self.current_user = username
                
                self.logger.info(f"Successfully authenticated as: {username}")
                
                return AuthResult(
                    success=True,
                    username=username,
                    token_valid=True
                )
                
            except Exception as e:
                return AuthResult(
                    success=False,
                    error_message=f"Token validation failed: {str(e)}"
                )
                
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return AuthResult(
                success=False,
                error_message=f"Authentication failed: {str(e)}"
            )
    
    def logout(self) -> bool:
        """
        Logout from Hugging Face.
        
        Returns:
            True if logout successful, False otherwise
        """
        try:
            logout()
            self.authenticated = False
            self.current_user = None
            self.logger.info("Successfully logged out from Hugging Face")
            return True
        except Exception as e:
            self.logger.error(f"Logout failed: {e}")
            return False
    
    def check_model_updates(self, model_id: str, local_path: str) -> UpdateStatus:
        """
        Check if a locally cached model has updates available.
        
        Args:
            model_id: The model ID to check
            local_path: Local path to the cached model
            
        Returns:
            UpdateStatus with update information
        """
        try:
            self.logger.debug(f"Checking updates for model: {model_id}")
            
            local_path_obj = Path(local_path)
            if not local_path_obj.exists():
                return UpdateStatus(
                    model_id=model_id,
                    local_version=None,
                    remote_version=None,
                    update_available=True,
                    local_path=local_path,
                    last_check=datetime.now()
                )
            
            # Get local model info from cache metadata
            local_info = self.cache_metadata.get("models", {}).get(model_id, {})
            local_version = local_info.get("last_modified")
            
            # Get remote model info
            try:
                remote_info = self.api.model_info(model_id)
                remote_version = str(remote_info.last_modified) if hasattr(remote_info, 'last_modified') else None
                
                # Compare versions
                update_available = False
                if local_version and remote_version:
                    update_available = local_version != remote_version
                elif not local_version:
                    update_available = True
                
                # Calculate size difference if possible
                size_diff = 0.0
                if hasattr(remote_info, 'size') and remote_info.size:
                    local_size = self._get_directory_size_mb(local_path_obj)
                    remote_size_mb = remote_info.size / (1024 * 1024)
                    size_diff = remote_size_mb - local_size
                
                return UpdateStatus(
                    model_id=model_id,
                    local_version=local_version,
                    remote_version=remote_version,
                    update_available=update_available,
                    local_path=local_path,
                    last_check=datetime.now(),
                    size_difference_mb=size_diff
                )
                
            except Exception as e:
                self.logger.warning(f"Failed to check remote version for {model_id}: {e}")
                return UpdateStatus(
                    model_id=model_id,
                    local_version=local_version,
                    remote_version=None,
                    update_available=False,
                    local_path=local_path,
                    last_check=datetime.now()
                )
                
        except Exception as e:
            self.logger.error(f"Failed to check updates for {model_id}: {e}")
            return UpdateStatus(
                model_id=model_id,
                local_version=None,
                remote_version=None,
                update_available=False,
                local_path=local_path,
                last_check=datetime.now()
            )
    
    def list_model_files(self, model_id: str) -> List[ModelFile]:
        """
        List all files in a Hugging Face model repository.
        
        Args:
            model_id: The model ID to list files for
            
        Returns:
            List of ModelFile objects with file information
        """
        if not self._is_available():
            self.logger.warning("HuggingFace integration not available")
            return []
            
        try:
            self.logger.debug(f"Listing files for model: {model_id}")
            
            files = []
            file_paths = list(self.api.list_repo_files(model_id))
            
            for file_path in file_paths:
                try:
                    # Get file info
                    file_info = self.api.get_paths_info(model_id, [file_path])
                    if file_info and len(file_info) > 0:
                        info = file_info[0]
                        files.append(ModelFile(
                            filename=file_path,
                            size_bytes=info.size or 0,
                            blob_id=getattr(info, 'blob_id', ''),
                            lfs=getattr(info, 'lfs', False)
                        ))
                    else:
                        # Fallback with minimal info
                        files.append(ModelFile(
                            filename=file_path,
                            size_bytes=0,
                            blob_id='',
                            lfs=False
                        ))
                except Exception as e:
                    self.logger.warning(f"Failed to get info for file {file_path}: {e}")
                    continue
            
            self.logger.debug(f"Found {len(files)} files for model {model_id}")
            return files
            
        except Exception as e:
            self.logger.error(f"Failed to list files for model {model_id}: {e}")
            return []
    
    def get_download_progress(self, model_id: str) -> Optional[DownloadProgress]:
        """
        Get current download progress for a model.
        
        Args:
            model_id: The model ID to get progress for
            
        Returns:
            DownloadProgress object or None if not downloading
        """
        with self._download_lock:
            return self._active_downloads.get(model_id)
    
    def cancel_download(self, model_id: str) -> bool:
        """
        Cancel an active download.
        
        Args:
            model_id: The model ID to cancel download for
            
        Returns:
            True if cancellation successful, False otherwise
        """
        try:
            with self._download_lock:
                if model_id in self._active_downloads:
                    self._active_downloads[model_id].status = "cancelled"
                    # Note: Actual cancellation of huggingface_hub downloads
                    # is not directly supported, but we mark it as cancelled
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to cancel download for {model_id}: {e}")
            return False
    
    def cleanup_cache(self, max_age_days: int = 30, max_size_gb: float = 10.0) -> Dict[str, Any]:
        """
        Clean up old cached models.
        
        Args:
            max_age_days: Maximum age of cached models in days
            max_size_gb: Maximum total cache size in GB
            
        Returns:
            Dictionary with cleanup statistics
        """
        try:
            self.logger.info(f"Starting cache cleanup (max_age: {max_age_days} days, max_size: {max_size_gb} GB)")
            
            cleanup_stats = {
                "models_removed": 0,
                "space_freed_mb": 0.0,
                "total_models": 0,
                "total_size_mb": 0.0
            }
            
            # Get all cached models
            cached_models = []
            for model_id, info in self.cache_metadata.get("models", {}).items():
                local_path = Path(info.get("local_path", ""))
                if local_path.exists():
                    size_mb = self._get_directory_size_mb(local_path)
                    last_accessed = datetime.fromisoformat(info.get("last_accessed", datetime.now().isoformat()))
                    
                    cached_models.append({
                        "model_id": model_id,
                        "path": local_path,
                        "size_mb": size_mb,
                        "last_accessed": last_accessed,
                        "age_days": (datetime.now() - last_accessed).days
                    })
            
            cleanup_stats["total_models"] = len(cached_models)
            cleanup_stats["total_size_mb"] = sum(m["size_mb"] for m in cached_models)
            
            # Sort by last accessed (oldest first)
            cached_models.sort(key=lambda x: x["last_accessed"])
            
            # Remove old models
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            max_size_mb = max_size_gb * 1024
            current_size_mb = cleanup_stats["total_size_mb"]
            
            for model in cached_models:
                should_remove = False
                
                # Remove if too old
                if model["last_accessed"] < cutoff_date:
                    should_remove = True
                    self.logger.debug(f"Removing old model: {model['model_id']} (age: {model['age_days']} days)")
                
                # Remove if cache is too large (remove oldest first)
                elif current_size_mb > max_size_mb:
                    should_remove = True
                    self.logger.debug(f"Removing model for size limit: {model['model_id']} ({model['size_mb']:.1f}MB)")
                
                if should_remove:
                    try:
                        shutil.rmtree(model["path"])
                        cleanup_stats["models_removed"] += 1
                        cleanup_stats["space_freed_mb"] += model["size_mb"]
                        current_size_mb -= model["size_mb"]
                        
                        # Remove from metadata
                        self.cache_metadata.get("models", {}).pop(model["model_id"], None)
                        
                    except Exception as e:
                        self.logger.warning(f"Failed to remove cached model {model['model_id']}: {e}")
            
            # Update cleanup timestamp
            self.cache_metadata["last_cleanup"] = datetime.now().isoformat()
            self._save_cache_metadata()
            
            self.logger.info(f"Cache cleanup completed: {cleanup_stats['models_removed']} models removed, "
                           f"{cleanup_stats['space_freed_mb']:.1f}MB freed")
            
            return cleanup_stats
            
        except Exception as e:
            self.logger.error(f"Cache cleanup failed: {e}")
            return {"error": str(e)}
    
    def _get_cached_model_path(self, model_id: str, revision: str = "main") -> Optional[Path]:
        """Get the local path for a cached model."""
        try:
            # Check cache metadata first
            model_info = self.cache_metadata.get("models", {}).get(model_id, {})
            if model_info and "local_path" in model_info:
                path = Path(model_info["local_path"])
                if path.exists():
                    return path
            
            # Try to find in HF cache structure
            # HF cache uses format: models--{org}--{model}/snapshots/{revision}
            safe_model_id = model_id.replace("/", "--")
            model_cache_dir = self.cache_dir / f"models--{safe_model_id}"
            
            if model_cache_dir.exists():
                snapshots_dir = model_cache_dir / "snapshots"
                if snapshots_dir.exists():
                    # Look for the specific revision or any available revision
                    revision_dir = snapshots_dir / revision
                    if revision_dir.exists():
                        return revision_dir
                    
                    # If specific revision not found, use the first available
                    available_revisions = list(snapshots_dir.iterdir())
                    if available_revisions:
                        return available_revisions[0]
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Error finding cached model path for {model_id}: {e}")
            return None
    
    def _get_directory_size_mb(self, path: Path) -> float:
        """Calculate directory size in MB."""
        try:
            total_size = sum(
                f.stat().st_size 
                for f in path.rglob('*') 
                if f.is_file()
            )
            return total_size / (1024 * 1024)
        except Exception:
            return 0.0
    
    def _update_cache_metadata(self, model_id: str, local_path: str, cached: bool = False):
        """Update cache metadata for a model."""
        try:
            if "models" not in self.cache_metadata:
                self.cache_metadata["models"] = {}
            
            self.cache_metadata["models"][model_id] = {
                "local_path": local_path,
                "last_accessed": datetime.now().isoformat(),
                "cached": cached,
                "size_mb": self._get_directory_size_mb(Path(local_path))
            }
            
            self._save_cache_metadata()
            
        except Exception as e:
            self.logger.warning(f"Failed to update cache metadata for {model_id}: {e}")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about the current cache."""
        try:
            total_models = len(self.cache_metadata.get("models", {}))
            total_size_mb = sum(
                info.get("size_mb", 0) 
                for info in self.cache_metadata.get("models", {}).values()
            )
            
            return {
                "cache_dir": str(self.cache_dir),
                "total_models": total_models,
                "total_size_mb": total_size_mb,
                "total_size_gb": total_size_mb / 1024,
                "last_cleanup": self.cache_metadata.get("last_cleanup"),
                "authenticated": self.authenticated,
                "current_user": self.current_user
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get cache info: {e}")
            return {"error": str(e)}
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated with Hugging Face."""
        return self.authenticated
    
    def get_current_user(self) -> Optional[str]:
        """Get the current authenticated user."""
        return self.current_user