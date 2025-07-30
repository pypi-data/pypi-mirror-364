"""
Anthropic (Claude) provider implementation for py-config-ai.
"""

import asyncio
from typing import Optional
import anthropic
from .base import AIProvider


class AnthropicProvider(AIProvider):
    """Anthropic (Claude) provider implementation."""

    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229", **kwargs):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key
            model: Model to use (default: claude-3-sonnet-20240229)
            **kwargs: Additional configuration
        """
        super().__init__(api_key, **kwargs)
        self.model = model
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    async def generate_config(
        self, 
        config_type: str, 
        description: str, 
        context: Optional[str] = None,
        preset: Optional[str] = None
    ) -> str:
        """
        Generate configuration using Anthropic Claude.

        Args:
            config_type: Type of configuration
            description: User description
            context: Optional context
            preset: Optional preset

        Returns:
            str: Generated configuration content

        Raises:
            Exception: If generation fails
        """
        prompt = self._build_prompt(config_type, description, context)
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.1,
                system="You are a helpful assistant that generates configuration files. Provide only the configuration content without any explanations or markdown formatting.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response.content[0].text.strip()
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")

    def test_connection(self) -> bool:
        """
        Test connection to Anthropic.

        Returns:
            bool: True if connection successful
        """
        try:
            # Use sync client for testing
            client = anthropic.Anthropic(api_key=self.api_key)
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=5,
                messages=[{"role": "user", "content": "Hello"}]
            )
            return True
        except Exception:
            return False

    def get_provider_name(self) -> str:
        """
        Get provider name.

        Returns:
            str: Provider name
        """
        return "anthropic" 