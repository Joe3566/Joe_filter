# Class Diagrams - LLM Compliance Filter System

## Overview
This document contains detailed class diagrams for the LLM Compliance Filter System, showing all classes, their relationships, methods, and attributes.

## 1. Core System Class Diagram

```plantuml
@startuml CoreSystemClasses
title LLM Compliance Filter - Core System Classes

package "Core System" {
    
    class ComplianceFilter {
        -config: Dict[str, Any]
        -compliance_config: Dict[str, Any]
        -scoring_method: str
        -weights: Dict[str, float]
        -thresholds: Dict[str, float]
        -cache: IntelligentCache
        -monitor: PerformanceMonitor
        -executor: ThreadPoolExecutor
        -privacy_detector: PrivacyDetector
        -hate_speech_detector: HateSpeechDetector
        -hate_speech_available: bool
        -enable_caching: bool
        -enable_monitoring: bool
        -max_workers: int
        -_total_checks: int
        -_total_time: float
        -_action_counts: Dict[str, int]
        --
        +__init__(config_path, config_dict, enable_performance_optimizations, ...)
        +check_compliance(text: str, user_context): ComplianceResult
        +batch_check_compliance(texts: List[str], ...): List[ComplianceResult]
        +check_compliance_async(text: str, user_context): ComplianceResult
        +batch_check_compliance_async(texts: List[str], ...): List[ComplianceResult]
        +update_thresholds(new_thresholds: Dict[str, float]): void
        +update_weights(new_weights: Dict[str, float]): void
        +get_performance_stats(): Dict[str, Any]
        +optimize_memory(): void
        +warm_cache(sample_texts: List[str]): void
        +get_configuration_summary(): Dict[str, Any]
        +validate_prompt_safety(text: str): Tuple[bool, str]
        +cleanup(): void
        -_load_config(config_path: str): Dict[str, Any]
        -_calculate_overall_score(hate_speech_score: float, privacy_score: float): float
        -_determine_action(overall_score: float): ComplianceAction
        -_generate_reasoning(...): str
        -_update_stats(action: ComplianceAction, processing_time: float): void
        -_log_compliance_check(text: str, result: ComplianceResult, user_context): void
        -_batch_sequential(texts: List[str], user_contexts): List[ComplianceResult]
        -_batch_parallel(texts: List[str], user_contexts, chunk_size): List[ComplianceResult]
        -_process_chunk(chunk_texts: List[str], chunk_contexts): List[ComplianceResult]
        -_create_error_result(text: str, error_msg: str): ComplianceResult
        -_compute_config_hash(): str
        +{static} create_optimized(...): ComplianceFilter
        +{static} create_standard(...): ComplianceFilter
        +{static} create_from_config(...): ComplianceFilter
    }

    enum ComplianceAction {
        ALLOW
        WARN
        BLOCK
    }

    class ComplianceResult {
        +action: ComplianceAction
        +overall_score: float
        +hate_speech_score: float
        +privacy_score: float
        +hate_speech_result: Optional[HateSpeechResult]
        +privacy_violations: List[PrivacyViolation]
        +processing_time: float
        +reasoning: str
        +timestamp: str
        --
        +__init__(action, overall_score, ...)
        +to_dict(): Dict[str, Any]
        +is_compliant(): bool
    }

    class PerformanceMetrics {
        +total_requests: int = 0
        +cache_hits: int = 0
        +cache_misses: int = 0
        +avg_response_time: float = 0.0
        +p95_response_time: float = 0.0
        +p99_response_time: float = 0.0
        +memory_usage_mb: float = 0.0
        +cpu_usage_percent: float = 0.0
        +requests_per_second: float = 0.0
        +error_rate: float = 0.0
        --
        +__init__(...)
        +to_dict(): Dict[str, Any]
    }
}

package "Performance" {
    
    class PerformanceMonitor {
        -window_size: int
        -response_times: deque
        -request_times: deque
        -cache_hits: int
        -cache_misses: int
        -errors: int
        -total_requests: int
        -lock: threading.Lock
        --
        +__init__(window_size: int = 1000)
        +record_request(response_time: float, cache_hit: bool = False, error: bool = False): void
        +get_metrics(): PerformanceMetrics
    }

    class IntelligentCache {
        -ttl: int
        -memory_cache_size: int
        -memory_cache: Dict[str, Tuple[Any, float]]
        -cache_access_times: Dict[str, float]
        -redis_client: Optional[redis.Redis]
        -stats: Dict[str, int]
        --
        +__init__(memory_cache_size: int, redis_host: str, ...)
        +get(key: str): Optional[Any]
        +set(key: str, value: Any): void
        +get_stats(): Dict[str, Any]
        +clear(): void
        -_get_cache_key(prompt: str, config_hash: str): str
        -_set_l1(key: str, value: Any, timestamp: float): void
        -_evict_lru(): void
    }
}

' Relationships
ComplianceFilter *-- ComplianceResult : creates
ComplianceFilter *-- PerformanceMonitor : uses
ComplianceFilter *-- IntelligentCache : uses
ComplianceResult *-- ComplianceAction : has
PerformanceMonitor ..> PerformanceMetrics : creates

@enduml
```

## 2. Detection System Class Diagram

```plantuml
@startuml DetectionSystemClasses
title Detection System Classes

package "Privacy Detection" {
    
    enum ViolationType {
        EMAIL
        PHONE
        SSN
        CREDIT_CARD
        ADDRESS
        MEDICAL_INFO
        FINANCIAL_INFO
        API_KEY
        TOKEN
        IP_ADDRESS
        DATE_OF_BIRTH
        DRIVER_LICENSE
        PASSPORT
        BANK_ACCOUNT
    }

    class PrivacyViolation {
        +violation_type: ViolationType
        +confidence: float
        +text_span: str
        +start_pos: int
        +end_pos: int
        +description: str
        --
        +__init__(violation_type, confidence, ...)
        +to_dict(): Dict[str, Any]
        +__str__(): str
    }

    class PrivacyDetector {
        -config: Dict[str, Any]
        -privacy_config: Dict[str, Any]
        -enabled_checks: Dict[str, bool]
        -risk_levels: Dict[str, float]
        -custom_patterns: Dict[str, str]
        -nlp: Optional[spacy.Language]
        -patterns: Dict[ViolationType, re.Pattern]
        --
        +__init__(config: Dict[str, Any])
        +detect_violations(text: str): List[PrivacyViolation]
        +calculate_privacy_score(violations: List[PrivacyViolation]): float
        +get_violation_summary(violations: List[PrivacyViolation]): Dict[str, Any]
        -_compile_patterns(): void
        -_detect_entities_nlp(text: str): List[PrivacyViolation]
        -_calculate_confidence(violation_type: ViolationType, text: str): float
    }
}

package "Hate Speech Detection" {
    
    class HateSpeechResult {
        +is_hate_speech: bool
        +confidence: float
        +label: str
        +all_scores: Dict[str, float]
        +model_used: str
        +processing_time: float
        --
        +__init__(is_hate_speech, confidence, ...)
        +to_dict(): Dict[str, Any]
        +__str__(): str
    }

    class HateSpeechDetector {
        -config: Dict[str, Any]
        -hate_speech_config: Dict[str, Any]
        -model_name: str
        -threshold: float
        -use_cache: bool
        -max_length: int
        -cache_dir: str
        -model: Optional[PreTrainedModel]
        -tokenizer: Optional[PreTrainedTokenizer]
        -pipeline: Optional[pipeline]
        -_model_loaded: bool
        -_total_predictions: int
        -_total_time: float
        --
        +__init__(config: Dict[str, Any])
        +detect_hate_speech(text: str): HateSpeechResult
        +batch_detect(texts: List[str]): List[HateSpeechResult]
        +update_threshold(new_threshold: float): void
        +switch_model(new_model_name: str): void
        +get_supported_models(): List[Dict[str, str]]
        +get_performance_stats(): Dict[str, float]
        +cleanup(): void
        -_load_model(): void
        -_parse_model_results(results: List[Dict[str, Any]]): Dict[str, Any]
        -_update_performance_stats(processing_time: float): void
    }
}

' Relationships
PrivacyDetector *-- PrivacyViolation : creates
PrivacyViolation *-- ViolationType : has
HateSpeechDetector *-- HateSpeechResult : creates

@enduml
```

## 3. Configuration and Factory Classes

```plantuml
@startuml ConfigurationClasses
title Configuration and Factory Classes

package "Configuration" {
    
    class ConfigurationManager {
        -config_path: str
        -config_data: Dict[str, Any]
        -watchers: List[Callable]
        --
        +__init__(config_path: str)
        +load_config(): Dict[str, Any]
        +save_config(config: Dict[str, Any]): void
        +update_section(section: str, data: Dict[str, Any]): void
        +get_section(section: str): Dict[str, Any]
        +validate_config(config: Dict[str, Any]): bool
        +add_config_watcher(callback: Callable): void
        +remove_config_watcher(callback: Callable): void
        -_notify_watchers(): void
        -_validate_section(section: str, data: Dict[str, Any]): bool
    }

    class ComplianceFilterFactory {
        +{static} create_from_config(config_path: str): ComplianceFilter
        +{static} create_optimized(config_path: str, **kwargs): ComplianceFilter
        +{static} create_standard(config_path: str, **kwargs): ComplianceFilter
        +{static} create_with_performance(config_path: str, **kwargs): ComplianceFilter
        +{static} validate_configuration(config: Dict[str, Any]): List[str]
        +{static} get_default_config(): Dict[str, Any]
        -{static} _apply_performance_settings(config: Dict[str, Any], **kwargs): Dict[str, Any]
        -{static} _validate_thresholds(thresholds: Dict[str, float]): bool
        -{static} _validate_weights(weights: Dict[str, float]): bool
    }
}

package "Utilities" {
    
    class TextProcessor {
        +{static} normalize_text(text: str): str
        +{static} extract_features(text: str): Dict[str, Any]
        +{static} truncate_text(text: str, max_length: int): str
        +{static} hash_text(text: str): str
        +{static} remove_pii(text: str, violations: List[PrivacyViolation]): str
        +{static} highlight_violations(text: str, violations: List[PrivacyViolation]): str
    }

    class MetricsCollector {
        -metrics: Dict[str, Any]
        -start_time: float
        -counters: Dict[str, int]
        -timers: Dict[str, List[float]]
        --
        +__init__()
        +increment(metric_name: str, value: int = 1): void
        +timing(metric_name: str, duration: float): void
        +gauge(metric_name: str, value: float): void
        +get_metrics(): Dict[str, Any]
        +reset_metrics(): void
        +start_timer(timer_name: str): void
        +end_timer(timer_name: str): float
    }

    class Logger {
        -logger: logging.Logger
        -handlers: List[logging.Handler]
        --
        +__init__(name: str, level: str, format: str)
        +info(message: str, **kwargs): void
        +warning(message: str, **kwargs): void
        +error(message: str, **kwargs): void
        +debug(message: str, **kwargs): void
        +audit(event_type: str, data: Dict[str, Any]): void
        +performance(metrics: Dict[str, Any]): void
        +add_handler(handler: logging.Handler): void
        +remove_handler(handler: logging.Handler): void
        +set_level(level: str): void
    }
}

' Factory pattern relationships
ComplianceFilterFactory ..> ComplianceFilter : creates
ComplianceFilterFactory --> ConfigurationManager : uses
ConfigurationManager --> TextProcessor : uses
MetricsCollector --> Logger : uses

@enduml
```

## 4. Web API and Integration Classes

```plantuml
@startuml WebAPIClasses
title Web API and Integration Classes

package "Web API" {
    
    class FlaskApp {
        -app: Flask
        -compliance_filter: ComplianceFilter
        -rate_limiter: RateLimiter
        -auth_manager: AuthManager
        --
        +__init__(compliance_filter: ComplianceFilter)
        +create_app(): Flask
        +setup_routes(): void
        +setup_middleware(): void
        +setup_error_handlers(): void
        +run(host: str, port: int, debug: bool): void
    }

    class APIController {
        -compliance_filter: ComplianceFilter
        -logger: Logger
        --
        +__init__(compliance_filter: ComplianceFilter)
        +check_single_text(request: Request): Response
        +check_batch_texts(request: Request): Response
        +get_performance_stats(request: Request): Response
        +update_configuration(request: Request): Response
        +health_check(request: Request): Response
        -_validate_request(request: Request, schema: Dict): bool
        -_format_response(data: Any, status_code: int): Response
        -_handle_error(error: Exception): Response
    }

    class RateLimiter {
        -limits: Dict[str, int]
        -windows: Dict[str, int]
        -storage: Dict[str, Dict[str, Any]]
        --
        +__init__(limits: Dict[str, int])
        +is_allowed(key: str, limit_type: str): bool
        +get_remaining(key: str, limit_type: str): int
        +reset_limit(key: str, limit_type: str): void
        -_get_window_key(key: str, window_size: int): str
        -_cleanup_expired(): void
    }

    class AuthManager {
        -api_keys: Dict[str, Dict[str, Any]]
        -sessions: Dict[str, Dict[str, Any]]
        --
        +__init__(config: Dict[str, Any])
        +validate_api_key(api_key: str): Optional[Dict[str, Any]]
        +validate_session(session_id: str): Optional[Dict[str, Any]]
        +create_session(user_id: str): str
        +revoke_session(session_id: str): bool
        +create_api_key(user_id: str, permissions: List[str]): str
        +revoke_api_key(api_key: str): bool
        -_hash_key(key: str): str
        -_generate_key(): str
    }
}

package "Client SDKs" {
    
    class PythonClient {
        -base_url: str
        -api_key: str
        -timeout: int
        -session: requests.Session
        --
        +__init__(base_url: str, api_key: str, timeout: int)
        +check_compliance(text: str, user_context: Dict): ComplianceResult
        +batch_check_compliance(texts: List[str]): List[ComplianceResult]
        +get_performance_stats(): Dict[str, Any]
        +update_configuration(config: Dict[str, Any]): bool
        -_make_request(method: str, endpoint: str, data: Dict): Dict
        -_handle_response(response: requests.Response): Dict
    }

    class AsyncPythonClient {
        -base_url: str
        -api_key: str
        -timeout: int
        -session: aiohttp.ClientSession
        --
        +__init__(base_url: str, api_key: str, timeout: int)
        +async check_compliance(text: str, user_context: Dict): ComplianceResult
        +async batch_check_compliance(texts: List[str]): List[ComplianceResult]
        +async get_performance_stats(): Dict[str, Any]
        -async _make_request(method: str, endpoint: str, data: Dict): Dict
        -async _handle_response(response: aiohttp.ClientResponse): Dict
        +async __aenter__(): AsyncPythonClient
        +async __aexit__(exc_type, exc_val, exc_tb): void
    }
}

' Web API relationships
FlaskApp *-- APIController : uses
FlaskApp *-- RateLimiter : uses
FlaskApp *-- AuthManager : uses
APIController --> ComplianceFilter : uses
PythonClient ..> APIController : calls
AsyncPythonClient ..> APIController : calls

@enduml
```

## 5. Exception and Error Handling Classes

```plantuml
@startuml ExceptionClasses
title Exception and Error Handling Classes

package "Exceptions" {
    
    class ComplianceFilterException {
        +message: str
        +error_code: str
        +details: Dict[str, Any]
        --
        +__init__(message: str, error_code: str, details: Dict)
        +__str__(): str
        +to_dict(): Dict[str, Any]
    }

    class ConfigurationError {
        +config_section: str
        +invalid_fields: List[str]
        --
        +__init__(message: str, config_section: str, invalid_fields: List[str])
    }

    class ModelLoadError {
        +model_name: str
        +model_path: str
        --
        +__init__(message: str, model_name: str, model_path: str)
    }

    class CacheError {
        +cache_type: str
        +operation: str
        --
        +__init__(message: str, cache_type: str, operation: str)
    }

    class ValidationError {
        +field_name: str
        +field_value: Any
        +validation_rule: str
        --
        +__init__(message: str, field_name: str, field_value: Any, validation_rule: str)
    }

    class RateLimitExceeded {
        +limit_type: str
        +reset_time: int
        +current_usage: int
        +limit: int
        --
        +__init__(limit_type: str, reset_time: int, current_usage: int, limit: int)
    }

    class AuthenticationError {
        +auth_type: str
        +provided_credentials: str
        --
        +__init__(message: str, auth_type: str, provided_credentials: str)
    }
}

package "Error Handlers" {
    
    class ErrorHandler {
        -logger: Logger
        -error_counts: Dict[str, int]
        --
        +__init__(logger: Logger)
        +handle_exception(exception: Exception, context: Dict[str, Any]): ComplianceResult
        +log_error(error: Exception, context: Dict[str, Any]): void
        +get_error_stats(): Dict[str, Any]
        +should_retry(error: Exception): bool
        -_create_safe_result(error: Exception): ComplianceResult
        -_classify_error(error: Exception): str
    }

    class RetryManager {
        -max_retries: int
        -backoff_factor: float
        -retry_on: List[type]
        --
        +__init__(max_retries: int, backoff_factor: float, retry_on: List[type])
        +execute_with_retry(func: Callable, *args, **kwargs): Any
        +should_retry(exception: Exception, attempt: int): bool
        +calculate_delay(attempt: int): float
    }
}

' Exception hierarchy
ComplianceFilterException <|-- ConfigurationError
ComplianceFilterException <|-- ModelLoadError  
ComplianceFilterException <|-- CacheError
ComplianceFilterException <|-- ValidationError
ComplianceFilterException <|-- RateLimitExceeded
ComplianceFilterException <|-- AuthenticationError

' Error handling relationships
ErrorHandler --> ComplianceFilterException : handles
RetryManager --> ErrorHandler : uses

@enduml
```

## Class Relationships Summary

### Key Design Patterns Used:

1. **Factory Pattern**: `ComplianceFilterFactory` creates different types of compliance filters
2. **Strategy Pattern**: Different scoring methods (weighted_average, max, product)
3. **Observer Pattern**: Configuration watchers for hot-reload
4. **Decorator Pattern**: Performance monitoring and caching decorators
5. **Singleton Pattern**: Logger and metrics collector
6. **Command Pattern**: API endpoints as commands
7. **Template Method Pattern**: Base detection classes with specific implementations

### Core Dependencies:

1. **ComplianceFilter** depends on:
   - PrivacyDetector, HateSpeechDetector (detection)
   - IntelligentCache, PerformanceMonitor (performance)
   - ConfigurationManager (configuration)

2. **Detection System** is independent and pluggable
3. **Performance System** provides cross-cutting concerns
4. **Web API** wraps core functionality with HTTP interface
5. **Error Handling** provides consistent error management

### Extensibility Points:

1. **New Detectors**: Implement base detection interface
2. **New Cache Backends**: Implement cache interface
3. **New Scoring Methods**: Add to ComplianceFilter
4. **New API Formats**: Add controllers for different protocols
5. **New Authentication**: Implement auth interface

This class diagram provides a comprehensive view of the system architecture, making it easy to understand the codebase structure and extend functionality.
