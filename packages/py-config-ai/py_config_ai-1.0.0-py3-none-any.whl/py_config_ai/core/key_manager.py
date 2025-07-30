"""
Secure API key management for py-config-ai.

This module handles secure storage and retrieval of API keys for various AI providers
using the keyring library for system-level secure storage.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, List
import keyring
from keyring.errors import KeyringError


class KeyManager:
    """Manages API keys for different AI providers securely."""

    SERVICE_NAME = "py-config-ai"
    FALLBACK_FILE = Path.home() / ".pyconfigai" / "keys.json"

    def __init__(self):
        """Initialize the key manager."""
        self._ensure_fallback_dir()

    def _ensure_fallback_dir(self) -> None:
        """Ensure the fallback directory exists."""
        self.FALLBACK_FILE.parent.mkdir(parents=True, exist_ok=True)

    def add_key(self, provider: str, api_key: str) -> bool:
        """
        Add an API key for a specific provider.

        Args:
            provider: The AI provider name (e.g., 'openai', 'anthropic')
            api_key: The API key to store

        Returns:
            bool: True if key was stored successfully, False otherwise
        """
        try:
            # Try to store in keyring first
            keyring.set_password(self.SERVICE_NAME, provider, api_key)
            return True
        except KeyringError:
            # Fallback to file storage
            return self._store_key_fallback(provider, api_key)

    def get_key(self, provider: str) -> Optional[str]:
        """
        Retrieve an API key for a specific provider.

        Args:
            provider: The AI provider name

        Returns:
            Optional[str]: The API key if found, None otherwise
        """
        try:
            # Try to get from keyring first
            key = keyring.get_password(self.SERVICE_NAME, provider)
            if key:
                return key
        except KeyringError:
            pass

        # Fallback to file storage
        return self._get_key_fallback(provider)

    def remove_key(self, provider: str) -> bool:
        """
        Remove an API key for a specific provider.

        Args:
            provider: The AI provider name

        Returns:
            bool: True if key was removed successfully, False otherwise
        """
        removed = False
        
        try:
            # Try to remove from keyring first
            keyring.delete_password(self.SERVICE_NAME, provider)
            removed = True
        except KeyringError:
            pass

        # Also remove from fallback storage
        fallback_removed = self._remove_key_fallback(provider)
        
        return removed or fallback_removed

    def list_providers(self) -> List[str]:
        """
        List all providers with stored keys.

        Returns:
            List[str]: List of provider names with stored keys
        """
        providers = []
        
        # Check keyring
        try:
            # Note: keyring doesn't have a direct way to list keys
            # We'll check common providers
            common_providers = ['openai', 'anthropic', 'gemini', 'groq']
            for provider in common_providers:
                if keyring.get_password(self.SERVICE_NAME, provider):
                    providers.append(provider)
        except KeyringError:
            pass

        # Check fallback storage
        fallback_providers = self._list_fallback_providers()
        for provider in fallback_providers:
            if provider not in providers:
                providers.append(provider)

        return providers

    def has_key(self, provider: str) -> bool:
        """
        Check if a key exists for a specific provider.

        Args:
            provider: The AI provider name

        Returns:
            bool: True if key exists, False otherwise
        """
        return self.get_key(provider) is not None

    def _store_key_fallback(self, provider: str, api_key: str) -> bool:
        """Store key in fallback file storage."""
        try:
            keys = self._load_fallback_keys()
            keys[provider] = api_key
            self._save_fallback_keys(keys)
            return True
        except Exception:
            return False

    def _get_key_fallback(self, provider: str) -> Optional[str]:
        """Get key from fallback file storage."""
        try:
            keys = self._load_fallback_keys()
            return keys.get(provider)
        except Exception:
            return None

    def _remove_key_fallback(self, provider: str) -> bool:
        """Remove key from fallback file storage."""
        try:
            keys = self._load_fallback_keys()
            if provider in keys:
                del keys[provider]
                self._save_fallback_keys(keys)
                return True
            return False
        except Exception:
            return False

    def _list_fallback_providers(self) -> List[str]:
        """List providers from fallback storage."""
        try:
            keys = self._load_fallback_keys()
            return list(keys.keys())
        except Exception:
            return []

    def _load_fallback_keys(self) -> Dict[str, str]:
        """Load keys from fallback file."""
        if not self.FALLBACK_FILE.exists():
            return {}
        
        try:
            with open(self.FALLBACK_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def _save_fallback_keys(self, keys: Dict[str, str]) -> None:
        """Save keys to fallback file."""
        with open(self.FALLBACK_FILE, 'w') as f:
            json.dump(keys, f, indent=2) 