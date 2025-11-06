#!/usr/bin/env python3
"""
LLM Compliance Filter - Customization Guide

This guide shows you various ways to customize the compliance filter
for different industries, use cases, and security requirements.
"""

import sys
import yaml
import json
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.compliance_filter import ComplianceFilter


def domain_specific_customizations():
    """Show customizations for different industries/domains."""
    print("🏢 Domain-Specific Customizations")
    print("=" * 80)
    
    print("1. HEALTHCARE (HIPAA Compliance)")
    print("-" * 50)
    
    healthcare_config = {
        'privacy': {
            'checks': {
                'pii_detection': True,
                'email_detection': True,
                'phone_detection': True,
                'ssn_detection': True,
                'medical_info': True,  # Enhanced medical detection
                'address_detection': True,
                'date_of_birth': True
            },
            'custom_patterns': {
                # Medical Record Numbers
                'mrn': r'(?i)(?:mrn|medical\s+record|patient\s+id)[:\s#]*([A-Z0-9]{6,12})',
                # Insurance numbers
                'insurance': r'(?i)(?:insurance|policy)[:\s#]*([A-Z0-9]{8,15})',
                # Drug names (simplified - you'd want a comprehensive list)
                'medications': r'(?i)\b(?:adderall|prozac|oxycodone|morphine|insulin|metformin)\b',
                # Medical conditions
                'conditions': r'(?i)\b(?:diabetes|cancer|depression|hypertension|covid|hiv|aids)\b',
                # Medical procedures
                'procedures': r'(?i)\b(?:surgery|biopsy|chemotherapy|dialysis|transplant)\b'
            },
            'risk_levels': {
                'high_risk_threshold': 0.9,  # Very strict for medical
                'medium_risk_threshold': 0.6,
                'low_risk_threshold': 0.3
            }
        },
        'compliance': {
            'thresholds': {
                'block_threshold': 0.4,  # Very strict
                'warn_threshold': 0.3,
                'pass_threshold': 0.1
            },
            'weights': {
                'privacy': 0.9,  # Heavily prioritize privacy
                'hate_speech': 0.1
            }
        }
    }
    
    print("Healthcare Configuration:")
    print(json.dumps(healthcare_config, indent=2))
    
    print("\n2. FINANCIAL SERVICES (PCI DSS/SOX)")
    print("-" * 50)
    
    financial_config = {
        'privacy': {
            'checks': {
                'credit_card_detection': True,
                'ssn_detection': True,
                'financial_info': True,
                'bank_account_detection': True,
                'phone_detection': True,
                'email_detection': True
            },
            'custom_patterns': {
                # Enhanced credit card patterns
                'credit_cards': r'(?i)\b(?:4\d{3}|5[1-5]\d{2}|3[47]\d{2}|6(?:011|5\d{2}))[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
                # Bank routing numbers
                'routing_numbers': r'\b[0-9]{9}\b',
                # IBAN
                'iban': r'\b[A-Z]{2}[0-9]{2}[A-Z0-9]{4}[0-9]{7}([A-Z0-9]?){0,16}\b',
                # SWIFT codes
                'swift': r'\b[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?\b',
                # Account numbers
                'account_numbers': r'(?i)(?:account|acct)[:\s#]*([0-9]{8,17})',
                # Financial terms
                'financial_terms': r'(?i)\b(?:salary|income|net\s+worth|balance|debt|loan|mortgage|credit\s+score)\b'
            },
            'risk_levels': {
                'high_risk_threshold': 0.8,
                'medium_risk_threshold': 0.5,
                'low_risk_threshold': 0.2
            }
        },
        'compliance': {
            'thresholds': {
                'block_threshold': 0.5,  # Strict but usable
                'warn_threshold': 0.4,
                'pass_threshold': 0.2
            },
            'weights': {
                'privacy': 0.8,
                'hate_speech': 0.2
            }
        }
    }
    
    print("Financial Services Configuration:")
    print(json.dumps(financial_config, indent=2))
    
    print("\n3. EDUCATION (FERPA Compliance)")
    print("-" * 50)
    
    education_config = {
        'privacy': {
            'checks': {
                'pii_detection': True,
                'email_detection': True,
                'phone_detection': True,
                'address_detection': True,
                'date_of_birth': True
            },
            'custom_patterns': {
                # Student IDs
                'student_id': r'(?i)(?:student\s+id|sid)[:\s#]*([A-Z0-9]{6,12})',
                # Grades
                'grades': r'(?i)\b(?:grade|gpa|score)[:\s]*([0-9]+\.?[0-9]*|[A-F][+-]?)\b',
                # Educational records
                'transcripts': r'(?i)\b(?:transcript|academic\s+record|diploma|degree)\b',
                # School info
                'school_info': r'(?i)\b(?:school|university|college|classroom|teacher)\s+(?:id|number|code)',
            }
        },
        'compliance': {
            'thresholds': {
                'block_threshold': 0.6,
                'warn_threshold': 0.4,
                'pass_threshold': 0.2
            }
        }
    }
    
    print("Education Configuration:")
    print(json.dumps(education_config, indent=2))


def custom_privacy_patterns():
    """Show how to add custom privacy detection patterns."""
    print("\n🔍 Custom Privacy Pattern Examples")
    print("=" * 80)
    
    print("1. COMPANY-SPECIFIC PATTERNS")
    print("-" * 40)
    
    company_patterns = {
        # Employee IDs
        'employee_id': r'(?i)(?:emp|employee)[:\s#]*([A-Z]{2}[0-9]{6})',
        
        # Internal project codes
        'project_codes': r'(?i)(?:project|proj)[:\s#]*([A-Z]{3}-[0-9]{4})',
        
        # Custom email domains
        'company_emails': r'\b[A-Za-z0-9._%+-]+@(?:yourcompany\.com|subsidiary\.net)\b',
        
        # Internal server names
        'server_names': r'(?i)\b(?:srv|server|host)-[a-z0-9-]+\.(?:internal|local)\b',
        
        # License keys
        'license_keys': r'[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}',
        
        # Custom ID formats
        'custom_ids': r'(?i)(?:ref|reference)[:\s#]*([A-Z]{2}[0-9]{8})'
    }
    
    print("Company-specific patterns:")
    for pattern_name, regex in company_patterns.items():
        print(f"  {pattern_name}: {regex}")
    
    print("\n2. INTERNATIONAL PATTERNS")
    print("-" * 40)
    
    international_patterns = {
        # UK National Insurance Numbers
        'uk_nino': r'\b[A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z][0-9]{6}[A-D]\b',
        
        # Canadian SIN
        'canadian_sin': r'\b[0-9]{3}[-\s]?[0-9]{3}[-\s]?[0-9]{3}\b',
        
        # Australian TFN
        'australian_tfn': r'\b[0-9]{3}[-\s]?[0-9]{3}[-\s]?[0-9]{3}\b',
        
        # European VAT numbers
        'eu_vat': r'\b[A-Z]{2}[0-9A-Z]{8,12}\b',
        
        # International phone numbers
        'intl_phone': r'\+[1-9][0-9]{1,3}[-\s]?[0-9]{1,4}[-\s]?[0-9]{1,4}[-\s]?[0-9]{1,4}',
        
        # Passport numbers (generic)
        'passport': r'(?i)(?:passport)[:\s#]*([A-Z0-9]{6,9})'
    }
    
    print("International patterns:")
    for pattern_name, regex in international_patterns.items():
        print(f"  {pattern_name}: {regex}")
    
    print("\n3. TECHNOLOGY-SPECIFIC PATTERNS")
    print("-" * 40)
    
    tech_patterns = {
        # Database connection strings
        'db_connection': r'(?i)(?:server|host|database)[=\s]*[a-zA-Z0-9.-]+',
        
        # AWS keys
        'aws_access_key': r'AKIA[0-9A-Z]{16}',
        'aws_secret_key': r'[A-Za-z0-9/+=]{40}',
        
        # JWT tokens
        'jwt_token': r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]*',
        
        # GitHub tokens
        'github_token': r'ghp_[A-Za-z0-9]{36}',
        
        # Docker registry credentials
        'docker_creds': r'(?i)(?:docker|registry)[:\s]*[a-zA-Z0-9._-]+:[a-zA-Z0-9._-]+',
        
        # Private keys
        'private_key': r'-----BEGIN (?:RSA )?PRIVATE KEY-----',
    }
    
    print("Technology-specific patterns:")
    for pattern_name, regex in tech_patterns.items():
        print(f"  {pattern_name}: {regex}")


def threshold_tuning_strategies():
    """Show different threshold tuning strategies."""
    print("\n⚖️ Threshold Tuning Strategies")
    print("=" * 80)
    
    print("1. RISK-BASED CONFIGURATIONS")
    print("-" * 40)
    
    risk_configs = {
        'maximum_security': {
            'description': 'Government, Military, Critical Infrastructure',
            'config': {
                'compliance': {
                    'thresholds': {
                        'block_threshold': 0.2,  # Block almost everything
                        'warn_threshold': 0.1,
                        'pass_threshold': 0.05
                    },
                    'weights': {
                        'privacy': 0.9,
                        'hate_speech': 0.1
                    }
                }
            }
        },
        'high_security': {
            'description': 'Healthcare, Finance, Legal',
            'config': {
                'compliance': {
                    'thresholds': {
                        'block_threshold': 0.4,
                        'warn_threshold': 0.3,
                        'pass_threshold': 0.1
                    },
                    'weights': {
                        'privacy': 0.8,
                        'hate_speech': 0.2
                    }
                }
            }
        },
        'balanced': {
            'description': 'General Business, E-commerce',
            'config': {
                'compliance': {
                    'thresholds': {
                        'block_threshold': 0.7,
                        'warn_threshold': 0.5,
                        'pass_threshold': 0.2
                    },
                    'weights': {
                        'privacy': 0.6,
                        'hate_speech': 0.4
                    }
                }
            }
        },
        'permissive': {
            'description': 'Internal Tools, Development',
            'config': {
                'compliance': {
                    'thresholds': {
                        'block_threshold': 0.85,
                        'warn_threshold': 0.7,
                        'pass_threshold': 0.3
                    },
                    'weights': {
                        'privacy': 0.4,
                        'hate_speech': 0.6
                    }
                }
            }
        },
        'development': {
            'description': 'Testing, Staging Environments',
            'config': {
                'compliance': {
                    'thresholds': {
                        'block_threshold': 0.95,  # Almost never block
                        'warn_threshold': 0.8,
                        'pass_threshold': 0.5
                    },
                    'weights': {
                        'privacy': 0.3,
                        'hate_speech': 0.7
                    }
                }
            }
        }
    }
    
    for config_name, config_info in risk_configs.items():
        print(f"\n{config_name.upper().replace('_', ' ')}:")
        print(f"  Use case: {config_info['description']}")
        print(f"  Block threshold: {config_info['config']['compliance']['thresholds']['block_threshold']}")
        print(f"  Privacy weight: {config_info['config']['compliance']['weights']['privacy']}")
    
    print("\n2. ADAPTIVE THRESHOLD STRATEGIES")
    print("-" * 40)
    
    adaptive_code = '''
class AdaptiveComplianceFilter:
    """Compliance filter with adaptive thresholds based on context."""
    
    def __init__(self):
        self.base_filter = ComplianceFilter()
        self.user_risk_profiles = {}
        self.content_type_adjustments = {
            'customer_support': 0.1,      # More permissive
            'financial_data': -0.2,       # More strict
            'internal_comms': 0.15,       # More permissive
            'public_facing': -0.1,        # More strict
            'development': 0.3            # Much more permissive
        }
    
    def check_compliance_adaptive(self, prompt, user_id=None, content_type='general'):
        """Check compliance with adaptive thresholds."""
        
        # Get base result
        result = self.base_filter.check_compliance(prompt)
        
        # Apply user-specific adjustments
        user_adjustment = self.user_risk_profiles.get(user_id, 0)
        
        # Apply content type adjustments
        content_adjustment = self.content_type_adjustments.get(content_type, 0)
        
        # Calculate adjusted score
        adjusted_score = result.overall_score + user_adjustment + content_adjustment
        adjusted_score = max(0.0, min(1.0, adjusted_score))  # Clamp to [0,1]
        
        # Determine new action based on adjusted score
        if adjusted_score >= self.base_filter.thresholds['block_threshold']:
            new_action = ComplianceAction.BLOCK
        elif adjusted_score >= self.base_filter.thresholds['warn_threshold']:
            new_action = ComplianceAction.WARN
        else:
            new_action = ComplianceAction.ALLOW
        
        # Return modified result
        result.overall_score = adjusted_score
        result.action = new_action
        return result
    
    def update_user_risk_profile(self, user_id, risk_adjustment):
        """Update user-specific risk profile."""
        self.user_risk_profiles[user_id] = risk_adjustment
'''
    
    print("Adaptive threshold example:")
    print(adaptive_code)


def advanced_customizations():
    """Show advanced customization techniques."""
    print("\n🔧 Advanced Customizations")
    print("=" * 80)
    
    print("1. CUSTOM VIOLATION TYPES")
    print("-" * 40)
    
    custom_violations_code = '''
from enum import Enum
from dataclasses import dataclass

class CustomViolationType(Enum):
    """Custom violation types for specific domains."""
    EMPLOYEE_ID = "employee_id"
    PROJECT_CODE = "project_code"
    INTERNAL_SYSTEM = "internal_system"
    PROPRIETARY_INFO = "proprietary_info"
    COMPETITIVE_INTEL = "competitive_intel"

@dataclass
class CustomPrivacyViolation:
    """Custom privacy violation with additional metadata."""
    violation_type: CustomViolationType
    confidence: float
    text_span: str
    start_pos: int
    end_pos: int
    description: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    remediation: str  # Suggested remediation action

class ExtendedPrivacyDetector:
    """Extended privacy detector with custom violation types."""
    
    def __init__(self):
        self.custom_patterns = {
            CustomViolationType.EMPLOYEE_ID: {
                'pattern': r'(?i)(?:emp|employee)[:\\s#]*([A-Z]{2}[0-9]{6})',
                'severity': 'medium',
                'remediation': 'Replace with generic identifier'
            },
            CustomViolationType.PROJECT_CODE: {
                'pattern': r'(?i)(?:project|proj)[:\\s#]*([A-Z]{3}-[0-9]{4})',
                'severity': 'high',
                'remediation': 'Remove project reference'
            }
        }
    
    def detect_custom_violations(self, text):
        """Detect custom violation types."""
        violations = []
        for violation_type, config in self.custom_patterns.items():
            pattern = re.compile(config['pattern'])
            for match in pattern.finditer(text):
                violation = CustomPrivacyViolation(
                    violation_type=violation_type,
                    confidence=0.95,
                    text_span=match.group(),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    description=f"Detected {violation_type.value}",
                    severity=config['severity'],
                    remediation=config['remediation']
                )
                violations.append(violation)
        return violations
'''
    
    print("Custom violation types:")
    print(custom_violations_code)
    
    print("\n2. CONTEXTUAL COMPLIANCE SCORING")
    print("-" * 40)
    
    contextual_scoring_code = '''
class ContextualComplianceFilter:
    """Compliance filter that considers request context."""
    
    def __init__(self):
        self.base_filter = ComplianceFilter()
        
        # Context-based multipliers
        self.context_multipliers = {
            'public_api': 1.2,           # More strict for public APIs
            'internal_tool': 0.8,        # Less strict for internal tools
            'customer_facing': 1.1,      # Slightly more strict
            'admin_panel': 0.9,          # Slightly less strict
            'data_export': 1.5,          # Much more strict
            'search_query': 0.7          # Less strict for searches
        }
        
        # Time-based adjustments
        self.time_adjustments = {
            'business_hours': 0.0,       # Normal strictness
            'after_hours': -0.1,         # Slightly less strict
            'weekend': -0.1,             # Slightly less strict
            'holiday': -0.2              # Less strict
        }
    
    def check_compliance_contextual(self, prompt, context=None):
        """Check compliance with contextual adjustments."""
        
        # Get base compliance result
        result = self.base_filter.check_compliance(prompt)
        
        if not context:
            return result
        
        # Apply context multiplier
        context_type = context.get('type', 'general')
        multiplier = self.context_multipliers.get(context_type, 1.0)
        
        # Apply time-based adjustment
        time_context = context.get('time_context', 'business_hours')
        time_adj = self.time_adjustments.get(time_context, 0.0)
        
        # Apply user role adjustment
        user_role = context.get('user_role', 'user')
        role_adj = {
            'admin': -0.2,      # Less strict for admins
            'moderator': -0.1,  # Less strict for moderators
            'user': 0.0,        # Normal strictness
            'guest': 0.1        # More strict for guests
        }.get(user_role, 0.0)
        
        # Calculate final adjusted score
        adjusted_score = result.overall_score * multiplier + time_adj + role_adj
        adjusted_score = max(0.0, min(1.0, adjusted_score))
        
        # Update result
        result.overall_score = adjusted_score
        result.reasoning += f" (adjusted for context: {context_type})"
        
        return result
'''
    
    print("Contextual scoring:")
    print(contextual_scoring_code)
    
    print("\n3. MACHINE LEARNING INTEGRATION")
    print("-" * 40)
    
    ml_integration_code = '''
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

class MLEnhancedComplianceFilter:
    """Compliance filter enhanced with custom ML models."""
    
    def __init__(self):
        self.base_filter = ComplianceFilter()
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.custom_classifier = LogisticRegression()
        self.model_trained = False
    
    def train_custom_classifier(self, training_texts, training_labels):
        """Train a custom classifier on your domain-specific data."""
        
        # Vectorize the training texts
        X = self.vectorizer.fit_transform(training_texts)
        
        # Train the classifier
        self.custom_classifier.fit(X, training_labels)
        self.model_trained = True
        
        # Save the models
        joblib.dump(self.vectorizer, 'custom_vectorizer.pkl')
        joblib.dump(self.custom_classifier, 'custom_classifier.pkl')
    
    def load_custom_models(self):
        """Load pre-trained custom models."""
        try:
            self.vectorizer = joblib.load('custom_vectorizer.pkl')
            self.custom_classifier = joblib.load('custom_classifier.pkl')
            self.model_trained = True
        except FileNotFoundError:
            print("Custom models not found. Train first or use base filter.")
    
    def check_compliance_ml_enhanced(self, prompt):
        """Check compliance using both rule-based and ML approaches."""
        
        # Get base compliance result
        base_result = self.base_filter.check_compliance(prompt)
        
        if not self.model_trained:
            return base_result
        
        # Get ML prediction
        X = self.vectorizer.transform([prompt])
        ml_prob = self.custom_classifier.predict_proba(X)[0][1]  # Probability of violation
        
        # Combine rule-based and ML scores
        combined_score = 0.7 * base_result.overall_score + 0.3 * ml_prob
        
        # Update the result
        base_result.overall_score = combined_score
        base_result.reasoning += f" (ML confidence: {ml_prob:.3f})"
        
        return base_result

# Example usage:
# ml_filter = MLEnhancedComplianceFilter()
# ml_filter.train_custom_classifier(your_training_texts, your_training_labels)
# result = ml_filter.check_compliance_ml_enhanced(prompt)
'''
    
    print("ML integration example:")
    print(ml_integration_code)


def performance_optimizations():
    """Show performance optimization techniques."""
    print("\n⚡ Performance Optimizations")
    print("=" * 80)
    
    print("1. CACHING STRATEGIES")
    print("-" * 40)
    
    caching_code = '''
import hashlib
from functools import lru_cache
import redis

class CachedComplianceFilter:
    """Compliance filter with intelligent caching."""
    
    def __init__(self, use_redis=False):
        self.base_filter = ComplianceFilter()
        self.use_redis = use_redis
        
        if use_redis:
            self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        
        # In-memory cache for recent results
        self.memory_cache = {}
        self.cache_size_limit = 1000
    
    def _get_cache_key(self, prompt):
        """Generate cache key for prompt."""
        return hashlib.md5(prompt.encode()).hexdigest()
    
    @lru_cache(maxsize=500)
    def _cached_privacy_check(self, prompt_hash, prompt):
        """Cached privacy detection (uses function-level caching)."""
        return self.base_filter.privacy_detector.detect_violations(prompt)
    
    def check_compliance_cached(self, prompt, cache_ttl=3600):
        """Check compliance with caching."""
        
        cache_key = self._get_cache_key(prompt)
        
        # Try Redis cache first
        if self.use_redis:
            cached_result = self.redis_client.get(f"compliance:{cache_key}")
            if cached_result:
                return json.loads(cached_result)
        
        # Try memory cache
        if cache_key in self.memory_cache:
            return self.memory_cache[cache_key]
        
        # Compute result
        result = self.base_filter.check_compliance(prompt)
        
        # Cache the result
        result_dict = {
            'action': result.action.value,
            'overall_score': result.overall_score,
            'privacy_score': result.privacy_score,
            'hate_speech_score': result.hate_speech_score,
            'reasoning': result.reasoning
        }
        
        # Store in Redis
        if self.use_redis:
            self.redis_client.setex(
                f"compliance:{cache_key}", 
                cache_ttl, 
                json.dumps(result_dict)
            )
        
        # Store in memory cache
        if len(self.memory_cache) < self.cache_size_limit:
            self.memory_cache[cache_key] = result_dict
        
        return result_dict
'''
    
    print("Caching implementation:")
    print(caching_code)
    
    print("\n2. BATCH OPTIMIZATION")
    print("-" * 40)
    
    batch_code = '''
import asyncio
from concurrent.futures import ThreadPoolExecutor

class OptimizedBatchProcessor:
    """Optimized batch processing for compliance checks."""
    
    def __init__(self, max_workers=4):
        self.filter = ComplianceFilter()
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def process_batch_parallel(self, prompts):
        """Process batch of prompts in parallel."""
        
        # Split into chunks for parallel processing
        chunk_size = max(1, len(prompts) // self.max_workers)
        chunks = [prompts[i:i+chunk_size] for i in range(0, len(prompts), chunk_size)]
        
        # Process chunks in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(self._process_chunk, chunk) 
                for chunk in chunks
            ]
            
            # Collect results
            results = []
            for future in futures:
                results.extend(future.result())
        
        return results
    
    def _process_chunk(self, chunk):
        """Process a chunk of prompts."""
        return [self.filter.check_compliance(prompt) for prompt in chunk]
    
    async def process_batch_async(self, prompts):
        """Process batch asynchronously."""
        
        async def check_single(prompt):
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                self.executor, 
                self.filter.check_compliance, 
                prompt
            )
        
        # Process all prompts concurrently
        tasks = [check_single(prompt) for prompt in prompts]
        return await asyncio.gather(*tasks)

# Usage:
# processor = OptimizedBatchProcessor(max_workers=8)
# results = processor.process_batch_parallel(large_prompt_list)
# results = await processor.process_batch_async(large_prompt_list)
'''
    
    print("Batch optimization:")
    print(batch_code)


def deployment_configurations():
    """Show deployment-specific configurations."""
    print("\n🚀 Deployment Configurations")
    print("=" * 80)
    
    print("1. ENVIRONMENT-SPECIFIC CONFIGS")
    print("-" * 40)
    
    configs = {
        'development.yaml': {
            'compliance': {
                'thresholds': {
                    'block_threshold': 0.95,  # Very permissive
                    'warn_threshold': 0.8,
                    'pass_threshold': 0.5
                }
            },
            'logging': {
                'level': 'DEBUG',
                'log_to_console': True,
                'log_to_file': False
            },
            'hate_speech': {
                'use_cache': True,
                'model_name': 'unitary/toxic-bert'
            }
        },
        'staging.yaml': {
            'compliance': {
                'thresholds': {
                    'block_threshold': 0.8,   # Moderate
                    'warn_threshold': 0.6,
                    'pass_threshold': 0.3
                }
            },
            'logging': {
                'level': 'INFO',
                'log_to_console': True,
                'log_to_file': True,
                'audit_logs': True
            }
        },
        'production.yaml': {
            'compliance': {
                'thresholds': {
                    'block_threshold': 0.7,   # Production settings
                    'warn_threshold': 0.5,
                    'pass_threshold': 0.2
                }
            },
            'logging': {
                'level': 'WARNING',
                'log_to_console': False,
                'log_to_file': True,
                'audit_logs': True,
                'log_details': {
                    'prompt_content': False,  # Privacy in production
                    'violation_details': True,
                    'scores': True,
                    'timestamps': True
                }
            },
            'caching': {
                'enable_model_caching': True,
                'cache_max_size_gb': 10
            }
        }
    }
    
    for filename, config in configs.items():
        print(f"\n{filename}:")
        print(yaml.dump(config, default_flow_style=False, indent=2))


def testing_customizations():
    """Show how to create custom test suites."""
    print("\n🧪 Custom Testing Strategies")
    print("=" * 80)
    
    testing_code = '''
class CustomTestSuite:
    """Custom test suite for domain-specific compliance testing."""
    
    def __init__(self, filter_config=None):
        self.filter = ComplianceFilter(config_dict=filter_config)
        self.test_results = {}
    
    def test_healthcare_compliance(self):
        """Test healthcare-specific patterns."""
        
        test_cases = [
            # Should be blocked
            ("Patient ID 12345 has diabetes", "block", "medical_info"),
            ("MRN: ABC123456", "block", "medical_record"),
            ("Insurance policy 987654321", "block", "insurance"),
            
            # Should be allowed
            ("General medical information", "allow", "general"),
            ("Healthcare industry overview", "allow", "general"),
        ]
        
        results = []
        for text, expected_action, category in test_cases:
            result = self.filter.check_compliance(text)
            passed = result.action.value == expected_action
            
            results.append({
                'text': text,
                'expected': expected_action,
                'actual': result.action.value,
                'passed': passed,
                'score': result.overall_score,
                'category': category
            })
        
        self.test_results['healthcare'] = results
        return results
    
    def test_financial_compliance(self):
        """Test financial-specific patterns."""
        
        test_cases = [
            ("Credit card 4532-1234-5678-9012", "block", "credit_card"),
            ("Account balance: $50,000", "warn", "financial_info"),
            ("SWIFT code ABCDUS33", "block", "swift_code"),
            ("General banking information", "allow", "general"),
        ]
        
        results = []
        for text, expected_action, category in test_cases:
            result = self.filter.check_compliance(text)
            passed = result.action.value == expected_action
            
            results.append({
                'text': text,
                'expected': expected_action,
                'actual': result.action.value,
                'passed': passed,
                'score': result.overall_score,
                'category': category
            })
        
        self.test_results['financial'] = results
        return results
    
    def run_regression_tests(self):
        """Run regression tests to ensure consistency."""
        
        # Load known good/bad examples from file
        with open('regression_tests.json', 'r') as f:
            test_data = json.load(f)
        
        results = []
        for test_case in test_data:
            result = self.filter.check_compliance(test_case['text'])
            
            # Check if result matches expected
            passed = (
                result.action.value == test_case['expected_action'] and
                abs(result.overall_score - test_case['expected_score']) < 0.1
            )
            
            if not passed:
                print(f"REGRESSION FAILURE: {test_case['text']}")
                print(f"  Expected: {test_case['expected_action']} ({test_case['expected_score']})")
                print(f"  Got: {result.action.value} ({result.overall_score})")
            
            results.append(passed)
        
        return results
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'categories': {}
        }
        
        for domain, results in self.test_results.items():
            category_stats = {'passed': 0, 'failed': 0, 'total': len(results)}
            
            for result in results:
                if result['passed']:
                    category_stats['passed'] += 1
                    report['passed_tests'] += 1
                else:
                    category_stats['failed'] += 1
                    report['failed_tests'] += 1
                
                report['total_tests'] += 1
            
            report['categories'][domain] = category_stats
        
        return report

# Usage:
# test_suite = CustomTestSuite(healthcare_config)
# test_suite.test_healthcare_compliance()
# test_suite.test_financial_compliance()
# report = test_suite.generate_test_report()
'''
    
    print("Custom testing framework:")
    print(testing_code)


def main():
    """Run the complete customization guide."""
    print("🎨 LLM Compliance Filter - Complete Customization Guide")
    print("=" * 100)
    print("This guide shows you how to customize the filter for any use case")
    print("=" * 100)
    
    domain_specific_customizations()
    custom_privacy_patterns()
    threshold_tuning_strategies()
    advanced_customizations()
    performance_optimizations()
    deployment_configurations()
    testing_customizations()
    
    print("\n" + "=" * 100)
    print("🎯 CUSTOMIZATION COMPLETE!")
    print("=" * 100)
    
    print("\n📋 Customization Summary:")
    print("✅ Domain-specific configurations (Healthcare, Finance, Education)")
    print("✅ Custom privacy pattern examples")
    print("✅ Threshold tuning strategies")
    print("✅ Advanced ML integration techniques")
    print("✅ Performance optimization methods")
    print("✅ Deployment configurations")
    print("✅ Custom testing frameworks")
    
    print("\n🛠️ Implementation Checklist:")
    print("1. Choose your domain-specific configuration")
    print("2. Add custom privacy patterns for your use case")
    print("3. Set appropriate thresholds for your risk level")
    print("4. Implement caching if processing high volumes")
    print("5. Create environment-specific configurations")
    print("6. Build custom test suites for your patterns")
    print("7. Monitor and adjust based on real usage")
    
    print("\n💡 Pro Tips:")
    print("- Start with a standard configuration and iterate")
    print("- Test thoroughly with representative data")
    print("- Monitor false positives/negatives in production")
    print("- Use A/B testing for threshold changes")
    print("- Keep audit logs for compliance requirements")
    print("- Regular reviews of blocked content patterns")


if __name__ == "__main__":
    main()
