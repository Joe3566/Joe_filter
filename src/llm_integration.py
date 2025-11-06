"""
LLM API Integration Module

Provides integration layer to connect the compliance filter with actual LLM API calls,
with before/after filtering hooks and comprehensive monitoring.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

from .compliance_filter import ComplianceFilter, ComplianceResult, ComplianceAction
from .feedback_system import FeedbackSystem


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"
    HUGGING_FACE = "hugging_face"
    CUSTOM = "custom"


@dataclass
class LLMRequest:
    """Represents an LLM API request."""
    prompt: str
    provider: LLMProvider
    model: str
    parameters: Dict[str, Any]
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


@dataclass
class LLMResponse:
    """Represents an LLM API response."""
    content: str
    provider: LLMProvider
    model: str
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    compliance_passed: bool = True
    compliance_result: Optional[ComplianceResult] = None


class LLMIntegration:
    """
    Integration layer for LLM APIs with compliance filtering.
    
    Features:
    - Pre-processing compliance checks
    - Post-processing content filtering
    - Multiple LLM provider support
    - Rate limiting and monitoring
    - Comprehensive logging and audit trails
    - Async support for better performance
    """
    
    def __init__(
        self, 
        compliance_filter: ComplianceFilter,
        config: Optional[Dict[str, Any]] = None,
        feedback_system: Optional[FeedbackSystem] = None
    ):
        """
        Initialize LLM integration.
        
        Args:
            compliance_filter: The compliance filter instance
            config: Configuration dictionary
            feedback_system: Optional feedback system
        """
        self.compliance_filter = compliance_filter
        self.feedback_system = feedback_system
        self.config = config or {}
        
        # Integration configuration
        integration_config = self.config.get('llm_integration', {})
        self.timeout_seconds = integration_config.get('timeout_seconds', 30)
        self.max_retries = integration_config.get('max_retries', 3)
        self.retry_delay = integration_config.get('retry_delay', 1.0)
        self.requests_per_minute = integration_config.get('requests_per_minute', 60)
        
        # Rate limiting
        self._request_times: List[float] = []      
        self._last_cleanup = time.time()       
        
        self._stats = {
            'total_requests': 0,
            'blocked_requests': 0,
            'warned_requests': 0,
            'allowed_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'total_response_time': 0.0,
            'by_provider': {}
        }
        
        # Custom LLM handlers
        self._custom_handlers: Dict[LLMProvider, Callable] = {}
        
        logging.info("LLMIntegration initialized")
    
    def register_custom_handler(self, provider: LLMProvider, handler: Callable):
        """
        Register a custom handler for an LLM provider.
        
        Args:
            provider: The LLM provider
            handler: Async callable that takes (request, **kwargs) and returns response content
        """
        self._custom_handlers[provider] = handler
        logging.info(f"Registered custom handler for {provider.value}")
    
    async def process_request(
        self, 
        request: LLMRequest,
        check_input: bool = True,
        check_output: bool = False
    ) -> LLMResponse:
        """
        Process an LLM request with compliance filtering.
        
        Args:
            request: The LLM request to process
            check_input: Whether to check input compliance
            check_output: Whether to check output compliance
            
        Returns:
            LLM response with compliance information
        """
        start_time = time.time()
        
        try:
            # Rate limiting check
            if not self._check_rate_limit():
                raise RuntimeError("Rate limit exceeded")
            
            # Pre-processing compliance check
            compliance_result = None
            if check_input:
                compliance_result = self.compliance_filter.check_compliance(
                    request.prompt,
                    user_context={
                        'user_id': request.user_id,
                        'session_id': request.session_id,
                        'provider': request.provider.value,
                        'model': request.model,
                        **(request.context or {})
                    }
                )
                
                # Handle compliance action
                if compliance_result.action == ComplianceAction.BLOCK:
                    self._update_stats('blocked', request.provider, time.time() - start_time)
                    return self._create_blocked_response(request, compliance_result)
                
                elif compliance_result.action == ComplianceAction.WARN:
                    logging.warning(f"Compliance warning for request: {compliance_result.reasoning}")
                    self._update_stats('warned', request.provider, time.time() - start_time)
            
            # Make LLM API call
            llm_response = await self._call_llm_api(request)
            
            # Post-processing compliance check
            output_compliance_result = None
            if check_output and llm_response:
                output_compliance_result = self.compliance_filter.check_compliance(
                    llm_response,
                    user_context={
                        'type': 'output_check',
                        'user_id': request.user_id,
                        'session_id': request.session_id,
                        'provider': request.provider.value,
                        'model': request.model
                    }
                )
                
                if output_compliance_result.action == ComplianceAction.BLOCK:
                    logging.warning("LLM output blocked due to compliance violation")
                    llm_response = "I apologize, but I cannot provide that response due to content policy violations."
            
            processing_time = time.time() - start_time
            self._update_stats('allowed', request.provider, processing_time)
            
            # Create response
            response = LLMResponse(
                content=llm_response,
                provider=request.provider,
                model=request.model,
                compliance_passed=True,
                compliance_result=compliance_result or output_compliance_result
            )
            
            # Request feedback if needed
            if self.feedback_system and compliance_result:
                if self.feedback_system.should_request_feedback(compliance_result):
                    logging.info("Compliance result may benefit from feedback")
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_stats('failed', request.provider, processing_time)
            logging.error(f"Error processing LLM request: {e}")
            
            return LLMResponse(
                content="I apologize, but I encountered an error processing your request.",
                provider=request.provider,
                model=request.model,
                compliance_passed=False,
                metadata={'error': str(e)}
            )
    
    def _create_blocked_response(self, request: LLMRequest, compliance_result: ComplianceResult) -> LLMResponse:
        """Create a response for blocked requests."""
        blocked_message = (
            "I cannot process this request due to content policy violations. "
            f"Reason: {compliance_result.reasoning}"
        )
        
        return LLMResponse(
            content=blocked_message,
            provider=request.provider,
            model=request.model,
            compliance_passed=False,
            compliance_result=compliance_result
        )
    
    async def _call_llm_api(self, request: LLMRequest) -> str:
        """
        Make the actual LLM API call.
        
        Args:
            request: The LLM request
            
        Returns:
            Response content from the LLM
        """
        # Check for custom handler
        if request.provider in self._custom_handlers:
            handler = self._custom_handlers[request.provider]
            return await handler(request)
        
        # Built-in provider support
        if request.provider == LLMProvider.OPENAI:
            return await self._call_openai(request)
        elif request.provider == LLMProvider.ANTHROPIC:
            return await self._call_anthropic(request)
        elif request.provider == LLMProvider.AZURE_OPENAI:
            return await self._call_azure_openai(request)
        elif request.provider == LLMProvider.HUGGING_FACE:
            return await self._call_hugging_face(request)
        else:
            raise ValueError(f"Unsupported LLM provider: {request.provider}")
    
    async def _call_openai(self, request: LLMRequest) -> str:
        """Call OpenAI API."""
        try:
            import openai
            
            response = await openai.ChatCompletion.acreate(
                model=request.model,
                messages=[
                    {"role": "user", "content": request.prompt}
                ],
                **request.parameters
            )
            
            return response.choices[0].message.content
            
        except ImportError:
            raise ImportError("openai library not installed")
        except Exception as e:
            logging.error(f"OpenAI API call failed: {e}")
            raise
    
    async def _call_anthropic(self, request: LLMRequest) -> str:
        """Call Anthropic Claude API."""
        try:
            import anthropic
            
            client = anthropic.AsyncAnthropic()
            
            response = await client.messages.create(
                model=request.model,
                max_tokens=request.parameters.get('max_tokens', 1000),
                messages=[
                    {"role": "user", "content": request.prompt}
                ]
            )
            
            return response.content[0].text
            
        except ImportError:
            raise ImportError("anthropic library not installed")
        except Exception as e:
            logging.error(f"Anthropic API call failed: {e}")
            raise
    
    async def _call_azure_openai(self, request: LLMRequest) -> str:
        """Call Azure OpenAI API."""
        try:
            import openai
            
            # Configure Azure OpenAI
            openai.api_type = "azure"
            openai.api_base = request.parameters.get('api_base')
            openai.api_version = request.parameters.get('api_version', '2023-05-15')
            openai.api_key = request.parameters.get('api_key')
            
            response = await openai.ChatCompletion.acreate(
                engine=request.model,  # deployment name in Azure
                messages=[
                    {"role": "user", "content": request.prompt}
                ],
                **{k: v for k, v in request.parameters.items() 
                   if k not in ['api_base', 'api_version', 'api_key']}
            )
            
            return response.choices[0].message.content
            
        except ImportError:
            raise ImportError("openai library not installed")
        except Exception as e:
            logging.error(f"Azure OpenAI API call failed: {e}")
            raise
    
    async def _call_hugging_face(self, request: LLMRequest) -> str:
        """Call Hugging Face API."""
        try:
            import aiohttp
            
            api_key = request.parameters.get('api_key')
            if not api_key:
                raise ValueError("Hugging Face API key required")
            
            url = f"https://api-inference.huggingface.co/models/{request.model}"
            headers = {"Authorization": f"Bearer {api_key}"}
            payload = {
                "inputs": request.prompt,
                "parameters": {k: v for k, v in request.parameters.items() if k != 'api_key'}
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        if isinstance(result, list) and len(result) > 0:
                            return result[0].get('generated_text', '')
                        return str(result)
                    else:
                        error_text = await response.text()
                        raise Exception(f"HuggingFace API error: {error_text}")
                        
        except ImportError:
            raise ImportError("aiohttp library required for Hugging Face integration")
        except Exception as e:
            logging.error(f"Hugging Face API call failed: {e}")
            raise
    
    def _check_rate_limit(self) -> bool:
        """Check if request is within rate limits."""
        current_time = time.time()
        
        # Clean old requests (older than 1 minute)
        if current_time - self._last_cleanup > 60:
            cutoff_time = current_time - 60
            self._request_times = [t for t in self._request_times if t > cutoff_time]
            self._last_cleanup = current_time
        
        # Check rate limit
        if len(self._request_times) >= self.requests_per_minute:
            return False
        
        # Add current request time
        self._request_times.append(current_time)
        return True
    
    def _update_stats(self, status: str, provider: LLMProvider, processing_time: float):
        """Update internal statistics."""
        self._stats['total_requests'] += 1
        self._stats[f'{status}_requests'] += 1
        self._stats['total_response_time'] += processing_time
        self._stats['average_response_time'] = (
            self._stats['total_response_time'] / self._stats['total_requests']
        )
        
        # Provider-specific stats
        provider_name = provider.value
        if provider_name not in self._stats['by_provider']:
            self._stats['by_provider'][provider_name] = {
                'total': 0, 'blocked': 0, 'warned': 0, 'allowed': 0, 'failed': 0
            }
        
        self._stats['by_provider'][provider_name]['total'] += 1
        self._stats['by_provider'][provider_name][status] += 1
    
    def batch_process_requests(
        self, 
        requests: List[LLMRequest],
        check_input: bool = True,
        check_output: bool = False
    ) -> List[LLMResponse]:
        """Process multiple requests concurrently."""
        async def process_batch():
            tasks = [
                self.process_request(req, check_input, check_output) 
                for req in requests
            ]
            return await asyncio.gather(*tasks, return_exceptions=True)
        
        return asyncio.run(process_batch())
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get integration statistics."""
        return self._stats.copy()
    
    def export_audit_log(self, output_file: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
        """Export audit logs for compliance reporting."""
        # This would typically read from persistent logs
        # For now, we'll export current statistics
        audit_data = {
            'export_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'statistics': self.get_statistics(),
            'compliance_stats': self.compliance_filter.get_performance_stats(),
            'configuration': self.compliance_filter.get_configuration_summary()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(audit_data, f, indent=2)
        
        logging.info(f"Audit log exported to {output_file}")
    
    def update_configuration(self, new_config: Dict[str, Any]):
        """Update integration configuration."""
        self.config.update(new_config)
        
        # Update specific settings
        integration_config = self.config.get('llm_integration', {})
        self.timeout_seconds = integration_config.get('timeout_seconds', self.timeout_seconds)
        self.max_retries = integration_config.get('max_retries', self.max_retries)
        self.retry_delay = integration_config.get('retry_delay', self.retry_delay)
        self.requests_per_minute = integration_config.get('requests_per_minute', self.requests_per_minute)
        
        logging.info("LLM integration configuration updated")
    
    def cleanup(self):
        """Clean up resources."""
        if self.compliance_filter:
            self.compliance_filter.cleanup()
        
        logging.info("LLMIntegration resources cleaned up")
