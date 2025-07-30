"""
Comprehensive Error Handling and Recovery System

This module provides a robust error handling and recovery system for the GGUF loader
application, including error classification, automatic recovery mechanisms, user-friendly
error messages, and analytics for continuous improvement.
"""

import logging
import time
import json
import traceback
import gc
import psutil
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
from abc import ABC, abstractmethod

from .model_backends import BackendError, InstallationError, HardwareError, ModelLoadingError


class ErrorCategory(Enum):
    """Categories of errors for classification."""
    INSTALLATION = "installation"
    HARDWARE = "hardware"
    MEMORY = "memory"
    NETWORK = "network"
    FILESYSTEM = "filesystem"
    CONFIGURATION = "configuration"
    MODEL_LOADING = "model_loading"
    GENERATION = "generation"
    BACKEND = "backend"
    UNKNOWN = "unknown"


class ErrorSeverity(Enum):
    """Severity levels for errors."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryAction(Enum):
    """Types of recovery actions."""
    RETRY = "retry"
    FALLBACK = "fallback"
    REDUCE_RESOURCES = "reduce_resources"
    RECONFIGURE = "reconfigure"
    MANUAL_INTERVENTION = "manual_intervention"


@dataclass
class ErrorContext:
    """Context information for an error."""
    backend_name: Optional[str] = None
    model_path: Optional[str] = None
    operation: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    system_context: Optional[Dict[str, Any]] = None
    additional_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorSolution:
    """A potential solution for an error."""
    title: str
    description: str
    action_type: RecoveryAction
    steps: List[str]
    estimated_time: str
    success_probability: float
    automatic: bool = False
    requires_restart: bool = False


@dataclass
class ClassifiedError:
    """A classified error with context and potential solutions."""
    error_id: str
    original_error: Exception
    category: ErrorCategory
    severity: ErrorSeverity
    title: str
    description: str
    context: ErrorContext
    solutions: List[ErrorSolution]
    timestamp: datetime = field(default_factory=datetime.now)
    recovery_attempted: bool = False
    recovery_successful: Optional[bool] = None

class ErrorClassifier:
    """Classifies errors into categories and provides solutions."""
    
    def __init__(self):
        self.logger = logging.getLogger("error.classifier")
        self._solution_templates = self._initialize_solution_templates()
    
    def classify_error(self, error: Exception, context: ErrorContext) -> ClassifiedError:
        """
        Classify an error and provide potential solutions.
        
        Args:
            error: The exception that occurred
            context: Context information about the error
            
        Returns:
            ClassifiedError with classification and solutions
        """
        # Generate unique error ID
        error_id = f"{int(time.time())}_{hash(str(error))}"
        
        # Determine category and severity
        category = self._categorize_error(error, context)
        severity = self._determine_severity(error, category, context)
        
        # Generate title and description
        title = self._generate_title(error, category)
        description = self._generate_description(error, context)
        
        # Get potential solutions
        solutions = self._get_solutions(error, category, context)
        
        return ClassifiedError(
            error_id=error_id,
            original_error=error,
            category=category,
            severity=severity,
            title=title,
            description=description,
            context=context,
            solutions=solutions
        )
    
    def _categorize_error(self, error: Exception, context: ErrorContext) -> ErrorCategory:
        """Categorize an error based on its type and context."""
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        # Check specific error types first
        if isinstance(error, InstallationError):
            return ErrorCategory.INSTALLATION
        elif isinstance(error, HardwareError):
            return ErrorCategory.HARDWARE
        elif isinstance(error, ModelLoadingError):
            return ErrorCategory.MODEL_LOADING
        
        # Check error message patterns
        if any(keyword in error_str for keyword in ['cuda', 'gpu', 'vram', 'device']):
            return ErrorCategory.HARDWARE
        elif any(keyword in error_str for keyword in ['memory', 'ram', 'oom', 'allocation']):
            return ErrorCategory.MEMORY
        elif any(keyword in error_str for keyword in ['install', 'dependency', 'import', 'module']):
            return ErrorCategory.INSTALLATION
        elif any(keyword in error_str for keyword in ['network', 'connection', 'timeout', 'download']):
            return ErrorCategory.NETWORK
        elif any(keyword in error_str for keyword in ['file', 'path', 'directory', 'permission']):
            return ErrorCategory.FILESYSTEM
        elif any(keyword in error_str for keyword in ['config', 'setting', 'parameter']):
            return ErrorCategory.CONFIGURATION
        elif context.operation == "generate":
            return ErrorCategory.GENERATION
        elif context.backend_name:
            return ErrorCategory.BACKEND
        
        return ErrorCategory.UNKNOWN
    
    def _determine_severity(self, error: Exception, category: ErrorCategory, context: ErrorContext) -> ErrorSeverity:
        """Determine the severity of an error."""
        error_str = str(error).lower()
        
        # Critical errors that prevent basic functionality
        if any(keyword in error_str for keyword in ['fatal', 'critical', 'crash', 'segmentation']):
            return ErrorSeverity.CRITICAL
        
        # High severity for hardware and installation issues
        if category in [ErrorCategory.HARDWARE, ErrorCategory.INSTALLATION]:
            return ErrorSeverity.HIGH
        
        # Memory issues are typically high severity
        if category == ErrorCategory.MEMORY:
            return ErrorSeverity.HIGH
        
        # Model loading failures are medium to high
        if category == ErrorCategory.MODEL_LOADING:
            return ErrorSeverity.HIGH
        
        # Generation errors are medium severity
        if category == ErrorCategory.GENERATION:
            return ErrorSeverity.MEDIUM
        
        # Configuration and filesystem issues are typically medium
        if category in [ErrorCategory.CONFIGURATION, ErrorCategory.FILESYSTEM]:
            return ErrorSeverity.MEDIUM
        
        # Network issues are typically low to medium
        if category == ErrorCategory.NETWORK:
            return ErrorSeverity.MEDIUM
        
        return ErrorSeverity.LOW
    
    def _generate_title(self, error: Exception, category: ErrorCategory) -> str:
        """Generate a user-friendly title for the error."""
        error_type = type(error).__name__
        
        titles = {
            ErrorCategory.INSTALLATION: f"Installation Error: {error_type}",
            ErrorCategory.HARDWARE: f"Hardware Acceleration Error: {error_type}",
            ErrorCategory.MEMORY: f"Memory Error: {error_type}",
            ErrorCategory.NETWORK: f"Network Error: {error_type}",
            ErrorCategory.FILESYSTEM: f"File System Error: {error_type}",
            ErrorCategory.CONFIGURATION: f"Configuration Error: {error_type}",
            ErrorCategory.MODEL_LOADING: f"Model Loading Error: {error_type}",
            ErrorCategory.GENERATION: f"Text Generation Error: {error_type}",
            ErrorCategory.BACKEND: f"Backend Error: {error_type}",
            ErrorCategory.UNKNOWN: f"Unknown Error: {error_type}"
        }
        
        return titles.get(category, f"Error: {error_type}")
    
    def _generate_description(self, error: Exception, context: ErrorContext) -> str:
        """Generate a detailed description of the error."""
        base_description = str(error)
        
        # Add context information
        context_parts = []
        if context.backend_name:
            context_parts.append(f"Backend: {context.backend_name}")
        if context.operation:
            context_parts.append(f"Operation: {context.operation}")
        if context.model_path:
            context_parts.append(f"Model: {Path(context.model_path).name}")
        
        if context_parts:
            return f"{base_description}\n\nContext: {', '.join(context_parts)}"
        
        return base_description 
   
    def _get_solutions(self, error: Exception, category: ErrorCategory, context: ErrorContext) -> List[ErrorSolution]:
        """Get potential solutions for an error."""
        solutions = []
        
        # Get category-specific solutions
        if category in self._solution_templates:
            solutions.extend(self._solution_templates[category])
        
        # Add context-specific solutions
        solutions.extend(self._get_context_specific_solutions(error, context))
        
        # Add backend-specific solutions
        if context.backend_name:
            solutions.extend(self._get_backend_specific_solutions(error, context.backend_name))
        
        # Ensure we always have at least one solution
        if not solutions:
            solutions.append(ErrorSolution(
                title="Manual Investigation Required",
                description="This error requires manual investigation as no automatic solutions are available.",
                action_type=RecoveryAction.MANUAL_INTERVENTION,
                steps=[
                    "Check the error logs for more details",
                    "Search for similar issues online",
                    "Contact support if the problem persists"
                ],
                estimated_time="Variable",
                success_probability=0.3,
                requires_restart=True
            ))
        
        return solutions
    
    def _get_context_specific_solutions(self, error: Exception, context: ErrorContext) -> List[ErrorSolution]:
        """Get solutions specific to the error context."""
        solutions = []
        error_str = str(error).lower()
        
        # CUDA-specific solutions
        if "cuda" in error_str:
            solutions.append(ErrorSolution(
                title="Install CUDA Toolkit",
                description="Install the appropriate CUDA toolkit version for your GPU.",
                action_type=RecoveryAction.MANUAL_INTERVENTION,
                steps=[
                    "Visit NVIDIA's CUDA toolkit download page",
                    "Download the appropriate CUDA toolkit version",
                    "Install the toolkit",
                    "Restart your computer"
                ],
                estimated_time="15-20 minutes",
                success_probability=0.8,
                requires_restart=True
            ))
        
        return solutions
    
    def _get_backend_specific_solutions(self, error: Exception, backend_name: str) -> List[ErrorSolution]:
        """Get solutions specific to a backend."""
        solutions = []
        
        if backend_name and "cuda" in str(error).lower():
            solutions.append(ErrorSolution(
                title="Switch to CPU Mode",
                description="Temporarily switch to CPU mode while resolving GPU issues.",
                action_type=RecoveryAction.RECONFIGURE,
                steps=[
                    "Open backend settings",
                    "Disable GPU acceleration",
                    "Restart the application"
                ],
                estimated_time="1-2 minutes",
                success_probability=0.9,
                automatic=True
            ))
        
        return solutions
    
    def _initialize_solution_templates(self) -> Dict[ErrorCategory, List[ErrorSolution]]:
        """Initialize solution templates for each error category."""
        return {
            ErrorCategory.INSTALLATION: [
                ErrorSolution(
                    title="Reinstall Dependencies",
                    description="Reinstall the backend dependencies to resolve installation issues.",
                    action_type=RecoveryAction.MANUAL_INTERVENTION,
                    steps=[
                        "Uninstall the problematic package",
                        "Clear package cache",
                        "Reinstall with latest version"
                    ],
                    estimated_time="5-10 minutes",
                    success_probability=0.7
                )
            ],
            ErrorCategory.HARDWARE: [
                ErrorSolution(
                    title="Check GPU Drivers",
                    description="Verify and update GPU drivers for hardware compatibility.",
                    action_type=RecoveryAction.MANUAL_INTERVENTION,
                    steps=[
                        "Check current GPU driver version",
                        "Visit GPU manufacturer's website",
                        "Download and install latest drivers",
                        "Restart computer"
                    ],
                    estimated_time="10-15 minutes",
                    success_probability=0.8,
                    requires_restart=True
                )
            ],
            ErrorCategory.MEMORY: [
                ErrorSolution(
                    title="Reduce Memory Usage",
                    description="Reduce memory usage by adjusting model parameters.",
                    action_type=RecoveryAction.REDUCE_RESOURCES,
                    steps=[
                        "Reduce context size",
                        "Reduce batch size",
                        "Close other applications"
                    ],
                    estimated_time="1-2 minutes",
                    success_probability=0.8,
                    automatic=True
                )
            ],
            ErrorCategory.NETWORK: [
                ErrorSolution(
                    title="Check Internet Connection",
                    description="Verify internet connection and retry the operation.",
                    action_type=RecoveryAction.RETRY,
                    steps=[
                        "Check internet connection",
                        "Verify firewall settings",
                        "Retry the operation"
                    ],
                    estimated_time="2-5 minutes",
                    success_probability=0.6,
                    automatic=True
                )
            ],
            ErrorCategory.FILESYSTEM: [
                ErrorSolution(
                    title="Check File Permissions",
                    description="Verify and fix file access permissions.",
                    action_type=RecoveryAction.MANUAL_INTERVENTION,
                    steps=[
                        "Check if the file or directory exists",
                        "Verify you have read/write permissions",
                        "Run the application as administrator if necessary"
                    ],
                    estimated_time="1-2 minutes",
                    success_probability=0.7
                )
            ],
            ErrorCategory.CONFIGURATION: [
                ErrorSolution(
                    title="Reset Configuration",
                    description="Reset to default configuration settings.",
                    action_type=RecoveryAction.RECONFIGURE,
                    steps=[
                        "Back up current configuration",
                        "Reset to default settings",
                        "Reconfigure essential settings",
                        "Test the application"
                    ],
                    estimated_time="2-3 minutes",
                    success_probability=0.9,
                    automatic=True
                )
            ]
        }

class RecoveryManager:
    """Manages automatic recovery mechanisms for common failures."""
    
    def __init__(self, backend_manager=None):
        self.logger = logging.getLogger("error.recovery")
        self.backend_manager = backend_manager
        self._max_retry_attempts = 3
        self._retry_delays = [1, 2, 5]  # Exponential backoff
        self._recovery_history = deque(maxlen=100)
        self._recovery_strategies = {}
        self._register_recovery_strategies()
    
    def _register_recovery_strategies(self):
        """Register category-specific recovery strategies."""
        self._recovery_strategies = {
            ErrorCategory.MEMORY: self._recover_memory_error,
            ErrorCategory.HARDWARE: self._recover_hardware_error,
            ErrorCategory.NETWORK: self._recover_network_error,
            ErrorCategory.INSTALLATION: self._recover_installation_error,
            ErrorCategory.CONFIGURATION: self._recover_configuration_error
        }
    
    def attempt_recovery(self, classified_error: ClassifiedError) -> bool:
        """
        Attempt automatic recovery for a classified error.
        
        Args:
            classified_error: The classified error to recover from
            
        Returns:
            True if recovery was successful, False otherwise
        """
        self.logger.info(f"Attempting recovery for error {classified_error.error_id}: {classified_error.title}")
        
        # Mark recovery as attempted
        classified_error.recovery_attempted = True
        
        # Try automatic solutions first
        for solution in classified_error.solutions:
            if solution.automatic:
                success = self._execute_recovery_solution(classified_error, solution)
                if success:
                    classified_error.recovery_successful = True
                    self._record_recovery_success(classified_error, solution)
                    self.logger.info(f"Successfully recovered from error {classified_error.error_id} using {solution.title}")
                    return True
        
        # Try category-specific recovery strategies
        if classified_error.category in self._recovery_strategies:
            strategy = self._recovery_strategies[classified_error.category]
            success = strategy(classified_error)
            if success:
                classified_error.recovery_successful = True
                self._record_recovery_success(classified_error, None)
                return True
        
        # If no automatic solutions worked, try fallback strategies
        if self.backend_manager:
            success = self._fallback_backend(classified_error)
            if success:
                classified_error.recovery_successful = True
                self._record_recovery_success(classified_error, None)
                return True
        
        # Recovery failed
        classified_error.recovery_successful = False
        self._record_recovery_failure(classified_error)
        self.logger.warning(f"Failed to recover from error {classified_error.error_id}")
        return False
    
    def _execute_recovery_solution(self, error: ClassifiedError, solution: ErrorSolution) -> bool:
        """Execute a specific recovery solution."""
        try:
            if solution.action_type == RecoveryAction.RETRY:
                return self._retry_operation(error)
            elif solution.action_type == RecoveryAction.FALLBACK:
                return self._fallback_backend(error)
            elif solution.action_type == RecoveryAction.REDUCE_RESOURCES:
                return self._reduce_resources(error)
            elif solution.action_type == RecoveryAction.RECONFIGURE:
                return self._reconfigure_settings(error)
            else:
                # Manual intervention required
                return False
        except Exception as e:
            self.logger.error(f"Recovery solution failed: {e}")
            return False
    
    def _retry_operation(self, error: ClassifiedError) -> bool:
        """Retry the failed operation with exponential backoff."""
        retry_count = error.context.additional_context.get('retry_count', 0)
        
        if retry_count >= self._max_retry_attempts:
            self.logger.info("Maximum retry attempts reached")
            return False
        
        # Wait with exponential backoff
        delay = self._retry_delays[min(retry_count, len(self._retry_delays) - 1)]
        self.logger.info(f"Retrying operation after {delay} seconds (attempt {retry_count + 1})")
        time.sleep(delay)
        
        # Update retry count
        error.context.additional_context['retry_count'] = retry_count + 1
        
        # This is just indicating that retry is possible
        # The actual retry would be handled by the calling code
        return True
    
    def _fallback_backend(self, error: ClassifiedError) -> bool:
        """Attempt to fall back to a different backend."""
        if not self.backend_manager:
            return False
        
        current_backend = error.context.backend_name
        if not current_backend:
            return False
        
        # Get available backends
        available_backends = self.backend_manager.get_available_backends()
        
        # Remove the current backend from options
        fallback_backends = [b for b in available_backends if b != current_backend]
        
        if not fallback_backends:
            return False
        
        # Try the next best backend
        next_backend = fallback_backends[0]
        self.logger.info(f"Falling back from {current_backend} to {next_backend}")
        
        try:
            success = self.backend_manager.switch_backend(next_backend)
            if success:
                self.logger.info(f"Successfully fell back to {next_backend}")
                return True
        except Exception as e:
            self.logger.error(f"Backend fallback failed: {e}")
        
        return False    

    def _reduce_resources(self, error: ClassifiedError) -> bool:
        """Reduce resource usage to avoid memory/hardware issues."""
        try:
            # Get current memory usage
            memory_info = psutil.virtual_memory()
            if memory_info.percent > 80:  # High memory usage
                self.logger.info("High memory usage detected, attempting to reduce resources")
                
                # Force garbage collection
                gc.collect()
                
                # Reduce configuration if available
                if error.context.config:
                    config = error.context.config
                    
                    # Reduce context size
                    if 'context_size' in config:
                        config['context_size'] = min(config['context_size'], 2048)
                    
                    # Reduce batch size
                    if 'batch_size' in config:
                        config['batch_size'] = max(1, config['batch_size'] // 2)
                    
                    # Disable GPU if memory issues
                    if 'use_gpu' in config:
                        config['use_gpu'] = False
                
                return True
        except Exception as e:
            self.logger.error(f"Resource reduction failed: {e}")
        
        return False
    
    def _reconfigure_settings(self, error: ClassifiedError) -> bool:
        """Reconfigure settings to resolve configuration errors."""
        if not error.context.config:
            return False
        
        try:
            # Reset to safe defaults
            safe_config = {
                'context_size': 2048,
                'batch_size': 1,
                'use_gpu': False,
                'gpu_layers': 0
            }
            
            # Update configuration
            error.context.config.update(safe_config)
            
            self.logger.info("Reconfigured to safe default settings")
            return True
        except Exception as e:
            self.logger.error(f"Reconfiguration failed: {e}")
        
        return False
    
    def _recover_memory_error(self, error: ClassifiedError) -> bool:
        """Specific recovery strategy for memory errors."""
        return self._reduce_resources(error)
    
    def _recover_hardware_error(self, error: ClassifiedError) -> bool:
        """Specific recovery strategy for hardware errors."""
        # Try fallback to CPU
        if error.context.config and error.context.config.get('use_gpu', True):
            error.context.config['use_gpu'] = False
            self.logger.info("Disabled GPU acceleration due to hardware error")
            return True
        return False
    
    def _recover_network_error(self, error: ClassifiedError) -> bool:
        """Specific recovery strategy for network errors."""
        # Simple retry for network errors
        return self._retry_operation(error)
    
    def _recover_installation_error(self, error: ClassifiedError) -> bool:
        """Specific recovery strategy for installation errors."""
        # Installation errors typically require manual intervention
        return False
    
    def _recover_configuration_error(self, error: ClassifiedError) -> bool:
        """Specific recovery strategy for configuration errors."""
        return self._reconfigure_settings(error)
    
    def _record_recovery_success(self, error: ClassifiedError, solution: Optional[ErrorSolution]):
        """Record a successful recovery."""
        record = {
            'timestamp': datetime.now().isoformat(),
            'error_id': error.error_id,
            'category': error.category.value,
            'solution': solution.title if solution else 'Fallback strategy',
            'success': True
        }
        self._recovery_history.append(record)
    
    def _record_recovery_failure(self, error: ClassifiedError):
        """Record a failed recovery attempt."""
        record = {
            'timestamp': datetime.now().isoformat(),
            'error_id': error.error_id,
            'category': error.category.value,
            'solution': None,
            'success': False
        }
        self._recovery_history.append(record)
    
    def get_recovery_statistics(self) -> Dict[str, Any]:
        """Get recovery statistics for analytics."""
        if not self._recovery_history:
            return {
                'total_attempts': 0,
                'success_rate': 0.0,
                'successful_attempts': 0,
                'category_stats': {}
            }
        
        total_attempts = len(self._recovery_history)
        successful_attempts = sum(1 for r in self._recovery_history if r['success'])
        success_rate = successful_attempts / total_attempts
        
        # Category breakdown
        category_stats = defaultdict(lambda: {'attempts': 0, 'successes': 0})
        for record in self._recovery_history:
            category = record['category']
            category_stats[category]['attempts'] += 1
            if record['success']:
                category_stats[category]['successes'] += 1
        
        return {
            'total_attempts': total_attempts,
            'success_rate': success_rate,
            'successful_attempts': successful_attempts,
            'category_stats': dict(category_stats)
        }
class ErrorAnalytics:
    """Provides error analytics and reporting for continuous improvement."""
    
    def __init__(self, storage_path: str = "logs/error_analytics.json"):
        self.logger = logging.getLogger("error.analytics")
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._error_patterns = defaultdict(int)
        self._solution_effectiveness = defaultdict(lambda: {'attempts': 0, 'successes': 0})
        self._system_context = {}
        
        self._load_analytics_data()
    
    def record_error(self, classified_error: ClassifiedError):
        """Record an error for analytics."""
        # Create error pattern key
        pattern_key = f"{classified_error.category.value}:{type(classified_error.original_error).__name__}"
        self._error_patterns[pattern_key] += 1
        
        # Update system context
        self._update_system_context()
        
        # Save analytics data
        self._save_analytics_data()
    
    def record_solution_attempt(self, error: ClassifiedError, solution: ErrorSolution, success: bool):
        """Record a solution attempt for effectiveness tracking."""
        solution_key = f"{error.category.value}:{solution.title}"
        self._solution_effectiveness[solution_key]['attempts'] += 1
        if success:
            self._solution_effectiveness[solution_key]['successes'] += 1
        
        self._save_analytics_data()
    
    def get_solution_effectiveness(self) -> Dict[str, Any]:
        """Get solution effectiveness statistics."""
        effectiveness = {}
        for solution_key, stats in self._solution_effectiveness.items():
            if stats['attempts'] > 0:
                effectiveness[solution_key] = stats['successes'] / stats['attempts']
        return effectiveness
    
    def get_error_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get error trends over a specified period."""
        # This would typically query a time-series database
        # For now, return current patterns
        return {
            'error_patterns': dict(self._error_patterns),
            'total_errors': sum(self._error_patterns.values()),
            'most_common': max(self._error_patterns.items(), key=lambda x: x[1]) if self._error_patterns else ("none", 0)
        }
    
    def generate_improvement_recommendations(self) -> List[str]:
        """Generate recommendations for system improvements."""
        recommendations = []
        
        # Analyze error patterns
        if self._error_patterns:
            most_common = max(self._error_patterns.items(), key=lambda x: x[1])
            if most_common[1] > 5:  # If error occurs more than 5 times
                recommendations.append(f"Consider addressing the recurring error pattern: {most_common[0]}")
        
        # Analyze solution effectiveness
        for solution_key, stats in self._solution_effectiveness.items():
            if stats['attempts'] > 3 and stats['successes'] / stats['attempts'] < 0.3:
                recommendations.append(f"Solution '{solution_key}' has low success rate, consider alternatives")
        
        # System-specific recommendations
        if not self._system_context.get('gpu_available', False):
            recommendations.append("Consider GPU acceleration for better performance")
        
        if self._system_context.get('memory_gb', 0) < 8:
            recommendations.append("Consider upgrading system memory or using smaller models")
        
        return recommendations
    
    def export_analytics_report(self, file_path: str) -> bool:
        """Export a comprehensive analytics report."""
        try:
            report = {
                'generated_at': datetime.now().isoformat(),
                'system_context': self._system_context,
                'error_trends': self.get_error_trends(),
                'solution_effectiveness': self.get_solution_effectiveness(),
                'recommendations': self.generate_improvement_recommendations()
            }
            
            with open(file_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to export analytics report: {e}")
            return False
    
    def _update_system_context(self):
        """Update system context information."""
        try:
            self._system_context = {
                'platform': self._collect_system_context().get('platform', 'unknown'),
                'python_version': self._collect_system_context().get('python_version', 'unknown'),
                'cpu_count': self._collect_system_context().get('cpu_count', 0),
                'memory_gb': round(self._collect_system_context().get('memory_gb', 0), 1),
                'gpu_available': self._check_gpu_availability()
            }
        except Exception:
            pass
    
    def _collect_system_context(self) -> Dict[str, Any]:
        """Collect system context information."""
        try:
            import sys
            import platform
            
            return {
                'platform': platform.platform(),
                'python_version': sys.version,
                'cpu_count': psutil.cpu_count(),
                'memory_gb': round(psutil.virtual_memory().total / (1024**3), 1)
            }
        except Exception:
            return {}
    
    def _check_gpu_availability(self) -> bool:
        """Check if GPU is available."""
        try:
            import torch
            return torch.cuda.is_available() and torch.cuda.device_count() > 0
        except ImportError:
            try:
                import tensorflow as tf
                return len(tf.config.list_physical_devices('GPU')) > 0
            except ImportError:
                return False
    
    def _load_analytics_data(self):
        """Load analytics data from storage."""
        if not self.storage_path.exists():
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            self._error_patterns.update(data.get('error_patterns', {}))
            
            # Load solution effectiveness
            for solution_key, stats in data.get('solution_effectiveness', {}).items():
                self._solution_effectiveness[solution_key].update(stats)
            
            self._system_context = data.get('system_context', {})
        except Exception as e:
            self.logger.error(f"Failed to load analytics data: {e}")
    
    def _save_analytics_data(self):
        """Save analytics data to storage."""
        try:
            data = {
                'last_updated': datetime.now().isoformat(),
                'error_patterns': dict(self._error_patterns),
                'solution_effectiveness': {
                    key: dict(stats) for key, stats in self._solution_effectiveness.items()
                },
                'system_context': self._system_context
            }
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save analytics data: {e}")
class ComprehensiveErrorHandler:
    """
    Main error handling system that integrates classification, recovery, and analytics.
    """
    
    def __init__(self, backend_manager=None, analytics_enabled: bool = True):
        self.logger = logging.getLogger("error.handler")
        self.classifier = ErrorClassifier()
        self.recovery_manager = RecoveryManager(backend_manager)
        self.analytics = ErrorAnalytics() if analytics_enabled else None
        self.backend_manager = backend_manager
        
        self._error_history = deque(maxlen=1000)
        self._notification_callbacks = []
    
    def handle_error(self, error: Exception, context: ErrorContext, 
                    attempt_recovery: bool = True, notify_user: bool = True) -> ClassifiedError:
        """
        Comprehensive error handling with full classification, recovery, and reporting.
        
        Args:
            error: The exception to handle
            context: Error context information
            attempt_recovery: Whether to attempt automatic recovery
            notify_user: Whether to notify the user about the error
            
        Returns:
            ClassifiedError with classification and recovery information
        """
        # Classify the error
        classified_error = self.classifier.classify_error(error, context)
        
        # Log the classified error
        self.logger.error(f"Error {classified_error.error_id}: {classified_error.title}")
        
        # Store in history
        self._error_history.append(classified_error)
        
        # Record for analytics
        if self.analytics:
            self.analytics.record_error(classified_error)
        
        # Attempt recovery if requested
        if attempt_recovery and classified_error.severity != ErrorSeverity.CRITICAL:
            recovery_success = self.recovery_manager.attempt_recovery(classified_error)
            if recovery_success:
                self.logger.info(f"Successfully recovered from error {classified_error.error_id}")
            else:
                self.logger.warning(f"Failed to recover from error {classified_error.error_id}")
        
        # Notify user if requested
        if notify_user:
            self._notify_user(classified_error)
        
        return classified_error
    
    def add_notification_callback(self, callback: Callable[[ClassifiedError], None]):
        """Add a callback for error notifications."""
        self._notification_callbacks.append(callback)
    
    def _notify_user(self, classified_error: ClassifiedError):
        """Notify user about the error."""
        for callback in self._notification_callbacks:
            try:
                callback(classified_error)
            except Exception as e:
                self.logger.error(f"Error notification callback failed: {e}")
    
    def get_error_history(self, limit: int = 10) -> List[ClassifiedError]:
        """Get recent error history."""
        return list(self._error_history)[-limit:]
    
    def get_system_health_report(self) -> Dict[str, Any]:
        """Generate a system health report based on recent errors."""
        recent_errors = list(self._error_history)[-50:]  # Last 50 errors
        
        if not recent_errors:
            return {
                'status': 'healthy',
                'error_count': 0,
                'critical_errors': 0,
                'recovery_rate': 1.0,
                'most_common_category': 'none'
            }
        
        # Count critical errors
        critical_errors = sum(1 for e in recent_errors if e.severity == ErrorSeverity.CRITICAL)
        
        # Calculate recovery rate
        recovered_errors = sum(1 for e in recent_errors if e.recovery_successful)
        recovery_rate = recovered_errors / len(recent_errors) if recent_errors else 0
        
        # Find most common category
        categories = [e.category.value for e in recent_errors]
        most_common_category = max(set(categories), key=categories.count) if categories else 'none'
        
        # Determine overall status
        if critical_errors > 5:
            status = 'critical'
        elif len(recent_errors) > 20:
            status = 'unstable'
        elif recovery_rate < 0.5:
            status = 'degraded'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'error_count': len(recent_errors),
            'critical_errors': critical_errors,
            'recovery_rate': recovery_rate,
            'most_common_category': most_common_category,
            'recommendations': self._get_health_recommendations(recent_errors)
        }
    
    def _get_health_recommendations(self, errors: List[ClassifiedError]) -> List[str]:
        """Get health recommendations based on error patterns."""
        recommendations = []
        
        if not errors:
            return recommendations
        
        # Check for recurring patterns
        categories = [e.category for e in errors]
        category_counts = {cat: categories.count(cat) for cat in set(categories)}
        
        for category, count in category_counts.items():
            if count > len(errors) * 0.3:  # More than 30% of errors
                if category == ErrorCategory.MEMORY:
                    recommendations.append("Consider upgrading system memory or using smaller models")
                elif category == ErrorCategory.HARDWARE:
                    recommendations.append("Check GPU drivers and hardware compatibility")
                elif category == ErrorCategory.INSTALLATION:
                    recommendations.append("Review backend dependencies and installation")
        
        return recommendations
    
    def _get_most_common_category(self, errors: List[ClassifiedError]) -> str:
        """Get the most common error category."""
        if not errors:
            return "none"
        
        categories = [e.category.value for e in errors]
        return max(set(categories), key=categories.count)


# Convenience functions for common error handling patterns
def handle_backend_error(error: Exception, backend_name: str, operation: str = "unknown", 
                        config: Dict[str, Any] = None) -> ClassifiedError:
    """Handle a backend-related error with appropriate context."""
    context = ErrorContext(
        backend_name=backend_name,
        operation=operation,
        config=config
    )
    return get_error_handler().handle_error(error, context)


def handle_model_loading_error(error: Exception, model_path: str, backend_name: str, 
                              config: Dict[str, Any] = None) -> ClassifiedError:
    """Handle a model loading error with appropriate context."""
    context = ErrorContext(
        backend_name=backend_name,
        model_path=model_path,
        operation="model_loading",
        config=config
    )
    return get_error_handler().handle_error(error, context)


def handle_generation_error(error: Exception, backend_name: str, 
                           config: Dict[str, Any] = None) -> ClassifiedError:
    """Handle a text generation error with appropriate context."""
    context = ErrorContext(
        backend_name=backend_name,
        operation="text_generation",
        config=config
    )
    return get_error_handler().handle_error(error, context)


# Global error handler instance
_global_error_handler: Optional[ComprehensiveErrorHandler] = None


def initialize_error_handling(backend_manager=None, analytics_enabled: bool = True):
    """Initialize the global error handling system."""
    global _global_error_handler
    _global_error_handler = ComprehensiveErrorHandler(backend_manager, analytics_enabled)
    return _global_error_handler


def get_error_handler() -> ComprehensiveErrorHandler:
    """Get the global error handler instance."""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ComprehensiveErrorHandler()
    return _global_error_handler