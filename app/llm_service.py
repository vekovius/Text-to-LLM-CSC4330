"""
LLM Service Layer - Handles communication with various LLM providers.
Supports: OpenAI, Anthropic (Claude), and xAI (Grok).
"""
import httpx
from typing import Dict, Any, Optional
from app.config import config
from app.utils.logger import logger


class LLMService:
    """
    Service class for interacting with LLM providers.
    Easily swap between OpenAI, Anthropic, and xAI by changing LLM_PROVIDER env variable.
    """

    def __init__(self):
        self.provider = config.LLM_PROVIDER.lower()
        self.api_key = config.LLM_API_KEY
        self.model = config.LLM_MODEL
        self.max_tokens = config.MAX_TOKENS

    async def generate(self, text: str, max_tokens: Optional[int] = None) -> str:
        """
        Generate a response from the configured LLM provider.

        Args:
            text: User input text/prompt
            max_tokens: Optional override for max tokens in response

        Returns:
            Generated text response from the LLM

        Raises:
            ValueError: If provider is not supported
            httpx.HTTPError: If API request fails
        """
        tokens = max_tokens or self.max_tokens

        logger.info(f"Generating response using {self.provider} (model: {self.model})")

        # Route to appropriate provider
        if self.provider == "openai":
            return await self._generate_openai(text, tokens)
        elif self.provider == "anthropic":
            return await self._generate_anthropic(text, tokens)
        elif self.provider == "xai":
            return await self._generate_xai(text, tokens)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    async def _generate_openai(self, text: str, max_tokens: int) -> str:
        """
        Generate response using OpenAI API.

        API Docs: https://platform.openai.com/docs/api-reference/chat/create
        """
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": text}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

                # Extract response text
                message_content = data["choices"][0]["message"]["content"]
                logger.info(f"OpenAI response received (tokens: {data.get('usage', {}).get('total_tokens', 'N/A')})")
                return message_content

            except httpx.HTTPStatusError as e:
                logger.error(f"OpenAI API error: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"OpenAI request failed: {str(e)}")
                raise

    async def _generate_anthropic(self, text: str, max_tokens: int) -> str:
        """
        Generate response using Anthropic (Claude) API.

        API Docs: https://docs.anthropic.com/en/api/messages
        """
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model or "claude-3-5-sonnet-20241022",
            "max_tokens": max_tokens,
            "messages": [
                {"role": "user", "content": text}
            ],
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

                # Extract response text
                message_content = data["content"][0]["text"]
                logger.info(f"Anthropic response received (tokens: {data.get('usage', {}).get('output_tokens', 'N/A')})")
                return message_content

            except httpx.HTTPStatusError as e:
                logger.error(f"Anthropic API error: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Anthropic request failed: {str(e)}")
                raise

    async def _generate_xai(self, text: str, max_tokens: int) -> str:
        """
        Generate response using xAI (Grok) API.

        xAI uses OpenAI-compatible API format.
        API Docs: https://docs.x.ai/api
        """
        url = "https://api.x.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model or "grok-beta",
            "messages": [
                {"role": "user", "content": text}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

                # Extract response text (OpenAI-compatible format)
                message_content = data["choices"][0]["message"]["content"]
                logger.info(f"xAI response received (tokens: {data.get('usage', {}).get('total_tokens', 'N/A')})")
                return message_content

            except httpx.HTTPStatusError as e:
                logger.error(f"xAI API error: {e.response.status_code} - {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"xAI request failed: {str(e)}")
                raise


# Create singleton instance
llm_service = LLMService()
