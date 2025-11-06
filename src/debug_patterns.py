#!/usr/bin/env python3
"""
Debug pattern matching for specific test cases
"""

import sys
import os
import re
sys.path.insert(0, os.path.dirname(__file__))

from enhanced_compliance_filter_v2 import EnhancedComplianceFilterV2
from semantic_analyzer import SemanticAnalyzer

def debug_pattern_matching():
    """Debug why patterns aren't matching"""
    
    print("🔍 Debug Pattern Matching")
    print("=" * 40)
    
    analyzer = SemanticAnalyzer()
    filter_v2 = EnhancedComplianceFilterV2(enable_cache=False)
    
    test_cases = [
        "I hate all immigrants and they should be deported",
        "I want to hurt people at my school tomorrow"
    ]
    
    for text in test_cases:
        print(f"\n📝 Testing: \"{text}\"")
        
        # Test semantic analysis
        semantic_analysis = analyzer.analyze(text)
        print(f"Context: {semantic_analysis.context.value}")
        print(f"Intent: {semantic_analysis.intent.value}")
        
        # Test pattern matching directly
        violations, confidence = filter_v2._basic_pattern_detection(text, semantic_analysis)
        print(f"Violations found: {[v.value for v in violations]}")
        print(f"Confidence: {confidence}")
        
        # Test individual patterns
        text_lower = text.lower()
        
        # Hate speech patterns
        hate_patterns = [
            (r'\bhate\s+all\s+(?:people|immigrants|foreigners|muslims)', 0.9),
            (r'\bhate.*immigrants.*should.*deported', 0.95)
        ]
        
        print("Hate speech pattern tests:")
        for pattern, score in hate_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            print(f"  Pattern: {pattern}")
            print(f"  Match: {match is not None}")
            if match:
                print(f"  Matched text: '{match.group()}'")
        
        # Violence patterns
        violence_patterns = [
            (r'\b(?:want\s+to\s+)?hurt\s+people\s+at\s+(?:my\s+)?(?:school|work)', 0.95),
            (r'\bwant\s+to\s+hurt\s+people\s+at\s+.*school', 0.95),
            (r'\bhurt\s+people.*school.*tomorrow', 0.95)
        ]
        
        print("Violence pattern tests:")
        for pattern, score in violence_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            print(f"  Pattern: {pattern}")
            print(f"  Match: {match is not None}")
            if match:
                print(f"  Matched text: '{match.group()}'")

if __name__ == "__main__":
    debug_pattern_matching()