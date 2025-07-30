"""
Configuration Migration Tools

This module provides tools for migrating existing installations to the new
backend configuration system, including detection of existing configurations,
automatic migration, and validation.
"""

import json
import logging
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum

from .backend_config_manager import BackendConfigManager, BackendConfigSet, BackendPreferences
from .model_backends import BackendConfig, BackendType


class MigrationType(Enum):
    """Types of configuration migrations."""
    LEGACY_APP_CONFIG = "legacy_app_config"
    OLD_BACKEND_CONFIG = "old_backend_config"
    MANUAL_SETTINGS = "manual_settings"
    EXTERNAL_CONFIG = "external_config"


@dataclass
class MigrationResult:
    """Result of a configuration migration."""
    success: bool
    migration_type: MigrationType
    source_path: Optional[Path]
    backup_path: Optional[Path]
    migrated_items: List[str]
    warnings: List[str]
    errors: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'success': self.success,
            'migration_type': self.migration_type.value,
            'source_path': str(self.source_path) if self.source_path else None,
            'backup_path': str(self.backup_path) if self.backup_path else None,
            'migrated_items': self.migrated_items,
            'warnings': self.warnings,
            'errors': self.errors
        }


class ConfigMigrationTools:
    """Tools for migrating existing configurations to the new backend system."""
    
    def __init__(self, config_manager: BackendConfigManager):
        """
        Initialize the configuration migration tools.
        
        Args:
            config_manager: Backend configuration manager
        """
        self.logger = logging.getLogger("backend.migration")
        self.config_manager = config_manager
        
        # Migration handlers
        self.migration_handlers = {
            MigrationType.LEGACY_APP_CONFIG: self._migrate_legacy_app_config,
            MigrationType.OLD_BACKEND_CONFIG: self._migrate_old_backend_config,
            MigrationType.MANUAL_SETTINGS: self._migrate_manual_settings,
            MigrationType.EXTERNAL_CONFIG: self._migrate_external_config
        }
    
    def detect_existing_configurations(self, search_paths: Optional[List[Path]] = None) -> List[Tuple[MigrationType, Path]]:
        """
        Detect existing configurations that can be migrated.
        
        Args:
            search_paths: Optional list of paths to search (uses defaults if None)
            
        Returns:
            List of tuples (migration_type, config_path)
        """
        found_configs = []
        
        if search_paths is None:
            # Default search paths
            config_dir = self.config_manager.config_path.parent
            app_dir = config_dir.parent
            # Include legacy paths for migration
            from llmtoolkit.resource_manager import get_user_config_dir
            user_config_dir = get_user_config_dir()
            
            search_paths = [
                config_dir,
                app_dir,
                app_dir / "config",
                app_dir / "settings",
                Path.home() / ".gguf-loader",  # Legacy path
                Path.home() / ".config" / "gguf-loader",  # Legacy path
                user_config_dir  # New user config directory
            ]
        
        for search_path in search_paths:
            if not search_path.exists():
                continue
                
            try:
                # Look for legacy app config
                legacy_config_path = search_path / "app_config.json"
                if legacy_config_path.exists():
                    found_configs.append((MigrationType.LEGACY_APP_CONFIG, legacy_config_path))
                
                # Look for old backend config
                old_backend_config_path = search_path / "backend_config.json"
                if old_backend_config_path.exists():
                    found_configs.append((MigrationType.OLD_BACKEND_CONFIG, old_backend_config_path))
                
                # Look for manual settings files
                for settings_file in ["settings.json", "preferences.json", "config.json"]:
                    settings_path = search_path / settings_file
                    if settings_path.exists() and settings_path != self.config_manager.config_path:
                        found_configs.append((MigrationType.MANUAL_SETTINGS, settings_path))
                
                # Look for external config files
                for config_file in search_path.glob("*.config.json"):
                    if config_file != self.config_manager.config_path:
                        found_configs.append((MigrationType.EXTERNAL_CONFIG, config_file))
                        
            except Exception as e:
                self.logger.warning(f"Error searching {search_path}: {e}")
        
        self.logger.info(f"Found {len(found_configs)} existing configurations")
        return found_configs
    
    def migrate_configuration(self, migration_type: MigrationType, source_path: Path, 
                            create_backup: bool = True) -> MigrationResult:
        """
        Migrate a specific configuration.
        
        Args:
            migration_type: Type of migration to perform
            source_path: Path to the source configuration
            create_backup: Whether to create a backup of the source
            
        Returns:
            MigrationResult with details of the migration
        """
        result = MigrationResult(
            success=False,
            migration_type=migration_type,
            source_path=source_path,
            backup_path=None,
            migrated_items=[],
            warnings=[],
            errors=[]
        )
        
        try:
            # Validate source path
            if not source_path.exists():
                result.errors.append(f"Source configuration not found: {source_path}")
                return result
            
            # Create backup if requested
            if create_backup:
                backup_path = source_path.with_suffix(f"{source_path.suffix}.backup")
                shutil.copy2(source_path, backup_path)
                result.backup_path = backup_path
                self.logger.info(f"Created backup at {backup_path}")
            
            # Get migration handler
            handler = self.migration_handlers.get(migration_type)
            if not handler:
                result.errors.append(f"No migration handler for type: {migration_type}")
                return result
            
            # Perform migration
            self.logger.info(f"Starting migration of {migration_type.value} from {source_path}")
            result = handler(source_path, result)
            
            if result.success:
                self.logger.info(f"Migration completed successfully. Migrated items: {result.migrated_items}")
            else:
                self.logger.error(f"Migration failed. Errors: {result.errors}")
            
            return result
            
        except Exception as e:
            result.errors.append(f"Migration error: {e}")
            self.logger.error(f"Error during migration: {e}")
            return result
    
    def _migrate_legacy_app_config(self, source_path: Path, result: MigrationResult) -> MigrationResult:
        """Migrate from legacy app configuration."""
        try:
            # Load legacy config
            with open(source_path, 'r') as f:
                legacy_config = json.load(f)
            
            # Extract relevant settings
            migrated_config = BackendConfigSet()
            
            # Migrate hardware acceleration settings
            if 'use_hardware_acceleration' in legacy_config:
                gpu_enabled = legacy_config['use_hardware_acceleration']
                
                # Apply to all backend configs
                for backend_name, config in migrated_config.backend_configs.items():
                    config.gpu_enabled = gpu_enabled
                    if gpu_enabled:
                        config.gpu_layers = -1  # Auto-detect
                    else:
                        config.gpu_layers = 0
                
                result.migrated_items.append("hardware_acceleration_setting")
            
            # Migrate AI settings
            if 'ai_settings' in legacy_config:
                ai_settings = legacy_config['ai_settings']
                
                # Update default context size based on max_tokens
                if 'max_tokens' in ai_settings:
                    max_tokens = ai_settings['max_tokens']
                    context_size = max(2048, max_tokens * 2)  # Ensure context is larger than max_tokens
                    
                    for config in migrated_config.backend_configs.values():
                        config.context_size = context_size
                    
                    result.migrated_items.append("context_size_from_max_tokens")
                
                # Migrate temperature and other generation settings
                # (These would typically go to generation defaults, not backend config)
                result.migrated_items.append("ai_settings")
            
            # Migrate memory settings
            if 'max_memory_usage' in legacy_config:
                max_memory = legacy_config['max_memory_usage']
                if max_memory > 0:
                    # Adjust context sizes based on memory limit
                    for config in migrated_config.backend_configs.values():
                        if max_memory < 4096:  # Less than 4GB
                            config.context_size = min(config.context_size, 2048)
                        elif max_memory < 8192:  # Less than 8GB
                            config.context_size = min(config.context_size, 4096)
                    
                    result.migrated_items.append("memory_optimization")
            
            # Set preferences based on legacy settings
            if 'use_hardware_acceleration' in legacy_config:
                migrated_config.preferences.gpu_preference = "gpu" if legacy_config['use_hardware_acceleration'] else "cpu"
            
            # Merge with existing configuration
            self._merge_migrated_config(migrated_config, result)
            
            result.success = True
            
        except Exception as e:
            result.errors.append(f"Error migrating legacy app config: {e}")
        
        return result
    
    def _migrate_old_backend_config(self, source_path: Path, result: MigrationResult) -> MigrationResult:
        """Migrate from old backend configuration format."""
        try:
            # Load old config
            with open(source_path, 'r') as f:
                old_config = json.load(f)
            
            # Check if this is already in the new format
            if 'version' in old_config and old_config['version'] == self.config_manager.config_set.version:
                result.warnings.append("Configuration is already in current format")
                result.success = True
                return result
            
            # Convert old format to new format
            migrated_config = BackendConfigSet()
            
            # Migrate backend configurations
            if 'backends' in old_config:
                for backend_name, config_data in old_config['backends'].items():
                    try:
                        # Convert old config format to new format
                        backend_config = self._convert_old_backend_config(backend_name, config_data)
                        migrated_config.backend_configs[backend_name] = backend_config
                        result.migrated_items.append(f"backend_config_{backend_name}")
                    except Exception as e:
                        result.warnings.append(f"Failed to migrate {backend_name}: {e}")
            
            # Migrate preferences
            if 'preferences' in old_config:
                try:
                    migrated_config.preferences = BackendPreferences.from_dict(old_config['preferences'])
                    result.migrated_items.append("preferences")
                except Exception as e:
                    result.warnings.append(f"Failed to migrate preferences: {e}")
            
            # Migrate fallback order
            if 'fallback_order' in old_config:
                migrated_config.custom_fallback_order = old_config['fallback_order']
                result.migrated_items.append("fallback_order")
            
            # Merge with existing configuration
            self._merge_migrated_config(migrated_config, result)
            
            result.success = True
            
        except Exception as e:
            result.errors.append(f"Error migrating old backend config: {e}")
        
        return result
    
    def _migrate_manual_settings(self, source_path: Path, result: MigrationResult) -> MigrationResult:
        """Migrate from manual settings files."""
        try:
            # Load settings
            with open(source_path, 'r') as f:
                settings = json.load(f)
            
            migrated_config = BackendConfigSet()
            
            # Try to extract backend-related settings
            backend_settings = {}
            
            # Look for common setting patterns
            for key, value in settings.items():
                if 'gpu' in key.lower():
                    if isinstance(value, bool):
                        # Apply GPU setting to all backends
                        for config in migrated_config.backend_configs.values():
                            config.gpu_enabled = value
                        result.migrated_items.append(f"gpu_setting_{key}")
                
                elif 'context' in key.lower() or 'ctx' in key.lower():
                    if isinstance(value, int) and value > 0:
                        # Apply context size to all backends
                        for config in migrated_config.backend_configs.values():
                            config.context_size = value
                        result.migrated_items.append(f"context_setting_{key}")
                
                elif 'thread' in key.lower():
                    if isinstance(value, int) and value > 0:
                        # Apply thread count to all backends
                        for config in migrated_config.backend_configs.values():
                            config.threads = value
                        result.migrated_items.append(f"thread_setting_{key}")
                
                elif 'batch' in key.lower():
                    if isinstance(value, int) and value > 0:
                        # Apply batch size to all backends
                        for config in migrated_config.backend_configs.values():
                            config.batch_size = value
                        result.migrated_items.append(f"batch_setting_{key}")
                
                elif key.lower() in ['backend', 'preferred_backend', 'default_backend']:
                    if isinstance(value, str) and value in [bt.value for bt in BackendType]:
                        migrated_config.preferences.preferred_backend = value
                        result.migrated_items.append("preferred_backend")
            
            # Merge with existing configuration
            if result.migrated_items:
                self._merge_migrated_config(migrated_config, result)
                result.success = True
            else:
                result.warnings.append("No recognizable backend settings found")
                result.success = True  # Not an error, just nothing to migrate
            
        except Exception as e:
            result.errors.append(f"Error migrating manual settings: {e}")
        
        return result
    
    def _migrate_external_config(self, source_path: Path, result: MigrationResult) -> MigrationResult:
        """Migrate from external configuration files."""
        try:
            # Load external config
            with open(source_path, 'r') as f:
                external_config = json.load(f)
            
            # Try to detect the format and migrate accordingly
            if 'backend_configs' in external_config or 'backends' in external_config:
                # Looks like a backend configuration
                return self._migrate_old_backend_config(source_path, result)
            elif 'ai_settings' in external_config or 'use_hardware_acceleration' in external_config:
                # Looks like an app configuration
                return self._migrate_legacy_app_config(source_path, result)
            else:
                # Treat as manual settings
                return self._migrate_manual_settings(source_path, result)
            
        except Exception as e:
            result.errors.append(f"Error migrating external config: {e}")
        
        return result
    
    def _convert_old_backend_config(self, backend_name: str, old_config: Dict[str, Any]) -> BackendConfig:
        """Convert old backend configuration format to new format."""
        # Create new config with defaults
        config = BackendConfig(name=backend_name)
        
        # Map old fields to new fields
        field_mapping = {
            'enabled': 'enabled',
            'priority': 'priority',
            'use_gpu': 'gpu_enabled',
            'gpu_enabled': 'gpu_enabled',
            'gpu_layers': 'gpu_layers',
            'n_gpu_layers': 'gpu_layers',
            'context_size': 'context_size',
            'n_ctx': 'context_size',
            'batch_size': 'batch_size',
            'n_batch': 'batch_size',
            'threads': 'threads',
            'n_threads': 'threads'
        }
        
        for old_field, new_field in field_mapping.items():
            if old_field in old_config:
                setattr(config, new_field, old_config[old_field])
        
        # Handle custom arguments
        if 'custom_args' in old_config:
            config.custom_args = old_config['custom_args']
        elif 'args' in old_config:
            config.custom_args = old_config['args']
        
        return config
    
    def _merge_migrated_config(self, migrated_config: BackendConfigSet, result: MigrationResult):
        """Merge migrated configuration with existing configuration."""
        try:
            # Get current configuration
            current_config = self.config_manager.config_set
            
            # Merge backend configurations
            for backend_name, config in migrated_config.backend_configs.items():
                if backend_name in current_config.backend_configs:
                    # Merge with existing config (migrated values take precedence for non-default values)
                    current = current_config.backend_configs[backend_name]
                    
                    # Only update if the migrated value is different from default
                    default_config = BackendConfig(name=backend_name)
                    
                    if config.enabled != default_config.enabled:
                        current.enabled = config.enabled
                    if config.priority != default_config.priority:
                        current.priority = config.priority
                    if config.gpu_enabled != default_config.gpu_enabled:
                        current.gpu_enabled = config.gpu_enabled
                    if config.gpu_layers != default_config.gpu_layers:
                        current.gpu_layers = config.gpu_layers
                    if config.context_size != default_config.context_size:
                        current.context_size = config.context_size
                    if config.batch_size != default_config.batch_size:
                        current.batch_size = config.batch_size
                    if config.threads != default_config.threads:
                        current.threads = config.threads
                    if config.custom_args:
                        current.custom_args.update(config.custom_args)
                else:
                    # Add new backend config
                    current_config.backend_configs[backend_name] = config
            
            # Merge preferences (migrated values take precedence for non-default values)
            default_prefs = BackendPreferences()
            current_prefs = current_config.preferences
            migrated_prefs = migrated_config.preferences
            
            if migrated_prefs.preferred_backend != default_prefs.preferred_backend:
                current_prefs.preferred_backend = migrated_prefs.preferred_backend
            if migrated_prefs.gpu_preference != default_prefs.gpu_preference:
                current_prefs.gpu_preference = migrated_prefs.gpu_preference
            if migrated_prefs.performance_priority != default_prefs.performance_priority:
                current_prefs.performance_priority = migrated_prefs.performance_priority
            
            # Merge fallback order
            if migrated_config.custom_fallback_order:
                current_config.custom_fallback_order = migrated_config.custom_fallback_order
            
            # Save the merged configuration
            if not self.config_manager.save():
                result.warnings.append("Failed to save merged configuration")
            
        except Exception as e:
            result.errors.append(f"Error merging migrated configuration: {e}")
    
    def auto_migrate_all(self, search_paths: Optional[List[Path]] = None, 
                        create_backups: bool = True) -> List[MigrationResult]:
        """
        Automatically detect and migrate all existing configurations.
        
        Args:
            search_paths: Optional list of paths to search
            create_backups: Whether to create backups of source files
            
        Returns:
            List of migration results
        """
        results = []
        
        try:
            # Detect existing configurations
            found_configs = self.detect_existing_configurations(search_paths)
            
            if not found_configs:
                self.logger.info("No existing configurations found to migrate")
                return results
            
            self.logger.info(f"Found {len(found_configs)} configurations to migrate")
            
            # Migrate each configuration
            for migration_type, config_path in found_configs:
                try:
                    result = self.migrate_configuration(migration_type, config_path, create_backups)
                    results.append(result)
                    
                    if result.success:
                        self.logger.info(f"Successfully migrated {migration_type.value} from {config_path}")
                    else:
                        self.logger.warning(f"Failed to migrate {migration_type.value} from {config_path}")
                        
                except Exception as e:
                    error_result = MigrationResult(
                        success=False,
                        migration_type=migration_type,
                        source_path=config_path,
                        backup_path=None,
                        migrated_items=[],
                        warnings=[],
                        errors=[f"Migration exception: {e}"]
                    )
                    results.append(error_result)
                    self.logger.error(f"Error migrating {config_path}: {e}")
            
            # Summary
            successful = sum(1 for r in results if r.success)
            self.logger.info(f"Migration completed: {successful}/{len(results)} successful")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error during auto-migration: {e}")
            return results
    
    def validate_migration(self, result: MigrationResult) -> Tuple[bool, List[str]]:
        """
        Validate that a migration was successful and complete.
        
        Args:
            result: Migration result to validate
            
        Returns:
            Tuple of (is_valid, validation_errors)
        """
        validation_errors = []
        
        try:
            if not result.success:
                validation_errors.append("Migration was not successful")
                return False, validation_errors
            
            # Check that configuration is valid
            is_valid, error = self.config_manager._validate_config_data(
                self.config_manager.config_set.to_dict()
            )
            
            if not is_valid:
                validation_errors.append(f"Migrated configuration is invalid: {error}")
            
            # Check that all expected items were migrated
            if not result.migrated_items:
                validation_errors.append("No items were migrated")
            
            # Check for critical errors
            critical_errors = [e for e in result.errors if 'critical' in e.lower() or 'fatal' in e.lower()]
            if critical_errors:
                validation_errors.extend(critical_errors)
            
            return len(validation_errors) == 0, validation_errors
            
        except Exception as e:
            validation_errors.append(f"Validation error: {e}")
            return False, validation_errors
    
    def create_migration_report(self, results: List[MigrationResult]) -> Dict[str, Any]:
        """
        Create a comprehensive migration report.
        
        Args:
            results: List of migration results
            
        Returns:
            Migration report dictionary
        """
        successful_migrations = [r for r in results if r.success]
        failed_migrations = [r for r in results if not r.success]
        
        all_migrated_items = []
        all_warnings = []
        all_errors = []
        
        for result in results:
            all_migrated_items.extend(result.migrated_items)
            all_warnings.extend(result.warnings)
            all_errors.extend(result.errors)
        
        report = {
            'summary': {
                'total_migrations': len(results),
                'successful': len(successful_migrations),
                'failed': len(failed_migrations),
                'success_rate': len(successful_migrations) / len(results) if results else 0
            },
            'migrated_items': {
                'total_count': len(all_migrated_items),
                'unique_items': list(set(all_migrated_items)),
                'item_counts': {item: all_migrated_items.count(item) for item in set(all_migrated_items)}
            },
            'issues': {
                'warnings': all_warnings,
                'errors': all_errors,
                'warning_count': len(all_warnings),
                'error_count': len(all_errors)
            },
            'migration_details': [result.to_dict() for result in results],
            'recommendations': self._generate_migration_recommendations(results)
        }
        
        return report
    
    def _generate_migration_recommendations(self, results: List[MigrationResult]) -> List[str]:
        """Generate recommendations based on migration results."""
        recommendations = []
        
        # Check for common issues
        all_errors = []
        for result in results:
            all_errors.extend(result.errors)
        
        if any('gpu' in error.lower() for error in all_errors):
            recommendations.append("Consider reviewing GPU settings after migration")
        
        if any('memory' in error.lower() for error in all_errors):
            recommendations.append("Consider optimizing memory settings for your hardware")
        
        if any('context' in error.lower() for error in all_errors):
            recommendations.append("Review context size settings for optimal performance")
        
        # Check for successful migrations
        successful_count = sum(1 for r in results if r.success)
        if successful_count > 0:
            recommendations.append("Test the migrated configuration with your models")
            recommendations.append("Consider creating a configuration preset for backup")
        
        if not recommendations:
            recommendations.append("Migration completed without specific recommendations")
        
        return recommendations