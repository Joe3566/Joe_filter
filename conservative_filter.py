#!/usr/bin/env python3
"""
🛡️ ULTRA-CONSERVATIVE COMPLIANCE FILTER
Only flags clear, unambiguous violations to minimize false positives.
"""

import re
import time
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class ConservativeResult:
    is_violation: bool
    confidence: float
    violation_type: str
    severity: str
    reasoning: List[str]
    processing_time_ms: float

class UltraConservativeFilter:
    """Ultra-conservative filter that only flags obvious violations"""
    
    def __init__(self):
        # Only the most explicit, unambiguous violations
        self.explicit_threats = [
            # Direct personal threats with clear intent
            r'\bi\s+will\s+kill\s+you\b',
            r'\bi\s+am\s+going\s+to\s+kill\s+you\b',
            r'\bi\s+will\s+murder\s+you\b',
            r'\bi\s+will\s+hurt\s+you\b',
            r'\byou\s+are\s+going\s+to\s+die\b',
            r'\bi\s+will\s+come\s+(?:for|after)\s+you\b'
        ]
        
        # Mass violence threats - very specific
        self.mass_violence = [
            r'\bshoot\s+up\s+(?:the\s+)?school\b',
            r'\bbomb\s+the\s+(?:school|building|mall)\b',
            r'\bmass\s+shooting\s+at\b',
            r'\bterrorist\s+attack\s+on\b',
            r'\bplanning\s+to\s+(?:bomb|shoot|attack)\b'
        ]
        
        # Clear hate speech with explicit calls for violence/elimination
        self.explicit_hate = [
            r'\b(?:kill|murder|eliminate)\s+all\s+(?:immigrants|muslims|jews|blacks|gays|women)\b',
            r'\ball\s+(?:immigrants|muslims|jews|blacks|gays|women)\s+(?:should|must|need\s+to)\s+(?:die|be\s+killed|be\s+eliminated)\b',
            r'\b(?:immigrants|muslims|jews|blacks|gays|women)\s+(?:should|must|need\s+to)\s+be\s+(?:eliminated|exterminated|wiped\s+out)\b'
        ]
        
        # Personal identifying information - very specific patterns
        self.pii_patterns = [
            r'\bssn:?\s*\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',
            r'\bsocial\s+security\s+number:?\s*\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',
            r'\bcredit\s+card:?\s*\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            r'\b\d{4}[-\s]\d{4}[-\s]\d{4}[-\s]\d{4}\b'  # Credit card format
        ]
        
        # Suicide/self-harm - only explicit statements
        self.self_harm = [
            r'\bi\s+want\s+to\s+kill\s+myself\b',
            r'\bi\s+am\s+going\s+to\s+kill\s+myself\b',
            r'\bcommit\s+suicide\s+(?:tonight|today|tomorrow)\b',
            r'\bsuicide\s+is\s+(?:my\s+only\s+option|the\s+only\s+way)\b'
        ]
        
        # Safe context indicators that override violations
        self.safe_contexts = [
            r'\b(?:academic|research|study|analysis|paper|article|news|report|documentary|book|movie|game|novel|story|fiction)\b',
            r'\b(?:history|historical|educational|learning|school|university|class)\b',
            r'\b(?:journalism|investigation|court|legal|law|policy)\b',
            r'\b(?:writing|creating|developing|designing)\b'
        ]
        
        # Hyperbolic/figurative expressions that should NOT be flagged
        self.figurative_expressions = [
            r'\bcould\s+kill\s+for\s+(?:a|some)\b',
            r'\bdying\s+to\s+(?:see|try|get|have)\b',
            r'\bto\s+die\s+for\b',
            r'\b(?:killing|murder(?:ing)?)\s+(?:my|our|the)\s+(?:mood|vibe|energy|productivity)\b',
            r'\bthis\s+(?:weather|traffic|assignment|project)\s+is\s+(?:killing|murdering)\s+me\b'
        ]
    
    def has_safe_context(self, text: str) -> bool:
        """Check if text has indicators of safe/academic context"""
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in self.safe_contexts)
    
    def is_figurative_expression(self, text: str) -> bool:
        """Check if text contains figurative/hyperbolic expressions"""
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in self.figurative_expressions)
    
    def analyze(self, text: str) -> ConservativeResult:
        """Analyze text with ultra-conservative approach"""
        start_time = time.time()
        
        text_lower = text.lower().strip()
        
        # Quick exit for empty or very short text
        if len(text_lower) < 5:
            return ConservativeResult(
                is_violation=False,
                confidence=0.0,
                violation_type="safe",
                severity="none",
                reasoning=["Text too short to analyze"],
                processing_time_ms=(time.time() - start_time) * 1000
            )
        
        # Check for safe context first - if present, be much more conservative
        has_safe_context = self.has_safe_context(text)
        is_figurative = self.is_figurative_expression(text)
        
        # If it's clearly figurative/hyperbolic, don't flag it
        if is_figurative:
            return ConservativeResult(
                is_violation=False,
                confidence=0.0,
                violation_type="safe",
                severity="none",
                reasoning=["Detected figurative/hyperbolic expression"],
                processing_time_ms=(time.time() - start_time) * 1000
            )
        
        violation_found = False
        violation_type = "safe"
        severity = "none"
        reasoning = []
        confidence = 0.0
        
        # Check for explicit personal threats
        for pattern in self.explicit_threats:
            if re.search(pattern, text_lower):
                if not has_safe_context:  # Only flag if no safe context
                    violation_found = True
                    violation_type = "direct_threat"
                    severity = "high"
                    confidence = 0.9
                    reasoning.append("Direct personal threat detected")
                    break
        
        # Check for mass violence threats
        if not violation_found:
            for pattern in self.mass_violence:
                if re.search(pattern, text_lower):
                    if not has_safe_context:
                        violation_found = True
                        violation_type = "mass_violence"
                        severity = "high"
                        confidence = 0.95
                        reasoning.append("Mass violence threat detected")
                        break
        
        # Check for explicit hate speech with violence
        if not violation_found:
            for pattern in self.explicit_hate:
                if re.search(pattern, text_lower):
                    if not has_safe_context:
                        violation_found = True
                        violation_type = "hate_speech"
                        severity = "high"
                        confidence = 0.9
                        reasoning.append("Explicit hate speech with violence detected")
                        break
        
        # Check for personal information (always flag regardless of context)
        if not violation_found:
            for pattern in self.pii_patterns:
                if re.search(pattern, text):
                    violation_found = True
                    violation_type = "privacy_violation"
                    severity = "medium"
                    confidence = 0.95
                    reasoning.append("Personal identifying information detected")
                    break
        
        # Check for explicit self-harm
        if not violation_found:
            for pattern in self.self_harm:
                if re.search(pattern, text_lower):
                    violation_found = True
                    violation_type = "self_harm"
                    severity = "high"
                    confidence = 0.85
                    reasoning.append("Explicit self-harm statement detected")
                    break
        
        # If we found a violation but there's safe context, reduce confidence significantly
        if violation_found and has_safe_context:
            confidence *= 0.3  # Reduce confidence by 70%
            reasoning.append("Safe context detected - reduced confidence")
            if confidence < 0.5:  # If confidence drops too low, don't flag it
                violation_found = False
                violation_type = "safe"
                severity = "none"
                reasoning = ["Safe context overrides potential violation"]
        
        processing_time = (time.time() - start_time) * 1000
        
        return ConservativeResult(
            is_violation=violation_found,
            confidence=confidence,
            violation_type=violation_type,
            severity=severity,
            reasoning=reasoning,
            processing_time_ms=processing_time
        )

def test_conservative_filter():
    """Test the conservative filter with various cases"""
    print("🛡️ ULTRA-CONSERVATIVE COMPLIANCE FILTER TEST")
    print("=" * 60)
    
    filter_system = UltraConservativeFilter()
    
    test_cases = [
        # Should be SAFE (common false positives from other systems)
        ("I hate broccoli with all my heart", "Should be SAFE"),
        ("This movie killed my expectations", "Should be SAFE"),
        ("I'm dying to see the new Marvel movie", "Should be SAFE"),
        ("This traffic is murder on my commute", "Should be SAFE"),
        ("I could kill for a good pizza right now", "Should be SAFE"),
        ("Academic research on hate speech detection", "Should be SAFE"),
        ("News report: terrorist attack in foreign country", "Should be SAFE"),
        ("Historical analysis of genocide events", "Should be SAFE"),
        ("Writing a crime novel about serial killers", "Should be SAFE"),
        ("I hate Mondays, they're the worst", "Should be SAFE"),
        ("That workout killed me but it was worth it", "Should be SAFE"),
        ("The suspense in this book is murder", "Should be SAFE"),
        
        # Should be VIOLATIONS (only clear, unambiguous threats)
        ("I will kill you tomorrow", "Should be VIOLATION"),
        ("I am going to murder you", "Should be VIOLATION"),
        ("Planning to bomb the school next week", "Should be VIOLATION"),
        ("Kill all immigrants they should die", "Should be VIOLATION"),
        ("SSN: 123-45-6789", "Should be VIOLATION"),
        ("Credit card: 4532-1234-5678-9012", "Should be VIOLATION"),
        ("I want to kill myself tonight", "Should be VIOLATION"),
        
        # Edge cases with context
        ("Academic study: 'I will kill you' was the threat received", "Should be SAFE - academic context"),
        ("News report: Terrorist planning to bomb the building", "Should be SAFE - news context"),
        ("In my novel, the character says 'kill all immigrants'", "Should be SAFE - creative context")
    ]
    
    print(f"\n🧪 Testing {len(test_cases)} cases:")
    print("-" * 80)
    
    correct_predictions = 0
    for i, (text, expected) in enumerate(test_cases, 1):
        result = filter_system.analyze(text)
        
        status = "🚫 VIOLATION" if result.is_violation else "✅ SAFE"
        confidence = f"{result.confidence:.3f}"
        
        # Simple accuracy check based on expected result
        expected_violation = "VIOLATION" in expected
        is_correct = (result.is_violation and expected_violation) or (not result.is_violation and not expected_violation)
        if is_correct:
            correct_predictions += 1
        
        accuracy_icon = "✓" if is_correct else "✗"
        
        print(f"\n{i:2d}. {status} [{accuracy_icon}] Confidence: {confidence}")
        print(f"    Text: '{text[:60]}{'...' if len(text) > 60 else ''}'")
        print(f"    Expected: {expected}")
        
        if result.reasoning:
            print(f"    Reasoning: {'; '.join(result.reasoning)}")
    
    accuracy = (correct_predictions / len(test_cases)) * 100
    print(f"\n🎯 ACCURACY: {correct_predictions}/{len(test_cases)} = {accuracy:.1f}%")
    print("🛡️ Ultra-conservative filter focuses on minimizing false positives!")
    
    return filter_system

if __name__ == "__main__":
    test_conservative_filter()