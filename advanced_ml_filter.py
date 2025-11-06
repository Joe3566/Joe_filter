#!/usr/bin/env python3
"""
🤖 ADVANCED ML COMPLIANCE FILTER
Multi-layered machine learning approach with training capabilities for high-accuracy content filtering.
"""

import numpy as np
import pandas as pd
import pickle
import re
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
import logging
from dataclasses import dataclass

# ML libraries
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, f1_score
from sklearn.preprocessing import StandardScaler
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Try to download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    print("Downloading NLTK data...")
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)

@dataclass
class FilterResult:
    """Result from advanced ML filtering"""
    is_violation: bool
    confidence: float
    violation_type: str
    severity: str
    reasoning: List[str]
    processing_time_ms: float
    model_scores: Dict[str, float]
    features_triggered: List[str]

class AdvancedTrainingDataGenerator:
    """Generate comprehensive training data for various violation types"""
    
    def __init__(self):
        self.violation_patterns = {
            'hate_speech': {
                'direct_hate': [
                    "I hate all {group} people", "All {group} should die", "{group} are inferior",
                    "Kill all {group}", "{group} don't belong here", "I despise {group}",
                    "{group} should be eliminated", "Death to all {group}", "{group} are scum",
                    "I wish all {group} would disappear", "{group} are worthless parasites"
                ],
                'coded_hate': [
                    "{group} are taking over our country", "We need to do something about the {group} problem",
                    "{group} are destroying our society", "The {group} invasion must be stopped",
                    "{group} are not like us", "Traditional values are under attack by {group}",
                    "Our children's future is threatened by {group}", "Real Americans vs {group}"
                ],
                'groups': ['immigrants', 'muslims', 'jews', 'blacks', 'whites', 'asians', 'latinos', 
                          'lgbtq', 'women', 'men', 'christians', 'foreigners', 'refugees']
            },
            'violence': {
                'direct_threats': [
                    "I'm going to kill you", "You deserve to die", "I'll hurt you badly",
                    "I'm coming for you", "You won't live to see tomorrow", "I'll make you suffer",
                    "Death is coming for you", "I'll end your life", "You're as good as dead"
                ],
                'mass_violence': [
                    "Shoot up the school", "Bomb the building", "Mass shooting plan",
                    "Kill everyone at {location}", "Terrorist attack on {location}",
                    "Explosive device instructions", "How to make bombs", "School shooting guide"
                ],
                'locations': ['school', 'mall', 'church', 'synagogue', 'mosque', 'office', 'concert']
            },
            'self_harm': [
                "I want to kill myself", "How to commit suicide", "End my life tonight",
                "Pills to overdose", "Hanging methods", "I can't go on living",
                "Suicide is the only option", "I want to die", "Kill myself today"
            ],
            'sexual_content': [
                "Explicit sexual content with minors", "Child exploitation material",
                "Non-consensual intimate content", "Revenge porn distribution",
                "Sexual violence descriptions", "Graphic sexual abuse content"
            ],
            'privacy_violations': [
                "SSN: 123-45-6789", "Credit card: 4532-1234-5678-9012",
                "Address: 123 Main St, City, State 12345", "Phone: (555) 123-4567",
                "Social security number 987654321", "My credit card number is 4111111111111111",
                "Email: john.doe@company.com password: secret123"
            ],
            'misinformation': [
                "COVID vaccine contains microchips", "Election results were fabricated",
                "Proven cure for cancer being suppressed", "Government controls weather",
                "Flat earth evidence covered up", "Moon landing was fake"
            ],
            'illegal_activities': [
                "How to make drugs at home", "Sell stolen goods online",
                "Hack into bank accounts", "Identity theft methods",
                "Money laundering tutorial", "Credit card fraud guide",
                "Tax evasion strategies", "Illegal weapons purchasing"
            ]
        }
        
        self.safe_content = [
            "Hello, how are you today?", "I love spending time with my family",
            "What's the weather like?", "Great job on the presentation!",
            "I enjoy reading books", "Thanks for your help", "Have a wonderful day",
            "The sunset looks beautiful", "I'm excited about the project",
            "Coffee tastes great this morning", "Looking forward to the weekend",
            "Academic research on social media", "Discussion about politics",
            "News article analysis", "Scientific study results",
            "Educational content about history", "Book review and recommendations",
            "Movie discussion and critique", "Recipe for chocolate cake",
            "Travel experiences and tips", "Technology tutorial and guide",
            "Professional networking message", "Customer service inquiry",
            "Product review and feedback", "Event planning discussion",
            "Creative writing sample", "Art appreciation post"
        ]

    def generate_training_data(self, samples_per_category: int = 200) -> pd.DataFrame:
        """Generate comprehensive training dataset"""
        training_data = []
        
        # Generate violation samples
        for category, patterns in self.violation_patterns.items():
            if category == 'hate_speech':
                for subcategory, templates in patterns.items():
                    if subcategory == 'groups':
                        continue
                    for template in templates:
                        for group in patterns['groups']:
                            content = template.format(group=group)
                            training_data.append({
                                'content': content,
                                'label': 1,  # Violation
                                'category': category,
                                'subcategory': subcategory,
                                'severity': 'high' if 'kill' in content.lower() or 'die' in content.lower() else 'medium'
                            })
            elif category == 'violence':
                for subcategory, templates in patterns.items():
                    if subcategory == 'locations':
                        continue
                    for template in templates:
                        if '{location}' in template:
                            for location in patterns['locations']:
                                content = template.format(location=location)
                                training_data.append({
                                    'content': content,
                                    'label': 1,
                                    'category': category,
                                    'subcategory': subcategory,
                                    'severity': 'high'
                                })
                        else:
                            training_data.append({
                                'content': template,
                                'label': 1,
                                'category': category,
                                'subcategory': subcategory,
                                'severity': 'high'
                            })
            else:
                for template in patterns:
                    severity = 'high' if any(word in template.lower() for word in ['kill', 'die', 'bomb', 'shoot']) else 'medium'
                    training_data.append({
                        'content': template,
                        'label': 1,
                        'category': category,
                        'subcategory': 'general',
                        'severity': severity
                    })
        
        # Generate safe content samples
        for content in self.safe_content:
            training_data.append({
                'content': content,
                'label': 0,  # Safe
                'category': 'safe',
                'subcategory': 'general',
                'severity': 'none'
            })
        
        # Add variations and augmentations
        augmented_data = []
        for item in training_data[:samples_per_category]:
            # Original
            augmented_data.append(item)
            
            # Case variations
            augmented_data.append({
                **item,
                'content': item['content'].upper()
            })
            augmented_data.append({
                **item,
                'content': item['content'].lower()
            })
            
            # Add typos and character substitutions (for evasion attempts)
            content_with_typos = item['content']
            content_with_typos = content_with_typos.replace('a', '@').replace('o', '0').replace('e', '3')
            augmented_data.append({
                **item,
                'content': content_with_typos
            })
        
        return pd.DataFrame(augmented_data)

class AdvancedTextProcessor:
    """Advanced text preprocessing for ML models"""
    
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
    def preprocess_text(self, text: str) -> str:
        """Advanced text preprocessing"""
        # Convert to lowercase
        text = text.lower()
        
        # Normalize character substitutions (common evasion)
        char_map = {'@': 'a', '0': 'o', '3': 'e', '1': 'i', '5': 's', '7': 't'}
        for char, replacement in char_map.items():
            text = text.replace(char, replacement)
        
        # Remove extra whitespace and special characters
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Tokenize and lemmatize
        tokens = word_tokenize(text)
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens 
                 if token not in self.stop_words and len(token) > 2]
        
        return ' '.join(tokens)
    
    def extract_features(self, text: str) -> Dict[str, float]:
        """Extract advanced features for ML models"""
        features = {}
        
        # Basic metrics
        features['length'] = len(text)
        features['word_count'] = len(text.split())
        features['avg_word_length'] = np.mean([len(word) for word in text.split()]) if text.split() else 0
        
        # Uppercase ratio
        features['uppercase_ratio'] = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        
        # Special character density
        features['special_char_density'] = sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text) if text else 0
        
        # Profanity indicators
        profanity_words = ['hate', 'kill', 'die', 'hurt', 'bomb', 'shoot', 'murder', 'death', 'terrorist']
        features['profanity_count'] = sum(1 for word in profanity_words if word in text.lower())
        
        # Threat indicators
        threat_phrases = ['i will', 'going to', 'plan to', 'you should', 'they deserve']
        features['threat_indicators'] = sum(1 for phrase in threat_phrases if phrase in text.lower())
        
        # Personal info patterns
        features['has_numbers'] = 1 if re.search(r'\d', text) else 0
        features['has_email'] = 1 if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text) else 0
        features['has_phone'] = 1 if re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text) else 0
        features['has_ssn'] = 1 if re.search(r'\b\d{3}[-]?\d{2}[-]?\d{4}\b', text) else 0
        
        return features

class MultiLayerMLFilter:
    """Multi-layered machine learning compliance filter"""
    
    def __init__(self, model_path: str = "ml_compliance_models"):
        self.model_path = Path(model_path)
        self.model_path.mkdir(exist_ok=True)
        
        self.text_processor = AdvancedTextProcessor()
        self.vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1, 3))
        self.scaler = StandardScaler()
        
        # Ensemble of models
        self.models = {
            'logistic': LogisticRegression(random_state=42),
            'svm': SVC(probability=True, random_state=42),
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42)
        }
        
        self.ensemble_model = None
        self.is_trained = False
        self.training_metrics = {}
        
    def train(self, force_retrain: bool = False) -> Dict[str, Any]:
        """Train the multi-layer ML models"""
        model_file = self.model_path / "trained_models.pkl"
        
        if model_file.exists() and not force_retrain:
            print("Loading existing trained models...")
            return self.load_models()
        
        print("Generating training data...")
        data_generator = AdvancedTrainingDataGenerator()
        df = data_generator.generate_training_data(samples_per_category=300)
        
        print(f"Training on {len(df)} samples...")
        
        # Preprocess text
        df['processed_content'] = df['content'].apply(self.text_processor.preprocess_text)
        
        # Prepare features
        X_text = self.vectorizer.fit_transform(df['processed_content'])
        
        # Extract additional features
        feature_dicts = df['content'].apply(self.text_processor.extract_features).tolist()
        X_features = pd.DataFrame(feature_dicts).fillna(0)
        X_features_scaled = self.scaler.fit_transform(X_features)
        
        # Combine text and engineered features
        X_combined = np.hstack([X_text.toarray(), X_features_scaled])
        y = df['label'].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_combined, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train individual models
        trained_models = []
        model_scores = {}
        
        for name, model in self.models.items():
            print(f"Training {name}...")
            model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            
            model_scores[name] = {'accuracy': accuracy, 'f1': f1}
            trained_models.append((name, model))
            
            print(f"{name} - Accuracy: {accuracy:.3f}, F1: {f1:.3f}")
        
        # Create ensemble
        self.ensemble_model = VotingClassifier(
            estimators=trained_models,
            voting='soft'
        )
        self.ensemble_model.fit(X_train, y_train)
        
        # Evaluate ensemble
        y_pred_ensemble = self.ensemble_model.predict(X_test)
        ensemble_accuracy = accuracy_score(y_test, y_pred_ensemble)
        ensemble_f1 = f1_score(y_test, y_pred_ensemble)
        
        model_scores['ensemble'] = {'accuracy': ensemble_accuracy, 'f1': ensemble_f1}
        print(f"Ensemble - Accuracy: {ensemble_accuracy:.3f}, F1: {ensemble_f1:.3f}")
        
        self.training_metrics = {
            'training_samples': len(df),
            'test_accuracy': ensemble_accuracy,
            'test_f1': ensemble_f1,
            'model_scores': model_scores,
            'training_date': datetime.now().isoformat()
        }
        
        # Save models
        self.save_models()
        self.is_trained = True
        
        return self.training_metrics
    
    def save_models(self):
        """Save trained models to disk"""
        model_data = {
            'vectorizer': self.vectorizer,
            'scaler': self.scaler,
            'ensemble_model': self.ensemble_model,
            'individual_models': self.models,
            'training_metrics': self.training_metrics
        }
        
        with open(self.model_path / "trained_models.pkl", 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Models saved to {self.model_path / 'trained_models.pkl'}")
    
    def load_models(self) -> Dict[str, Any]:
        """Load trained models from disk"""
        try:
            with open(self.model_path / "trained_models.pkl", 'rb') as f:
                model_data = pickle.load(f)
            
            self.vectorizer = model_data['vectorizer']
            self.scaler = model_data['scaler']
            self.ensemble_model = model_data['ensemble_model']
            self.models = model_data['individual_models']
            self.training_metrics = model_data['training_metrics']
            self.is_trained = True
            
            print("Models loaded successfully")
            return self.training_metrics
        
        except Exception as e:
            print(f"Error loading models: {e}")
            return {}
    
    def predict(self, text: str) -> FilterResult:
        """Predict if text contains violations"""
        if not self.is_trained:
            raise ValueError("Models not trained. Call train() first.")
        
        start_time = time.time()
        
        # Preprocess text
        processed_text = self.text_processor.preprocess_text(text)
        
        # Extract features
        X_text = self.vectorizer.transform([processed_text])
        feature_dict = self.text_processor.extract_features(text)
        X_features = self.scaler.transform(pd.DataFrame([feature_dict]).fillna(0))
        
        # Combine features
        X_combined = np.hstack([X_text.toarray(), X_features])
        
        # Get predictions from all models
        model_scores = {}
        individual_predictions = []
        
        for name, model in self.models.items():
            pred_proba = model.predict_proba(X_combined)[0]
            violation_prob = pred_proba[1] if len(pred_proba) > 1 else 0
            model_scores[name] = violation_prob
            individual_predictions.append(violation_prob)
        
        # Ensemble prediction
        ensemble_pred = self.ensemble_model.predict(X_combined)[0]
        ensemble_proba = self.ensemble_model.predict_proba(X_combined)[0]
        final_confidence = ensemble_proba[1] if len(ensemble_proba) > 1 else 0
        
        # Determine violation type and severity
        violation_type = "unknown"
        severity = "low"
        reasoning = []
        features_triggered = []
        
        if final_confidence > 0.5:
            # Analyze content for specific violation types
            text_lower = text.lower()
            
            if any(word in text_lower for word in ['hate', 'kill', 'die', 'murder']):
                violation_type = "hate_speech_violence"
                severity = "high"
                reasoning.append("Contains explicit hate speech or violent language")
                features_triggered.append("violent_language")
            
            if re.search(r'\d{3}[-.]?\d{2}[-.]?\d{4}', text) or '@' in text:
                violation_type = "privacy_violation"
                severity = "medium"
                reasoning.append("Contains potential personal information")
                features_triggered.append("personal_info")
            
            if feature_dict.get('threat_indicators', 0) > 0:
                violation_type = "threat"
                severity = "high"
                reasoning.append("Contains threatening language patterns")
                features_triggered.append("threat_patterns")
            
            if feature_dict.get('profanity_count', 0) > 0:
                reasoning.append("Contains offensive or harmful language")
                features_triggered.append("offensive_language")
        
        processing_time = (time.time() - start_time) * 1000
        
        return FilterResult(
            is_violation=ensemble_pred == 1,
            confidence=float(final_confidence),
            violation_type=violation_type,
            severity=severity,
            reasoning=reasoning,
            processing_time_ms=processing_time,
            model_scores=model_scores,
            features_triggered=features_triggered
        )

def main():
    """Demonstration of the advanced ML filter"""
    print("🤖 Advanced ML Compliance Filter - Training & Demo")
    print("=" * 60)
    
    # Initialize filter
    ml_filter = MultiLayerMLFilter()
    
    # Train models
    print("\n🔧 Training ML models...")
    training_results = ml_filter.train(force_retrain=True)
    
    print(f"\n✅ Training complete!")
    print(f"Training samples: {training_results['training_samples']}")
    print(f"Test accuracy: {training_results['test_accuracy']:.3f}")
    print(f"Test F1 score: {training_results['test_f1']:.3f}")
    
    # Test cases
    test_cases = [
        "Hello, how are you today?",
        "I hate all immigrants and they should go back",
        "My social security number is 123-45-6789",
        "I'm going to kill everyone at the school tomorrow",
        "This is an academic paper on hate speech detection",
        "You deserve to die for what you've done",
        "The weather is beautiful today",
        "How to make bombs at home tutorial",
        "Customer service was excellent",
        "I will hurt you if you don't listen"
    ]
    
    print(f"\n🧪 Testing on {len(test_cases)} cases:")
    print("-" * 80)
    
    for i, text in enumerate(test_cases, 1):
        result = ml_filter.predict(text)
        
        status = "🚫 VIOLATION" if result.is_violation else "✅ SAFE"
        print(f"\n{i}. {status}")
        print(f"   Text: '{text[:60]}{'...' if len(text) > 60 else ''}'")
        print(f"   Confidence: {result.confidence:.3f}")
        print(f"   Type: {result.violation_type}")
        print(f"   Severity: {result.severity}")
        print(f"   Processing: {result.processing_time_ms:.1f}ms")
        
        if result.reasoning:
            print(f"   Reasoning: {', '.join(result.reasoning)}")
    
    print(f"\n🎯 Advanced ML filter ready for production use!")
    return ml_filter

if __name__ == "__main__":
    main()