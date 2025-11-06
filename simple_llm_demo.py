#!/usr/bin/env python3
"""
Simplified LLM Integration Demo

This demonstrates the core concepts of integrating the compliance filter 
with LLM APIs without using the problematic LLMIntegration class.
"""

import asyncio
import sys
import json
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.compliance_filter import ComplianceFilter


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    CUSTOM = "custom"


@dataclass
class LLMRequest:
    """Simple LLM request structure."""
    prompt: str
    provider: LLMProvider
    model: str
    user_id: str
    parameters: Dict[str, Any] = None


@dataclass
class LLMResponse:
    """Simple LLM response structure."""
    content: str
    provider: LLMProvider
    model: str
    compliance_passed: bool
    compliance_details: Dict[str, Any] = None


class SimpleLLMIntegration:
    """Simplified LLM integration with compliance filtering."""
    
    def __init__(self, compliance_filter: ComplianceFilter):
        self.compliance_filter = compliance_filter
        self.handlers = {}
        self.stats = {
            'total_requests': 0,
            'blocked_requests': 0,
            'allowed_requests': 0
        }
    
    def register_handler(self, provider: LLMProvider, handler):
        """Register an LLM handler."""
        self.handlers[provider] = handler
    
    async def process_request(self, request: LLMRequest, check_compliance: bool = True) -> LLMResponse:
        """Process an LLM request with optional compliance checking."""
        self.stats['total_requests'] += 1
        
        compliance_details = None
        
        if check_compliance:
            # Check compliance first
            compliance_result = self.compliance_filter.check_compliance(request.prompt)
            
            compliance_details = {
                'action': compliance_result.action.value,
                'overall_score': compliance_result.overall_score,
                'privacy_score': compliance_result.privacy_score,
                'hate_speech_score': compliance_result.hate_speech_score,
                'violations': len(compliance_result.privacy_violations),
                'reasoning': compliance_result.reasoning
            }
            
            # Block if compliance check fails
            if compliance_result.action.value == "block":
                self.stats['blocked_requests'] += 1
                return LLMResponse(
                    content="I cannot process this request due to content policy violations.",
                    provider=request.provider,
                    model=request.model,
                    compliance_passed=False,
                    compliance_details=compliance_details
                )
        
        # Process with LLM if compliance passes
        if request.provider in self.handlers:
            try:
                content = await self.handlers[request.provider](request)
                self.stats['allowed_requests'] += 1
                
                return LLMResponse(
                    content=content,
                    provider=request.provider,
                    model=request.model,
                    compliance_passed=True,
                    compliance_details=compliance_details
                )
            except Exception as e:
                return LLMResponse(
                    content=f"Error processing request: {str(e)}",
                    provider=request.provider,
                    model=request.model,
                    compliance_passed=False,
                    compliance_details=compliance_details
                )
        else:
            return LLMResponse(
                content=f"No handler registered for provider: {request.provider.value}",
                provider=request.provider,
                model=request.model,
                compliance_passed=False,
                compliance_details=compliance_details
            )


# Mock LLM Handlers
async def mock_openai_handler(request: LLMRequest) -> str:
    """Mock OpenAI handler."""
    await asyncio.sleep(0.1)  # Simulate API delay
    
    if 'weather' in request.prompt.lower():
        return "Today's weather is sunny with temperatures around 72°F. Perfect for outdoor activities!"
    elif 'recipe' in request.prompt.lower() or 'cook' in request.prompt.lower():
        return "Here's a simple recipe: Combine ingredients, mix well, and cook according to instructions. Enjoy your meal!"
    elif 'explain' in request.prompt.lower() or 'what is' in request.prompt.lower():
        return f"Great question! Let me explain {request.prompt.split()[-1]} in simple terms..."
    else:
        return f"I understand you're asking about '{request.prompt[:30]}...'. Here's my response based on that topic."


async def mock_anthropic_handler(request: LLMRequest) -> str:
    """Mock Anthropic Claude handler."""
    await asyncio.sleep(0.15)  # Simulate API delay
    
    return f"Thank you for your thoughtful question. Regarding '{request.prompt[:40]}...', I'd be happy to provide a comprehensive response that addresses your specific needs."


async def mock_local_handler(request: LLMRequest) -> str:
    """Mock local model handler."""
    await asyncio.sleep(0.05)  # Faster than API calls
    
    return f"[Local Model {request.model}] Processing: {request.prompt[:50]}... Response generated locally."


async def demo_basic_integration():
    """Demo basic integration."""
    print("🔗 Basic LLM Integration with Compliance")
    print("=" * 60)
    
    # Initialize
    compliance_filter = ComplianceFilter()
    integration = SimpleLLMIntegration(compliance_filter)
    
    # Register handlers
    integration.register_handler(LLMProvider.OPENAI, mock_openai_handler)
    integration.register_handler(LLMProvider.ANTHROPIC, mock_anthropic_handler)
    integration.register_handler(LLMProvider.LOCAL, mock_local_handler)
    
    # Test cases
    test_requests = [
        LLMRequest("What's the weather like?", LLMProvider.OPENAI, "gpt-4", "user1"),
        LLMRequest("My email is test@example.com, help me", LLMProvider.OPENAI, "gpt-4", "user2"),
        LLMRequest("How do you cook pasta?", LLMProvider.ANTHROPIC, "claude-3", "user3"),
        LLMRequest("My SSN is 123-45-6789", LLMProvider.LOCAL, "llama-7b", "user4"),
    ]
    
    print("Processing test requests...\n")
    
    for i, request in enumerate(test_requests, 1):
        print(f"Request {i}: {request.prompt}")
        print(f"Provider: {request.provider.value} | Model: {request.model}")
        
        response = await integration.process_request(request)
        
        if response.compliance_passed:
            print(f"✅ ALLOWED | {response.content[:60]}...")
        else:
            print(f"🚫 BLOCKED | {response.content}")
        
        if response.compliance_details:
            details = response.compliance_details
            print(f"   Compliance: {details['action'].upper()} | Score: {details['overall_score']:.3f} | Violations: {details['violations']}")
        
        print()


async def demo_compliance_scenarios():
    """Demo different compliance scenarios."""
    print("🛡️ Compliance Scenarios")
    print("=" * 60)
    
    compliance_filter = ComplianceFilter()
    integration = SimpleLLMIntegration(compliance_filter)
    integration.register_handler(LLMProvider.CUSTOM, mock_local_handler)
    
    scenarios = [
        ("Safe Query", "What are the benefits of renewable energy?"),
        ("Email Violation", "Send updates to john@example.com"),
        ("Phone Violation", "Call me at (555) 123-4567"),
        ("Multiple PII", "Email user@test.com or call (555) 999-1234"),
        ("Credit Card", "Process payment with 4532-1234-5678-9012"),
        ("Borderline", "I work at a tech company in San Francisco"),
    ]
    
    for scenario_name, prompt in scenarios:
        print(f"Scenario: {scenario_name}")
        print(f"Prompt: {prompt}")
        
        request = LLMRequest(prompt, LLMProvider.CUSTOM, "test-model", "demo_user")
        response = await integration.process_request(request)
        
        if response.compliance_passed:
            status = "✅ PROCESSED"
        else:
            status = "🚫 BLOCKED"
        
        print(f"Result: {status}")
        
        if response.compliance_details:
            details = response.compliance_details
            print(f"Action: {details['action'].upper()} | Score: {details['overall_score']:.3f}")
            if details['violations'] > 0:
                print(f"Privacy violations: {details['violations']}")
        
        print("-" * 40)


def demo_real_integration_code():
    """Show examples of real integration code."""
    print("💻 Real Integration Code Examples")
    print("=" * 60)
    
    print("1. OpenAI Integration:")
    openai_code = '''
import openai
from your_project import ComplianceFilter

async def process_openai_request(prompt, user_id):
    # Initialize compliance filter
    filter = ComplianceFilter()
    
    # Check compliance first
    compliance_result = filter.check_compliance(prompt)
    
    if compliance_result.action.value == "block":
        return {
            "blocked": True,
            "reason": compliance_result.reasoning,
            "score": compliance_result.overall_score
        }
    
    # If compliance passes, call OpenAI
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        
        return {
            "blocked": False,
            "content": response.choices[0].message.content,
            "compliance_score": compliance_result.overall_score
        }
    except Exception as e:
        return {"error": str(e)}

# Usage
result = await process_openai_request("What's the weather?", "user123")
'''
    print(openai_code)
    
    print("\n2. Anthropic Claude Integration:")
    anthropic_code = '''
import anthropic
from your_project import ComplianceFilter

class SafeClaudeClient:
    def __init__(self, api_key):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.compliance_filter = ComplianceFilter()
    
    async def safe_completion(self, prompt, user_id="anonymous"):
        # Pre-check compliance
        compliance_result = self.compliance_filter.check_compliance(prompt)
        
        if compliance_result.action.value == "block":
            return {
                "success": False,
                "message": "Content blocked due to policy violations",
                "violations": len(compliance_result.privacy_violations)
            }
        
        # Call Claude
        response = await self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "success": True,
            "content": response.content[0].text,
            "compliance_score": compliance_result.overall_score
        }

# Usage
claude_client = SafeClaudeClient("your-api-key")
result = await claude_client.safe_completion("Explain quantum physics")
'''
    print(anthropic_code)
    
    print("\n3. Configuration-Based Integration:")
    config_code = '''
# config.yaml
compliance:
  thresholds:
    block_threshold: 0.8  # High security
    warn_threshold: 0.6
  weights:
    privacy: 0.7
    hate_speech: 0.3

# Python code
import yaml
from your_project import ComplianceFilter

class ConfigurableLLMGateway:
    def __init__(self, config_path="config.yaml"):
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        self.compliance_filter = ComplianceFilter(config_dict=config)
        self.blocked_count = 0
        self.total_count = 0
    
    async def process_request(self, prompt, llm_function, **kwargs):
        self.total_count += 1
        
        # Compliance check
        result = self.compliance_filter.check_compliance(prompt)
        
        if result.action.value == "block":
            self.blocked_count += 1
            return {
                "blocked": True,
                "reason": result.reasoning,
                "block_rate": self.blocked_count / self.total_count
            }
        
        # Process with LLM
        try:
            response = await llm_function(prompt, **kwargs)
            return {"content": response, "compliance_score": result.overall_score}
        except Exception as e:
            return {"error": str(e)}
'''
    print(config_code)


async def main():
    """Run all demos."""
    print("🚀 Simplified LLM Integration Demo")
    print("=" * 80)
    print("This shows core concepts for integrating compliance filtering with LLM APIs")
    print("=" * 80)
    
    try:
        await demo_basic_integration()
        await demo_compliance_scenarios()
        demo_real_integration_code()
        
        print("\n" + "=" * 80)
        print("🎉 INTEGRATION DEMOS COMPLETED!")
        print("=" * 80)
        
        print("\n📋 Key Integration Concepts:")
        print("✅ Pre-filter prompts before sending to LLM APIs")
        print("🔄 Handle blocked content gracefully")
        print("📊 Track compliance statistics")
        print("⚙️ Configure thresholds for your use case")
        print("🌐 Support multiple LLM providers")
        
        print("\n🛠️ Implementation Steps:")
        print("1. Install LLM API libraries: pip install openai anthropic")
        print("2. Set up API keys as environment variables")
        print("3. Create compliance wrapper functions")
        print("4. Configure appropriate thresholds for your use case")
        print("5. Add logging and monitoring")
        print("6. Test with representative content")
        
        print("\n🔐 Security Best Practices:")
        print("- Always check compliance before API calls")
        print("- Log blocked attempts for analysis")
        print("- Use environment variables for API keys")
        print("- Implement rate limiting")
        print("- Monitor compliance statistics")
        print("- Adjust thresholds based on real usage")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
