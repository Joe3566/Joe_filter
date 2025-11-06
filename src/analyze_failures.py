#!/usr/bin/env python3
"""
Analyze false negatives to identify what needs fixing
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from enhanced_compliance_filter_v2 import EnhancedComplianceFilterV2, ENHANCED_TEST_CASES
from compliance_filter import ComplianceAction

def analyze_failures():
    """Analyze which test cases are failing and why"""
    
    print("🔍 Analyzing False Negatives")
    print("=" * 50)
    
    filter_v2 = EnhancedComplianceFilterV2(enable_cache=False)
    
    false_negatives = []
    false_positives = []
    
    print("📊 Running all test cases...")
    
    for i, test_case in enumerate(ENHANCED_TEST_CASES, 1):
        text = test_case['text']
        expected_violation = test_case['expected_violation']
        
        result = filter_v2.check_compliance(text)
        detected_violation = result.action != ComplianceAction.ALLOW
        
        if expected_violation and not detected_violation:
            false_negatives.append({
                'index': i,
                'text': text,
                'expected': 'VIOLATION',
                'got': result.action.value.upper(),
                'score': result.overall_score,
                'context': result.content_context.value,
                'intent': result.user_intent.value,
                'threat_level': result.threat_level.value,
                'violations': [v.value for v in result.violation_types],
                'reasoning': result.reasoning,
                'false_positive': result.likely_false_positive,
                'fp_reason': result.false_positive_reason
            })
        elif not expected_violation and detected_violation:
            false_positives.append({
                'index': i,
                'text': text,
                'expected': 'SAFE',
                'got': result.action.value.upper(),
                'score': result.overall_score,
                'context': result.content_context.value,
                'reasoning': result.reasoning
            })
    
    print(f"\n❌ FALSE NEGATIVES ({len(false_negatives)}):")
    print("=" * 40)
    
    for fn in false_negatives:
        print(f"\n{fn['index']:2d}. MISSED VIOLATION:")
        print(f"    Text: \"{fn['text']}\"")
        print(f"    Expected: {fn['expected']} | Got: {fn['got']}")
        print(f"    Score: {fn['score']:.3f} | Threat: {fn['threat_level']}")
        print(f"    Context: {fn['context']} | Intent: {fn['intent']}")
        print(f"    Violations: {fn['violations']}")
        print(f"    False Positive: {fn['false_positive']}")
        if fn['false_positive']:
            print(f"    FP Reason: {fn['fp_reason']}")
        print(f"    Reasoning: {fn['reasoning']}")
    
    print(f"\n✅ FALSE POSITIVES ({len(false_positives)}):")
    print("=" * 40)
    
    for fp in false_positives:
        print(f"\n{fp['index']:2d}. INCORRECT VIOLATION:")
        print(f"    Text: \"{fp['text']}\"")
        print(f"    Expected: {fp['expected']} | Got: {fp['got']}")
        print(f"    Score: {fp['score']:.3f}")
        print(f"    Context: {fp['context']}")
        print(f"    Reasoning: {fp['reasoning']}")
    
    # Summary analysis
    print(f"\n📋 SUMMARY:")
    print(f"False Negatives: {len(false_negatives)}")
    print(f"False Positives: {len(false_positives)}")
    print(f"Total Issues: {len(false_negatives) + len(false_positives)}")
    
    # Categorize false negative types
    if false_negatives:
        print(f"\n🔬 FALSE NEGATIVE PATTERNS:")
        violation_types = {}
        for fn in false_negatives:
            # Try to categorize what type of violation was missed
            text = fn['text'].lower()
            if 'ssn' in text or 'credit card' in text or 'phone' in text:
                violation_types['personal_info'] = violation_types.get('personal_info', 0) + 1
            elif any(word in text for word in ['kill', 'murder', 'bomb', 'explosive', 'hurt', 'harm', 'violence']):
                violation_types['violence'] = violation_types.get('violence', 0) + 1
            elif any(word in text for word in ['hate', 'stupid', 'inferior', 'terrorist']):
                violation_types['hate_speech'] = violation_types.get('hate_speech', 0) + 1
            elif 'ignore' in text or 'forget' in text or 'bypass' in text:
                violation_types['prompt_injection'] = violation_types.get('prompt_injection', 0) + 1
            else:
                violation_types['other'] = violation_types.get('other', 0) + 1
        
        for vtype, count in violation_types.items():
            print(f"  • {vtype}: {count} cases")
    
    return false_negatives, false_positives

if __name__ == "__main__":
    analyze_failures()