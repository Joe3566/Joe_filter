"""
Advanced Training System for LLM Compliance Filter

This module provides comprehensive training capabilities to improve harmful content detection,
including data collection, model fine-tuning, and active learning.
"""

import json
import os
import time
import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import pandas as pd
import numpy as np

try:
    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification,
        TrainingArguments, Trainer, EarlyStoppingCallback
    )
    from datasets import Dataset
    import torch
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support
    from sklearn.model_selection import train_test_split
    TRAINING_AVAILABLE = True
except ImportError:
    logging.warning("Training dependencies not available. Install with: pip install torch transformers datasets scikit-learn")
    TRAINING_AVAILABLE = False


class HarmfulContentCategory(Enum):
    """Categories of harmful content for training and detection."""
    HATE_SPEECH = "hate_speech"
    TOXICITY = "toxicity"
    VIOLENCE = "violence"
    SELF_HARM = "self_harm"
    HARASSMENT = "harassment"
    ILLEGAL_ACTIVITIES = "illegal_activities"
    ADULT_CONTENT = "adult_content"
    MISINFORMATION = "misinformation"
    EXTREMISM = "extremism"
    CYBERBULLYING = "cyberbullying"
    THREATS = "threats"
    DISCRIMINATION = "discrimination"


@dataclass
class TrainingExample:
    """A single training example for harmful content detection."""
    text: str
    label: int  # 0 = safe, 1 = harmful
    category: HarmfulContentCategory
    confidence: float
    source: str
    timestamp: str
    verified: bool = False
    user_feedback: Optional[str] = None


@dataclass
class ModelPerformance:
    """Model performance metrics."""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    category_performance: Dict[str, Dict[str, float]]
    training_loss: float
    validation_loss: float
    epoch: int
    timestamp: str


class TrainingDataCollector:
    """Collects and manages training data for harmful content detection."""
    
    def __init__(self, data_dir: str = "./training_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize data storage files
        self.examples_file = self.data_dir / "training_examples.jsonl"
        self.performance_file = self.data_dir / "model_performance.jsonl"
        
        # Load existing data
        self.examples = self._load_examples()
        self.performance_history = self._load_performance_history()
        
    def add_example(self, 
                   text: str, 
                   is_harmful: bool, 
                   category: HarmfulContentCategory,
                   confidence: float = 1.0,
                   source: str = "manual",
                   verified: bool = False) -> str:
        """Add a new training example."""
        
        example = TrainingExample(
            text=text,
            label=1 if is_harmful else 0,
            category=category,
            confidence=confidence,
            source=source,
            timestamp=datetime.now().isoformat(),
            verified=verified
        )
        
        # Generate unique ID
        example_id = hashlib.md5(f"{text}{category.value}{datetime.now()}".encode()).hexdigest()[:12]
        self.examples[example_id] = example
        
        # Save to file
        self._save_example(example_id, example)
        
        logging.info(f"Added training example: {example_id} ({category.value}, harmful={is_harmful})")
        return example_id
    
    def add_batch_examples(self, examples: List[Dict[str, Any]]) -> List[str]:
        """Add multiple training examples at once."""
        example_ids = []
        
        for ex in examples:
            example_id = self.add_example(
                text=ex['text'],
                is_harmful=ex['is_harmful'],
                category=HarmfulContentCategory(ex['category']),
                confidence=ex.get('confidence', 1.0),
                source=ex.get('source', 'batch'),
                verified=ex.get('verified', False)
            )
            example_ids.append(example_id)
        
        return example_ids
    
    def get_training_data(self, 
                         categories: Optional[List[HarmfulContentCategory]] = None,
                         min_confidence: float = 0.7,
                         verified_only: bool = False) -> Tuple[List[str], List[int]]:
        """Get training data filtered by criteria."""
        
        texts = []
        labels = []
        
        for example in self.examples.values():
            # Apply filters
            if categories and example.category not in categories:
                continue
            if example.confidence < min_confidence:
                continue
            if verified_only and not example.verified:
                continue
            
            texts.append(example.text)
            labels.append(example.label)
        
        return texts, labels
    
    def get_category_distribution(self) -> Dict[str, Dict[str, int]]:
        """Get distribution of examples by category and label."""
        distribution = {}
        
        for example in self.examples.values():
            category = example.category.value
            if category not in distribution:
                distribution[category] = {"safe": 0, "harmful": 0}
            
            label_key = "harmful" if example.label == 1 else "safe"
            distribution[category][label_key] += 1
        
        return distribution
    
    def _load_examples(self) -> Dict[str, TrainingExample]:
        """Load existing training examples from file."""
        examples = {}
        
        if self.examples_file.exists():
            try:
                with open(self.examples_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        data = json.loads(line.strip())
                        example_id = data.pop('id')
                        data['category'] = HarmfulContentCategory(data['category'])
                        examples[example_id] = TrainingExample(**data)
            except Exception as e:
                logging.error(f"Error loading training examples: {e}")
        
        return examples
    
    def _save_example(self, example_id: str, example: TrainingExample):
        """Save a single example to file."""
        try:
            with open(self.examples_file, 'a', encoding='utf-8') as f:
                data = asdict(example)
                data['id'] = example_id
                data['category'] = example.category.value
                f.write(json.dumps(data) + '\n')
        except Exception as e:
            logging.error(f"Error saving training example: {e}")
    
    def _load_performance_history(self) -> List[ModelPerformance]:
        """Load model performance history."""
        history = []
        
        if self.performance_file.exists():
            try:
                with open(self.performance_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        data = json.loads(line.strip())
                        history.append(ModelPerformance(**data))
            except Exception as e:
                logging.error(f"Error loading performance history: {e}")
        
        return history


class HarmfulContentTrainer:
    """Trains and fine-tunes models for harmful content detection."""
    
    def __init__(self, 
                 base_model: str = "unitary/toxic-bert",
                 training_dir: str = "./model_training",
                 data_collector: Optional[TrainingDataCollector] = None):
        
        if not TRAINING_AVAILABLE:
            raise ImportError("Training dependencies not available")
        
        self.base_model = base_model
        self.training_dir = Path(training_dir)
        self.training_dir.mkdir(exist_ok=True)
        
        self.data_collector = data_collector or TrainingDataCollector()
        
        # Initialize model components
        self.tokenizer = None
        self.model = None
        self.trainer = None
        
    def prepare_training_data(self, 
                            test_size: float = 0.2,
                            categories: Optional[List[HarmfulContentCategory]] = None,
                            min_confidence: float = 0.8) -> Tuple[Dataset, Dataset]:
        """Prepare training and validation datasets."""
        
        # Get training data
        texts, labels = self.data_collector.get_training_data(
            categories=categories,
            min_confidence=min_confidence,
            verified_only=True
        )
        
        if len(texts) < 50:
            logging.warning(f"Only {len(texts)} training examples available. Consider adding more data.")
        
        # Split into train/validation
        train_texts, val_texts, train_labels, val_labels = train_test_split(
            texts, labels, test_size=test_size, random_state=42, stratify=labels
        )
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.base_model)
        
        # Tokenize data
        train_encodings = self.tokenizer(train_texts, truncation=True, padding=True, max_length=512)
        val_encodings = self.tokenizer(val_texts, truncation=True, padding=True, max_length=512)
        
        # Create datasets
        train_dataset = Dataset.from_dict({
            'input_ids': train_encodings['input_ids'],
            'attention_mask': train_encodings['attention_mask'],
            'labels': train_labels
        })
        
        val_dataset = Dataset.from_dict({
            'input_ids': val_encodings['input_ids'],
            'attention_mask': val_encodings['attention_mask'],
            'labels': val_labels
        })
        
        return train_dataset, val_dataset
    
    def fine_tune_model(self, 
                       train_dataset: Dataset,
                       val_dataset: Dataset,
                       output_dir: str = None,
                       epochs: int = 3,
                       learning_rate: float = 2e-5,
                       batch_size: int = 16) -> ModelPerformance:
        """Fine-tune the model on training data."""
        
        if output_dir is None:
            output_dir = self.training_dir / f"fine_tuned_{int(time.time())}"
        
        # Load model
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.base_model, 
            num_labels=2
        )
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=str(output_dir),
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            warmup_steps=500,
            weight_decay=0.01,
            learning_rate=learning_rate,
            logging_dir=str(output_dir / "logs"),
            logging_steps=10,
            evaluation_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            save_total_limit=3,
            seed=42
        )
        
        # Initialize trainer
        self.trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            compute_metrics=self._compute_metrics,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
        )
        
        # Train the model
        logging.info("Starting model fine-tuning...")
        training_result = self.trainer.train()
        
        # Evaluate the model
        eval_result = self.trainer.evaluate()
        
        # Save the model
        self.trainer.save_model(str(output_dir))
        self.tokenizer.save_pretrained(str(output_dir))
        
        # Create performance metrics
        performance = ModelPerformance(
            accuracy=eval_result['eval_accuracy'],
            precision=eval_result['eval_precision'],
            recall=eval_result['eval_recall'],
            f1_score=eval_result['eval_f1'],
            category_performance={},  # TODO: Add category-specific metrics
            training_loss=training_result.training_loss,
            validation_loss=eval_result['eval_loss'],
            epoch=epochs,
            timestamp=datetime.now().isoformat()
        )
        
        # Save performance
        self._save_performance(performance)
        
        logging.info(f"Model fine-tuning completed. F1 Score: {performance.f1_score:.4f}")
        return performance
    
    def evaluate_model(self, test_texts: List[str], test_labels: List[int]) -> Dict[str, float]:
        """Evaluate the model on test data."""
        if not self.model or not self.tokenizer:
            raise ValueError("Model not loaded. Train or load a model first.")
        
        # Tokenize test data
        test_encodings = self.tokenizer(test_texts, truncation=True, padding=True, max_length=512)
        test_dataset = Dataset.from_dict({
            'input_ids': test_encodings['input_ids'],
            'attention_mask': test_encodings['attention_mask'],
            'labels': test_labels
        })
        
        # Evaluate
        eval_result = self.trainer.evaluate(test_dataset)
        
        return {
            'accuracy': eval_result['eval_accuracy'],
            'precision': eval_result['eval_precision'],
            'recall': eval_result['eval_recall'],
            'f1_score': eval_result['eval_f1'],
            'loss': eval_result['eval_loss']
        }
    
    def _compute_metrics(self, eval_pred):
        """Compute metrics for evaluation."""
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        
        precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average='weighted')
        accuracy = accuracy_score(labels, predictions)
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
    
    def _save_performance(self, performance: ModelPerformance):
        """Save performance metrics to file."""
        try:
            with open(self.data_collector.performance_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(asdict(performance)) + '\n')
        except Exception as e:
            logging.error(f"Error saving performance: {e}")


class ActiveLearningSystem:
    """Implements active learning to continuously improve the model."""
    
    def __init__(self, 
                 compliance_filter,
                 data_collector: TrainingDataCollector,
                 uncertainty_threshold: float = 0.6):
        
        self.compliance_filter = compliance_filter
        self.data_collector = data_collector
        self.uncertainty_threshold = uncertainty_threshold
        
        # Track predictions for active learning
        self.uncertain_predictions = []
    
    def should_request_feedback(self, result) -> bool:
        """Determine if we should request user feedback for this result."""
        
        # Request feedback for uncertain predictions
        if hasattr(result, 'hate_speech_result') and result.hate_speech_result:
            confidence = result.hate_speech_result.confidence
            
            # If confidence is around threshold, it's uncertain
            if abs(confidence - 0.5) < self.uncertainty_threshold:
                return True
        
        # Request feedback for borderline overall scores
        if abs(result.overall_score - 0.5) < 0.2:
            return True
        
        return False
    
    def collect_feedback(self, 
                        text: str, 
                        result,
                        user_feedback: str,
                        is_correct: bool,
                        suggested_category: Optional[HarmfulContentCategory] = None):
        """Collect user feedback for active learning."""
        
        if not is_correct and suggested_category:
            # Add as training example
            is_harmful = suggested_category != HarmfulContentCategory.HATE_SPEECH  # Adjust logic
            
            self.data_collector.add_example(
                text=text,
                is_harmful=is_harmful,
                category=suggested_category,
                confidence=0.9,  # High confidence from human feedback
                source="user_feedback",
                verified=True
            )
            
            logging.info(f"Added feedback-based training example: {suggested_category.value}")
    
    def suggest_examples_for_labeling(self, n_examples: int = 10) -> List[str]:
        """Suggest examples that would be most valuable to label."""
        
        # For now, return examples with uncertain predictions
        # In a full implementation, this would use uncertainty sampling
        uncertain_texts = [pred['text'] for pred in self.uncertain_predictions[-n_examples:]]
        return uncertain_texts


# Pre-defined harmful content examples for initial training
HARMFUL_CONTENT_EXAMPLES = {
    HarmfulContentCategory.VIOLENCE: [
        ("I want to hurt someone badly", True),
        ("Let's discuss conflict resolution", False),
        ("How to build weapons", True),
        ("History of warfare", False)
    ],
    
    HarmfulContentCategory.SELF_HARM: [
        ("I want to hurt myself", True),
        ("I'm feeling sad today", False),
        ("Ways to end it all", True),
        ("Mental health resources", False)
    ],
    
    HarmfulContentCategory.ILLEGAL_ACTIVITIES: [
        ("How to steal credit cards", True),
        ("How to protect against fraud", False),
        ("Making illegal drugs", True),
        ("Pharmaceutical research", False)
    ],
    
    HarmfulContentCategory.HARASSMENT: [
        ("Let's target this person", True),
        ("Let's support this person", False),
        ("Make them suffer", True),
        ("Help them succeed", False)
    ],
    
    HarmfulContentCategory.EXTREMISM: [
        ("Join our radical group", True),
        ("Join our community group", False),
        ("Overthrow the government", True),
        ("Vote in elections", False)
    ]
}