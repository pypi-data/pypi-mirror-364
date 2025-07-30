"""
Google Gemini provider implementation for py-config-ai.
"""

import asyncio
from typing import Optional
import google.generativeai as genai
from .base import AIProvider


class GeminiProvider(AIProvider):
    """Google Gemini provider implementation."""

    def __init__(self, api_key: str, model: str = "gemini-1.5-pro", **kwargs):
        """
        Initialize Gemini provider.

        Args:
            api_key: Google API key
            model: Model to use (default: gemini-1.5-pro)
            **kwargs: Additional configuration
        """
        super().__init__(api_key, **kwargs)
        self.model = model
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(model)

    async def generate_config(
        self, 
        config_type: str, 
        description: str, 
        context: Optional[str] = None,
        preset: Optional[str] = None
    ) -> str:
        """
        Generate configuration using Google Gemini.

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
            # Run in executor since Gemini doesn't have async API
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                self.client.generate_content,
                prompt
            )
            
            return response.text.strip()
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

    def test_connection(self) -> bool:
        """
        Test connection to Gemini.

        Returns:
            bool: True if connection successful
        """
        try:
            response = self.client.generate_content("Hello")
            return True
        except Exception:
            return False

    def get_provider_name(self) -> str:
        """
        Get provider name.

        Returns:
            str: Provider name
        """
        return "gemini" 