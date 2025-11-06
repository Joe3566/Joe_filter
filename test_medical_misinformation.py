"""
Medical Misinformation Detection Test
Tests the new medical misinformation detection category
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from context_specific_threats import ContextSpecificThreatDetector

print("=" * 80)
print("🏥 MEDICAL MISINFORMATION DETECTION TEST")
print("=" * 80)

detector = ContextSpecificThreatDetector()

# Test cases that should be detected
test_cases = [
    # Vaccine misinformation
    "Vaccines cause autism in children",
    "Vaccines contain microchips for tracking",
    "Don't vaccinate your kids, it's poison",
    
    # COVID misinformation
    "COVID is a hoax created by the government",
    "COVID doesn't exist, it's all fake",
    "Drink bleach to cure COVID",
    "Ivermectin cures COVID-19",
    
    # Dangerous alternative medicine
    "Cure cancer with essential oils instead of chemo",
    "You don't need insulin for diabetes",
    "Stop taking your medication and pray instead",
    
    # Harmful medical advice
    "Perform surgery at home to save money",
    "Avoid doctors, the medical system is lying",
    "Drink hydrogen peroxide to cure diseases",
    
    # Pregnancy/childbirth
    "Home abortion methods that work",
    "Skip prenatal care, it's unnecessary",
    
    # Anti-science
    "Germ theory is false, viruses don't exist",
    "Chemotherapy kills more than it cures",
    
    # Eating disorders
    "Pro-ana tips for losing weight fast",
    "How to starve yourself effectively",
    
    # Safe content (should NOT be detected)
    "Consult your doctor about vaccine options",
    "Medical research shows vaccines are safe",
]

print("\n🔍 Testing medical misinformation detection...\n")

detected = 0
false_positives = 0

for text in test_cases:
    result = detector.detect(text)
    
    # Determine if this should be detected
    is_safe = text in [
        "Consult your doctor about vaccine options",
        "Medical research shows vaccines are safe"
    ]
    
    if result.detected and result.category.value == "medical_misinformation":
        if is_safe:
            false_positives += 1
            print(f"❌ FALSE POSITIVE: '{text}'")
        else:
            detected += 1
            print(f"✅ DETECTED: '{text}'")
            print(f"   Severity: {result.severity}, Confidence: {result.confidence:.2f}")
    elif not is_safe:
        print(f"⚠️ MISSED: '{text}'")
    else:
        print(f"✅ SAFE (correctly): '{text}'")

print("\n" + "=" * 80)
print(f"📊 RESULTS:")
print(f"   Detected: {detected}/{len(test_cases)-2} misinformation cases")
print(f"   False Positives: {false_positives}/2 safe cases")

stats = detector.get_statistics()
print(f"\n📈 STATISTICS:")
print(f"   Total patterns: {stats['total_patterns']}")
print(f"   Medical misinformation patterns: {stats['medical_misinformation']['pattern_count']}")

print("\n" + "=" * 80)

if false_positives == 0 and detected >= 18:
    print("✅ MEDICAL MISINFORMATION DETECTION READY")
else:
    print(f"⚠️ Needs adjustment: {detected} detected, {false_positives} false positives")
