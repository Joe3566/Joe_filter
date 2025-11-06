#!/usr/bin/env python3
"""
🚀 Semantic & Contextual Analysis Demo
Showcase of Innovation #5: Deep meaning and context understanding

This demo demonstrates:
- Semantic meaning beyond keywords
- Contextual frame analysis
- Intent classification
- Implicit threat detection
- Metaphorical understanding
- Cultural context awareness
- Pragmatic meaning extraction
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any

try:
    from src.semantic_contextual_analyzer import SemanticContextualAnalyzer
    SEMANTIC_AVAILABLE = True
    print("✅ Semantic & Contextual Analyzer available")
except ImportError:
    SEMANTIC_AVAILABLE = False
    print("⚠️  Semantic & Contextual Analyzer not available")

class SemanticAnalysisDemo:
    """Demonstration of semantic and contextual analysis capabilities"""
    
    def __init__(self):
        if SEMANTIC_AVAILABLE:
            self.analyzer = SemanticContextualAnalyzer()
            print("🧠 Semantic & Contextual Analysis Engine initialized")
        else:
            self.analyzer = None
            print("⚠️  Running in fallback mode")

    async def run_semantic_demo(self):
        """Run comprehensive semantic analysis demo"""
        
        print("\n" + "="*80)
        print("🧠 SEMANTIC & CONTEXTUAL ANALYSIS ENGINE DEMO")
        print("="*80)
        
        if not SEMANTIC_AVAILABLE:
            print("❌ Semantic analyzer not available. Please install required dependencies:")
            print("   pip install spacy nltk sentence-transformers")
            print("   python -m spacy download en_core_web_sm")
            return
        
        # Demo scenarios showcasing different aspects
        semantic_scenarios = [
            {
                "name": "🎯 Euphemistic Threat Detection",
                "content": "I need to take care of this problem once and for all. Time to handle the situation permanently.",
                "conversation_history": [],
                "user_context": {"user_type": "unknown", "previous_interactions": 0},
                "expected_features": ["euphemisms", "implicit_threats", "veiled_language"]
            },
            {
                "name": "🕰️ Temporal Context Analysis",
                "content": "This is urgent! I need to do something about those people at school tomorrow morning.",
                "conversation_history": [],
                "user_context": {"location_context": "school_area", "time_sensitive": True},
                "expected_features": ["temporal_urgency", "location_context", "threat_planning"]
            },
            {
                "name": "💬 Conversational Escalation",
                "content": "You're really starting to annoy me now. Maybe I should teach you a lesson.",
                "conversation_history": [
                    "Hi, can you help me with something?",
                    "That's not what I wanted to hear.",
                    "You're not being very helpful.",
                    "I'm getting frustrated with you."
                ],
                "user_context": {"conversation_id": "conv_001", "escalating": True},
                "expected_features": ["escalation_pattern", "conversational_context", "implicit_threat"]
            },
            {
                "name": "🎭 Coded Language Detection", 
                "content": "We need to protect our traditional values from those urban youths who don't respect law and order.",
                "conversation_history": [],
                "user_context": {"political_context": True},
                "expected_features": ["coded_language", "bias_detection", "dog_whistles"]
            },
            {
                "name": "🌍 Cultural Context Analysis",
                "content": "No cap, this situation is totally sus. Someone needs to get ratio'd for real.",
                "conversation_history": [],
                "user_context": {"platform": "social_media", "demographic": "gen_z"},
                "expected_features": ["generational_markers", "platform_language", "cultural_references"]
            },
            {
                "name": "🎪 Metaphorical Threat Analysis",
                "content": "It's time to pull the trigger on this operation. We need to bury the competition and cross the line.",
                "conversation_history": [],
                "user_context": {"business_context": True},
                "expected_features": ["metaphors", "business_context", "competitive_language"]
            },
            {
                "name": "🔍 Social Engineering Detection",
                "content": "Trust me, I'm authorized to access this information. It's confidential and urgent - don't tell your supervisor.",
                "conversation_history": [],
                "user_context": {"impersonation_attempt": True, "credential_harvesting": True},
                "expected_features": ["social_engineering", "authority_claims", "secrecy_pressure"]
            },
            {
                "name": "✅ Legitimate Academic Inquiry",
                "content": "I'm researching semantic analysis techniques for my PhD thesis on computational linguistics and NLP.",
                "conversation_history": [],
                "user_context": {"academic_context": True, "research_purpose": True},
                "expected_features": ["informational_intent", "academic_language", "legitimate_purpose"]
            }
        ]
        
        print(f"🔍 Analyzing {len(semantic_scenarios)} scenarios for semantic and contextual understanding...")
        
        # Process each scenario
        for i, scenario in enumerate(semantic_scenarios, 1):
            print(f"\n{'='*20} SEMANTIC SCENARIO {i}: {scenario['name']} {'='*20}")
            print(f"📝 Content: {scenario['content']}")
            print(f"💭 Context: {scenario['user_context']}")
            if scenario['conversation_history']:
                print(f"🗣️  History: {len(scenario['conversation_history'])} previous messages")
            
            # Perform semantic analysis
            start_time = time.time()
            result = await self.analyzer.analyze_semantic_context(
                text=scenario['content'],
                conversation_history=scenario['conversation_history'],
                user_context=scenario['user_context']
            )
            analysis_time = time.time() - start_time
            
            # Display comprehensive results
            self._display_semantic_results(result, scenario['expected_features'])
            
            print(f"⏱️  Processing Time: {result.processing_time_ms:.1f}ms")
            print(f"🎯 Overall Confidence: {result.confidence_score:.2f}")
            
            # Small delay for readability
            await asyncio.sleep(1)
        
        # Display system capabilities
        await self._display_system_capabilities()

    def _display_semantic_results(self, result, expected_features: List[str]):
        """Display detailed semantic analysis results"""
        
        print(f"\n🧠 SEMANTIC ANALYSIS RESULTS:")
        
        # Semantic Annotations
        if result.semantic_annotations:
            print(f"\n📝 Semantic Annotations ({len(result.semantic_annotations)}):")
            for annotation in result.semantic_annotations:
                print(f"   • {annotation.text} → {annotation.semantic_type} (confidence: {annotation.confidence:.2f})")
                if annotation.implicit_meanings:
                    print(f"     Implicit: {', '.join(annotation.implicit_meanings)}")
                if annotation.related_concepts:
                    print(f"     Related: {', '.join(annotation.related_concepts)}")
        else:
            print(f"\n📝 Semantic Annotations: None detected")
        
        # Contextual Frames
        if result.contextual_frames:
            print(f"\n🔍 Contextual Frames ({len(result.contextual_frames)}):")
            for frame in result.contextual_frames:
                print(f"   • {frame.frame_type.value}: {frame.relevance_score:.2f}")
                for key, value in frame.context_elements.items():
                    if isinstance(value, (list, dict)):
                        print(f"     {key}: {json.dumps(value)[:100]}...")
                    else:
                        print(f"     {key}: {value}")
        else:
            print(f"\n🔍 Contextual Frames: None detected")
        
        # Intent Classification
        if result.intent_classification:
            print(f"\n🎯 Intent Classification:")
            sorted_intents = sorted(result.intent_classification.items(), key=lambda x: x[1], reverse=True)
            for intent, score in sorted_intents[:5]:  # Top 5 intents
                print(f"   • {intent}: {score:.2f}")
        else:
            print(f"\n🎯 Intent Classification: No clear intent detected")
        
        # Implicit Threat Indicators
        if result.implicit_threat_indicators:
            print(f"\n⚠️  Implicit Threats ({len(result.implicit_threat_indicators)}):")
            for threat in result.implicit_threat_indicators:
                print(f"   • {threat}")
        else:
            print(f"\n⚠️  Implicit Threats: None detected")
        
        # Metaphorical Mappings
        if result.metaphorical_mappings:
            print(f"\n🎭 Metaphorical Analysis:")
            for metaphor, meaning in result.metaphorical_mappings.items():
                print(f"   • '{metaphor}' → {meaning}")
        else:
            print(f"\n🎭 Metaphorical Analysis: No metaphors detected")
        
        # Semantic Similarities
        if result.semantic_similarity_scores:
            print(f"\n📊 Semantic Similarities:")
            high_similarities = [(k, v) for k, v in result.semantic_similarity_scores.items() if v > 0.3]
            for pattern, score in high_similarities:
                print(f"   • {pattern}: {score:.3f}")
        
        # Pragmatic Meaning
        print(f"\n💭 Pragmatic Meaning: {result.pragmatic_meaning}")
        
        # Expected vs Detected Features
        print(f"\n✓ Expected Features Analysis:")
        detected_types = set()
        
        # Collect detected feature types
        for annotation in result.semantic_annotations:
            detected_types.add(annotation.semantic_type)
        
        for frame in result.contextual_frames:
            detected_types.add(frame.frame_type.value)
        
        if result.implicit_threat_indicators:
            detected_types.add("implicit_threats")
        
        if result.metaphorical_mappings:
            detected_types.add("metaphors")
        
        for expected in expected_features:
            detected = any(expected.lower() in str(dt).lower() for dt in detected_types)
            status = "✅" if detected else "⚠️"
            print(f"   {status} {expected}: {'Detected' if detected else 'Not detected'}")

    async def _display_system_capabilities(self):
        """Display system capabilities and statistics"""
        
        print(f"\n{'='*25} SEMANTIC SYSTEM CAPABILITIES {'='*25}")
        
        stats = self.analyzer.get_semantic_statistics()
        
        print(f"🔧 Available Models:")
        for model, available in stats['models_available'].items():
            status = "✅" if available else "❌"
            print(f"   {status} {model.upper()}: {'Available' if available else 'Not available'}")
        
        print(f"\n📚 Knowledge Bases:")
        for kb, count in stats['knowledge_bases'].items():
            print(f"   • {kb.replace('_', ' ').title()}: {count}")
        
        print(f"\n🧠 Analysis Capabilities:")
        for capability, available in stats['analysis_capabilities'].items():
            status = "✅" if available else "❌"
            print(f"   {status} {capability.replace('_', ' ').title()}")
        
        print(f"\n💾 Cache Statistics:")
        for cache, size in stats['cache_statistics'].items():
            print(f"   • {cache.replace('_', ' ').title()}: {size} entries")

    async def demonstrate_advanced_features(self):
        """Demonstrate advanced semantic analysis features"""
        
        print(f"\n{'='*25} ADVANCED SEMANTIC FEATURES {'='*25}")
        
        # Advanced feature demonstrations
        advanced_examples = [
            {
                "title": "Multi-layered Threat Detection",
                "content": "It would be terrible if something happened to your nice family. Accidents happen, you know.",
                "features": ["veiled_threats", "conditional_implications", "intimidation_tactics"]
            },
            {
                "title": "Cultural Code-switching",
                "content": "These urban youths with their hip-hop culture are destroying traditional American values.",
                "features": ["coded_racism", "cultural_bias", "nationalist_rhetoric"]
            },
            {
                "title": "Semantic Ambiguity Resolution",
                "content": "I'm going to kill it at the presentation tomorrow. Time to crush the competition.",
                "features": ["positive_metaphors", "business_context", "competitive_language"]
            }
        ]
        
        for example in advanced_examples:
            print(f"\n📊 {example['title']}:")
            print(f"   Content: '{example['content']}'")
            
            result = await self.analyzer.analyze_semantic_context(example['content'])
            
            print(f"   Confidence: {result.confidence_score:.2f}")
            print(f"   Annotations: {len(result.semantic_annotations)}")
            print(f"   Contextual Frames: {len(result.contextual_frames)}")
            print(f"   Implicit Threats: {len(result.implicit_threat_indicators)}")

async def main():
    """Main demo entry point"""
    
    print("🚀 Starting Semantic & Contextual Analysis Demo...")
    
    try:
        demo = SemanticAnalysisDemo()
        
        await demo.run_semantic_demo()
        
        await demo.demonstrate_advanced_features()
        
        print(f"\n🎉 SEMANTIC ANALYSIS DEMO COMPLETE!")
        print("="*80)
        
        print(f"\n💡 KEY CAPABILITIES DEMONSTRATED:")
        print(f"1. 🧠 Deep semantic understanding beyond keyword matching")
        print(f"2. 🔍 Multi-layered contextual frame analysis")
        print(f"3. 🎯 Advanced intent classification and prediction")
        print(f"4. ⚠️  Implicit and veiled threat detection")
        print(f"5. 🎭 Metaphorical language understanding")
        print(f"6. 🌍 Cultural context and generational marker recognition")
        print(f"7. 💭 Pragmatic meaning extraction from conversational context")
        print(f"8. 🔗 Semantic similarity analysis with threat patterns")
        
        print(f"\n🚀 Innovation #5 adds unprecedented understanding capabilities!")
        print(f"   Your compliance filter now understands MEANING, not just words.")
        
    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())