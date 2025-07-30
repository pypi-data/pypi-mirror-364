"""
Model Metadata Extractor

This module contains the ModelMetadataExtractor class, which is responsible for
parsing GGUF file structure, extracting model parameters and configuration,
and implementing metadata caching for performance.
"""

import os
import json
import logging
import struct
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union, BinaryIO
from datetime import datetime, timedelta

class GGUFParseError(Exception):
    """Exception raised for errors during GGUF parsing."""
    pass

class ModelMetadataExtractor:
    """
    Extracts metadata from GGUF model files.
    
    This class is responsible for:
    - Parsing GGUF file structure
    - Extracting model parameters and configuration
    - Implementing metadata caching for performance
    """
    
    # GGUF file header magic bytes
    GGUF_MAGIC = b"GGUF"
    
    # GGUF version supported
    GGUF_VERSION = 2
    
    # GGUF value types
    GGUF_TYPE_UINT8 = 0
    GGUF_TYPE_INT8 = 1
    GGUF_TYPE_UINT16 = 2
    GGUF_TYPE_INT16 = 3
    GGUF_TYPE_UINT32 = 4
    GGUF_TYPE_INT32 = 5
    GGUF_TYPE_FLOAT32 = 6
    GGUF_TYPE_BOOL = 7
    GGUF_TYPE_STRING = 8
    GGUF_TYPE_ARRAY = 9
    GGUF_TYPE_UINT64 = 10
    GGUF_TYPE_INT64 = 11
    GGUF_TYPE_FLOAT64 = 12
    
    # Cache settings - use user config directory
    from llmtoolkit.resource_manager import get_user_config_dir
    CACHE_DIR = get_user_config_dir() / "cache"
    CACHE_EXPIRY = timedelta(days=7)  # Cache entries expire after 7 days
    
    def __init__(self):
        """Initialize the metadata extractor."""
        self.logger = logging.getLogger("gguf_loader.metadata_extractor")
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.CACHE_DIR, exist_ok=True)
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from a GGUF file.
        
        Args:
            file_path: Path to the GGUF file
            
        Returns:
            Dictionary containing model metadata
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            GGUFParseError: If the file is not a valid GGUF file
            IOError: If there's an error reading the file
        """
        self.logger.info(f"Extracting metadata from {file_path}")
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check if metadata is cached
        cached_metadata = self._get_cached_metadata(file_path)
        if cached_metadata:
            self.logger.info(f"Using cached metadata for {file_path}")
            return cached_metadata
        
        # Extract metadata from file
        try:
            with open(file_path, 'rb') as f:
                metadata = self._parse_gguf_file(f)
                
                # Add file information
                file_stat = os.stat(file_path)
                metadata["file_info"] = {
                    "size": file_stat.st_size,
                    "created": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    "path": file_path,
                    "name": os.path.basename(file_path)
                }
                
                # Cache the metadata
                self._cache_metadata(file_path, metadata)
                
                return metadata
                
        except (IOError, struct.error) as e:
            self.logger.error(f"Error reading GGUF file: {e}")
            raise GGUFParseError(f"Error reading GGUF file: {e}")
    
    def _parse_gguf_file(self, file: BinaryIO) -> Dict[str, Any]:
        """
        Parse a GGUF file and extract metadata.
        
        Args:
            file: Open file object in binary mode
            
        Returns:
            Dictionary containing model metadata
            
        Raises:
            GGUFParseError: If the file is not a valid GGUF file
        """
        # Read magic bytes
        magic = file.read(4)
        if magic != self.GGUF_MAGIC:
            raise GGUFParseError(f"Invalid GGUF file: magic bytes mismatch")
        
        # Read version
        version = struct.unpack("<I", file.read(4))[0]
        if version != self.GGUF_VERSION:
            self.logger.warning(f"Unsupported GGUF version: {version}, expected {self.GGUF_VERSION}")
        
        # Read tensor count
        tensor_count = struct.unpack("<Q", file.read(8))[0]
        
        # Read metadata key-value count
        kv_count = struct.unpack("<Q", file.read(8))[0]
        
        # Initialize metadata dictionary
        metadata = {
            "version": version,
            "tensor_count": tensor_count,
            "parameters": {},
            "metadata": {}
        }
        
        # Read metadata key-value pairs
        for _ in range(kv_count):
            # Read key
            key_length = struct.unpack("<Q", file.read(8))[0]
            key = file.read(key_length).decode('utf-8')
            
            # Read value type
            value_type = struct.unpack("<I", file.read(4))[0]
            
            # Read value based on type
            value = self._read_value(file, value_type)
            
            # Store in appropriate category
            if key.startswith("general."):
                # General parameters
                param_key = key[8:]  # Remove "general." prefix
                metadata["parameters"][param_key] = value
            else:
                # Other metadata
                metadata["metadata"][key] = value
        
        # Extract architecture information
        architecture = metadata["parameters"].get("architecture", "Unknown")
        
        # Add common parameters based on architecture
        if architecture == "llama":
            # Add common LLaMA parameters if not already present
            if "context_length" not in metadata["parameters"]:
                metadata["parameters"]["context_length"] = 2048
            if "embedding_dim" not in metadata["parameters"]:
                metadata["parameters"]["embedding_dim"] = 4096
            if "num_layers" not in metadata["parameters"]:
                metadata["parameters"]["num_layers"] = 32
            if "num_heads" not in metadata["parameters"]:
                metadata["parameters"]["num_heads"] = 32
        
        return metadata
    
    def _read_value(self, file: BinaryIO, value_type: int) -> Any:
        """
        Read a value of the specified type from the file.
        
        Args:
            file: Open file object in binary mode
            value_type: Type of the value to read
            
        Returns:
            The value read from the file
            
        Raises:
            GGUFParseError: If the value type is unknown
        """
        if value_type == self.GGUF_TYPE_UINT8:
            return struct.unpack("<B", file.read(1))[0]
        elif value_type == self.GGUF_TYPE_INT8:
            return struct.unpack("<b", file.read(1))[0]
        elif value_type == self.GGUF_TYPE_UINT16:
            return struct.unpack("<H", file.read(2))[0]
        elif value_type == self.GGUF_TYPE_INT16:
            return struct.unpack("<h", file.read(2))[0]
        elif value_type == self.GGUF_TYPE_UINT32:
            return struct.unpack("<I", file.read(4))[0]
        elif value_type == self.GGUF_TYPE_INT32:
            return struct.unpack("<i", file.read(4))[0]
        elif value_type == self.GGUF_TYPE_FLOAT32:
            return struct.unpack("<f", file.read(4))[0]
        elif value_type == self.GGUF_TYPE_BOOL:
            return bool(struct.unpack("<B", file.read(1))[0])
        elif value_type == self.GGUF_TYPE_STRING:
            length = struct.unpack("<Q", file.read(8))[0]
            return file.read(length).decode('utf-8')
        elif value_type == self.GGUF_TYPE_ARRAY:
            # Read array type and count
            array_type = struct.unpack("<I", file.read(4))[0]
            array_count = struct.unpack("<Q", file.read(8))[0]
            
            # Read array elements
            array = []
            for _ in range(array_count):
                array.append(self._read_value(file, array_type))
            
            return array
        elif value_type == self.GGUF_TYPE_UINT64:
            return struct.unpack("<Q", file.read(8))[0]
        elif value_type == self.GGUF_TYPE_INT64:
            return struct.unpack("<q", file.read(8))[0]
        elif value_type == self.GGUF_TYPE_FLOAT64:
            return struct.unpack("<d", file.read(8))[0]
        else:
            raise GGUFParseError(f"Unknown value type: {value_type}")
    
    def _get_cache_path(self, file_path: str) -> Path:
        """
        Get the cache file path for a model file.
        
        Args:
            file_path: Path to the model file
            
        Returns:
            Path to the cache file
        """
        # Create a hash of the file path to use as the cache file name
        file_hash = hashlib.md5(file_path.encode()).hexdigest()
        return self.CACHE_DIR / f"{file_hash}.json"
    
    def _get_cached_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get cached metadata for a model file.
        
        Args:
            file_path: Path to the model file
            
        Returns:
            Cached metadata, or None if not cached or cache is invalid
        """
        cache_path = self._get_cache_path(file_path)
        
        # Check if cache file exists
        if not cache_path.exists():
            return None
        
        try:
            # Check if cache is expired
            cache_stat = os.stat(cache_path)
            cache_time = datetime.fromtimestamp(cache_stat.st_mtime)
            if datetime.now() - cache_time > self.CACHE_EXPIRY:
                self.logger.info(f"Cache expired for {file_path}")
                return None
            
            # Check if model file has been modified since cache was created
            file_stat = os.stat(file_path)
            file_time = datetime.fromtimestamp(file_stat.st_mtime)
            if file_time > cache_time:
                self.logger.info(f"Model file modified since cache was created: {file_path}")
                return None
            
            # Load cached metadata
            with open(cache_path, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            self.logger.warning(f"Error reading cache file: {e}")
            return None
    
    def _cache_metadata(self, file_path: str, metadata: Dict[str, Any]) -> None:
        """
        Cache metadata for a model file.
        
        Args:
            file_path: Path to the model file
            metadata: Metadata to cache
        """
        cache_path = self._get_cache_path(file_path)
        
        try:
            # Save metadata to cache file
            with open(cache_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
            self.logger.info(f"Cached metadata for {file_path}")
                
        except Exception as e:
            self.logger.warning(f"Error writing cache file: {e}")
    
    def clear_cache(self) -> int:
        """
        Clear the metadata cache.
        
        Returns:
            Number of cache files deleted
        """
        count = 0
        for cache_file in self.CACHE_DIR.glob("*.json"):
            try:
                os.unlink(cache_file)
                count += 1
            except Exception as e:
                self.logger.warning(f"Error deleting cache file {cache_file}: {e}")
        
        self.logger.info(f"Cleared {count} cache files")
        return count
    
    def clear_expired_cache(self) -> int:
        """
        Clear expired cache entries.
        
        Returns:
            Number of cache files deleted
        """
        count = 0
        now = datetime.now()
        
        for cache_file in self.CACHE_DIR.glob("*.json"):
            try:
                # Check if cache is expired
                cache_stat = os.stat(cache_file)
                cache_time = datetime.fromtimestamp(cache_stat.st_mtime)
                if now - cache_time > self.CACHE_EXPIRY:
                    os.unlink(cache_file)
                    count += 1
            except Exception as e:
                self.logger.warning(f"Error processing cache file {cache_file}: {e}")
        
        self.logger.info(f"Cleared {count} expired cache files")
        return count