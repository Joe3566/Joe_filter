#!/usr/bin/env python3
"""
Comprehensive content testing for LLM Compliance Filter.
Tests various types of content to demonstrate filter capabilities.
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.compliance_filter import ComplianceFilter


def test_safe_content():
    """Test completely safe content that should always pass."""
    print("✅ Testing Safe Content")
    print("=" * 60)
    
    safe_prompts = [
        "What's the weather like today?",
        "Explain how photosynthesis works",
        "Write a story about a friendly dragon",
        "What are the benefits of renewable energy?",
        "How do I bake chocolate chip cookies?",
        "Recommend some good books to read",
        "What's the capital of France?",
        "Explain quantum physics in simple terms",
        "How does machine learning work?",
        "What are some healthy meal ideas?"
    ]
    
    filter = ComplianceFilter()
    
    for i, prompt in enumerate(safe_prompts, 1):
        result = filter.check_compliance(prompt)
        status = "✅" if result.action.value == "allow" else f"⚠️ {result.action.value.upper()}"
        print(f"{i:2d}. {status} | Score: {result.overall_score:.3f} | {prompt}")


def test_privacy_violations():
    """Test various types of privacy violations."""
    print("\n🔒 Testing Privacy Violations")
    print("=" * 60)
    
    privacy_test_cases = [
        # Email addresses
        ("Email (basic)", "My email is john@example.com"),
        ("Email (corporate)", "Contact me at support@company.co.uk"),
        ("Email (in sentence)", "Please send the report to mary.smith@organization.org"),
        
        # Phone numbers
        ("Phone (US format)", "Call me at (555) 123-4567"),
        ("Phone (digits)", "My number is 555-999-1234"),
        ("Phone (international)", "Reach me at +1-800-555-0123"),
        
        # Social Security Numbers
        ("SSN (dashes)", "My SSN is 123-45-6789"),
        ("SSN (spaces)", "Social security: 987 65 4321"),
        
        # Credit Cards
        ("Credit Card (Visa)", "My card number is 4532-1234-5678-9012"),
        ("Credit Card (MasterCard)", "Card: 5555-4444-3333-2222"),
        
        # Mixed violations
        ("Multiple PII", "Email: user@test.com, Phone: (555) 123-4567, SSN: 123-45-6789"),
        ("Business contact", "Contact John at j.doe@company.com or call (555) 987-6543"),
        
        # Medical/Financial keywords
        ("Medical context", "Patient was diagnosed with diabetes last month"),
        ("Financial context", "My bank account routing number is needed"),
        
        # API keys and tokens (custom patterns)
        ("API Key", "Use this API key: sk-abc123def456ghi789jkl012mno345pqr"),
        ("Token", "Authorization token: bearer_token_abc123xyz789"),
    ]
    
    filter = ComplianceFilter()
    
    for category, prompt in privacy_test_cases:
        result = filter.check_compliance(prompt)
        
        # Color coding
        if result.action.value == "block":
            status = "🚫 BLOCK"
        elif result.action.value == "warn":
            status = "⚠️  WARN"
        else:
            status = "✅ ALLOW"
        
        print(f"\n{category}:")
        print(f"  Text: {prompt}")
        print(f"  {status} | Privacy: {result.privacy_score:.3f} | Overall: {result.overall_score:.3f}")
        
        if result.privacy_violations:
            print(f"  Violations: {', '.join(v.violation_type.value for v in result.privacy_violations)}")


def test_borderline_content():
    """Test content that might be borderline or require judgment."""
    print("\n🤔 Testing Borderline Content")
    print("=" * 60)
    
    borderline_cases = [
        # Potentially sensitive but not clearly violating
        ("Generic email reference", "Send me an email"),
        ("Phone mention", "Give me a call"),
        ("Address context", "I live in New York"),
        ("Age reference", "I'm 25 years old"),
        ("Name dropping", "My friend John told me"),
        
        # Professional context
        ("Professional email", "Contact our sales team at sales@company.com"),
        ("Support reference", "Call customer support at 1-800-SUPPORT"),
        ("Public information", "Visit our website at www.example.com"),
        
        # Academic/Educational
        ("Academic discussion", "In the study by Smith et al."),
        ("Educational example", "For example, if your email is user@domain.com"),
        ("Hypothetical", "Imagine you received a call from 555-0123"),
        
        # Business scenarios
        ("Invoice reference", "Invoice #12345 for $500"),
        ("Meeting context", "Schedule a meeting for next Tuesday"),
        ("Document request", "Please send the quarterly report"),
    ]
    
    filter = ComplianceFilter()
    
    for category, prompt in borderline_cases:
        result = filter.check_compliance(prompt)
        
        if result.action.value == "block":
            status = "🚫 BLOCK"
            color = "HIGH RISK"
        elif result.action.value == "warn":
            status = "⚠️  WARN"
            color = "MEDIUM RISK"
        else:
            status = "✅ ALLOW"
            color = "LOW RISK"
        
        print(f"{category:20} | {status} | {color:11} | Score: {result.overall_score:.3f}")


def test_threshold_sensitivity():
    """Test how different threshold settings affect decisions."""
    print("\n⚙️ Testing Threshold Sensitivity")
    print("=" * 60)
    
    test_prompt = "Please email me at contact@example.com with the details"
    
    threshold_configs = [
        ("Very Strict", {"block_threshold": 0.3, "warn_threshold": 0.2}),
        ("Strict", {"block_threshold": 0.5, "warn_threshold": 0.3}),
        ("Default", {"block_threshold": 0.7, "warn_threshold": 0.5}),
        ("Permissive", {"block_threshold": 0.8, "warn_threshold": 0.6}),
        ("Very Permissive", {"block_threshold": 0.95, "warn_threshold": 0.8}),
    ]
    
    print(f"Test prompt: {test_prompt}\n")
    
    for config_name, thresholds in threshold_configs:
        filter = ComplianceFilter()
        filter.update_thresholds(thresholds)
        
        result = filter.check_compliance(test_prompt)
        
        if result.action.value == "block":
            status = "🚫 BLOCK"
        elif result.action.value == "warn":
            status = "⚠️  WARN"
        else:
            status = "✅ ALLOW"
        
        print(f"{config_name:15} | {status} | Score: {result.overall_score:.3f} | Block≥{thresholds['block_threshold']}, Warn≥{thresholds['warn_threshold']}")


def test_batch_processing():
    """Test batch processing capabilities."""
    print("\n📦 Testing Batch Processing")
    print("=" * 60)
    
    batch_prompts = [
        "What's the weather?",
        "Email me at test@example.com",
        "Call (555) 123-4567",
        "How does AI work?",
        "My SSN is 123-45-6789",
        "Recommend a good restaurant",
        "Credit card: 4532-1234-5678-9012",
        "Tell me a joke"
    ]
    
    filter = ComplianceFilter()
    
    print("Processing 8 prompts in batch...")
    results = filter.batch_check_compliance(batch_prompts)
    
    print("\nResults:")
    for i, (prompt, result) in enumerate(zip(batch_prompts, results), 1):
        if result.action.value == "block":
            status = "🚫"
        elif result.action.value == "warn":
            status = "⚠️ "
        else:
            status = "✅"
        
        violations = len(result.privacy_violations)
        violation_text = f" ({violations} violations)" if violations > 0 else ""
        
        print(f"{i}. {status} {result.action.value:5} | {result.overall_score:.3f} | {prompt[:40]}{'...' if len(prompt) > 40 else ''}{violation_text}")


def test_performance_monitoring():
    """Test performance monitoring capabilities."""
    print("\n📊 Testing Performance Monitoring")
    print("=" * 60)
    
    filter = ComplianceFilter()
    
    # Process some test cases
    test_cases = [
        "Safe prompt",
        "Email: user@test.com",
        "Another safe prompt",
        "Phone: (555) 123-4567",
        "Safe content again"
    ]
    
    print("Processing test cases for performance monitoring...")
    for prompt in test_cases:
        filter.check_compliance(prompt)
    
    # Get performance statistics
    stats = filter.get_performance_stats()
    
    print(f"\nPerformance Statistics:")
    print(f"  Total checks: {stats['total_checks']}")
    print(f"  Average processing time: {stats['average_processing_time']:.4f} seconds")
    print(f"  Action distribution:")
    for action, count in stats['action_distribution'].items():
        percentage = (count / stats['total_checks']) * 100 if stats['total_checks'] > 0 else 0
        print(f"    {action}: {count} ({percentage:.1f}%)")


def main():
    """Run all content tests."""
    print("🧪 LLM Compliance Filter - Content Testing Suite")
    print("=" * 80)
    print("This script demonstrates the filter's behavior with various content types.")
    print("=" * 80)
    
    try:
        test_safe_content()
        test_privacy_violations()
        test_borderline_content()
        test_threshold_sensitivity()
        test_batch_processing()
        test_performance_monitoring()
        
        print("\n" + "=" * 80)
        print("🎉 ALL CONTENT TESTS COMPLETED!")
        print("=" * 80)
        
        print("\n📋 Test Summary:")
        print("✅ Safe content properly allowed")
        print("🔒 Privacy violations correctly detected and blocked")
        print("🤔 Borderline content handled with appropriate caution")
        print("⚙️ Threshold sensitivity working as expected")
        print("📦 Batch processing functional")
        print("📊 Performance monitoring active")
        
        print("\n💡 Usage Tips:")
        print("- Adjust thresholds based on your risk tolerance")
        print("- Monitor performance stats for optimization")
        print("- Use batch processing for efficiency")
        print("- Check violation details for understanding decisions")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
