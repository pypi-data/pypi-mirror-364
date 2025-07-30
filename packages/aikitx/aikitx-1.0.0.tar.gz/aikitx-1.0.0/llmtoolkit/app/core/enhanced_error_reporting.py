"""
Enhanced Error Reporting Engine

This module provides comprehensive error reporting and analysis for the Universal Model Loader,
with format-aware root cause analysis, context-aware error messages, and actionable resolution
suggestions for all supported model formats (GGUF, safetensors, PyTorch, Hugging Face).

Requirements addressed: 3.1, 3.2, 3.3, 3.4
"""

import logging
import traceback
import time
import json
import re
import psutil
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass, field
from enum import Enum

from .universal_format_detector import ModelFormat
from .error_handling import (
    ErrorCategory, ErrorSeverity, ErrorContext, ErrorSolution, 
    RecoveryAction, ClassifiedError
)


class ErrorType(Enum):
    """Specific error types for enhanced categorization."""
    # Format-specific errors
    GGUF_VERSION_UNSUPPORTED = "gguf_version_unsupported"
    GGUF_CORRUPTED = "gguf_corrupted"
    SAFETENSORS_INVALID_HEADER = "safetensors_invalid_header"
    SAFETENSORS_CORRUPTED = "safetensors_corrupted"
    PYTORCH_INVALID_FORMAT = "pytorch_invalid_format"
    PYTORCH_MISSING_CONFIG = "pytorch_missing_config"
    
    # Hugging Face specific errors
    HF_MODEL_NOT_FOUND = "hf_model_not_found"
    HF_AUTH_REQUIRED = "hf_auth_required"
    HF_AUTH_INVALID = "hf_auth_invalid"
    HF_DOWNLOAD_FAILED = "hf_download_failed"
    HF_NETWORK_ERROR = "hf_network_error"
    HF_QUOTA_EXCEEDED = "hf_quota_exceeded"
    
    # Backend errors
    BACKEND_NOT_AVAILABLE = "backend_not_available"
    BACKEND_INCOMPATIBLE = "backend_incompatible"
    BACKEND_INITIALIZATION_FAILED = "backend_initialization_failed"
    
    # Hardware/Memory errors
    INSUFFICIENT_MEMORY = "insufficient_memory"
    INSUFFICIENT_VRAM = "insufficient_vram"
    GPU_NOT_AVAILABLE = "gpu_not_available"
    CUDA_ERROR = "cuda_error"
    
    # File system errors
    FILE_NOT_FOUND = "file_not_found"
    PERMISSION_DENIED = "permission_denied"
    DISK_SPACE_INSUFFICIENT = "disk_space_insufficient"
    
    # Network errors
    CONNECTION_TIMEOUT = "connection_timeout"
    CONNECTION_REFUSED = "connection_refused"
    DNS_RESOLUTION_FAILED = "dns_resolution_failed"
    
    # Generic errors
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class LoadingContext:
    """Extended context information for model loading operations."""
    model_format: Optional[ModelFormat] = None
    model_path: Optional[str] = None
    model_id: Optional[str] = None
    backend_name: Optional[str] = None
    operation: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    system_info: Optional[Dict[str, Any]] = None
    hardware_info: Optional[Dict[str, Any]] = None
    memory_info: Optional[Dict[str, Any]] = None
    network_info: Optional[Dict[str, Any]] = None
    additional_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResolutionSuggestion:
    """Actionable resolution suggestion for an error."""
    title: str
    description: str
    action_type: RecoveryAction
    steps: List[str]
    estimated_time: str
    difficulty: str  # "Easy", "Intermediate", "Advanced"
    success_probability: float
    automatic: bool = False
    requires_restart: bool = False
    format_specific: bool = False
    prerequisites: List[str] = field(default_factory=list)
    links: List[str] = field(default_factory=list)


@dataclass
class ErrorAnalysis:
    """Comprehensive error analysis result."""
    error_id: str
    error_type: ErrorType
    category: ErrorCategory
    severity: ErrorSeverity
    root_cause: str
    user_friendly_message: str
    technical_details: str
    context: LoadingContext
    affected_components: List[str]
    resolution_suggestions: List[ResolutionSuggestion]
    similar_errors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class FormatAwareErrorAnalyzer:
    """Analyzes errors with format-specific knowledge."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._error_patterns = self._initialize_error_patterns()
        self._format_specific_analyzers = {
            ModelFormat.GGUF: self._analyze_gguf_error,
            ModelFormat.SAFETENSORS: self._analyze_safetensors_error,
            ModelFormat.PYTORCH_BIN: self._analyze_pytorch_error,
            ModelFormat.HUGGINGFACE: self._analyze_huggingface_error
        } 
   
    def analyze_loading_error(self, error: Exception, context: LoadingContext) -> ErrorAnalysis:
        """
        Perform comprehensive error analysis with format-aware root cause analysis.
        
        Args:
            error: The exception that occurred
            context: Context information about the loading operation
            
        Returns:
            ErrorAnalysis with detailed analysis and resolution suggestions
        """
        # Generate unique error ID
        error_id = f"ERR_{int(time.time())}_{hash(str(error))}"
        
        # Determine error type and category
        error_type = self._classify_error_type(error, context)
        category = self._determine_category(error_type, error, context)
        severity = self._assess_severity(error_type, error, context)
        
        # Perform root cause analysis
        root_cause = self._analyze_root_cause(error, context, error_type)
        
        # Generate user-friendly message
        user_message = self._generate_user_message(error, context, error_type)
        
        # Extract technical details
        technical_details = self._extract_technical_details(error, context)
        
        # Identify affected components
        affected_components = self._identify_affected_components(error, context)
        
        # Generate resolution suggestions
        resolution_suggestions = self._generate_resolution_suggestions(error, context, error_type)
        
        # Find similar errors
        similar_errors = self._find_similar_errors(error, context)
        
        return ErrorAnalysis(
            error_id=error_id,
            error_type=error_type,
            category=category,
            severity=severity,
            root_cause=root_cause,
            user_friendly_message=user_message,
            technical_details=technical_details,
            context=context,
            affected_components=affected_components,
            resolution_suggestions=resolution_suggestions,
            similar_errors=similar_errors
        )
    
    def _classify_error_type(self, error: Exception, context: LoadingContext) -> ErrorType:
        """Classify the specific error type based on error and context."""
        error_str = str(error).lower()
        error_class = type(error).__name__.lower()
        
        # Format-specific error classification
        if context.model_format:
            format_analyzer = self._format_specific_analyzers.get(context.model_format)
            if format_analyzer:
                format_error_type = format_analyzer(error, context)
                if format_error_type != ErrorType.UNKNOWN_ERROR:
                    return format_error_type
        
        # Hugging Face specific errors
        if "huggingface" in error_str or "hf_hub" in error_str:
            return self._classify_huggingface_error(error, context)
        
        # Backend errors
        if context.backend_name and any(keyword in error_str for keyword in ['backend', 'import', 'module']):
            return ErrorType.BACKEND_NOT_AVAILABLE
        
        # Memory errors - check VRAM first, then general memory
        if any(keyword in error_str for keyword in ['vram', 'gpu memory']) or \
           ('cuda' in error_str and 'memory' in error_str):
            return ErrorType.INSUFFICIENT_VRAM
        elif any(keyword in error_str for keyword in ['memory', 'oom', 'allocation', 'ram']):
            return ErrorType.INSUFFICIENT_MEMORY
        
        # Hardware errors
        if any(keyword in error_str for keyword in ['cuda', 'gpu', 'device']):
            return ErrorType.CUDA_ERROR
        
        # File system errors
        if "filenotfounderror" in error_class or "no such file" in error_str:
            return ErrorType.FILE_NOT_FOUND
        elif "permissionerror" in error_class or "permission denied" in error_str:
            return ErrorType.PERMISSION_DENIED
        
        # Network errors
        if any(keyword in error_str for keyword in ['timeout', 'connection', 'network']):
            return ErrorType.CONNECTION_TIMEOUT
        
        return ErrorType.UNKNOWN_ERROR
    
    def _analyze_gguf_error(self, error: Exception, context: LoadingContext) -> ErrorType:
        """Analyze GGUF-specific errors."""
        error_str = str(error).lower()
        
        if ("version" in error_str and ("unsupported" in error_str or "not supported" in error_str)) or \
           ("gguf version" in error_str):
            return ErrorType.GGUF_VERSION_UNSUPPORTED
        elif any(keyword in error_str for keyword in ['corrupted', 'invalid header', 'malformed']) or \
             ('invalid' in error_str and 'gguf' in error_str):
            return ErrorType.GGUF_CORRUPTED
        
        return ErrorType.UNKNOWN_ERROR
    
    def _analyze_safetensors_error(self, error: Exception, context: LoadingContext) -> ErrorType:
        """Analyze safetensors-specific errors."""
        error_str = str(error).lower()
        
        if "header" in error_str and ("invalid" in error_str or "corrupted" in error_str):
            return ErrorType.SAFETENSORS_INVALID_HEADER
        elif any(keyword in error_str for keyword in ['corrupted', 'malformed', 'invalid format']):
            return ErrorType.SAFETENSORS_CORRUPTED
        
        return ErrorType.UNKNOWN_ERROR
    
    def _analyze_pytorch_error(self, error: Exception, context: LoadingContext) -> ErrorType:
        """Analyze PyTorch-specific errors."""
        error_str = str(error).lower()
        
        if "config.json" in error_str and ("not found" in error_str or "missing" in error_str):
            return ErrorType.PYTORCH_MISSING_CONFIG
        elif any(keyword in error_str for keyword in ['invalid format', 'corrupted', 'malformed']):
            return ErrorType.PYTORCH_INVALID_FORMAT
        
        return ErrorType.UNKNOWN_ERROR
    
    def _analyze_huggingface_error(self, error: Exception, context: LoadingContext) -> ErrorType:
        """Analyze Hugging Face-specific errors."""
        error_str = str(error).lower()
        
        if "404" in error_str or "not found" in error_str:
            return ErrorType.HF_MODEL_NOT_FOUND
        elif "401" in error_str or "unauthorized" in error_str:
            return ErrorType.HF_AUTH_REQUIRED
        elif "403" in error_str or "forbidden" in error_str:
            return ErrorType.HF_AUTH_INVALID
        elif "429" in error_str or "quota" in error_str:
            return ErrorType.HF_QUOTA_EXCEEDED
        elif any(keyword in error_str for keyword in ['download', 'fetch', 'retrieve']):
            return ErrorType.HF_DOWNLOAD_FAILED
        elif any(keyword in error_str for keyword in ['network', 'connection', 'timeout']):
            return ErrorType.HF_NETWORK_ERROR
        
        return ErrorType.UNKNOWN_ERROR
    
    def _classify_huggingface_error(self, error: Exception, context: LoadingContext) -> ErrorType:
        """Classify Hugging Face specific errors."""
        error_str = str(error).lower()
        
        # Check for HTTP status codes in error message
        if "404" in error_str:
            return ErrorType.HF_MODEL_NOT_FOUND
        elif "401" in error_str:
            return ErrorType.HF_AUTH_REQUIRED
        elif "403" in error_str:
            return ErrorType.HF_AUTH_INVALID
        elif "429" in error_str:
            return ErrorType.HF_QUOTA_EXCEEDED
        
        # Check for specific error patterns
        if "repository not found" in error_str or "model not found" in error_str:
            return ErrorType.HF_MODEL_NOT_FOUND
        elif "authentication" in error_str or "token" in error_str:
            return ErrorType.HF_AUTH_REQUIRED
        elif "download" in error_str or "fetch" in error_str:
            return ErrorType.HF_DOWNLOAD_FAILED
        elif "network" in error_str or "connection" in error_str:
            return ErrorType.HF_NETWORK_ERROR
        
        return ErrorType.UNKNOWN_ERROR
    
    def _determine_category(self, error_type: ErrorType, error: Exception, context: LoadingContext) -> ErrorCategory:
        """Determine the error category based on error type."""
        category_mapping = {
            ErrorType.GGUF_VERSION_UNSUPPORTED: ErrorCategory.MODEL_LOADING,
            ErrorType.GGUF_CORRUPTED: ErrorCategory.MODEL_LOADING,
            ErrorType.SAFETENSORS_INVALID_HEADER: ErrorCategory.MODEL_LOADING,
            ErrorType.SAFETENSORS_CORRUPTED: ErrorCategory.MODEL_LOADING,
            ErrorType.PYTORCH_INVALID_FORMAT: ErrorCategory.MODEL_LOADING,
            ErrorType.PYTORCH_MISSING_CONFIG: ErrorCategory.MODEL_LOADING,
            ErrorType.HF_MODEL_NOT_FOUND: ErrorCategory.NETWORK,
            ErrorType.HF_AUTH_REQUIRED: ErrorCategory.CONFIGURATION,
            ErrorType.HF_AUTH_INVALID: ErrorCategory.CONFIGURATION,
            ErrorType.HF_DOWNLOAD_FAILED: ErrorCategory.NETWORK,
            ErrorType.HF_NETWORK_ERROR: ErrorCategory.NETWORK,
            ErrorType.HF_QUOTA_EXCEEDED: ErrorCategory.NETWORK,
            ErrorType.BACKEND_NOT_AVAILABLE: ErrorCategory.INSTALLATION,
            ErrorType.BACKEND_INCOMPATIBLE: ErrorCategory.INSTALLATION,
            ErrorType.BACKEND_INITIALIZATION_FAILED: ErrorCategory.BACKEND,
            ErrorType.INSUFFICIENT_MEMORY: ErrorCategory.MEMORY,
            ErrorType.INSUFFICIENT_VRAM: ErrorCategory.MEMORY,
            ErrorType.GPU_NOT_AVAILABLE: ErrorCategory.HARDWARE,
            ErrorType.CUDA_ERROR: ErrorCategory.HARDWARE,
            ErrorType.FILE_NOT_FOUND: ErrorCategory.FILESYSTEM,
            ErrorType.PERMISSION_DENIED: ErrorCategory.FILESYSTEM,
            ErrorType.DISK_SPACE_INSUFFICIENT: ErrorCategory.FILESYSTEM,
            ErrorType.CONNECTION_TIMEOUT: ErrorCategory.NETWORK,
            ErrorType.CONNECTION_REFUSED: ErrorCategory.NETWORK,
            ErrorType.DNS_RESOLUTION_FAILED: ErrorCategory.NETWORK,
        }
        
        return category_mapping.get(error_type, ErrorCategory.UNKNOWN)
    
    def _assess_severity(self, error_type: ErrorType, error: Exception, context: LoadingContext) -> ErrorSeverity:
        """Assess the severity of the error."""
        high_severity_types = {
            ErrorType.GGUF_CORRUPTED,
            ErrorType.SAFETENSORS_CORRUPTED,
            ErrorType.PYTORCH_INVALID_FORMAT,
            ErrorType.BACKEND_NOT_AVAILABLE,
            ErrorType.INSUFFICIENT_MEMORY,
            ErrorType.INSUFFICIENT_VRAM,
            ErrorType.CUDA_ERROR
        }
        
        medium_severity_types = {
            ErrorType.GGUF_VERSION_UNSUPPORTED,
            ErrorType.SAFETENSORS_INVALID_HEADER,
            ErrorType.PYTORCH_MISSING_CONFIG,
            ErrorType.HF_MODEL_NOT_FOUND,
            ErrorType.HF_AUTH_REQUIRED,
            ErrorType.HF_DOWNLOAD_FAILED,
            ErrorType.BACKEND_INCOMPATIBLE,
            ErrorType.FILE_NOT_FOUND,
            ErrorType.PERMISSION_DENIED
        }
        
        if error_type in high_severity_types:
            return ErrorSeverity.HIGH
        elif error_type in medium_severity_types:
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    def _analyze_root_cause(self, error: Exception, context: LoadingContext, error_type: ErrorType) -> str:
        """Perform root cause analysis based on error type and context."""
        root_cause_templates = {
            ErrorType.GGUF_VERSION_UNSUPPORTED: "The GGUF file uses a version that is not supported by the current backend. This typically occurs when trying to load newer GGUF files with older software versions.",
            
            ErrorType.GGUF_CORRUPTED: "The GGUF file appears to be corrupted or incomplete. This can happen due to incomplete downloads, file system errors, or storage device issues.",
            
            ErrorType.SAFETENSORS_INVALID_HEADER: "The safetensors file has an invalid or corrupted header. This prevents the system from reading the tensor metadata required for loading.",
            
            ErrorType.SAFETENSORS_CORRUPTED: "The safetensors file is corrupted or incomplete. This can occur during download, transfer, or due to storage issues.",
            
            ErrorType.PYTORCH_INVALID_FORMAT: "The PyTorch model files are in an invalid or unsupported format. This may be due to version incompatibilities or corrupted files.",
            
            ErrorType.PYTORCH_MISSING_CONFIG: "The PyTorch model directory is missing the required config.json file, which contains essential model configuration information.",
            
            ErrorType.HF_MODEL_NOT_FOUND: "The specified Hugging Face model ID does not exist or is not accessible. This could be due to a typo in the model name or the model being private/removed.",
            
            ErrorType.HF_AUTH_REQUIRED: "The Hugging Face model requires authentication to access. You need to provide a valid Hugging Face token to download this model.",
            
            ErrorType.HF_AUTH_INVALID: "The provided Hugging Face authentication token is invalid or has insufficient permissions to access the requested model.",
            
            ErrorType.HF_DOWNLOAD_FAILED: "Failed to download the model from Hugging Face Hub. This could be due to network issues, server problems, or insufficient disk space.",
            
            ErrorType.HF_NETWORK_ERROR: "Network connectivity issues are preventing access to Hugging Face Hub. Check your internet connection and firewall settings.",
            
            ErrorType.HF_QUOTA_EXCEEDED: "You have exceeded the rate limit or quota for Hugging Face Hub requests. Wait before trying again or upgrade your account.",
            
            ErrorType.BACKEND_NOT_AVAILABLE: "The required backend is not installed or not available. This prevents loading models that depend on this specific backend.",
            
            ErrorType.BACKEND_INCOMPATIBLE: "The selected backend is incompatible with the model format or system configuration.",
            
            ErrorType.BACKEND_INITIALIZATION_FAILED: "The backend failed to initialize properly. This could be due to missing dependencies, configuration issues, or hardware problems.",
            
            ErrorType.INSUFFICIENT_MEMORY: "The system does not have enough RAM to load the model. Large models require significant memory resources.",
            
            ErrorType.INSUFFICIENT_VRAM: "The GPU does not have enough VRAM to load the model. Consider using CPU mode or a smaller model.",
            
            ErrorType.GPU_NOT_AVAILABLE: "GPU acceleration is not available on this system. This could be due to missing drivers, unsupported hardware, or configuration issues.",
            
            ErrorType.CUDA_ERROR: "CUDA-related error occurred. This typically indicates GPU driver issues, CUDA installation problems, or hardware compatibility issues.",
            
            ErrorType.FILE_NOT_FOUND: "The specified model file or directory does not exist at the given path.",
            
            ErrorType.PERMISSION_DENIED: "Insufficient permissions to access the model file or directory. The application needs read access to load models.",
            
            ErrorType.CONNECTION_TIMEOUT: "Network connection timed out while trying to access remote resources.",
            
            ErrorType.CONNECTION_REFUSED: "Connection was refused by the remote server. This could indicate server issues or network configuration problems."
        }
        
        base_cause = root_cause_templates.get(error_type, f"An error of type {error_type.value} occurred: {str(error)}")
        
        # Add context-specific information
        if context.model_path:
            base_cause += f" Model path: {context.model_path}"
        if context.model_id:
            base_cause += f" Model ID: {context.model_id}"
        if context.backend_name:
            base_cause += f" Backend: {context.backend_name}"
        
        return base_cause
    
    def _generate_user_message(self, error: Exception, context: LoadingContext, error_type: ErrorType) -> str:
        """Generate a user-friendly error message."""
        user_messages = {
            ErrorType.GGUF_VERSION_UNSUPPORTED: "This GGUF model uses a newer version format that isn't supported yet. Try updating your software or finding an older version of the model.",
            
            ErrorType.GGUF_CORRUPTED: "The GGUF model file appears to be corrupted. Try re-downloading the model or checking if you have enough disk space.",
            
            ErrorType.SAFETENSORS_INVALID_HEADER: "The safetensors model file has an invalid format. Try re-downloading the model or using a different version.",
            
            ErrorType.SAFETENSORS_CORRUPTED: "The safetensors model file is corrupted. Please re-download the model from a reliable source.",
            
            ErrorType.PYTORCH_INVALID_FORMAT: "The PyTorch model files are in an unsupported format. Try using a different model or updating your software.",
            
            ErrorType.PYTORCH_MISSING_CONFIG: "The model directory is missing required configuration files. Make sure you have the complete model files.",
            
            ErrorType.HF_MODEL_NOT_FOUND: "The Hugging Face model you're trying to load doesn't exist or isn't accessible. Check the model name and try again.",
            
            ErrorType.HF_AUTH_REQUIRED: "This model requires authentication. Please provide your Hugging Face token in the settings.",
            
            ErrorType.HF_AUTH_INVALID: "Your Hugging Face token is invalid or doesn't have permission to access this model. Please check your token.",
            
            ErrorType.HF_DOWNLOAD_FAILED: "Failed to download the model from Hugging Face. Check your internet connection and try again.",
            
            ErrorType.HF_NETWORK_ERROR: "Can't connect to Hugging Face Hub. Check your internet connection and firewall settings.",
            
            ErrorType.HF_QUOTA_EXCEEDED: "You've made too many requests to Hugging Face. Please wait a few minutes before trying again.",
            
            ErrorType.BACKEND_NOT_AVAILABLE: "The required software component isn't installed. Please install the missing dependencies.",
            
            ErrorType.BACKEND_INCOMPATIBLE: "The selected backend isn't compatible with this model. Try using a different backend or model format.",
            
            ErrorType.BACKEND_INITIALIZATION_FAILED: "Failed to initialize the model loading system. Check your installation and try restarting the application.",
            
            ErrorType.INSUFFICIENT_MEMORY: "Not enough memory to load this model. Try closing other applications or using a smaller model.",
            
            ErrorType.INSUFFICIENT_VRAM: "Your GPU doesn't have enough memory for this model. Try using CPU mode or a smaller model.",
            
            ErrorType.GPU_NOT_AVAILABLE: "GPU acceleration isn't available. Check your GPU drivers or switch to CPU mode.",
            
            ErrorType.CUDA_ERROR: "GPU error occurred. Update your GPU drivers or switch to CPU mode.",
            
            ErrorType.FILE_NOT_FOUND: "The model file couldn't be found. Check the file path and make sure the file exists.",
            
            ErrorType.PERMISSION_DENIED: "Don't have permission to access the model file. Check file permissions or run as administrator.",
            
            ErrorType.CONNECTION_TIMEOUT: "Connection timed out. Check your internet connection and try again.",
            
            ErrorType.CONNECTION_REFUSED: "Connection was refused. The server might be down or your firewall might be blocking the connection."
        }
        
        return user_messages.get(error_type, f"An unexpected error occurred: {str(error)}")
    
    def _extract_technical_details(self, error: Exception, context: LoadingContext) -> str:
        """Extract technical details for debugging."""
        details = []
        
        # Basic error information
        details.append(f"Error Type: {type(error).__name__}")
        details.append(f"Error Message: {str(error)}")
        
        # Context information
        if context.model_format:
            details.append(f"Model Format: {context.model_format.value}")
        if context.backend_name:
            details.append(f"Backend: {context.backend_name}")
        if context.operation:
            details.append(f"Operation: {context.operation}")
        
        # System information
        if context.system_info:
            details.append(f"System Info: {json.dumps(context.system_info, indent=2)}")
        
        # Stack trace
        details.append(f"Stack Trace:\n{traceback.format_exc()}")
        
        return "\n".join(details)
    
    def _identify_affected_components(self, error: Exception, context: LoadingContext) -> List[str]:
        """Identify which components are affected by the error."""
        components = []
        
        # Always affected
        components.append("Model Loader")
        
        # Format-specific components
        if context.model_format:
            components.append(f"{context.model_format.value.upper()} Handler")
        
        # Backend components
        if context.backend_name:
            components.append(f"{context.backend_name} Backend")
        
        # System components based on error type
        error_str = str(error).lower()
        if any(keyword in error_str for keyword in ['cuda', 'gpu']):
            components.append("GPU System")
        if any(keyword in error_str for keyword in ['memory', 'ram']):
            components.append("Memory Manager")
        if any(keyword in error_str for keyword in ['network', 'download']):
            components.append("Network Layer")
        if any(keyword in error_str for keyword in ['file', 'path']):
            components.append("File System")
        
        return list(set(components))  # Remove duplicates
    
    def _generate_resolution_suggestions(self, error: Exception, context: LoadingContext, error_type: ErrorType) -> List[ResolutionSuggestion]:
        """Generate actionable resolution suggestions based on error type."""
        suggestions = []
        
        # Get format-specific suggestions
        if context.model_format and context.model_format in self._format_specific_analyzers:
            format_suggestions = self._get_format_specific_suggestions(error_type, context)
            suggestions.extend(format_suggestions)
        
        # Get general suggestions based on error type
        general_suggestions = self._get_general_suggestions(error_type, context)
        suggestions.extend(general_suggestions)
        
        # Sort by success probability (highest first)
        suggestions.sort(key=lambda x: x.success_probability, reverse=True)
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def _get_format_specific_suggestions(self, error_type: ErrorType, context: LoadingContext) -> List[ResolutionSuggestion]:
        """Get format-specific resolution suggestions."""
        suggestions = []
        
        if context.model_format == ModelFormat.GGUF:
            if error_type == ErrorType.GGUF_VERSION_UNSUPPORTED:
                suggestions.append(ResolutionSuggestion(
                    title="Update GGUF Backend",
                    description="Update llama-cpp-python to support newer GGUF versions",
                    action_type=RecoveryAction.MANUAL_INTERVENTION,
                    steps=[
                        "Open command prompt as administrator",
                        "Run: pip install --upgrade llama-cpp-python",
                        "Restart the application",
                        "Try loading the model again"
                    ],
                    estimated_time="5-10 minutes",
                    difficulty="Easy",
                    success_probability=0.8,
                    format_specific=True,
                    links=["https://github.com/abetlen/llama-cpp-python"]
                ))
            elif error_type == ErrorType.GGUF_CORRUPTED:
                suggestions.append(ResolutionSuggestion(
                    title="Re-download GGUF Model",
                    description="Download the model again from a reliable source",
                    action_type=RecoveryAction.MANUAL_INTERVENTION,
                    steps=[
                        "Delete the corrupted model file",
                        "Clear browser cache if downloaded via browser",
                        "Re-download from the original source",
                        "Verify file size matches expected size",
                        "Try loading the model again"
                    ],
                    estimated_time="10-30 minutes",
                    difficulty="Easy",
                    success_probability=0.9,
                    format_specific=True
                ))
        
        elif context.model_format == ModelFormat.HUGGINGFACE:
            if error_type == ErrorType.HF_AUTH_REQUIRED:
                suggestions.append(ResolutionSuggestion(
                    title="Configure Hugging Face Token",
                    description="Set up authentication for private models",
                    action_type=RecoveryAction.RECONFIGURE,
                    steps=[
                        "Go to https://huggingface.co/settings/tokens",
                        "Create a new access token",
                        "Copy the token",
                        "Open application settings",
                        "Paste token in Hugging Face authentication field",
                        "Save settings and try again"
                    ],
                    estimated_time="3-5 minutes",
                    difficulty="Easy",
                    success_probability=0.95,
                    format_specific=True,
                    links=["https://huggingface.co/docs/hub/security-tokens"]
                ))
        
        return suggestions
    
    def _get_general_suggestions(self, error_type: ErrorType, context: LoadingContext) -> List[ResolutionSuggestion]:
        """Get general resolution suggestions based on error type."""
        suggestions = []
        
        if error_type in [ErrorType.INSUFFICIENT_MEMORY, ErrorType.INSUFFICIENT_VRAM]:
            suggestions.extend([
                ResolutionSuggestion(
                    title="Close Other Applications",
                    description="Free up memory by closing unnecessary applications",
                    action_type=RecoveryAction.REDUCE_RESOURCES,
                    steps=[
                        "Close web browsers with many tabs",
                        "Close other memory-intensive applications",
                        "Check Task Manager for high memory usage",
                        "Try loading the model again"
                    ],
                    estimated_time="2-3 minutes",
                    difficulty="Easy",
                    success_probability=0.7,
                    automatic=True
                ),
                ResolutionSuggestion(
                    title="Use CPU Mode",
                    description="Switch to CPU-only mode to reduce memory requirements",
                    action_type=RecoveryAction.RECONFIGURE,
                    steps=[
                        "Open backend settings",
                        "Disable GPU acceleration",
                        "Set backend to CPU mode",
                        "Try loading the model again"
                    ],
                    estimated_time="1-2 minutes",
                    difficulty="Easy",
                    success_probability=0.8,
                    automatic=True
                )
            ])
        
        elif error_type in [ErrorType.CUDA_ERROR, ErrorType.GPU_NOT_AVAILABLE]:
            suggestions.extend([
                ResolutionSuggestion(
                    title="Update GPU Drivers",
                    description="Install the latest GPU drivers",
                    action_type=RecoveryAction.MANUAL_INTERVENTION,
                    steps=[
                        "Identify your GPU model",
                        "Visit manufacturer website (NVIDIA/AMD)",
                        "Download latest drivers",
                        "Install drivers",
                        "Restart computer",
                        "Try loading the model again"
                    ],
                    estimated_time="15-20 minutes",
                    difficulty="Intermediate",
                    success_probability=0.8,
                    requires_restart=True,
                    links=["https://www.nvidia.com/drivers", "https://www.amd.com/support"]
                ),
                ResolutionSuggestion(
                    title="Switch to CPU Mode",
                    description="Use CPU instead of GPU for model loading",
                    action_type=RecoveryAction.FALLBACK,
                    steps=[
                        "Open settings",
                        "Disable GPU acceleration",
                        "Select CPU backend",
                        "Try loading the model again"
                    ],
                    estimated_time="1-2 minutes",
                    difficulty="Easy",
                    success_probability=0.9,
                    automatic=True
                )
            ])
        
        elif error_type == ErrorType.BACKEND_NOT_AVAILABLE:
            suggestions.append(ResolutionSuggestion(
                title="Install Missing Backend",
                description="Install the required backend dependencies",
                action_type=RecoveryAction.MANUAL_INTERVENTION,
                steps=[
                    "Open command prompt as administrator",
                    "Install required package (e.g., pip install transformers)",
                    "Restart the application",
                    "Try loading the model again"
                ],
                estimated_time="5-10 minutes",
                difficulty="Intermediate",
                success_probability=0.85,
                requires_restart=True
            ))
        
        elif error_type in [ErrorType.HF_NETWORK_ERROR, ErrorType.CONNECTION_TIMEOUT]:
            suggestions.extend([
                ResolutionSuggestion(
                    title="Check Internet Connection",
                    description="Verify and troubleshoot network connectivity",
                    action_type=RecoveryAction.RETRY,
                    steps=[
                        "Check internet connection",
                        "Try accessing other websites",
                        "Restart router if necessary",
                        "Disable VPN temporarily",
                        "Try loading the model again"
                    ],
                    estimated_time="5-10 minutes",
                    difficulty="Easy",
                    success_probability=0.7,
                    automatic=True
                ),
                ResolutionSuggestion(
                    title="Configure Proxy Settings",
                    description="Set up proxy if behind corporate firewall",
                    action_type=RecoveryAction.RECONFIGURE,
                    steps=[
                        "Check if behind corporate firewall",
                        "Get proxy settings from IT department",
                        "Configure proxy in application settings",
                        "Try loading the model again"
                    ],
                    estimated_time="10-15 minutes",
                    difficulty="Intermediate",
                    success_probability=0.6
                )
            ])
        
        return suggestions
    
    def _find_similar_errors(self, error: Exception, context: LoadingContext) -> List[str]:
        """Find similar errors that have occurred before."""
        # This would typically query a database of previous errors
        # For now, return empty list as placeholder
        return []
    
    def _initialize_error_patterns(self) -> Dict[str, Any]:
        """Initialize error pattern matching rules."""
        return {
            'gguf_patterns': [
                r'unsupported.*version',
                r'invalid.*header',
                r'corrupted.*file'
            ],
            'safetensors_patterns': [
                r'invalid.*header',
                r'corrupted.*tensor',
                r'malformed.*file'
            ],
            'pytorch_patterns': [
                r'config\.json.*not found',
                r'invalid.*format',
                r'missing.*files'
            ],
            'huggingface_patterns': [
                r'404.*not found',
                r'401.*unauthorized',
                r'403.*forbidden',
                r'429.*rate limit'
            ],
            'memory_patterns': [
                r'out of memory',
                r'memory.*allocation',
                r'insufficient.*memory'
            ],
            'cuda_patterns': [
                r'cuda.*error',
                r'gpu.*not available',
                r'device.*error'
            ]
        }


class EnhancedErrorReportingEngine:
    """
    Main enhanced error reporting engine that coordinates all error analysis components.
    
    This class provides the main interface for comprehensive error reporting with
    format-aware analysis, context-aware messaging, and actionable resolution suggestions.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.analyzer = FormatAwareErrorAnalyzer()
        self._error_history = []
        self._analytics_enabled = True
    
    def analyze_loading_error(self, error: Exception, context: LoadingContext) -> ErrorAnalysis:
        """
        Analyze a model loading error and provide comprehensive analysis.
        
        Args:
            error: The exception that occurred during model loading
            context: Context information about the loading operation
            
        Returns:
            ErrorAnalysis with detailed analysis and resolution suggestions
        """
        try:
            # Enhance context with system information
            enhanced_context = self._enhance_context(context)
            
            # Perform comprehensive error analysis
            analysis = self.analyzer.analyze_loading_error(error, enhanced_context)
            
            # Store for analytics if enabled
            if self._analytics_enabled:
                self._record_error_analysis(analysis)
            
            # Log the analysis
            self._log_error_analysis(analysis)
            
            return analysis
            
        except Exception as analysis_error:
            self.logger.error(f"Error during error analysis: {analysis_error}")
            
            # Return basic analysis if comprehensive analysis fails
            return self._create_fallback_analysis(error, context)
    
    def generate_user_message(self, analysis: ErrorAnalysis) -> str:
        """
        Generate a formatted user-friendly error message.
        
        Args:
            analysis: The error analysis result
            
        Returns:
            Formatted user message with suggestions
        """
        message_parts = []
        
        # Main error message
        message_parts.append(f"[ERROR] {analysis.user_friendly_message}")
        message_parts.append("")
        
        # Add context if available
        if analysis.context.model_path or analysis.context.model_id:
            model_info = analysis.context.model_path or analysis.context.model_id
            message_parts.append(f"📁 Model: {Path(model_info).name if analysis.context.model_path else model_info}")
        
        if analysis.context.model_format:
            message_parts.append(f"[LIST] Format: {analysis.context.model_format.value.upper()}")
        
        if analysis.context.backend_name:
            message_parts.append(f"⚙️ Backend: {analysis.context.backend_name}")
        
        message_parts.append("")
        
        # Add top resolution suggestions
        if analysis.resolution_suggestions:
            message_parts.append("💡 Suggested Solutions:")
            for i, suggestion in enumerate(analysis.resolution_suggestions[:3], 1):
                message_parts.append(f"{i}. {suggestion.title}")
                message_parts.append(f"   {suggestion.description}")
                message_parts.append(f"   ⏱️ Time: {suggestion.estimated_time} | 📊 Success Rate: {int(suggestion.success_probability * 100)}%")
                message_parts.append("")
        else:
            message_parts.append("💡 No automatic solutions available - manual investigation required")
            message_parts.append("")
        
        # Add error ID for support
        message_parts.append(f"🔍 Error ID: {analysis.error_id}")
        
        return "\n".join(message_parts)
    
    def get_resolution_suggestions(self, analysis: ErrorAnalysis) -> List[ResolutionSuggestion]:
        """
        Get actionable resolution suggestions for an error.
        
        Args:
            analysis: The error analysis result
            
        Returns:
            List of resolution suggestions sorted by effectiveness
        """
        return analysis.resolution_suggestions
    
    def categorize_error(self, error: Exception, context: LoadingContext) -> ErrorCategory:
        """
        Categorize an error for routing and handling.
        
        Args:
            error: The exception that occurred
            context: Context information about the error
            
        Returns:
            ErrorCategory for the error
        """
        error_type = self.analyzer._classify_error_type(error, context)
        return self.analyzer._determine_category(error_type, error, context)
    
    def _enhance_context(self, context: LoadingContext) -> LoadingContext:
        """Enhance context with additional system information."""
        enhanced_context = LoadingContext(
            model_format=context.model_format,
            model_path=context.model_path,
            model_id=context.model_id,
            backend_name=context.backend_name,
            operation=context.operation,
            config=context.config,
            additional_context=context.additional_context.copy()
        )
        
        # Add system information
        try:
            import platform
            import sys
            enhanced_context.system_info = {
                'platform': platform.system(),
                'python_version': sys.version,
                'cpu_count': psutil.cpu_count(),
                'total_memory': psutil.virtual_memory().total
            }
            
            enhanced_context.memory_info = {
                'available': psutil.virtual_memory().available,
                'percent_used': psutil.virtual_memory().percent,
                'total': psutil.virtual_memory().total
            }
            
            # Add GPU information if available
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    enhanced_context.hardware_info = {
                        'gpu_count': len(gpus),
                        'gpu_names': [gpu.name for gpu in gpus],
                        'gpu_memory': [gpu.memoryTotal for gpu in gpus]
                    }
            except ImportError:
                pass
            
        except Exception as e:
            self.logger.warning(f"Failed to enhance context with system info: {e}")
        
        return enhanced_context
    
    def _record_error_analysis(self, analysis: ErrorAnalysis):
        """Record error analysis for analytics."""
        self._error_history.append({
            'timestamp': analysis.timestamp.isoformat(),
            'error_id': analysis.error_id,
            'error_type': analysis.error_type.value,
            'category': analysis.category.value,
            'severity': analysis.severity.value,
            'model_format': analysis.context.model_format.value if analysis.context.model_format else None,
            'backend_name': analysis.context.backend_name,
            'resolution_count': len(analysis.resolution_suggestions)
        })
        
        # Keep only last 1000 errors
        if len(self._error_history) > 1000:
            self._error_history = self._error_history[-1000:]
    
    def _log_error_analysis(self, analysis: ErrorAnalysis):
        """Log the error analysis for debugging."""
        self.logger.error(f"Error Analysis [{analysis.error_id}]: {analysis.error_type.value}")
        self.logger.error(f"Category: {analysis.category.value}, Severity: {analysis.severity.value}")
        self.logger.error(f"Root Cause: {analysis.root_cause}")
        self.logger.error(f"Suggestions: {len(analysis.resolution_suggestions)} available")
    
    def _create_fallback_analysis(self, error: Exception, context: LoadingContext) -> ErrorAnalysis:
        """Create a basic error analysis when comprehensive analysis fails."""
        return ErrorAnalysis(
            error_id=f"FALLBACK_{int(time.time())}",
            error_type=ErrorType.UNKNOWN_ERROR,
            category=ErrorCategory.UNKNOWN,
            severity=ErrorSeverity.MEDIUM,
            root_cause=f"An error occurred: {str(error)}",
            user_friendly_message=f"An unexpected error occurred while loading the model: {str(error)}",
            technical_details=f"Error: {type(error).__name__}: {str(error)}\nTraceback: {traceback.format_exc()}",
            context=context,
            affected_components=["Model Loader"],
            resolution_suggestions=[
                ResolutionSuggestion(
                    title="Restart Application",
                    description="Try restarting the application and loading the model again",
                    action_type=RecoveryAction.RETRY,
                    steps=["Close the application", "Restart the application", "Try loading the model again"],
                    estimated_time="1-2 minutes",
                    difficulty="Easy",
                    success_probability=0.5,
                    automatic=False
                )
            ]
        )
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for analytics."""
        if not self._error_history:
            return {
                'total_errors': 0,
                'error_types': {},
                'categories': {},
                'severities': {},
                'formats': {}
            }
        
        from collections import Counter
        
        total_errors = len(self._error_history)
        error_types = Counter(error['error_type'] for error in self._error_history)
        categories = Counter(error['category'] for error in self._error_history)
        severities = Counter(error['severity'] for error in self._error_history)
        formats = Counter(error['model_format'] for error in self._error_history if error['model_format'])
        
        return {
            'total_errors': total_errors,
            'error_types': dict(error_types),
            'categories': dict(categories),
            'severities': dict(severities),
            'formats': dict(formats)
        }