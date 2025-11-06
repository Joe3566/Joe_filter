#!/usr/bin/env python3
"""
Test AdvancedDetector directly
"""

import sys
import os
import asyncio
sys.path.insert(0, os.path.dirname(__file__))

from advanced_detector import AdvancedDetector

async def test_detector():
    """Test AdvancedDetector directly"""
    
    print("🔍 Testing AdvancedDetector Directly")
    print("=" * 40)
    
    detector = AdvancedDetector()
    
    test_cases = [
        "I hate all immigrants and they should be deported",
        "I want to hurt people at my school tomorrow"
    ]
    
    for text in test_cases:
        print(f"\n📝 Testing: \"{text}\"")
        
        result = await detector.detect(text)
        
        print(f"Is Violation: {result.is_violation}")
        print(f"Confidence: {result.confidence_score}")
        print(f"Threat Level: {result.threat_level.value}")
        print(f"Violations: {[v.value for v in result.violation_types]}")
        print(f"Reasoning: {result.reasoning}")

if __name__ == "__main__":
    asyncio.run(test_detector())