"""
Semantic Toxicity Detection Module

This module uses a transformer-based model (toxic-bert) to detect toxicity
and threats based on semantic understanding rather than just keyword matching.

Benefits:
- Detects novel phrasings ("end someone's life" vs "kill")
- Context understanding (creative writing vs real threat)
- Semantic similarity matching
- Catches obfuscated threats that bypass keyword filters

Model: unitary/toxic-bert (66MB, fine-tuned on Jigsaw Toxic Comments dataset)
"""

import warnings
warnings.filterwarnings('ignore')

from dataclasses import dataclass
from typing import Dict, Optional
import logging

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SemanticResult:
    """Result from semantic toxicity detection"""
    is_toxic: bool
    toxic_score: float
    severe_toxic_score: float
    obscene_score: float
    threat_score: float
    insult_score: float
    identity_hate_score: float
    confidence: float
    explanation: str
    model_available: bool = True
    
    @property
    def max_score(self) -> float:
        """Get the maximum toxicity score"""
        return max(
            self.toxic_score,
            self.severe_toxic_score,
            self.threat_score,
            self.identity_hate_score
        )
    
    @property
    def primary_category(self) -> str:
        """Get the primary toxicity category"""
        scores = {
            'toxic': self.toxic_score,
            'severe_toxic': self.severe_toxic_score,
            'obscene': self.obscene_score,
            'threat': self.threat_score,
            'insult': self.insult_score,
            'identity_hate': self.identity_hate_score,
        }
        return max(scores, key=scores.get)


class SemanticToxicityDetector:
    """
    Semantic toxicity detector using transformer models
    
    Falls back to basic heuristics if model is not available
    """
    
    def __init__(self, model_name: str = "unitary/toxic-bert", threshold: float = 0.7):
        """
        Initialize semantic detector
        
        Args:
            model_name: HuggingFace model name
            threshold: Threshold for toxicity detection (0-1)
        """
        self.model_name = model_name
        self.threshold = threshold
        self.model = None
        self.tokenizer = None
        self.model_available = False
        
        # Try to load model
        self._load_model()
    
    def _load_model(self):
        """Load the transformer model and tokenizer"""
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch
            
            logger.info(f"Loading semantic model: {self.model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self.model.eval()
            
            # Store torch for later use
            self.torch = torch
            
            self.model_available = True
            logger.info("✓ Semantic model loaded successfully")
            
        except ImportError:
            logger.warning(
                "⚠ Transformers library not installed. "
                "Semantic detection will use fallback mode. "
                "Install with: pip install transformers torch"
            )
            self.model_available = False
            
        except Exception as e:
            logger.warning(f"⚠ Could not load semantic model: {e}")
            logger.warning("Semantic detection will use fallback mode")
            self.model_available = False
    
    def predict(self, text: str) -> SemanticResult:
        """
        Predict toxicity using semantic understanding
        
        Args:
            text: Text to analyze
            
        Returns:
            SemanticResult with toxicity scores
        """
        if not text or len(text.strip()) < 3:
            return self._create_safe_result()
        
        # Use model if available
        if self.model_available and self.model is not None:
            return self._predict_with_model(text)
        else:
            # Fallback to heuristic
            return self._predict_fallback(text)
    
    def _predict_with_model(self, text: str) -> SemanticResult:
        """Predict using transformer model"""
        try:
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            
            # Predict
            with self.torch.no_grad():
                outputs = self.model(**inputs)
                probabilities = self.torch.sigmoid(outputs.logits)[0]
            
            # Extract scores
            toxic = float(probabilities[0])
            severe_toxic = float(probabilities[1])
            obscene = float(probabilities[2])
            threat = float(probabilities[3])
            insult = float(probabilities[4])
            identity_hate = float(probabilities[5])
            
            # Determine if toxic
            max_score = max(toxic, severe_toxic, threat, identity_hate)
            is_toxic = max_score >= self.threshold
            
            # Generate explanation
            if is_toxic:
                categories = []
                if threat >= self.threshold:
                    categories.append("threat")
                if severe_toxic >= self.threshold:
                    categories.append("severe toxicity")
                if identity_hate >= self.threshold:
                    categories.append("identity-based hate")
                if toxic >= self.threshold and not categories:
                    categories.append("general toxicity")
                
                explanation = f"Semantic analysis detected: {', '.join(categories)}"
            else:
                explanation = "Content appears safe based on semantic analysis"
            
            return SemanticResult(
                is_toxic=is_toxic,
                toxic_score=toxic,
                severe_toxic_score=severe_toxic,
                obscene_score=obscene,
                threat_score=threat,
                insult_score=insult,
                identity_hate_score=identity_hate,
                confidence=max_score,
                explanation=explanation,
                model_available=True
            )
            
        except Exception as e:
            logger.error(f"Error in semantic prediction: {e}")
            return self._predict_fallback(text)
    
    def _predict_fallback(self, text: str) -> SemanticResult:
        """Fallback heuristic-based prediction when model is unavailable"""
        text_lower = text.lower()
        
        # Simple heuristics for basic detection
        threat_keywords = [
            'kill', 'murder', 'shoot', 'bomb', 'attack', 'destroy',
            'harm', 'hurt', 'violence', 'weapon', 'gun', 'knife'
        ]
        
        hate_keywords = [
            'hate', 'nazi', 'racist', 'supremacist', 'genocide',
            'ethnic cleansing', 'subhuman'
        ]
        
        severe_keywords = [
            'massacre', 'assassinate', 'terrorist', 'terrorism',
            'slaughter', 'exterminate'
        ]
        
        # Count matches
        threat_count = sum(1 for kw in threat_keywords if kw in text_lower)
        hate_count = sum(1 for kw in hate_keywords if kw in text_lower)
        severe_count = sum(1 for kw in severe_keywords if kw in text_lower)
        
        # Calculate scores (simple heuristic)
        threat_score = min(1.0, threat_count * 0.3)
        identity_hate = min(1.0, hate_count * 0.4)
        severe_toxic = min(1.0, severe_count * 0.5)
        toxic = max(threat_score, identity_hate, severe_toxic) * 0.8
        
        max_score = max(toxic, severe_toxic, threat_score, identity_hate)
        is_toxic = max_score >= self.threshold
        
        explanation = (
            "Fallback heuristic detection (install transformers for better accuracy)"
            if is_toxic else
            "Content appears safe (fallback mode)"
        )
        
        return SemanticResult(
            is_toxic=is_toxic,
            toxic_score=toxic,
            severe_toxic_score=severe_toxic,
            obscene_score=0.0,
            threat_score=threat_score,
            insult_score=0.0,
            identity_hate_score=identity_hate,
            confidence=max_score * 0.6,  # Lower confidence in fallback mode
            explanation=explanation,
            model_available=False
        )
    
    def _create_safe_result(self) -> SemanticResult:
        """Create a result indicating safe content"""
        return SemanticResult(
            is_toxic=False,
            toxic_score=0.0,
            severe_toxic_score=0.0,
            obscene_score=0.0,
            threat_score=0.0,
            insult_score=0.0,
            identity_hate_score=0.0,
            confidence=0.0,
            explanation="Content too short or empty",
            model_available=self.model_available
        )
    
    def batch_predict(self, texts: list[str]) -> list[SemanticResult]:
        """
        Predict toxicity for multiple texts
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of SemanticResult objects
        """
        return [self.predict(text) for text in texts]
    
    def get_status(self) -> Dict:
        """Get detector status information"""
        return {
            'model_available': self.model_available,
            'model_name': self.model_name if self.model_available else 'fallback',
            'threshold': self.threshold,
            'mode': 'transformer' if self.model_available else 'heuristic'
        }


# Example usage and testing
if __name__ == "__main__":
    print("Semantic Toxicity Detector")
    print("=" * 50)
    
    # Initialize detector
    detector = SemanticToxicityDetector(threshold=0.7)
    
    # Print status
    status = detector.get_status()
    print(f"Status: {status}")
    print()
    
    # Test cases
    test_cases = [
        # Direct threats
        "I will kill you tomorrow",
        "Let's plan a terrorist attack",
        
        # Semantic variations (same meaning, different words)
        "I want to end someone's life",
        "Planning to eliminate my enemy",
        
        # Context-dependent
        "The character dies in the movie scene",
        "We need to kill the process",
        
        # Hate speech
        "All [group] people should be eliminated",
        
        # Safe content
        "I love going to school",
        "How to cook a healthy meal",
    ]
    
    print("Testing semantic detection:")
    print("-" * 50)
    
    for text in test_cases:
        result = detector.predict(text)
        print(f"\nText: {text}")
        print(f"Toxic: {result.is_toxic}")
        print(f"Confidence: {result.confidence:.3f}")
        
        if result.is_toxic:
            print(f"Primary Category: {result.primary_category}")
            print(f"Threat Score: {result.threat_score:.3f}")
            print(f"Severe Toxic: {result.severe_toxic_score:.3f}")
            print(f"Identity Hate: {result.identity_hate_score:.3f}")
            print(f"Explanation: {result.explanation}")
    
    print("\n" + "=" * 50)
    print("Note: For best results, install transformers:")
    print("  pip install transformers torch")
