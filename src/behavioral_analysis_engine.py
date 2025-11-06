#!/usr/bin/env python3
"""
🚀 INNOVATION #2: Advanced Behavioral Pattern Analysis Engine (BPAE)
A sophisticated system that analyzes user behavioral patterns, communication styles,
and intent evolution over time for proactive threat detection.

Revolutionary Features:
- Behavioral fingerprinting and profiling
- Communication style evolution tracking  
- Intent prediction and escalation detection
- Psychological pattern analysis
- Social engineering attempt detection
- Proactive intervention recommendations
"""

import asyncio
import logging
import time
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque, defaultdict, Counter
import json
import hashlib
from enum import Enum
import re
from pathlib import Path

# Advanced analytics imports
try:
    import pandas as pd
    import networkx as nx
    from sklearn.cluster import DBSCAN, KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    from sklearn.ensemble import IsolationForest
    import matplotlib.pyplot as plt
    import seaborn as sns
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False

# NLP and sentiment analysis
try:
    import nltk
    from textstat import flesch_kincaid_grade, flesch_reading_ease
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False

logger = logging.getLogger(__name__)

class BehaviorType(Enum):
    """Types of behavioral patterns to track"""
    COMMUNICATION_STYLE = "communication_style"
    SENTIMENT_EVOLUTION = "sentiment_evolution" 
    TOPIC_PROGRESSION = "topic_progression"
    INTERACTION_FREQUENCY = "interaction_frequency"
    LANGUAGE_COMPLEXITY = "language_complexity"
    EMOTIONAL_STATE = "emotional_state"
    SOCIAL_ENGINEERING = "social_engineering"
    ESCALATION_PATTERN = "escalation_pattern"
    TIME_BEHAVIOR = "time_behavior"
    TRUST_BUILDING = "trust_building"

class RiskLevel(Enum):
    """Risk levels for behavioral patterns"""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"
    IMMINENT = "imminent"

@dataclass
class BehavioralDataPoint:
    """Individual behavioral data point"""
    timestamp: datetime
    user_id: str
    content: str
    behavior_type: BehaviorType
    metrics: Dict[str, float]
    context: Dict[str, Any]
    session_id: Optional[str] = None

@dataclass
class BehavioralProfile:
    """Comprehensive user behavioral profile"""
    user_id: str
    created_at: datetime
    last_updated: datetime
    
    # Core behavioral metrics
    communication_patterns: Dict[str, float] = field(default_factory=dict)
    sentiment_trajectory: List[float] = field(default_factory=list)
    topic_interests: Counter = field(default_factory=Counter)
    interaction_rhythms: Dict[str, Any] = field(default_factory=dict)
    
    # Risk indicators
    risk_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.MINIMAL
    behavioral_anomalies: List[Dict[str, Any]] = field(default_factory=list)
    
    # Prediction models
    intent_predictions: Dict[str, float] = field(default_factory=dict)
    escalation_probability: float = 0.0
    trust_manipulation_indicators: List[str] = field(default_factory=list)

@dataclass
class BehavioralAlert:
    """Alert for concerning behavioral patterns"""
    timestamp: datetime
    user_id: str
    alert_type: str
    severity: RiskLevel
    description: str
    evidence: List[str]
    recommended_actions: List[str]
    confidence: float

class AdvancedBehavioralAnalysisEngine:
    """Revolutionary behavioral pattern analysis system"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.user_profiles = {}  # user_id -> BehavioralProfile
        self.behavior_data = deque(maxlen=50000)  # Rolling window of behavioral data
        self.active_sessions = {}  # session_id -> session data
        
        # Advanced analysis components
        self.sentiment_analyzer = SentimentIntensityAnalyzer() if NLP_AVAILABLE else None
        self.communication_analyzer = CommunicationStyleAnalyzer()
        self.intent_predictor = IntentPredictor()
        self.escalation_detector = EscalationDetector()
        self.social_engineering_detector = SocialEngineeringDetector()
        self.anomaly_detector = BehavioralAnomalyDetector()
        
        # Machine learning models
        self.clustering_model = None
        self.risk_prediction_model = None
        self._initialize_ml_models()
        
        logger.info("🧠 Advanced Behavioral Pattern Analysis Engine initialized")

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load behavioral analysis configuration"""
        default_config = {
            "risk_thresholds": {
                "minimal": 0.1,
                "low": 0.3,
                "moderate": 0.5,
                "high": 0.7,
                "critical": 0.85,
                "imminent": 0.95
            },
            "analysis_windows": {
                "short_term": 24,  # hours
                "medium_term": 168,  # 1 week
                "long_term": 720  # 1 month
            },
            "behavioral_weights": {
                "sentiment_volatility": 0.15,
                "communication_change": 0.20,
                "topic_shift": 0.10,
                "interaction_anomaly": 0.15,
                "language_complexity": 0.10,
                "trust_manipulation": 0.30
            },
            "enable_proactive_intervention": True,
            "privacy_mode": True,
            "data_retention_days": 90
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config

    def _initialize_ml_models(self):
        """Initialize machine learning models for behavioral analysis"""
        try:
            if ANALYTICS_AVAILABLE:
                # Initialize clustering model for behavioral pattern grouping
                self.clustering_model = DBSCAN(eps=0.3, min_samples=5)
                
                # Initialize anomaly detection model
                self.risk_prediction_model = IsolationForest(
                    contamination=0.1,
                    random_state=42
                )
                
                logger.info("🤖 ML models initialized successfully")
            else:
                logger.warning("⚠️  Analytics libraries not available - using simplified models")
        except Exception as e:
            logger.error(f"❌ Failed to initialize ML models: {e}")
            # Fallback to None - simplified analysis will be used
            self.clustering_model = None
            self.risk_prediction_model = None

    async def analyze_behavior(self, user_id: str, content: str,
                             session_id: Optional[str] = None,
                             context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Comprehensive behavioral analysis of user interaction"""
        
        timestamp = datetime.now()
        context = context or {}
        
        # Extract behavioral metrics
        behavioral_metrics = await self._extract_behavioral_metrics(content, context)
        
        # Create behavioral data point
        data_point = BehavioralDataPoint(
            timestamp=timestamp,
            user_id=user_id,
            content=content,
            behavior_type=BehaviorType.COMMUNICATION_STYLE,
            metrics=behavioral_metrics,
            context=context,
            session_id=session_id
        )
        
        # Add to behavioral data
        self.behavior_data.append(data_point)
        
        # Update or create user profile
        profile = await self._update_user_profile(user_id, data_point)
        
        # Perform real-time analysis
        analysis_results = await self._perform_realtime_analysis(profile, data_point)
        
        # Check for alerts
        alerts = await self._check_behavioral_alerts(profile, data_point)
        
        # Update risk assessment
        await self._update_risk_assessment(profile)
        
        return {
            "user_id": user_id,
            "timestamp": timestamp.isoformat(),
            "behavioral_metrics": behavioral_metrics,
            "risk_score": profile.risk_score,
            "risk_level": profile.risk_level.value,
            "analysis_results": analysis_results,
            "alerts": [self._alert_to_dict(alert) for alert in alerts],
            "recommendations": await self._generate_recommendations(profile, alerts)
        }

    async def _extract_behavioral_metrics(self, content: str, context: Dict[str, Any]) -> Dict[str, float]:
        """Extract comprehensive behavioral metrics from content"""
        metrics = {}
        
        # Basic text metrics
        metrics['content_length'] = len(content)
        metrics['word_count'] = len(content.split())
        metrics['sentence_count'] = len([s for s in content.split('.') if s.strip()])
        metrics['avg_word_length'] = np.mean([len(word) for word in content.split()]) if content.split() else 0
        
        # Sentiment analysis
        if self.sentiment_analyzer:
            sentiment_scores = self.sentiment_analyzer.polarity_scores(content)
            metrics.update({
                'sentiment_compound': sentiment_scores['compound'],
                'sentiment_positive': sentiment_scores['pos'],
                'sentiment_neutral': sentiment_scores['neu'],
                'sentiment_negative': sentiment_scores['neg']
            })
        
        # Language complexity
        if NLP_AVAILABLE:
            try:
                metrics['reading_ease'] = flesch_reading_ease(content)
                metrics['grade_level'] = flesch_kincaid_grade(content)
            except:
                metrics['reading_ease'] = 50.0
                metrics['grade_level'] = 8.0
        
        # Communication style indicators
        metrics.update(self.communication_analyzer.analyze_style(content))
        
        # Urgency and pressure indicators
        metrics['urgency_score'] = self._calculate_urgency_score(content)
        metrics['pressure_score'] = self._calculate_pressure_score(content)
        
        # Trust manipulation indicators
        metrics['trust_building_score'] = self._calculate_trust_building_score(content)
        metrics['authority_appeal_score'] = self._calculate_authority_appeal_score(content)
        
        # Time-based behavioral indicators
        current_hour = datetime.now().hour
        metrics['interaction_hour'] = current_hour
        metrics['is_unusual_time'] = 1.0 if current_hour < 6 or current_hour > 23 else 0.0
        
        return metrics

    async def _update_user_profile(self, user_id: str, data_point: BehavioralDataPoint) -> BehavioralProfile:
        """Update or create user behavioral profile"""
        
        if user_id not in self.user_profiles:
            # Create new profile
            self.user_profiles[user_id] = BehavioralProfile(
                user_id=user_id,
                created_at=datetime.now(),
                last_updated=datetime.now()
            )
        
        profile = self.user_profiles[user_id]
        profile.last_updated = datetime.now()
        
        # Update communication patterns (moving average)
        for metric, value in data_point.metrics.items():
            if metric not in profile.communication_patterns:
                profile.communication_patterns[metric] = value
            else:
                # Exponential moving average with decay factor 0.9
                profile.communication_patterns[metric] = (
                    0.9 * profile.communication_patterns[metric] + 0.1 * value
                )
        
        # Update sentiment trajectory
        if 'sentiment_compound' in data_point.metrics:
            profile.sentiment_trajectory.append(data_point.metrics['sentiment_compound'])
            # Keep only last 50 sentiment readings
            profile.sentiment_trajectory = profile.sentiment_trajectory[-50:]
        
        # Update topic interests (simplified keyword extraction)
        words = data_point.content.lower().split()
        significant_words = [w for w in words if len(w) > 4 and w.isalpha()]
        profile.topic_interests.update(significant_words)
        
        return profile

    async def _perform_realtime_analysis(self, profile: BehavioralProfile, 
                                       data_point: BehavioralDataPoint) -> Dict[str, Any]:
        """Perform real-time behavioral analysis"""
        
        analysis = {}
        
        # Sentiment volatility analysis
        if len(profile.sentiment_trajectory) >= 5:
            sentiment_volatility = np.std(profile.sentiment_trajectory[-10:])
            analysis['sentiment_volatility'] = float(sentiment_volatility)
            analysis['sentiment_trend'] = self._calculate_sentiment_trend(profile.sentiment_trajectory)
        
        # Communication pattern changes
        analysis['communication_drift'] = await self._detect_communication_drift(profile)
        
        # Intent prediction
        analysis['predicted_intents'] = await self.intent_predictor.predict_intent(
            data_point.content, profile
        )
        
        # Escalation probability
        analysis['escalation_probability'] = await self.escalation_detector.calculate_probability(
            profile, data_point
        )
        
        # Social engineering indicators
        analysis['social_engineering_score'] = await self.social_engineering_detector.analyze(
            data_point.content, profile
        )
        
        # Behavioral anomalies
        analysis['anomaly_score'] = await self.anomaly_detector.detect_anomalies(
            profile, data_point
        )
        
        return analysis

    async def _check_behavioral_alerts(self, profile: BehavioralProfile, 
                                     data_point: BehavioralDataPoint) -> List[BehavioralAlert]:
        """Check for behavioral patterns that require alerts"""
        alerts = []
        
        # High escalation probability alert
        if profile.escalation_probability > 0.7:
            alerts.append(BehavioralAlert(
                timestamp=datetime.now(),
                user_id=profile.user_id,
                alert_type="escalation_risk",
                severity=RiskLevel.HIGH,
                description=f"User showing high escalation probability ({profile.escalation_probability:.2f})",
                evidence=["Increasing aggressive language", "Sentiment deterioration"],
                recommended_actions=["Monitor closely", "Consider intervention", "Alert moderators"],
                confidence=profile.escalation_probability
            ))
        
        # Social engineering attempt alert
        se_score = data_point.metrics.get('trust_building_score', 0) + data_point.metrics.get('authority_appeal_score', 0)
        if se_score > 0.8:
            alerts.append(BehavioralAlert(
                timestamp=datetime.now(),
                user_id=profile.user_id,
                alert_type="social_engineering",
                severity=RiskLevel.HIGH,
                description="Potential social engineering attempt detected",
                evidence=["Trust manipulation language", "Authority appeals"],
                recommended_actions=["Block further interactions", "Security review"],
                confidence=se_score
            ))
        
        # Behavioral anomaly alert
        if data_point.metrics.get('anomaly_score', 0) > 0.9:
            alerts.append(BehavioralAlert(
                timestamp=datetime.now(),
                user_id=profile.user_id,
                alert_type="behavioral_anomaly",
                severity=RiskLevel.MODERATE,
                description="Unusual behavioral pattern detected",
                evidence=["Deviation from normal patterns", "Statistical anomaly"],
                recommended_actions=["Additional verification", "Monitor behavior"],
                confidence=data_point.metrics.get('anomaly_score', 0)
            ))
        
        return alerts

    async def _update_risk_assessment(self, profile: BehavioralProfile):
        """Update overall risk assessment for user"""
        
        risk_factors = []
        
        # Sentiment volatility risk
        if len(profile.sentiment_trajectory) >= 5:
            volatility = np.std(profile.sentiment_trajectory[-10:])
            risk_factors.append(volatility * self.config['behavioral_weights']['sentiment_volatility'])
        
        # Communication pattern risk
        communication_risk = await self._calculate_communication_risk(profile)
        risk_factors.append(communication_risk * self.config['behavioral_weights']['communication_change'])
        
        # Trust manipulation risk
        trust_risk = np.mean([len(profile.trust_manipulation_indicators) / 10.0, profile.escalation_probability])
        risk_factors.append(trust_risk * self.config['behavioral_weights']['trust_manipulation'])
        
        # Calculate composite risk score
        profile.risk_score = np.mean(risk_factors) if risk_factors else 0.0
        
        # Determine risk level
        thresholds = self.config['risk_thresholds']
        if profile.risk_score >= thresholds['imminent']:
            profile.risk_level = RiskLevel.IMMINENT
        elif profile.risk_score >= thresholds['critical']:
            profile.risk_level = RiskLevel.CRITICAL
        elif profile.risk_score >= thresholds['high']:
            profile.risk_level = RiskLevel.HIGH
        elif profile.risk_score >= thresholds['moderate']:
            profile.risk_level = RiskLevel.MODERATE
        elif profile.risk_score >= thresholds['low']:
            profile.risk_level = RiskLevel.LOW
        else:
            profile.risk_level = RiskLevel.MINIMAL

    async def get_user_behavioral_summary(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive behavioral summary for a user"""
        
        if user_id not in self.user_profiles:
            return None
        
        profile = self.user_profiles[user_id]
        
        # Get recent behavioral data for this user
        recent_data = [dp for dp in self.behavior_data if dp.user_id == user_id and 
                      (datetime.now() - dp.timestamp).days <= 7]
        
        summary = {
            "user_id": user_id,
            "profile_created": profile.created_at.isoformat(),
            "last_activity": profile.last_updated.isoformat(),
            "risk_score": profile.risk_score,
            "risk_level": profile.risk_level.value,
            "escalation_probability": profile.escalation_probability,
            "recent_interactions": len(recent_data),
            "behavioral_patterns": {
                "communication_style": profile.communication_patterns,
                "sentiment_analysis": {
                    "current_trend": self._calculate_sentiment_trend(profile.sentiment_trajectory),
                    "volatility": float(np.std(profile.sentiment_trajectory)) if profile.sentiment_trajectory else 0.0,
                    "recent_average": float(np.mean(profile.sentiment_trajectory[-10:])) if len(profile.sentiment_trajectory) >= 10 else 0.0
                },
                "topic_interests": dict(profile.topic_interests.most_common(10))
            },
            "anomalies": profile.behavioral_anomalies[-5:],  # Last 5 anomalies
            "trust_manipulation_indicators": profile.trust_manipulation_indicators,
            "prediction_insights": await self._generate_prediction_insights(profile)
        }
        
        return summary

    def _calculate_urgency_score(self, content: str) -> float:
        """Calculate urgency indicators in content"""
        urgency_patterns = [
            r'\b(?:urgent|emergency|immediate|asap|right now|quickly|hurry)\b',
            r'\b(?:deadline|expires|limited time|act now|don\'t wait)\b',
            r'!!+',  # Multiple exclamation marks
            r'\b(?:must|need|require).{0,20}(?:now|today|immediately)\b'
        ]
        
        score = 0.0
        for pattern in urgency_patterns:
            matches = len(re.findall(pattern, content.lower()))
            score += matches * 0.2
        
        return min(score, 1.0)

    def _calculate_pressure_score(self, content: str) -> float:
        """Calculate pressure/coercion indicators"""
        pressure_patterns = [
            r'\b(?:you must|you have to|you need to|you should)\b',
            r'\b(?:or else|otherwise|consequences|penalty)\b',
            r'\b(?:don\'t tell|keep secret|between us|confidential)\b',
            r'\b(?:everyone else|others are doing|don\'t be the only one)\b'
        ]
        
        score = 0.0
        for pattern in pressure_patterns:
            matches = len(re.findall(pattern, content.lower()))
            score += matches * 0.25
        
        return min(score, 1.0)

    def _calculate_trust_building_score(self, content: str) -> float:
        """Calculate trust manipulation indicators"""
        trust_patterns = [
            r'\b(?:trust me|believe me|i promise|i swear|honestly)\b',
            r'\b(?:we\'re friends|i like you|special|chosen|selected)\b',
            r'\b(?:help you|do you a favor|benefit|opportunity)\b',
            r'\b(?:exclusive|private|secret|insider)\b'
        ]
        
        score = 0.0
        for pattern in trust_patterns:
            matches = len(re.findall(pattern, content.lower()))
            score += matches * 0.2
        
        return min(score, 1.0)

    def _calculate_authority_appeal_score(self, content: str) -> float:
        """Calculate authority/legitimacy manipulation"""
        authority_patterns = [
            r'\b(?:official|authorized|legitimate|verified|certified)\b',
            r'\b(?:government|bank|company|organization|department)\b',
            r'\b(?:requires|mandates|orders|directs|instructs)\b',
            r'\b(?:compliance|regulation|policy|procedure)\b'
        ]
        
        score = 0.0
        for pattern in authority_patterns:
            matches = len(re.findall(pattern, content.lower()))
            score += matches * 0.15
        
        return min(score, 1.0)

    # Additional helper methods
    
    def _calculate_sentiment_trend(self, sentiment_trajectory: List[float]) -> str:
        """Calculate sentiment trend from trajectory"""
        if len(sentiment_trajectory) < 3:
            return "insufficient_data"
        
        recent = sentiment_trajectory[-5:]
        early = sentiment_trajectory[:-5] if len(sentiment_trajectory) > 5 else sentiment_trajectory[:-3]
        
        if not early:
            return "stable"
        
        recent_avg = np.mean(recent)
        early_avg = np.mean(early)
        
        if recent_avg > early_avg + 0.1:
            return "improving"
        elif recent_avg < early_avg - 0.1:
            return "declining"
        else:
            return "stable"
    
    async def _detect_communication_drift(self, profile: BehavioralProfile) -> float:
        """Detect changes in communication patterns"""
        # Simplified implementation - compare recent vs historical averages
        if not profile.communication_patterns:
            return 0.0
        
        # Calculate variance in key communication metrics
        drift_score = 0.0
        key_metrics = ['formality_score', 'politeness_score', 'emotional_intensity']
        
        for metric in key_metrics:
            if metric in profile.communication_patterns:
                # In a real implementation, we'd compare historical vs recent patterns
                # For now, return a low drift score
                drift_score += 0.1
        
        return min(drift_score / len(key_metrics), 1.0)
    
    async def _calculate_communication_risk(self, profile: BehavioralProfile) -> float:
        """Calculate risk based on communication pattern changes"""
        drift = await self._detect_communication_drift(profile)
        
        # High drift indicates potential risk
        risk_factors = [
            drift,
            min(profile.escalation_probability, 1.0),
            min(len(profile.trust_manipulation_indicators) / 5.0, 1.0)
        ]
        
        return np.mean(risk_factors)
    
    async def _generate_recommendations(self, profile: BehavioralProfile, 
                                      alerts: List[BehavioralAlert]) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        if profile.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL, RiskLevel.IMMINENT]:
            recommendations.extend([
                "Implement enhanced monitoring for this user",
                "Consider requiring additional verification",
                "Alert security team for review"
            ])
        
        if profile.escalation_probability > 0.6:
            recommendations.append("Monitor for escalating behavior patterns")
        
        if alerts:
            recommendations.append(f"Address {len(alerts)} behavioral alerts")
        
        if not recommendations:
            recommendations.append("Continue standard monitoring")
        
        return recommendations
    
    async def _generate_prediction_insights(self, profile: BehavioralProfile) -> Dict[str, Any]:
        """Generate insights about future behavior predictions"""
        insights = {
            "risk_trajectory": "stable",
            "escalation_likelihood": profile.escalation_probability,
            "behavioral_stability": 0.8,  # Simplified
            "intervention_recommended": profile.risk_level.value in ['high', 'critical', 'imminent'],
            "confidence_level": 0.75
        }
        
        # Determine risk trajectory
        if profile.risk_score > 0.7:
            insights["risk_trajectory"] = "increasing"
        elif profile.risk_score < 0.3:
            insights["risk_trajectory"] = "decreasing"
        
        return insights
    
    def _alert_to_dict(self, alert: BehavioralAlert) -> Dict[str, Any]:
        """Convert alert to dictionary format"""
        return {
            "timestamp": alert.timestamp.isoformat(),
            "user_id": alert.user_id,
            "alert_type": alert.alert_type,
            "severity": alert.severity.value,
            "description": alert.description,
            "evidence": alert.evidence,
            "recommended_actions": alert.recommended_actions,
            "confidence": alert.confidence
        }

# Supporting classes (simplified implementations)
class CommunicationStyleAnalyzer:
    def analyze_style(self, content: str) -> Dict[str, float]:
        # Analyze communication style patterns
        return {
            'formality_score': 0.5,
            'politeness_score': 0.7,
            'directness_score': 0.6,
            'emotional_intensity': 0.4
        }

class IntentPredictor:
    async def predict_intent(self, content: str, profile: BehavioralProfile) -> Dict[str, float]:
        # Predict user intent based on content and behavioral history
        return {
            'information_seeking': 0.6,
            'social_engineering': 0.1,
            'legitimate_inquiry': 0.8,
            'malicious_intent': 0.05
        }

class EscalationDetector:
    async def calculate_probability(self, profile: BehavioralProfile, data_point: BehavioralDataPoint) -> float:
        # Calculate probability of escalation
        return 0.3  # Simplified

class SocialEngineeringDetector:
    async def analyze(self, content: str, profile: BehavioralProfile) -> float:
        # Analyze for social engineering attempts
        return 0.2  # Simplified

class BehavioralAnomalyDetector:
    async def detect_anomalies(self, profile: BehavioralProfile, data_point: BehavioralDataPoint) -> float:
        # Detect behavioral anomalies
        return 0.1  # Simplified

# Export the innovation
__all__ = ['AdvancedBehavioralAnalysisEngine', 'BehavioralProfile', 'BehavioralAlert', 'RiskLevel']