"""
Ensemble Model System for Enhanced Harmful Content Detection

Combines multiple models and detection approaches for superior accuracy and coverage.
"""

import logging
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
import concurrent.futures
from pathlib import Path

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    ENSEMBLE_AVAILABLE = True
except ImportError:
    logging.warning("Ensemble dependencies not available")
    ENSEMBLE_AVAILABLE = False

from .training_system import HarmfulContentCategory


@dataclass
class EnsembleResult:
    """Result from ensemble model prediction."""
    category: HarmfulContentCategory
    confidence: float
    individual_scores: Dict[str, float]
    consensus_score: float
    is_harmful: bool
    reasoning: List[str]


class ModelWeight(Enum):
    """Weighting strategies for ensemble models."""
    EQUAL = "equal"
    PERFORMANCE_BASED = "performance_based"
    CONFIDENCE_BASED = "confidence_based"
    ADAPTIVE = "adaptive"


class EnsembleHarmfulContentDetector:
    """Ensemble detector combining multiple models for harmful content detection."""
    
    def __init__(self, config: Dict[str, Any] = None):
        if not ENSEMBLE_AVAILABLE:
            raise ImportError("Ensemble dependencies not available")
        
        self.config = config or {}
        
        # Initialize multiple models
        self.models = {}
        self.model_weights = {}
        self.model_performance = {}
        
        # Load ensemble configuration
        self.ensemble_config = self.config.get('ensemble', {})
        self.weighting_strategy = ModelWeight(
            self.ensemble_config.get('weighting_strategy', 'equal')
        )
        
        # Initialize models
        self._initialize_models()
        
        # Category-specific thresholds
        self.category_thresholds = {
            HarmfulContentCategory.VIOLENCE: 0.7,
            HarmfulContentCategory.SELF_HARM: 0.6,
            HarmfulContentCategory.ILLEGAL_ACTIVITIES: 0.8,
            HarmfulContentCategory.HARASSMENT: 0.65,
            HarmfulContentCategory.EXTREMISM: 0.75,
            HarmfulContentCategory.HATE_SPEECH: 0.7,
            HarmfulContentCategory.TOXICITY: 0.65,
            HarmfulContentCategory.THREATS: 0.8,
            HarmfulContentCategory.CYBERBULLYING: 0.6,
            HarmfulContentCategory.DISCRIMINATION: 0.7,
            HarmfulContentCategory.ADULT_CONTENT: 0.75,
            HarmfulContentCategory.MISINFORMATION: 0.8
        }
    
    def _initialize_models(self):
        """Initialize the ensemble of models."""
        
        # Define available models for different categories
        model_configs = {
            'toxic_bert': {
                'model': 'unitary/toxic-bert',
                'categories': [HarmfulContentCategory.TOXICITY, HarmfulContentCategory.HATE_SPEECH],
                'weight': 1.0
            },
            'hate_speech_bert': {
                'model': 'Hate-speech-CNERG/dehatebert-mono-english',
                'categories': [HarmfulContentCategory.HATE_SPEECH, HarmfulContentCategory.DISCRIMINATION],
                'weight': 1.0,
                'fallback': True  # Use as fallback if primary fails
            },
            'violence_classifier': {
                'model': 'unitary/toxic-bert',  # Repurposed for violence detection
                'categories': [HarmfulContentCategory.VIOLENCE, HarmfulContentCategory.THREATS],
                'weight': 0.8
            }
        }
        
        # Load models that are available
        for model_name, config in model_configs.items():
            try:
                model_path = config['model']
                
                # Try to load the model
                tokenizer = AutoTokenizer.from_pretrained(model_path)
                model = AutoModelForSequenceClassification.from_pretrained(model_path)
                
                # Create pipeline
                classifier = pipeline(
                    "text-classification",
                    model=model,
                    tokenizer=tokenizer,
                    device=0 if torch.cuda.is_available() else -1,
                    return_all_scores=True
                )
                
                self.models[model_name] = {
                    'classifier': classifier,
                    'categories': config['categories'],
                    'weight': config['weight'],
                    'model_path': model_path
                }
                
                self.model_weights[model_name] = config['weight']
                self.model_performance[model_name] = {'accuracy': 0.85}  # Default performance
                
                logging.info(f"Loaded ensemble model: {model_name}")
                
            except Exception as e:
                if not config.get('fallback', False):
                    logging.error(f"Failed to load model {model_name}: {e}")
                else:
                    logging.warning(f"Fallback model {model_name} not available: {e}")
    
    async def detect_harmful_content_async(self, text: str) -> Dict[HarmfulContentCategory, EnsembleResult]:
        """Asynchronously detect harmful content across all categories."""
        
        # Run predictions for all models in parallel
        tasks = []
        for model_name, model_info in self.models.items():
            task = self._predict_single_model_async(text, model_name, model_info)
            tasks.append(task)
        
        # Wait for all predictions to complete
        model_predictions = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results by category
        category_results = {}
        
        for category in HarmfulContentCategory:
            relevant_predictions = []
            
            # Collect predictions from models that handle this category
            for i, (model_name, model_info) in enumerate(self.models.items()):
                if category in model_info['categories'] and i < len(model_predictions):
                    prediction = model_predictions[i]
                    if not isinstance(prediction, Exception):
                        relevant_predictions.append((model_name, prediction))
            
            # Ensemble the predictions for this category
            if relevant_predictions:
                category_results[category] = self._ensemble_predictions(
                    text, category, relevant_predictions
                )
        
        return category_results
    
    def detect_harmful_content(self, text: str) -> Dict[HarmfulContentCategory, EnsembleResult]:
        """Synchronously detect harmful content across all categories."""
        
        category_results = {}
        
        # Get predictions from all models
        model_predictions = {}
        for model_name, model_info in self.models.items():
            try:
                prediction = self._predict_single_model(text, model_name, model_info)
                model_predictions[model_name] = prediction
            except Exception as e:
                logging.error(f"Error in model {model_name}: {e}")
                continue
        
        # Combine results by category
        for category in HarmfulContentCategory:
            relevant_predictions = []
            
            # Collect predictions from models that handle this category
            for model_name, model_info in self.models.items():
                if (category in model_info['categories'] and 
                    model_name in model_predictions):
                    
                    prediction = model_predictions[model_name]
                    relevant_predictions.append((model_name, prediction))
            
            # Ensemble the predictions for this category
            if relevant_predictions:
                category_results[category] = self._ensemble_predictions(
                    text, category, relevant_predictions
                )
        
        return category_results
    
    async def _predict_single_model_async(self, text: str, model_name: str, model_info: Dict) -> Dict:
        """Asynchronously predict using a single model."""
        
        loop = asyncio.get_event_loop()
        
        # Run the prediction in a thread pool to avoid blocking
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self._predict_single_model, text, model_name, model_info)
            result = await loop.run_in_executor(None, future.result)
            return result
    
    def _predict_single_model(self, text: str, model_name: str, model_info: Dict) -> Dict:
        """Predict using a single model."""
        
        classifier = model_info['classifier']
        
        try:
            # Get prediction
            results = classifier(text)
            
            # Parse results based on model type
            parsed_results = self._parse_model_results(results, model_name)
            
            return {
                'model_name': model_name,
                'results': parsed_results,
                'categories': model_info['categories'],
                'weight': model_info['weight']
            }
            
        except Exception as e:
            logging.error(f"Error in model {model_name}: {e}")
            return {
                'model_name': model_name,
                'results': {'toxic': 0.0, 'non_toxic': 1.0},
                'categories': model_info['categories'],
                'weight': 0.0  # Zero weight for failed predictions
            }
    
    def _parse_model_results(self, results: List[Dict], model_name: str) -> Dict[str, float]:
        """Parse results from different model types."""
        
        parsed = {}
        
        if isinstance(results, list) and len(results) > 0:
            # Handle nested list structure
            if isinstance(results[0], list):
                results = results[0]
            
            for result in results:
                if isinstance(result, dict) and 'label' in result and 'score' in result:
                    label = result['label'].lower()
                    score = result['score']
                    parsed[label] = score
        
        # Normalize to common format
        if 'toxic' not in parsed and 'non_toxic' not in parsed:
            # Try to find harmful/non-harmful indicators
            harmful_score = 0.0
            
            harmful_keywords = ['toxic', 'hate', 'offensive', 'harmful', 'violence', 'threat']
            for keyword in harmful_keywords:
                for label, score in parsed.items():
                    if keyword in label:
                        harmful_score = max(harmful_score, score)
            
            parsed['toxic'] = harmful_score
            parsed['non_toxic'] = 1.0 - harmful_score
        
        return parsed
    
    def _ensemble_predictions(self, 
                            text: str,
                            category: HarmfulContentCategory, 
                            predictions: List[Tuple[str, Dict]]) -> EnsembleResult:
        """Ensemble predictions from multiple models for a specific category."""
        
        individual_scores = {}
        weighted_scores = []
        reasoning = []
        
        for model_name, prediction in predictions:
            model_weight = self._get_model_weight(model_name, category)
            
            # Extract harmful score
            results = prediction['results']
            harmful_score = results.get('toxic', 0.0)
            
            # Apply category-specific adjustments
            adjusted_score = self._adjust_score_for_category(harmful_score, category, text)
            
            individual_scores[model_name] = adjusted_score
            weighted_scores.append(adjusted_score * model_weight)
            
            if adjusted_score > self.category_thresholds[category]:
                reasoning.append(f"{model_name}: {adjusted_score:.2f} (threshold: {self.category_thresholds[category]:.2f})")
        
        # Calculate ensemble score
        if weighted_scores:
            if self.weighting_strategy == ModelWeight.EQUAL:
                consensus_score = np.mean([score for score, _ in zip(weighted_scores, predictions)])
            elif self.weighting_strategy == ModelWeight.PERFORMANCE_BASED:
                total_weight = sum(self._get_model_weight(model_name, category) 
                                 for model_name, _ in predictions)
                consensus_score = sum(weighted_scores) / total_weight if total_weight > 0 else 0.0
            else:
                consensus_score = np.mean(weighted_scores)
        else:
            consensus_score = 0.0
        
        # Determine if harmful
        is_harmful = consensus_score > self.category_thresholds[category]
        
        return EnsembleResult(
            category=category,
            confidence=consensus_score,
            individual_scores=individual_scores,
            consensus_score=consensus_score,
            is_harmful=is_harmful,
            reasoning=reasoning
        )
    
    def _get_model_weight(self, model_name: str, category: HarmfulContentCategory) -> float:
        """Get the weight for a model for a specific category."""
        
        base_weight = self.model_weights.get(model_name, 1.0)
        
        if self.weighting_strategy == ModelWeight.PERFORMANCE_BASED:
            performance = self.model_performance.get(model_name, {})
            category_performance = performance.get('category_accuracy', {}).get(category.value, 0.85)
            return base_weight * category_performance
        
        return base_weight
    
    def _adjust_score_for_category(self, score: float, category: HarmfulContentCategory, text: str) -> float:
        """Apply category-specific adjustments to the score."""
        
        # Category-specific keyword boosting
        category_keywords = {
            HarmfulContentCategory.VIOLENCE: ['kill', 'murder', 'attack', 'hurt', 'violence', 'weapon'],
            HarmfulContentCategory.SELF_HARM: ['suicide', 'kill myself', 'end it all', 'hurt myself'],
            HarmfulContentCategory.ILLEGAL_ACTIVITIES: ['steal', 'drugs', 'illegal', 'hack', 'fraud'],
            HarmfulContentCategory.HARASSMENT: ['target', 'harass', 'bully', 'stalk'],
            HarmfulContentCategory.EXTREMISM: ['radical', 'overthrow', 'revolution', 'extremist'],
            HarmfulContentCategory.THREATS: ['threat', 'going to hurt', 'will kill', 'watch out'],
            HarmfulContentCategory.CYBERBULLYING: ['loser', 'stupid', 'worthless', 'kill yourself'],
            HarmfulContentCategory.DISCRIMINATION: ['race', 'gender', 'religion', 'discriminate']
        }
        
        text_lower = text.lower()
        keywords = category_keywords.get(category, [])
        
        # Boost score if category-specific keywords are found
        keyword_boost = 0.0
        for keyword in keywords:
            if keyword in text_lower:
                keyword_boost += 0.1
        
        # Apply boost (max 0.3)
        adjusted_score = min(1.0, score + min(keyword_boost, 0.3))
        
        return adjusted_score
    
    def update_model_performance(self, model_name: str, performance: Dict[str, float]):
        """Update performance metrics for a model."""
        
        if model_name in self.model_performance:
            self.model_performance[model_name].update(performance)
        else:
            self.model_performance[model_name] = performance
        
        logging.info(f"Updated performance for {model_name}: {performance}")
    
    def get_model_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status information for all models in the ensemble."""
        
        status = {}
        
        for model_name, model_info in self.models.items():
            status[model_name] = {
                'loaded': True,
                'model_path': model_info['model_path'],
                'categories': [cat.value for cat in model_info['categories']],
                'weight': self.model_weights.get(model_name, 1.0),
                'performance': self.model_performance.get(model_name, {})
            }
        
        return status


# Integration with existing compliance filter
def integrate_ensemble_detector(compliance_filter, ensemble_detector):
    """Integrate ensemble detector with existing compliance filter."""
    
    # Replace the existing hate speech detector with ensemble detector
    original_check = compliance_filter.check_compliance
    
    def enhanced_check_compliance(text, user_context=None, use_cache=True):
        """Enhanced compliance check using ensemble detector."""
        
        # Get original result
        result = original_check(text, user_context, use_cache)
        
        # Get ensemble predictions
        try:
            ensemble_results = ensemble_detector.detect_harmful_content(text)
            
            # Find the highest risk category
            max_risk_score = 0.0
            max_risk_category = None
            
            for category, ensemble_result in ensemble_results.items():
                if ensemble_result.is_harmful and ensemble_result.confidence > max_risk_score:
                    max_risk_score = ensemble_result.confidence
                    max_risk_category = category
            
            # Update result if ensemble found higher risk
            if max_risk_score > result.hate_speech_score:
                result.hate_speech_score = max_risk_score
                result.overall_score = compliance_filter._calculate_overall_score(
                    result.hate_speech_score, result.privacy_score
                )
                result.action = compliance_filter._determine_action(result.overall_score)
                
                # Update reasoning
                if max_risk_category:
                    result.reasoning += f" Enhanced detection flagged {max_risk_category.value} (confidence: {max_risk_score:.2f})"
        
        except Exception as e:
            logging.error(f"Error in ensemble detection: {e}")
        
        return result
    
    # Replace the method
    compliance_filter.check_compliance = enhanced_check_compliance
    
    return compliance_filter