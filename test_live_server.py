#!/usr/bin/env python3
"""
Test the live server to see what's being flagged
"""

import requests
import json

# Test cases - all should be safe
safe_queries = [
    "What is the capital of France?",
    "How do I learn Python programming?",
    "Explain machine learning",
    "What's the weather like today?",
    "Tell me about photosynthesis",
]

print("🧪 Testing Live Server at http://localhost:5000")
print("=" * 80)

flagged_count = 0

for i, query in enumerate(safe_queries, 1):
    print(f"\nTest {i}: {query}")
    print("-" * 80)
    
    try:
        response = requests.post(
            "http://localhost:5000/api/analyze",
            json={"text": query},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            
            is_compliant = result.get('is_compliant', True)
            threat_level = result.get('threat_level', 'unknown')
            risk_score = result.get('overall_risk_score', 0)
            
            if not is_compliant:
                flagged_count += 1
                print(f"❌ FLAGGED AS VIOLATION")
                print(f"   Threat Level: {threat_level}")
                print(f"   Risk Score: {risk_score:.2f}")
                print(f"   Violations: {result.get('violations', [])}")
                
                # Show which detector flagged it
                detections = result.get('detections', {})
                if detections.get('openai', {}).get('flagged'):
                    print(f"   ⚠️ OpenAI Moderation: FLAGGED")
                    print(f"      Categories: {detections['openai'].get('flagged_categories', [])}")
                
                if detections.get('jailbreak', {}).get('detected'):
                    print(f"   ⚠️ Jailbreak Detection: YES")
                    print(f"      Confidence: {detections['jailbreak'].get('confidence', 0):.2f}")
                    print(f"      Patterns: {detections['jailbreak'].get('patterns', [])}")
                
                if detections.get('ml_compliance', {}).get('detected'):
                    print(f"   ⚠️ ML Filter: VIOLATION")
                    print(f"      Type: {detections['ml_compliance'].get('violation_type', 'unknown')}")
            else:
                print(f"✅ PASS - Correctly identified as safe")
                print(f"   Threat Level: {threat_level}")
                print(f"   Risk Score: {risk_score:.3f}")
        else:
            print(f"❌ Server returned error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server at http://localhost:5000")
        print("   Make sure the server is running!")
        break
    except Exception as e:
        print(f"❌ ERROR: {e}")

print("\n" + "=" * 80)
print(f"\n📊 SUMMARY")
print(f"Total Tests: {len(safe_queries)}")
print(f"✅ Passed: {len(safe_queries) - flagged_count}")
print(f"❌ Incorrectly Flagged: {flagged_count}")

if flagged_count > 0:
    print(f"\n⚠️ WARNING: {flagged_count} safe queries were incorrectly flagged!")
    print("\nPossible causes:")
    print("1. OpenAI Moderation API hitting rate limits (429 errors)")
    print("2. ML model being too aggressive")
    print("3. Detection thresholds need adjustment")
    print("\nSuggestions:")
    print("- Disable OpenAI API temporarily (unset OPENAI_API_KEY)")
    print("- Check server logs for errors")
    print("- Review detection settings")
else:
    print("\n✅ All safe queries passed correctly!")
