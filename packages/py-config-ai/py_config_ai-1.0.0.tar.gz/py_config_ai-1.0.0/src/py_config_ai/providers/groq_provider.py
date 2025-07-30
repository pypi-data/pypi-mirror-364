"""
Groq provider implementation for py-config-ai.
"""

import asyncio
from typing import Optional
from groq import AsyncGroq
from .base import AIProvider


class GroqProvider(AIProvider):
    """Groq provider implementation."""

    def __init__(self, api_key: str, model: str = "llama3-8b-8192", **kwargs):
        """
        Initialize Groq provider.

        Args:
            api_key: Groq API key
            model: Model to use (default: llama3-8b-8192)
            **kwargs: Additional configuration
        """
        super().__init__(api_key, **kwargs)
        self.model = model
        self.client = AsyncGroq(api_key=api_key)

    async def generate_config(
        self, 
        config_type: str, 
        description: str, 
        context: Optional[str] = None,
        preset: Optional[str] = None
    ) -> str:
        """
        Generate configuration using Groq.

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
            raise Exception(f"Groq API error: {str(e)}")

    def test_connection(self) -> bool:
        """
        Test connection to Groq.

        Returns:
            bool: True if connection successful
        """
        try:
            # Use sync client for testing
            from groq import Groq
            client = Groq(api_key=self.api_key)
            response = client.chat.completions.create(
                model="llama3-8b-8192",
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
        return "groq" 