#!/usr/bin/env python3
"""
Enhanced Privacy Violation Detector

Comprehensive detection of confidential and personally identifiable information (PII):
- API Keys (OpenAI, AWS, GitHub, Google, Slack, Stripe, etc.)
- Passwords and Secrets
- Credit Cards (with Luhn algorithm validation)
- Social Security Numbers
- Email Addresses and Phone Numbers
- Bank Account Numbers, Routing Numbers, IBAN
- Private Keys (RSA, SSH, PGP)
- OAuth Tokens and JWTs
- Database Connection Strings
- IP Addresses (public/private)
- Medical Records and Health Information
- Biometric Data References
"""

import re
import hashlib
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PrivacyCategory(Enum):
    """Categories of privacy violations"""
    API_KEY = "api_key"
    PASSWORD = "password"
    CREDIT_CARD = "credit_card"
    SSN = "ssn"
    EMAIL = "email"
    PHONE = "phone"
    BANK_ACCOUNT = "bank_account"
    PRIVATE_KEY = "private_key"
    OAUTH_TOKEN = "oauth_token"
    JWT_TOKEN = "jwt_token"
    DATABASE_CONNECTION = "database_connection"
    IP_ADDRESS = "ip_address"
    MEDICAL_RECORD = "medical_record"
    BIOMETRIC = "biometric"
    PASSPORT = "passport"
    DRIVERS_LICENSE = "drivers_license"
    DATE_OF_BIRTH = "date_of_birth"
    ADDRESS = "address"
    AWS_SECRET = "aws_secret"


@dataclass
class PrivacyViolation:
    """Detected privacy violation"""
    category: PrivacyCategory
    confidence: float
    masked_value: str  # Redacted version for logging
    position: int
    severity: str  # low, medium, high, critical
    description: str


@dataclass
class PrivacyDetectionResult:
    """Result from privacy detection"""
    has_violations: bool
    violations: List[PrivacyViolation] = field(default_factory=list)
    privacy_score: float = 0.0  # 0.0 = safe, 1.0 = severe violations
    risk_level: str = "safe"  # safe, low, medium, high, critical
    redacted_text: Optional[str] = None
    explanation: str = ""


class EnhancedPrivacyDetector:
    """
    Enhanced privacy violation detector with comprehensive pattern matching
    """
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
        self.total_detections = 0
        self.category_counts = {cat: 0 for cat in PrivacyCategory}
        
    def _initialize_patterns(self) -> Dict[PrivacyCategory, Dict]:
        """Initialize all detection patterns"""
        
        return {
            # API Keys
            PrivacyCategory.API_KEY: {
                'severity': 'critical',
                'patterns': [
                    # OpenAI
                    (r'sk-[A-Za-z0-9]{48}', 'OpenAI API Key'),
                    (r'sk-proj-[A-Za-z0-9_-]{30,}', 'OpenAI Project API Key'),
                    
                    # AWS
                    (r'\bAKIA[0-9A-Z]{16}\b', 'AWS Access Key ID'),
                    (r'\b[A-Za-z0-9/+=]{40}\b', 'AWS Secret Access Key (potential)'),
                    
                    # GitHub
                    (r'ghp_[A-Za-z0-9]{30,40}', 'GitHub Personal Access Token'),
                    (r'gho_[A-Za-z0-9]{36}', 'GitHub OAuth Token'),
                    (r'ghu_[A-Za-z0-9]{36}', 'GitHub User Token'),
                    (r'ghs_[A-Za-z0-9]{36}', 'GitHub Server Token'),
                    (r'ghr_[A-Za-z0-9]{36}', 'GitHub Refresh Token'),
                    
                    # Google
                    (r'\bAIza[0-9A-Za-z\-_]{35}\b', 'Google API Key'),
                    (r'\bya29\.[0-9A-Za-z\-_]+\b', 'Google OAuth Token'),
                    
                    # Slack
                    (r'\bxox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[A-Za-z0-9]{24,}\b', 'Slack Token'),
                    
                    # Stripe
                    (r'\bsk_live_[0-9a-zA-Z]{24,}\b', 'Stripe Secret Key'),
                    (r'\brk_live_[0-9a-zA-Z]{24,}\b', 'Stripe Restricted Key'),
                    
                    # Azure
                    (r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b', 'Azure/Generic UUID'),
                    
                    # Twilio
                    (r'\bSK[0-9a-f]{32}\b', 'Twilio API Key'),
                    
                    # Generic API key patterns
                    (r'\bapi[_-]?key[\s:=]+["\']?([A-Za-z0-9_\-]{20,})["\']?', 'Generic API Key'),
                    (r'\bapikey[\s:=]+["\']?([A-Za-z0-9_\-]{20,})["\']?', 'Generic API Key'),
                ]
            },
            
            # AWS Secret Keys
            PrivacyCategory.AWS_SECRET: {
                'severity': 'critical',
                'patterns': [
                    (r'\baws[_-]?secret[_-]?access[_-]?key[\s:=]+["\']?([A-Za-z0-9/+=]{40})["\']?', 'AWS Secret Access Key'),
                ]
            },
            
            # Passwords
            PrivacyCategory.PASSWORD: {
                'severity': 'critical',
                'patterns': [
                    (r'\bpassword[\s:=]+["\']?([^\s"\']{6,})["\']?', 'Password'),
                    (r'\bpwd[\s:=]+["\']?([^\s"\']{6,})["\']?', 'Password'),
                    (r'\bpass[\s:=]+["\']?([^\s"\']{6,})["\']?', 'Password'),
                    (r'\bsecret[\s:=]+["\']?([A-Za-z0-9_\-]{8,})["\']?', 'Secret'),
                    (r'\bauth[_-]?token[\s:=]+["\']?([A-Za-z0-9_\-]{16,})["\']?', 'Auth Token'),
                ]
            },
            
            # Private Keys
            PrivacyCategory.PRIVATE_KEY: {
                'severity': 'critical',
                'patterns': [
                    (r'-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----', 'Private Key'),
                    (r'-----BEGIN PGP PRIVATE KEY BLOCK-----', 'PGP Private Key'),
                    (r'\bprivate[_-]?key[\s:=]+["\']?([A-Za-z0-9/+=\n]{32,})["\']?', 'Private Key'),
                ]
            },
            
            # JWT Tokens
            PrivacyCategory.JWT_TOKEN: {
                'severity': 'high',
                'patterns': [
                    (r'\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b', 'JWT Token'),
                ]
            },
            
            # OAuth Tokens
            PrivacyCategory.OAUTH_TOKEN: {
                'severity': 'high',
                'patterns': [
                    (r'\baccess[_-]?token[\s:=]+["\']?([A-Za-z0-9_\-\.]{20,})["\']?', 'OAuth Access Token'),
                    (r'\brefresh[_-]?token[\s:=]+["\']?([A-Za-z0-9_\-\.]{20,})["\']?', 'OAuth Refresh Token'),
                    (r'\bbearer\s+([A-Za-z0-9_\-\.=]{20,})\b', 'Bearer Token'),
                ]
            },
            
            # Credit Cards
            PrivacyCategory.CREDIT_CARD: {
                'severity': 'critical',
                'patterns': [
                    # Visa: starts with 4
                    (r'4[0-9]{3}[\s\-]?[0-9]{4}[\s\-]?[0-9]{4}[\s\-]?[0-9]{4}', 'Visa Card'),
                    # Mastercard: starts with 51-55 or 2221-2720
                    (r'\b5[1-5][0-9]{2}[\s\-]?[0-9]{4}[\s\-]?[0-9]{4}[\s\-]?[0-9]{4}\b', 'Mastercard'),
                    # Amex: starts with 34 or 37
                    (r'\b3[47][0-9]{2}[\s\-]?[0-9]{6}[\s\-]?[0-9]{5}\b', 'American Express'),
                    # Discover: starts with 6011, 644-649, 65
                    (r'\b6(?:011|5[0-9]{2}|4[4-9][0-9])[\s\-]?[0-9]{4}[\s\-]?[0-9]{4}[\s\-]?[0-9]{4}\b', 'Discover'),
                    # With CVV
                    (r'\b[0-9]{4}[\s\-]?[0-9]{4}[\s\-]?[0-9]{4}[\s\-]?[0-9]{4}\s+(?:cvv|cvc)[\s:=]+[0-9]{3,4}\b', 'Card with CVV'),
                ]
            },
            
            # Social Security Numbers
            PrivacyCategory.SSN: {
                'severity': 'critical',
                'patterns': [
                    (r'\b(?!000|666|9\d{2})\d{3}[\s\-]?(?!00)\d{2}[\s\-]?(?!0000)\d{4}\b', 'Social Security Number'),
                    (r'\bssn[\s:=]+\d{3}[\s\-]?\d{2}[\s\-]?\d{4}\b', 'SSN with label'),
                ]
            },
            
            # Email Addresses
            PrivacyCategory.EMAIL: {
                'severity': 'medium',
                'patterns': [
                    (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'Email Address'),
                ]
            },
            
            # Phone Numbers
            PrivacyCategory.PHONE: {
                'severity': 'medium',
                'patterns': [
                    # US format
                    (r'\b(?:\+?1[\s\-]?)?\(?([0-9]{3})\)?[\s\-]?([0-9]{3})[\s\-]?([0-9]{4})\b', 'US Phone Number'),
                    # International format
                    (r'\b\+[0-9]{1,3}[\s\-]?[0-9]{6,14}\b', 'International Phone'),
                ]
            },
            
            # Bank Account Numbers
            PrivacyCategory.BANK_ACCOUNT: {
                'severity': 'critical',
                'patterns': [
                    (r'\baccount[\s_-]?number[\s:=]+\d{8,17}\b', 'Bank Account Number'),
                    (r'\brouting[\s_-]?number[\s:=]+\d{9}\b', 'Bank Routing Number'),
                    (r'\biban[\s:=]+[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b', 'IBAN'),
                    (r'\bswift[\s:=]+[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?\b', 'SWIFT Code'),
                ]
            },
            
            # Database Connection Strings
            PrivacyCategory.DATABASE_CONNECTION: {
                'severity': 'critical',
                'patterns': [
                    (r'(mysql|postgresql|mongodb|redis)://[^\s]+:[^\s]+@[^\s]+', 'Database Connection String'),
                    (r'Server=[^;]+;Database=[^;]+;User Id=[^;]+;Password=[^;]+', 'SQL Server Connection String'),
                    (r'mongodb\+srv://[^\s]+', 'MongoDB Atlas Connection String'),
                ]
            },
            
            # IP Addresses
            PrivacyCategory.IP_ADDRESS: {
                'severity': 'low',
                'patterns': [
                    (r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', 'IPv4 Address'),
                    (r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b', 'IPv6 Address'),
                ]
            },
            
            # Medical Records
            PrivacyCategory.MEDICAL_RECORD: {
                'severity': 'high',
                'patterns': [
                    (r'\bmedical[\s_-]?record[\s_-]?number[\s:=]+[A-Z0-9\-]{6,}', 'Medical Record Number'),
                    (r'\bpatient[\s_-]?id[\s:=]+[A-Z0-9\-]{6,}', 'Patient ID'),
                    (r'\bhealth[\s_-]?insurance[\s:=]+[A-Z0-9\-]{6,}', 'Health Insurance Number'),
                ]
            },
            
            # Biometric Data
            PrivacyCategory.BIOMETRIC: {
                'severity': 'critical',
                'patterns': [
                    (r'\bfingerprint[\s_-]?data[\s:=]', 'Fingerprint Data Reference'),
                    (r'\bfacial[\s_-]?recognition[\s:=]', 'Facial Recognition Data'),
                    (r'\biris[\s_-]?scan[\s:=]', 'Iris Scan Data'),
                    (r'\bvoice[\s_-]?print[\s:=]', 'Voice Print Data'),
                ]
            },
            
            # Passport Numbers
            PrivacyCategory.PASSPORT: {
                'severity': 'critical',
                'patterns': [
                    (r'\bpassport[\s_-]?number[\s:=]+[A-Z0-9]{6,9}\b', 'Passport Number'),
                ]
            },
            
            # Driver's License
            PrivacyCategory.DRIVERS_LICENSE: {
                'severity': 'high',
                'patterns': [
                    (r'\bdriver[\s\']?s?[\s_-]?license[\s:=]+[A-Z0-9\-]{6,20}\b', "Driver's License"),
                    (r'\bDL[\s:=]+[A-Z0-9\-]{6,20}\b', "Driver's License (DL)"),
                ]
            },
            
            # Date of Birth
            PrivacyCategory.DATE_OF_BIRTH: {
                'severity': 'medium',
                'patterns': [
                    (r'\b(?:dob|date[\s_-]?of[\s_-]?birth)[\s:=]+\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', 'Date of Birth'),
                    (r'\bborn[\s:]+\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', 'Birth Date'),
                ]
            },
            
            # Physical Address
            PrivacyCategory.ADDRESS: {
                'severity': 'medium',
                'patterns': [
                    (r'\b\d{1,5}\s+[\w\s]{5,},\s*[\w\s]{3,},\s*[A-Z]{2}\s+\d{5}\b', 'US Street Address'),
                    (r'\baddress[\s:=]+\d+[^,]{10,}', 'Address with Number'),
                ]
            },
        }
    
    def detect(self, text: str) -> PrivacyDetectionResult:
        """
        Detect privacy violations in text
        
        Args:
            text: Input text to analyze
            
        Returns:
            PrivacyDetectionResult with all detected violations
        """
        if not text or len(text.strip()) < 5:
            return PrivacyDetectionResult(
                has_violations=False,
                explanation="Text too short for analysis"
            )
        
        violations = []
        redacted_text = text
        
        # Check each pattern category
        for category, config in self.patterns.items():
            severity = config['severity']
            patterns = config['patterns']
            
            for pattern, description in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    matched_text = match.group(0)
                    
                    # Additional validation for certain types
                    if category == PrivacyCategory.CREDIT_CARD:
                        if not self._validate_credit_card(matched_text):
                            continue  # Skip invalid credit card numbers
                    
                    # Calculate confidence
                    confidence = self._calculate_confidence(category, matched_text)
                    
                    # Mask the sensitive data
                    masked_value = self._mask_value(category, matched_text)
                    
                    # Create violation
                    violation = PrivacyViolation(
                        category=category,
                        confidence=confidence,
                        masked_value=masked_value,
                        position=match.start(),
                        severity=severity,
                        description=f"{description} detected"
                    )
                    
                    violations.append(violation)
                    
                    # Redact in text
                    redacted_text = redacted_text.replace(
                        matched_text,
                        f"[REDACTED_{category.value.upper()}]"
                    )
                    
                    # Update metrics
                    self.total_detections += 1
                    self.category_counts[category] += 1
        
        # Calculate overall privacy score
        privacy_score = self._calculate_privacy_score(violations)
        
        # Determine risk level
        risk_level = self._determine_risk_level(privacy_score, violations)
        
        # Generate explanation
        explanation = self._generate_explanation(violations)
        
        result = PrivacyDetectionResult(
            has_violations=len(violations) > 0,
            violations=violations,
            privacy_score=privacy_score,
            risk_level=risk_level,
            redacted_text=redacted_text if len(violations) > 0 else None,
            explanation=explanation
        )
        
        return result
    
    def _validate_credit_card(self, card_number: str) -> bool:
        """
        Validate credit card using Luhn algorithm
        """
        # Remove spaces and dashes
        digits = re.sub(r'[\s\-]', '', card_number)
        
        if not digits.isdigit() or len(digits) < 13 or len(digits) > 19:
            return False
        
        # Luhn algorithm
        total = 0
        reverse_digits = digits[::-1]
        
        for i, digit in enumerate(reverse_digits):
            n = int(digit)
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n -= 9
            total += n
        
        return total % 10 == 0
    
    def _calculate_confidence(self, category: PrivacyCategory, text: str) -> float:
        """Calculate confidence score for detection"""
        base_confidence = {
            PrivacyCategory.API_KEY: 0.95,
            PrivacyCategory.AWS_SECRET: 0.98,
            PrivacyCategory.PASSWORD: 0.85,
            PrivacyCategory.CREDIT_CARD: 0.95,
            PrivacyCategory.SSN: 0.95,
            PrivacyCategory.EMAIL: 0.90,
            PrivacyCategory.PHONE: 0.85,
            PrivacyCategory.BANK_ACCOUNT: 0.90,
            PrivacyCategory.PRIVATE_KEY: 0.98,
            PrivacyCategory.JWT_TOKEN: 0.95,
            PrivacyCategory.OAUTH_TOKEN: 0.90,
            PrivacyCategory.DATABASE_CONNECTION: 0.98,
            PrivacyCategory.IP_ADDRESS: 0.70,
            PrivacyCategory.MEDICAL_RECORD: 0.85,
            PrivacyCategory.BIOMETRIC: 0.90,
            PrivacyCategory.PASSPORT: 0.90,
            PrivacyCategory.DRIVERS_LICENSE: 0.85,
            PrivacyCategory.DATE_OF_BIRTH: 0.70,
            PrivacyCategory.ADDRESS: 0.75,
        }
        
        confidence = base_confidence.get(category, 0.70)
        
        # Adjust based on context
        if len(text) < 6:
            confidence *= 0.7
        elif len(text) > 100:
            confidence *= 0.8
        
        return min(confidence, 1.0)
    
    def _mask_value(self, category: PrivacyCategory, value: str) -> str:
        """Mask sensitive value for logging"""
        if len(value) <= 4:
            return "***"
        
        # Show first 2 and last 2 characters
        return f"{value[:2]}...{value[-2:]}"
    
    def _calculate_privacy_score(self, violations: List[PrivacyViolation]) -> float:
        """Calculate overall privacy violation score"""
        if not violations:
            return 0.0
        
        # Weight by severity
        severity_weights = {
            'critical': 1.0,
            'high': 0.8,
            'medium': 0.5,
            'low': 0.3
        }
        
        max_score = 0.0
        total_score = 0.0
        
        for violation in violations:
            weight = severity_weights.get(violation.severity, 0.5)
            weighted_score = violation.confidence * weight
            max_score = max(max_score, weighted_score)
            total_score += weighted_score
        
        # Combine max risk with cumulative risk
        avg_score = total_score / len(violations)
        final_score = max_score * 0.7 + avg_score * 0.3
        
        return min(final_score, 1.0)
    
    def _determine_risk_level(self, privacy_score: float, violations: List[PrivacyViolation]) -> str:
        """Determine overall risk level"""
        # Check for critical violations
        critical_categories = {
            PrivacyCategory.API_KEY,
            PrivacyCategory.AWS_SECRET,
            PrivacyCategory.PASSWORD,
            PrivacyCategory.CREDIT_CARD,
            PrivacyCategory.SSN,
            PrivacyCategory.PRIVATE_KEY,
            PrivacyCategory.DATABASE_CONNECTION,
            PrivacyCategory.BIOMETRIC,
            PrivacyCategory.PASSPORT
        }
        
        has_critical = any(v.category in critical_categories for v in violations)
        
        if has_critical or privacy_score >= 0.9:
            return "critical"
        elif privacy_score >= 0.7:
            return "high"
        elif privacy_score >= 0.5:
            return "medium"
        elif privacy_score >= 0.3:
            return "low"
        else:
            return "safe"
    
    def _generate_explanation(self, violations: List[PrivacyViolation]) -> str:
        """Generate human-readable explanation"""
        if not violations:
            return "No privacy violations detected. Content is safe to process."
        
        categories = {}
        for v in violations:
            cat_name = v.category.value.replace('_', ' ').title()
            if cat_name not in categories:
                categories[cat_name] = 0
            categories[cat_name] += 1
        
        parts = []
        for cat, count in categories.items():
            parts.append(f"{count} {cat}{'s' if count > 1 else ''}")
        
        violation_summary = ", ".join(parts)
        
        return (
            f"Privacy violation detected: {violation_summary}. "
            f"This content contains confidential information that should not be processed. "
            f"RECOMMENDATION: BLOCK and sanitize input before proceeding."
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get detection statistics"""
        return {
            'total_detections': self.total_detections,
            'detections_by_category': {
                cat.value: count 
                for cat, count in self.category_counts.items() 
                if count > 0
            },
            'patterns_loaded': sum(len(config['patterns']) for config in self.patterns.values())
        }


# Demo and testing
if __name__ == "__main__":
    print("🔒 Enhanced Privacy Violation Detector")
    print("=" * 80)
    
    detector = EnhancedPrivacyDetector()
    
    # Test cases
    test_cases = [
        # API Keys
        "My OpenAI API key is sk-proj-abc123def456ghi789jkl012mno345pqr678",
        "AWS credentials: AKIAIOSFODNN7EXAMPLE",
        
        # Credit Cards
        "My credit card is 4532-1234-5678-9010 CVV 123",
        "Card number: 5425233430109903",
        
        # SSN
        "John Smith SSN: 123-45-6789",
        
        # Passwords
        'password = "MySecretPass123!"',
        "token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abc",
        
        # Database connections
        "postgresql://user:pass123@localhost:5432/mydb",
        
        # Email and Phone
        "Contact me at john.doe@example.com or 555-123-4567",
        
        # Safe content
        "What is the capital of France?",
        "How do I reset my password?",
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}: {test[:60]}{'...' if len(test) > 60 else ''}")
        print('-' * 80)
        
        result = detector.detect(test)
        
        print(f"Has Violations: {result.has_violations}")
        print(f"Risk Level: {result.risk_level.upper()}")
        print(f"Privacy Score: {result.privacy_score:.2f}")
        
        if result.has_violations:
            print(f"\nViolations Found: {len(result.violations)}")
            for v in result.violations:
                print(f"  - {v.description} (confidence: {v.confidence:.2f}, severity: {v.severity})")
                print(f"    Masked: {v.masked_value}")
            
            print(f"\nExplanation: {result.explanation}")
            
            if result.redacted_text:
                print(f"\nRedacted Text: {result.redacted_text[:100]}...")
    
    print("\n" + "=" * 80)
    print("\n📊 Detection Statistics:")
    stats = detector.get_statistics()
    print(f"Total detections: {stats['total_detections']}")
    print(f"Patterns loaded: {stats['patterns_loaded']}")
    print(f"Categories detected: {len(stats['detections_by_category'])}")
    for cat, count in stats['detections_by_category'].items():
        print(f"  - {cat}: {count}")
