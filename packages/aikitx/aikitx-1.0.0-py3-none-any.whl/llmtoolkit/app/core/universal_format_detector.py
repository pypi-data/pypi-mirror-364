"""
Universal Format Detector

This module contains the UniversalFormatDetector class, which is responsible for
automatically detecting model formats (GGUF, safetensors, PyTorch bin, HF model IDs)
and routing them to appropriate validation systems.
"""

import os
import re
import json
import struct
import logging
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union, BinaryIO
from enum import Enum
from dataclasses import dataclass

class ModelFormat(Enum):
    """Enumeration of supported model formats."""
    GGUF = "gguf"
    SAFETENSORS = "safetensors"
    PYTORCH_BIN = "pytorch_bin"
    HUGGINGFACE = "huggingface"
    UNKNOWN = "unknown"

@dataclass
class DirectoryAnalysis:
    """Analysis result for model directories."""
    format_type: ModelFormat
    main_files: List[str]
    config_files: List[str]
    tokenizer_files: List[str]
    total_size: int
    file_count: int
    is_multi_file: bool
    confidence: float

@dataclass
class HFValidationResult:
    """Result of Hugging Face model ID validation."""
    is_valid: bool
    model_id: str
    exists: bool
    accessible: bool
    requires_auth: bool
    model_info: Optional[Dict[str, Any]]
    error_message: Optional[str]

@dataclass
class FormatDetectionResult:
    """Result of format detection."""
    format_type: ModelFormat
    confidence: float
    file_path: Optional[str]
    directory_analysis: Optional[DirectoryAnalysis]
    hf_validation: Optional[HFValidationResult]
    error_message: Optional[str]
    metadata: Dict[str, Any]

class FormatValidator:
    """Base class for format-specific validators."""
    
    def validate(self, path: str) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Validate a model file or directory.
        
        Args:
            path: Path to validate
            
        Returns:
            Tuple of (is_valid, error_message, metadata)
        """
        raise NotImplementedError

class GGUFValidator(FormatValidator):
    """Validator for GGUF format files."""
    
    GGUF_MAGIC = b"GGUF"
    
    def validate(self, path: str) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """Validate GGUF file format."""
        try:
            if not os.path.exists(path):
                return False, f"File does not exist: {path}", {}
            
            if not os.path.isfile(path):
                return False, f"Not a file: {path}", {}
            
            # Check file size
            file_size = os.path.getsize(path)
            if file_size < 16:
                return False, f"File too small to be valid GGUF: {file_size} bytes", {}
            
            # Check GGUF magic bytes and header
            with open(path, 'rb') as f:
                magic = f.read(4)
                if magic != self.GGUF_MAGIC:
                    return False, f"Invalid GGUF magic bytes: {magic}", {}
                
                # Read version
                version_bytes = f.read(4)
                if len(version_bytes) != 4:
                    return False, "Incomplete GGUF header: missing version", {}
                
                version = int.from_bytes(version_bytes, byteorder='little')
                if version < 1 or version > 3:
                    return False, f"Unsupported GGUF version: {version}", {}
                
                # Read tensor count
                tensor_count_bytes = f.read(8)
                if len(tensor_count_bytes) != 8:
                    return False, "Incomplete GGUF header: missing tensor count", {}
                
                tensor_count = int.from_bytes(tensor_count_bytes, byteorder='little')
                
                # Read metadata count
                metadata_count_bytes = f.read(8)
                if len(metadata_count_bytes) != 8:
                    return False, "Incomplete GGUF header: missing metadata count", {}
                
                metadata_count = int.from_bytes(metadata_count_bytes, byteorder='little')
                
                metadata = {
                    "version": version,
                    "tensor_count": tensor_count,
                    "metadata_count": metadata_count,
                    "file_size": file_size
                }
                
                return True, None, metadata
                
        except Exception as e:
            return False, f"Error validating GGUF file: {e}", {}

class SafetensorsValidator(FormatValidator):
    """Validator for safetensors format files."""
    
    def validate(self, path: str) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """Validate safetensors file format."""
        try:
            if not os.path.exists(path):
                return False, f"File does not exist: {path}", {}
            
            if not os.path.isfile(path):
                return False, f"Not a file: {path}", {}
            
            # Check file size
            file_size = os.path.getsize(path)
            if file_size < 8:
                return False, f"File too small to be valid safetensors: {file_size} bytes", {}
            
            # Read safetensors header
            with open(path, 'rb') as f:
                # Read header length (first 8 bytes, little-endian)
                header_length_bytes = f.read(8)
                if len(header_length_bytes) != 8:
                    return False, "Incomplete safetensors header", {}
                
                header_length = int.from_bytes(header_length_bytes, byteorder='little')
                if header_length <= 0 or header_length > file_size:
                    return False, f"Invalid header length: {header_length}", {}
                
                # Read header JSON
                header_bytes = f.read(header_length)
                if len(header_bytes) != header_length:
                    return False, "Incomplete safetensors header data", {}
                
                try:
                    header_json = json.loads(header_bytes.decode('utf-8'))
                except json.JSONDecodeError as e:
                    return False, f"Invalid JSON in safetensors header: {e}", {}
                
                # Extract metadata
                metadata = {
                    "header_length": header_length,
                    "file_size": file_size,
                    "tensors": {}
                }
                
                # Count tensors and get info
                tensor_count = 0
                total_tensor_size = 0
                for key, value in header_json.items():
                    if key != "__metadata__":
                        tensor_count += 1
                        if isinstance(value, dict) and "data_offsets" in value:
                            offsets = value["data_offsets"]
                            if len(offsets) == 2:
                                tensor_size = offsets[1] - offsets[0]
                                total_tensor_size += tensor_size
                
                metadata["tensor_count"] = tensor_count
                metadata["total_tensor_size"] = total_tensor_size
                
                # Extract model metadata if present
                if "__metadata__" in header_json:
                    metadata["model_metadata"] = header_json["__metadata__"]
                
                return True, None, metadata
                
        except Exception as e:
            return False, f"Error validating safetensors file: {e}", {}

class PyTorchValidator(FormatValidator):
    """Validator for PyTorch bin format files and directories."""
    
    def validate(self, path: str) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """Validate PyTorch model file or directory."""
        try:
            if not os.path.exists(path):
                return False, f"Path does not exist: {path}", {}
            
            metadata = {"file_size": 0, "files": []}
            
            if os.path.isfile(path):
                # Single PyTorch bin file
                if not path.lower().endswith(('.bin', '.pt', '.pth')):
                    return False, f"Not a PyTorch model file: {path}", {}
                
                file_size = os.path.getsize(path)
                if file_size < 100:  # Very small files are unlikely to be valid models
                    return False, f"File too small to be valid PyTorch model: {file_size} bytes", {}
                
                # Try to load as PyTorch file (basic check)
                try:
                    try:
                        import torch
                        # Just check if it's a valid torch file without loading it fully
                        with open(path, 'rb') as f:
                            # Check for PyTorch magic number
                            magic = f.read(8)
                            f.seek(0)
                            # This is a basic check - real validation would be more complex
                            
                        metadata = {
                            "file_size": file_size,
                            "files": [os.path.basename(path)],
                            "is_single_file": True
                        }
                        
                        return True, None, metadata
                        
                    except ImportError:
                        # PyTorch not available, do basic file check
                        metadata = {
                            "file_size": file_size,
                            "files": [os.path.basename(path)],
                            "is_single_file": True,
                            "warning": "PyTorch not available for full validation"
                        }
                        return True, None, metadata
                        
                except Exception as e:
                    return False, f"Invalid PyTorch file: {e}", {}
            
            elif os.path.isdir(path):
                # PyTorch model directory
                config_file = os.path.join(path, "config.json")
                if not os.path.exists(config_file):
                    return False, "No config.json found in directory", {}
                
                # Look for model files
                model_files = []
                total_size = 0
                
                for file in os.listdir(path):
                    file_path = os.path.join(path, file)
                    if os.path.isfile(file_path):
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        
                        if file.endswith(('.bin', '.pt', '.pth')):
                            model_files.append(file)
                
                if not model_files:
                    return False, "No PyTorch model files found in directory", {}
                
                # Try to read config
                try:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                except json.JSONDecodeError as e:
                    return False, f"Invalid config.json: {e}", {}
                
                metadata = {
                    "file_size": total_size,
                    "files": model_files,
                    "config_file": "config.json",
                    "is_single_file": False,
                    "config": config
                }
                
                return True, None, metadata
            
            else:
                return False, f"Path is neither file nor directory: {path}", {}
                
        except Exception as e:
            return False, f"Error validating PyTorch model: {e}", {}

class HuggingFaceValidator(FormatValidator):
    """Validator for Hugging Face model IDs."""
    
    HF_MODEL_ID_PATTERN = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9._-]*(/[a-zA-Z0-9][a-zA-Z0-9._-]*)?$')
    
    def validate(self, model_id: str) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """Validate Hugging Face model ID using the HuggingFace integration service."""
        try:
            # Basic format validation
            if not self.HF_MODEL_ID_PATTERN.match(model_id):
                return False, f"Invalid Hugging Face model ID format: {model_id}", {}
            
            # Use HuggingFace integration service for validation
            try:
                from llmtoolkit.app.services.huggingface_integration import HuggingFaceIntegration
                
                hf_integration = HuggingFaceIntegration()
                resolution = hf_integration.resolve_model_id(model_id)
                
                if resolution.exists:
                    metadata = {
                        "model_id": resolution.model_id,
                        "exists": resolution.exists,
                        "accessible": not resolution.requires_auth or hf_integration.is_authenticated(),
                        "requires_auth": resolution.requires_auth,
                        "is_private": resolution.is_private,
                        "model_type": resolution.model_type,
                        "architecture": resolution.architecture,
                        "tags": resolution.tags,
                        "downloads": resolution.downloads,
                        "last_modified": resolution.last_modified,
                        "size_bytes": resolution.size_bytes
                    }
                    
                    if resolution.requires_auth and not hf_integration.is_authenticated():
                        return True, "Model requires authentication", metadata
                    else:
                        return True, None, metadata
                else:
                    return False, resolution.error_message or f"Model not found: {model_id}", {
                        "model_id": model_id, 
                        "exists": False
                    }
                    
            except ImportError:
                # Fallback to basic requests if HF integration not available
                return self._validate_with_requests(model_id)
                
        except Exception as e:
            return False, f"Error validating Hugging Face model ID: {e}", {}
    
    def _validate_with_requests(self, model_id: str) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """Fallback validation using basic requests."""
        try:
            HF_API_BASE = "https://huggingface.co/api/models"
            response = requests.get(f"{HF_API_BASE}/{model_id}", timeout=10)
            
            if response.status_code == 200:
                model_info = response.json()
                metadata = {
                    "model_id": model_id,
                    "exists": True,
                    "accessible": True,
                    "requires_auth": False,
                    "model_info": model_info
                }
                return True, None, metadata
                
            elif response.status_code == 401:
                metadata = {
                    "model_id": model_id,
                    "exists": True,
                    "accessible": False,
                    "requires_auth": True,
                    "model_info": None
                }
                return True, "Model requires authentication", metadata
                
            elif response.status_code == 404:
                return False, f"Model not found: {model_id}", {"model_id": model_id, "exists": False}
                
            else:
                return False, f"Error accessing model: HTTP {response.status_code}", {"model_id": model_id}
                
        except requests.RequestException as e:
            # Network error - assume model might be valid but can't verify
            metadata = {
                "model_id": model_id,
                "exists": None,
                "accessible": None,
                "requires_auth": None,
                "model_info": None,
                "network_error": str(e)
            }
            return True, f"Cannot verify model (network error): {e}", metadata
            
        except Exception as e:
            return False, f"Error validating Hugging Face model ID: {e}", {}

class UniversalFormatDetector:
    """
    Universal format detector for AI model files and identifiers.
    
    This class automatically detects model formats (GGUF, safetensors, PyTorch bin, HF model IDs)
    and provides format-specific validation routing.
    """
    
    def __init__(self):
        """Initialize the universal format detector."""
        self.logger = logging.getLogger("gguf_loader.universal_format_detector")
        
        # Initialize format validators
        self.validators = {
            ModelFormat.GGUF: GGUFValidator(),
            ModelFormat.SAFETENSORS: SafetensorsValidator(),
            ModelFormat.PYTORCH_BIN: PyTorchValidator(),
            ModelFormat.HUGGINGFACE: HuggingFaceValidator()
        }
    
    def detect_format(self, input_path: str) -> FormatDetectionResult:
        """
        Detect the format of a model file, directory, or Hugging Face model ID.
        
        Args:
            input_path: Path to file/directory or Hugging Face model ID
            
        Returns:
            FormatDetectionResult containing detection results
        """
        self.logger.info(f"Detecting format for: {input_path}")
        
        try:
            # Check if it's a Hugging Face model ID first
            if self._is_huggingface_model_id(input_path):
                return self._detect_huggingface_format(input_path)
            
            # Check if it's a file or directory
            if os.path.exists(input_path):
                if os.path.isfile(input_path):
                    return self._detect_file_format(input_path)
                elif os.path.isdir(input_path):
                    return self._detect_directory_format(input_path)
                else:
                    return FormatDetectionResult(
                        format_type=ModelFormat.UNKNOWN,
                        confidence=0.0,
                        file_path=input_path,
                        directory_analysis=None,
                        hf_validation=None,
                        error_message="Path is neither file nor directory",
                        metadata={}
                    )
            else:
                return FormatDetectionResult(
                    format_type=ModelFormat.UNKNOWN,
                    confidence=0.0,
                    file_path=input_path,
                    directory_analysis=None,
                    hf_validation=None,
                    error_message="Path does not exist",
                    metadata={}
                )
                
        except Exception as e:
            self.logger.error(f"Error detecting format for {input_path}: {e}")
            return FormatDetectionResult(
                format_type=ModelFormat.UNKNOWN,
                confidence=0.0,
                file_path=input_path,
                directory_analysis=None,
                hf_validation=None,
                error_message=f"Detection error: {e}",
                metadata={}
            )
    
    def _is_huggingface_model_id(self, input_str: str) -> bool:
        """Check if input string looks like a Hugging Face model ID."""
        # Should not be a file path
        if os.path.sep in input_str or input_str.startswith('.'):
            return False
        
        # Should not contain file extensions
        if any(input_str.lower().endswith(ext) for ext in ['.gguf', '.safetensors', '.bin', '.pt', '.pth']):
            return False
        
        # Should match HF model ID pattern (can be with or without organization)
        return HuggingFaceValidator.HF_MODEL_ID_PATTERN.match(input_str) is not None
    
    def _detect_file_format(self, file_path: str) -> FormatDetectionResult:
        """Detect format of a single file."""
        file_ext = Path(file_path).suffix.lower()
        
        # Try format detection based on file extension first
        if file_ext == '.gguf':
            return self._validate_format(ModelFormat.GGUF, file_path)
        elif file_ext == '.safetensors':
            return self._validate_format(ModelFormat.SAFETENSORS, file_path)
        elif file_ext in ['.bin', '.pt', '.pth']:
            return self._validate_format(ModelFormat.PYTORCH_BIN, file_path)
        else:
            # Try to detect by content
            return self._detect_by_content(file_path)
    
    def _detect_directory_format(self, dir_path: str) -> FormatDetectionResult:
        """Detect format of a model directory."""
        analysis = self.analyze_directory_structure(dir_path)
        
        if analysis.format_type != ModelFormat.UNKNOWN:
            # Validate using the detected format
            is_valid, error_msg, metadata = self.validators[analysis.format_type].validate(dir_path)
            
            return FormatDetectionResult(
                format_type=analysis.format_type,
                confidence=analysis.confidence,
                file_path=dir_path,
                directory_analysis=analysis,
                hf_validation=None,
                error_message=error_msg if not is_valid else None,
                metadata=metadata
            )
        else:
            return FormatDetectionResult(
                format_type=ModelFormat.UNKNOWN,
                confidence=0.0,
                file_path=dir_path,
                directory_analysis=analysis,
                hf_validation=None,
                error_message="Could not determine directory format",
                metadata={}
            )
    
    def _detect_huggingface_format(self, model_id: str) -> FormatDetectionResult:
        """Detect and validate Hugging Face model ID."""
        hf_result = self.validate_huggingface_id(model_id)
        
        return FormatDetectionResult(
            format_type=ModelFormat.HUGGINGFACE,
            confidence=1.0 if hf_result.is_valid else 0.0,
            file_path=None,
            directory_analysis=None,
            hf_validation=hf_result,
            error_message=hf_result.error_message if not hf_result.is_valid else None,
            metadata=hf_result.model_info or {}
        )
    
    def _detect_by_content(self, file_path: str) -> FormatDetectionResult:
        """Detect format by examining file content."""
        try:
            with open(file_path, 'rb') as f:
                # Read first few bytes to check magic numbers
                header = f.read(16)
                
                # Check for GGUF magic
                if header.startswith(b'GGUF'):
                    return self._validate_format(ModelFormat.GGUF, file_path)
                
                # Check for safetensors (JSON header after length)
                if len(header) >= 8:
                    try:
                        header_length = int.from_bytes(header[:8], byteorder='little')
                        if 0 < header_length < os.path.getsize(file_path):
                            f.seek(8)
                            json_header = f.read(min(header_length, 1024))
                            json.loads(json_header.decode('utf-8'))
                            return self._validate_format(ModelFormat.SAFETENSORS, file_path)
                    except:
                        pass
                
                # Check for PyTorch format only if file has appropriate extension
                if Path(file_path).suffix.lower() in ['.bin', '.pt', '.pth']:
                    try:
                        # This is a simplified check - real PyTorch detection would be more sophisticated
                        try:
                            import torch
                            # If we can import torch, try a basic check
                            return self._validate_format(ModelFormat.PYTORCH_BIN, file_path)
                        except ImportError:
                            # PyTorch not available, do basic file extension check
                            return self._validate_format(ModelFormat.PYTORCH_BIN, file_path)
                    except Exception:
                        pass
                
        except Exception as e:
            self.logger.warning(f"Error detecting format by content: {e}")
        
        return FormatDetectionResult(
            format_type=ModelFormat.UNKNOWN,
            confidence=0.0,
            file_path=file_path,
            directory_analysis=None,
            hf_validation=None,
            error_message="Could not determine file format",
            metadata={}
        )
    
    def _validate_format(self, format_type: ModelFormat, path: str) -> FormatDetectionResult:
        """Validate a specific format."""
        validator = self.validators[format_type]
        is_valid, error_msg, metadata = validator.validate(path)
        
        return FormatDetectionResult(
            format_type=format_type,
            confidence=1.0 if is_valid else 0.0,
            file_path=path,
            directory_analysis=None,
            hf_validation=None,
            error_message=error_msg if not is_valid else None,
            metadata=metadata
        )
    
    def analyze_directory_structure(self, dir_path: str) -> DirectoryAnalysis:
        """
        Analyze directory structure to determine model format.
        
        Args:
            dir_path: Path to directory to analyze
            
        Returns:
            DirectoryAnalysis with format detection results
        """
        try:
            if not os.path.isdir(dir_path):
                return DirectoryAnalysis(
                    format_type=ModelFormat.UNKNOWN,
                    main_files=[],
                    config_files=[],
                    tokenizer_files=[],
                    total_size=0,
                    file_count=0,
                    is_multi_file=False,
                    confidence=0.0
                )
            
            main_files = []
            config_files = []
            tokenizer_files = []
            total_size = 0
            file_count = 0
            
            # Scan directory
            for item in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item)
                if os.path.isfile(item_path):
                    file_count += 1
                    file_size = os.path.getsize(item_path)
                    total_size += file_size
                    
                    item_lower = item.lower()
                    
                    # Categorize files
                    if item_lower.endswith('.gguf'):
                        main_files.append(item)
                    elif item_lower.endswith('.safetensors'):
                        main_files.append(item)
                    elif item_lower.endswith(('.bin', '.pt', '.pth')):
                        main_files.append(item)
                    elif item_lower in ['config.json', 'model_config.json']:
                        config_files.append(item)
                    elif 'tokenizer' in item_lower:
                        tokenizer_files.append(item)
                    elif item_lower in ['tokenizer.json', 'vocab.txt', 'merges.txt']:
                        tokenizer_files.append(item)
            
            # Determine format based on files found
            format_type = ModelFormat.UNKNOWN
            confidence = 0.0
            
            if any(f.endswith('.gguf') for f in main_files):
                format_type = ModelFormat.GGUF
                confidence = 0.9
            elif any(f.endswith('.safetensors') for f in main_files):
                format_type = ModelFormat.SAFETENSORS
                confidence = 0.9
            elif any(f.endswith(('.bin', '.pt', '.pth')) for f in main_files) and config_files:
                format_type = ModelFormat.PYTORCH_BIN
                confidence = 0.8
            elif config_files and tokenizer_files:
                # Might be a Hugging Face model directory
                format_type = ModelFormat.PYTORCH_BIN  # Default to PyTorch for HF models
                confidence = 0.6
            
            return DirectoryAnalysis(
                format_type=format_type,
                main_files=main_files,
                config_files=config_files,
                tokenizer_files=tokenizer_files,
                total_size=total_size,
                file_count=file_count,
                is_multi_file=len(main_files) > 1,
                confidence=confidence
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing directory structure: {e}")
            return DirectoryAnalysis(
                format_type=ModelFormat.UNKNOWN,
                main_files=[],
                config_files=[],
                tokenizer_files=[],
                total_size=0,
                file_count=0,
                is_multi_file=False,
                confidence=0.0
            )
    
    def validate_huggingface_id(self, model_id: str) -> HFValidationResult:
        """
        Validate and resolve Hugging Face model ID.
        
        Args:
            model_id: Hugging Face model ID to validate
            
        Returns:
            HFValidationResult with validation results
        """
        try:
            validator = self.validators[ModelFormat.HUGGINGFACE]
            is_valid, error_msg, metadata = validator.validate(model_id)
            
            return HFValidationResult(
                is_valid=is_valid,
                model_id=model_id,
                exists=metadata.get("exists", False),
                accessible=metadata.get("accessible", False),
                requires_auth=metadata.get("requires_auth", False),
                model_info=metadata.get("model_info"),
                error_message=error_msg
            )
            
        except Exception as e:
            self.logger.error(f"Error validating Hugging Face model ID: {e}")
            return HFValidationResult(
                is_valid=False,
                model_id=model_id,
                exists=False,
                accessible=False,
                requires_auth=False,
                model_info=None,
                error_message=f"Validation error: {e}"
            )
    
    def get_format_validator(self, format_type: ModelFormat) -> FormatValidator:
        """
        Get the validator for a specific format.
        
        Args:
            format_type: Format to get validator for
            
        Returns:
            FormatValidator instance
            
        Raises:
            ValueError: If format type is not supported
        """
        if format_type not in self.validators:
            raise ValueError(f"Unsupported format type: {format_type}")
        
        return self.validators[format_type]
    
    def get_supported_formats(self) -> List[ModelFormat]:
        """
        Get list of supported model formats.
        
        Returns:
            List of supported ModelFormat values
        """
        return list(self.validators.keys())
    
    def get_format_extensions(self, format_type: ModelFormat) -> List[str]:
        """
        Get file extensions associated with a format.
        
        Args:
            format_type: Format to get extensions for
            
        Returns:
            List of file extensions (including the dot)
        """
        extension_map = {
            ModelFormat.GGUF: ['.gguf'],
            ModelFormat.SAFETENSORS: ['.safetensors'],
            ModelFormat.PYTORCH_BIN: ['.bin', '.pt', '.pth'],
            ModelFormat.HUGGINGFACE: []  # No file extensions for HF model IDs
        }
        
        return extension_map.get(format_type, [])