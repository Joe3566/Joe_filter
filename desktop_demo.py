#!/usr/bin/env python3
"""
LLM Compliance Filter Desktop Demo

This script demonstrates the compliance filter capabilities with various test cases.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import time

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from src.compliance_filter import ComplianceFilter, ComplianceAction
    from src.feedback_system import FeedbackSystem, FeedbackType
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running this from the project root directory.")
    sys.exit(1)

def print_separator(title=""):
    """Print a nice separator with optional title."""
    width = 80
    if title:
        padding = (width - len(title) - 2) // 2
        print("=" * padding + f" {title} " + "=" * padding)
    else:
        print("=" * width)

def print_result(prompt, result, index=None):
    """Print a compliance check result in a nice format."""
    prefix = f"{index}. " if index else ""
    
    # Color coding for actions
    action_colors = {
        ComplianceAction.ALLOW: "🟢",
        ComplianceAction.WARN: "🟡", 
        ComplianceAction.BLOCK: "🔴"
    }
    
    color = action_colors.get(result.action, "⚪")
    
    print(f"\n{prefix}📝 Prompt: '{prompt[:60]}{'...' if len(prompt) > 60 else ''}'")
    print(f"   {color} Action: {result.action.value.upper()}")
    print(f"   📊 Overall Score: {result.overall_score:.2f}")
    print(f"   🎭 Hate Speech: {result.hate_speech_score:.2f}")
    print(f"   🔒 Privacy: {result.privacy_score:.2f}")
    print(f"   ⏱️  Processing Time: {result.processing_time:.3f}s")
    
    if result.privacy_violations:
        print(f"   🚨 Privacy Violations ({len(result.privacy_violations)}):")
        for violation in result.privacy_violations:
            print(f"      - {violation.violation_type.value}: '{violation.text_span}' (confidence: {violation.confidence:.2f})")
    
    print(f"   💭 Reasoning: {result.reasoning}")

def run_demo():
    """Run the compliance filter demonstration."""
    print_separator("🛡️  LLM COMPLIANCE FILTER DESKTOP DEMO")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Initialize the compliance filter
        print("🔄 Initializing Compliance Filter...")
        start_time = time.time()
        filter = ComplianceFilter()
        init_time = time.time() - start_time
        print(f"✅ Filter initialized successfully in {init_time:.2f}s")
        print(f"📋 Configuration loaded from: config/default.yaml")
        print()
        
        # Initialize feedback system
        feedback_system = FeedbackSystem(filter.config)
        
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False
    
    # Test cases organized by category
    test_cases = {
        "✅ Safe Prompts": [
            "What is the capital of France?",
            "How do I bake a chocolate cake?",
            "Explain machine learning in simple terms.",
            "What's the weather like today?",
            "Tell me a joke about programming."
        ],
        
        "🔒 Privacy Violations": [
            "My email is john.doe@example.com",
            "Call me at (555) 123-4567",
            "My SSN is 123-45-6789",
            "Contact me at sarah@company.com and my phone is 555-0123",
            "My credit card number is 4532-1234-5678-9012"
        ],
        
        "🎭 Potential Hate Speech": [
            "I really dislike that policy",
            "This is absolutely terrible content", 
            "That person is completely wrong about everything"
        ],
        
        "🚨 High-Risk Combinations": [
            "My email is test@example.com and SSN is 123-45-6789",
            "Call me at (555) 123-4567, my card is 4532-1234-5678-9012",
            "I live at 123 Main St, email: user@domain.com, SSN: 987-65-4321"
        ]
    }
    
    # Run tests for each category
    total_tests = sum(len(cases) for cases in test_cases.values())
    test_count = 0
    
    for category, prompts in test_cases.items():
        print_separator(category)
        
        for i, prompt in enumerate(prompts, 1):
            test_count += 1
            print(f"\n[{test_count}/{total_tests}] Testing prompt {i} of {len(prompts)}")
            
            try:
                result = filter.check_compliance(prompt)
                print_result(prompt, result, i)
                
                # Simulate feedback for interesting cases
                if result.action in [ComplianceAction.WARN, ComplianceAction.BLOCK]:
                    if feedback_system.should_request_feedback(result):
                        print(f"   💬 System suggests requesting user feedback for this case")
                
            except Exception as e:
                print(f"❌ Error processing prompt: {e}")
        
        print()
    
    # Performance summary
    print_separator("📈 PERFORMANCE SUMMARY")
    stats = filter.get_performance_stats()
    
    print(f"📊 Total Compliance Checks: {stats.get('total_checks', 'N/A')}")
    print(f"⏱️  Average Processing Time: {stats.get('average_processing_time', 'N/A'):.3f}s")
    print(f"📋 Action Distribution:")
    
    action_dist = stats.get('action_distribution', {})
    for action, count in action_dist.items():
        percentage = (count / stats.get('total_checks', 1)) * 100
        print(f"   {action}: {count} ({percentage:.1f}%)")
    
    # System information
    print()
    print_separator("🖥️  SYSTEM INFORMATION")
    print(f"🐍 Python Version: {sys.version.split()[0]}")
    print(f"📁 Working Directory: {os.getcwd()}")
    print(f"🧠 Hate Speech Model: {filter.hate_speech_detector.model_name if filter.hate_speech_detector else 'Not Available'}")
    print(f"🔧 Privacy Checks Enabled: {len(filter.privacy_detector.patterns)} pattern types")
    print(f"⚖️  Scoring Method: {filter.scoring_method}")
    print(f"📊 Weights: Hate Speech={filter.weights.get('hate_speech', 'N/A')}, Privacy={filter.weights.get('privacy', 'N/A')}")
    print(f"🚦 Thresholds: Block≥{filter.thresholds.get('block_threshold', 'N/A')}, Warn≥{filter.thresholds.get('warn_threshold', 'N/A')}")
    
    print()
    print_separator("✅ DEMO COMPLETED SUCCESSFULLY")
    print(f"🕐 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📝 All test cases processed. The compliance filter is working correctly!")
    print()
    print("💡 To use the filter in your own code:")
    print("   from src.compliance_filter import ComplianceFilter")
    print("   filter = ComplianceFilter()")
    print("   result = filter.check_compliance('Your prompt here')")
    print("   print(f'Action: {result.action}, Score: {result.overall_score}')")
    
    return True

def interactive_mode():
    """Run an interactive mode where users can test their own prompts."""
    print_separator("🎮 INTERACTIVE MODE")
    print("Enter prompts to test (type 'quit' or 'exit' to stop):")
    print()
    
    try:
        filter = ComplianceFilter()
    except Exception as e:
        print(f"❌ Failed to initialize filter: {e}")
        return
    
    while True:
        try:
            prompt = input("📝 Enter prompt: ").strip()
            
            if not prompt:
                continue
                
            if prompt.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            print("🔄 Processing...")
            result = filter.check_compliance(prompt)
            print_result(prompt, result)
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🛡️  LLM Compliance Filter - Desktop Demo")
    print("=" * 50)
    print()
    print("Choose a mode:")
    print("1. 🔬 Run full demo with test cases")
    print("2. 🎮 Interactive mode - test your own prompts")
    print("3. 📊 Both demo and interactive")
    print()
    
    try:
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == "1":
            success = run_demo()
            if not success:
                sys.exit(1)
                
        elif choice == "2":
            interactive_mode()
            
        elif choice == "3":
            success = run_demo()
            if success:
                print("\n" + "="*50)
                interactive_mode()
            else:
                sys.exit(1)
                
        else:
            print("❌ Invalid choice. Please run the script again.")
            
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)