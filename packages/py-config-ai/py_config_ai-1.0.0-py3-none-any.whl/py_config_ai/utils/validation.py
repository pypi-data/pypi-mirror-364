"""
Validation utility functions for py-config-ai.
"""

import json
import yaml
import toml
from typing import Any, Dict, Optional, Tuple


def validate_json(content: str) -> Tuple[bool, Optional[str]]:
    """
    Validate JSON content.

    Args:
        content: JSON content to validate

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    try:
        json.loads(content)
        return True, None
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {str(e)}"


def validate_yaml(content: str) -> Tuple[bool, Optional[str]]:
    """
    Validate YAML content.

    Args:
        content: YAML content to validate

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    try:
        yaml.safe_load(content)
        return True, None
    except yaml.YAMLError as e:
        return False, f"Invalid YAML: {str(e)}"


def validate_toml(content: str) -> Tuple[bool, Optional[str]]:
    """
    Validate TOML content.

    Args:
        content: TOML content to validate

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    try:
        toml.loads(content)
        return True, None
    except toml.TomlDecodeError as e:
        return False, f"Invalid TOML: {str(e)}"


def validate_config_format(content: str, config_type: str) -> Tuple[bool, Optional[str]]:
    """
    Validate configuration content based on its type.

    Args:
        content: Configuration content to validate
        config_type: Type of configuration

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not content.strip():
        return False, "Configuration content is empty"

    # Determine format based on config type
    if config_type.endswith('.json') or config_type in ['.prettierrc', '.eslintrc', 'tsconfig.json', 'markdownlint.json']:
        return validate_json(content)
    elif config_type.endswith('.yaml') or config_type.endswith('.yml') or config_type == 'docker-compose.yml':
        return validate_yaml(content)
    elif config_type.endswith('.toml') or config_type in ['pyproject.toml', 'black', 'isort', 'ruff', 'mypy']:
        return validate_toml(content)
    elif config_type.endswith('.ini') or config_type == 'flake8':
        # Basic INI validation
        return validate_ini(content)
    else:
        # For other formats (like .env, Dockerfile, etc.), just check if not empty
        return True, None


def validate_ini(content: str) -> Tuple[bool, Optional[str]]:
    """
    Basic INI validation.

    Args:
        content: INI content to validate

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    lines = content.strip().split('\n')
    if not lines:
        return False, "INI content is empty"

    # Basic validation: check for valid key=value or [section] format
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        if line.startswith('[') and line.endswith(']'):
            # Section header
            continue
        
        if '=' not in line:
            return False, f"Invalid INI format at line {i}: missing '=' in key-value pair"
    
    return True, None


def validate_api_key(api_key: str, provider: str) -> Tuple[bool, Optional[str]]:
    """
    Basic API key validation.

    Args:
        api_key: API key to validate
        provider: Provider name

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not api_key or not api_key.strip():
        return False, "API key cannot be empty"

    api_key = api_key.strip()

    # Provider-specific validation
    if provider == "openai":
        if not api_key.startswith("sk-"):
            return False, "OpenAI API key should start with 'sk-'"
        if len(api_key) < 20:
            return False, "OpenAI API key seems too short"
    
    elif provider == "anthropic":
        if not api_key.startswith("sk-ant-"):
            return False, "Anthropic API key should start with 'sk-ant-'"
        if len(api_key) < 20:
            return False, "Anthropic API key seems too short"
    
    elif provider == "gemini":
        # Google API keys can have various formats
        if len(api_key) < 10:
            return False, "Google API key seems too short"
    
    elif provider == "groq":
        if not api_key.startswith("gsk_"):
            return False, "Groq API key should start with 'gsk_'"
        if len(api_key) < 20:
            return False, "Groq API key seems too short"

    return True, None


def validate_file_path(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate file path.

    Args:
        file_path: File path to validate

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not file_path or not file_path.strip():
        return False, "File path cannot be empty"

    # Check for invalid characters
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
    for char in invalid_chars:
        if char in file_path:
            return False, f"File path contains invalid character: {char}"

    return True, None 