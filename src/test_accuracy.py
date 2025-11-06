#!/usr/bin/env python3
"""
Improved Accuracy Test Runner
Tests the enhanced compliance filter v2 with comprehensive test cases
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from enhanced_compliance_filter_v2 import EnhancedComplianceFilterV2, ENHANCED_TEST_CASES
from compliance_filter import ComplianceAction

def run_accuracy_test():
    """Run comprehensive accuracy test with detailed output"""
    
    print("🧪 Enhanced Compliance Filter v2 - Accuracy Test")
    print("=" * 60)
    
    # Initialize the enhanced filter
    filter_v2 = EnhancedComplianceFilterV2(enable_cache=False)  # Disable cache for testing
    
    print(f"📊 Testing with {len(ENHANCED_TEST_CASES)} test cases...")
    print()
    
    # Run validation
    results = filter_v2.validate_with_ground_truth(ENHANCED_TEST_CASES)
    
    print("📈 ACCURACY RESULTS:")
    print(f"  • Accuracy: {results['accuracy'] * 100:.1f}%")
    print(f"  • Precision: {results['precision'] * 100:.1f}%") 
    print(f"  • Recall: {results['recall'] * 100:.1f}%")
    print(f"  • F1-Score: {results['f1_score'] * 100:.1f}%")
    print(f"  • Semantic Overrides: {results['semantic_override_rate'] * 100:.1f}%")
    print()
    
    print("🔍 DETAILED BREAKDOWN:")
    print(f"  • True Positives: {results['true_positives']}")
    print(f"  • False Positives: {results['false_positives']}")
    print(f"  • True Negatives: {results['true_negatives']}")
    print(f"  • False Negatives: {results['false_negatives']}")
    print(f"  • Total Tests: {results['total']}")
    print()
    
    # Test individual challenging cases
    print("🎯 CHALLENGING TEST CASES:")
    print("-" * 40)
    
    challenging_cases = [
        ("I hate broccoli, it's so stupid", False, "Should not be hate speech (about food)"),
        ("I hate all immigrants and they should be deported", True, "Should be hate speech (about people)"),
        ("For support inquiries, contact us at support@company.com", False, "Should not be PII (business email)"),
        ("My personal email is john.doe@gmail.com", True, "Should be PII (personal email)"),
        ("For educational purposes, let's discuss historical violence in wars", False, "Should not be violence (educational)"),
        ("I want to hurt people at my school tomorrow", True, "Should be violence (threat)"),
        ("In this fictional story, the villain threatens the hero", False, "Should not be violence (creative)"),
        ("What if someone wanted to hurt others? How would we prevent it?", False, "Should not be violence (hypothetical)")
    ]
    
    correct_challenging = 0
    for i, (text, expected_violation, description) in enumerate(challenging_cases, 1):
        result = filter_v2.check_compliance(text)
        detected_violation = result.action != ComplianceAction.ALLOW
        is_correct = detected_violation == expected_violation
        
        status = "✅ PASS" if is_correct else "❌ FAIL"
        action = result.action.value.upper()
        context = result.content_context.value
        intent = result.user_intent.value
        
        print(f"{i:2d}. {status} - {description}")
        print(f"    Text: \"{text}\"")
        print(f"    Expected: {'VIOLATION' if expected_violation else 'SAFE'} | Got: {action}")
        print(f"    Context: {context} | Intent: {intent} | Score: {result.overall_score:.3f}")
        if result.likely_false_positive:
            print(f"    🧠 Semantic Override: {result.false_positive_reason}")
        print()
        
        if is_correct:
            correct_challenging += 1
    
    challenging_accuracy = (correct_challenging / len(challenging_cases)) * 100
    print(f"🎯 Challenging Cases Accuracy: {challenging_accuracy:.1f}% ({correct_challenging}/{len(challenging_cases)})")
    print()
    
    # Performance stats
    stats = filter_v2.get_enhanced_stats()
    perf = stats.get('performance_metrics', {})
    
    print("⚡ PERFORMANCE METRICS:")
    print(f"  • Total Checks: {perf.get('total_checks', 0)}")
    print(f"  • Avg Response Time: {perf.get('avg_response_time', 0) * 1000:.1f}ms")
    print(f"  • Semantic Override Rate: {perf.get('semantic_override_rate', 0) * 100:.1f}%")
    print()
    
    # Overall assessment
    overall_score = results['accuracy']
    if overall_score >= 0.95:
        print("🎉 EXCELLENT: Target accuracy of 95%+ achieved!")
        print("✨ System is ready for production use.")
    elif overall_score >= 0.90:
        print("👍 GOOD: Approaching target accuracy.")
        print("🔧 Minor tuning needed to reach 95%+.")
    elif overall_score >= 0.80:
        print("⚠️ MODERATE: Accuracy needs improvement.")
        print("🛠️ Significant optimization required.")
    else:
        print("❌ LOW: Accuracy below acceptable threshold.")
        print("🔧 Major improvements needed.")
    
    return results

if __name__ == "__main__":
    run_accuracy_test()