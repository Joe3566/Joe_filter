#!/usr/bin/env python3
"""
Debug action determination logic
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from enhanced_compliance_filter_v2 import EnhancedComplianceFilterV2
from advanced_detector import DetectionResult, ThreatLevel, ViolationType

def debug_action_logic():
    """Debug why high-confidence violations aren't being blocked"""
    
    print("🔍 Debug Action Determination")
    print("=" * 40)
    
    filter_v2 = EnhancedComplianceFilterV2(enable_cache=False)
    
    test_cases = [
        "I hate all immigrants and they should be deported",
        "I want to hurt people at my school tomorrow"
    ]
    
    for text in test_cases:
        print(f"\n📝 Testing: \"{text}\"")
        
        # Run full compliance check
        result = filter_v2.check_compliance(text)
        
        print(f"Final Action: {result.action.value}")
        print(f"Overall Score: {result.overall_score}")
        print(f"Threat Level: {result.threat_level.value}")
        print(f"Context: {result.content_context.value}")
        print(f"Intent: {result.user_intent.value}")
        print(f"False Positive: {result.likely_false_positive}")
        if result.likely_false_positive:
            print(f"FP Reason: {result.false_positive_reason}")
        
        # Check thresholds
        base_thresholds = filter_v2.base_thresholds
        context_thresholds = filter_v2._get_context_thresholds(result.content_context)
        
        print(f"\nThreshold Analysis:")
        print(f"Base thresholds: {base_thresholds}")
        print(f"Context thresholds: {context_thresholds}")
        print(f"Score vs Warn: {result.overall_score} >= {context_thresholds['warn']} = {result.overall_score >= context_thresholds['warn']}")
        print(f"Score vs Block: {result.overall_score} >= {context_thresholds['block']} = {result.overall_score >= context_thresholds['block']}")

if __name__ == "__main__":
    debug_action_logic()