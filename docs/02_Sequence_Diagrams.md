# Sequence Diagrams - LLM Compliance Filter System

## Overview
This document contains sequence diagrams for the key workflows in the LLM Compliance Filter System, showing the interactions between different components over time.

## 1. Single Text Compliance Check

```plantuml
@startuml SingleTextCheck
title Single Text Compliance Check Sequence

participant "Client" as C
participant "ComplianceFilter" as CF
participant "IntelligentCache" as IC
participant "PrivacyDetector" as PD
participant "HateSpeechDetector" as HSD
participant "PerformanceMonitor" as PM

C -> CF: check_compliance(text, user_context)
activate CF

CF -> PM: start_timer()
activate PM

CF -> IC: get(cache_key)
activate IC
IC --> CF: cached_result (if exists)
deactivate IC

alt Cache Hit
    CF -> PM: record_request(cache_hit=True)
    CF --> C: ComplianceResult
else Cache Miss
    CF -> PD: detect_violations(text)
    activate PD
    
    PD -> PD: apply_regex_patterns()
    PD -> PD: nlp_entity_detection()
    PD --> CF: privacy_violations[]
    deactivate PD
    
    CF -> HSD: detect_hate_speech(text)
    activate HSD
    
    HSD -> HSD: tokenize_text()
    HSD -> HSD: model_inference()
    HSD -> HSD: parse_results()
    HSD --> CF: HateSpeechResult
    deactivate HSD
    
    CF -> CF: calculate_overall_score()
    CF -> CF: determine_action()
    CF -> CF: generate_reasoning()
    
    CF -> IC: set(cache_key, result)
    activate IC
    IC -> IC: store_l1_cache()
    IC -> IC: store_l2_redis()
    deactivate IC
    
    CF -> PM: record_request(cache_hit=False)
    
    CF -> CF: log_compliance_check()
    CF --> C: ComplianceResult
end

deactivate PM
deactivate CF

@enduml
```

## 2. Batch Processing Workflow

```plantuml
@startuml BatchProcessing
title Batch Processing Workflow

participant "Client" as C
participant "ComplianceFilter" as CF
participant "ThreadPoolExecutor" as TPE
participant "Worker1" as W1
participant "Worker2" as W2
participant "IntelligentCache" as IC

C -> CF: batch_check_compliance(texts[], parallel=True)
activate CF

CF -> CF: determine_chunk_size()
CF -> CF: create_chunks()

CF -> TPE: submit_chunks()
activate TPE

par Parallel Processing
    TPE -> W1: process_chunk(chunk1)
    activate W1
    
    W1 -> CF: check_compliance(text1)
    CF -> IC: get/set operations
    W1 -> CF: check_compliance(text2)
    CF -> IC: get/set operations
    W1 --> TPE: chunk1_results[]
    deactivate W1
    
else
    TPE -> W2: process_chunk(chunk2)
    activate W2
    
    W2 -> CF: check_compliance(text3)
    CF -> IC: get/set operations
    W2 -> CF: check_compliance(text4)
    CF -> IC: get/set operations
    W2 --> TPE: chunk2_results[]
    deactivate W2
end

TPE --> CF: all_results[]
deactivate TPE

CF -> CF: combine_results()
CF -> CF: log_batch_performance()
CF --> C: ComplianceResult[]

deactivate CF

@enduml
```

## 3. Async Processing Flow

```plantuml
@startuml AsyncProcessing
title Async Processing Flow

participant "Client" as C
participant "ComplianceFilter" as CF
participant "AsyncExecutor" as AE
participant "EventLoop" as EL

C -> CF: check_compliance_async(text)
activate CF

CF -> EL: get_event_loop()
activate EL

EL -> AE: run_in_executor(check_compliance, text)
activate AE

AE -> CF: check_compliance(text)
note right: Runs in thread pool
CF --> AE: ComplianceResult
deactivate AE

EL --> CF: Future[ComplianceResult]
deactivate EL

CF --> C: await ComplianceResult
deactivate CF

@enduml
```

## 4. Performance Monitoring Workflow

```plantuml
@startuml PerformanceMonitoring
title Performance Monitoring Workflow

participant "ComplianceFilter" as CF
participant "PerformanceMonitor" as PM
participant "IntelligentCache" as IC
participant "SystemMetrics" as SM

CF -> PM: record_request(response_time, cache_hit)
activate PM

PM -> PM: update_response_times()
PM -> PM: update_cache_stats()
PM -> PM: update_request_count()

PM -> SM: get_system_metrics()
activate SM
SM -> SM: get_memory_usage()
SM -> SM: get_cpu_usage()
SM --> PM: system_stats
deactivate SM

CF -> PM: get_metrics()
PM -> PM: calculate_percentiles()
PM -> PM: calculate_rates()
PM -> IC: get_cache_stats()
activate IC
IC --> PM: cache_statistics
deactivate IC

PM --> CF: PerformanceMetrics
deactivate PM

@enduml
```

## 5. Cache Management Flow

```plantuml
@startuml CacheManagement
title Multi-Tier Cache Management

participant "ComplianceFilter" as CF
participant "IntelligentCache" as IC
participant "L1Cache" as L1
participant "RedisCache" as L2

CF -> IC: get(cache_key)
activate IC

IC -> L1: check_memory_cache()
activate L1

alt L1 Hit
    L1 --> IC: cached_value
    IC -> IC: update_access_time()
    IC --> CF: result
else L1 Miss
    deactivate L1
    IC -> L2: redis_get(key)
    activate L2
    
    alt L2 Hit
        L2 --> IC: serialized_value
        IC -> IC: deserialize()
        IC -> L1: promote_to_l1()
        activate L1
        L1 -> L1: check_capacity()
        L1 -> L1: evict_lru_if_needed()
        deactivate L1
        IC --> CF: result
    else L2 Miss
        deactivate L2
        IC --> CF: null
    end
end

deactivate IC

alt Cache Miss - Store New Result
    CF -> IC: set(cache_key, result)
    activate IC
    
    IC -> L1: store_in_memory()
    activate L1
    L1 -> L1: check_capacity()
    L1 -> L1: evict_lru_if_needed()
    deactivate L1
    
    IC -> L2: redis_set(key, serialized_value, ttl)
    activate L2
    L2 -> L2: store_with_expiration()
    deactivate L2
    
    deactivate IC
end

@enduml
```

## 6. Error Handling Sequence

```plantuml
@startuml ErrorHandling
title Error Handling Sequence

participant "Client" as C
participant "ComplianceFilter" as CF
participant "HateSpeechDetector" as HSD
participant "PerformanceMonitor" as PM

C -> CF: check_compliance(text)
activate CF

CF -> HSD: detect_hate_speech(text)
activate HSD

HSD -> HSD: model_inference()

alt Model Error
    HSD -> HSD: log_error()
    HSD -> HSD: return_safe_default()
    HSD --> CF: error_result (is_hate_speech=True)
    deactivate HSD
    
    CF -> CF: log_error()
    CF -> PM: record_request(error=True)
    activate PM
    PM -> PM: increment_error_count()
    deactivate PM
    
    CF -> CF: create_safe_result()
    CF --> C: ComplianceResult(BLOCK, error_msg)
else Normal Flow
    HSD --> CF: HateSpeechResult
    deactivate HSD
    CF -> CF: process_normally()
    CF --> C: ComplianceResult
end

deactivate CF

@enduml
```

## 7. Configuration Update Flow

```plantuml
@startuml ConfigurationUpdate
title Configuration Update Flow

participant "Admin" as A
participant "ComplianceFilter" as CF
participant "IntelligentCache" as IC
participant "ConfigManager" as CM

A -> CF: update_thresholds(new_thresholds)
activate CF

CF -> CF: validate_thresholds()

alt Valid Configuration
    CF -> CM: update_config(new_thresholds)
    activate CM
    CM -> CM: validate_config()
    CM -> CM: write_to_file()
    CM --> CF: success
    deactivate CM
    
    CF -> CF: apply_new_thresholds()
    CF -> IC: clear_cache()
    activate IC
    IC -> IC: clear_memory_cache()
    IC -> IC: clear_redis_cache()
    deactivate IC
    
    CF -> CF: log_config_change()
    CF --> A: success_response
else Invalid Configuration
    CF -> CF: log_validation_error()
    CF --> A: validation_error
end

deactivate CF

@enduml
```

## Sequence Diagram Analysis

### Key Patterns Identified

1. **Cache-First Pattern**: All requests check cache before processing
2. **Parallel Processing**: Batch operations use thread pools for scalability
3. **Error Resilience**: Comprehensive error handling with safe defaults
4. **Performance Monitoring**: Every operation is tracked for metrics
5. **Multi-Tier Caching**: L1 (memory) + L2 (Redis) for optimal performance

### Performance Characteristics

1. **Cache Hit Path**: ~1-5ms response time
2. **Cache Miss Path**: ~50-200ms response time (depending on ML models)
3. **Batch Processing**: Linear scalability with worker threads
4. **Error Recovery**: Graceful degradation with safe defaults

### Integration Points

1. **Client Integration**: Simple async/sync API calls
2. **Cache Integration**: Transparent multi-tier caching
3. **Monitoring Integration**: Built-in performance tracking
4. **Configuration**: Hot-reload of settings without restart

This sequence diagram documentation provides a comprehensive view of how the system components interact during runtime, making it easier for developers to understand the flow and optimize performance.
