#!/usr/bin/env python3
"""
LLM API Integration Demo

This script demonstrates how to integrate the compliance filter with actual LLM APIs.
Includes examples for OpenAI, Anthropic, local models, and custom handlers.
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Optional
import json

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.compliance_filter import ComplianceFilter
from src.llm_integration import LLMIntegration, LLMRequest, LLMResponse, LLMProvider


# Mock API implementations for demonstration
class MockOpenAI:
    """Mock OpenAI API for demonstration purposes."""
    
    @staticmethod
    async def acreate(**kwargs):
        """Mock OpenAI chat completion."""
        messages = kwargs.get('messages', [])
        prompt = messages[-1].get('content', '') if messages else ''
        
        # Simulate different responses based on input
        if 'weather' in prompt.lower():
            response_text = "Today's weather is sunny with a temperature of 75°F (24°C). It's a perfect day to go outside!"
        elif 'machine learning' in prompt.lower():
            response_text = "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed for each task."
        elif 'recipe' in prompt.lower():
            response_text = "Here's a simple chocolate chip cookie recipe: Mix flour, sugar, butter, eggs, and chocolate chips. Bake at 375°F for 10-12 minutes."
        else:
            response_text = f"I understand you're asking about: '{prompt[:50]}...'. Here's a helpful response tailored to your query."
        
        # Mock response object
        class MockResponse:
            def __init__(self, content):
                self.choices = [MockChoice(content)]
        
        class MockChoice:
            def __init__(self, content):
                self.message = MockMessage(content)
        
        class MockMessage:
            def __init__(self, content):
                self.content = content
        
        # Simulate API delay
        await asyncio.sleep(0.1)
        return MockResponse(response_text)


class MockAnthropic:
    """Mock Anthropic Claude API for demonstration purposes."""
    
    def __init__(self):
        pass
    
    async def messages_create(self, **kwargs):
        """Mock Anthropic messages create."""
        messages = kwargs.get('messages', [])
        prompt = messages[-1].get('content', '') if messages else ''
        
        # Simulate Claude-style responses
        if 'explain' in prompt.lower():
            response_text = f"I'd be happy to explain this topic. {prompt} is an interesting subject that involves several key concepts..."
        elif 'help' in prompt.lower():
            response_text = f"I'm here to help! Regarding your question about '{prompt[:30]}...', let me provide some guidance..."
        else:
            response_text = f"Thank you for your question. Here's my response to '{prompt[:40]}...': This is a thoughtful inquiry that I'll address comprehensively."
        
        # Mock response object
        class MockResponse:
            def __init__(self, content):
                self.content = [MockContent(content)]
        
        class MockContent:
            def __init__(self, text):
                self.text = text
        
        # Simulate API delay
        await asyncio.sleep(0.15)
        return MockResponse(response_text)


async def demo_basic_integration():
    """Demonstrate basic LLM integration with compliance filtering."""
    print("🔗 Basic LLM Integration Demo")
    print("=" * 60)
    
    # Initialize components
    compliance_filter = ComplianceFilter()
    llm_integration = LLMIntegration(compliance_filter)
    
    # Register mock OpenAI handler
    async def mock_openai_handler(request: LLMRequest) -> str:
        """Mock OpenAI handler using our mock API."""
        mock_api = MockOpenAI()
        response = await mock_api.acreate(
            model=request.model,
            messages=[{"role": "user", "content": request.prompt}],
            **request.parameters
        )
        return response.choices[0].message.content
    
    llm_integration.register_custom_handler(LLMProvider.OPENAI, mock_openai_handler)
    
    # Test cases
    test_requests = [
        LLMRequest(
            prompt="What's the weather like today?",
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            parameters={"max_tokens": 150},
            user_id="user123"
        ),
        LLMRequest(
            prompt="My email is user@example.com, can you help me?",
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            parameters={"max_tokens": 150},
            user_id="user123"
        ),
        LLMRequest(
            prompt="Explain machine learning concepts",
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            parameters={"max_tokens": 200},
            user_id="user123"
        )
    ]
    
    print("Testing basic integration with compliance filtering...\n")
    
    for i, request in enumerate(test_requests, 1):
        print(f"Request {i}:")
        print(f"  Prompt: {request.prompt}")
        
        # Process request with compliance filtering
        response = await llm_integration.process_request(request, check_input=True)
        
        print(f"  Compliance: {'✅ PASSED' if response.compliance_passed else '🚫 BLOCKED'}")
        
        if response.compliance_result:
            print(f"  Action: {response.compliance_result.action.value}")
            print(f"  Score: {response.compliance_result.overall_score:.3f}")
            if response.compliance_result.privacy_violations:
                violations = [v.violation_type.value for v in response.compliance_result.privacy_violations]
                print(f"  Violations: {', '.join(violations)}")
        
        if response.compliance_passed:
            print(f"  Response: {response.content[:100]}{'...' if len(response.content) > 100 else ''}")
        else:
            print(f"  Blocked: {response.content}")
        
        print()


async def demo_multi_provider():
    """Demonstrate integration with multiple LLM providers."""
    print("🌐 Multi-Provider Integration Demo")
    print("=" * 60)
    
    # Initialize components
    compliance_filter = ComplianceFilter()
    llm_integration = LLMIntegration(compliance_filter)
    
    # Register multiple providers
    async def mock_openai_handler(request: LLMRequest) -> str:
        mock_api = MockOpenAI()
        response = await mock_api.acreate(
            model=request.model,
            messages=[{"role": "user", "content": request.prompt}]
        )
        return response.choices[0].message.content
    
    async def mock_anthropic_handler(request: LLMRequest) -> str:
        mock_api = MockAnthropic()
        response = await mock_api.messages_create(
            model=request.model,
            messages=[{"role": "user", "content": request.prompt}],
            max_tokens=request.parameters.get('max_tokens', 1000)
        )
        return response.content[0].text
    
    async def mock_local_handler(request: LLMRequest) -> str:
        """Mock local model handler."""
        return f"[Local Model Response] I've processed your request: '{request.prompt[:50]}...' using {request.model}"
    
    # Register handlers
    llm_integration.register_custom_handler(LLMProvider.OPENAI, mock_openai_handler)
    llm_integration.register_custom_handler(LLMProvider.ANTHROPIC, mock_anthropic_handler)
    llm_integration.register_custom_handler(LLMProvider.CUSTOM, mock_local_handler)
    
    # Test with different providers
    test_prompt = "How do I bake a chocolate cake?"
    
    providers_to_test = [
        (LLMProvider.OPENAI, "gpt-4"),
        (LLMProvider.ANTHROPIC, "claude-3-sonnet"),
        (LLMProvider.CUSTOM, "local-llama-7b")
    ]
    
    print(f"Testing prompt: '{test_prompt}' across multiple providers...\n")
    
    for provider, model in providers_to_test:
        print(f"Provider: {provider.value.upper()}")
        print(f"Model: {model}")
        
        request = LLMRequest(
            prompt=test_prompt,
            provider=provider,
            model=model,
            parameters={"max_tokens": 150},
            user_id="multi_user"
        )
        
        try:
            response = await llm_integration.process_request(request)
            print(f"  ✅ Success: {response.content[:80]}{'...' if len(response.content) > 80 else ''}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        print()


async def demo_compliance_scenarios():
    """Demonstrate different compliance scenarios."""
    print("🛡️ Compliance Scenarios Demo")
    print("=" * 60)
    
    compliance_filter = ComplianceFilter()
    llm_integration = LLMIntegration(compliance_filter)
    
    # Mock handler
    async def simple_handler(request: LLMRequest) -> str:
        return f"I'll help you with: {request.prompt}"
    
    llm_integration.register_custom_handler(LLMProvider.CUSTOM, simple_handler)
    
    # Different compliance scenarios
    scenarios = [
        ("Safe Content", "What are some good book recommendations?"),
        ("Privacy Violation - Email", "My email is john@example.com, please send me updates"),
        ("Privacy Violation - Phone", "Call me at (555) 123-4567 to discuss"),
        ("Privacy Violation - Multiple", "Contact me at user@test.com or (555) 999-1234"),
        ("High Risk - Credit Card", "Process payment with card 4532-1234-5678-9012"),
        ("Borderline Content", "I live in New York and work at a tech company"),
    ]
    
    print("Testing various compliance scenarios...\n")
    
    for scenario_name, prompt in scenarios:
        print(f"Scenario: {scenario_name}")
        print(f"  Prompt: {prompt}")
        
        request = LLMRequest(
            prompt=prompt,
            provider=LLMProvider.CUSTOM,
            model="test-model",
            parameters={},
            user_id="test_user"
        )
        
        response = await llm_integration.process_request(request, check_input=True)
        
        if response.compliance_result:
            action = response.compliance_result.action.value
            score = response.compliance_result.overall_score
            violations = len(response.compliance_result.privacy_violations)
            
            if action == "block":
                status = "🚫 BLOCKED"
            elif action == "warn":
                status = "⚠️  WARNING"
            else:
                status = "✅ ALLOWED"
            
            print(f"  {status} | Score: {score:.3f} | Violations: {violations}")
            
            if response.compliance_passed:
                print(f"  Response: {response.content}")
            else:
                print(f"  Blocked Message: {response.content}")
        
        print()


async def demo_batch_processing():
    """Demonstrate batch processing with compliance."""
    print("📦 Batch Processing Demo")
    print("=" * 60)
    
    compliance_filter = ComplianceFilter()
    llm_integration = LLMIntegration(compliance_filter)
    
    # Mock handler
    async def batch_handler(request: LLMRequest) -> str:
        return f"Response to: {request.prompt[:30]}..."
    
    llm_integration.register_custom_handler(LLMProvider.CUSTOM, batch_handler)
    
    # Batch of requests
    batch_prompts = [
        "What's the weather forecast?",
        "Email me at test@example.com",
        "How does photosynthesis work?",
        "My phone is (555) 123-4567",
        "Explain quantum computing",
        "Send report to user@company.com",
        "What's 2+2?",
        "My SSN is 123-45-6789"
    ]
    
    # Create batch requests
    batch_requests = [
        LLMRequest(
            prompt=prompt,
            provider=LLMProvider.CUSTOM,
            model="batch-model",
            parameters={},
            user_id=f"batch_user_{i}"
        ) for i, prompt in enumerate(batch_prompts)
    ]
    
    print(f"Processing {len(batch_requests)} requests in batch...\n")
    
    # Process batch
    responses = llm_integration.batch_process_requests(batch_requests, check_input=True)
    
    print("Batch Results:")
    print("-" * 80)
    
    allowed_count = 0
    blocked_count = 0
    warned_count = 0
    
    for i, (request, response) in enumerate(zip(batch_requests, responses), 1):
        if isinstance(response, Exception):
            print(f"{i:2d}. ❌ ERROR | {request.prompt[:40]}...")
            print(f"     Error: {response}")
        else:
            action = response.compliance_result.action.value if response.compliance_result else "unknown"
            
            if action == "block":
                status = "🚫 BLOCK"
                blocked_count += 1
            elif action == "warn":
                status = "⚠️  WARN"
                warned_count += 1
            else:
                status = "✅ ALLOW"
                allowed_count += 1
            
            score = response.compliance_result.overall_score if response.compliance_result else 0
            violations = len(response.compliance_result.privacy_violations) if response.compliance_result else 0
            
            print(f"{i:2d}. {status} | Score: {score:.3f} | Violations: {violations} | {request.prompt[:35]}...")
    
    print(f"\nBatch Summary:")
    print(f"  ✅ Allowed: {allowed_count}")
    print(f"  ⚠️  Warned: {warned_count}")
    print(f"  🚫 Blocked: {blocked_count}")
    print(f"  Total: {len(batch_requests)}")


def demo_configuration_examples():
    """Show configuration examples for different use cases."""
    print("\n⚙️ Configuration Examples")
    print("=" * 60)
    
    print("1. High Security Configuration (Financial Services):")
    high_security_config = {
        'compliance': {
            'thresholds': {
                'block_threshold': 0.3,  # Very strict
                'warn_threshold': 0.2,
                'pass_threshold': 0.1
            },
            'weights': {
                'privacy': 0.8,  # Heavily weight privacy
                'hate_speech': 0.2
            }
        },
        'privacy': {
            'risk_levels': {
                'high_risk_threshold': 0.6,  # Lower threshold
                'medium_risk_threshold': 0.3,
                'low_risk_threshold': 0.1
            }
        }
    }
    print(json.dumps(high_security_config, indent=2))
    
    print("\n2. Balanced Configuration (General Business):")
    balanced_config = {
        'compliance': {
            'thresholds': {
                'block_threshold': 0.7,  # Default
                'warn_threshold': 0.5,
                'pass_threshold': 0.2
            },
            'weights': {
                'privacy': 0.6,
                'hate_speech': 0.4
            }
        }
    }
    print(json.dumps(balanced_config, indent=2))
    
    print("\n3. Permissive Configuration (Internal Tools):")
    permissive_config = {
        'compliance': {
            'thresholds': {
                'block_threshold': 0.9,  # Very permissive
                'warn_threshold': 0.7,
                'pass_threshold': 0.3
            },
            'weights': {
                'privacy': 0.4,
                'hate_speech': 0.6  # Focus more on hate speech
            }
        }
    }
    print(json.dumps(permissive_config, indent=2))


async def main():
    """Run all integration demos."""
    print("🚀 LLM API Integration Demonstrations")
    print("=" * 80)
    print("This demonstrates how to integrate the compliance filter with LLM APIs.")
    print("=" * 80)
    
    try:
        await demo_basic_integration()
        await demo_multi_provider()
        await demo_compliance_scenarios()
        await demo_batch_processing()
        demo_configuration_examples()
        
        print("\n" + "=" * 80)
        print("🎉 ALL INTEGRATION DEMOS COMPLETED!")
        print("=" * 80)
        
        print("\n📋 Integration Summary:")
        print("✅ Basic LLM integration with compliance filtering")
        print("🌐 Multi-provider support (OpenAI, Anthropic, Custom)")
        print("🛡️ Various compliance scenarios handled appropriately")
        print("📦 Batch processing with compliance checks")
        print("⚙️ Configurable for different security requirements")
        
        print("\n🔧 Real Implementation Steps:")
        print("1. Install LLM provider libraries (openai, anthropic, etc.)")
        print("2. Set up API keys securely (environment variables)")
        print("3. Replace mock handlers with real API calls")
        print("4. Configure thresholds for your use case")
        print("5. Set up logging and monitoring for production")
        print("6. Test thoroughly with your specific content")
        
        print("\n💡 Production Tips:")
        print("- Use async processing for better performance")
        print("- Implement proper error handling and retries")
        print("- Monitor compliance decisions and adjust thresholds")
        print("- Set up alerts for blocked content patterns")
        print("- Consider caching for repeated similar requests")
        
    except Exception as e:
        print(f"❌ Error during integration demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
