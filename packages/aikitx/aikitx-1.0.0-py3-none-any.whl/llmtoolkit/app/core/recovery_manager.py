"""
Recovery Manager

This module provides a recovery manager for handling transient errors,
implementing graceful degradation, and preserving state during crashes.
"""

import os
import json
import time
import logging
import threading
import traceback
from typing import Dict, Any, Optional, List, Callable, Tuple
from pathlib import Path
from functools import wraps

from llmtoolkit.utils.error_handling import ErrorCategory, ErrorSeverity
from llmtoolkit.utils.exceptions import GGUFLoaderError

logger = logging.getLogger("gguf_loader.core.recovery_manager")

class RecoveryManager:
    """
    Recovery manager for handling transient errors and implementing recovery strategies.
    
    This class provides:
    - Automatic retry for transient errors
    - Graceful degradation when features are unavailable
    - State preservation during crashes
    """
    
    def __init__(self, event_bus=None, config_manager=None):
        """
        Initialize the recovery manager.
        
        Args:
            event_bus: Application event bus
            config_manager: Configuration manager
        """
        self.event_bus = event_bus
        self.config_manager = config_manager
        
        # Default retry settings
        self.default_max_retries = 3
        self.default_retry_delay = 1.0  # seconds
        self.default_backoff_factor = 2.0
        
        # State preservation
        # Use user config directory from resource manager
        from llmtoolkit.resource_manager import get_user_config_dir
        user_config_dir = get_user_config_dir()
        
        self.state_dir = None
        if self.config_manager:
            app_data_dir = self.config_manager.get_value("app_data_dir")
            if app_data_dir:
                self.state_dir = Path(app_data_dir) / "recovery"
            else:
                self.state_dir = user_config_dir / "recovery"
        else:
            self.state_dir = user_config_dir / "recovery"
        
        # Create state directory if it doesn't exist
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # Feature degradation tracking
        self._degraded_features = {}
        
        # Register event handlers
        if self.event_bus:
            self.event_bus.subscribe("app.initialized", self._on_app_initialized)
            self.event_bus.subscribe("app.shutdown", self._on_app_shutdown)
    
    def retry(self, max_retries=None, retry_delay=None, backoff_factor=None):
        """
        Decorator for retrying functions that may fail with transient errors.
        
        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (seconds)
            backoff_factor: Factor to increase delay between retries
            
        Returns:
            Decorated function
        """
        max_retries = max_retries or self.default_max_retries
        retry_delay = retry_delay or self.default_retry_delay
        backoff_factor = backoff_factor or self.default_backoff_factor
        
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                delay = retry_delay
                
                for attempt in range(max_retries + 1):
                    try:
                        if attempt > 0:
                            func_name = getattr(func, '__name__', str(func))
                            logger.info(f"Retry attempt {attempt}/{max_retries} for {func_name}")
                            
                            # Publish retry event
                            if self.event_bus:
                                self.event_bus.publish("recovery.retry", {
                                    "function": func_name,
                                    "attempt": attempt,
                                    "max_retries": max_retries
                                })
                        
                        return func(*args, **kwargs)
                        
                    except Exception as e:
                        last_exception = e
                        
                        # Check if we should retry
                        if attempt < max_retries and self._is_retriable_error(e):
                            func_name = getattr(func, '__name__', str(func))
                            logger.warning(f"Error in {func_name}, will retry: {e}")
                            
                            # Wait before retrying
                            time.sleep(delay)
                            
                            # Increase delay for next attempt
                            delay *= backoff_factor
                        else:
                            # Max retries reached or non-retriable error
                            break
                
                # If we get here, all retries failed
                if last_exception:
                    func_name = getattr(func, '__name__', str(func))
                    logger.error(f"All retry attempts failed for {func_name}: {last_exception}")
                    
                    # Publish retry failed event
                    if self.event_bus:
                        self.event_bus.publish("recovery.retry.failed", {
                            "function": func_name,
                            "exception": last_exception,
                            "attempts": max_retries
                        })
                    
                    raise last_exception
            
            return wrapper
        
        return decorator
    
    def retry_async(self, func, args=None, kwargs=None, 
                   max_retries=None, retry_delay=None, backoff_factor=None,
                   on_success=None, on_failure=None):
        """
        Retry a function asynchronously.
        
        Args:
            func: Function to retry
            args: Function arguments
            kwargs: Function keyword arguments
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (seconds)
            backoff_factor: Factor to increase delay between retries
            on_success: Callback for successful execution
            on_failure: Callback for failed execution
        """
        args = args or ()
        kwargs = kwargs or {}
        max_retries = max_retries or self.default_max_retries
        retry_delay = retry_delay or self.default_retry_delay
        backoff_factor = backoff_factor or self.default_backoff_factor
        
        def _retry_thread():
            last_exception = None
            delay = retry_delay
            
            for attempt in range(max_retries + 1):
                try:
                    if attempt > 0:
                        func_name = getattr(func, '__name__', str(func))
                        logger.info(f"Async retry attempt {attempt}/{max_retries} for {func_name}")
                        
                        # Publish retry event
                        if self.event_bus:
                            self.event_bus.publish("recovery.retry", {
                                "function": func_name,
                                "attempt": attempt,
                                "max_retries": max_retries,
                                "async": True
                            })
                    
                    result = func(*args, **kwargs)
                    
                    # Call success callback
                    if on_success:
                        on_success(result)
                    
                    return
                    
                except Exception as e:
                    last_exception = e
                    
                    # Check if we should retry
                    if attempt < max_retries and self._is_retriable_error(e):
                        func_name = getattr(func, '__name__', str(func))
                        logger.warning(f"Error in async {func_name}, will retry: {e}")
                        
                        # Wait before retrying
                        time.sleep(delay)
                        
                        # Increase delay for next attempt
                        delay *= backoff_factor
                    else:
                        # Max retries reached or non-retriable error
                        break
            
            # If we get here, all retries failed
            if last_exception and on_failure:
                func_name = getattr(func, '__name__', str(func))
                logger.error(f"All async retry attempts failed for {func_name}: {last_exception}")
                
                # Publish retry failed event
                if self.event_bus:
                    self.event_bus.publish("recovery.retry.failed", {
                        "function": func_name,
                        "exception": last_exception,
                        "attempts": max_retries,
                        "async": True
                    })
                
                on_failure(last_exception)
        
        # Start retry thread
        thread = threading.Thread(target=_retry_thread)
        thread.daemon = True
        thread.start()
        
        return thread
    
    def save_state(self, state_id: str, state_data: Dict[str, Any]) -> bool:
        """
        Save application state for recovery.
        
        Args:
            state_id: Identifier for the state
            state_data: State data to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add timestamp to state data
            state_data["_timestamp"] = time.time()
            
            # Save state to file
            state_file = self.state_dir / f"{state_id}.json"
            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
            
            logger.debug(f"Saved state: {state_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save state {state_id}: {e}")
            return False
    
    def load_state(self, state_id: str) -> Optional[Dict[str, Any]]:
        """
        Load saved application state.
        
        Args:
            state_id: Identifier for the state
            
        Returns:
            State data, or None if not found or error
        """
        try:
            # Check if state file exists
            state_file = self.state_dir / f"{state_id}.json"
            if not state_file.exists():
                logger.debug(f"State file not found: {state_id}")
                return None
            
            # Load state from file
            with open(state_file, 'r') as f:
                state_data = json.load(f)
            
            logger.debug(f"Loaded state: {state_id}")
            return state_data
            
        except Exception as e:
            logger.error(f"Failed to load state {state_id}: {e}")
            return None
    
    def clear_state(self, state_id: str) -> bool:
        """
        Clear saved application state.
        
        Args:
            state_id: Identifier for the state
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if state file exists
            state_file = self.state_dir / f"{state_id}.json"
            if not state_file.exists():
                logger.debug(f"State file not found: {state_id}")
                return True
            
            # Delete state file
            state_file.unlink()
            
            logger.debug(f"Cleared state: {state_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear state {state_id}: {e}")
            return False
    
    def get_all_states(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all saved states.
        
        Returns:
            Dictionary of state_id -> state_data
        """
        states = {}
        
        try:
            # Get all state files
            for state_file in self.state_dir.glob("*.json"):
                state_id = state_file.stem
                
                try:
                    # Load state from file
                    with open(state_file, 'r') as f:
                        state_data = json.load(f)
                    
                    states[state_id] = state_data
                    
                except Exception as e:
                    logger.error(f"Failed to load state {state_id}: {e}")
            
            return states
            
        except Exception as e:
            logger.error(f"Failed to get all states: {e}")
            return {}
    
    def degrade_feature(self, feature_id: str, reason: str, 
                       severity: str = ErrorSeverity.WARNING) -> None:
        """
        Mark a feature as degraded.
        
        Args:
            feature_id: Identifier for the feature
            reason: Reason for degradation
            severity: Severity of the degradation
        """
        self._degraded_features[feature_id] = {
            "reason": reason,
            "severity": severity,
            "timestamp": time.time()
        }
        
        logger.warning(f"Feature degraded: {feature_id} - {reason}")
        
        # Publish feature degraded event
        if self.event_bus:
            self.event_bus.publish("recovery.feature.degraded", {
                "feature_id": feature_id,
                "reason": reason,
                "severity": severity
            })
    
    def restore_feature(self, feature_id: str) -> bool:
        """
        Mark a feature as restored.
        
        Args:
            feature_id: Identifier for the feature
            
        Returns:
            True if feature was degraded, False otherwise
        """
        if feature_id in self._degraded_features:
            del self._degraded_features[feature_id]
            
            logger.info(f"Feature restored: {feature_id}")
            
            # Publish feature restored event
            if self.event_bus:
                self.event_bus.publish("recovery.feature.restored", {
                    "feature_id": feature_id
                })
            
            return True
        
        return False
    
    def is_feature_degraded(self, feature_id: str) -> bool:
        """
        Check if a feature is degraded.
        
        Args:
            feature_id: Identifier for the feature
            
        Returns:
            True if feature is degraded, False otherwise
        """
        return feature_id in self._degraded_features
    
    def get_degraded_features(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all degraded features.
        
        Returns:
            Dictionary of feature_id -> degradation_info
        """
        return self._degraded_features.copy()
    
    def _is_retriable_error(self, error: Exception) -> bool:
        """
        Check if an error is retriable.
        
        Args:
            error: The exception
            
        Returns:
            True if error is retriable, False otherwise
        """
        # Network-related errors are typically retriable
        if isinstance(error, (ConnectionError, TimeoutError)):
            return True
        
        # I/O errors may be retriable
        if isinstance(error, (IOError, OSError)) and not isinstance(error, (FileNotFoundError, PermissionError)):
            return True
        
        # Custom retriable errors
        if hasattr(error, "retriable") and error.retriable:
            return True
        
        return False
    
    def _on_app_initialized(self):
        """Handle application initialized event."""
        logger.info("Recovery manager initialized")
        
        # Check for crash recovery state
        crash_state = self.load_state("crash_recovery")
        if crash_state:
            logger.info("Found crash recovery state, attempting recovery")
            
            # Publish crash recovery event
            if self.event_bus:
                self.event_bus.publish("recovery.crash.detected", {
                    "state": crash_state
                })
            
            # Clear crash state after recovery attempt
            self.clear_state("crash_recovery")
    
    def _on_app_shutdown(self):
        """Handle application shutdown event."""
        logger.info("Saving application state for crash recovery")
        
        # Save current application state
        if self.config_manager:
            # Get current state from config
            app_state = {
                "config": self.config_manager.get_all_values(),
                "degraded_features": self._degraded_features
            }
            
            # Save state
            self.save_state("crash_recovery", app_state)