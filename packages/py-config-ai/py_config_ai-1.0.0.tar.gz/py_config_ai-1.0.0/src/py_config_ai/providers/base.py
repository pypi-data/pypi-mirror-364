"""
Base AI provider interface for py-config-ai.

This module defines the abstract base class that all AI providers must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from ..configs.config_types import get_config_info


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    def __init__(self, api_key: str, **kwargs):
        """
        Initialize the AI provider.

        Args:
            api_key: The API key for the provider
            **kwargs: Additional provider-specific configuration
        """
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    async def generate_config(
        self, 
        config_type: str, 
        description: str, 
        context: Optional[str] = None,
        preset: Optional[str] = None
    ) -> str:
        """
        Generate a configuration file using AI.

        Args:
            config_type: Type of configuration (e.g., 'black', 'prettierrc')
            description: User description of desired configuration
            context: Optional context about the codebase
            preset: Optional preset configuration

        Returns:
            str: Generated configuration content

        Raises:
            Exception: If generation fails
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test the connection to the AI provider.

        Returns:
            bool: True if connection is successful, False otherwise
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of the provider.

        Returns:
            str: Provider name
        """
        pass

    def _build_prompt(self, config_type: str, description: str, context: Optional[str] = None) -> str:
        """Build a comprehensive prompt for configuration generation."""
        config_info = get_config_info(config_type)
        
        prompt = f"""You are an expert configuration file generator. Your task is to create a {config_type} configuration file based on the user's requirements.

Configuration Type: {config_type}
Description: {config_info['description']}
File Extension: {config_info['file_extension']}

User Requirements: {description}

Please generate a {config_type} configuration that:
1. Follows best practices for {config_type}
2. Meets the user's specific requirements
3. Is production-ready and well-documented
4. Uses the correct file format ({config_info['file_extension']})

{self._get_format_instructions(config_type)}

{self._get_examples_section(config_type)}

{self._get_context_section(context)}

Important:
- Generate ONLY the configuration content, no markdown formatting or explanations
- Use the correct syntax for {config_type}
- Include helpful comments where appropriate
- Make sure the configuration is valid and follows the tool's specifications
- If the user's requirements are unclear, provide sensible defaults with comments explaining the choices

Generate the {config_type} configuration:"""

        return prompt

    def _get_format_instructions(self, config_type: str) -> str:
        """Get format-specific instructions."""
        format_instructions = {
            'pyproject.toml': "Use TOML format with proper section headers like [tool.black], [tool.isort], etc.",
            'black': "Use TOML format with [black] section. Common options: line-length, target-version, include, exclude.",
            'isort': "Use TOML format with [tool.isort] section. Common options: profile, line_length, multi_line_output.",
            'ruff': "Use TOML format with [tool.ruff] section. Include linter and formatter configurations.",
            'flake8': "Use INI format with [flake8] section. Common options: max-line-length, ignore, exclude.",
            'pylint': "Use INI format with [MASTER] and [MESSAGES CONTROL] sections.",
            'mypy': "Use TOML format with [tool.mypy] section. Include strict settings and ignore patterns.",
            '.prettierrc': "Use JSON format. Common options: printWidth, tabWidth, semi, singleQuote, trailingComma.",
            '.eslintrc': "Use JSON format. Include extends, plugins, rules, and env settings.",
            'tsconfig.json': "Use JSON format. Include compilerOptions, include, exclude, and other TypeScript settings.",
            'markdownlint.json': "Use JSON format. Include default and custom rules for markdown linting.",
            'stylelint': "Use JSON format. Include extends, rules, and ignoreFiles for CSS/SCSS linting.",
            'dockerfile': "Use Dockerfile format with FROM, RUN, COPY, CMD instructions. Include best practices.",
            '.env': "Use environment variable format (KEY=value). Include common development variables.",
            'docker-compose.yml': "Use YAML format. Include services, networks, and volumes configurations.",
            'nginx.conf': "Use Nginx configuration format with server, location, and upstream blocks.",
            'gitignore': "Use gitignore format with patterns for files and directories to ignore."
        }
        
        return format_instructions.get(config_type, f"Use the standard format for {config_type}.")

    def _get_examples_section(self, config_type: str) -> str:
        """Get examples section for the configuration type."""
        config_info = get_config_info(config_type)
        examples = config_info.get('examples', [])
        
        if examples:
            return f"Common configuration options: {', '.join(examples)}"
        return ""

    def _get_context_section(self, context: Optional[str]) -> str:
        """Get context section if provided."""
        if context:
            return f"Project Context: {context}\nUse this context to tailor the configuration to the specific project structure and requirements."
        return "" 