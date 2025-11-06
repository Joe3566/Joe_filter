# Activity Diagrams - LLM Compliance Filter System

## Overview
This document contains activity diagrams for the LLM Compliance Filter System, showing the workflow and decision points in key processes.

## 1. Single Text Compliance Check Activity

```plantuml
@startuml SingleComplianceCheck
title Single Text Compliance Check Activity

start

:Receive text input and user context;

if (Is caching enabled?) then (yes)
    :Generate cache key from text + config;
    :Check L1 cache;
    if (Cache hit in L1?) then (yes)
        :Record cache hit metrics;
        :Return cached result;
        stop
    endif
    
    :Check L2 cache (Redis);
    if (Cache hit in L2?) then (yes)
        :Deserialize cached result;
        :Promote to L1 cache;
        :Record cache hit metrics;
        :Return cached result;
        stop
    endif
    
    :Record cache miss;
endif

:Start processing timer;

partition "Privacy Detection" {
    :Initialize privacy violations list;
    
    if (Email detection enabled?) then (yes)
        :Apply email regex patterns;
        :Add violations to list;
    endif
    
    if (Phone detection enabled?) then (yes)
        :Apply phone regex patterns;
        :Add violations to list;
    endif
    
    if (SSN detection enabled?) then (yes)
        :Apply SSN regex patterns;
        :Add violations to list;
    endif
    
    if (Credit card detection enabled?) then (yes)
        :Apply credit card patterns;
        :Add violations to list;
    endif
    
    if (Custom patterns enabled?) then (yes)
        :Apply custom regex patterns;
        :Add violations to list;
    endif
    
    if (NLP detection available?) then (yes)
        :Run spaCy NER;
        :Extract person, location, organization entities;
        :Add NLP violations to list;
    endif
    
    :Calculate privacy score from violations;
}

partition "Hate Speech Detection" {
    if (Hate speech detector available?) then (yes)
        :Load transformer model if not cached;
        :Tokenize input text;
        :Run model inference;
        :Parse model results;
        :Extract confidence scores;
        :Determine if hate speech detected;
    else (no)
        :Set hate speech score to 0;
    endif
}

:Calculate overall compliance score;
note right
    Using configured method:
    - weighted_average
    - max
    - product
end note

if (Score >= block threshold?) then (yes)
    :Set action to BLOCK;
elseif (Score >= warn threshold?) then (yes)
    :Set action to WARN;
else (no)
    :Set action to ALLOW;
endif

:Generate human-readable reasoning;

:Create ComplianceResult object;

:Stop processing timer;

if (Caching enabled?) then (yes)
    :Store result in cache;
    :Update cache statistics;
endif

if (Monitoring enabled?) then (yes)
    :Record processing metrics;
    :Update performance statistics;
endif

if (Audit logging enabled?) then (yes)
    :Log compliance check details;
    :Write to audit trail;
endif

:Return ComplianceResult;

stop

@enduml
```

## 2. Batch Processing Activity

```plantuml
@startuml BatchProcessing
title Batch Processing Activity

start

:Receive batch of texts;

if (Texts list empty?) then (yes)
    :Return empty results;
    stop
endif

:Validate user contexts length;
:Pad contexts if necessary;

:Start batch timer;

if (Parallel processing enabled AND batch size > 1?) then (yes)
    partition "Parallel Processing" {
        :Calculate optimal chunk size;
        note right
            chunk_size = max(1, len(texts) / (workers * 2))
            chunk_size = min(chunk_size, 50)
        end note
        
        :Split texts into chunks;
        
        fork
            :Submit chunk 1 to worker thread;
            :Process texts in chunk 1 sequentially;
            :Return chunk 1 results;
        fork again
            :Submit chunk 2 to worker thread;
            :Process texts in chunk 2 sequentially;
            :Return chunk 2 results;
        fork again
            :Submit chunk N to worker thread;
            :Process texts in chunk N sequentially;
            :Return chunk N results;
        end fork
        
        :Wait for all chunks to complete;
        :Combine results in original order;
    }
else (no)
    partition "Sequential Processing" {
        :Initialize results list;
        
        repeat
            :Get next text from batch;
            :Run single compliance check;
            :Add result to results list;
        repeat while (More texts remaining?)
    }
endif

:Calculate total processing time;
:Calculate throughput (texts/second);

if (Performance monitoring enabled?) then (yes)
    :Record batch processing metrics;
    :Update throughput statistics;
endif

:Log batch completion;
note right
    "Batch processed X items in Y seconds (Z items/sec)"
end note

:Return results list;

stop

@enduml
```

## 3. Cache Management Activity

```plantuml
@startuml CacheManagement
title Cache Management Activity

start

:Receive cache operation request;

if (Operation type?) then (GET)
    partition "Cache Retrieval" {
        :Check L1 memory cache;
        
        if (Found in L1?) then (yes)
            if (Not expired?) then (yes)
                :Update access time;
                :Increment L1 hit counter;
                :Return cached value;
                stop
            else (expired)
                :Remove from L1 cache;
            endif
        endif
        
        :Increment L1 miss counter;
        
        if (Redis cache available?) then (yes)
            :Query Redis with key;
            
            if (Found in Redis?) then (yes)
                :Deserialize value;
                :Increment L2 hit counter;
                
                if (L1 cache has space?) then (yes)
                    :Store in L1 cache;
                else (no)
                    :Evict LRU item from L1;
                    :Store in L1 cache;
                endif
                
                :Return cached value;
                stop
            endif
        endif
        
        :Increment L2 miss counter;
        :Return null (cache miss);
    }
    
elseif (SET) then
    partition "Cache Storage" {
        :Prepare value for caching;
        
        if (L1 cache full?) then (yes)
            :Find least recently used item;
            :Remove LRU item from L1;
            :Increment eviction counter;
        endif
        
        :Store in L1 cache with timestamp;
        
        if (Redis cache available?) then (yes)
            :Serialize value;
            :Store in Redis with TTL;
        endif
        
        :Increment total sets counter;
        :Update cache statistics;
    }
    
else (CLEAR)
    partition "Cache Clearing" {
        :Clear all L1 cache entries;
        :Reset access times;
        
        if (Redis cache available?) then (yes)
            :Find all compliance keys in Redis;
            :Delete compliance keys;
        endif
        
        :Reset cache statistics;
    }
endif

stop

@enduml
```

## 4. Configuration Update Activity

```plantuml
@startuml ConfigurationUpdate
title Configuration Update Activity

start

:Receive configuration update request;

:Extract configuration section and new values;

partition "Validation" {
    if (Threshold update?) then (yes)
        repeat
            :Get threshold name and value;
            if (Value between 0.0 and 1.0?) then (no)
                :Add validation error;
            endif
        repeat while (More thresholds?)
        
    elseif (Weight update?) then (yes)
        :Calculate total weight sum;
        if (Sum approximately equals 1.0?) then (no)
            :Add validation warning;
        endif
        
    elseif (Model switch?) then (yes)
        if (Model supported?) then (no)
            :Add validation error;
        endif
    endif
    
    if (Validation errors exist?) then (yes)
        :Return validation error response;
        stop
    endif
}

partition "Apply Changes" {
    :Backup current configuration;
    
    if (Threshold update?) then (yes)
        :Update threshold values;
    elseif (Weight update?) then (yes)
        :Update scoring weights;
    elseif (Model switch?) then (yes)
        :Cleanup current model;
        :Load new model;
        if (Model load failed?) then (yes)
            :Restore previous model;
            :Return error response;
            stop
        endif
    endif
    
    :Calculate new configuration hash;
    
    if (Caching enabled?) then (yes)
        :Clear all cached results;
        note right: Cache invalidation needed due to config change
    endif
}

partition "Persistence" {
    if (Save to file enabled?) then (yes)
        :Write configuration to YAML file;
        if (Write failed?) then (yes)
            :Restore backup configuration;
            :Return error response;
            stop
        endif
    endif
}

:Log configuration change;
:Notify configuration watchers;
:Return success response;

stop

@enduml
```

## 5. Error Handling and Recovery Activity

```plantuml
@startuml ErrorHandling
title Error Handling and Recovery Activity

start

:Detect error/exception;

:Classify error type;
note right
    - Configuration error
    - Model load error
    - Cache error
    - Network error
    - Processing error
end note

if (Error type?) then (Configuration)
    :Log configuration error;
    :Use default safe configuration;
    :Continue with degraded functionality;
    
elseif (Model Load) then
    :Log model load error;
    if (Fallback model available?) then (yes)
        :Load fallback model;
        :Continue with fallback;
    else (no)
        :Disable hate speech detection;
        :Continue with privacy detection only;
    endif
    
elseif (Cache) then
    :Log cache error;
    :Disable caching temporarily;
    :Continue without cache;
    
elseif (Network/Redis) then
    :Log network error;
    :Fallback to L1 cache only;
    :Continue with reduced caching;
    
else (Processing)
    :Log processing error;
    if (Retry possible?) then (yes)
        :Calculate retry delay;
        :Wait for backoff period;
        :Retry operation;
        if (Retry successful?) then (yes)
            :Return successful result;
            stop
        elseif (Max retries reached?) then (yes)
            :Create safe error result;
        else
            :Increment retry count;
        endif
    else (no)
        :Create safe error result;
    endif
endif

:Update error statistics;
:Record error metrics;

if (Critical error?) then (yes)
    :Set system to safe mode;
    :Block all requests with safe default;
    :Alert system administrators;
else (no)
    :Continue normal operation;
endif

:Return error result or continue;

stop

@enduml
```

## 6. Performance Optimization Activity

```plantuml
@startuml PerformanceOptimization
title Performance Optimization Activity

start

:Monitor system performance metrics;

if (Memory usage > threshold?) then (yes)
    partition "Memory Optimization" {
        :Calculate current memory usage;
        
        if (Usage > 1GB?) then (yes)
            :Clear oldest 50% of cache entries;
            :Force garbage collection;
            :Log memory optimization;
        endif
        
        if (Cache size > limit?) then (yes)
            :Evict LRU cache entries;
            :Reduce cache size target;
        endif
    }
endif

if (Response time > SLA?) then (yes)
    partition "Performance Tuning" {
        :Analyze bottlenecks;
        
        if (Cache hit rate < 80%?) then (yes)
            :Increase cache size;
            :Extend cache TTL;
        endif
        
        if (Model inference slow?) then (yes)
            :Enable model warm-up;
            :Consider faster model;
        endif
        
        if (Batch size inefficient?) then (yes)
            :Adjust chunk size;
            :Optimize worker allocation;
        endif
    }
endif

if (Error rate > threshold?) then (yes)
    partition "Reliability Improvement" {
        :Identify error patterns;
        
        :Enable more aggressive retries;
        :Add circuit breakers;
        :Improve error recovery;
    }
endif

:Update performance configuration;
:Log optimization actions;

stop

@enduml
```

## Activity Diagram Analysis

### Key Process Flows:

1. **Single Compliance Check**: Linear flow with decision points for caching, detection methods, and scoring
2. **Batch Processing**: Fork/join pattern for parallel processing with sequential fallback
3. **Cache Management**: Multi-tier caching with LRU eviction and TTL management
4. **Configuration Updates**: Validation-first approach with rollback capability
5. **Error Handling**: Graceful degradation with retry logic and safe defaults
6. **Performance Optimization**: Reactive optimization based on metrics and thresholds

### Decision Points:

1. **Caching Strategy**: L1 → L2 → Process → Store
2. **Processing Mode**: Parallel vs Sequential based on batch size and resources
3. **Error Recovery**: Retry, fallback, or safe default based on error type
4. **Optimization Triggers**: Memory, performance, and reliability thresholds

### Performance Characteristics:

1. **Cache Hit Path**: ~1-5ms (immediate return)
2. **Cache Miss Path**: ~50-200ms (full processing)
3. **Parallel Processing**: Linear scalability with worker threads
4. **Error Recovery**: Graceful degradation without service interruption

### Optimization Strategies:

1. **Proactive Caching**: Cache warming and intelligent prefetching
2. **Adaptive Batching**: Dynamic chunk sizing based on performance
3. **Circuit Breaker**: Fail-fast for known problematic operations
4. **Graceful Degradation**: Continue with reduced functionality during failures

These activity diagrams provide a comprehensive view of the system's behavior, making it easier to understand the workflow, identify bottlenecks, and optimize performance.
