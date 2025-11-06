#!/usr/bin/env python3
"""
OpenAI Moderation API Integration
Uses ChatGPT's moderation models for highly accurate content filtering
"""

import os
import logging
from typing import Dict, Any, Optional
import time

logger = logging.getLogger(__name__)

# Try to import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not installed. Run: pip install openai")


class OpenAIModerationFilter:
    """
    Integrates OpenAI's Moderation API for highly accurate content filtering
    Categories detected:
    - hate, hate/threatening
    - harassment, harassment/threatening  
    - self-harm, self-harm/intent, self-harm/instructions
    - sexual, sexual/minors
    - violence, violence/graphic
    """
    
    def __init__(self, api_key: Optional[str] = None):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            logger.warning("⚠️ No OpenAI API key found. Set OPENAI_API_KEY environment variable.")
            self.enabled = False
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=self.api_key)
                self.enabled = True
                logger.info("✅ OpenAI Moderation API initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI client: {e}")
                self.enabled = False
                self.client = None
        
        # Performance tracking
        self.total_requests = 0
        self.total_time = 0.0
        self.flagged_count = 0
        
    def moderate(self, text: str) -> Dict[str, Any]:
        """
        Use OpenAI's moderation API to analyze content
        Returns detailed moderation results
        """
        if not self.enabled or not self.client:
            return {
                'enabled': False,
                'flagged': False,
                'categories': {},
                'category_scores': {},
                'error': 'OpenAI Moderation not enabled'
            }
        
        try:
            start_time = time.time()
            
            # Call OpenAI Moderation API
            response = self.client.moderations.create(input=text)
            
            elapsed = time.time() - start_time
            self.total_requests += 1
            self.total_time += elapsed
            
            # Extract results
            result = response.results[0]
            
            if result.flagged:
                self.flagged_count += 1
            
            # Build detailed response
            moderation_result = {
                'enabled': True,
                'flagged': result.flagged,
                'categories': {
                    'hate': result.categories.hate,
                    'hate_threatening': result.categories.hate_threatening,
                    'harassment': result.categories.harassment,
                    'harassment_threatening': result.categories.harassment_threatening,
                    'self_harm': result.categories.self_harm,
                    'self_harm_intent': result.categories.self_harm_intent,
                    'self_harm_instructions': result.categories.self_harm_instructions,
                    'sexual': result.categories.sexual,
                    'sexual_minors': result.categories.sexual_minors,
                    'violence': result.categories.violence,
                    'violence_graphic': result.categories.violence_graphic,
                },
                'category_scores': {
                    'hate': result.category_scores.hate,
                    'hate_threatening': result.category_scores.hate_threatening,
                    'harassment': result.category_scores.harassment,
                    'harassment_threatening': result.category_scores.harassment_threatening,
                    'self_harm': result.category_scores.self_harm,
                    'self_harm_intent': result.category_scores.self_harm_intent,
                    'self_harm_instructions': result.category_scores.self_harm_instructions,
                    'sexual': result.category_scores.sexual,
                    'sexual_minors': result.category_scores.sexual_minors,
                    'violence': result.category_scores.violence,
                    'violence_graphic': result.category_scores.violence_graphic,
                },
                'processing_time_ms': elapsed * 1000,
                'model': getattr(result, 'model', 'text-moderation-latest')
            }
            
            # Add flagged categories list
            moderation_result['flagged_categories'] = [
                category for category, flagged in moderation_result['categories'].items()
                if flagged
            ]
            
            # Get highest risk category
            if moderation_result['category_scores']:
                max_category = max(
                    moderation_result['category_scores'].items(),
                    key=lambda x: x[1]
                )
                moderation_result['highest_risk_category'] = max_category[0]
                moderation_result['highest_risk_score'] = max_category[1]
            
            return moderation_result
            
        except Exception as e:
            logger.error(f"OpenAI Moderation API error: {e}")
            return {
                'enabled': True,
                'flagged': False,
                'categories': {},
                'category_scores': {},
                'error': str(e),
                'processing_time_ms': 0
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        avg_time = (self.total_time / self.total_requests * 1000) if self.total_requests > 0 else 0
        flagged_rate = (self.flagged_count / self.total_requests) if self.total_requests > 0 else 0
        
        return {
            'enabled': self.enabled,
            'total_requests': self.total_requests,
            'flagged_count': self.flagged_count,
            'flagged_rate': flagged_rate,
            'avg_time_ms': avg_time,
            'total_time_seconds': self.total_time,
        }


class HybridModerationFilter:
    """
    Combines OpenAI Moderation with local detection for best accuracy
    Falls back to local detection if OpenAI is unavailable
    """
    
    def __init__(self, local_detector, api_key: Optional[str] = None):
        self.local_detector = local_detector
        
        # Initialize OpenAI moderation (may fail if no API key)
        try:
            self.openai_filter = OpenAIModerationFilter(api_key)
        except Exception as e:
            logger.warning(f"OpenAI filter initialization failed: {e}")
            self.openai_filter = None
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Hybrid analysis using both OpenAI and local detection
        """
        result = {
            'text': text[:100] + '...' if len(text) > 100 else text,
            'is_compliant': True,
            'confidence': 0.0,
            'sources': [],
            'violations': [],
            'openai_moderation': None,
            'local_detection': None,
        }
        
        # 1. OpenAI Moderation (Primary - Most Accurate)
        if self.openai_filter and self.openai_filter.enabled:
            openai_result = self.openai_filter.moderate(text)
            result['openai_moderation'] = openai_result
            
            if openai_result['flagged']:
                result['is_compliant'] = False
                result['sources'].append('openai_moderation')
                result['violations'].extend(openai_result['flagged_categories'])
                result['confidence'] = max(
                    result['confidence'],
                    openai_result.get('highest_risk_score', 0.9)
                )
        
        # 2. Local Detection (Secondary - Backup & Additional Checks)
        if self.local_detector:
            local_result = self.local_detector.analyze_enhanced(text)
            result['local_detection'] = {
                'is_jailbreak': local_result.is_jailbreak,
                'severity': local_result.severity.value,
                'confidence': local_result.confidence,
                'techniques': [t.value for t in local_result.techniques],
                'patterns': local_result.patterns_detected[:5],
            }
            
            if local_result.is_jailbreak:
                if not result['is_compliant']:
                    # Already flagged by OpenAI, just add local info
                    result['sources'].append('local_detection')
                else:
                    # Only local detected it (jailbreak-specific)
                    result['is_compliant'] = False
                    result['sources'].append('local_detection')
                
                result['confidence'] = max(result['confidence'], local_result.confidence)
                result['violations'].extend([t.value for t in local_result.techniques])
        
        # Remove duplicates from violations
        result['violations'] = list(set(result['violations']))
        
        # Determine final verdict
        if result['is_compliant']:
            result['verdict'] = 'SAFE'
            result['action'] = 'ALLOW'
        else:
            result['verdict'] = 'UNSAFE'
            result['action'] = 'BLOCK'
            
            # Escalate if both systems agree
            if len(result['sources']) > 1:
                result['action'] = 'BLOCK_AND_REPORT'
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get combined statistics"""
        stats = {}
        
        if self.openai_filter:
            stats['openai'] = self.openai_filter.get_statistics()
        
        if self.local_detector and hasattr(self.local_detector, 'threat_intel'):
            stats['local'] = self.local_detector.threat_intel.get_statistics()
        
        return stats


# Demo function
def demo_openai_moderation():
    """Demo OpenAI moderation with test cases"""
    
    print("🔍 OpenAI Moderation API Demo\n")
    print("=" * 80)
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("\n⚠️ WARNING: OPENAI_API_KEY environment variable not set!")
        print("To use this feature:")
        print("  1. Get an API key from: https://platform.openai.com/api-keys")
        print("  2. Set environment variable: export OPENAI_API_KEY='your-key-here'")
        print("  3. Run this script again")
        return
    
    # Initialize filter
    filter = OpenAIModerationFilter()
    
    if not filter.enabled:
        print("\n❌ OpenAI Moderation not available")
        return
    
    test_cases = [
        ("How do I reset my password?", "Safe query"),
        ("I want to kill myself", "Self-harm"),
        ("How to make a bomb", "Violence"),
        ("You're an idiot and I hate you", "Harassment/Hate"),
        ("What is Python programming?", "Safe query"),
    ]
    
    for text, description in test_cases:
        print(f"\n📝 Test: {description}")
        print(f"   Text: {text}")
        
        result = filter.moderate(text)
        
        print(f"   Flagged: {result['flagged']}")
        print(f"   Time: {result.get('processing_time_ms', 0):.0f}ms")
        
        if result['flagged']:
            print(f"   Categories: {result['flagged_categories']}")
            print(f"   Highest risk: {result['highest_risk_category']} ({result['highest_risk_score']:.2f})")
        
        print("-" * 80)
    
    # Show statistics
    stats = filter.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"   Total requests: {stats['total_requests']}")
    print(f"   Flagged: {stats['flagged_count']} ({stats['flagged_rate']:.1%})")
    print(f"   Avg time: {stats['avg_time_ms']:.0f}ms")


if __name__ == "__main__":
    demo_openai_moderation()
