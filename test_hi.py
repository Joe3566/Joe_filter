import sys
sys.path.insert(0, 'src')

from enhanced_jailbreak_detector import EnhancedJailbreakDetector

d = EnhancedJailbreakDetector()
r = d.analyze_enhanced('hi')

print(f'Jailbreak: {r.is_jailbreak}')
print(f'Confidence: {r.confidence:.3f}')
print(f'Severity: {r.severity.value}')
print(f'Patterns: {r.patterns_detected}')
print(f'Techniques: {[t.value for t in r.techniques]}')

if r.semantic_analysis:
    print(f'\nSemantic Analysis:')
    print(f'  Toxic: {r.semantic_analysis["is_toxic"]}')
    print(f'  Confidence: {r.semantic_analysis["confidence"]:.3f}')
    print(f'  Threat Score: {r.semantic_analysis["threat_score"]:.3f}')
    print(f'  Category: {r.semantic_analysis["primary_category"]}')

if r.context_threat_analysis:
    print(f'\nContext Threat:')
    print(f'  Detected: {r.context_threat_analysis["detected"]}')
    print(f'  Confidence: {r.context_threat_analysis["confidence"]:.3f}')
