#!/usr/bin/env python3
"""
Quick Test Script for LLM Compliance Filter

A simple one-liner test script to quickly verify the system is working.
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from src.compliance_filter import ComplianceFilter
    
    print("🛡️  LLM Compliance Filter - Quick Test")
    print("=" * 40)
    
    # Initialize filter
    print("🔄 Initializing filter...")
    filter = ComplianceFilter()
    print("✅ Filter ready!")
    print()
    
    # Test cases
    test_cases = [
        ("What is Python?", "Safe prompt"),
        ("My email is test@example.com", "Privacy violation"),
        ("Call me at 555-123-4567", "Phone number"),
        ("My SSN is 123-45-6789", "High-risk PII")
    ]
    
    for prompt, description in test_cases:
        result = filter.check_compliance(prompt)
        action_emoji = {"allow": "🟢", "warn": "🟡", "block": "🔴"}
        
        print(f"{action_emoji.get(result.action.value, '⚪')} {description}")
        print(f"   Prompt: '{prompt}'")
        print(f"   Action: {result.action.value.upper()}")
        print(f"   Score: {result.overall_score:.2f}")
        print()
    
    print("🎉 All tests completed successfully!")
    print("💡 Run 'python desktop_demo.py' for the full interactive demo.")
    
except ImportError as e:
    print(f"❌ Error: {e}")
    print("Make sure you're in the project directory and dependencies are installed.")
except Exception as e:
    print(f"❌ Unexpected error: {e}")