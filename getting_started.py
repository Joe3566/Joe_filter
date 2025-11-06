#!/usr/bin/env python3
"""
Getting Started with LLM Compliance Filter

This script shows you exactly how to integrate the compliance filter
into your existing projects with real LLM APIs.
"""

import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.compliance_filter import ComplianceFilter


def setup_instructions():
    """Show setup instructions for different scenarios."""
    print("🚀 LLM Compliance Filter - Getting Started Guide")
    print("=" * 80)
    
    print("\n📦 1. INSTALLATION")
    print("-" * 40)
    print("All dependencies are already installed! ✅")
    print("You can start using the filter right away.")
    
    print("\n🔧 2. BASIC USAGE")
    print("-" * 40)
    
    # Basic example
    filter = ComplianceFilter()
    
    # Test safe content
    safe_result = filter.check_compliance("What's the weather like today?")
    print(f"Safe content: {safe_result.action.value} (score: {safe_result.overall_score:.3f})")
    
    # Test risky content
    risky_result = filter.check_compliance("My email is user@example.com")
    print(f"Risky content: {risky_result.action.value} (score: {risky_result.overall_score:.3f})")
    print(f"Violations found: {len(risky_result.privacy_violations)}")


def openai_integration_example():
    """Show how to integrate with OpenAI."""
    print("\n🤖 3. OPENAI INTEGRATION")
    print("-" * 40)
    
    print("First install OpenAI:")
    print("pip install openai")
    
    print("\nThen use this pattern:")
    print('''
import os
import openai
from src.compliance_filter import ComplianceFilter

# Set up your API key (never hardcode this!)
openai.api_key = os.getenv("OPENAI_API_KEY")

def safe_openai_completion(prompt, user_id="anonymous"):
    """Safe wrapper for OpenAI API with compliance filtering."""
    
    # Initialize compliance filter
    filter = ComplianceFilter()
    
    # Check compliance first
    compliance_result = filter.check_compliance(prompt)
    
    if compliance_result.action.value == "block":
        return {
            "success": False,
            "message": "Content blocked due to policy violations",
            "reason": compliance_result.reasoning,
            "score": compliance_result.overall_score
        }
    
    try:
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        
        return {
            "success": True,
            "content": response.choices[0].message.content,
            "compliance_score": compliance_result.overall_score,
            "action": compliance_result.action.value
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Usage examples:
# result = safe_openai_completion("What's the weather?")
# result = safe_openai_completion("My email is test@example.com")  # This will be blocked
''')


def anthropic_integration_example():
    """Show how to integrate with Anthropic Claude."""
    print("\n🧠 4. ANTHROPIC CLAUDE INTEGRATION")
    print("-" * 40)
    
    print("First install Anthropic:")
    print("pip install anthropic")
    
    print("\nThen use this pattern:")
    print('''
import os
import anthropic
from src.compliance_filter import ComplianceFilter

class SafeClaudeClient:
    """Safe wrapper for Anthropic Claude with compliance filtering."""
    
    def __init__(self):
        # Set up your API key (never hardcode this!)
        api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.compliance_filter = ComplianceFilter()
    
    def safe_completion(self, prompt, user_id="anonymous"):
        """Generate completion with compliance check."""
        
        # Check compliance first
        compliance_result = self.compliance_filter.check_compliance(prompt)
        
        if compliance_result.action.value == "block":
            return {
                "success": False,
                "message": "Content blocked due to policy violations",
                "violations": len(compliance_result.privacy_violations),
                "score": compliance_result.overall_score
            }
        
        try:
            # Call Claude API
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                "success": True,
                "content": response.content[0].text,
                "compliance_score": compliance_result.overall_score,
                "action": compliance_result.action.value
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Usage:
# claude_client = SafeClaudeClient()
# result = claude_client.safe_completion("Explain quantum physics")
''')


def flask_api_example():
    """Show how to create a Flask API with compliance."""
    print("\n🌐 5. FLASK API INTEGRATION")
    print("-" * 40)
    
    print("Install Flask:")
    print("pip install flask")
    
    print("\nCreate a secure API endpoint:")
    print('''
from flask import Flask, request, jsonify
from src.compliance_filter import ComplianceFilter

app = Flask(__name__)
filter = ComplianceFilter()

@app.route('/api/check-prompt', methods=['POST'])
def check_prompt():
    """API endpoint to check prompt compliance."""
    data = request.get_json()
    prompt = data.get('prompt', '')
    user_id = data.get('user_id', 'anonymous')
    
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400
    
    # Check compliance
    result = filter.check_compliance(prompt)
    
    return jsonify({
        "action": result.action.value,
        "score": result.overall_score,
        "privacy_score": result.privacy_score,
        "hate_speech_score": result.hate_speech_score,
        "violations": len(result.privacy_violations),
        "reasoning": result.reasoning,
        "safe_to_process": result.action.value != "block"
    })

@app.route('/api/safe-completion', methods=['POST'])
def safe_completion():
    """API endpoint for LLM completion with compliance."""
    data = request.get_json()
    prompt = data.get('prompt', '')
    
    # Check compliance first
    compliance_result = filter.check_compliance(prompt)
    
    if compliance_result.action.value == "block":
        return jsonify({
            "blocked": True,
            "reason": compliance_result.reasoning,
            "score": compliance_result.overall_score
        })
    
    # Here you would call your LLM API
    # For demo purposes, we'll return a mock response
    return jsonify({
        "blocked": False,
        "content": f"Mock response to: {prompt[:50]}...",
        "compliance_score": compliance_result.overall_score
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)

# Test with:
# curl -X POST http://localhost:5000/api/check-prompt \\
#      -H "Content-Type: application/json" \\
#      -d '{"prompt": "What is the weather?"}'
''')


def configuration_examples():
    """Show different configuration examples."""
    print("\n⚙️ 6. CONFIGURATION OPTIONS")
    print("-" * 40)
    
    print("You can customize the filter for different use cases:")
    
    print("\nA. High Security (Financial Services):")
    print('''
high_security_config = {
    'compliance': {
        'thresholds': {
            'block_threshold': 0.3,    # Very strict
            'warn_threshold': 0.2,
            'pass_threshold': 0.1
        },
        'weights': {
            'privacy': 0.8,            # Heavily weight privacy
            'hate_speech': 0.2
        }
    }
}

filter = ComplianceFilter(config_dict=high_security_config)
''')
    
    print("\nB. Balanced (General Business):")
    print('''
balanced_config = {
    'compliance': {
        'thresholds': {
            'block_threshold': 0.7,    # Default
            'warn_threshold': 0.5,
            'pass_threshold': 0.2
        },
        'weights': {
            'privacy': 0.6,
            'hate_speech': 0.4
        }
    }
}

filter = ComplianceFilter(config_dict=balanced_config)
''')
    
    print("\nC. Permissive (Internal Tools):")
    print('''
permissive_config = {
    'compliance': {
        'thresholds': {
            'block_threshold': 0.9,    # Very permissive
            'warn_threshold': 0.7,
            'pass_threshold': 0.3
        }
    }
}

filter = ComplianceFilter(config_dict=permissive_config)
''')


def environment_setup():
    """Show how to set up environment variables."""
    print("\n🔐 7. ENVIRONMENT SETUP")
    print("-" * 40)
    
    print("Create a .env file for your API keys:")
    print('''
# .env file
OPENAI_API_KEY=sk-your-openai-api-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
''')
    
    print("\nInstall python-dotenv:")
    print("pip install python-dotenv")
    
    print("\nLoad environment variables:")
    print('''
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Use them securely
openai_key = os.getenv("OPENAI_API_KEY")
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
''')


def testing_tips():
    """Show testing recommendations."""
    print("\n🧪 8. TESTING RECOMMENDATIONS")
    print("-" * 40)
    
    print("Test with these categories of content:")
    print('''
test_prompts = [
    # Safe content
    "What's the weather like today?",
    "Explain machine learning",
    "Write a story about dragons",
    
    # Privacy violations
    "My email is user@example.com",
    "Call me at (555) 123-4567",
    "My SSN is 123-45-6789",
    
    # Borderline content
    "I work at a tech company",
    "Send me an email",
    "My friend John told me",
    
    # High-risk content
    "Credit card: 4532-1234-5678-9012",
    "Bank account: 123456789",
    "API key: sk-abc123def456"
]

# Test all prompts
filter = ComplianceFilter()
for prompt in test_prompts:
    result = filter.check_compliance(prompt)
    print(f"{result.action.value:5} | {result.overall_score:.3f} | {prompt}")
''')


def production_checklist():
    """Show production deployment checklist."""
    print("\n✅ 9. PRODUCTION CHECKLIST")
    print("-" * 40)
    
    checklist_items = [
        "✅ API keys stored in environment variables (not in code)",
        "✅ Appropriate thresholds configured for your use case",
        "✅ Logging configured for monitoring and debugging",
        "✅ Error handling implemented for API failures",
        "✅ Rate limiting configured to prevent abuse",
        "✅ Monitoring set up for blocked content patterns",
        "✅ Regular testing with representative content",
        "✅ Documentation for your team on how to use the system",
        "✅ Backup/fallback behavior if compliance service fails",
        "✅ Regular review of compliance decisions and threshold adjustments"
    ]
    
    for item in checklist_items:
        print(f"  {item}")


def next_steps():
    """Show next steps for implementation."""
    print("\n🎯 10. NEXT STEPS")
    print("-" * 40)
    
    print("1. Choose Your LLM Provider:")
    print("   - OpenAI (GPT-3.5/4)")
    print("   - Anthropic (Claude)")
    print("   - Local models (Llama, etc.)")
    
    print("\n2. Set Up API Keys:")
    print("   - Create accounts with your chosen providers")
    print("   - Set up environment variables")
    print("   - Test basic API connectivity")
    
    print("\n3. Configure Thresholds:")
    print("   - Start with default settings")
    print("   - Test with your specific content")
    print("   - Adjust based on your risk tolerance")
    
    print("\n4. Implement Integration:")
    print("   - Use the code examples above")
    print("   - Add error handling and logging")
    print("   - Test thoroughly")
    
    print("\n5. Monitor and Adjust:")
    print("   - Track compliance decisions")
    print("   - Adjust thresholds as needed")
    print("   - Review blocked content patterns")


def main():
    """Run the getting started guide."""
    setup_instructions()
    openai_integration_example()
    anthropic_integration_example()
    flask_api_example()
    configuration_examples()
    environment_setup()
    testing_tips()
    production_checklist()
    next_steps()
    
    print("\n" + "=" * 80)
    print("🎉 YOU'RE READY TO GO!")
    print("=" * 80)
    print("\n💡 Remember:")
    print("- Start simple and iterate")
    print("- Test with real content from your use case")
    print("- Monitor compliance decisions in production")
    print("- Adjust thresholds based on actual usage patterns")
    
    print("\n📞 Need help? Check the WARP.md file for development guidance!")


if __name__ == "__main__":
    main()
