"""
Performance Optimization Integration

This module provides integration between the performance optimizer and the backend manager,
implementing automatic backend selection, dynamic GPU layer allocation, and performance caching.

Requirements: 1.3, 4.1, 4.2
"""

import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

from .performance_optimizer import PerformanceOptimizer, OptimizationRecommendation
from .backend_manager import BackendManager
from .hardware_detector import HardwareDetector
from .model_backends import BackendConfig, GenerationConfig, LoadingResult, HardwareInfo


class PerformanceIntegratedBackendManager(BackendManager):
    """
    Enhanced backend manager with integrated performance optimization.
    
    This class extends the base BackendManager to include:
    - Automatic backend selection based on model size and hardware
    - Dynamic GPU layer allocation optimization
    - Model-specific performance caching
    - Batch processing optimization for multiple requests
    """
    
    def __init__(self, hardware_detector: Optional[HardwareDetector] = None):
        """
        Initialize the performance-integrated backend manager.
        
        Args:
            hardware_detector: Hardware detector instance (creates new if None)
        """
        super().__init__(hardware_detector)
        
        # Initialize performance optimizer
        self.performance_optimizer = PerformanceOptimizer(self.hardware_detector)
        self.performance_optimizer.start()
        
        # Performance tracking
        self._model_performance_history: Dict[str, List[Dict[str, Any]]] = {}
        self._optimization_cache: Dict[str, OptimizationRecommendation] = {}
        
        self.logger.info("Performance-integrated backend manager initialized")
    
    def load_model_optimized(self, model_path: str, 
                           hardware_preference: str = 'auto',
                           performance_target: str = 'balanced',
                           force_backend: Optional[str] = None) -> LoadingResult:
        """
        Load a model with automatic performance optimization.
        
        Args:
            model_path: Path to the model file
            hardware_preference: Hardware preference ('auto', 'gpu', 'cpu')
            performance_target: Performance target ('speed', 'balanced', 'quality')
            force_backend: Force specific backend (overrides optimization)
            
        Returns:
            LoadingResult with optimization details
        """
        self.logger.info(f"Loading model with optimization: {Path(model_path).name}")
        
        # Get or create optimization recommendation
        cache_key = f"{model_path}_{hardware_preference}_{performance_target}"
        
        if force_backend:
            # Use forced backend without optimization
            recommendation = None
            backend_name = force_backend
        elif cache_key in self._optimization_cache:
            # Use cached recommendation
            recommendation = self._optimization_cache[cache_key]
            backend_name = recommendation.recommended_backend
            self.logger.info(f"Using cached optimization for {backend_name}")
        else:
            # Get new optimization recommendation
            available_backends = self.get_available_backends()
            if not available_backends:
                return LoadingResult(
                    success=False,
                    backend_used="none",
                    hardware_used="none",
                    load_time=0.0,
                    error_message="No backends available"
                )
            
            recommendation = self.performance_optimizer.get_optimal_backend(
                model_path=model_path,
                available_backends=available_backends,
                hardware_preference=hardware_preference
            )
            
            # Cache the recommendation
            self._optimization_cache[cache_key] = recommendation
            backend_name = recommendation.recommended_backend
            
            self.logger.info(f"Optimization recommendation: {backend_name} (confidence: {recommendation.confidence_score:.2%})")
            for reason in recommendation.reasoning:
                self.logger.debug(f"  - {reason}")
        
        # Apply performance optimizations to backend configuration
        if recommendation:
            optimized_config = self._apply_performance_optimizations(
                recommendation.recommended_config,
                model_path,
                backend_name,
                performance_target
            )
        else:
            # Use default config for forced backend
            optimized_config = self.configs.get(backend_name, BackendConfig(name=backend_name))
        
        # Update backend configuration
        self.configs[backend_name] = optimized_config
        
        # Load model using optimized configuration
        start_time = time.time()
        result = super().load_model(model_path, backend_name)
        
        # Record performance metrics
        if result.success:
            load_time_ms = (time.time() - start_time) * 1000
            
            # Get hardware info for performance recording
            hardware_info = self.hardware_detector.get_hardware_info()
            hardware_config = {
                'gpu_count': hardware_info.gpu_count,
                'total_vram': hardware_info.total_vram,
                'cpu_cores': hardware_info.cpu_cores,
                'total_ram': hardware_info.total_ram
            }
            
            # Record performance for future optimization
            self.performance_optimizer.record_performance(
                backend_name=backend_name,
                model_path=model_path,
                load_time_ms=load_time_ms,
                memory_usage_mb=result.memory_usage,
                tokens_per_second=0.0,  # Will be updated during generation
                success=True,
                hardware_config=hardware_config
            )
            
            # Update result with optimization info
            result.model_info.update({
                'optimization_applied': True,
                'performance_target': performance_target,
                'gpu_layers_optimized': optimized_config.gpu_layers,
                'batch_size_optimized': optimized_config.batch_size,
                'context_size_optimized': optimized_config.context_size,
                'recommendation_confidence': recommendation.confidence_score if recommendation else 1.0
            })
            
            self.logger.info(f"Model loaded with optimization in {load_time_ms:.1f}ms")
        else:
            # Record failure for learning
            self.performance_optimizer.record_performance(
                backend_name=backend_name,
                model_path=model_path,
                load_time_ms=0.0,
                memory_usage_mb=0,
                tokens_per_second=0.0,
                success=False
            )
        
        return result
    
    def _apply_performance_optimizations(self, base_config: BackendConfig,
                                       model_path: str, backend_name: str,
                                       performance_target: str) -> BackendConfig:
        """Apply performance optimizations to backend configuration."""
        # Create optimized configuration
        optimized_config = BackendConfig(
            name=base_config.name,
            enabled=base_config.enabled,
            priority=base_config.priority,
            gpu_enabled=base_config.gpu_enabled,
            gpu_layers=base_config.gpu_layers,
            context_size=base_config.context_size,
            batch_size=base_config.batch_size,
            threads=base_config.threads,
            custom_args=base_config.custom_args.copy()
        )
        
        # Get hardware info
        hardware_info = self.hardware_detector.get_hardware_info()
        
        # Optimize GPU layers
        if optimized_config.gpu_enabled and hardware_info.total_vram > 0:
            optimal_layers = self.performance_optimizer.optimize_gpu_layers(
                model_path=model_path,
                backend_name=backend_name,
                available_vram_mb=hardware_info.total_vram
            )
            optimized_config.gpu_layers = optimal_layers
            self.logger.info(f"Optimized GPU layers: {optimal_layers}")
        
        # Optimize batch size
        optimal_batch_size = self.performance_optimizer.get_dynamic_batch_size(
            model_path=model_path,
            backend_name=backend_name,
            available_memory_mb=hardware_info.total_ram,
            concurrent_requests=1  # Default to 1, could be made configurable
        )
        optimized_config.batch_size = optimal_batch_size
        self.logger.info(f"Optimized batch size: {optimal_batch_size}")
        
        # Optimize context size
        optimal_context_size = self.performance_optimizer.get_adaptive_context_size(
            model_path=model_path,
            backend_name=backend_name,
            available_memory_mb=hardware_info.total_ram,
            target_performance=performance_target
        )
        optimized_config.context_size = optimal_context_size
        self.logger.info(f"Optimized context size: {optimal_context_size}")
        
        return optimized_config
    
    def generate_text_optimized(self, prompt: str, config: GenerationConfig,
                              use_batch_processing: bool = True) -> str:
        """
        Generate text with performance optimizations.
        
        Args:
            prompt: Input text prompt
            config: Generation configuration
            use_batch_processing: Whether to use batch processing optimization
            
        Returns:
            Generated text
        """
        if not self.current_backend:
            raise ValueError("No model is currently loaded")
        
        start_time = time.time()
        
        if use_batch_processing and len(prompt) < 1000:  # Use batching for shorter prompts
            # Use batch processor for optimization
            request_id = self.performance_optimizer.batch_processor.submit_request(
                prompt=prompt,
                generation_config=config,
                priority=1
            )
            
            result = self.performance_optimizer.batch_processor.get_result(
                request_id, 
                timeout=30.0
            )
            
            if result is None:
                # Fallback to direct generation
                result = super().generate_text(prompt, config)
        else:
            # Use direct generation for longer prompts or when batching is disabled
            result = super().generate_text(prompt, config)
        
        # Record generation performance
        generation_time = time.time() - start_time
        if result and self.current_model_path:
            # Estimate tokens generated (rough approximation)
            tokens_generated = len(result.split())
            tokens_per_second = tokens_generated / generation_time if generation_time > 0 else 0
            
            # Update performance cache with generation metrics
            self.performance_optimizer.record_performance(
                backend_name=self.current_backend.config.name,
                model_path=self.current_model_path,
                load_time_ms=0.0,  # Not applicable for generation
                memory_usage_mb=0,  # Would need to measure actual memory usage
                tokens_per_second=tokens_per_second,
                success=True
            )
        
        return result
    
    def get_performance_insights(self) -> Dict[str, Any]:
        """Get comprehensive performance insights and recommendations."""
        insights = {
            'current_model': None,
            'backend_performance': {},
            'optimization_recommendations': [],
            'hardware_utilization': {},
            'cache_statistics': {}
        }
        
        if self.current_model_path:
            insights['current_model'] = {
                'path': self.current_model_path,
                'backend': self.current_backend.config.name if self.current_backend else None,
                'config': self.current_backend.config.to_dict() if self.current_backend else None
            }
            
            # Get model-specific insights
            model_insights = self.performance_optimizer.get_optimization_insights(self.current_model_path)
            insights['optimization_recommendations'] = model_insights['recommendations']
            insights['backend_performance'] = model_insights['performance_trends']
        
        # Hardware utilization
        hardware_info = self.hardware_detector.get_hardware_info()
        insights['hardware_utilization'] = {
            'gpu_count': hardware_info.gpu_count,
            'total_vram_mb': hardware_info.total_vram,
            'cpu_cores': hardware_info.cpu_cores,
            'total_ram_mb': hardware_info.total_ram,
            'recommended_backend': hardware_info.recommended_backend
        }
        
        # Cache statistics
        cache_stats = self.performance_optimizer.get_performance_stats()
        insights['cache_statistics'] = {
            'total_models_cached': cache_stats.get('total_models', 0),
            'total_backend_profiles': cache_stats.get('total_backend_profiles', 0),
            'optimization_cache_size': len(self._optimization_cache)
        }
        
        return insights
    
    def benchmark_current_setup(self, num_iterations: int = 5) -> Dict[str, Any]:
        """
        Benchmark the current model and backend setup.
        
        Args:
            num_iterations: Number of benchmark iterations
            
        Returns:
            Dictionary with benchmark results
        """
        if not self.current_backend or not self.current_model_path:
            raise ValueError("No model loaded for benchmarking")
        
        self.logger.info(f"Running benchmark with {num_iterations} iterations...")
        
        # Test prompts of varying lengths
        test_prompts = [
            "Hello",
            "What is artificial intelligence?",
            "Explain the concept of machine learning in detail, including its applications and benefits.",
            "Write a comprehensive essay about the future of technology and its impact on society, covering topics such as artificial intelligence, automation, and digital transformation."
        ]
        
        results = {
            'backend': self.current_backend.config.name,
            'model_path': self.current_model_path,
            'iterations': num_iterations,
            'prompt_results': [],
            'average_metrics': {}
        }
        
        all_tokens_per_sec = []
        all_response_times = []
        
        for prompt in test_prompts:
            prompt_results = {
                'prompt_length': len(prompt),
                'iterations': [],
                'average_tokens_per_sec': 0,
                'average_response_time': 0
            }
            
            tokens_per_sec_list = []
            response_times = []
            
            for i in range(num_iterations):
                try:
                    start_time = time.time()
                    
                    # Generate response
                    config = GenerationConfig(max_tokens=100, temperature=0.7)
                    response = self.generate_text_optimized(prompt, config, use_batch_processing=False)
                    
                    response_time = time.time() - start_time
                    tokens_generated = len(response.split()) if response else 0
                    tokens_per_sec = tokens_generated / response_time if response_time > 0 else 0
                    
                    iteration_result = {
                        'iteration': i + 1,
                        'response_time': response_time,
                        'tokens_generated': tokens_generated,
                        'tokens_per_sec': tokens_per_sec,
                        'success': bool(response)
                    }
                    
                    prompt_results['iterations'].append(iteration_result)
                    
                    if response:
                        tokens_per_sec_list.append(tokens_per_sec)
                        response_times.append(response_time)
                        all_tokens_per_sec.append(tokens_per_sec)
                        all_response_times.append(response_time)
                
                except Exception as e:
                    self.logger.error(f"Benchmark iteration {i+1} failed: {e}")
                    prompt_results['iterations'].append({
                        'iteration': i + 1,
                        'error': str(e),
                        'success': False
                    })
            
            # Calculate averages for this prompt
            if tokens_per_sec_list:
                prompt_results['average_tokens_per_sec'] = sum(tokens_per_sec_list) / len(tokens_per_sec_list)
                prompt_results['average_response_time'] = sum(response_times) / len(response_times)
            
            results['prompt_results'].append(prompt_results)
        
        # Calculate overall averages
        if all_tokens_per_sec:
            results['average_metrics'] = {
                'overall_tokens_per_sec': sum(all_tokens_per_sec) / len(all_tokens_per_sec),
                'overall_response_time': sum(all_response_times) / len(all_response_times),
                'success_rate': len(all_tokens_per_sec) / (len(test_prompts) * num_iterations),
                'total_successful_generations': len(all_tokens_per_sec)
            }
        
        self.logger.info("Benchmark completed")
        return results
    
    def export_performance_report(self, output_path: str):
        """Export comprehensive performance report."""
        self.performance_optimizer.export_performance_report(
            output_path=output_path,
            model_path=self.current_model_path
        )
    
    def cleanup(self):
        """Clean up resources including performance optimizer."""
        self.logger.info("Cleaning up performance-integrated backend manager...")
        
        # Stop performance optimizer
        self.performance_optimizer.stop()
        
        # Clear caches
        self._optimization_cache.clear()
        self._model_performance_history.clear()
        
        # Call parent cleanup
        super().cleanup()
        
        self.logger.info("Performance-integrated backend manager cleanup complete")


# Factory function for easy integration
def create_optimized_backend_manager(hardware_detector: Optional[HardwareDetector] = None) -> PerformanceIntegratedBackendManager:
    """
    Create a performance-optimized backend manager.
    
    Args:
        hardware_detector: Hardware detector instance (creates new if None)
        
    Returns:
        PerformanceIntegratedBackendManager instance
    """
    return PerformanceIntegratedBackendManager(hardware_detector)