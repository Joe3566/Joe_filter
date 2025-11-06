#!/usr/bin/env python3
"""
Test Suite for Enhanced Privacy Violation Detector
Tests various PII and confidential information detection scenarios
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from enhanced_privacy_detector import EnhancedPrivacyDetector, PrivacyCategory


def test_privacy_detector():
    """Comprehensive test suite for privacy detector"""
    
    print("🔒 Privacy Violation Detector - Comprehensive Test Suite")
    print("=" * 100)
    
    detector = EnhancedPrivacyDetector()
    
    test_cases = [
        # Critical - API Keys
        {
            'name': 'OpenAI API Key',
            'text': 'Use this API key: sk-proj-1234567890abcdefghijklmnopqrstuvwxyz123456',
            'should_detect': True,
            'expected_category': PrivacyCategory.API_KEY,
            'severity': 'critical'
        },
        {
            'name': 'AWS Access Key',
            'text': 'My AWS key is AKIAIOSFODNN7EXAMPLE',
            'should_detect': True,
            'expected_category': PrivacyCategory.API_KEY,
            'severity': 'critical'
        },
        {
            'name': 'GitHub Token',
            'text': 'GitHub PAT: ghp_1234567890abcdefghijklmnopqrstuvwx',
            'should_detect': True,
            'expected_category': PrivacyCategory.API_KEY,
            'severity': 'critical'
        },
        
        # Critical - Passwords
        {
            'name': 'Password Assignment',
            'text': 'password = "MySecretPass123!"',
            'should_detect': True,
            'expected_category': PrivacyCategory.PASSWORD,
            'severity': 'critical'
        },
        {
            'name': 'Database Credentials',
            'text': 'Connection: postgresql://admin:Pass1234@db.example.com:5432/mydb',
            'should_detect': True,
            'expected_category': PrivacyCategory.DATABASE_CONNECTION,
            'severity': 'critical'
        },
        
        # Critical - Credit Cards
        {
            'name': 'Valid Visa Card',
            'text': 'Card number: 4532-1234-5678-9013',  # Valid Luhn checksum
            'should_detect': True,
            'expected_category': PrivacyCategory.CREDIT_CARD,
            'severity': 'critical'
        },
        {
            'name': 'Mastercard with CVV',
            'text': 'Pay with 5425-2334-3010-9903 CVV 123',
            'should_detect': True,
            'expected_category': PrivacyCategory.CREDIT_CARD,
            'severity': 'critical'
        },
        
        # Critical - SSN
        {
            'name': 'Social Security Number',
            'text': 'Employee SSN: 123-45-6789',
            'should_detect': True,
            'expected_category': PrivacyCategory.SSN,
            'severity': 'critical'
        },
        
        # High - OAuth/JWT Tokens
        {
            'name': 'JWT Token',
            'text': 'Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abc123',
            'should_detect': True,
            'expected_category': PrivacyCategory.JWT_TOKEN,
            'severity': 'high'
        },
        {
            'name': 'OAuth Access Token',
            'text': 'access_token = "ya29.a0AfH6SMBxyz123abc456def"',
            'should_detect': True,
            'expected_category': PrivacyCategory.OAUTH_TOKEN,
            'severity': 'high'
        },
        
        # Medium - Email and Phone
        {
            'name': 'Email Address',
            'text': 'Contact: john.doe@company.com',
            'should_detect': True,
            'expected_category': PrivacyCategory.EMAIL,
            'severity': 'medium'
        },
        {
            'name': 'US Phone Number',
            'text': 'Call me at (555) 123-4567',
            'should_detect': True,
            'expected_category': PrivacyCategory.PHONE,
            'severity': 'medium'
        },
        
        # Critical - Private Keys
        {
            'name': 'RSA Private Key',
            'text': '-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA...',
            'should_detect': True,
            'expected_category': PrivacyCategory.PRIVATE_KEY,
            'severity': 'critical'
        },
        
        # High - Bank Accounts
        {
            'name': 'Bank Account Number',
            'text': 'account_number = 1234567890',
            'should_detect': True,
            'expected_category': PrivacyCategory.BANK_ACCOUNT,
            'severity': 'critical'
        },
        {
            'name': 'Routing Number',
            'text': 'routing_number = 021000021',
            'should_detect': True,
            'expected_category': PrivacyCategory.BANK_ACCOUNT,
            'severity': 'critical'
        },
        
        # High - Medical Records
        {
            'name': 'Medical Record Number',
            'text': 'patient_id = MRN123456',
            'should_detect': True,
            'expected_category': PrivacyCategory.MEDICAL_RECORD,
            'severity': 'high'
        },
        
        # SAFE - No violations
        {
            'name': 'Safe Query - Question',
            'text': 'What is the capital of France?',
            'should_detect': False,
            'expected_category': None,
            'severity': None
        },
        {
            'name': 'Safe Query - Help Request',
            'text': 'How do I reset my password?',
            'should_detect': False,
            'expected_category': None,
            'severity': None
        },
        {
            'name': 'Safe Query - Programming',
            'text': 'Write a Python function to sort a list',
            'should_detect': False,
            'expected_category': None,
            'severity': None
        },
        {
            'name': 'Safe Query - General',
            'text': 'Explain machine learning concepts',
            'should_detect': False,
            'expected_category': None,
            'severity': None
        },
    ]
    
    passed = 0
    failed = 0
    total = len(test_cases)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*100}")
        print(f"Test {i}/{total}: {test['name']}")
        print(f"Input: {test['text'][:80]}{'...' if len(test['text']) > 80 else ''}")
        print('-' * 100)
        
        result = detector.detect(test['text'])
        
        # Check detection
        detected = result.has_violations
        expected = test['should_detect']
        
        test_passed = True
        
        if detected != expected:
            test_passed = False
            print(f"❌ FAILED: Expected detection={expected}, got detection={detected}")
        else:
            print(f"✓ Detection: {detected} (as expected)")
        
        # Show details
        print(f"  Risk Level: {result.risk_level.upper()}")
        print(f"  Privacy Score: {result.privacy_score:.2f}")
        
        if result.has_violations:
            print(f"  Violations Found: {len(result.violations)}")
            for v in result.violations[:3]:  # Show first 3
                print(f"    - {v.description}")
                print(f"      Category: {v.category.value}")
                print(f"      Severity: {v.severity}")
                print(f"      Confidence: {v.confidence:.2f}")
                print(f"      Masked Value: {v.masked_value}")
            
            if len(result.violations) > 3:
                print(f"    ... and {len(result.violations) - 3} more")
            
            # Check category if expected
            if test['expected_category']:
                found_expected = any(v.category == test['expected_category'] for v in result.violations)
                if not found_expected:
                    test_passed = False
                    print(f"❌ Expected category {test['expected_category'].value} not found")
                else:
                    print(f"  ✓ Found expected category: {test['expected_category'].value}")
        
        # Overall result
        if test_passed:
            print(f"\n✅ PASS")
            passed += 1
        else:
            print(f"\n❌ FAIL")
            failed += 1
    
    # Summary
    print(f"\n{'='*100}")
    print(f"\n📊 TEST SUMMARY")
    print(f"{'='*100}")
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed} ({passed/total*100:.1f}%)")
    print(f"❌ Failed: {failed} ({failed/total*100:.1f}%)")
    
    # Statistics
    print(f"\n📈 DETECTOR STATISTICS")
    print(f"{'='*100}")
    stats = detector.get_statistics()
    print(f"Total Detections: {stats['total_detections']}")
    print(f"Patterns Loaded: {stats['patterns_loaded']}")
    print(f"Categories Detected: {len(stats['detections_by_category'])}")
    
    if stats['detections_by_category']:
        print(f"\nDetections by Category:")
        for cat, count in sorted(stats['detections_by_category'].items(), key=lambda x: x[1], reverse=True):
            print(f"  - {cat.replace('_', ' ').title()}: {count}")
    
    print(f"\n{'='*100}")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! Privacy detector is working correctly.")
    else:
        print(f"⚠️  {failed} test(s) failed. Review the results above.")
    
    return failed == 0


if __name__ == "__main__":
    success = test_privacy_detector()
    sys.exit(0 if success else 1)
