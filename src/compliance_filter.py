"""
Main Compliance Filter Module

Combines hate speech and privacy violation detection into a unified compliance
scoring system with configurable thresholds and actions.
"""

import logging
import time
import hashlib
import asyncio
import threading
import json
import pickle
import gc
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import yaml
from pathlib import Path
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import deque, defaultdict

from privacy_detector import PrivacyDetector, PrivacyViolation
from hate_speech_detector import HateSpeechDetector, HateSpeechResult

# Try to import optional performance libraries
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class ComplianceAction(Enum):
    """Actions that can be taken based on compliance score."""
    ALLOW = "allow"
    WARN = "warn" 
    BLOCK = "block"


@dataclass
class PerformanceMetrics:
    """Performance metrics for monitoring."""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    avg_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    requests_per_second: float = 0.0
    error_rate: float = 0.0


@dataclass
class ComplianceResult:
    """Result from compliance filtering."""
    action: ComplianceAction
    overall_score: float
    hate_speech_score: float
    privacy_score: float
    hate_speech_result: Optional[HateSpeechResult]
    privacy_violations: List[PrivacyViolation]
    processing_time: float
    reasoning: str
    timestamp: str


class PerformanceMonitor:
    """Real-time performance monitoring."""
    
    def __init__(self, window_size=1000):
        self.window_size = window_size
        self.response_times = deque(maxlen=window_size)
        self.request_times = deque(maxlen=window_size)
        self.cache_hits = 0
        self.cache_misses = 0
        self.errors = 0
        self.total_requests = 0
        self.lock = threading.Lock()
    
    def record_request(self, response_time: float, cache_hit: bool = False, error: bool = False):
        """Record a request's performance metrics."""
        with self.lock:
            current_time = time.time()
            self.response_times.append(response_time)
            self.request_times.append(current_time)
            self.total_requests += 1
            
            if cache_hit:
                self.cache_hits += 1
            else:
                self.cache_misses += 1
            
            if error:
                self.errors += 1
    
    def get_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics."""
        with self.lock:
            if not self.response_times:
                return PerformanceMetrics()
            
            # Calculate response time percentiles
            sorted_times = sorted(self.response_times)
            n = len(sorted_times)
            
            avg_time = sum(sorted_times) / n
            p95_time = sorted_times[int(0.95 * n)] if n > 0 else 0
            p99_time = sorted_times[int(0.99 * n)] if n > 0 else 0
            
            # Calculate requests per second (last 60 seconds)
            current_time = time.time()
            recent_requests = sum(1 for t in self.request_times if current_time - t <= 60)
            rps = recent_requests / 60
            
            # Error rate
            error_rate = (self.errors / self.total_requests * 100) if self.total_requests > 0 else 0
            
            # System metrics
            memory_usage = 0.0
            cpu_usage = 0.0
            if PSUTIL_AVAILABLE:
                try:
                    process = psutil.Process()
                    memory_usage = process.memory_info().rss / 1024 / 1024  # MB
                    cpu_usage = psutil.cpu_percent()
                except:
                    pass
            
            return PerformanceMetrics(
                total_requests=self.total_requests,
                cache_hits=self.cache_hits,
                cache_misses=self.cache_misses,
                avg_response_time=avg_time,
                p95_response_time=p95_time,
                p99_response_time=p99_time,
                memory_usage_mb=memory_usage,
                cpu_usage_percent=cpu_usage,
                requests_per_second=rps,
                error_rate=error_rate
            )


class IntelligentCache:
    """Multi-tier intelligent caching system."""
    
    def __init__(self, 
                 memory_cache_size: int = 1000,
                 redis_host: str = 'localhost',
                 redis_port: int = 6379,
                 redis_db: int = 0,
                 ttl: int = 3600):
        
        self.ttl = ttl
        self.memory_cache_size = memory_cache_size
        
        # L1 Cache: In-memory LRU cache (fastest)
        self.memory_cache: Dict[str, Tuple[Any, float]] = {}
        self.cache_access_times: Dict[str, float] = {}
        
        # L2 Cache: Redis (fast, shared across instances)
        self.redis_client = None
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(
                    host=redis_host, 
                    port=redis_port, 
                    db=redis_db,
                    decode_responses=False  # We'll handle serialization
                )
                # Test connection
                self.redis_client.ping()
                logging.info("Redis cache connected successfully")
            except Exception as e:
                logging.warning(f"Redis connection failed: {e}")
                self.redis_client = None
        
        # Cache statistics
        self.stats = {
            'l1_hits': 0, 'l1_misses': 0,
            'l2_hits': 0, 'l2_misses': 0,
            'total_sets': 0, 'evictions': 0
        }
    
    def _get_cache_key(self, prompt: str, config_hash: str = "") -> str:
        """Generate cache key for prompt and configuration."""
        combined = f"{prompt}:{config_hash}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache (tries L1 then L2)."""
        current_time = time.time()
        
        # Try L1 cache first
        if key in self.memory_cache:
            value, timestamp = self.memory_cache[key]
            if current_time - timestamp < self.ttl:
                self.cache_access_times[key] = current_time
                self.stats['l1_hits'] += 1
                return value
            else:
                # Expired, remove from L1
                del self.memory_cache[key]
                if key in self.cache_access_times:
                    del self.cache_access_times[key]
        
        self.stats['l1_misses'] += 1
        
        # Try L2 cache (Redis)
        if self.redis_client:
            try:
                serialized_data = self.redis_client.get(f"compliance:{key}")
                if serialized_data:
                    value = pickle.loads(serialized_data)
                    self.stats['l2_hits'] += 1
                    
                    # Promote to L1 cache
                    self._set_l1(key, value, current_time)
                    return value
            except Exception as e:
                logging.warning(f"Redis get error: {e}")
        
        self.stats['l2_misses'] += 1
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache (stores in both L1 and L2)."""
        current_time = time.time()
        
        # Store in L1
        self._set_l1(key, value, current_time)
        
        # Store in L2 (Redis)
        if self.redis_client:
            try:
                serialized_data = pickle.dumps(value)
                self.redis_client.setex(f"compliance:{key}", self.ttl, serialized_data)
            except Exception as e:
                logging.warning(f"Redis set error: {e}")
        
        self.stats['total_sets'] += 1
    
    def _set_l1(self, key: str, value: Any, timestamp: float = None) -> None:
        """Set value in L1 cache with LRU eviction."""
        if timestamp is None:
            timestamp = time.time()
        
        # Evict if cache is full
        if len(self.memory_cache) >= self.memory_cache_size:
            self._evict_lru()
        
        self.memory_cache[key] = (value, timestamp)
        self.cache_access_times[key] = timestamp
    
    def _evict_lru(self) -> None:
        """Evict least recently used item from L1 cache."""
        if not self.cache_access_times:
            return
        
        lru_key = min(self.cache_access_times, key=self.cache_access_times.get)
        
        if lru_key in self.memory_cache:
            del self.memory_cache[lru_key]
        if lru_key in self.cache_access_times:
            del self.cache_access_times[lru_key]
        
        self.stats['evictions'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = (self.stats['l1_hits'] + self.stats['l1_misses'] + 
                         self.stats['l2_hits'] + self.stats['l2_misses'])
        
        if total_requests == 0:
            return self.stats
        
        stats = self.stats.copy()
        stats.update({
            'l1_hit_rate': (self.stats['l1_hits'] / total_requests) * 100,
            'l2_hit_rate': (self.stats['l2_hits'] / total_requests) * 100,
            'overall_hit_rate': ((self.stats['l1_hits'] + self.stats['l2_hits']) / total_requests) * 100,
            'memory_cache_size': len(self.memory_cache),
            'memory_cache_capacity': self.memory_cache_size
        })
        
        return stats
    
    def clear(self) -> None:
        """Clear all caches."""
        self.memory_cache.clear()
        self.cache_access_times.clear()
        
        if self.redis_client:
            try:
                # Clear only compliance-related keys
                keys = self.redis_client.keys("compliance:*")
                if keys:
                    self.redis_client.delete(*keys)
            except Exception as e:
                logging.warning(f"Redis clear error: {e}")


class ComplianceFilter:
    """
    Main compliance filter that combines multiple detection methods.
    
    Features:
    - Configurable scoring methods (weighted_average, max, product)
    - Adjustable thresholds for different risk levels
    - Comprehensive logging and audit trail
    - Performance monitoring
    - Feedback integration
    """
    
    def __init__(self, 
                 config_path: Optional[str] = None, 
                 config_dict: Optional[Dict[str, Any]] = None,
                 enable_performance_optimizations: bool = None,
                 enable_caching: bool = None,
                 enable_monitoring: bool = None,
                 cache_size: int = 1000,
                 max_workers: int = 4):
        """
        Initialize the compliance filter.
        
        Args:
            config_path: Path to YAML configuration file
            config_dict: Configuration dictionary (takes precedence over config_path)
            enable_performance_optimizations: Enable all performance features (auto-detected from config if None)
            enable_caching: Enable intelligent caching system
            enable_monitoring: Enable real-time performance monitoring
            cache_size: Size of L1 memory cache
            max_workers: Number of worker threads for parallel processing
        """
        # Load configuration
        if config_dict:
            self.config = config_dict
        elif config_path:
            self.config = self._load_config(config_path)
        else:
            # Use default config path
            default_config_path = Path(__file__).parent.parent / "config" / "default.yaml"
            self.config = self._load_config(str(default_config_path))
        
        # Extract configuration sections
        self.compliance_config = self.config.get('compliance', {})
        self.scoring_method = self.compliance_config.get('scoring_method', 'weighted_average')
        self.weights = self.compliance_config.get('weights', {'hate_speech': 0.6, 'privacy': 0.4})
        self.thresholds = self.compliance_config.get('thresholds', {
            'block_threshold': 0.7,
            'warn_threshold': 0.5,
            'pass_threshold': 0.2
        })
        
        # Performance configuration
        performance_config = self.config.get('performance', {})
        
        # Determine performance settings (parameters override config)
        if enable_performance_optimizations is None:
            enable_performance_optimizations = performance_config.get('enable_optimizations', False)
        
        if enable_caching is None:
            enable_caching = performance_config.get('enable_caching', enable_performance_optimizations)
            
        if enable_monitoring is None:
            enable_monitoring = performance_config.get('enable_monitoring', enable_performance_optimizations)
            
        self.enable_caching = enable_caching
        self.enable_monitoring = enable_monitoring
        self.max_workers = max_workers
        
        # Initialize performance components
        if self.enable_caching:
            cache_config = performance_config.get('cache', {})
            self.cache = IntelligentCache(
                memory_cache_size=cache_config.get('memory_size', cache_size),
                redis_host=cache_config.get('redis_host', 'localhost'),
                redis_port=cache_config.get('redis_port', 6379),
                redis_db=cache_config.get('redis_db', 0),
                ttl=cache_config.get('ttl', 3600)
            )
            self.config_hash = self._compute_config_hash()
        else:
            self.cache = None
            
        if self.enable_monitoring:
            self.monitor = PerformanceMonitor(
                window_size=performance_config.get('monitor_window_size', 1000)
            )
        else:
            self.monitor = None
            
        # Thread pool for parallel processing
        if enable_performance_optimizations:
            self.executor = ThreadPoolExecutor(max_workers=max_workers)
        else:
            self.executor = None
        
        # Initialize detectors
        self.privacy_detector = PrivacyDetector(self.config)
        
        try:
            self.hate_speech_detector = HateSpeechDetector(self.config)
            self.hate_speech_available = True
        except ImportError:
            logging.warning("Hate speech detection not available - transformers library not installed")
            self.hate_speech_detector = None
            self.hate_speech_available = False
        
        # Performance tracking
        self._total_checks = 0
        self._total_time = 0.0
        self._action_counts = {action.value: 0 for action in ComplianceAction}
        
        logging.info(f"ComplianceFilter initialized with performance optimizations: caching={self.enable_caching}, monitoring={self.enable_monitoring}")
    
    def _compute_config_hash(self) -> str:
        """Compute hash of current configuration for cache invalidation."""
        config_str = json.dumps(self.config, sort_keys=True, default=str)
        return hashlib.md5(config_str.encode()).hexdigest()[:8]
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logging.info(f"Configuration loaded from {config_path}")
            return config
        except FileNotFoundError:
            logging.error(f"Configuration file not found: {config_path}")
            # Return minimal default config
            return {
                'compliance': {
                    'scoring_method': 'weighted_average',
                    'weights': {'hate_speech': 0.6, 'privacy': 0.4},
                    'thresholds': {'block_threshold': 0.7, 'warn_threshold': 0.5, 'pass_threshold': 0.2}
                },
                'privacy': {'checks': {}},
                'hate_speech': {'threshold': 0.7}
            }
        except yaml.YAMLError as e:
            logging.error(f"Error parsing configuration file: {e}")
            raise
    
    def check_compliance(self, 
                        text: str, 
                        user_context: Optional[Dict[str, Any]] = None,
                        use_cache: bool = True) -> ComplianceResult:
        """
        Check compliance of input text against all filters.
        
        Args:
            text: Input text to check
            user_context: Optional user context for logging
            use_cache: Whether to use caching for this request
            
        Returns:
            ComplianceResult with detailed analysis
        """
        start_time = time.time()
        cache_hit = False
        error = False
        
        try:
            # Try cache first if enabled
            if use_cache and self.cache:
                cache_key = self.cache._get_cache_key(text, self.config_hash)
                cached_result = self.cache.get(cache_key)
                
                if cached_result:
                    cache_hit = True
                    if self.monitor:
                        response_time = time.time() - start_time
                        self.monitor.record_request(response_time, cache_hit=True)
                    return cached_result
        
            # Run compliance checks
            privacy_violations = self.privacy_detector.detect_violations(text)
            privacy_score = self.privacy_detector.calculate_privacy_score(privacy_violations)
            
            # Run hate speech detection if available
            hate_speech_result = None
            hate_speech_score = 0.0
            
            if self.hate_speech_available:
                try:
                    hate_speech_result = self.hate_speech_detector.detect_hate_speech(text)
                    hate_speech_score = hate_speech_result.confidence if hate_speech_result.is_hate_speech else 0.0
                except Exception as e:
                    logging.error(f"Hate speech detection failed: {e}")
                    # Use conservative default
                    hate_speech_score = 1.0
            
            # Calculate overall compliance score
            overall_score = self._calculate_overall_score(hate_speech_score, privacy_score)
            
            # Determine action
            action = self._determine_action(overall_score)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                overall_score, hate_speech_score, privacy_score, 
                hate_speech_result, privacy_violations
            )
            
            processing_time = time.time() - start_time
            
            # Update statistics
            self._update_stats(action, processing_time)
            
            # Create result
            result = ComplianceResult(
                action=action,
                overall_score=overall_score,
                hate_speech_score=hate_speech_score,
                privacy_score=privacy_score,
                hate_speech_result=hate_speech_result,
                privacy_violations=privacy_violations,
                processing_time=processing_time,
                reasoning=reasoning,
                timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
            )
            
            # Cache the result if enabled
            if use_cache and self.cache:
                self.cache.set(cache_key, result)
            
            # Log the result
            self._log_compliance_check(text, result, user_context)
            
            return result
            
        except Exception as e:
            error = True
            logging.error(f"Compliance check error: {e}")
            # Return safe default
            processing_time = time.time() - start_time
            return ComplianceResult(
                action=ComplianceAction.BLOCK,
                overall_score=1.0,
                hate_speech_score=1.0,
                privacy_score=1.0,
                hate_speech_result=None,
                privacy_violations=[],
                processing_time=processing_time,
                reasoning=f"Error during processing: {str(e)}",
                timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
            )
        
        finally:
            if self.monitor:
                response_time = time.time() - start_time
                self.monitor.record_request(response_time, cache_hit=cache_hit, error=error)
    
    def _calculate_overall_score(self, hate_speech_score: float, privacy_score: float) -> float:
        """
        Calculate overall compliance score using configured method.
        
        Args:
            hate_speech_score: Score from hate speech detection
            privacy_score: Score from privacy detection
            
        Returns:
            Overall compliance score between 0.0 and 1.0
        """
        if self.scoring_method == 'weighted_average':
            return (
                hate_speech_score * self.weights.get('hate_speech', 0.6) +
                privacy_score * self.weights.get('privacy', 0.4)
            )
        
        elif self.scoring_method == 'max':
            return max(hate_speech_score, privacy_score)
        
        elif self.scoring_method == 'product':
            # Using 1 - (1-a)(1-b) to combine probabilities
            return 1 - (1 - hate_speech_score) * (1 - privacy_score)
        
        else:
            logging.warning(f"Unknown scoring method: {self.scoring_method}, using weighted_average")
            return (
                hate_speech_score * self.weights.get('hate_speech', 0.6) +
                privacy_score * self.weights.get('privacy', 0.4)
            )
    
    def _determine_action(self, overall_score: float) -> ComplianceAction:
        """Determine action based on overall score and thresholds."""
        if overall_score >= self.thresholds.get('block_threshold', 0.7):
            return ComplianceAction.BLOCK
        elif overall_score >= self.thresholds.get('warn_threshold', 0.5):
            return ComplianceAction.WARN
        else:
            return ComplianceAction.ALLOW
    
    def _generate_reasoning(
        self, 
        overall_score: float, 
        hate_speech_score: float, 
        privacy_score: float,
        hate_speech_result: Optional[HateSpeechResult],
        privacy_violations: List[PrivacyViolation]
    ) -> str:
        """Generate human-readable reasoning for the compliance decision."""
        reasons = []
        
        if overall_score < self.thresholds.get('pass_threshold', 0.2):
            reasons.append("Content appears compliant with minimal risk.")
        
        if hate_speech_score > 0.3:
            if hate_speech_result:
                reasons.append(f"Potential hate speech detected (confidence: {hate_speech_score:.2f}, "
                             f"model: {hate_speech_result.model_used}).")
            else:
                reasons.append(f"Hate speech score elevated: {hate_speech_score:.2f}")
        
        if privacy_violations:
            violation_types = set(v.violation_type.value for v in privacy_violations)
            reasons.append(f"Privacy violations detected: {', '.join(violation_types)} "
                          f"(score: {privacy_score:.2f}).")
        
        if overall_score >= self.thresholds.get('block_threshold', 0.7):
            reasons.append("Content blocked due to high compliance risk.")
        elif overall_score >= self.thresholds.get('warn_threshold', 0.5):
            reasons.append("Content flagged for review due to moderate compliance risk.")
        
        return " ".join(reasons) if reasons else "No significant compliance issues detected."
    
    def _update_stats(self, action: ComplianceAction, processing_time: float):
        """Update performance statistics."""
        self._total_checks += 1
        self._total_time += processing_time
        self._action_counts[action.value] += 1
    
    def _log_compliance_check(
        self, 
        text: str, 
        result: ComplianceResult, 
        user_context: Optional[Dict[str, Any]]
    ):
        """Log compliance check details."""
        logging_config = self.config.get('logging', {})
        
        if not logging_config.get('audit_logs', True):
            return
        
        log_details = logging_config.get('log_details', {})
        
        log_entry = {
            'timestamp': result.timestamp,
            'action': result.action.value,
            'overall_score': result.overall_score,
            'hate_speech_score': result.hate_speech_score,
            'privacy_score': result.privacy_score,
            'processing_time': result.processing_time,
            'reasoning': result.reasoning
        }
        
        # Add optional details based on config
        if log_details.get('scores', True):
            if result.hate_speech_result:
                log_entry['hate_speech_details'] = {
                    'model': result.hate_speech_result.model_used,
                    'all_scores': result.hate_speech_result.all_scores
                }
        
        if log_details.get('violation_details', True):
            log_entry['privacy_violations'] = [
                {
                    'type': v.violation_type.value,
                    'confidence': v.confidence,
                    'description': v.description
                } for v in result.privacy_violations
            ]
        
        if log_details.get('user_context', True) and user_context:
            log_entry['user_context'] = user_context
        
        # Don't log prompt content by default for privacy
        if log_details.get('prompt_content', False):
            log_entry['prompt'] = text
        
        logging.info(f"Compliance check: {log_entry}")
    
    def batch_check_compliance(self, 
                              texts: List[str],
                              user_contexts: Optional[List[Dict[str, Any]]] = None,
                              parallel: bool = None,
                              chunk_size: Optional[int] = None) -> List[ComplianceResult]:
        """
        Check compliance for multiple texts with optional parallel processing.
        
        Args:
            texts: List of texts to check
            user_contexts: Optional list of user contexts for each text
            parallel: Use parallel processing (auto-detected based on performance config if None)
            chunk_size: Size of chunks for parallel processing
            
        Returns:
            List of ComplianceResult objects
        """
        if not texts:
            return []
        
        # Auto-detect parallel processing
        if parallel is None:
            parallel = bool(self.executor and len(texts) > 1)
        
        # Ensure user_contexts has the same length as texts
        if user_contexts is None:
            user_contexts = [None] * len(texts)
        elif len(user_contexts) != len(texts):
            user_contexts = user_contexts + [None] * (len(texts) - len(user_contexts))
        
        start_time = time.time()
        
        try:
            if parallel and self.executor:
                results = self._batch_parallel(texts, user_contexts, chunk_size)
            else:
                results = self._batch_sequential(texts, user_contexts)
            
            return results
            
        finally:
            total_time = time.time() - start_time
            logging.info(f"Batch processed {len(texts)} items in {total_time:.3f}s "
                        f"({len(texts)/total_time:.1f} items/sec)")
    
    def _batch_sequential(self, 
                         texts: List[str], 
                         user_contexts: List[Optional[Dict[str, Any]]]) -> List[ComplianceResult]:
        """Sequential batch processing."""
        results = []
        for text, context in zip(texts, user_contexts):
            result = self.check_compliance(text, context)
            results.append(result)
        return results
    
    def _batch_parallel(self, 
                       texts: List[str], 
                       user_contexts: List[Optional[Dict[str, Any]]],
                       chunk_size: Optional[int] = None) -> List[ComplianceResult]:
        """Parallel batch processing with optimal chunking."""
        
        # Determine optimal chunk size
        if chunk_size is None:
            chunk_size = max(1, len(texts) // (self.max_workers * 2))
            chunk_size = min(chunk_size, 50)  # Cap at 50 to avoid memory issues
        
        # Create chunks
        chunks = []
        for i in range(0, len(texts), chunk_size):
            end_idx = min(i + chunk_size, len(texts))
            chunk_texts = texts[i:end_idx]
            chunk_contexts = user_contexts[i:end_idx]
            chunks.append((chunk_texts, chunk_contexts))
        
        # Process chunks in parallel
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all chunks
            futures = []
            for chunk_texts, chunk_contexts in chunks:
                future = executor.submit(self._process_chunk, chunk_texts, chunk_contexts)
                futures.append(future)
            
            # Collect results in order
            for future in futures:
                try:
                    chunk_result = future.result()
                    results.extend(chunk_result)
                except Exception as e:
                    logging.error(f"Chunk processing error: {e}")
                    # Create error results for this chunk
                    error_results = [self._create_error_result(text, str(e)) for text in chunk_texts]
                    results.extend(error_results)
        
        return results
    
    def _process_chunk(self, 
                      chunk_texts: List[str], 
                      chunk_contexts: List[Optional[Dict[str, Any]]]) -> List[ComplianceResult]:
        """Process a single chunk of texts."""
        results = []
        for text, context in zip(chunk_texts, chunk_contexts):
            result = self.check_compliance(text, context)
            results.append(result)
        return results
    
    def _create_error_result(self, text: str, error_msg: str) -> ComplianceResult:
        """Create an error result."""
        return ComplianceResult(
            action=ComplianceAction.BLOCK,
            overall_score=1.0,
            hate_speech_score=1.0,
            privacy_score=1.0,
            hate_speech_result=None,
            privacy_violations=[],
            processing_time=0.0,
            reasoning=f"Processing error: {error_msg}",
            timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
        )
    
    def update_thresholds(self, new_thresholds: Dict[str, float]):
        """
        Update compliance thresholds.
        
        Args:
            new_thresholds: Dictionary with new threshold values
        """
        for threshold_name, value in new_thresholds.items():
            if threshold_name in self.thresholds:
                if not 0.0 <= value <= 1.0:
                    raise ValueError(f"Threshold {threshold_name} must be between 0.0 and 1.0")
                self.thresholds[threshold_name] = value
        
        logging.info(f"Updated thresholds: {new_thresholds}")
    
    def update_weights(self, new_weights: Dict[str, float]):
        """
        Update scoring weights.
        
        Args:
            new_weights: Dictionary with new weight values
        """
        total_weight = sum(new_weights.values())
        if abs(total_weight - 1.0) > 0.01:  # Allow small floating point errors
            logging.warning(f"Weights sum to {total_weight}, not 1.0. Consider normalizing.")
        
        self.weights.update(new_weights)
        logging.info(f"Updated weights: {new_weights}")
    
    async def check_compliance_async(self, 
                                   text: str, 
                                   user_context: Optional[Dict[str, Any]] = None) -> ComplianceResult:
        """Async compliance check."""
        if not self.executor:
            # Fallback to sync if no executor
            return self.check_compliance(text, user_context)
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self.check_compliance, 
            text, 
            user_context
        )
    
    async def batch_check_compliance_async(self, 
                                         texts: List[str],
                                         user_contexts: Optional[List[Dict[str, Any]]] = None) -> List[ComplianceResult]:
        """Async batch processing."""
        
        if user_contexts is None:
            user_contexts = [None] * len(texts)
        
        # Create async tasks
        tasks = []
        for text, context in zip(texts, user_contexts):
            task = self.check_compliance_async(text, context)
            tasks.append(task)
        
        # Process all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(self._create_error_result(texts[i], str(result)))
            else:
                final_results.append(result)
        
        return final_results
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        stats = {
            'total_checks': self._total_checks,
            'average_processing_time': self._total_time / max(self._total_checks, 1),
            'total_processing_time': self._total_time,
            'action_distribution': self._action_counts.copy(),
            'performance_optimizations_enabled': {
                'caching': self.enable_caching,
                'monitoring': self.enable_monitoring,
                'parallel_processing': bool(self.executor)
            }
        }
        
        # Add performance monitor metrics
        if self.monitor:
            perf_metrics = self.monitor.get_metrics()
            stats['performance_metrics'] = asdict(perf_metrics)
        
        # Add cache statistics
        if self.cache:
            stats['cache_stats'] = self.cache.get_stats()
        
        # Add detector-specific stats
        if self.hate_speech_available:
            stats['hate_speech_detector'] = self.hate_speech_detector.get_performance_stats()
        
        # Add system metrics
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                stats['system_metrics'] = {
                    'memory_mb': process.memory_info().rss / 1024 / 1024,
                    'cpu_percent': process.cpu_percent(),
                    'threads': process.num_threads(),
                    'open_files': len(process.open_files())
                }
            except:
                pass
        
        return stats
    
    def optimize_memory(self):
        """Perform memory optimization."""
        
        # Clear caches if memory usage is high
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                
                if memory_mb > 1000:  # More than 1GB
                    logging.info(f"High memory usage ({memory_mb:.1f}MB), optimizing...")
                    
                    if self.cache:
                        # Clear oldest 50% of cache entries
                        cache_size = len(self.cache.memory_cache)
                        if cache_size > 100:
                            sorted_keys = sorted(
                                self.cache.cache_access_times.items(),
                                key=lambda x: x[1]
                            )
                            keys_to_remove = [k for k, _ in sorted_keys[:cache_size//2]]
                            
                            for key in keys_to_remove:
                                if key in self.cache.memory_cache:
                                    del self.cache.memory_cache[key]
                                if key in self.cache.cache_access_times:
                                    del self.cache.cache_access_times[key]
                    
                    # Force garbage collection
                    gc.collect()
            except:
                pass
    
    def warm_cache(self, sample_texts: List[str]):
        """Pre-warm cache with sample texts."""
        if not self.cache:
            logging.warning("Caching not enabled, cannot warm cache")
            return
        
        logging.info(f"Warming cache with {len(sample_texts)} sample texts")
        
        for text in sample_texts:
            try:
                self.check_compliance(text, use_cache=False)  # Don't use cache, but store result
            except Exception as e:
                logging.warning(f"Cache warming error for text '{text[:50]}...': {e}")
        
        logging.info("Cache warming completed")
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get current configuration summary."""
        return {
            'scoring_method': self.scoring_method,
            'weights': self.weights.copy(),
            'thresholds': self.thresholds.copy(),
            'hate_speech_available': self.hate_speech_available,
            'hate_speech_model': self.hate_speech_detector.model_name if self.hate_speech_available else None
        }
    
    def validate_prompt_safety(self, text: str) -> Tuple[bool, str]:
        """
        Quick safety validation for prompts.
        
        Args:
            text: Text to validate
            
        Returns:
            Tuple of (is_safe, reason)
        """
        result = self.check_compliance(text)
        
        is_safe = result.action == ComplianceAction.ALLOW
        reason = result.reasoning
        
        return is_safe, reason
    
    def cleanup(self):
        """Clean up resources."""
        # Stop performance monitoring
        if hasattr(self, 'monitor') and self.monitor:
            if hasattr(self.monitor, 'stop'):
                self.monitor.stop()
        
        # Shutdown thread pool
        if hasattr(self, 'executor') and self.executor:
            self.executor.shutdown(wait=True)
        
        # Clear caches
        if hasattr(self, 'cache') and self.cache:
            self.cache.clear()
        
        # Cleanup detectors
        if self.hate_speech_detector:
            self.hate_speech_detector.cleanup()
        
        logging.info("ComplianceFilter resources cleaned up")
    
    @classmethod
    def create_optimized(cls, 
                        config_path: Optional[str] = None,
                        config_dict: Optional[Dict[str, Any]] = None,
                        cache_size: int = 1000,
                        max_workers: int = 4) -> 'ComplianceFilter':
        """
        Factory method to create a performance-optimized compliance filter.
        
        Args:
            config_path: Path to YAML configuration file
            config_dict: Configuration dictionary (takes precedence over config_path)
            cache_size: Size of L1 memory cache
            max_workers: Number of worker threads
            
        Returns:
            ComplianceFilter with all performance optimizations enabled
        """
        return cls(
            config_path=config_path,
            config_dict=config_dict,
            enable_performance_optimizations=True,
            enable_caching=True,
            enable_monitoring=True,
            cache_size=cache_size,
            max_workers=max_workers
        )
    
    @classmethod
    def create_standard(cls,
                       config_path: Optional[str] = None,
                       config_dict: Optional[Dict[str, Any]] = None) -> 'ComplianceFilter':
        """
        Factory method to create a standard compliance filter without performance optimizations.
        
        Args:
            config_path: Path to YAML configuration file
            config_dict: Configuration dictionary (takes precedence over config_path)
            
        Returns:
            ComplianceFilter without performance optimizations (backward compatible)
        """
        return cls(
            config_path=config_path,
            config_dict=config_dict,
            enable_performance_optimizations=False,
            enable_caching=False,
            enable_monitoring=False
        )
    
    @classmethod
    def create_from_config(cls,
                          config_path: Optional[str] = None,
                          config_dict: Optional[Dict[str, Any]] = None) -> 'ComplianceFilter':
        """
        Factory method to create compliance filter based on configuration settings.
        
        Args:
            config_path: Path to YAML configuration file
            config_dict: Configuration dictionary (takes precedence over config_path)
            
        Returns:
            ComplianceFilter configured according to the performance settings in the config
        """
        return cls(
            config_path=config_path,
            config_dict=config_dict,
            enable_performance_optimizations=None,  # Auto-detect from config
            enable_caching=None,  # Auto-detect from config
            enable_monitoring=None  # Auto-detect from config
        )
