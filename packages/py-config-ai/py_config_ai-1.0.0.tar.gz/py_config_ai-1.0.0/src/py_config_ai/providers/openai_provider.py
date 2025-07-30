"""
OpenAI provider implementation for py-config-ai.
"""

import asyncio
from typing import Optional
import openai
from .base import AIProvider


class OpenAIProvider(AIProvider):
    """OpenAI provider implementation."""

    def __init__(self, api_key: str, model: str = "gpt-4", **kwargs):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-4)
            **kwargs: Additional configuration
        """
        super().__init__(api_key, **kwargs)
        self.model = model
        self.client = openai.AsyncOpenAI(api_key=api_key)

    async def generate_config(
        self, 
        config_type: str, 
        description: str, 
        context: Optional[str] = None,
        preset: Optional[str] = None
    ) -> str:
        """
        Generate configuration using OpenAI.

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
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates configuration files. Provide only the configuration content without any explanations or markdown formatting."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def test_connection(self) -> bool:
        """
        Test connection to OpenAI.

        Returns:
            bool: True if connection successful
        """
        try:
            # Use sync client for testing
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
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
        return "openai" 