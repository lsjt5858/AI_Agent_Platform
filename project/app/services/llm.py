"""
LLM Service module for AI Agent Platform.
Handles communication with LLM APIs (通义千问/OpenAI compatible).

Requirements: 3.2, 3.3, 3.4, 3.5, 3.6
"""

import logging
from typing import Any, Optional

import httpx

from ..config import get_settings

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Base exception for LLM service errors."""
    pass


class LLMTimeoutError(LLMError):
    """Exception raised when LLM API request times out."""
    pass


class LLMAPIError(LLMError):
    """Exception raised when LLM API returns an error."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}


def format_messages_for_llm(
    messages: list[dict[str, str]],
    system_prompt: str
) -> list[dict[str, str]]:
    """
    Format messages for LLM API request.
    
    Converts internal message format to LLM provider's specification.
    Prepends system prompt as the first message.
    
    Args:
        messages: List of message dicts with 'role' and 'content' keys
        system_prompt: The system prompt defining agent behavior
        
    Returns:
        List of formatted messages ready for LLM API
        
    Requirements: 3.5
    """
    formatted = []
    
    # Add system prompt as first message
    if system_prompt:
        formatted.append({
            "role": "system",
            "content": system_prompt
        })
    
    # Add conversation messages
    for msg in messages:
        formatted.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", "")
        })
    
    return formatted


def parse_llm_response(response_data: dict[str, Any]) -> tuple[str, dict[str, int]]:
    """
    Parse LLM API response and extract assistant message content and token usage.

    Args:
        response_data: Raw response from LLM API

    Returns:
        Tuple of (assistant_message_content, token_usage_dict)

    Raises:
        LLMAPIError: If response format is invalid

    Requirements: 3.6
    """
    try:
        choices = response_data.get("choices", [])
        if not choices:
            raise LLMAPIError(
                "Invalid LLM response: no choices returned",
                details={"response": response_data}
            )

        message = choices[0].get("message", {})
        content = message.get("content")

        if content is None:
            raise LLMAPIError(
                "Invalid LLM response: no content in message",
                details={"response": response_data}
            )

        # Extract token usage information
        usage = response_data.get("usage", {})
        token_usage = {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0)
        }

        return content, token_usage

    except (KeyError, IndexError, TypeError) as e:
        raise LLMAPIError(
            f"Failed to parse LLM response: {str(e)}",
            details={"response": response_data}
        )



class LLMService:
    """
    Service for interacting with LLM APIs.
    
    Supports OpenAI-compatible APIs including 通义千问 (DashScope).
    Uses httpx for async HTTP requests with configurable timeout.
    
    Requirements: 3.2, 3.3, 3.4
    """
    
    def __init__(
        self,
        api_base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: int = 2
    ):
        """
        Initialize LLM service.
        
        Args:
            api_base_url: Base URL for LLM API (defaults to config)
            api_key: API key for authentication (defaults to config)
            model: Model name to use (defaults to config)
            timeout: Request timeout in seconds (defaults to config, 30s)
            max_retries: Maximum number of retry attempts for transient errors
        """
        settings = get_settings()
        
        self.api_base_url = api_base_url or settings.llm_api_base_url
        self.api_key = api_key or settings.llm_api_key
        self.model = model or settings.llm_model
        self.timeout = timeout or settings.llm_timeout
        self.max_retries = max_retries
        
        # Ensure base URL doesn't end with slash
        self.api_base_url = self.api_base_url.rstrip("/")
    
    def _get_headers(self) -> dict[str, str]:
        """Get HTTP headers for API request."""
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def _build_request_body(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> dict[str, Any]:
        """
        Build request body for LLM API.
        
        Args:
            messages: Formatted messages list
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            
        Returns:
            Request body dict
        """
        body: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        
        if max_tokens is not None:
            body["max_tokens"] = max_tokens
            
        return body
    
    async def _make_request(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> dict[str, Any]:
        """
        Make async HTTP request to LLM API.
        
        Args:
            messages: Formatted messages list
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            Parsed JSON response
            
        Raises:
            LLMTimeoutError: If request times out
            LLMAPIError: If API returns an error
        """
        url = f"{self.api_base_url}/chat/completions"
        headers = self._get_headers()
        body = self._build_request_body(messages, temperature, max_tokens)
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, headers=headers, json=body)
                
                if response.status_code != 200:
                    error_detail = response.text
                    try:
                        error_json = response.json()
                        error_detail = error_json.get("error", {}).get("message", error_detail)
                    except Exception:
                        pass
                    
                    raise LLMAPIError(
                        f"LLM API error: {error_detail}",
                        status_code=response.status_code,
                        details={"response": response.text}
                    )
                
                return response.json()
                
            except httpx.TimeoutException as e:
                logger.error(f"LLM API timeout after {self.timeout}s: {e}")
                raise LLMTimeoutError(
                    f"LLM API request timed out after {self.timeout} seconds"
                )
            except httpx.RequestError as e:
                logger.error(f"LLM API request error: {e}")
                raise LLMAPIError(f"LLM API request failed: {str(e)}")
    
    async def chat(
        self,
        messages: list[dict[str, str]],
        system_prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> tuple[str, dict[str, int]]:
        """
        Send chat request to LLM and get response with token usage.

        Handles the complete flow:
        1. Format messages with system prompt
        2. Make async API request with retry logic
        3. Parse and return response content with token usage

        Args:
            messages: List of conversation messages with 'role' and 'content'
            system_prompt: System prompt defining agent behavior
            temperature: Sampling temperature (0-2, default 0.7)
            max_tokens: Maximum tokens in response (optional)

        Returns:
            Tuple of (assistant's response content, token_usage_dict)

        Raises:
            LLMTimeoutError: If request times out after 30 seconds
            LLMAPIError: If API returns an error

        Requirements: 3.1, 3.2, 3.3, 3.4
        """
        # Format messages for LLM API (Requirements: 3.5)
        formatted_messages = format_messages_for_llm(messages, system_prompt)

        last_error: Optional[Exception] = None

        # Retry logic for transient errors
        for attempt in range(self.max_retries + 1):
            try:
                # Make async request (Requirements: 3.2)
                response_data = await self._make_request(
                    formatted_messages,
                    temperature,
                    max_tokens
                )

                # Parse response (Requirements: 3.6)
                return parse_llm_response(response_data)
                
            except LLMTimeoutError:
                # Don't retry on timeout (Requirements: 3.4)
                raise
            except LLMAPIError as e:
                last_error = e
                # Only retry on 5xx errors (server errors)
                if e.status_code and 500 <= e.status_code < 600:
                    if attempt < self.max_retries:
                        logger.warning(
                            f"LLM API error (attempt {attempt + 1}/{self.max_retries + 1}): {e}"
                        )
                        continue
                # Don't retry on client errors (4xx)
                raise
            except Exception as e:
                last_error = e
                if attempt < self.max_retries:
                    logger.warning(
                        f"Unexpected error (attempt {attempt + 1}/{self.max_retries + 1}): {e}"
                    )
                    continue
                raise LLMAPIError(f"Unexpected error: {str(e)}")
        
        # Should not reach here, but just in case
        if last_error:
            raise last_error
        raise LLMAPIError("Unknown error occurred")


# Singleton instance for dependency injection
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """
    Get LLM service instance (singleton pattern).
    
    Returns:
        LLMService instance
    """
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
