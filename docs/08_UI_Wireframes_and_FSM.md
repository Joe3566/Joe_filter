# UI Wireframes and FSM Diagram - LLM Compliance Filter System

## UI Mockups and Wireframes

### Web Interface Wireframes

```plantuml
@startuml WebInterfaceWireframes
!define RECTANGLE class

title LLM Compliance Filter - Web Interface Wireframes

RECTANGLE "Main Dashboard" as dashboard {
    -- Header --
    🛡️ LLM Compliance Filter
    [Performance Stats] [Configuration] [Logout]
    
    -- Single Text Check --
    📝 Single Text Check
    [Text Area: "Enter text to check..."]
    [🔍 Check Compliance] [⚙️ Advanced Options]
    
    -- Results Panel --
    📊 Compliance Result
    Status: [✅ ALLOW] | [⚠️ WARN] | [🚫 BLOCK]
    Score: 0.234 | Processing: 47ms
    Reasoning: "No significant violations detected."
    
    -- Batch Processing --
    📦 Batch Processing
    [📁 Upload File] [📋 Paste Multiple Texts]
    Progress: ████████░░ 80% (40/50 processed)
    [📥 Download Results]
}

RECTANGLE "Performance Dashboard" as perf_dash {
    -- Performance Metrics --
    📈 Real-time Metrics
    
    Requests/sec: 245.3
    Avg Response: 67ms
    Cache Hit Rate: 87.3%
    Error Rate: 0.2%
    
    -- Charts Section --
    [📊 Response Time Chart]
    [📈 Throughput Graph]
    [🎯 Cache Performance]
    [⚠️ Error Rate Trends]
    
    -- System Health --
    🖥️ System Health
    CPU: 45% | Memory: 2.1GB | Disk: 78%
    [🔄 Refresh] [📋 Full Report]
}

RECTANGLE "Configuration Panel" as config_panel {
    -- Threshold Settings --
    ⚙️ Compliance Thresholds
    Block Threshold: [0.7] (0.0 - 1.0)
    Warn Threshold: [0.5] (0.0 - 1.0)
    Pass Threshold: [0.2] (0.0 - 1.0)
    
    -- Scoring Weights --
    🏷️ Detection Weights
    Hate Speech: [0.6] (60%)
    Privacy: [0.4] (40%)
    Scoring Method: [weighted_average ▼]
    
    -- Model Settings --
    🤖 Model Configuration
    Hate Speech Model: [toxic-bert ▼]
    Enable Caching: [☑️]
    Enable Monitoring: [☑️]
    
    [💾 Save Configuration] [🔄 Reset to Defaults]
}

dashboard --> perf_dash : Navigate
dashboard --> config_panel : Configure
perf_dash --> dashboard : Back
config_panel --> dashboard : Back

@enduml
```

### Mobile-Responsive Wireframes

```plantuml
@startuml MobileWireframes
title Mobile-Responsive Interface

RECTANGLE "Mobile Main View" as mobile_main {
    ╔════════════════════════╗
    ║ 🛡️ Compliance Filter   ║
    ║                        ║
    ║ 📝 Check Text          ║
    ║ ┌──────────────────┐   ║
    ║ │ Enter text here  │   ║
    ║ │                  │   ║
    ║ │                  │   ║
    ║ └──────────────────┘   ║
    ║ [🔍 Check]             ║
    ║                        ║
    ║ 📊 Last Result:        ║
    ║ ✅ ALLOW (Score: 0.23) ║
    ║                        ║
    ║ ═══ Navigation ═══     ║
    ║ [📊] [⚙️] [📦] [📈]    ║
    ╚════════════════════════╝
}

RECTANGLE "Mobile Result View" as mobile_result {
    ╔════════════════════════╗
    ║ 📊 Compliance Result   ║
    ║                        ║
    ║ 🚫 BLOCK               ║
    ║ Score: 0.847           ║
    ║ Time: 134ms            ║
    ║                        ║
    ║ 📝 Reasoning:          ║
    ║ Privacy violations     ║
    ║ detected: email, phone ║
    ║                        ║
    ║ 🔍 Violations Found:   ║
    ║ • Email: j***@test.com ║
    ║ • Phone: (555) ***-*** ║
    ║                        ║
    ║ [🔙 Back] [📋 Details]  ║
    ╚════════════════════════╝
}

mobile_main --> mobile_result : Check Text
mobile_result --> mobile_main : Back

@enduml
```

### API Documentation Interface

```plantuml
@startuml APIDocumentation
title API Documentation Interface

RECTANGLE "API Documentation Portal" as api_docs {
    -- Header --
    📚 LLM Compliance Filter API Documentation v2.1
    [🏠 Home] [🔐 Authentication] [🧪 Try It] [📥 Download SDK]
    
    -- Navigation Sidebar --
    📑 Contents
    • Getting Started
    • Authentication
    • Endpoints
      ├─ POST /api/check
      ├─ POST /api/batch
      ├─ GET /api/stats
      └─ PUT /api/config
    • Response Formats
    • Error Codes
    • SDKs & Examples
    • Rate Limits
    
    -- Main Content Area --
    🚀 Getting Started
    
    Base URL: https://api.compliance-filter.com/v2
    
    📋 Quick Example:
    ```json
    POST /api/check
    {
      "text": "Hello world",
      "user_context": {"user_id": "123"}
    }
    ```
    
    📤 Response:
    ```json
    {
      "action": "ALLOW",
      "score": 0.234,
      "reasoning": "No violations detected",
      "processing_time": 0.047
    }
    ```
    
    -- Interactive Section --
    🧪 Try It Live
    [Text Input Field]
    [Send Request] [🔄 Loading...]
    [Response Display Area]
}

RECTANGLE "Endpoint Details" as endpoint_details {
    -- Endpoint Specification --
    🎯 POST /api/check
    
    📝 Description:
    Check a single text for compliance violations
    
    📥 Request Body:
    ```json
    {
      "text": "string (required)",
      "user_context": "object (optional)",
      "use_cache": "boolean (optional)"
    }
    ```
    
    📤 Response Format:
    ```json
    {
      "action": "ALLOW|WARN|BLOCK",
      "score": "number (0.0-1.0)",
      "hate_speech_score": "number",
      "privacy_score": "number",
      "violations": ["array"],
      "reasoning": "string",
      "processing_time": "number",
      "timestamp": "string"
    }
    ```
    
    ⚠️ Error Responses:
    • 400: Bad Request
    • 401: Unauthorized
    • 429: Rate Limited
    • 500: Internal Error
    
    📊 Rate Limits:
    • 1000 requests/hour (authenticated)
    • 100 requests/hour (unauthenticated)
}

api_docs --> endpoint_details : View Endpoint
endpoint_details --> api_docs : Back to Docs

@enduml
```

## Finite State Machine Diagram

### Compliance Processing FSM

```plantuml
@startuml ComplianceProcessingFSM
title Compliance Processing - Finite State Machine

[*] --> Initialized : System Start

state Initialized {
    [*] --> ConfigLoaded
    ConfigLoaded : Load configuration
    ConfigLoaded : Initialize detectors
    ConfigLoaded --> Ready : All components loaded
    ConfigLoaded --> ConfigError : Config load failed
    ConfigError --> ConfigLoaded : Retry with defaults
}

Ready --> Processing : receive_request()

state Processing {
    [*] --> CacheCheck
    
    CacheCheck : Check L1/L2 cache
    CacheCheck --> CacheHit : cache_found()
    CacheCheck --> CacheMiss : cache_not_found()
    
    CacheHit --> ResultReady : return_cached_result()
    
    CacheMiss --> DetectionPhase : start_detection()
    
    state DetectionPhase {
        [*] --> PrivacyDetection
        [*] --> HateSpeechDetection
        
        PrivacyDetection : Apply regex patterns
        PrivacyDetection : Run NLP detection
        PrivacyDetection --> PrivacyComplete : violations_detected()
        
        HateSpeechDetection : Load ML model
        HateSpeechDetection : Run inference
        HateSpeechDetection --> HateSpeechComplete : analysis_complete()
        
        PrivacyComplete --> ScoreCalculation
        HateSpeechComplete --> ScoreCalculation
    }
    
    ScoreCalculation : Calculate overall score
    ScoreCalculation : Determine action
    ScoreCalculation --> ResultReady : scoring_complete()
    
    ResultReady : Generate reasoning
    ResultReady : Create result object
    ResultReady --> CacheStore : store_in_cache()
    
    CacheStore --> Completed : result_cached()
}

Processing --> Completed : processing_finished()
Processing --> ErrorState : processing_failed()

state ErrorState {
    [*] --> ErrorAnalysis
    ErrorAnalysis : Classify error type
    ErrorAnalysis --> RetryableError : can_retry()
    ErrorAnalysis --> FatalError : cannot_retry()
    
    RetryableError --> Processing : retry_processing()
    FatalError --> SafeDefault : create_safe_result()
    SafeDefault --> Completed : error_handled()
}

Completed --> Ready : ready_for_next()
Completed --> Shutdown : system_shutdown()

state ConfigUpdate {
    [*] --> ValidateConfig
    ValidateConfig : Check configuration
    ValidateConfig --> ApplyConfig : config_valid()
    ValidateConfig --> ConfigError : config_invalid()
    
    ApplyConfig : Update thresholds
    ApplyConfig : Clear cache
    ApplyConfig --> Ready : config_applied()
}

Ready --> ConfigUpdate : update_configuration()
ConfigUpdate --> Ready : configuration_updated()

Shutdown --> [*] : cleanup_complete()

note right of Processing
  Main processing state with
  parallel detection workflows
end note

note right of ErrorState
  Error recovery with
  graceful degradation
end note

@enduml
```

### Cache State Machine

```plantuml
@startuml CacheStateMachine
title Intelligent Cache - State Machine

[*] --> Initialized : cache_start()

state Initialized {
    [*] --> L1Init
    L1Init : Initialize memory cache
    L1Init --> L2Init : memory_ready()
    
    L2Init : Connect to Redis
    L2Init --> Ready : redis_connected()
    L2Init --> L1Only : redis_failed()
    
    L1Only : Fallback to L1 only
    L1Only --> Ready : fallback_ready()
}

Ready --> CacheOperation : cache_request()

state CacheOperation {
    [*] --> RequestType
    
    RequestType --> GetOperation : get_request()
    RequestType --> SetOperation : set_request()
    RequestType --> ClearOperation : clear_request()
    
    state GetOperation {
        [*] --> CheckL1
        CheckL1 : Look in memory cache
        CheckL1 --> L1Hit : found_in_l1()
        CheckL1 --> CheckL2 : not_in_l1()
        
        L1Hit : Update access time
        L1Hit --> CacheHitResult : return_value()
        
        CheckL2 : Query Redis
        CheckL2 --> L2Hit : found_in_l2()
        CheckL2 --> CacheMissResult : not_in_l2()
        
        L2Hit : Deserialize value
        L2Hit : Promote to L1
        L2Hit --> CacheHitResult : return_promoted_value()
    }
    
    state SetOperation {
        [*] --> StoreL1
        StoreL1 : Check L1 capacity
        StoreL1 --> EvictLRU : cache_full()
        StoreL1 --> StoreDirectly : cache_has_space()
        
        EvictLRU : Remove oldest entry
        EvictLRU --> StoreDirectly : space_available()
        
        StoreDirectly : Store in L1
        StoreDirectly --> StoreL2 : l1_stored()
        
        StoreL2 : Serialize and store in Redis
        StoreL2 --> SetComplete : l2_stored()
        StoreL2 --> SetComplete : l2_failed()
    }
    
    state ClearOperation {
        [*] --> ClearL1
        ClearL1 : Clear memory cache
        ClearL1 --> ClearL2 : l1_cleared()
        
        ClearL2 : Clear Redis cache
        ClearL2 --> ClearComplete : l2_cleared()
        ClearL2 --> ClearComplete : l2_failed()
    }
    
    CacheHitResult --> OperationComplete
    CacheMissResult --> OperationComplete
    SetComplete --> OperationComplete
    ClearComplete --> OperationComplete
}

CacheOperation --> Ready : operation_finished()
CacheOperation --> ErrorRecovery : cache_error()

state ErrorRecovery {
    [*] --> DiagnoseError
    DiagnoseError : Classify error type
    DiagnoseError --> RedisError : redis_connection_lost()
    DiagnoseError --> MemoryError : memory_exhausted()
    DiagnoseError --> SerializationError : serialization_failed()
    
    RedisError : Disable L2 cache
    RedisError --> L1Only : fallback_to_l1()
    
    MemoryError : Trigger cache cleanup
    MemoryError --> Ready : memory_freed()
    
    SerializationError : Skip problematic entry
    SerializationError --> Ready : error_handled()
}

ErrorRecovery --> Ready : recovery_complete()

Ready --> MaintenanceMode : trigger_maintenance()

state MaintenanceMode {
    [*] --> StatsCollection
    StatsCollection : Collect cache statistics
    StatsCollection --> Optimization : stats_collected()
    
    Optimization : Optimize cache size
    Optimization : Clean expired entries
    Optimization --> Ready : maintenance_complete()
}

MaintenanceMode --> Ready : maintenance_finished()

Ready --> [*] : cache_shutdown()

note right of CacheOperation
  Cache operations with
  multi-tier fallback
end note

note right of ErrorRecovery
  Graceful error handling
  with service continuity
end note

@enduml
```

### Batch Processing FSM

```plantuml
@startuml BatchProcessingFSM
title Batch Processing - Finite State Machine

[*] --> Idle : system_ready()

Idle --> BatchReceived : receive_batch()

state BatchReceived {
    [*] --> ValidateBatch
    ValidateBatch : Check batch size
    ValidateBatch : Validate input format
    ValidateBatch --> BatchValid : validation_passed()
    ValidateBatch --> BatchInvalid : validation_failed()
    
    BatchInvalid --> Idle : return_error()
    
    BatchValid : Determine processing mode
    BatchValid --> ParallelMode : enable_parallel()
    BatchValid --> SequentialMode : use_sequential()
}

state ParallelMode {
    [*] --> ChunkCreation
    ChunkCreation : Calculate optimal chunk size
    ChunkCreation : Split texts into chunks
    ChunkCreation --> WorkerDispatch : chunks_created()
    
    state WorkerDispatch {
        [*] --> SubmitTasks
        SubmitTasks : Submit chunks to thread pool
        SubmitTasks --> AwaitCompletion : all_tasks_submitted()
        
        AwaitCompletion : Monitor worker progress
        AwaitCompletion --> ResultCollection : all_workers_finished()
        AwaitCompletion --> WorkerError : worker_failed()
        
        WorkerError : Handle failed chunks
        WorkerError --> ResultCollection : errors_processed()
    }
    
    ResultCollection : Combine chunk results
    ResultCollection : Maintain original order
    ResultCollection --> ProcessingComplete : results_combined()
}

state SequentialMode {
    [*] --> ItemProcessing
    ItemProcessing : Process next text
    ItemProcessing --> NextItem : item_completed()
    ItemProcessing --> ProcessingError : item_failed()
    
    NextItem --> ItemProcessing : more_items()
    NextItem --> ProcessingComplete : all_items_done()
    
    ProcessingError : Handle failed item
    ProcessingError --> NextItem : error_handled()
}

ParallelMode --> ProcessingComplete : parallel_finished()
SequentialMode --> ProcessingComplete : sequential_finished()

ProcessingComplete --> ResultDelivery : prepare_results()

state ResultDelivery {
    [*] --> FormatResults
    FormatResults : Create response format
    FormatResults : Calculate statistics
    FormatResults --> StoreResults : formatting_complete()
    
    StoreResults : Save to database
    StoreResults : Update metrics
    StoreResults --> ResponseReady : storage_complete()
    
    ResponseReady : Prepare final response
    ResponseReady --> Completed : response_prepared()
}

ResultDelivery --> Completed : delivery_finished()
BatchReceived --> Completed : processing_complete()

Completed --> Idle : ready_for_next()

note right of ParallelMode
  Parallel processing with
  optimal chunk sizing and
  worker thread management
end note

note right of SequentialMode
  Sequential fallback for
  small batches or when
  parallel processing unavailable
end note

@enduml
```

## UI/UX Design Principles

### Design Guidelines

1. **Clarity and Simplicity**
   - Clean, uncluttered interface
   - Clear visual hierarchy
   - Consistent navigation patterns

2. **Real-time Feedback**
   - Immediate compliance results
   - Live performance metrics
   - Progress indicators for batch processing

3. **Accessibility**
   - WCAG 2.1 AA compliance
   - Keyboard navigation support
   - Screen reader compatibility
   - High contrast mode

4. **Responsive Design**
   - Mobile-first approach
   - Adaptive layouts for different screen sizes
   - Touch-friendly interface elements

5. **Performance Optimization**
   - Progressive loading
   - Efficient data visualization
   - Minimal network requests

### Color Coding System

- **Green (#28a745)**: ALLOW actions, success states
- **Yellow (#ffc107)**: WARN actions, caution states
- **Red (#dc3545)**: BLOCK actions, error states
- **Blue (#007bff)**: Information, processing states
- **Gray (#6c757d)**: Neutral states, disabled elements

### Interactive Elements

- **Buttons**: Rounded corners with hover effects
- **Form Fields**: Clear labels with validation feedback
- **Charts**: Interactive with tooltips and zoom capabilities
- **Tables**: Sortable columns with search/filter options
- **Modals**: Overlay dialogs for detailed information

This comprehensive UI design provides an intuitive and efficient interface for managing the LLM Compliance Filter system, supporting both technical users and business stakeholders with appropriate levels of detail and control.
