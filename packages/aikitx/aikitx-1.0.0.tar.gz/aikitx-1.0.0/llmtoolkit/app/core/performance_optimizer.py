"""
Performance Optimization Features

This module provides advanced performance optimization features including:
- Automatic backend selection based on model size and hardware
- Dynamic GPU layer allocation optimization
- Model-specific performance caching
- Batch processing optimization for multiple requests

Requirements: 1.3, 4.1, 4.2
"""

import logging
import time
import json
import threading
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict, deque
import hashlib

from .model_backends import BackendType, BackendConfig, HardwareInfo, LoadingResult, GenerationConfig
from .hardware_detector import HardwareDetector
from .monitoring import PerformanceMetrics


@dataclass
class ModelProfile:
    """Profile information for a specific model."""
    model_path: str
    model_hash: str
    size_mb: int
    parameter_count: Optional[int] = None
    quantization: Optional[str] = None
    architecture: Optional[str] = None
    context_length: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelProfile':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class BackendPerformanceProfile:
    """Performance profile for a backend with a specific model."""
    backend_name: str
    model_hash: str
    hardware_config: Dict[str, Any]
    load_time_ms: float
    memory_usage_mb: int
    tokens_per_second: float
    success_rate: float
    last_updated: float
    usage_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackendPerformanceProfile':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class OptimizationRecommendation:
    """Recommendation for optimal backend and configuration."""
    recommended_backend: str
    recommended_config: BackendConfig
    expected_performance: Dict[str, float]
    confidence_score: float
    reasoning: List[str]
    alternative_backends: List[Tuple[str, BackendConfig, float]]


@dataclass
class BatchRequest:
    """Request for batch processing."""
    request_id: str
    prompt: str
    generation_config: GenerationConfig
    priority: int = 0
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class ModelPerformanceCache:
    """Cache for model-specific performance data."""
    
    def __init__(self, cache_file: Optional[str] = None):
        """
        Initialize the performance cache.
        
        Args:
            cache_file: Path to cache file (optional)
        """
        self.logger = logging.getLogger("performance.cache")
        self.cache_file = cache_file or "model_performance_cache.json"
        self._lock = threading.RLock()
        
        # Cache data structures
        self.model_profiles: Dict[str, ModelProfile] = {}
        self.backend_profiles: Dict[str, Dict[str, BackendPerformanceProfile]] = defaultdict(dict)
        self.optimization_history: deque = deque(maxlen=1000)
        
        # Load existing cache
        self._load_cache()
    
    def _calculate_model_hash(self, model_path: str) -> str:
        """Calculate hash for model file."""
        try:
            path = Path(model_path)
            if not path.exists():
                return ""
            
            # Use file size and modification time for quick hash
            stat = path.stat()
            hash_input = f"{model_path}_{stat.st_size}_{stat.st_mtime}"
            return hashlib.md5(hash_input.encode()).hexdigest()
        except Exception as e:
            self.logger.warning(f"Error calculating model hash: {e}")
            return ""
    
    def get_model_profile(self, model_path: str) -> Optional[ModelProfile]:
        """Get model profile from cache."""
        model_hash = self._calculate_model_hash(model_path)
        if not model_hash:
            return None
        
        with self._lock:
            return self.model_profiles.get(model_hash)
    
    def store_model_profile(self, model_path: str, size_mb: int, 
                          parameter_count: Optional[int] = None,
                          quantization: Optional[str] = None,
                          architecture: Optional[str] = None,
                          context_length: Optional[int] = None):
        """Store model profile in cache."""
        model_hash = self._calculate_model_hash(model_path)
        if not model_hash:
            return
        
        profile = ModelProfile(
            model_path=model_path,
            model_hash=model_hash,
            size_mb=size_mb,
            parameter_count=parameter_count,
            quantization=quantization,
            architecture=architecture,
            context_length=context_length
        )
        
        with self._lock:
            self.model_profiles[model_hash] = profile
            self._save_cache()
    
    def store_backend_performance(self, backend_name: str, model_path: str,
                                hardware_config: Dict[str, Any],
                                load_time_ms: float, memory_usage_mb: int,
                                tokens_per_second: float, success_rate: float):
        """Store backend performance profile."""
        model_hash = self._calculate_model_hash(model_path)
        if not model_hash:
            return
        
        profile = BackendPerformanceProfile(
            backend_name=backend_name,
            model_hash=model_hash,
            hardware_config=hardware_config,
            load_time_ms=load_time_ms,
            memory_usage_mb=memory_usage_mb,
            tokens_per_second=tokens_per_second,
            success_rate=success_rate,
            last_updated=time.time(),
            usage_count=1
        )
        
        with self._lock:
            if model_hash not in self.backend_profiles:
                self.backend_profiles[model_hash] = {}
            
            # Update existing profile or create new one
            key = f"{backend_name}_{hash(str(hardware_config))}"
            if key in self.backend_profiles[model_hash]:
                existing = self.backend_profiles[model_hash][key]
                # Update with weighted average
                weight = existing.usage_count / (existing.usage_count + 1)
                profile.load_time_ms = existing.load_time_ms * weight + load_time_ms * (1 - weight)
                profile.memory_usage_mb = int(existing.memory_usage_mb * weight + memory_usage_mb * (1 - weight))
                profile.tokens_per_second = existing.tokens_per_second * weight + tokens_per_second * (1 - weight)
                profile.success_rate = existing.success_rate * weight + success_rate * (1 - weight)
                profile.usage_count = existing.usage_count + 1
            
            self.backend_profiles[model_hash][key] = profile
            self._save_cache()
    
    def get_backend_performance(self, model_path: str, backend_name: Optional[str] = None) -> Dict[str, BackendPerformanceProfile]:
        """Get backend performance profiles for a model."""
        model_hash = self._calculate_model_hash(model_path)
        if not model_hash:
            return {}
        
        with self._lock:
            profiles = self.backend_profiles.get(model_hash, {})
            
            if backend_name:
                # Filter by backend name
                return {k: v for k, v in profiles.items() if v.backend_name == backend_name}
            
            return profiles
    
    def _load_cache(self):
        """Load cache from file."""
        try:
            cache_path = Path(self.cache_file)
            if cache_path.exists():
                with open(cache_path, 'r') as f:
                    data = json.load(f)
                
                # Load model profiles
                for model_hash, profile_data in data.get('model_profiles', {}).items():
                    self.model_profiles[model_hash] = ModelProfile.from_dict(profile_data)
                
                # Load backend profiles
                for model_hash, backend_data in data.get('backend_profiles', {}).items():
                    self.backend_profiles[model_hash] = {}
                    for key, profile_data in backend_data.items():
                        self.backend_profiles[model_hash][key] = BackendPerformanceProfile.from_dict(profile_data)
                
                self.logger.info(f"Loaded performance cache with {len(self.model_profiles)} models")
        
        except Exception as e:
            self.logger.warning(f"Error loading performance cache: {e}")
    
    def _save_cache(self):
        """Save cache to file."""
        try:
            data = {
                'model_profiles': {k: v.to_dict() for k, v in self.model_profiles.items()},
                'backend_profiles': {
                    model_hash: {k: v.to_dict() for k, v in profiles.items()}
                    for model_hash, profiles in self.backend_profiles.items()
                }
            }
            
            cache_path = Path(self.cache_file)
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=2)
        
        except Exception as e:
            self.logger.warning(f"Error saving performance cache: {e}")


class BatchProcessor:
    """Batch processing optimization for multiple requests."""
    
    def __init__(self, max_batch_size: int = 8, max_wait_time: float = 0.1):
        """
        Initialize batch processor.
        
        Args:
            max_batch_size: Maximum number of requests to batch together
            max_wait_time: Maximum time to wait for batching (seconds)
        """
        self.logger = logging.getLogger("performance.batch")
        self.max_batch_size = max_batch_size
        self.max_wait_time = max_wait_time
        
        self._pending_requests: List[BatchRequest] = []
        self._processing_queue = deque()
        self._results: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)
        self._worker_thread = None
        self._running = False
    
    def start(self):
        """Start the batch processor."""
        if self._running:
            return
        
        self._running = True
        self._worker_thread = threading.Thread(target=self._process_batches, daemon=True)
        self._worker_thread.start()
        self.logger.info("Batch processor started")
    
    def stop(self):
        """Stop the batch processor."""
        if not self._running:
            return
        
        self._running = False
        with self._condition:
            self._condition.notify_all()
        
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
        
        self.logger.info("Batch processor stopped")
    
    def submit_request(self, prompt: str, generation_config: GenerationConfig, 
                      priority: int = 0) -> str:
        """
        Submit a request for batch processing.
        
        Args:
            prompt: Text prompt for generation
            generation_config: Generation configuration
            priority: Request priority (higher = more important)
            
        Returns:
            Request ID for tracking
        """
        request_id = f"batch_{time.time()}_{hash(prompt) % 10000}"
        
        request = BatchRequest(
            request_id=request_id,
            prompt=prompt,
            generation_config=generation_config,
            priority=priority
        )
        
        with self._condition:
            self._pending_requests.append(request)
            self._pending_requests.sort(key=lambda x: (-x.priority, x.timestamp))
            self._condition.notify()
        
        return request_id
    
    def get_result(self, request_id: str, timeout: float = 30.0) -> Optional[str]:
        """
        Get result for a request.
        
        Args:
            request_id: Request ID from submit_request
            timeout: Maximum time to wait for result
            
        Returns:
            Generated text or None if timeout/error
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            with self._lock:
                if request_id in self._results:
                    result = self._results.pop(request_id)
                    if isinstance(result, Exception):
                        raise result
                    return result
            
            time.sleep(0.01)  # Small sleep to avoid busy waiting
        
        return None
    
    def _process_batches(self):
        """Main batch processing loop."""
        while self._running:
            try:
                batch = self._collect_batch()
                if batch:
                    self._process_batch(batch)
                else:
                    # Wait for new requests
                    with self._condition:
                        self._condition.wait(timeout=self.max_wait_time)
            
            except Exception as e:
                self.logger.error(f"Error in batch processing: {e}")
    
    def _collect_batch(self) -> List[BatchRequest]:
        """Collect requests for batching."""
        with self._lock:
            if not self._pending_requests:
                return []
            
            # Check if we should wait for more requests
            oldest_request = self._pending_requests[0]
            wait_time = time.time() - oldest_request.timestamp
            
            if len(self._pending_requests) < self.max_batch_size and wait_time < self.max_wait_time:
                return []
            
            # Collect batch
            batch_size = min(self.max_batch_size, len(self._pending_requests))
            batch = self._pending_requests[:batch_size]
            self._pending_requests = self._pending_requests[batch_size:]
            
            return batch
    
    def _process_batch(self, batch: List[BatchRequest]):
        """Process a batch of requests."""
        self.logger.debug(f"Processing batch of {len(batch)} requests")
        
        # Group requests by similar generation configs for better batching
        config_groups = self._group_requests_by_config(batch)
        
        for config_key, requests in config_groups.items():
            try:
                # Process similar requests together
                self._process_similar_requests(requests)
            except Exception as e:
                self.logger.error(f"Error processing batch group {config_key}: {e}")
                # Mark all requests in this group as failed
                for request in requests:
                    with self._lock:
                        self._results[request.request_id] = e
    
    def _group_requests_by_config(self, batch: List[BatchRequest]) -> Dict[str, List[BatchRequest]]:
        """Group requests by similar generation configurations."""
        groups = {}
        
        for request in batch:
            # Create a key based on generation config
            config = request.generation_config
            key = f"{config.max_tokens}_{config.temperature}_{config.top_p}_{config.top_k}"
            
            if key not in groups:
                groups[key] = []
            groups[key].append(request)
        
        return groups
    
    def _process_similar_requests(self, requests: List[BatchRequest]):
        """Process requests with similar configurations together."""
        # For now, process individually but this could be enhanced
        # to use actual backend batching capabilities
        for request in requests:
            try:
                # Simulate processing time based on request complexity
                processing_time = len(request.prompt) * 0.001  # 1ms per character
                time.sleep(min(processing_time, 0.1))  # Cap at 100ms for simulation
                
                # Generate response (placeholder)
                result = f"Generated response for: {request.prompt[:50]}..."
                
                with self._lock:
                    self._results[request.request_id] = result
            
            except Exception as e:
                self.logger.error(f"Error processing request {request.request_id}: {e}")
                with self._lock:
                    self._results[request.request_id] = e
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get statistics about the batch processing queue."""
        with self._lock:
            return {
                'pending_requests': len(self._pending_requests),
                'completed_results': len(self._results),
                'max_batch_size': self.max_batch_size,
                'max_wait_time': self.max_wait_time,
                'is_running': self._running
            }


class PerformanceOptimizer:
    """Main performance optimization coordinator."""
    
    def __init__(self, hardware_detector: HardwareDetector):
        """
        Initialize the performance optimizer.
        
        Args:
            hardware_detector: Hardware detection instance
        """
        self.logger = logging.getLogger("performance.optimizer")
        self.hardware_detector = hardware_detector
        self.performance_cache = ModelPerformanceCache()
        self.batch_processor = BatchProcessor()
        
        # GPU layer allocation cache
        self._gpu_layer_cache: Dict[str, int] = {}
        self._lock = threading.Lock()
    
    def start(self):
        """Start the performance optimizer."""
        self.batch_processor.start()
        self.logger.info("Performance optimizer started")
    
    def stop(self):
        """Stop the performance optimizer."""
        self.batch_processor.stop()
        self.logger.info("Performance optimizer stopped")
    
    def get_optimal_backend(self, model_path: str, 
                          available_backends: List[str],
                          hardware_preference: str = 'auto') -> OptimizationRecommendation:
        """
        Get optimal backend recommendation for a model.
        
        Args:
            model_path: Path to the model file
            available_backends: List of available backend names
            hardware_preference: Hardware preference ('auto', 'gpu', 'cpu')
            
        Returns:
            OptimizationRecommendation with best backend and configuration
        """
        self.logger.info(f"Finding optimal backend for model: {Path(model_path).name}")
        
        # Get model profile
        model_profile = self.performance_cache.get_model_profile(model_path)
        if not model_profile:
            # Create basic profile from file info
            try:
                model_size = Path(model_path).stat().st_size // (1024 * 1024)
                self.performance_cache.store_model_profile(model_path, model_size)
                model_profile = self.performance_cache.get_model_profile(model_path)
            except Exception as e:
                self.logger.warning(f"Could not create model profile: {e}")
                model_size = 1000  # Default size
        else:
            model_size = model_profile.size_mb
        
        # Get hardware info
        hardware_info = self.hardware_detector.get_hardware_info()
        
        # Get performance history for this model
        backend_performances = self.performance_cache.get_backend_performance(model_path)
        
        # Score each available backend
        backend_scores = []
        
        for backend_name in available_backends:
            score, config, reasoning = self._score_backend(
                backend_name, model_size, hardware_info, 
                backend_performances, hardware_preference
            )
            
            backend_scores.append((backend_name, config, score, reasoning))
        
        # Sort by score (highest first)
        backend_scores.sort(key=lambda x: x[2], reverse=True)
        
        if not backend_scores:
            raise ValueError("No available backends to recommend")
        
        # Get best recommendation
        best_backend, best_config, best_score, best_reasoning = backend_scores[0]
        
        # Calculate expected performance
        expected_performance = self._estimate_performance(
            best_backend, model_size, hardware_info, backend_performances
        )
        
        # Get alternatives
        alternatives = [(name, config, score) for name, config, score, _ in backend_scores[1:3]]
        
        return OptimizationRecommendation(
            recommended_backend=best_backend,
            recommended_config=best_config,
            expected_performance=expected_performance,
            confidence_score=best_score / 100.0,
            reasoning=best_reasoning,
            alternative_backends=alternatives
        )
    
    def _score_backend(self, backend_name: str, model_size_mb: int, 
                      hardware_info: HardwareInfo, 
                      backend_performances: Dict[str, BackendPerformanceProfile],
                      hardware_preference: str) -> Tuple[float, 'BackendConfig', List[str]]:
        """Score a backend for the given model and hardware."""
        from .model_backends import BackendConfig
        
        score = 0.0
        reasoning = []
        
        # Base scores by backend type (based on general reliability)
        base_scores = {
            'ctransformers': 85,
            'transformers': 80,
            'llamafile': 75,
            'llama-cpp-python': 70
        }
        
        score += base_scores.get(backend_name, 50)
        reasoning.append(f"Base reliability score: {base_scores.get(backend_name, 50)}")
        
        # Hardware compatibility scoring
        gpu_bonus = 0
        if hardware_info.gpu_count > 0 and hardware_preference != 'cpu':
            if backend_name == 'ctransformers':
                # ctransformers has good GPU support
                gpu_bonus = 15
                reasoning.append("GPU acceleration available with ctransformers")
            elif backend_name == 'transformers':
                # transformers has excellent GPU support
                gpu_bonus = 20
                reasoning.append("Excellent GPU support with transformers")
            elif backend_name == 'llamafile':
                # llamafile has automatic GPU detection
                gpu_bonus = 10
                reasoning.append("Automatic GPU detection with llamafile")
            elif backend_name == 'llama-cpp-python':
                # llama-cpp-python has GPU support but installation issues
                gpu_bonus = 5
                reasoning.append("GPU support available but may have installation issues")
        
        score += gpu_bonus
        
        # Model size considerations
        if model_size_mb > 8000:  # Large models (>8GB)
            if backend_name == 'transformers':
                score += 10
                reasoning.append("Transformers handles large models well")
            elif backend_name == 'llamafile':
                score += 5
                reasoning.append("Llamafile can handle large models")
        elif model_size_mb < 2000:  # Small models (<2GB)
            if backend_name == 'ctransformers':
                score += 5
                reasoning.append("ctransformers efficient for smaller models")
        
        # Memory considerations
        available_vram = hardware_info.total_vram
        if available_vram > 0:
            if available_vram >= model_size_mb * 1.5:
                # Enough VRAM for full GPU loading
                if backend_name in ['ctransformers', 'transformers']:
                    score += 10
                    reasoning.append("Sufficient VRAM for full GPU acceleration")
            elif available_vram >= model_size_mb:
                # Partial GPU loading possible
                score += 5
                reasoning.append("Sufficient VRAM for partial GPU acceleration")
        
        # Performance history bonus
        matching_profiles = [p for p in backend_performances.values() 
                           if p.backend_name == backend_name]
        if matching_profiles:
            avg_success_rate = sum(p.success_rate for p in matching_profiles) / len(matching_profiles)
            avg_tokens_per_sec = sum(p.tokens_per_second for p in matching_profiles) / len(matching_profiles)
            
            score += avg_success_rate * 10  # Up to 10 points for success rate
            score += min(avg_tokens_per_sec / 10, 10)  # Up to 10 points for speed
            reasoning.append(f"Historical performance: {avg_success_rate:.1%} success, {avg_tokens_per_sec:.1f} tokens/sec")
        
        # Create optimal configuration
        config = self._create_optimal_config(
            backend_name, model_size_mb, hardware_info, hardware_preference
        )
        
        return score, config, reasoning
    
    def _create_optimal_config(self, backend_name: str, model_size_mb: int,
                             hardware_info: HardwareInfo, 
                             hardware_preference: str) -> 'BackendConfig':
        """Create optimal configuration for a backend."""
        from .model_backends import BackendConfig
        
        # Get optimal settings from hardware detector
        optimal_settings = self.hardware_detector.get_optimal_settings(backend_name, model_size_mb)
        
        # Override based on hardware preference
        if hardware_preference == 'cpu':
            optimal_settings['gpu_enabled'] = False
            optimal_settings['gpu_layers'] = 0
        elif hardware_preference == 'gpu' and hardware_info.gpu_count == 0:
            self.logger.warning("GPU preference specified but no GPUs detected")
        
        return BackendConfig(
            name=backend_name,
            enabled=True,
            priority=1,
            gpu_enabled=optimal_settings.get('gpu_enabled', True),
            gpu_layers=optimal_settings.get('gpu_layers', -1),
            context_size=optimal_settings.get('context_size', 4096),
            batch_size=optimal_settings.get('batch_size', 512),
            threads=optimal_settings.get('threads', -1),
            custom_args={}
        )
    
    def _estimate_performance(self, backend_name: str, model_size_mb: int,
                            hardware_info: HardwareInfo,
                            backend_performances: Dict[str, BackendPerformanceProfile]) -> Dict[str, float]:
        """Estimate expected performance for a backend."""
        # Get historical performance data
        matching_profiles = [p for p in backend_performances.values() 
                           if p.backend_name == backend_name]
        
        if matching_profiles:
            # Use historical data
            avg_load_time = sum(p.load_time_ms for p in matching_profiles) / len(matching_profiles)
            avg_memory_usage = sum(p.memory_usage_mb for p in matching_profiles) / len(matching_profiles)
            avg_tokens_per_sec = sum(p.tokens_per_second for p in matching_profiles) / len(matching_profiles)
        else:
            # Estimate based on model size and hardware
            if hardware_info.gpu_count > 0 and hardware_info.total_vram >= model_size_mb:
                # GPU acceleration available
                avg_load_time = model_size_mb * 0.1  # ~0.1ms per MB
                avg_memory_usage = model_size_mb * 1.2  # 20% overhead
                avg_tokens_per_sec = 50.0  # Reasonable GPU speed
            else:
                # CPU only
                avg_load_time = model_size_mb * 0.5  # Slower loading
                avg_memory_usage = model_size_mb * 1.5  # More overhead
                avg_tokens_per_sec = 10.0  # Slower generation
        
        return {
            'estimated_load_time_ms': avg_load_time,
            'estimated_memory_usage_mb': avg_memory_usage,
            'estimated_tokens_per_second': avg_tokens_per_sec
        }
    
    def optimize_gpu_layers(self, model_path: str, backend_name: str,
                          available_vram_mb: int) -> int:
        """
        Optimize GPU layer allocation for a model.
        
        Args:
            model_path: Path to the model file
            backend_name: Backend name
            available_vram_mb: Available VRAM in MB
            
        Returns:
            Optimal number of GPU layers
        """
        cache_key = f"{model_path}_{backend_name}_{available_vram_mb}"
        
        with self._lock:
            if cache_key in self._gpu_layer_cache:
                return self._gpu_layer_cache[cache_key]
        
        # Get model profile
        model_profile = self.performance_cache.get_model_profile(model_path)
        if not model_profile:
            model_size_mb = Path(model_path).stat().st_size // (1024 * 1024)
        else:
            model_size_mb = model_profile.size_mb
        
        # Estimate optimal GPU layers
        if available_vram_mb <= 0:
            optimal_layers = 0
        else:
            # Estimate total layers (varies by model architecture)
            if model_profile and model_profile.parameter_count:
                # Rough estimation: larger models have more layers
                if model_profile.parameter_count > 30_000_000_000:  # 30B+
                    total_layers = 80
                elif model_profile.parameter_count > 13_000_000_000:  # 13B+
                    total_layers = 60
                elif model_profile.parameter_count > 7_000_000_000:  # 7B+
                    total_layers = 40
                else:
                    total_layers = 32
            else:
                # Estimate based on model size
                if model_size_mb > 20000:  # >20GB
                    total_layers = 80
                elif model_size_mb > 10000:  # >10GB
                    total_layers = 60
                elif model_size_mb > 5000:  # >5GB
                    total_layers = 40
                else:
                    total_layers = 32
            
            if available_vram_mb >= model_size_mb * 1.5:
                # Enough VRAM for full model
                optimal_layers = -1  # All layers
            else:
                # Partial GPU loading
                # Estimate layers based on VRAM ratio
                vram_ratio = available_vram_mb / (model_size_mb * 1.2)  # 20% overhead
                optimal_layers = int(total_layers * vram_ratio)
                optimal_layers = max(0, min(optimal_layers, total_layers))
        
        # Cache the result
        with self._lock:
            self._gpu_layer_cache[cache_key] = optimal_layers
        
        self.logger.info(f"Optimized GPU layers for {Path(model_path).name}: {optimal_layers}")
        return optimal_layers
    
    def get_dynamic_batch_size(self, model_path: str, backend_name: str,
                             available_memory_mb: int, concurrent_requests: int = 1) -> int:
        """
        Calculate optimal batch size based on model size, available memory, and concurrent requests.
        
        Args:
            model_path: Path to the model file
            backend_name: Backend name
            available_memory_mb: Available memory in MB
            concurrent_requests: Number of concurrent requests expected
            
        Returns:
            Optimal batch size
        """
        # Get model profile
        model_profile = self.performance_cache.get_model_profile(model_path)
        if not model_profile:
            model_size_mb = Path(model_path).stat().st_size // (1024 * 1024)
        else:
            model_size_mb = model_profile.size_mb
        
        # Base batch size calculation
        # Reserve memory for model and overhead, use remaining for batching
        model_memory_mb = model_size_mb * 1.2  # 20% overhead
        available_for_batching = max(available_memory_mb - model_memory_mb, 512)  # At least 512MB
        
        # Estimate memory per token (varies by model size and backend)
        if backend_name == 'transformers':
            # Transformers typically uses more memory per token
            memory_per_token = 0.5 if model_size_mb < 5000 else 1.0
        else:
            # Other backends are more memory efficient
            memory_per_token = 0.2 if model_size_mb < 5000 else 0.4
        
        # Calculate batch size considering concurrent requests
        base_batch_size = int(available_for_batching / (memory_per_token * concurrent_requests))
        
        # Apply backend-specific constraints
        if backend_name == 'ctransformers':
            # ctransformers works well with moderate batch sizes
            optimal_batch_size = min(max(base_batch_size, 32), 512)
        elif backend_name == 'transformers':
            # transformers can handle larger batches but uses more memory
            optimal_batch_size = min(max(base_batch_size, 16), 256)
        elif backend_name == 'llamafile':
            # llamafile prefers smaller batches
            optimal_batch_size = min(max(base_batch_size, 16), 128)
        else:
            # Default constraints
            optimal_batch_size = min(max(base_batch_size, 32), 256)
        
        self.logger.info(f"Calculated optimal batch size for {backend_name}: {optimal_batch_size}")
        return optimal_batch_size
    
    def get_adaptive_context_size(self, model_path: str, backend_name: str,
                                available_memory_mb: int, target_performance: str = 'balanced') -> int:
        """
        Calculate adaptive context size based on available memory and performance target.
        
        Args:
            model_path: Path to the model file
            backend_name: Backend name
            available_memory_mb: Available memory in MB
            target_performance: Performance target ('speed', 'balanced', 'quality')
            
        Returns:
            Optimal context size
        """
        # Get model profile
        model_profile = self.performance_cache.get_model_profile(model_path)
        if not model_profile:
            model_size_mb = Path(model_path).stat().st_size // (1024 * 1024)
        else:
            model_size_mb = model_profile.size_mb
        
        # Base context sizes by performance target
        base_contexts = {
            'speed': 2048,      # Prioritize speed
            'balanced': 4096,   # Balance speed and quality
            'quality': 8192     # Prioritize quality
        }
        
        base_context = base_contexts.get(target_performance, 4096)
        
        # Adjust based on available memory
        model_memory_mb = model_size_mb * 1.2  # 20% overhead
        available_for_context = available_memory_mb - model_memory_mb
        
        # Estimate memory usage per context token (rough approximation)
        memory_per_context_token = 0.1  # MB per token
        max_context_by_memory = int(available_for_context / memory_per_context_token)
        
        # Apply backend-specific constraints
        if backend_name == 'ctransformers':
            # ctransformers handles context efficiently
            max_context = min(max_context_by_memory, 16384)
        elif backend_name == 'transformers':
            # transformers uses more memory for context
            max_context = min(max_context_by_memory, 8192)
        elif backend_name == 'llamafile':
            # llamafile is memory efficient
            max_context = min(max_context_by_memory, 32768)
        else:
            # Default constraints
            max_context = min(max_context_by_memory, 8192)
        
        # Choose the smaller of base context and memory-constrained context
        optimal_context = min(base_context, max_context)
        
        # Ensure minimum context size
        optimal_context = max(optimal_context, 512)
        
        self.logger.info(f"Calculated adaptive context size for {backend_name}: {optimal_context}")
        return optimal_context
    
    def predict_performance(self, model_path: str, backend_name: str,
                          hardware_config: Dict[str, Any]) -> Dict[str, float]:
        """
        Predict performance metrics for a model/backend combination.
        
        Args:
            model_path: Path to the model file
            backend_name: Backend name
            hardware_config: Hardware configuration
            
        Returns:
            Dictionary with predicted performance metrics
        """
        # Get historical performance data
        backend_performances = self.performance_cache.get_backend_performance(model_path, backend_name)
        
        if backend_performances:
            # Use historical data for prediction
            profiles = list(backend_performances.values())
            avg_load_time = sum(p.load_time_ms for p in profiles) / len(profiles)
            avg_memory_usage = sum(p.memory_usage_mb for p in profiles) / len(profiles)
            avg_tokens_per_sec = sum(p.tokens_per_second for p in profiles) / len(profiles)
            avg_success_rate = sum(p.success_rate for p in profiles) / len(profiles)
        else:
            # Estimate based on model size and hardware
            model_size_mb = Path(model_path).stat().st_size // (1024 * 1024) if Path(model_path).exists() else 1000
            
            # Base estimates by backend type
            backend_estimates = {
                'ctransformers': {
                    'load_time_factor': 0.1,    # ms per MB
                    'memory_factor': 1.2,       # memory overhead
                    'base_tokens_per_sec': 45.0,
                    'success_rate': 0.95
                },
                'transformers': {
                    'load_time_factor': 0.15,
                    'memory_factor': 1.5,
                    'base_tokens_per_sec': 35.0,
                    'success_rate': 0.90
                },
                'llamafile': {
                    'load_time_factor': 0.08,
                    'memory_factor': 1.0,
                    'base_tokens_per_sec': 50.0,
                    'success_rate': 0.98
                },
                'llama-cpp-python': {
                    'load_time_factor': 0.12,
                    'memory_factor': 1.1,
                    'base_tokens_per_sec': 40.0,
                    'success_rate': 0.85
                }
            }
            
            estimates = backend_estimates.get(backend_name, backend_estimates['ctransformers'])
            
            # Adjust for hardware
            gpu_multiplier = 1.0
            if hardware_config.get('gpu_count', 0) > 0 and hardware_config.get('total_vram', 0) >= model_size_mb:
                gpu_multiplier = 2.5  # GPU acceleration boost
            
            avg_load_time = model_size_mb * estimates['load_time_factor']
            avg_memory_usage = model_size_mb * estimates['memory_factor']
            avg_tokens_per_sec = estimates['base_tokens_per_sec'] * gpu_multiplier
            avg_success_rate = estimates['success_rate']
        
        return {
            'predicted_load_time_ms': avg_load_time,
            'predicted_memory_usage_mb': avg_memory_usage,
            'predicted_tokens_per_second': avg_tokens_per_sec,
            'predicted_success_rate': avg_success_rate,
            'confidence': 0.8 if backend_performances else 0.5
        }
    
    def record_performance(self, backend_name: str, model_path: str,
                         load_time_ms: float, memory_usage_mb: int,
                         tokens_per_second: float, success: bool,
                         hardware_config: Optional[Dict[str, Any]] = None):
        """
        Record performance metrics for future optimization.
        
        Args:
            backend_name: Name of the backend used
            model_path: Path to the model
            load_time_ms: Loading time in milliseconds
            memory_usage_mb: Memory usage in MB
            tokens_per_second: Generation speed
            success: Whether the operation was successful
            hardware_config: Hardware configuration used
        """
        if hardware_config is None:
            hardware_info = self.hardware_detector.get_hardware_info()
            hardware_config = {
                'gpu_count': hardware_info.gpu_count,
                'total_vram': hardware_info.total_vram,
                'cpu_cores': hardware_info.cpu_cores,
                'total_ram': hardware_info.total_ram
            }
        
        success_rate = 1.0 if success else 0.0
        
        self.performance_cache.store_backend_performance(
            backend_name=backend_name,
            model_path=model_path,
            hardware_config=hardware_config,
            load_time_ms=load_time_ms,
            memory_usage_mb=memory_usage_mb,
            tokens_per_second=tokens_per_second,
            success_rate=success_rate
        )
        
        self.logger.debug(f"Recorded performance: {backend_name} - {tokens_per_second:.1f} tokens/sec")
    
    def get_performance_stats(self, model_path: Optional[str] = None,
                            backend_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance statistics.
        
        Args:
            model_path: Filter by model path (optional)
            backend_name: Filter by backend name (optional)
            
        Returns:
            Dictionary with performance statistics
        """
        stats = {
            'total_models': len(self.performance_cache.model_profiles),
            'total_backend_profiles': sum(len(profiles) for profiles in self.performance_cache.backend_profiles.values()),
            'cache_file': self.performance_cache.cache_file
        }
        
        if model_path:
            backend_performances = self.performance_cache.get_backend_performance(model_path, backend_name)
            stats['model_performances'] = {k: v.to_dict() for k, v in backend_performances.items()}
        
        return stats
    
    def get_optimization_insights(self, model_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Get optimization insights and recommendations.
        
        Args:
            model_path: Filter by model path (optional)
            
        Returns:
            Dictionary with optimization insights
        """
        insights = {
            'recommendations': [],
            'performance_trends': {},
            'bottlenecks': [],
            'optimization_opportunities': []
        }
        
        # Analyze performance data
        if model_path:
            backend_performances = self.performance_cache.get_backend_performance(model_path)
            
            if backend_performances:
                # Analyze backend performance
                backend_stats = {}
                for profile in backend_performances.values():
                    backend_name = profile.backend_name
                    if backend_name not in backend_stats:
                        backend_stats[backend_name] = {
                            'load_times': [],
                            'tokens_per_sec': [],
                            'memory_usage': [],
                            'success_rates': []
                        }
                    
                    backend_stats[backend_name]['load_times'].append(profile.load_time_ms)
                    backend_stats[backend_name]['tokens_per_sec'].append(profile.tokens_per_second)
                    backend_stats[backend_name]['memory_usage'].append(profile.memory_usage_mb)
                    backend_stats[backend_name]['success_rates'].append(profile.success_rate)
                
                # Generate recommendations
                best_backend = None
                best_score = 0
                
                for backend_name, stats in backend_stats.items():
                    avg_tokens_per_sec = sum(stats['tokens_per_sec']) / len(stats['tokens_per_sec'])
                    avg_success_rate = sum(stats['success_rates']) / len(stats['success_rates'])
                    avg_load_time = sum(stats['load_times']) / len(stats['load_times'])
                    
                    # Calculate composite score
                    score = (avg_tokens_per_sec * avg_success_rate) / (avg_load_time / 1000)
                    
                    if score > best_score:
                        best_score = score
                        best_backend = backend_name
                    
                    # Identify bottlenecks
                    if avg_load_time > 5000:  # > 5 seconds
                        insights['bottlenecks'].append(f"Slow loading with {backend_name}: {avg_load_time:.0f}ms")
                    
                    if avg_tokens_per_sec < 10:  # < 10 tokens/sec
                        insights['bottlenecks'].append(f"Slow generation with {backend_name}: {avg_tokens_per_sec:.1f} tokens/sec")
                    
                    if avg_success_rate < 0.9:  # < 90% success rate
                        insights['bottlenecks'].append(f"Low reliability with {backend_name}: {avg_success_rate:.1%} success rate")
                
                if best_backend:
                    insights['recommendations'].append(f"Best performing backend: {best_backend} (score: {best_score:.2f})")
                
                # Performance trends
                insights['performance_trends'] = {
                    backend_name: {
                        'avg_tokens_per_sec': sum(stats['tokens_per_sec']) / len(stats['tokens_per_sec']),
                        'avg_load_time_ms': sum(stats['load_times']) / len(stats['load_times']),
                        'avg_memory_usage_mb': sum(stats['memory_usage']) / len(stats['memory_usage']),
                        'success_rate': sum(stats['success_rates']) / len(stats['success_rates'])
                    }
                    for backend_name, stats in backend_stats.items()
                }
        
        # General optimization opportunities
        hardware_info = self.hardware_detector.get_hardware_info()
        
        if hardware_info.gpu_count > 0 and hardware_info.total_vram > 8192:
            insights['optimization_opportunities'].append("High-end GPU detected - consider using GPU-optimized backends")
        
        if hardware_info.total_ram > 32768:
            insights['optimization_opportunities'].append("High RAM available - consider larger context sizes")
        
        if hardware_info.cpu_cores > 16:
            insights['optimization_opportunities'].append("High core count CPU - consider parallel processing optimizations")
        
        return insights
    
    def export_performance_report(self, output_path: str, model_path: Optional[str] = None):
        """
        Export a comprehensive performance report.
        
        Args:
            output_path: Path to save the report
            model_path: Filter by model path (optional)
        """
        report = {
            'timestamp': time.time(),
            'hardware_info': self.hardware_detector.get_hardware_info().to_dict(),
            'performance_stats': self.get_performance_stats(model_path),
            'optimization_insights': self.get_optimization_insights(model_path),
            'cache_summary': {
                'total_models': len(self.performance_cache.model_profiles),
                'total_backend_profiles': sum(len(profiles) for profiles in self.performance_cache.backend_profiles.values()),
                'cache_file': self.performance_cache.cache_file
            }
        }
        
        try:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            self.logger.info(f"Performance report exported to {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to export performance report: {e}")
    
    def clear_performance_cache(self, model_path: Optional[str] = None):
        """
        Clear performance cache data.
        
        Args:
            model_path: Clear data for specific model (optional, clears all if None)
        """
        if model_path:
            model_hash = self.performance_cache._calculate_model_hash(model_path)
            if model_hash:
                with self.performance_cache._lock:
                    self.performance_cache.model_profiles.pop(model_hash, None)
                    self.performance_cache.backend_profiles.pop(model_hash, None)
                    self.performance_cache._save_cache()
                self.logger.info(f"Cleared performance cache for {Path(model_path).name}")
        else:
            with self.performance_cache._lock:
                self.performance_cache.model_profiles.clear()
                self.performance_cache.backend_profiles.clear()
                self.performance_cache._save_cache()
            self.logger.info("Cleared all performance cache data")
        
        # Also clear GPU layer cache
        with self._lock:
            if model_path:
                # Clear entries for specific model
                keys_to_remove = [k for k in self._gpu_layer_cache.keys() if model_path in k]
                for key in keys_to_remove:
                    self._gpu_layer_cache.pop(key, None)
            else:
                self._gpu_layer_cache.clear()