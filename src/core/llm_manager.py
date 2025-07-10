"""
LLM Manager for the Legal Document Analyzer.
Handles multiple LLM providers with fallback support and performance monitoring.
"""

import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor

from langchain.prompts import PromptTemplate
from langchain.schema import BaseMessage

from src.config import config
from src.utils import logger, performance_logger


class LLMProvider(Enum):
    """Supported LLM providers."""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class LLMResponse:
    """Response from LLM with metadata."""
    content: str
    provider: str
    model: str
    processing_time: float
    token_count: Optional[int] = None
    cost: Optional[float] = None
    error: Optional[str] = None


class LLMManager:
    """Manages multiple LLM providers with fallback support."""
    
    def __init__(self):
        self.providers = {}
        self.current_provider = config.LLM_PROVIDER
        self.executor = ThreadPoolExecutor(max_workers=config.MAX_WORKERS)
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available LLM providers."""
        try:
            # Initialize Ollama
            if self._is_ollama_available():
                from langchain_ollama import OllamaLLM
                self.providers[LLMProvider.OLLAMA.value] = {
                    "client": OllamaLLM(model=config.OLLAMA_MODEL),
                    "model": config.OLLAMA_MODEL,
                    "available": True
                }
                logger.info(f"Ollama initialized with model: {config.OLLAMA_MODEL}")
            
            # Initialize OpenAI
            if config.OPENAI_API_KEY:
                from langchain_openai import ChatOpenAI
                self.providers[LLMProvider.OPENAI.value] = {
                    "client": ChatOpenAI(
                        model=config.OPENAI_MODEL,
                        openai_api_key=config.OPENAI_API_KEY,
                        temperature=0
                    ),
                    "model": config.OPENAI_MODEL,
                    "available": True
                }
                logger.info(f"OpenAI initialized with model: {config.OPENAI_MODEL}")
            
            # Initialize Anthropic
            if config.ANTHROPIC_API_KEY:
                from langchain_anthropic import ChatAnthropic
                self.providers[LLMProvider.ANTHROPIC.value] = {
                    "client": ChatAnthropic(
                        model=config.ANTHROPIC_MODEL,
                        anthropic_api_key=config.ANTHROPIC_API_KEY,
                        temperature=0
                    ),
                    "model": config.ANTHROPIC_MODEL,
                    "available": True
                }
                logger.info(f"Anthropic initialized with model: {config.ANTHROPIC_MODEL}")
            
            if not self.providers:
                raise ValueError("No LLM providers available")
            
            # Validate current provider
            if self.current_provider not in self.providers:
                self.current_provider = list(self.providers.keys())[0]
                logger.warning(f"Configured provider not available, using: {self.current_provider}")
                
        except Exception as e:
            logger.error("Failed to initialize LLM providers", exception=e)
            raise
    
    def _is_ollama_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def invoke(self, prompt: str, provider: Optional[str] = None) -> LLMResponse:
        """
        Invoke LLM with fallback support.
        
        Args:
            prompt: The prompt to send to the LLM
            provider: Specific provider to use (optional)
            
        Returns:
            LLMResponse with the result
        """
        start_time = time.time()
        provider = provider or self.current_provider
        
        # Try primary provider
        try:
            response = self._invoke_provider(prompt, provider)
            if response.error is None:
                return response
        except Exception as e:
            logger.warning(f"Primary provider {provider} failed: {e}")
        
        # Try fallback providers
        for fallback_provider in self.providers:
            if fallback_provider != provider:
                try:
                    logger.info(f"Trying fallback provider: {fallback_provider}")
                    response = self._invoke_provider(prompt, fallback_provider)
                    if response.error is None:
                        return response
                except Exception as e:
                    logger.warning(f"Fallback provider {fallback_provider} failed: {e}")
        
        # All providers failed
        processing_time = time.time() - start_time
        return LLMResponse(
            content="",
            provider=provider,
            model="",
            processing_time=processing_time,
            error="All LLM providers failed"
        )
    
    def _invoke_provider(self, prompt: str, provider: str) -> LLMResponse:
        """Invoke specific LLM provider."""
        start_time = time.time()
        
        if provider not in self.providers:
            raise ValueError(f"Provider {provider} not available")
        
        provider_config = self.providers[provider]
        client = provider_config["client"]
        model = provider_config["model"]
        
        try:
            # Handle different client types
            if provider == LLMProvider.ANTHROPIC.value:
                # Anthropic returns AIMessage
                result = client.invoke(prompt)
                content = result.content if hasattr(result, 'content') else str(result)
            else:
                # Ollama and OpenAI return string directly
                result = client.invoke(prompt)
                content = result.strip() if isinstance(result, str) else str(result).strip()
            
            processing_time = time.time() - start_time
            
            # Log performance
            performance_logger.log_timing(
                f"llm_invoke_{provider}",
                processing_time,
                model=model,
                prompt_length=len(prompt),
                response_length=len(content)
            )
            
            return LLMResponse(
                content=content,
                provider=provider,
                model=model,
                processing_time=processing_time,
                token_count=self._estimate_tokens(prompt + content)
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Provider {provider} failed: {str(e)}"
            logger.error(error_msg)
            
            return LLMResponse(
                content="",
                provider=provider,
                model=model,
                processing_time=processing_time,
                error=error_msg
            )
    
    def batch_invoke(self, prompts: List[str], provider: Optional[str] = None) -> List[LLMResponse]:
        """
        Process multiple prompts in parallel.
        
        Args:
            prompts: List of prompts to process
            provider: Specific provider to use (optional)
            
        Returns:
            List of LLMResponse objects
        """
        provider = provider or self.current_provider
        
        # Process in parallel using ThreadPoolExecutor
        futures = []
        for prompt in prompts:
            future = self.executor.submit(self.invoke, prompt, provider)
            futures.append(future)
        
        # Collect results
        results = []
        for future in futures:
            try:
                result = future.result(timeout=300)  # 5 minute timeout
                results.append(result)
            except Exception as e:
                logger.error(f"Batch processing failed: {e}")
                results.append(LLMResponse(
                    content="",
                    provider=provider,
                    model="",
                    processing_time=0,
                    error=str(e)
                ))
        
        return results
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 characters ≈ 1 token)."""
        return len(text) // 4
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers."""
        status = {}
        for provider_name, provider_config in self.providers.items():
            status[provider_name] = {
                "available": provider_config["available"],
                "model": provider_config["model"],
                "current": provider_name == self.current_provider
            }
        return status
    
    def switch_provider(self, provider: str) -> bool:
        """Switch to a different provider."""
        if provider in self.providers and self.providers[provider]["available"]:
            self.current_provider = provider
            logger.info(f"Switched to provider: {provider}")
            return True
        else:
            logger.error(f"Cannot switch to provider: {provider}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of all providers."""
        health_status = {}
        
        for provider_name in self.providers:
            try:
                start_time = time.time()
                response = self._invoke_provider("Test prompt", provider_name)
                response_time = time.time() - start_time
                
                health_status[provider_name] = {
                    "healthy": response.error is None,
                    "response_time": response_time,
                    "error": response.error
                }
            except Exception as e:
                health_status[provider_name] = {
                    "healthy": False,
                    "response_time": 0,
                    "error": str(e)
                }
        
        return health_status


# Global LLM manager instance
llm_manager = LLMManager()

# Convenience functions
def invoke_llm(prompt: str, provider: Optional[str] = None) -> LLMResponse:
    """Invoke LLM with the given prompt."""
    return llm_manager.invoke(prompt, provider)

def batch_invoke_llm(prompts: List[str], provider: Optional[str] = None) -> List[LLMResponse]:
    """Process multiple prompts in parallel."""
    return llm_manager.batch_invoke(prompts, provider)

def get_llm_status() -> Dict[str, Any]:
    """Get status of all LLM providers."""
    return llm_manager.get_provider_status()

def switch_llm_provider(provider: str) -> bool:
    """Switch to a different LLM provider."""
    return llm_manager.switch_provider(provider)
