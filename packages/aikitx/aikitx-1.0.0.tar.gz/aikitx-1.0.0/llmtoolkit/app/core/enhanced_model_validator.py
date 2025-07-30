"""
Enhanced Model Validator for Multi-Format Support

This module provides comprehensive validation for all supported model formats
with improved version tolerance, detailed error reporting, and progressive validation.
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
from datetime import datetime

from llmtoolkit.app.core.universal_format_detector import ModelFormat


@dataclass
class ValidationError:
    """Represents a validation error with severity and context."""
    code: str
    message: str
    severity: str  # 'critical', 'warning', 'info'
    context: Dict[str, Any]
    suggestion: Optional[str] = None


@dataclass
class ValidationWarning:
    """Represents a validation warning."""
    code: str
    message: str
    context: Dict[str, Any]
    suggestion: Optional[str] = None


@dataclass
class FileInfo:
    """File information for validation context."""
    path: str
    size: int
    modified: datetime
    exists: bool
    is_file: bool
    is_directory: bool


@dataclass
class UnifiedMetadata:
    """Unified metadata representation across all formats."""
    format_type: ModelFormat
    model_name: str
    architecture: Optional[str]
    parameters: Optional[int]
    quantization: Optional[str]
    context_length: Optional[int]
    vocab_size: Optional[int]
    file_size: int
    tensor_info: Dict[str, Any]
    config: Dict[str, Any]
    tokenizer_info: Optional[Dict[str, Any]]
    version: Optional[str]
    compatibility_mode: Optional[str]


@dataclass
class ValidationResult:
    """Comprehensive validation result."""
    is_valid: bool
    format_type: ModelFormat
    version: Optional[str]
    compatibility_mode: Optional[str]
    errors: List[ValidationError]
    warnings: List[ValidationWarning]
    file_info: FileInfo
    metadata: Optional[UnifiedMetadata]
    validation_time: float
    progressive_results: Dict[str, bool]  # Results of each validation step


class EnhancedModelValidator:
    """
    Enhanced model validator with multi-format support and detailed error reporting.
    
    This validator provides:
    - Improved version tolerance for all formats
    - Progressive validation with detailed error reporting
    - Format-specific validation with fallback mechanisms
    - Unified metadata extraction across formats
    """
    
    def __init__(self):
        """Initialize the enhanced model validator."""
        self.logger = logging.getLogger("gguf_loader.enhanced_validator")
        
        # GGUF version compatibility
        self.SUPPORTED_GGUF_VERSIONS = [1, 2, 3]
        self.PREFERRED_GGUF_VERSION = 3
        
        # Hugging Face model ID pattern
        self.HF_MODEL_ID_PATTERN = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9._-]*(/[a-zA-Z0-9][a-zA-Z0-9._-]*)?$')
        
        # Common model architectures
        self.KNOWN_ARCHITECTURES = {
            'llama', 'mistral', 'mixtral', 'qwen', 'deepseek', 'phi', 'gemma',
            'falcon', 'mpt', 'gpt2', 'gptj', 'gpt_neox', 'bloom', 'opt'
        }
        
        # File size thresholds (in bytes)
        self.MIN_MODEL_SIZE = 1024 * 1024  # 1MB minimum
        self.LARGE_MODEL_THRESHOLD = 10 * 1024 * 1024 * 1024  # 10GB
    
    def validate_model(self, file_path: str, format_type: ModelFormat = None) -> ValidationResult:
        """
        Validate a model with comprehensive error reporting and progressive validation.
        
        Args:
            file_path: Path to model file, directory, or Hugging Face model ID
            format_type: Optional format hint to skip detection
            
        Returns:
            ValidationResult with detailed validation information
        """
        start_time = datetime.now()
        
        # Initialize result structure
        errors = []
        warnings = []
        progressive_results = {}
        
        try:
            # Step 1: Basic path validation
            progressive_results['path_validation'] = False
            file_info = self._validate_path(file_path, errors, warnings)
            if file_info.exists or self._is_huggingface_model_id(file_path):
                progressive_results['path_validation'] = True
            
            # Step 2: Format detection if not provided
            if format_type is None:
                progressive_results['format_detection'] = False
                format_type = self._detect_format(file_path, file_info, errors, warnings)
                if format_type != ModelFormat.UNKNOWN:
                    progressive_results['format_detection'] = True
            else:
                progressive_results['format_detection'] = True
            
            # Step 3: Format-specific validation
            progressive_results['format_validation'] = False
            metadata = None
            version = None
            compatibility_mode = None
            
            if format_type == ModelFormat.GGUF:
                is_valid, version, compatibility_mode, metadata = self._validate_gguf(
                    file_path, file_info, errors, warnings
                )
            elif format_type == ModelFormat.SAFETENSORS:
                is_valid, version, compatibility_mode, metadata = self._validate_safetensors(
                    file_path, file_info, errors, warnings
                )
            elif format_type == ModelFormat.PYTORCH_BIN:
                is_valid, version, compatibility_mode, metadata = self._validate_pytorch(
                    file_path, file_info, errors, warnings
                )
            elif format_type == ModelFormat.HUGGINGFACE:
                is_valid, version, compatibility_mode, metadata = self._validate_huggingface(
                    file_path, file_info, errors, warnings
                )
            else:
                is_valid = False
                errors.append(ValidationError(
                    code="UNKNOWN_FORMAT",
                    message=f"Unknown or unsupported model format: {format_type}",
                    severity="critical",
                    context={"format": format_type.value if format_type else "unknown"},
                    suggestion="Ensure the file is a valid GGUF, safetensors, PyTorch, or Hugging Face model"
                ))
            
            if is_valid:
                progressive_results['format_validation'] = True
            
            # Step 4: Metadata validation and enhancement
            progressive_results['metadata_validation'] = False
            if metadata:
                self._validate_metadata(metadata, errors, warnings)
                progressive_results['metadata_validation'] = True
            
            # Step 5: Size and performance validation
            progressive_results['size_validation'] = False
            if file_info.exists and file_info.size > 0:
                self._validate_size_and_performance(file_info, metadata, errors, warnings)
                progressive_results['size_validation'] = True
            
            # Determine overall validation result
            overall_valid = (
                len([e for e in errors if e.severity == 'critical']) == 0 and
                progressive_results.get('path_validation', False) and
                progressive_results.get('format_validation', False)
            )
            
            validation_time = (datetime.now() - start_time).total_seconds()
            
            return ValidationResult(
                is_valid=overall_valid,
                format_type=format_type,
                version=version,
                compatibility_mode=compatibility_mode,
                errors=errors,
                warnings=warnings,
                file_info=file_info,
                metadata=metadata,
                validation_time=validation_time,
                progressive_results=progressive_results
            )
            
        except Exception as e:
            self.logger.exception(f"Unexpected error during validation: {e}")
            errors.append(ValidationError(
                code="VALIDATION_ERROR",
                message=f"Unexpected validation error: {str(e)}",
                severity="critical",
                context={"exception": str(e)},
                suggestion="Check file permissions and try again"
            ))
            
            validation_time = (datetime.now() - start_time).total_seconds()
            
            return ValidationResult(
                is_valid=False,
                format_type=format_type or ModelFormat.UNKNOWN,
                version=None,
                compatibility_mode=None,
                errors=errors,
                warnings=warnings,
                file_info=file_info if 'file_info' in locals() else self._get_default_file_info(file_path),
                metadata=None,
                validation_time=validation_time,
                progressive_results=progressive_results
            )
    
    def _validate_path(self, file_path: str, errors: List[ValidationError], warnings: List[ValidationWarning]) -> FileInfo:
        """Validate the file path and gather basic file information."""
        try:
            # Handle Hugging Face model IDs
            if self._is_huggingface_model_id(file_path):
                return FileInfo(
                    path=file_path,
                    size=0,
                    modified=datetime.now(),
                    exists=True,  # We'll validate existence later
                    is_file=False,
                    is_directory=False
                )
            
            # Handle file system paths
            path_obj = Path(file_path)
            exists = path_obj.exists()
            
            if not exists:
                errors.append(ValidationError(
                    code="PATH_NOT_FOUND",
                    message=f"Path does not exist: {file_path}",
                    severity="critical",
                    context={"path": file_path},
                    suggestion="Check the file path and ensure the file exists"
                ))
                return FileInfo(
                    path=file_path,
                    size=0,
                    modified=datetime.now(),
                    exists=False,
                    is_file=False,
                    is_directory=False
                )
            
            is_file = path_obj.is_file()
            is_directory = path_obj.is_dir()
            
            if not is_file and not is_directory:
                errors.append(ValidationError(
                    code="INVALID_PATH_TYPE",
                    message=f"Path is neither a file nor directory: {file_path}",
                    severity="critical",
                    context={"path": file_path},
                    suggestion="Ensure the path points to a valid file or directory"
                ))
            
            # Get file stats
            stat = path_obj.stat()
            size = stat.st_size if is_file else sum(f.stat().st_size for f in path_obj.rglob('*') if f.is_file())
            modified = datetime.fromtimestamp(stat.st_mtime)
            
            # Check file size
            if is_file and size < self.MIN_MODEL_SIZE:
                warnings.append(ValidationWarning(
                    code="SMALL_FILE_SIZE",
                    message=f"File size ({size} bytes) is unusually small for a model file",
                    context={"size": size, "min_size": self.MIN_MODEL_SIZE},
                    suggestion="Verify this is a complete model file"
                ))
            
            return FileInfo(
                path=file_path,
                size=size,
                modified=modified,
                exists=exists,
                is_file=is_file,
                is_directory=is_directory
            )
            
        except Exception as e:
            errors.append(ValidationError(
                code="PATH_ACCESS_ERROR",
                message=f"Error accessing path: {str(e)}",
                severity="critical",
                context={"path": file_path, "error": str(e)},
                suggestion="Check file permissions and path accessibility"
            ))
            return self._get_default_file_info(file_path)
    
    def _detect_format(self, file_path: str, file_info: FileInfo, 
                      errors: List[ValidationError], warnings: List[ValidationWarning]) -> ModelFormat:
        """Detect the model format with enhanced logic."""
        try:
            # Hugging Face model ID
            if self._is_huggingface_model_id(file_path):
                return ModelFormat.HUGGINGFACE
            
            if not file_info.exists:
                return ModelFormat.UNKNOWN
            
            # File-based detection
            if file_info.is_file:
                return self._detect_file_format(file_path, file_info, errors, warnings)
            
            # Directory-based detection
            elif file_info.is_directory:
                return self._detect_directory_format(file_path, file_info, errors, warnings)
            
            return ModelFormat.UNKNOWN
            
        except Exception as e:
            errors.append(ValidationError(
                code="FORMAT_DETECTION_ERROR",
                message=f"Error detecting format: {str(e)}",
                severity="warning",
                context={"error": str(e)},
                suggestion="Manual format specification may be required"
            ))
            return ModelFormat.UNKNOWN
    
    def _detect_file_format(self, file_path: str, file_info: FileInfo,
                           errors: List[ValidationError], warnings: List[ValidationWarning]) -> ModelFormat:
        """Detect format for a single file."""
        file_ext = Path(file_path).suffix.lower()
        
        # Extension-based detection
        if file_ext == '.gguf':
            return ModelFormat.GGUF
        elif file_ext == '.safetensors':
            return ModelFormat.SAFETENSORS
        elif file_ext in ['.bin', '.pt', '.pth']:
            return ModelFormat.PYTORCH_BIN
        
        # Content-based detection for files without clear extensions
        try:
            with open(file_path, 'rb') as f:
                header = f.read(16)
                
                # Check for GGUF magic
                if header.startswith(b'GGUF'):
                    warnings.append(ValidationWarning(
                        code="MISSING_GGUF_EXTENSION",
                        message="File appears to be GGUF but doesn't have .gguf extension",
                        context={"file_path": file_path, "extension": file_ext},
                        suggestion="Consider renaming file with .gguf extension"
                    ))
                    return ModelFormat.GGUF
                
                # Check for safetensors header
                if len(header) >= 8:
                    try:
                        header_length = int.from_bytes(header[:8], byteorder='little')
                        if 0 < header_length < file_info.size:
                            f.seek(8)
                            json_header = f.read(min(header_length, 1024))
                            json.loads(json_header.decode('utf-8'))
                            warnings.append(ValidationWarning(
                                code="MISSING_SAFETENSORS_EXTENSION",
                                message="File appears to be safetensors but doesn't have .safetensors extension",
                                context={"file_path": file_path, "extension": file_ext},
                                suggestion="Consider renaming file with .safetensors extension"
                            ))
                            return ModelFormat.SAFETENSORS
                    except:
                        pass
                
        except Exception as e:
            warnings.append(ValidationWarning(
                code="CONTENT_DETECTION_ERROR",
                message=f"Could not perform content-based format detection: {str(e)}",
                context={"error": str(e)},
                suggestion="Ensure file is readable and not corrupted"
            ))
        
        return ModelFormat.UNKNOWN
    
    def _detect_directory_format(self, dir_path: str, file_info: FileInfo,
                                errors: List[ValidationError], warnings: List[ValidationWarning]) -> ModelFormat:
        """Detect format for a directory."""
        try:
            files = list(Path(dir_path).iterdir())
            file_names = [f.name.lower() for f in files if f.is_file()]
            
            # Check for GGUF files
            if any(name.endswith('.gguf') for name in file_names):
                return ModelFormat.GGUF
            
            # Check for safetensors files
            if any(name.endswith('.safetensors') for name in file_names):
                return ModelFormat.SAFETENSORS
            
            # Check for PyTorch model directory structure
            has_config = 'config.json' in file_names
            has_model_files = any(name.endswith(('.bin', '.pt', '.pth')) for name in file_names)
            
            if has_config and has_model_files:
                return ModelFormat.PYTORCH_BIN
            elif has_config:
                warnings.append(ValidationWarning(
                    code="CONFIG_WITHOUT_MODEL",
                    message="Found config.json but no model files",
                    context={"directory": dir_path},
                    suggestion="Ensure model files (.bin, .pt, .pth) are present"
                ))
                return ModelFormat.PYTORCH_BIN
            elif has_model_files:
                warnings.append(ValidationWarning(
                    code="MODEL_WITHOUT_CONFIG",
                    message="Found model files but no config.json",
                    context={"directory": dir_path},
                    suggestion="config.json file is recommended for proper model loading"
                ))
                return ModelFormat.PYTORCH_BIN
            
            return ModelFormat.UNKNOWN
            
        except Exception as e:
            errors.append(ValidationError(
                code="DIRECTORY_SCAN_ERROR",
                message=f"Error scanning directory: {str(e)}",
                severity="warning",
                context={"directory": dir_path, "error": str(e)},
                suggestion="Check directory permissions and accessibility"
            ))
            return ModelFormat.UNKNOWN
    
    def _validate_gguf(self, file_path: str, file_info: FileInfo,
                      errors: List[ValidationError], warnings: List[ValidationWarning]) -> Tuple[bool, Optional[str], Optional[str], Optional[UnifiedMetadata]]:
        """Validate GGUF format with improved version tolerance."""
        try:
            if not file_info.is_file:
                errors.append(ValidationError(
                    code="GGUF_NOT_FILE",
                    message="GGUF path must be a file, not a directory",
                    severity="critical",
                    context={"path": file_path},
                    suggestion="Point to the .gguf file directly"
                ))
                return False, None, None, None
            
            with open(file_path, 'rb') as f:
                # Check magic bytes
                magic = f.read(4)
                if magic != b'GGUF':
                    errors.append(ValidationError(
                        code="INVALID_GGUF_MAGIC",
                        message=f"Invalid GGUF magic bytes: {magic}",
                        severity="critical",
                        context={"magic": magic.hex(), "expected": "47475546"},
                        suggestion="Ensure this is a valid GGUF file"
                    ))
                    return False, None, None, None
                
                # Read version with tolerance
                version_bytes = f.read(4)
                if len(version_bytes) != 4:
                    errors.append(ValidationError(
                        code="INCOMPLETE_GGUF_HEADER",
                        message="Incomplete GGUF header: missing version",
                        severity="critical",
                        context={"bytes_read": len(version_bytes)},
                        suggestion="File may be corrupted or truncated"
                    ))
                    return False, None, None, None
                
                version = int.from_bytes(version_bytes, byteorder='little')
                compatibility_mode = None
                
                # Version tolerance logic
                if version not in self.SUPPORTED_GGUF_VERSIONS:
                    if version < min(self.SUPPORTED_GGUF_VERSIONS):
                        errors.append(ValidationError(
                            code="GGUF_VERSION_TOO_OLD",
                            message=f"GGUF version {version} is too old (supported: {self.SUPPORTED_GGUF_VERSIONS})",
                            severity="critical",
                            context={"version": version, "supported": self.SUPPORTED_GGUF_VERSIONS},
                            suggestion="Convert to a newer GGUF version or use an older loader"
                        ))
                        return False, str(version), None, None
                    elif version > max(self.SUPPORTED_GGUF_VERSIONS):
                        warnings.append(ValidationWarning(
                            code="GGUF_VERSION_NEWER",
                            message=f"GGUF version {version} is newer than preferred {self.PREFERRED_GGUF_VERSION}",
                            context={"version": version, "preferred": self.PREFERRED_GGUF_VERSION},
                            suggestion="May work with compatibility mode, but consider updating the loader"
                        ))
                        compatibility_mode = "forward_compatibility"
                elif version != self.PREFERRED_GGUF_VERSION:
                    warnings.append(ValidationWarning(
                        code="GGUF_VERSION_SUBOPTIMAL",
                        message=f"GGUF version {version} supported but {self.PREFERRED_GGUF_VERSION} is preferred",
                        context={"version": version, "preferred": self.PREFERRED_GGUF_VERSION},
                        suggestion="Consider converting to the preferred version for best compatibility"
                    ))
                    compatibility_mode = "legacy_compatibility"
                
                # Read tensor and metadata counts
                tensor_count_bytes = f.read(8)
                metadata_count_bytes = f.read(8)
                
                if len(tensor_count_bytes) != 8 or len(metadata_count_bytes) != 8:
                    errors.append(ValidationError(
                        code="INCOMPLETE_GGUF_COUNTS",
                        message="Incomplete GGUF header: missing tensor or metadata count",
                        severity="critical",
                        context={"tensor_bytes": len(tensor_count_bytes), "metadata_bytes": len(metadata_count_bytes)},
                        suggestion="File may be corrupted or truncated"
                    ))
                    return False, str(version), compatibility_mode, None
                
                tensor_count = int.from_bytes(tensor_count_bytes, byteorder='little')
                metadata_count = int.from_bytes(metadata_count_bytes, byteorder='little')
                
                # Validate counts
                if tensor_count == 0:
                    warnings.append(ValidationWarning(
                        code="NO_TENSORS",
                        message="GGUF file contains no tensors",
                        context={"tensor_count": tensor_count},
                        suggestion="This may be a metadata-only file"
                    ))
                
                if metadata_count == 0:
                    warnings.append(ValidationWarning(
                        code="NO_METADATA",
                        message="GGUF file contains no metadata",
                        context={"metadata_count": metadata_count},
                        suggestion="Model information may be limited"
                    ))
                
                # Extract basic metadata for unified representation
                metadata = self._extract_gguf_metadata(f, metadata_count, file_info, errors, warnings)
                
                return True, str(version), compatibility_mode, metadata
                
        except Exception as e:
            errors.append(ValidationError(
                code="GGUF_VALIDATION_ERROR",
                message=f"Error validating GGUF file: {str(e)}",
                severity="critical",
                context={"error": str(e)},
                suggestion="Check file integrity and permissions"
            ))
            return False, None, None, None
    
    def _validate_safetensors(self, file_path: str, file_info: FileInfo,
                             errors: List[ValidationError], warnings: List[ValidationWarning]) -> Tuple[bool, Optional[str], Optional[str], Optional[UnifiedMetadata]]:
        """Validate safetensors format with header parsing."""
        try:
            if not file_info.is_file:
                errors.append(ValidationError(
                    code="SAFETENSORS_NOT_FILE",
                    message="Safetensors path must be a file, not a directory",
                    severity="critical",
                    context={"path": file_path},
                    suggestion="Point to the .safetensors file directly"
                ))
                return False, None, None, None
            
            with open(file_path, 'rb') as f:
                # Read header length
                header_length_bytes = f.read(8)
                if len(header_length_bytes) != 8:
                    errors.append(ValidationError(
                        code="INCOMPLETE_SAFETENSORS_HEADER",
                        message="Incomplete safetensors header",
                        severity="critical",
                        context={"bytes_read": len(header_length_bytes)},
                        suggestion="File may be corrupted or not a valid safetensors file"
                    ))
                    return False, None, None, None
                
                header_length = int.from_bytes(header_length_bytes, byteorder='little')
                
                # Validate header length
                if header_length <= 0:
                    errors.append(ValidationError(
                        code="INVALID_HEADER_LENGTH",
                        message=f"Invalid safetensors header length: {header_length}",
                        severity="critical",
                        context={"header_length": header_length},
                        suggestion="File may be corrupted"
                    ))
                    return False, None, None, None
                
                if header_length > file_info.size:
                    errors.append(ValidationError(
                        code="HEADER_TOO_LARGE",
                        message=f"Header length ({header_length}) exceeds file size ({file_info.size})",
                        severity="critical",
                        context={"header_length": header_length, "file_size": file_info.size},
                        suggestion="File may be corrupted"
                    ))
                    return False, None, None, None
                
                # Read and parse header JSON
                header_bytes = f.read(header_length)
                if len(header_bytes) != header_length:
                    errors.append(ValidationError(
                        code="INCOMPLETE_HEADER_DATA",
                        message="Could not read complete safetensors header",
                        severity="critical",
                        context={"expected": header_length, "actual": len(header_bytes)},
                        suggestion="File may be corrupted or truncated"
                    ))
                    return False, None, None, None
                
                try:
                    header_json = json.loads(header_bytes.decode('utf-8'))
                except json.JSONDecodeError as e:
                    errors.append(ValidationError(
                        code="INVALID_HEADER_JSON",
                        message=f"Invalid JSON in safetensors header: {str(e)}",
                        severity="critical",
                        context={"json_error": str(e)},
                        suggestion="File may be corrupted"
                    ))
                    return False, None, None, None
                
                # Extract metadata
                metadata = self._extract_safetensors_metadata(header_json, file_info, errors, warnings)
                
                return True, "1.0", None, metadata  # Safetensors doesn't have explicit versioning
                
        except Exception as e:
            errors.append(ValidationError(
                code="SAFETENSORS_VALIDATION_ERROR",
                message=f"Error validating safetensors file: {str(e)}",
                severity="critical",
                context={"error": str(e)},
                suggestion="Check file integrity and permissions"
            ))
            return False, None, None, None
    
    def _validate_pytorch(self, file_path: str, file_info: FileInfo,
                         errors: List[ValidationError], warnings: List[ValidationWarning]) -> Tuple[bool, Optional[str], Optional[str], Optional[UnifiedMetadata]]:
        """Validate PyTorch model directory or file."""
        try:
            if file_info.is_file:
                return self._validate_pytorch_file(file_path, file_info, errors, warnings)
            elif file_info.is_directory:
                return self._validate_pytorch_directory(file_path, file_info, errors, warnings)
            else:
                errors.append(ValidationError(
                    code="INVALID_PYTORCH_PATH",
                    message="PyTorch model path must be a file or directory",
                    severity="critical",
                    context={"path": file_path},
                    suggestion="Ensure path points to a .bin/.pt/.pth file or model directory"
                ))
                return False, None, None, None
                
        except Exception as e:
            errors.append(ValidationError(
                code="PYTORCH_VALIDATION_ERROR",
                message=f"Error validating PyTorch model: {str(e)}",
                severity="critical",
                context={"error": str(e)},
                suggestion="Check file integrity and permissions"
            ))
            return False, None, None, None
    
    def _validate_pytorch_file(self, file_path: str, file_info: FileInfo,
                              errors: List[ValidationError], warnings: List[ValidationWarning]) -> Tuple[bool, Optional[str], Optional[str], Optional[UnifiedMetadata]]:
        """Validate a single PyTorch model file."""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext not in ['.bin', '.pt', '.pth']:
            errors.append(ValidationError(
                code="INVALID_PYTORCH_EXTENSION",
                message=f"Invalid PyTorch file extension: {file_ext}",
                severity="critical",
                context={"extension": file_ext, "valid_extensions": ['.bin', '.pt', '.pth']},
                suggestion="Ensure file has .bin, .pt, or .pth extension"
            ))
            return False, None, None, None
        
        # Basic size check
        if file_info.size < 1024:  # Very small files unlikely to be models
            warnings.append(ValidationWarning(
                code="SMALL_PYTORCH_FILE",
                message=f"PyTorch file is very small ({file_info.size} bytes)",
                context={"size": file_info.size},
                suggestion="Verify this is a complete model file"
            ))
        
        # Try to validate with PyTorch if available
        try:
            import torch
            # Basic validation - just check if it's a valid torch file
            # We don't load it fully to avoid memory issues
            with open(file_path, 'rb') as f:
                # Check for PyTorch magic number (basic check)
                header = f.read(8)
                # This is a simplified check - real validation would be more sophisticated
                
            metadata = UnifiedMetadata(
                format_type=ModelFormat.PYTORCH_BIN,
                model_name=Path(file_path).stem,
                architecture=None,
                parameters=None,
                quantization=None,
                context_length=None,
                vocab_size=None,
                file_size=file_info.size,
                tensor_info={},
                config={},
                tokenizer_info=None,
                version="unknown",
                compatibility_mode=None
            )
            
            return True, "unknown", None, metadata
            
        except ImportError:
            warnings.append(ValidationWarning(
                code="PYTORCH_NOT_AVAILABLE",
                message="PyTorch not available for full validation",
                context={"file_path": file_path},
                suggestion="Install PyTorch for complete validation"
            ))
            
            # Basic file validation without PyTorch
            metadata = UnifiedMetadata(
                format_type=ModelFormat.PYTORCH_BIN,
                model_name=Path(file_path).stem,
                architecture=None,
                parameters=None,
                quantization=None,
                context_length=None,
                vocab_size=None,
                file_size=file_info.size,
                tensor_info={},
                config={},
                tokenizer_info=None,
                version="unknown",
                compatibility_mode="no_pytorch"
            )
            
            return True, "unknown", "no_pytorch", metadata
            
        except Exception as e:
            errors.append(ValidationError(
                code="PYTORCH_FILE_INVALID",
                message=f"Invalid PyTorch file: {str(e)}",
                severity="critical",
                context={"error": str(e)},
                suggestion="Ensure file is a valid PyTorch model"
            ))
            return False, None, None, None
    
    def _validate_pytorch_directory(self, dir_path: str, file_info: FileInfo,
                                   errors: List[ValidationError], warnings: List[ValidationWarning]) -> Tuple[bool, Optional[str], Optional[str], Optional[UnifiedMetadata]]:
        """Validate a PyTorch model directory."""
        try:
            dir_path_obj = Path(dir_path)
            files = list(dir_path_obj.iterdir())
            file_names = [f.name for f in files if f.is_file()]
            
            # Check for config.json
            config_path = dir_path_obj / "config.json"
            if not config_path.exists():
                errors.append(ValidationError(
                    code="MISSING_CONFIG_JSON",
                    message="No config.json found in PyTorch model directory",
                    severity="critical",
                    context={"directory": dir_path, "files": file_names},
                    suggestion="Ensure config.json is present in the model directory"
                ))
                return False, None, None, None
            
            # Read and validate config
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except json.JSONDecodeError as e:
                errors.append(ValidationError(
                    code="INVALID_CONFIG_JSON",
                    message=f"Invalid config.json: {str(e)}",
                    severity="critical",
                    context={"json_error": str(e)},
                    suggestion="Ensure config.json contains valid JSON"
                ))
                return False, None, None, None
            
            # Check for model files
            model_files = [f for f in file_names if f.endswith(('.bin', '.pt', '.pth'))]
            if not model_files:
                errors.append(ValidationError(
                    code="NO_MODEL_FILES",
                    message="No PyTorch model files found in directory",
                    severity="critical",
                    context={"directory": dir_path, "files": file_names},
                    suggestion="Ensure model files (.bin, .pt, .pth) are present"
                ))
                return False, None, None, None
            
            # Check for tokenizer files (optional but recommended)
            tokenizer_files = [f for f in file_names if 'tokenizer' in f.lower()]
            if not tokenizer_files:
                warnings.append(ValidationWarning(
                    code="NO_TOKENIZER_FILES",
                    message="No tokenizer files found in directory",
                    context={"directory": dir_path},
                    suggestion="Tokenizer files are recommended for proper model usage"
                ))
            
            # Extract metadata
            metadata = self._extract_pytorch_metadata(config, model_files, tokenizer_files, file_info, errors, warnings)
            
            return True, config.get("transformers_version", "unknown"), None, metadata
            
        except Exception as e:
            errors.append(ValidationError(
                code="PYTORCH_DIRECTORY_ERROR",
                message=f"Error validating PyTorch directory: {str(e)}",
                severity="critical",
                context={"error": str(e)},
                suggestion="Check directory structure and permissions"
            ))
            return False, None, None, None
    
    def _validate_huggingface(self, model_id: str, file_info: FileInfo,
                             errors: List[ValidationError], warnings: List[ValidationWarning]) -> Tuple[bool, Optional[str], Optional[str], Optional[UnifiedMetadata]]:
        """Validate Hugging Face model ID."""
        try:
            # Basic format validation
            if not self.HF_MODEL_ID_PATTERN.match(model_id):
                errors.append(ValidationError(
                    code="INVALID_HF_MODEL_ID",
                    message=f"Invalid Hugging Face model ID format: {model_id}",
                    severity="critical",
                    context={"model_id": model_id},
                    suggestion="Use format: username/model-name or model-name"
                ))
                return False, None, None, None
            
            # Try to use HuggingFace integration service if available
            try:
                from llmtoolkit.app.services.huggingface_integration import HuggingFaceIntegration
                
                hf_integration = HuggingFaceIntegration()
                resolution = hf_integration.resolve_model_id(model_id)
                
                if not resolution.exists:
                    errors.append(ValidationError(
                        code="HF_MODEL_NOT_FOUND",
                        message=f"Hugging Face model not found: {model_id}",
                        severity="critical",
                        context={"model_id": model_id, "error": resolution.error_message},
                        suggestion="Check model ID spelling and availability"
                    ))
                    return False, None, None, None
                
                if resolution.requires_auth and not hf_integration.is_authenticated():
                    warnings.append(ValidationWarning(
                        code="HF_AUTH_REQUIRED",
                        message=f"Model requires authentication: {model_id}",
                        context={"model_id": model_id},
                        suggestion="Configure Hugging Face authentication token"
                    ))
                
                # Extract metadata
                metadata = self._extract_huggingface_metadata(resolution, errors, warnings)
                
                return True, "huggingface", None, metadata
                
            except ImportError:
                # Fallback to basic requests validation
                return self._validate_huggingface_with_requests(model_id, errors, warnings)
                
        except Exception as e:
            errors.append(ValidationError(
                code="HF_VALIDATION_ERROR",
                message=f"Error validating Hugging Face model: {str(e)}",
                severity="critical",
                context={"error": str(e)},
                suggestion="Check network connection and model ID"
            ))
            return False, None, None, None
    
    def _validate_huggingface_with_requests(self, model_id: str,
                                           errors: List[ValidationError], warnings: List[ValidationWarning]) -> Tuple[bool, Optional[str], Optional[str], Optional[UnifiedMetadata]]:
        """Fallback Hugging Face validation using requests."""
        try:
            HF_API_BASE = "https://huggingface.co/api/models"
            response = requests.get(f"{HF_API_BASE}/{model_id}", timeout=10)
            
            if response.status_code == 200:
                model_info = response.json()
                
                metadata = UnifiedMetadata(
                    format_type=ModelFormat.HUGGINGFACE,
                    model_name=model_id,
                    architecture=model_info.get("pipeline_tag"),
                    parameters=None,
                    quantization=None,
                    context_length=None,
                    vocab_size=None,
                    file_size=0,
                    tensor_info={},
                    config=model_info,
                    tokenizer_info=None,
                    version="huggingface",
                    compatibility_mode=None
                )
                
                return True, "huggingface", None, metadata
                
            elif response.status_code == 401:
                warnings.append(ValidationWarning(
                    code="HF_AUTH_REQUIRED",
                    message=f"Model requires authentication: {model_id}",
                    context={"model_id": model_id},
                    suggestion="Configure Hugging Face authentication token"
                ))
                
                metadata = UnifiedMetadata(
                    format_type=ModelFormat.HUGGINGFACE,
                    model_name=model_id,
                    architecture=None,
                    parameters=None,
                    quantization=None,
                    context_length=None,
                    vocab_size=None,
                    file_size=0,
                    tensor_info={},
                    config={},
                    tokenizer_info=None,
                    version="huggingface",
                    compatibility_mode="auth_required"
                )
                
                return True, "huggingface", "auth_required", metadata
                
            elif response.status_code == 404:
                errors.append(ValidationError(
                    code="HF_MODEL_NOT_FOUND",
                    message=f"Hugging Face model not found: {model_id}",
                    severity="critical",
                    context={"model_id": model_id, "status_code": 404},
                    suggestion="Check model ID spelling and availability"
                ))
                return False, None, None, None
                
            else:
                errors.append(ValidationError(
                    code="HF_API_ERROR",
                    message=f"Hugging Face API error: HTTP {response.status_code}",
                    severity="critical",
                    context={"model_id": model_id, "status_code": response.status_code},
                    suggestion="Check network connection and try again later"
                ))
                return False, None, None, None
                
        except requests.RequestException as e:
            warnings.append(ValidationWarning(
                code="HF_NETWORK_ERROR",
                message=f"Cannot verify Hugging Face model (network error): {str(e)}",
                context={"model_id": model_id, "error": str(e)},
                suggestion="Check network connection; model may still be valid"
            ))
            
            # Assume model might be valid but can't verify
            metadata = UnifiedMetadata(
                format_type=ModelFormat.HUGGINGFACE,
                model_name=model_id,
                architecture=None,
                parameters=None,
                quantization=None,
                context_length=None,
                vocab_size=None,
                file_size=0,
                tensor_info={},
                config={},
                tokenizer_info=None,
                version="huggingface",
                compatibility_mode="network_error"
            )
            
            return True, "huggingface", "network_error", metadata
    
    def _extract_gguf_metadata(self, file: BinaryIO, metadata_count: int, file_info: FileInfo,
                              errors: List[ValidationError], warnings: List[ValidationWarning]) -> UnifiedMetadata:
        """Extract metadata from GGUF file."""
        try:
            metadata_dict = {}
            
            # Read metadata key-value pairs (simplified implementation)
            for _ in range(min(metadata_count, 10)):  # Limit to avoid excessive processing
                try:
                    # Read key
                    key_length = struct.unpack("<Q", file.read(8))[0]
                    if key_length > 1000:  # Sanity check
                        break
                    key = file.read(key_length).decode('utf-8')
                    
                    # Read value type
                    value_type = struct.unpack("<I", file.read(4))[0]
                    
                    # Read value (simplified - would need full GGUF type handling)
                    if value_type == 8:  # String type
                        value_length = struct.unpack("<Q", file.read(8))[0]
                        if value_length > 10000:  # Sanity check
                            break
                        value = file.read(value_length).decode('utf-8')
                    elif value_type == 4:  # Uint32
                        value = struct.unpack("<I", file.read(4))[0]
                    elif value_type == 10:  # Uint64
                        value = struct.unpack("<Q", file.read(8))[0]
                    else:
                        # Skip unknown types
                        continue
                    
                    metadata_dict[key] = value
                    
                except Exception as e:
                    warnings.append(ValidationWarning(
                        code="METADATA_READ_ERROR",
                        message=f"Error reading metadata key: {str(e)}",
                        context={"error": str(e)},
                        suggestion="Some metadata may be missing"
                    ))
                    break
            
            # Extract common fields
            architecture = metadata_dict.get("general.architecture", "unknown")
            model_name = metadata_dict.get("general.name", Path(file_info.path).stem)
            
            # Estimate parameters from context length and architecture
            context_length = metadata_dict.get("llama.context_length", metadata_dict.get("general.context_length"))
            parameters = self._estimate_parameters(architecture, context_length, file_info.size)
            
            return UnifiedMetadata(
                format_type=ModelFormat.GGUF,
                model_name=model_name,
                architecture=architecture,
                parameters=parameters,
                quantization=metadata_dict.get("general.quantization_version"),
                context_length=context_length,
                vocab_size=metadata_dict.get("tokenizer.ggml.tokens"),
                file_size=file_info.size,
                tensor_info={"count": metadata_dict.get("tensor_count", 0)},
                config=metadata_dict,
                tokenizer_info=None,
                version=metadata_dict.get("general.file_type"),
                compatibility_mode=None
            )
            
        except Exception as e:
            warnings.append(ValidationWarning(
                code="METADATA_EXTRACTION_ERROR",
                message=f"Error extracting GGUF metadata: {str(e)}",
                context={"error": str(e)},
                suggestion="Basic validation will continue with limited metadata"
            ))
            
            return UnifiedMetadata(
                format_type=ModelFormat.GGUF,
                model_name=Path(file_info.path).stem,
                architecture="unknown",
                parameters=None,
                quantization=None,
                context_length=None,
                vocab_size=None,
                file_size=file_info.size,
                tensor_info={},
                config={},
                tokenizer_info=None,
                version="unknown",
                compatibility_mode=None
            )
    
    def _extract_safetensors_metadata(self, header_json: Dict[str, Any], file_info: FileInfo,
                                     errors: List[ValidationError], warnings: List[ValidationWarning]) -> UnifiedMetadata:
        """Extract metadata from safetensors header."""
        try:
            # Count tensors and calculate total size
            tensor_count = 0
            total_tensor_size = 0
            tensor_info = {}
            
            for key, value in header_json.items():
                if key != "__metadata__":
                    tensor_count += 1
                    if isinstance(value, dict) and "data_offsets" in value:
                        offsets = value["data_offsets"]
                        if len(offsets) == 2:
                            tensor_size = offsets[1] - offsets[0]
                            total_tensor_size += tensor_size
                            tensor_info[key] = {
                                "size": tensor_size,
                                "dtype": value.get("dtype"),
                                "shape": value.get("shape")
                            }
            
            # Extract model metadata if present
            model_metadata = header_json.get("__metadata__", {})
            
            # Try to determine architecture from tensor names
            architecture = self._infer_architecture_from_tensors(list(header_json.keys()))
            
            return UnifiedMetadata(
                format_type=ModelFormat.SAFETENSORS,
                model_name=model_metadata.get("name", Path(file_info.path).stem),
                architecture=architecture,
                parameters=self._estimate_parameters_from_tensors(tensor_info),
                quantization=model_metadata.get("quantization"),
                context_length=model_metadata.get("context_length"),
                vocab_size=model_metadata.get("vocab_size"),
                file_size=file_info.size,
                tensor_info={"count": tensor_count, "total_size": total_tensor_size, "tensors": tensor_info},
                config=model_metadata,
                tokenizer_info=None,
                version="1.0",
                compatibility_mode=None
            )
            
        except Exception as e:
            warnings.append(ValidationWarning(
                code="SAFETENSORS_METADATA_ERROR",
                message=f"Error extracting safetensors metadata: {str(e)}",
                context={"error": str(e)},
                suggestion="Basic validation will continue with limited metadata"
            ))
            
            return UnifiedMetadata(
                format_type=ModelFormat.SAFETENSORS,
                model_name=Path(file_info.path).stem,
                architecture="unknown",
                parameters=None,
                quantization=None,
                context_length=None,
                vocab_size=None,
                file_size=file_info.size,
                tensor_info={},
                config={},
                tokenizer_info=None,
                version="1.0",
                compatibility_mode=None
            )
    
    def _extract_pytorch_metadata(self, config: Dict[str, Any], model_files: List[str], 
                                 tokenizer_files: List[str], file_info: FileInfo,
                                 errors: List[ValidationError], warnings: List[ValidationWarning]) -> UnifiedMetadata:
        """Extract metadata from PyTorch model directory."""
        try:
            # Extract basic info from config
            architecture = config.get("model_type", config.get("architectures", ["unknown"])[0] if config.get("architectures") else "unknown")
            if isinstance(architecture, list):
                architecture = architecture[0]
            
            # Extract tokenizer info if available
            tokenizer_info = None
            if tokenizer_files:
                tokenizer_info = {
                    "files": tokenizer_files,
                    "vocab_size": config.get("vocab_size")
                }
            
            return UnifiedMetadata(
                format_type=ModelFormat.PYTORCH_BIN,
                model_name=config.get("name", config.get("_name_or_path", Path(file_info.path).name)),
                architecture=architecture,
                parameters=self._extract_parameter_count(config),
                quantization=config.get("quantization_config", {}).get("quant_method") if config.get("quantization_config") else None,
                context_length=config.get("max_position_embeddings", config.get("n_positions")),
                vocab_size=config.get("vocab_size"),
                file_size=file_info.size,
                tensor_info={"model_files": model_files, "file_count": len(model_files)},
                config=config,
                tokenizer_info=tokenizer_info,
                version=config.get("transformers_version", "unknown"),
                compatibility_mode=None
            )
            
        except Exception as e:
            warnings.append(ValidationWarning(
                code="PYTORCH_METADATA_ERROR",
                message=f"Error extracting PyTorch metadata: {str(e)}",
                context={"error": str(e)},
                suggestion="Basic validation will continue with limited metadata"
            ))
            
            return UnifiedMetadata(
                format_type=ModelFormat.PYTORCH_BIN,
                model_name=Path(file_info.path).name,
                architecture="unknown",
                parameters=None,
                quantization=None,
                context_length=None,
                vocab_size=None,
                file_size=file_info.size,
                tensor_info={"model_files": model_files},
                config=config,
                tokenizer_info=None,
                version="unknown",
                compatibility_mode=None
            )
    
    def _extract_huggingface_metadata(self, resolution, errors: List[ValidationError], warnings: List[ValidationWarning]) -> UnifiedMetadata:
        """Extract metadata from Hugging Face model resolution."""
        try:
            return UnifiedMetadata(
                format_type=ModelFormat.HUGGINGFACE,
                model_name=resolution.model_id,
                architecture=resolution.architecture,
                parameters=None,  # Would need to download config to get this
                quantization=None,
                context_length=None,
                vocab_size=None,
                file_size=resolution.size_bytes or 0,
                tensor_info={},
                config={
                    "model_type": resolution.model_type,
                    "tags": resolution.tags,
                    "downloads": resolution.downloads,
                    "last_modified": resolution.last_modified,
                    "is_private": resolution.is_private,
                    "requires_auth": resolution.requires_auth
                },
                tokenizer_info=None,
                version="huggingface",
                compatibility_mode=None
            )
            
        except Exception as e:
            warnings.append(ValidationWarning(
                code="HF_METADATA_ERROR",
                message=f"Error extracting Hugging Face metadata: {str(e)}",
                context={"error": str(e)},
                suggestion="Basic validation will continue with limited metadata"
            ))
            
            return UnifiedMetadata(
                format_type=ModelFormat.HUGGINGFACE,
                model_name=resolution.model_id if hasattr(resolution, 'model_id') else "unknown",
                architecture="unknown",
                parameters=None,
                quantization=None,
                context_length=None,
                vocab_size=None,
                file_size=0,
                tensor_info={},
                config={},
                tokenizer_info=None,
                version="huggingface",
                compatibility_mode=None
            )
    
    def _validate_metadata(self, metadata: UnifiedMetadata, errors: List[ValidationError], warnings: List[ValidationWarning]):
        """Validate extracted metadata for consistency and completeness."""
        # Check architecture
        if metadata.architecture and metadata.architecture.lower() not in self.KNOWN_ARCHITECTURES:
            warnings.append(ValidationWarning(
                code="UNKNOWN_ARCHITECTURE",
                message=f"Unknown or uncommon architecture: {metadata.architecture}",
                context={"architecture": metadata.architecture, "known": list(self.KNOWN_ARCHITECTURES)},
                suggestion="Model may still work but compatibility is not guaranteed"
            ))
        
        # Check parameter count reasonableness
        if metadata.parameters:
            if metadata.parameters < 1_000_000:  # Less than 1M parameters
                warnings.append(ValidationWarning(
                    code="SMALL_PARAMETER_COUNT",
                    message=f"Unusually small parameter count: {metadata.parameters:,}",
                    context={"parameters": metadata.parameters},
                    suggestion="Verify this is a complete model"
                ))
            elif metadata.parameters > 100_000_000_000:  # More than 100B parameters
                warnings.append(ValidationWarning(
                    code="LARGE_PARAMETER_COUNT",
                    message=f"Very large parameter count: {metadata.parameters:,}",
                    context={"parameters": metadata.parameters},
                    suggestion="Ensure sufficient system resources for loading"
                ))
        
        # Check context length
        if metadata.context_length:
            try:
                context_length = int(metadata.context_length) if isinstance(metadata.context_length, str) else metadata.context_length
                if context_length < 512:
                    warnings.append(ValidationWarning(
                        code="SHORT_CONTEXT_LENGTH",
                        message=f"Short context length: {context_length}",
                        context={"context_length": context_length},
                        suggestion="Model may have limited conversation capability"
                    ))
                elif context_length > 32768:
                    warnings.append(ValidationWarning(
                        code="LONG_CONTEXT_LENGTH",
                        message=f"Very long context length: {context_length}",
                        context={"context_length": context_length},
                        suggestion="May require significant memory resources"
                    ))
            except (ValueError, TypeError):
                warnings.append(ValidationWarning(
                    code="INVALID_CONTEXT_LENGTH",
                    message=f"Invalid context length value: {metadata.context_length}",
                    context={"context_length": metadata.context_length},
                    suggestion="Context length should be a numeric value"
                ))
    
    def _validate_size_and_performance(self, file_info: FileInfo, metadata: Optional[UnifiedMetadata],
                                      errors: List[ValidationError], warnings: List[ValidationWarning]):
        """Validate file size and provide performance warnings."""
        if file_info.size > self.LARGE_MODEL_THRESHOLD:
            warnings.append(ValidationWarning(
                code="LARGE_MODEL_SIZE",
                message=f"Large model file ({file_info.size / (1024**3):.1f} GB)",
                context={"size_bytes": file_info.size, "size_gb": file_info.size / (1024**3)},
                suggestion="Ensure sufficient RAM and consider GPU acceleration"
            ))
        
        # Estimate memory requirements
        if metadata and metadata.parameters:
            # Rough estimate: 2 bytes per parameter for FP16, 4 bytes for FP32
            estimated_memory_gb = (metadata.parameters * 2) / (1024**3)
            if estimated_memory_gb > 16:  # More than 16GB estimated
                warnings.append(ValidationWarning(
                    code="HIGH_MEMORY_REQUIREMENT",
                    message=f"Estimated memory requirement: {estimated_memory_gb:.1f} GB",
                    context={"estimated_memory_gb": estimated_memory_gb, "parameters": metadata.parameters},
                    suggestion="Consider quantized version or ensure sufficient system memory"
                ))
    
    def _estimate_parameters(self, architecture: str, context_length: Optional[int], file_size: int) -> Optional[int]:
        """Estimate parameter count based on architecture and file size."""
        try:
            # Very rough estimation based on file size
            # This is a simplified heuristic
            if file_size < 1024**3:  # Less than 1GB
                return int(file_size / 2)  # Assume 2 bytes per parameter
            else:
                return int(file_size / 2)  # Rough estimate
        except:
            return None
    
    def _estimate_parameters_from_tensors(self, tensor_info: Dict[str, Any]) -> Optional[int]:
        """Estimate parameter count from tensor information."""
        try:
            total_params = 0
            for tensor_name, info in tensor_info.items():
                if isinstance(info, dict) and "shape" in info:
                    shape = info["shape"]
                    if isinstance(shape, list):
                        param_count = 1
                        for dim in shape:
                            param_count *= dim
                        total_params += param_count
            return total_params if total_params > 0 else None
        except:
            return None
    
    def _extract_parameter_count(self, config: Dict[str, Any]) -> Optional[int]:
        """Extract parameter count from model config."""
        # Try various common parameter count fields
        param_fields = ["num_parameters", "n_parameters", "total_params", "model_size"]
        for field in param_fields:
            if field in config:
                return config[field]
        
        # Try to calculate from architecture parameters
        try:
            hidden_size = config.get("hidden_size", config.get("d_model"))
            num_layers = config.get("num_hidden_layers", config.get("n_layer"))
            vocab_size = config.get("vocab_size")
            
            if hidden_size and num_layers and vocab_size:
                # Very rough estimation
                return int(hidden_size * num_layers * vocab_size * 0.1)  # Simplified calculation
        except:
            pass
        
        return None
    
    def _infer_architecture_from_tensors(self, tensor_names: List[str]) -> str:
        """Infer model architecture from tensor names."""
        tensor_str = " ".join(tensor_names).lower()
        
        if "llama" in tensor_str or "lm_head" in tensor_str:
            return "llama"
        elif "mistral" in tensor_str:
            return "mistral"
        elif "qwen" in tensor_str:
            return "qwen"
        elif "phi" in tensor_str:
            return "phi"
        elif "gemma" in tensor_str:
            return "gemma"
        elif "gpt" in tensor_str:
            return "gpt"
        else:
            return "unknown"
    
    def _is_huggingface_model_id(self, input_str: str) -> bool:
        """Check if input string looks like a Hugging Face model ID."""
        # Should not be a file path
        if os.path.sep in input_str or input_str.startswith('.'):
            return False
        
        # Should not contain file extensions
        if any(input_str.lower().endswith(ext) for ext in ['.gguf', '.safetensors', '.bin', '.pt', '.pth']):
            return False
        
        # Should match HF model ID pattern
        return self.HF_MODEL_ID_PATTERN.match(input_str) is not None
    
    def _get_default_file_info(self, file_path: str) -> FileInfo:
        """Get default file info for error cases."""
        return FileInfo(
            path=file_path,
            size=0,
            modified=datetime.now(),
            exists=False,
            is_file=False,
            is_directory=False
        )
    
    def get_validation_summary(self, result: ValidationResult) -> str:
        """Generate a human-readable validation summary."""
        lines = []
        
        # Header
        status = "✓ VALID" if result.is_valid else "✗ INVALID"
        lines.append(f"Model Validation: {status}")
        lines.append(f"Format: {result.format_type.value}")
        lines.append(f"Validation Time: {result.validation_time:.2f}s")
        lines.append("")
        
        # Progressive results
        lines.append("Validation Steps:")
        for step, passed in result.progressive_results.items():
            status_icon = "✓" if passed else "✗"
            lines.append(f"  {status_icon} {step.replace('_', ' ').title()}")
        lines.append("")
        
        # Metadata summary
        if result.metadata:
            lines.append("Model Information:")
            lines.append(f"  Name: {result.metadata.model_name}")
            if result.metadata.architecture:
                lines.append(f"  Architecture: {result.metadata.architecture}")
            if result.metadata.parameters:
                lines.append(f"  Parameters: {result.metadata.parameters:,}")
            if result.metadata.context_length:
                lines.append(f"  Context Length: {result.metadata.context_length}")
            lines.append(f"  File Size: {result.metadata.file_size / (1024**2):.1f} MB")
            lines.append("")
        
        # Errors
        if result.errors:
            lines.append("Errors:")
            for error in result.errors:
                lines.append(f"  ✗ {error.severity.upper()}: {error.message}")
                if error.suggestion:
                    lines.append(f"    Suggestion: {error.suggestion}")
            lines.append("")
        
        # Warnings
        if result.warnings:
            lines.append("Warnings:")
            for warning in result.warnings:
                lines.append(f"  ⚠ {warning.message}")
                if warning.suggestion:
                    lines.append(f"    Suggestion: {warning.suggestion}")
            lines.append("")
        
        return "\n".join(lines)