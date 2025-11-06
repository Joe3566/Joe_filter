#!/usr/bin/env python3
"""
Semantic Analyzer for Context-Aware Compliance Detection
Provides semantic understanding and context analysis to reduce false positives
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json
import math

logger = logging.getLogger(__name__)

class ContentContext(Enum):
    """Types of content context"""
    PROFESSIONAL = "professional"
    EDUCATIONAL = "educational"
    PERSONAL = "personal"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    NEWS = "news"
    SOCIAL = "social"
    UNKNOWN = "unknown"

class IntentType(Enum):
    """User intent classification"""
    INFORMATIONAL = "informational"
    INSTRUCTIONAL = "instructional"
    CONVERSATIONAL = "conversational"
    MALICIOUS = "malicious"
    TESTING = "testing"
    CREATIVE_WRITING = "creative_writing"
    UNKNOWN = "unknown"

@dataclass
class SemanticAnalysis:
    """Result of semantic analysis"""
    context: ContentContext
    intent: IntentType
    sentiment_score: float  # -1 (negative) to 1 (positive)
    formality_score: float  # 0 (informal) to 1 (formal)
    toxicity_indicators: List[str]
    context_modifiers: List[str]
    confidence: float

class SemanticAnalyzer:
    """Advanced semantic analyzer for content understanding"""
    
    def __init__(self):
        self.context_keywords = self._load_context_keywords()
        self.intent_patterns = self._load_intent_patterns()
        self.sentiment_lexicon = self._load_sentiment_lexicon()
        self.formality_indicators = self._load_formality_indicators()
        
    def _load_context_keywords(self) -> Dict[ContentContext, List[str]]:
        """Load context classification keywords"""
        return {
            ContentContext.PROFESSIONAL: [
                'company', 'business', 'meeting', 'project', 'team', 'client', 
                'proposal', 'report', 'deadline', 'budget', 'revenue', 'strategy',
                'corporate', 'enterprise', 'department', 'manager', 'director',
                'email', 'contact', 'support', 'service', 'professional',
                'assistance', 'help', 'customer', 'inquiries', 'reach us'
            ],
            ContentContext.EDUCATIONAL: [
                'learn', 'study', 'education', 'school', 'university', 'college',
                'student', 'teacher', 'professor', 'course', 'class', 'lecture',
                'homework', 'assignment', 'research', 'academic', 'textbook',
                'knowledge', 'example', 'explanation', 'tutorial', 'training',
                'educational purposes', 'academic research', 'historical',
                'discussion', 'understand', 'learning about'
            ],
            ContentContext.TECHNICAL: [
                'code', 'programming', 'software', 'development', 'algorithm',
                'database', 'server', 'network', 'system', 'technology',
                'documentation', 'api', 'framework', 'library', 'debug',
                'configuration', 'deployment', 'architecture', 'technical',
                'cybersecurity', 'exploit', 'vulnerability'
            ],
            ContentContext.CREATIVE: [
                'story', 'novel', 'character', 'fiction', 'creative', 'writing',
                'art', 'design', 'music', 'poetry', 'literature', 'imagination',
                'fantasy', 'science fiction', 'drama', 'comedy', 'plot',
                'narrative', 'artistic', 'creative expression', 'fictional',
                'in my novel', 'in this story', 'character commits', 'medieval times'
            ],
            ContentContext.NEWS: [
                'news', 'report', 'journalist', 'article', 'breaking', 'update',
                'press', 'media', 'newspaper', 'broadcast', 'coverage',
                'headline', 'story', 'investigation', 'interview', 'source'
            ]
        }
    
    def _load_intent_patterns(self) -> Dict[IntentType, List[str]]:
        """Load intent classification patterns"""
        return {
            IntentType.INFORMATIONAL: [
                r'\bwhat\s+is\b', r'\bhow\s+to\b', r'\bwhy\s+does\b',
                r'\bexplain\b', r'\btell\s+me\s+about\b', r'\binformation\s+about\b',
                r'\bdefine\b', r'\bdefinition\s+of\b', r'\bhelp\s+me\s+understand\b'
            ],
            IntentType.INSTRUCTIONAL: [
                r'\bstep\s+by\s+step\b', r'\binstructions?\b', r'\bguide\b',
                r'\btutorial\b', r'\bhow\s+do\s+i\b', r'\bteach\s+me\b',
                r'\bshow\s+me\s+how\b', r'\bwalk\s+me\s+through\b'
            ],
            IntentType.MALICIOUS: [
                r'\bhow\s+to\s+(?:hack|break|bypass|exploit)\b',
                r'\bignore\s+(?:all|previous|your)\s+instructions\b',
                r'\bpretend\s+to\s+be\b', r'\byou\s+are\s+now\b',
                r'\bact\s+like\s+you\b', r'\bjailbreak\b', r'\bbypass\s+(?:safety|restrictions)\b'
            ],
            IntentType.TESTING: [
                r'\btest\b', r'\btesting\b', r'\bexample\b', r'\bsample\b',
                r'\bdemo\b', r'\btrial\b', r'\bcheck\s+if\b', r'\bvalidate\b'
            ]
        }
    
    def _load_sentiment_lexicon(self) -> Dict[str, float]:
        """Load sentiment analysis lexicon"""
        positive_words = {
            'good': 0.7, 'great': 0.8, 'excellent': 0.9, 'amazing': 0.9,
            'wonderful': 0.8, 'fantastic': 0.8, 'awesome': 0.8, 'love': 0.9,
            'like': 0.6, 'enjoy': 0.7, 'happy': 0.8, 'pleased': 0.7,
            'satisfied': 0.7, 'positive': 0.6, 'helpful': 0.6, 'thank': 0.6
        }
        
        negative_words = {
            'bad': -0.7, 'terrible': -0.9, 'horrible': -0.9, 'awful': -0.9,
            'hate': -0.9, 'dislike': -0.6, 'angry': -0.8, 'frustrated': -0.7,
            'disappointed': -0.7, 'sad': -0.7, 'upset': -0.7, 'annoyed': -0.6,
            'stupid': -0.8, 'idiotic': -0.8, 'worthless': -0.9, 'useless': -0.7
        }
        
        return {**positive_words, **negative_words}
    
    def _load_formality_indicators(self) -> Dict[str, float]:
        """Load formality scoring indicators"""
        formal_indicators = {
            # Formal language patterns
            'professional': 1.0, 'corporation': 1.0, 'organization': 1.0,
            'therefore': 0.8, 'furthermore': 0.8, 'consequently': 0.8,
            'respectively': 0.9, 'pursuant': 0.9, 'hereby': 0.9,
            'sincerely': 0.8, 'regards': 0.7, 'dear': 0.6
        }
        
        informal_indicators = {
            # Informal language patterns
            'yeah': -0.7, 'yep': -0.7, 'nope': -0.7, 'gonna': -0.8,
            'wanna': -0.8, 'kinda': -0.7, 'sorta': -0.7, 'dunno': -0.8,
            'btw': -0.8, 'lol': -0.9, 'omg': -0.9, 'wtf': -0.9,
            'hey': -0.5, 'hi': -0.3, 'cool': -0.4
        }
        
        return {**formal_indicators, **informal_indicators}
    
    def analyze(self, text: str) -> SemanticAnalysis:
        """
        Perform comprehensive semantic analysis of text
        
        Args:
            text: Text content to analyze
            
        Returns:
            SemanticAnalysis with context, intent, sentiment, etc.
        """
        text_lower = text.lower()
        
        # Classify content context
        context = self._classify_context(text_lower)
        
        # Classify user intent
        intent = self._classify_intent(text_lower)
        
        # Analyze sentiment
        sentiment_score = self._analyze_sentiment(text_lower)
        
        # Analyze formality
        formality_score = self._analyze_formality(text_lower)
        
        # Detect toxicity indicators
        toxicity_indicators = self._detect_toxicity_indicators(text_lower)
        
        # Find context modifiers
        context_modifiers = self._find_context_modifiers(text_lower)
        
        # Calculate overall confidence
        confidence = self._calculate_confidence(context, intent, sentiment_score, formality_score)
        
        return SemanticAnalysis(
            context=context,
            intent=intent,
            sentiment_score=sentiment_score,
            formality_score=formality_score,
            toxicity_indicators=toxicity_indicators,
            context_modifiers=context_modifiers,
            confidence=confidence
        )
    
    def _classify_context(self, text: str) -> ContentContext:
        """Classify the content context"""
        import re
        context_scores = {}
        
        # Check for explicit personal indicators first
        if re.search(r'\bmy\s+(?:personal\s+)?(?:email|phone|address)', text):
            return ContentContext.PERSONAL
        
        # Check for threats that mention school/educational settings but are not educational
        if re.search(r'\b(?:hurt|kill|harm).*(?:school|people)', text):
            return ContentContext.UNKNOWN  # Don't classify threats as educational
        
        for context_type, keywords in self.context_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                # Weight by keyword frequency and text length
                context_scores[context_type] = score / len(text.split()) * 100
        
        # Special handling for ambiguous cases
        if 'email' in text and 'support' not in text and 'contact' not in text:
            # Likely personal if no business indicators
            context_scores[ContentContext.PERSONAL] = context_scores.get(ContentContext.PERSONAL, 0) + 5
        
        if not context_scores:
            return ContentContext.UNKNOWN
        
        # Return the context with highest score
        return max(context_scores.items(), key=lambda x: x[1])[0]
    
    def _classify_intent(self, text: str) -> IntentType:
        """Classify user intent"""
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return intent_type
        
        return IntentType.UNKNOWN
    
    def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment polarity"""
        words = re.findall(r'\b\w+\b', text)
        sentiment_scores = []
        
        for word in words:
            if word in self.sentiment_lexicon:
                sentiment_scores.append(self.sentiment_lexicon[word])
        
        if not sentiment_scores:
            return 0.0
        
        # Return average sentiment with some decay for longer texts
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        decay_factor = min(1.0, 10 / len(words))  # Less extreme for longer texts
        
        return avg_sentiment * decay_factor
    
    def _analyze_formality(self, text: str) -> float:
        """Analyze formality level"""
        words = re.findall(r'\b\w+\b', text)
        formality_scores = []
        
        for word in words:
            if word in self.formality_indicators:
                formality_scores.append(self.formality_indicators[word])
        
        # Check for formal patterns
        formal_patterns = [
            r'\b(?:however|therefore|furthermore|consequently|nevertheless)\b',
            r'\bsincerely\b', r'\bregards\b', r'\bdear\s+\w+\b',
            r'\bi\s+am\s+writing\s+to\b', r'\bthank\s+you\s+for\s+your\b'
        ]
        
        for pattern in formal_patterns:
            if re.search(pattern, text):
                formality_scores.append(0.8)
        
        # Check for informal patterns
        informal_patterns = [
            r'\b(?:gonna|wanna|kinda|sorta|dunno)\b',
            r'\b(?:lol|omg|wtf|btw|tbh)\b',
            r'[!]{2,}', r'[?]{2,}',  # Multiple punctuation
            r'\b\w+\b(?=\s*[.!?]*\s*$)'  # Ending with informal words
        ]
        
        for pattern in informal_patterns:
            if re.search(pattern, text):
                formality_scores.append(-0.6)
        
        if not formality_scores:
            return 0.5  # Neutral formality
        
        # Normalize to 0-1 scale
        avg_formality = sum(formality_scores) / len(formality_scores)
        return max(0.0, min(1.0, (avg_formality + 1) / 2))
    
    def _detect_toxicity_indicators(self, text: str) -> List[str]:
        """Detect indicators that might suggest toxicity"""
        indicators = []
        
        # Excessive capitalization
        if re.search(r'\b[A-Z]{3,}\b.*\b[A-Z]{3,}\b', text):
            indicators.append('excessive_capitalization')
        
        # Multiple exclamation marks
        if re.search(r'[!]{3,}', text):
            indicators.append('excessive_punctuation')
        
        # Profanity markers (without explicit words)
        if re.search(r'\b\w*\*+\w*\b', text):
            indicators.append('censored_profanity')
        
        # Aggressive language patterns
        aggressive_patterns = [
            r'\byou\s+(?:always|never)\b',
            r'\bshut\s+up\b',
            r'\bget\s+out\b',
            r'\bgo\s+away\b'
        ]
        
        for pattern in aggressive_patterns:
            if re.search(pattern, text):
                indicators.append('aggressive_language')
                break
        
        return indicators
    
    def _find_context_modifiers(self, text: str) -> List[str]:
        """Find words/phrases that modify context interpretation"""
        modifiers = []
        
        # Hypothetical/fictional modifiers
        hypothetical_patterns = [
            r'\bimagine\s+if\b', r'\bwhat\s+if\b', r'\bsuppose\b',
            r'\bhypothetically\b', r'\bin\s+a\s+story\b', r'\bfictional\b',
            r'\bmake\s+believe\b', r'\bpretend\b'
        ]
        
        for pattern in hypothetical_patterns:
            if re.search(pattern, text):
                modifiers.append('hypothetical')
                break
        
        # Educational/informational modifiers
        educational_patterns = [
            r'\bfor\s+educational\s+purposes\b', r'\bto\s+learn\s+about\b',
            r'\bacademic\s+research\b', r'\bhistorical\s+context\b',
            r'\binformation\s+only\b'
        ]
        
        for pattern in educational_patterns:
            if re.search(pattern, text):
                modifiers.append('educational')
                break
        
        # Negation modifiers (but not for hate speech contexts)
        negation_patterns = [
            r'\bdon\'?t\b', r'\bnever\b', r'\bnot\b', r'\bno\s+(?:way|one)\b',
            r'\brefuse\s+to\b', r'\bwon\'?t\b'
        ]
        
        # Don't apply negation modifier if it's hate speech like "don't belong"
        has_hate_indicators = bool(re.search(r'\b(?:inferior|subhuman|hate|stupid)\b', text, re.IGNORECASE))
        
        if not has_hate_indicators:
            for pattern in negation_patterns:
                if re.search(pattern, text):
                    modifiers.append('negation')
                    break
        
        return modifiers
    
    def _calculate_confidence(self, context: ContentContext, intent: IntentType, 
                           sentiment: float, formality: float) -> float:
        """Calculate confidence in semantic analysis"""
        confidence_factors = []
        
        # Context confidence
        if context != ContentContext.UNKNOWN:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.3)
        
        # Intent confidence
        if intent != IntentType.UNKNOWN:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.4)
        
        # Sentiment confidence (higher for more extreme sentiments)
        sentiment_confidence = min(0.9, abs(sentiment) + 0.3)
        confidence_factors.append(sentiment_confidence)
        
        # Formality confidence (higher for more extreme formality)
        formality_confidence = min(0.8, abs(formality - 0.5) * 2 + 0.4)
        confidence_factors.append(formality_confidence)
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def is_likely_false_positive(self, text: str, violation_type: str) -> Tuple[bool, str]:
        """
        Determine if a detected violation is likely a false positive
        
        Returns:
            (is_false_positive, reason)
        """
        analysis = self.analyze(text)
        
        # Check for educational/professional context
        if analysis.context in [ContentContext.EDUCATIONAL, ContentContext.PROFESSIONAL]:
            if violation_type in ['personal_info', 'hate_speech']:
                return True, f"Content appears to be {analysis.context.value} in nature"
        
        # Check for creative writing context
        if analysis.context == ContentContext.CREATIVE:
            if violation_type in ['violence', 'hate_speech']:
                return True, "Content appears to be creative fiction"
        
        # Check for informational intent (but not for clearly harmful queries)
        if analysis.intent == IntentType.INFORMATIONAL:
            if violation_type in ['violence', 'illegal_activity']:
                # Don't override if it's explicitly about harming others
                if not re.search(r'\b(?:harm|hurt|kill)\s+(?:others|people)', text, re.IGNORECASE):
                    return True, "Content appears to be seeking information, not planning harm"
        
        # Check for hypothetical context
        if 'hypothetical' in analysis.context_modifiers:
            if violation_type in ['violence', 'illegal_activity', 'hate_speech']:
                return True, "Content appears to be hypothetical discussion"
        
        # Check for educational modifiers
        if 'educational' in analysis.context_modifiers:
            return True, "Content marked for educational purposes"
        
        # Check for negation
        if 'negation' in analysis.context_modifiers and violation_type == 'hate_speech':
            return True, "Content contains negation that may change meaning"
        
        # Check formality for professional contexts
        if analysis.formality_score > 0.7 and violation_type == 'personal_info':
            # High formality might indicate business communication
            if re.search(r'\b(?:contact|support|info)@\w+\.\w+\b', text):
                return True, "Formal context suggests business contact information"
        
        return False, ""

# Helper function for integration
def create_semantic_analyzer() -> SemanticAnalyzer:
    """Create and return a SemanticAnalyzer instance"""
    return SemanticAnalyzer()

if __name__ == "__main__":
    # Test the semantic analyzer
    analyzer = SemanticAnalyzer()
    
    test_cases = [
        "I hate broccoli, it tastes terrible",
        "I hate all immigrants from that country",
        "For support, please contact us at help@company.com",
        "My personal email is john.doe@gmail.com",
        "In this fictional story, the character commits violence",
        "How to commit violence in real life",
        "What if someone wanted to hurt others? (hypothetically)",
        "I'm researching historical violence for my thesis"
    ]
    
    print("🧠 Testing Semantic Analyzer")
    print("=" * 50)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {text}")
        analysis = analyzer.analyze(text)
        
        print(f"🎯 Context: {analysis.context.value}")
        print(f"💡 Intent: {analysis.intent.value}")
        print(f"😊 Sentiment: {analysis.sentiment_score:.2f}")
        print(f"👔 Formality: {analysis.formality_score:.2f}")
        print(f"⚠️ Toxicity Indicators: {analysis.toxicity_indicators}")
        print(f"🔧 Context Modifiers: {analysis.context_modifiers}")
        print(f"📊 Confidence: {analysis.confidence:.2f}")
        
        # Test false positive detection
        false_positive, reason = analyzer.is_likely_false_positive(text, "hate_speech")
        if false_positive:
            print(f"✅ Likely false positive: {reason}")
        else:
            print("❌ Not a false positive")