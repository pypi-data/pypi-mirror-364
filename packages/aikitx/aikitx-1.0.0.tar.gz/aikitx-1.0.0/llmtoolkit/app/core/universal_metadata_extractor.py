"""
Universal Metadata Extraction Engine

This module contains the UniversalMetadataExtractor class, which provides
comprehensive metadata extraction for all supported model formats:
- GGUF files with improved version support
- Safetensors files with tensor information extraction
- PyTorch model directories with config.json parsing
- Hugging Face models with model card and config extraction
- Unified metadata representation across all formats
- Graceful degradation and parameter estimation for incomplete metadata
"""

import os
import json
import struct
import logging
import hashlib
import time
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union, BinaryIO
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

# Import format detector for format types
from .universal_format_detector import ModelFormat

class MetadataExtractionError(Exception):
    """Exception raised for errors during metadata extraction."""
    pass

@dataclass
class UnifiedMetadata:
    """Unified metadata representation across all model formats."""
    format_type: ModelFormat
    model_name: str
    architecture: Optional[str] = None
    parameters: Optional[int] = None
    quantization: Optional[str] = None
    context_length: Optional[int] = None
    vocab_size: Optional[int] = None
    file_size: int = 0
    tensor_info: Dict[str, Any] = None
    config: Dict[str, Any] = None
    tokenizer_info: Optional[Dict[str, Any]] = None
    model_type: Optional[str] = None
    library_name: Optional[str] = None
    tags: List[str] = None
    license: Optional[str] = None
    created_at: Optional[str] = None
    modified_at: Optional[str] = None
    downloads: Optional[int] = None
    confidence: float = 1.0
    warnings: List[str] = None
    errors: List[str] = None
    
    def __post_init__(self):
        """Initialize default values for mutable fields."""
        if self.tensor_info is None:
            self.tensor_info = {}
        if self.config is None:
            self.config = {}
        if self.tokenizer_info is None:
            self.tokenizer_info = {}
        if self.tags is None:
            self.tags = []
        if self.warnings is None:
            self.warnings = []
        if self.errors is None:
            self.errors = []

class UniversalMetadataExtractor:
    """
    Universal metadata extractor for all supported model formats.
    
    This class provides comprehensive metadata extraction with:
    - Format-specific parsing for GGUF, safetensors, PyTorch, and HF models
    - Unified metadata representation
    - Graceful degradation for incomplete metadata
    - Parameter estimation for unknown values
    - Caching for performance optimization
    """
    
    # GGUF constants
    GGUF_MAGIC = b"GGUF"
    GGUF_SUPPORTED_VERSIONS = [1, 2, 3]
    
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
    CACHE_DIR = get_user_config_dir() / "metadata_cache"
    CACHE_EXPIRY = timedelta(days=7)
    
    def __init__(self):
        """Initialize the universal metadata extractor."""
        self.logger = logging.getLogger("gguf_loader.universal_metadata_extractor")
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.CACHE_DIR, exist_ok=True)
    
    def extract_metadata(self, model_path: str, format_type: ModelFormat) -> UnifiedMetadata:
        """
        Extract metadata from a model file or directory.
        
        Args:
            model_path: Path to model file/directory or HF model ID
            format_type: Detected format type
            
        Returns:
            UnifiedMetadata object with extracted information
            
        Raises:
            MetadataExtractionError: If extraction fails critically
        """
        self.logger.info(f"Extracting metadata for {model_path} (format: {format_type.value})")
        
        try:
            # Check cache first
            cached_metadata = self._get_cached_metadata(model_path, format_type)
            if cached_metadata:
                self.logger.info(f"Using cached metadata for {model_path}")
                return cached_metadata
            
            # Extract based on format
            if format_type == ModelFormat.GGUF:
                metadata = self._extract_gguf_metadata(model_path)
            elif format_type == ModelFormat.SAFETENSORS:
                metadata = self._extract_safetensors_metadata(model_path)
            elif format_type == ModelFormat.PYTORCH_BIN:
                metadata = self._extract_pytorch_metadata(model_path)
            elif format_type == ModelFormat.HUGGINGFACE:
                metadata = self._extract_huggingface_metadata(model_path)
            else:
                metadata = self._create_fallback_metadata(model_path, format_type)
            
            # Apply parameter estimation if needed
            metadata = self._estimate_missing_parameters(metadata)
            
            # Cache the metadata
            self._cache_metadata(model_path, format_type, metadata)
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting metadata from {model_path}: {e}")
            # Return fallback metadata instead of failing completely
            return self._create_fallback_metadata(model_path, format_type, str(e))
    
    def _extract_gguf_metadata(self, file_path: str) -> UnifiedMetadata:
        """Extract metadata from GGUF file with improved version support."""
        try:
            if not os.path.exists(file_path):
                raise MetadataExtractionError(f"File not found: {file_path}")
            
            file_size = os.path.getsize(file_path)
            file_stat = os.stat(file_path)
            
            with open(file_path, 'rb') as f:
                # Read and validate header
                magic = f.read(4)
                if magic != self.GGUF_MAGIC:
                    raise MetadataExtractionError(f"Invalid GGUF magic bytes: {magic}")
                
                version = struct.unpack("<I", f.read(4))[0]
                if version not in self.GGUF_SUPPORTED_VERSIONS:
                    self.logger.warning(f"Unsupported GGUF version: {version}")
                
                tensor_count = struct.unpack("<Q", f.read(8))[0]
                kv_count = struct.unpack("<Q", f.read(8))[0]
                
                # Extract metadata key-value pairs
                raw_metadata = {}
                warnings = []
                errors = []
                
                try:
                    for _ in range(kv_count):
                        key_length = struct.unpack("<Q", f.read(8))[0]
                        key = f.read(key_length).decode('utf-8')
                        value_type = struct.unpack("<I", f.read(4))[0]
                        value = self._read_gguf_value(f, value_type)
                        raw_metadata[key] = value
                except Exception as e:
                    warnings.append(f"Error reading some metadata entries: {e}")
                
                # Parse metadata into unified format
                metadata = self._parse_gguf_metadata(raw_metadata, file_path, file_size, tensor_count)
                metadata.warnings.extend(warnings)
                metadata.errors.extend(errors)
                
                # Add file timestamps
                metadata.created_at = datetime.fromtimestamp(file_stat.st_ctime).isoformat()
                metadata.modified_at = datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                
                return metadata
                
        except Exception as e:
            self.logger.error(f"Error extracting GGUF metadata: {e}")
            return self._create_fallback_metadata(file_path, ModelFormat.GGUF, str(e))
    
    def _extract_safetensors_metadata(self, file_path: str) -> UnifiedMetadata:
        """Extract metadata from safetensors file with tensor information."""
        try:
            if not os.path.exists(file_path):
                raise MetadataExtractionError(f"File not found: {file_path}")
            
            file_size = os.path.getsize(file_path)
            file_stat = os.stat(file_path)
            
            with open(file_path, 'rb') as f:
                # Read header length
                header_length_bytes = f.read(8)
                if len(header_length_bytes) != 8:
                    raise MetadataExtractionError("Incomplete safetensors header")
                
                header_length = struct.unpack("<Q", header_length_bytes)[0]
                if header_length <= 0 or header_length > file_size:
                    raise MetadataExtractionError(f"Invalid header length: {header_length}")
                
                # Read and parse header JSON
                header_bytes = f.read(header_length)
                if len(header_bytes) != header_length:
                    raise MetadataExtractionError("Incomplete safetensors header data")
                
                try:
                    header_json = json.loads(header_bytes.decode('utf-8'))
                except json.JSONDecodeError as e:
                    raise MetadataExtractionError(f"Invalid JSON in safetensors header: {e}")
                
                # Parse metadata
                metadata = self._parse_safetensors_metadata(header_json, file_path, file_size)
                
                # Add file timestamps
                metadata.created_at = datetime.fromtimestamp(file_stat.st_ctime).isoformat()
                metadata.modified_at = datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                
                return metadata
                
        except Exception as e:
            self.logger.error(f"Error extracting safetensors metadata: {e}")
            return self._create_fallback_metadata(file_path, ModelFormat.SAFETENSORS, str(e))
    
    def _extract_pytorch_metadata(self, model_path: str) -> UnifiedMetadata:
        """Extract metadata from PyTorch model directory with config.json parsing."""
        try:
            if not os.path.exists(model_path):
                raise MetadataExtractionError(f"Path not found: {model_path}")
            
            if os.path.isfile(model_path):
                # Single PyTorch file
                return self._extract_pytorch_file_metadata(model_path)
            elif os.path.isdir(model_path):
                # PyTorch model directory
                return self._extract_pytorch_directory_metadata(model_path)
            else:
                raise MetadataExtractionError(f"Invalid path type: {model_path}")
                
        except Exception as e:
            self.logger.error(f"Error extracting PyTorch metadata: {e}")
            return self._create_fallback_metadata(model_path, ModelFormat.PYTORCH_BIN, str(e))
    
    def _extract_huggingface_metadata(self, model_id: str) -> UnifiedMetadata:
        """Extract metadata from Hugging Face model with model card and config."""
        try:
            # Use HuggingFace integration service if available
            try:
                from llmtoolkit.app.services.huggingface_integration import HuggingFaceIntegration
                
                hf_integration = HuggingFaceIntegration()
                resolution = hf_integration.resolve_model_id(model_id)
                
                if not resolution.exists:
                    raise MetadataExtractionError(f"Hugging Face model not found: {model_id}")
                
                # Parse HF metadata
                metadata = self._parse_huggingface_metadata(resolution, model_id)
                return metadata
                
            except ImportError:
                # Fallback to direct API calls
                return self._extract_huggingface_metadata_fallback(model_id)
                
        except Exception as e:
            self.logger.error(f"Error extracting Hugging Face metadata: {e}")
            return self._create_fallback_metadata(model_id, ModelFormat.HUGGINGFACE, str(e))
    
    def _read_gguf_value(self, file: BinaryIO, value_type: int) -> Any:
        """Read a value of the specified type from GGUF file."""
        try:
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
                array_type = struct.unpack("<I", file.read(4))[0]
                array_count = struct.unpack("<Q", file.read(8))[0]
                return [self._read_gguf_value(file, array_type) for _ in range(array_count)]
            elif value_type == self.GGUF_TYPE_UINT64:
                return struct.unpack("<Q", file.read(8))[0]
            elif value_type == self.GGUF_TYPE_INT64:
                return struct.unpack("<q", file.read(8))[0]
            elif value_type == self.GGUF_TYPE_FLOAT64:
                return struct.unpack("<d", file.read(8))[0]
            else:
                self.logger.warning(f"Unknown GGUF value type: {value_type}")
                return None
        except Exception as e:
            self.logger.warning(f"Error reading GGUF value type {value_type}: {e}")
            return None
    
    def _parse_gguf_metadata(self, raw_metadata: Dict[str, Any], file_path: str, 
                           file_size: int, tensor_count: int) -> UnifiedMetadata:
        """Parse raw GGUF metadata into unified format."""
        warnings = []
        
        # Extract basic information
        model_name = os.path.basename(file_path)
        architecture = raw_metadata.get("general.architecture", "unknown")
        
        # Extract parameters with fallbacks
        parameters = None
        if "general.parameter_count" in raw_metadata:
            parameters = raw_metadata["general.parameter_count"]
        elif f"{architecture}.block_count" in raw_metadata and f"{architecture}.embed_dim" in raw_metadata:
            # Estimate parameters for transformer models
            block_count = raw_metadata.get(f"{architecture}.block_count", 0)
            embed_dim = raw_metadata.get(f"{architecture}.embed_dim", 0)
            if block_count and embed_dim:
                # Rough estimation: params ≈ 12 * layers * embed_dim^2 / 1e6 (for transformer models)
                parameters = int(12 * block_count * embed_dim * embed_dim / 1e6) * 1e6
                warnings.append("Parameter count estimated from architecture")
        
        # Extract quantization info
        quantization = None
        if "general.quantization_version" in raw_metadata:
            quantization = f"GGUF v{raw_metadata['general.quantization_version']}"
        elif "general.file_type" in raw_metadata:
            file_type = raw_metadata["general.file_type"]
            quantization = self._map_gguf_file_type_to_quantization(file_type)
        
        # Extract context length
        context_length = raw_metadata.get(f"{architecture}.context_length", 
                                        raw_metadata.get("general.context_length"))
        
        # Extract vocabulary size
        vocab_size = raw_metadata.get(f"{architecture}.vocab_size",
                                    raw_metadata.get("tokenizer.ggml.tokens", []))
        if isinstance(vocab_size, list):
            vocab_size = len(vocab_size)
        
        # Build tensor info
        tensor_info = {
            "tensor_count": tensor_count,
            "total_size": file_size,
            "architecture_specific": {}
        }
        
        # Add architecture-specific tensor info
        for key, value in raw_metadata.items():
            if key.startswith(f"{architecture}.") and "tensor" in key.lower():
                tensor_info["architecture_specific"][key] = value
        
        # Build config from raw metadata
        config = {}
        for key, value in raw_metadata.items():
            if key.startswith("general."):
                config[key[8:]] = value  # Remove "general." prefix
            elif key.startswith(f"{architecture}."):
                config[key] = value
            elif key.startswith("tokenizer."):
                if "tokenizer" not in config:
                    config["tokenizer"] = {}
                config["tokenizer"][key[10:]] = value  # Remove "tokenizer." prefix
        
        return UnifiedMetadata(
            format_type=ModelFormat.GGUF,
            model_name=model_name,
            architecture=architecture,
            parameters=parameters,
            quantization=quantization,
            context_length=context_length,
            vocab_size=vocab_size,
            file_size=file_size,
            tensor_info=tensor_info,
            config=config,
            model_type="text-generation",  # Most GGUF models are text generation
            library_name="gguf",
            warnings=warnings
        )
    
    def _parse_safetensors_metadata(self, header_json: Dict[str, Any], file_path: str, 
                                  file_size: int) -> UnifiedMetadata:
        """Parse safetensors header into unified format."""
        warnings = []
        
        model_name = os.path.basename(file_path)
        
        # Extract tensor information
        tensor_info = {"tensors": {}, "total_tensors": 0, "total_tensor_size": 0}
        total_tensor_size = 0
        tensor_count = 0
        
        for key, value in header_json.items():
            if key != "__metadata__":
                tensor_count += 1
                if isinstance(value, dict):
                    tensor_info["tensors"][key] = value
                    if "data_offsets" in value and len(value["data_offsets"]) == 2:
                        tensor_size = value["data_offsets"][1] - value["data_offsets"][0]
                        total_tensor_size += tensor_size
        
        tensor_info["total_tensors"] = tensor_count
        tensor_info["total_tensor_size"] = total_tensor_size
        tensor_info["file_size"] = file_size
        
        # Extract model metadata if present
        model_metadata = header_json.get("__metadata__", {})
        
        # Try to determine architecture from tensor names
        architecture = self._infer_architecture_from_tensors(list(header_json.keys()))
        
        # Estimate parameters from tensor sizes
        parameters = self._estimate_parameters_from_tensors(header_json)
        if parameters:
            warnings.append("Parameter count estimated from tensor sizes")
        
        # Build config from metadata
        config = dict(model_metadata) if model_metadata else {}
        config["tensor_count"] = tensor_count
        config["total_tensor_size"] = total_tensor_size
        
        return UnifiedMetadata(
            format_type=ModelFormat.SAFETENSORS,
            model_name=model_name,
            architecture=architecture,
            parameters=parameters,
            file_size=file_size,
            tensor_info=tensor_info,
            config=config,
            model_type="text-generation",  # Most safetensors models are text generation
            library_name="safetensors",
            warnings=warnings
        )
    
    def _extract_pytorch_file_metadata(self, file_path: str) -> UnifiedMetadata:
        """Extract metadata from single PyTorch file."""
        file_size = os.path.getsize(file_path)
        file_stat = os.stat(file_path)
        model_name = os.path.basename(file_path)
        
        warnings = []
        errors = []
        
        # Try to load with PyTorch if available
        tensor_info = {"file_size": file_size}
        parameters = None
        
        try:
            import torch
            
            # Load state dict to analyze
            try:
                state_dict = torch.load(file_path, map_location='cpu')
                if isinstance(state_dict, dict):
                    tensor_count = len(state_dict)
                    total_params = sum(p.numel() for p in state_dict.values() if hasattr(p, 'numel'))
                    
                    tensor_info.update({
                        "tensor_count": tensor_count,
                        "total_parameters": total_params,
                        "tensor_names": list(state_dict.keys())[:10]  # First 10 tensor names
                    })
                    
                    parameters = total_params
                    
                    # Try to infer architecture
                    architecture = self._infer_architecture_from_tensors(list(state_dict.keys()))
                else:
                    warnings.append("PyTorch file does not contain a state dictionary")
                    
            except Exception as e:
                errors.append(f"Error loading PyTorch file: {e}")
                
        except ImportError:
            warnings.append("PyTorch not available for detailed analysis")
        
        return UnifiedMetadata(
            format_type=ModelFormat.PYTORCH_BIN,
            model_name=model_name,
            parameters=parameters,
            file_size=file_size,
            tensor_info=tensor_info,
            config={"single_file": True},
            model_type="text-generation",
            library_name="pytorch",
            created_at=datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
            modified_at=datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
            warnings=warnings,
            errors=errors
        )
    
    def _extract_pytorch_directory_metadata(self, dir_path: str) -> UnifiedMetadata:
        """Extract metadata from PyTorch model directory."""
        warnings = []
        errors = []
        
        # Look for config.json
        config_path = os.path.join(dir_path, "config.json")
        config = {}
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except Exception as e:
                errors.append(f"Error reading config.json: {e}")
        else:
            warnings.append("No config.json found in directory")
        
        # Analyze model files
        model_files = []
        total_size = 0
        
        for file in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                total_size += file_size
                
                if file.endswith(('.bin', '.pt', '.pth', '.safetensors')):
                    model_files.append({
                        "name": file,
                        "size": file_size,
                        "type": file.split('.')[-1]
                    })
        
        # Extract information from config
        model_name = config.get("name", config.get("model_name", os.path.basename(dir_path)))
        architecture = config.get("architectures", [None])[0] if config.get("architectures") else None
        if not architecture:
            architecture = config.get("model_type", "unknown")
        
        # Extract parameters
        parameters = None
        if "num_parameters" in config:
            parameters = config["num_parameters"]
        elif "hidden_size" in config and "num_hidden_layers" in config:
            # Estimate for transformer models
            hidden_size = config["hidden_size"]
            num_layers = config["num_hidden_layers"]
            vocab_size = config.get("vocab_size", 50000)
            
            # Rough estimation for transformer models
            parameters = int(12 * num_layers * hidden_size * hidden_size + vocab_size * hidden_size)
            warnings.append("Parameter count estimated from config")
        
        # Extract other config values
        context_length = config.get("max_position_embeddings", config.get("n_positions"))
        vocab_size = config.get("vocab_size")
        
        # Look for tokenizer info
        tokenizer_info = {}
        tokenizer_files = ["tokenizer.json", "tokenizer_config.json", "vocab.txt", "merges.txt"]
        
        for tokenizer_file in tokenizer_files:
            tokenizer_path = os.path.join(dir_path, tokenizer_file)
            if os.path.exists(tokenizer_path):
                try:
                    if tokenizer_file.endswith('.json'):
                        with open(tokenizer_path, 'r', encoding='utf-8') as f:
                            tokenizer_info[tokenizer_file] = json.load(f)
                    else:
                        tokenizer_info[tokenizer_file] = {"exists": True, "size": os.path.getsize(tokenizer_path)}
                except Exception as e:
                    warnings.append(f"Error reading {tokenizer_file}: {e}")
        
        # Build tensor info
        tensor_info = {
            "model_files": model_files,
            "total_files": len(model_files),
            "total_size": total_size,
            "directory_size": total_size
        }
        
        # Get directory timestamps
        dir_stat = os.stat(dir_path)
        
        return UnifiedMetadata(
            format_type=ModelFormat.PYTORCH_BIN,
            model_name=model_name,
            architecture=architecture,
            parameters=parameters,
            context_length=context_length,
            vocab_size=vocab_size,
            file_size=total_size,
            tensor_info=tensor_info,
            config=config,
            tokenizer_info=tokenizer_info,
            model_type=config.get("model_type", "text-generation"),
            library_name="transformers",
            created_at=datetime.fromtimestamp(dir_stat.st_ctime).isoformat(),
            modified_at=datetime.fromtimestamp(dir_stat.st_mtime).isoformat(),
            warnings=warnings,
            errors=errors
        )
    
    def _extract_huggingface_metadata_fallback(self, model_id: str) -> UnifiedMetadata:
        """Fallback HF metadata extraction using direct API calls."""
        warnings = []
        errors = []
        
        try:
            # Get model info from HF API
            HF_API_BASE = "https://huggingface.co/api/models"
            response = requests.get(f"{HF_API_BASE}/{model_id}", timeout=30)
            
            if response.status_code == 200:
                model_info = response.json()
                return self._parse_huggingface_api_response(model_info, model_id)
            elif response.status_code == 401:
                errors.append("Model requires authentication")
            elif response.status_code == 404:
                errors.append("Model not found")
            else:
                errors.append(f"API error: HTTP {response.status_code}")
                
        except requests.RequestException as e:
            errors.append(f"Network error: {e}")
        except Exception as e:
            errors.append(f"Unexpected error: {e}")
        
        # Return fallback metadata
        return UnifiedMetadata(
            format_type=ModelFormat.HUGGINGFACE,
            model_name=model_id,
            config={"model_id": model_id},
            errors=errors,
            warnings=warnings,
            confidence=0.1
        )
    
    def _parse_huggingface_metadata(self, resolution, model_id: str) -> UnifiedMetadata:
        """Parse HuggingFace integration resolution into unified metadata."""
        return UnifiedMetadata(
            format_type=ModelFormat.HUGGINGFACE,
            model_name=resolution.model_id,
            architecture=resolution.architecture,
            model_type=resolution.model_type,
            library_name=getattr(resolution, 'library_name', 'transformers'),
            tags=resolution.tags or [],
            license=getattr(resolution, 'license', None),
            downloads=resolution.downloads,
            file_size=resolution.size_bytes or 0,
            config={
                "model_id": model_id,
                "is_private": resolution.is_private,
                "requires_auth": resolution.requires_auth,
                "last_modified": resolution.last_modified
            },
            created_at=getattr(resolution, 'created_at', None),
            modified_at=resolution.last_modified
        )
    
    def _parse_huggingface_api_response(self, model_info: Dict[str, Any], model_id: str) -> UnifiedMetadata:
        """Parse HuggingFace API response into unified metadata."""
        return UnifiedMetadata(
            format_type=ModelFormat.HUGGINGFACE,
            model_name=model_id,
            architecture=model_info.get("pipeline_tag"),
            model_type=model_info.get("pipeline_tag", "text-generation"),
            library_name=model_info.get("library_name", "transformers"),
            tags=model_info.get("tags", []),
            license=model_info.get("license"),
            downloads=model_info.get("downloads", 0),
            config={
                "model_id": model_id,
                "is_private": model_info.get("private", False),
                "last_modified": model_info.get("lastModified"),
                "siblings": model_info.get("siblings", [])
            },
            created_at=model_info.get("createdAt"),
            modified_at=model_info.get("lastModified")
        )
    
    def _infer_architecture_from_tensors(self, tensor_names: List[str]) -> Optional[str]:
        """Infer model architecture from tensor names."""
        tensor_str = ' '.join(tensor_names).lower()
        
        if 'llama' in tensor_str or 'lm_head' in tensor_str:
            return 'llama'
        elif 'mistral' in tensor_str:
            return 'mistral'
        elif 'qwen' in tensor_str:
            return 'qwen'
        elif 'deepseek' in tensor_str:
            return 'deepseek'
        elif 'bert' in tensor_str:
            return 'bert'
        elif 'gpt' in tensor_str:
            return 'gpt'
        elif any(name in tensor_str for name in ['transformer', 'attention', 'mlp']):
            return 'transformer'
        elif 'embed_tokens' in tensor_str and 'self_attn' in tensor_str:
            # Generic transformer pattern - likely LLaMA-style
            return 'llama'
        
        return None
  
    def _estimate_missing_parameters(self, metadata: UnifiedMetadata) -> UnifiedMetadata:
        """Estimate missing parameters using various heuristics."""
        if metadata.parameters is not None:
            return metadata
        
        warnings = list(metadata.warnings) if metadata.warnings else []
        
        # Try to estimate from file size
        if metadata.file_size > 0:
            # Very rough estimation: 1 parameter ≈ 2-4 bytes (depending on precision)
            # This is a fallback estimation
            if metadata.format_type == ModelFormat.GGUF:
                # GGUF files are often quantized
                estimated_params = metadata.file_size // 2  # Assume 2 bytes per param on average
            else:
                # Full precision models
                estimated_params = metadata.file_size // 4  # Assume 4 bytes per param (float32)
            
            # Round to reasonable values
            if estimated_params > 1e9:
                estimated_params = round(estimated_params / 1e9) * 1e9
            elif estimated_params > 1e6:
                estimated_params = round(estimated_params / 1e6) * 1e6
            
            metadata.parameters = int(estimated_params)
            warnings.append("Parameter count estimated from file size")
            metadata.confidence *= 0.7  # Reduce confidence for estimates
        
        # Try to estimate from architecture and config
        if metadata.config and metadata.architecture:
            estimated = self._estimate_params_from_architecture(metadata.config, metadata.architecture)
            if estimated and (not metadata.parameters or abs(estimated - metadata.parameters) < metadata.parameters * 0.5):
                metadata.parameters = estimated
                warnings.append("Parameter count estimated from architecture")
        
        metadata.warnings = warnings
        return metadata
    
    def _estimate_params_from_architecture(self, config: Dict[str, Any], architecture: str) -> Optional[int]:
        """Estimate parameters from architecture and config."""
        try:
            if architecture.lower() in ['llama', 'mistral', 'qwen', 'deepseek']:
                # Transformer architecture estimation
                hidden_size = config.get('hidden_size', config.get('embed_dim', config.get('d_model')))
                num_layers = config.get('num_hidden_layers', config.get('num_layers', config.get('n_layer')))
                vocab_size = config.get('vocab_size', 50000)
                
                if hidden_size and num_layers:
                    # Rough transformer parameter estimation
                    # Embedding: vocab_size * hidden_size
                    # Attention: 4 * hidden_size^2 per layer (Q, K, V, O projections)
                    # FFN: 8 * hidden_size^2 per layer (assuming 4x expansion)
                    # Layer norm: 2 * hidden_size per layer
                    
                    embedding_params = vocab_size * hidden_size
                    attention_params = num_layers * 4 * hidden_size * hidden_size
                    ffn_params = num_layers * 8 * hidden_size * hidden_size
                    norm_params = num_layers * 2 * hidden_size
                    
                    total_params = embedding_params + attention_params + ffn_params + norm_params
                    return int(total_params)
            
        except Exception:
            pass
        
        return None
    
    def _estimate_parameters_from_tensors(self, header_json: Dict[str, Any]) -> Optional[int]:
        """Estimate parameters from safetensors tensor information."""
        try:
            total_params = 0
            
            for key, value in header_json.items():
                if key != "__metadata__" and isinstance(value, dict):
                    shape = value.get("shape", [])
                    if shape:
                        # Calculate number of parameters in this tensor
                        tensor_params = 1
                        for dim in shape:
                            tensor_params *= dim
                        total_params += tensor_params
            
            return total_params if total_params > 0 else None
            
        except Exception:
            return None
    
    def _map_gguf_file_type_to_quantization(self, file_type: int) -> str:
        """Map GGUF file type to quantization string."""
        quantization_map = {
            0: "F32",
            1: "F16",
            2: "Q4_0",
            3: "Q4_1",
            6: "Q5_0",
            7: "Q5_1",
            8: "Q8_0",
            9: "Q8_1",
            10: "Q2_K",
            11: "Q3_K_S",
            12: "Q3_K_M",
            13: "Q3_K_L",
            14: "Q4_K_S",
            15: "Q4_K_M",
            16: "Q5_K_S",
            17: "Q5_K_M",
            18: "Q6_K"
        }
        
        return quantization_map.get(file_type, f"Unknown({file_type})")
    
    def _create_fallback_metadata(self, path: str, format_type: ModelFormat, 
                                error_msg: str = None) -> UnifiedMetadata:
        """Create fallback metadata when extraction fails."""
        model_name = os.path.basename(path) if os.path.exists(path) else path
        file_size = 0
        
        try:
            if os.path.exists(path):
                if os.path.isfile(path):
                    file_size = os.path.getsize(path)
                elif os.path.isdir(path):
                    file_size = sum(os.path.getsize(os.path.join(path, f)) 
                                  for f in os.listdir(path) 
                                  if os.path.isfile(os.path.join(path, f)))
        except Exception:
            pass
        
        errors = [error_msg] if error_msg else []
        
        return UnifiedMetadata(
            format_type=format_type,
            model_name=model_name,
            file_size=file_size,
            config={"fallback": True},
            errors=errors,
            confidence=0.1
        )
    
    def _get_cache_path(self, model_path: str, format_type: ModelFormat) -> Path:
        """Get cache file path for model metadata."""
        # Create hash from path and format
        cache_key = f"{model_path}:{format_type.value}"
        file_hash = hashlib.md5(cache_key.encode()).hexdigest()
        return self.CACHE_DIR / f"{file_hash}.json"
    
    def _get_cached_metadata(self, model_path: str, format_type: ModelFormat) -> Optional[UnifiedMetadata]:
        """Get cached metadata if valid."""
        cache_path = self._get_cache_path(model_path, format_type)
        
        if not cache_path.exists():
            return None
        
        try:
            # Check cache age
            cache_stat = os.stat(cache_path)
            cache_time = datetime.fromtimestamp(cache_stat.st_mtime)
            if datetime.now() - cache_time > self.CACHE_EXPIRY:
                return None
            
            # Check if source file/directory has been modified
            if os.path.exists(model_path):
                source_stat = os.stat(model_path)
                source_time = datetime.fromtimestamp(source_stat.st_mtime)
                if source_time > cache_time:
                    return None
            
            # Load cached metadata
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Convert back to UnifiedMetadata
            # Handle enum conversion
            data['format_type'] = ModelFormat(data['format_type'])
            
            return UnifiedMetadata(**data)
            
        except Exception as e:
            self.logger.warning(f"Error reading cache: {e}")
            return None
    
    def _cache_metadata(self, model_path: str, format_type: ModelFormat, 
                       metadata: UnifiedMetadata) -> None:
        """Cache metadata for future use."""
        cache_path = self._get_cache_path(model_path, format_type)
        
        try:
            # Convert to dict for JSON serialization
            data = asdict(metadata)
            data['format_type'] = metadata.format_type.value  # Convert enum to string
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.warning(f"Error caching metadata: {e}")
    
    def clear_cache(self) -> int:
        """Clear all cached metadata."""
        count = 0
        try:
            for cache_file in self.CACHE_DIR.glob("*.json"):
                cache_file.unlink()
                count += 1
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
        
        return count
    
    def clear_expired_cache(self) -> int:
        """Clear expired cache entries."""
        count = 0
        now = datetime.now()
        
        try:
            for cache_file in self.CACHE_DIR.glob("*.json"):
                try:
                    cache_stat = os.stat(cache_file)
                    cache_time = datetime.fromtimestamp(cache_stat.st_mtime)
                    if now - cache_time > self.CACHE_EXPIRY:
                        cache_file.unlink()
                        count += 1
                except Exception:
                    continue
        except Exception as e:
            self.logger.error(f"Error clearing expired cache: {e}")
        
        return count
    
    def unify_metadata(self, raw_metadata: Dict[str, Any], format_type: ModelFormat) -> UnifiedMetadata:
        """
        Convert raw metadata from any format into unified representation.
        
        This is a utility method for external use when raw metadata is already available.
        """
        if format_type == ModelFormat.GGUF:
            return self._parse_gguf_metadata(raw_metadata, "unknown", 0, 0)
        elif format_type == ModelFormat.SAFETENSORS:
            return self._parse_safetensors_metadata(raw_metadata, "unknown", 0)
        elif format_type == ModelFormat.PYTORCH_BIN:
            # For PyTorch, raw_metadata should be the config
            metadata = UnifiedMetadata(
                format_type=format_type,
                model_name="unknown",
                config=raw_metadata
            )
            return self._estimate_missing_parameters(metadata)
        elif format_type == ModelFormat.HUGGINGFACE:
            return self._parse_huggingface_api_response(raw_metadata, "unknown")
        else:
            return self._create_fallback_metadata("unknown", format_type)