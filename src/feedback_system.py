"""
Feedback System Module

Handles feedback for compliance violations and provides mechanisms
to improve filter accuracy over time.
"""

import json
import logging
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

from .compliance_filter import ComplianceResult, ComplianceAction


class FeedbackType(Enum):
    """Types of feedback that can be provided."""
    FALSE_POSITIVE = "false_positive"  # Filter incorrectly flagged safe content
    FALSE_NEGATIVE = "false_negative"  # Filter missed harmful content
    CORRECT_POSITIVE = "correct_positive"  # Filter correctly flagged harmful content
    CORRECT_NEGATIVE = "correct_negative"  # Filter correctly allowed safe content
    THRESHOLD_SUGGESTION = "threshold_suggestion"  # User suggests threshold adjustment
    MODEL_IMPROVEMENT = "model_improvement"  # General model improvement suggestion


@dataclass
class FeedbackEntry:
    """Represents a single feedback entry."""
    feedback_id: str
    feedback_type: FeedbackType
    original_text: str
    compliance_result: ComplianceResult
    user_assessment: str
    suggested_action: Optional[ComplianceAction]
    confidence: float  # User's confidence in their assessment
    context: Dict[str, Any]
    timestamp: str
    user_id: Optional[str] = None
    processed: bool = False
    notes: Optional[str] = None


class FeedbackSystem:
    """
    System for collecting and processing feedback to improve compliance filtering.
    
    Features:
    - Collect various types of feedback
    - Store feedback in structured format
    - Analyze feedback patterns
    - Generate improvement suggestions
    - Track feedback processing status
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the feedback system.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.feedback_config = self.config.get('feedback', {})
        
        # Configuration
        self.enable_feedback = self.feedback_config.get('enable_feedback', True)
        self.feedback_threshold = self.feedback_config.get('feedback_threshold', 0.1)
        self.store_feedback = self.feedback_config.get('store_feedback', True)
        self.feedback_file = self.feedback_config.get('feedback_file', './logs/feedback.jsonl')
        
        # In-memory feedback storage
        self.feedback_entries: List[FeedbackEntry] = []
        
        # Statistics
        self.feedback_stats = {
            'total_entries': 0,
            'by_type': {ftype.value: 0 for ftype in FeedbackType},
            'processed_count': 0,
            'average_confidence': 0.0
        }
        
        # Load existing feedback if file exists
        if self.store_feedback:
            self._load_feedback_from_file()
        
        logging.info("FeedbackSystem initialized")
    
    def submit_feedback(
        self,
        feedback_type: FeedbackType,
        original_text: str,
        compliance_result: ComplianceResult,
        user_assessment: str,
        confidence: float = 0.8,
        suggested_action: Optional[ComplianceAction] = None,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = None
    ) -> str:
        """
        Submit feedback about a compliance decision.
        
        Args:
            feedback_type: Type of feedback
            original_text: The original text that was checked
            compliance_result: The original compliance result
            user_assessment: User's assessment of the content
            confidence: User's confidence in their assessment (0.0-1.0)
            suggested_action: What action should have been taken
            user_id: Optional user identifier
            context: Additional context information
            notes: Optional notes from the user
            
        Returns:
            Feedback ID for tracking
        """
        if not self.enable_feedback:
            logging.warning("Feedback submission disabled")
            return ""
        
        feedback_id = f"fb_{int(time.time())}_{len(self.feedback_entries)}"
        
        feedback_entry = FeedbackEntry(
            feedback_id=feedback_id,
            feedback_type=feedback_type,
            original_text=original_text,
            compliance_result=compliance_result,
            user_assessment=user_assessment,
            suggested_action=suggested_action,
            confidence=confidence,
            context=context or {},
            timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
            user_id=user_id,
            notes=notes
        )
        
        self.feedback_entries.append(feedback_entry)
        self._update_stats(feedback_entry)
        
        # Store to file if enabled
        if self.store_feedback:
            self._save_feedback_to_file(feedback_entry)
        
        logging.info(f"Feedback submitted: {feedback_id} ({feedback_type.value})")
        return feedback_id
    
    def analyze_feedback_patterns(self) -> Dict[str, Any]:
        """
        Analyze feedback patterns to identify improvement opportunities.
        
        Returns:
            Dictionary with analysis results
        """
        if not self.feedback_entries:
            return {"message": "No feedback data available for analysis"}
        
        analysis = {
            'summary': self.feedback_stats.copy(),
            'false_positive_rate': 0.0,
            'false_negative_rate': 0.0,
            'threshold_suggestions': [],
            'model_performance': {},
            'common_issues': []
        }
        
        total_judgments = len([f for f in self.feedback_entries 
                              if f.feedback_type in [FeedbackType.FALSE_POSITIVE, 
                                                   FeedbackType.FALSE_NEGATIVE,
                                                   FeedbackType.CORRECT_POSITIVE,
                                                   FeedbackType.CORRECT_NEGATIVE]])
        
        if total_judgments > 0:
            false_positives = len([f for f in self.feedback_entries if f.feedback_type == FeedbackType.FALSE_POSITIVE])
            false_negatives = len([f for f in self.feedback_entries 
                                   if f.feedback_type == FeedbackType.FALSE_NEGATIVE])
            
            analysis['false_positive_rate'] = false_positives / total_judgments
            analysis['false_negative_rate'] = false_negatives / total_judgments
        
        # Analyze threshold suggestions
        threshold_feedback = [f for f in self.feedback_entries 
                              if f.feedback_type == FeedbackType.THRESHOLD_SUGGESTION]
        
        if threshold_feedback:
            # Group by suggested thresholds and find common suggestions
            threshold_suggestions = {}
            for feedback in threshold_feedback:
                suggested = feedback.context.get('suggested_threshold', 'unknown')
                if suggested not in threshold_suggestions:
                    threshold_suggestions[suggested] = []
                threshold_suggestions[suggested].append(feedback)
            
            analysis['threshold_suggestions'] = [
                {
                    'threshold': threshold,
                    'count': len(entries),
                    'average_confidence': sum(e.confidence for e in entries) / len(entries)
                }
                for threshold, entries in threshold_suggestions.items()
            ]
        
        # Identify common issues
        common_issues = self._identify_common_issues()
        analysis['common_issues'] = common_issues
        
        return analysis
    
    def _identify_common_issues(self) -> List[Dict[str, Any]]:
        """Identify common issues from feedback."""
        issues = []
        
        # Analyze false positives by violation type
        false_positives = [f for f in self.feedback_entries 
                         if f.feedback_type == FeedbackType.FALSE_POSITIVE]
        
        if false_positives:
            privacy_fps = [f for f in false_positives 
                          if getattr(f.compliance_result, 'privacy_violations', False)]
            hate_speech_fps = [f for f in false_positives 
                             if getattr(f.compliance_result, 'hate_speech_result', None) and 
                             getattr(f.compliance_result.hate_speech_result, 'is_hate_speech', False)]
            
            if len(privacy_fps) > len(false_positives) * 0.3:  # More than 30% of FPs
                issues.append({
                    'type': 'privacy_detection_too_sensitive',
                    'count': len(privacy_fps),
                    'description': 'Privacy detection may be too sensitive',
                    'suggestion': 'Consider adjusting privacy detection thresholds'
                })
            
            if len(hate_speech_fps) > len(false_positives) * 0.3:
                issues.append({
                    'type': 'hate_speech_detection_too_sensitive',
                    'count': len(hate_speech_fps),
                    'description': 'Hate speech detection may be too sensitive',
                    'suggestion': 'Consider adjusting hate speech model threshold'
                })
        
        return issues
    
    def generate_improvement_suggestions(self) -> List[Dict[str, Any]]:
        """Generate specific suggestions for improving the filter."""
        suggestions = []
        analysis = self.analyze_feedback_patterns()
        
        # Threshold adjustment suggestions
        if analysis['false_positive_rate'] > 0.2:  # High false positive rate
            suggestions.append({
                'type': 'threshold_adjustment',
                'priority': 'high',
                'description': 'High false positive rate detected',
                'action': 'Consider increasing block/warn thresholds',
                'current_fp_rate': analysis['false_positive_rate']
            })
        
        if analysis['false_negative_rate'] > 0.1:  # High false negative rate
            suggestions.append({
                'type': 'threshold_adjustment',
                'priority': 'critical',
                'description': 'High false negative rate detected',
                'action': 'Consider decreasing block/warn thresholds',
                'current_fn_rate': analysis['false_negative_rate']
            })
        
        # Model-specific suggestions
        for issue in analysis.get('common_issues', []):
            suggestions.append({
                'type': 'model_tuning',
                'priority': 'medium',
                'description': issue['description'],
                'action': issue['suggestion'],
                'affected_count': issue['count']
            })
        
        return suggestions
    
    def get_feedback_by_type(self, feedback_type: FeedbackType) -> List[FeedbackEntry]:
        """Get all feedback entries of a specific type."""
        return [f for f in self.feedback_entries if f.feedback_type == feedback_type]
    
    def mark_feedback_processed(self, feedback_ids: List[str]):
        """Mark feedback entries as processed."""
        processed_count = 0
        for feedback in self.feedback_entries:
            if feedback.feedback_id in feedback_ids and not feedback.processed:
                feedback.processed = True
                processed_count += 1
        
        self.feedback_stats['processed_count'] += processed_count
        logging.info(f"Marked {processed_count} feedback entries as processed")
    
    def export_feedback_for_training(self, output_file: str, include_processed: bool = False):
        """Export feedback data in format suitable for model training."""
        training_data = []
        
        for feedback in self.feedback_entries:
            if not include_processed and feedback.processed:
                continue
            
            # Convert to training format
            training_entry = {
                'text': feedback.original_text,
                'original_prediction': {
                    'action': feedback.compliance_result.action.value,
                    'overall_score': feedback.compliance_result.overall_score,
                    'hate_speech_score': feedback.compliance_result.hate_speech_score,
                    'privacy_score': feedback.compliance_result.privacy_score
                },
                'user_label': feedback.user_assessment,
                'feedback_type': feedback.feedback_type.value,
                'confidence': feedback.confidence,
                'suggested_action': feedback.suggested_action.value if feedback.suggested_action else None
            }
            training_data.append(training_entry)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for entry in training_data:
                f.write(json.dumps(entry) + '\n')
        
        logging.info(f"Exported {len(training_data)} feedback entries to {output_file}")
    
    def _update_stats(self, feedback_entry: FeedbackEntry):
        """Update internal statistics."""
        self.feedback_stats['total_entries'] += 1
        self.feedback_stats['by_type'][feedback_entry.feedback_type.value] += 1
        
        # Update average confidence
        total_confidence = (self.feedback_stats['average_confidence'] * 
                          (self.feedback_stats['total_entries'] - 1) + 
                          feedback_entry.confidence)
        self.feedback_stats['average_confidence'] = total_confidence / self.feedback_stats['total_entries']
    
    def _save_feedback_to_file(self, feedback_entry: FeedbackEntry):
        """Save feedback entry to file."""
        try:
            # Create directory if it doesn't exist
            Path(self.feedback_file).parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to JSON-serializable format
            entry_dict = asdict(feedback_entry)
            entry_dict['compliance_result'] = asdict(feedback_entry.compliance_result)
            
            # Handle enum serialization
            entry_dict['feedback_type'] = feedback_entry.feedback_type.value
            entry_dict['compliance_result']['action'] = feedback_entry.compliance_result.action.value
            if feedback_entry.suggested_action:
                entry_dict['suggested_action'] = feedback_entry.suggested_action.value
            
            with open(self.feedback_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry_dict) + '\n')
                
        except Exception as e:
            logging.error(f"Failed to save feedback to file: {e}")
    
    def _load_feedback_from_file(self):
        """Load existing feedback from file."""
        if not Path(self.feedback_file).exists():
            return
        
        try:
            with open(self.feedback_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        entry_dict = json.loads(line)
                        # Note: This is a simplified loading - full deserialization 
                        # would require more complex handling of nested objects
                        self.feedback_stats['total_entries'] += 1
                        feedback_type = entry_dict.get('feedback_type', 'unknown')
                        if feedback_type in self.feedback_stats['by_type']:
                            self.feedback_stats['by_type'][feedback_type] += 1
                            
                    except json.JSONDecodeError as e:
                        logging.warning(f"Failed to parse feedback line {line_num}: {e}")
                        
            logging.info(f"Loaded feedback statistics from {self.feedback_file}")
            
        except Exception as e:
            logging.error(f"Failed to load feedback from file: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current feedback statistics."""
        return self.feedback_stats.copy()
    
    def should_request_feedback(self, compliance_result: ComplianceResult) -> bool:
        """
        Determine if feedback should be requested based on the compliance result.
        
        Args:
            compliance_result: The compliance check result
            
        Returns:
            True if feedback should be requested
        """
        if not self.enable_feedback:
            return False
        
        # Request feedback for borderline cases
        threshold = self.feedback_threshold
        score = compliance_result.overall_score
        
        # Cases where we should ask for feedback:
        # 1. Score is close to thresholds
        # 2. High uncertainty (score around 0.5)
        # 3. Mixed signals (high hate speech but low privacy, or vice versa)
        
        if abs(score - 0.5) < threshold:  # High uncertainty
            return True
        
        if abs(score - self.config.get('compliance', {}).get('thresholds', {}).get('block_threshold', 0.7)) < threshold:
            return True
            
        if abs(score - self.config.get('compliance', {}).get('thresholds', {}).get('warn_threshold', 0.5)) < threshold:
            return True
        
        # Mixed signals
        hate_score = compliance_result.hate_speech_score
        privacy_score = compliance_result.privacy_score
        if abs(hate_score - privacy_score) > 0.4:  # Large difference
            return True
        
        return False
    
    def get_precision_recall_stats(self) -> Dict[str, float]:
        """
        Calculate precision and recall metrics from feedback.
        
        Returns:
            Dictionary with precision, recall, and F1 score
        """
        if not self.feedback_entries:
            return {'precision': 0.0, 'recall': 0.0, 'f1_score': 0.0}
        
        # True positives: correct detections of violations
        true_positives = len([f for f in self.feedback_entries 
                            if f.feedback_type == FeedbackType.CORRECT_POSITIVE])
        
        # False positives: incorrect flags
        false_positives = len([f for f in self.feedback_entries 
                             if f.feedback_type == FeedbackType.FALSE_POSITIVE])
        
        # False negatives: missed violations
        false_negatives = len([f for f in self.feedback_entries 
                             if f.feedback_type == FeedbackType.FALSE_NEGATIVE])
        
        # Calculate metrics
        precision = (true_positives / (true_positives + false_positives) 
                    if (true_positives + false_positives) > 0 else 0.0)
        
        recall = (true_positives / (true_positives + false_negatives) 
                 if (true_positives + false_negatives) > 0 else 0.0)
        
        f1_score = (2 * precision * recall / (precision + recall) 
                   if (precision + recall) > 0 else 0.0)
        
        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives
        }
    
    def get_mislabeled_hashes(self) -> List[str]:
        """
        Get text hashes of mislabeled samples for retraining.
        
        Returns:
            List of text hashes (SHA256) that were mislabeled
        """
        import hashlib
        
        mislabeled = []
        for feedback in self.feedback_entries:
            if feedback.feedback_type in [FeedbackType.FALSE_POSITIVE, FeedbackType.FALSE_NEGATIVE]:
                text_hash = hashlib.sha256(feedback.original_text.encode('utf-8')).hexdigest()
                mislabeled.append({
                    'text_hash': text_hash,
                    'feedback_type': feedback.feedback_type.value,
                    'confidence': feedback.confidence,
                    'timestamp': feedback.timestamp
                })
        
        return mislabeled
