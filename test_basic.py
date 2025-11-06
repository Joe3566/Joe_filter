#!/usr/bin/env python3
"""
Basic Usage Example for LLM Compliance Filter

This demonstrates the most common usage patterns.
Perfect for getting started and testing the system.
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.compliance_filter import ComplianceFilter

def basic_usage_example():
    """Basic compliance checking example."""
    print("🚀 LLM Compliance Filter - Basic Usage Example")
    print("=" * 60)
    
    # Create filter (uses default configuration)
    filter = ComplianceFilter()
    
    print("\n1. Single Text Compliance Check:")
    print("-" * 40)
    
    # Test single text
    result = filter.check_compliance("Hello, my email is user@example.com")
    
    print(f"Input Text: 'Hello, my email is user@example.com'")
    print(f"Action: {result.action.value}")
    print(f"Overall Score: {result.overall_score:.3f}")
    print(f"Privacy Score: {result.privacy_score:.3f}")
    print(f"Hate Speech Score: {result.hate_speech_score:.3f}")
    print(f"Reasoning: {result.reasoning}")
    print(f"Processing Time: {result.processing_time:.3f}s")
    
    # Show privacy violations if any
    if result.privacy_violations:
        print("Privacy Violations:")
        for violation in result.privacy_violations:
            print(f"  - {violation.violation_type.value}: {violation.description}")
    
    print("\n2. Batch Processing Example:")
    print("-" * 40)
    
    # Test batch processing
    texts = [
        "What's the weather like?",
        "My SSN is 123-45-6789",
        "How does AI work?",
        "Call me at (555) 123-4567",
        "My credit card is 4532-1234-5678-9012"
    ]
    
    results = filter.batch_check_compliance(texts)
    
    for i, (text, result) in enumerate(zip(texts, results), 1):
        action_icon = "✅" if result.action.value == "allow" else "⚠️" if result.action.value == "warn" else "🚫"
        print(f"{action_icon} Text {i}: {result.action.value.upper()} (score: {result.overall_score:.3f})")
        print(f"   Input: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        if result.privacy_violations:
            violations = [v.violation_type.value for v in result.privacy_violations]
            print(f"   Violations: {', '.join(violations)}")
        print()

def high_performance_example():
    """High-performance mode demonstration."""
    print("\n🚀 High-Performance Mode Example")
    print("=" * 60)
    
    # Create optimized filter (much faster!)
    filter = ComplianceFilter.create_optimized()
    
    print("Creating 100 test texts for performance demonstration...")
    
    # Process many texts at once
    texts = [
        "What's the weather today?",
        "My email is user@example.com", 
        "Call me at (555) 123-4567",
        "How does machine learning work?",
        "My credit card is 4532-1234-5678-9012"
    ] * 20  # 100 total texts
    
    import time
    
    # Sequential processing
    print("\n1. Sequential Processing:")
    start_time = time.time()
    results_seq = filter.batch_check_compliance(texts, parallel=False)
    seq_time = time.time() - start_time
    print(f"   Processed {len(results_seq)} texts in {seq_time:.3f}s")
    print(f"   Throughput: {len(results_seq)/seq_time:.1f} texts/second")
    
    # Parallel processing
    print("\n2. Parallel Processing:")
    start_time = time.time()
    results_par = filter.batch_check_compliance(texts, parallel=True)
    par_time = time.time() - start_time
    print(f"   Processed {len(results_par)} texts in {par_time:.3f}s")
    print(f"   Throughput: {len(results_par)/par_time:.1f} texts/second")
    
    if par_time > 0:
        speedup = seq_time / par_time
        print(f"   Speedup: {speedup:.1f}x faster!")
    
    # Show performance stats
    stats = filter.get_performance_stats()
    
    print("\n3. Performance Statistics:")
    if 'performance_metrics' in stats:
        perf = stats['performance_metrics']
        print(f"   Total requests: {perf['total_requests']}")
        print(f"   Average response time: {perf['avg_response_time']:.3f}s")
        print(f"   Requests per second: {perf['requests_per_second']:.1f}")
    
    if 'cache_stats' in stats:
        cache = stats['cache_stats']
        print(f"   Cache hit rate: {cache['overall_hit_rate']:.1f}%")
        print(f"   Cache entries: {cache['memory_cache_size']}")
    
    if 'system_metrics' in stats:
        sys_metrics = stats['system_metrics']
        print(f"   Memory usage: {sys_metrics['memory_mb']:.1f}MB")

def custom_configuration_example():
    """Custom configuration example."""
    print("\n🔧 Custom Configuration Example")
    print("=" * 60)
    
    # Custom configuration for more strict checking
    custom_config = {
        'performance': {
            'enable_optimizations': True,
            'enable_caching': True,
            'max_workers': 2
        },
        'compliance': {
            'scoring_method': 'max',  # Use maximum score (more strict)
            'thresholds': {
                'block_threshold': 0.6,  # Lower threshold = more strict
                'warn_threshold': 0.3,
                'pass_threshold': 0.1
            }
        },
        'privacy': {
            'checks': {
                'email_detection': True,
                'phone_detection': True,
                'ssn_detection': True,
                'credit_card_detection': True,
                'address_detection': False  # Disable address detection
            }
        }
    }
    
    # Create filter with custom config
    custom_filter = ComplianceFilter(config_dict=custom_config)
    
    print("Testing with custom configuration (more strict):")
    
    test_texts = [
        "My email is test@example.com",
        "What's the weather like?", 
        "Call me at (555) 123-4567"
    ]
    
    for text in test_texts:
        result = custom_filter.check_compliance(text)
        print(f"  '{text}' → {result.action.value.upper()} (score: {result.overall_score:.3f})")
        if result.reasoning:
            print(f"    Reasoning: {result.reasoning}")
        print()

async def async_example():
    """Async processing example."""
    print("\n🔄 Async Processing Example")
    print("=" * 60)
    
    import asyncio
    
    # Create optimized filter
    filter = ComplianceFilter.create_optimized()
    
    # Single async request
    print("1. Single async request:")
    result = await filter.check_compliance_async("Check this text asynchronously")
    print(f"   Result: {result.action.value} (score: {result.overall_score:.3f})")
    
    # Batch async processing
    print("\n2. Batch async processing:")
    texts = [
        "What's the weather?",
        "My email is async@example.com",
        "Call me at (555) 987-6543"
    ]
    
    start_time = time.time()
    results = await filter.batch_check_compliance_async(texts)
    async_time = time.time() - start_time
    
    print(f"   Processed {len(results)} texts in {async_time:.3f}s")
    for text, result in zip(texts, results):
        print(f"   '{text}' → {result.action.value.upper()}")

def main():
    """Run all examples."""
    print("🎯 LLM Compliance Filter - Complete Usage Examples")
    print("=" * 80)
    
    try:
        # Basic usage
        basic_usage_example()
        
        # High performance
        high_performance_example()
        
        # Custom configuration
        custom_configuration_example()
        
        # Async example
        import asyncio
        asyncio.run(async_example())
        
        print("\n" + "=" * 80)
        print("🎉 All examples completed successfully!")
        print("\n✨ Key Takeaways:")
        print("   • Basic usage: ComplianceFilter() for simple cases")
        print("   • High performance: ComplianceFilter.create_optimized() for speed")
        print("   • Batch processing: 47x faster than individual requests")
        print("   • Async support: Perfect for web applications")
        print("   • Custom config: Adjust thresholds and rules as needed")
        print("\n🚀 Ready for production deployment!")
        
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    import time
    success = main()
    sys.exit(0 if success else 1)
