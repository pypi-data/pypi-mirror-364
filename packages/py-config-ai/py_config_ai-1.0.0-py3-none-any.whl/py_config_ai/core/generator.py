"""
Main configuration generator for py-config-ai.

This module contains the core logic for generating configuration files using AI.
"""

import asyncio
import json
import yaml
import toml
from pathlib import Path
from typing import Dict, Any, Optional, List
from halo import Halo

from ..providers.base import AIProvider
from ..providers.openai_provider import OpenAIProvider
from ..providers.anthropic_provider import AnthropicProvider
from ..providers.gemini_provider import GeminiProvider
from ..providers.groq_provider import GroqProvider
from ..configs.config_types import SUPPORTED_CONFIGS, get_config_info
from ..configs.presets import PRESETS, get_preset_config
from .key_manager import KeyManager


class ConfigGenerator:
    """Main configuration generator class."""

    PROVIDER_MAP = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "gemini": GeminiProvider,
        "groq": GroqProvider,
    }

    def __init__(self):
        """Initialize the configuration generator."""
        self.key_manager = KeyManager()

    def get_available_providers(self) -> List[str]:
        """
        Get list of available AI providers.

        Returns:
            List[str]: List of provider names
        """
        return list(self.PROVIDER_MAP.keys())

    def get_provider(self, provider_name: str) -> Optional[AIProvider]:
        """
        Get an AI provider instance.

        Args:
            provider_name: Name of the provider

        Returns:
            Optional[AIProvider]: Provider instance or None if not found
        """
        if provider_name not in self.PROVIDER_MAP:
            return None

        api_key = self.key_manager.get_key(provider_name)
        if not api_key:
            return None

        provider_class = self.PROVIDER_MAP[provider_name]
        return provider_class(api_key)

    async def generate_config(
        self,
        config_type: str,
        description: str,
        provider: str = "openai",
        context: Optional[str] = None,
        preset: Optional[str] = None,
        output_file: Optional[str] = None,
        preview: bool = True
    ) -> str:
        """
        Generate a configuration file.

        Args:
            config_type: Type of configuration to generate
            description: User description of desired configuration
            provider: AI provider to use
            context: Optional context about the codebase
            preset: Optional preset configuration
            output_file: Optional output file path
            preview: Whether to show preview before saving

        Returns:
            str: Generated configuration content

        Raises:
            ValueError: If provider or config type is invalid
            Exception: If generation fails
        """
        # Validate config type
        if not get_config_info(config_type):
            raise ValueError(f"Unsupported config type: {config_type}")

        # Get provider
        ai_provider = self.get_provider(provider)
        if not ai_provider:
            raise ValueError(f"Provider '{provider}' not available or no API key configured")

        # Analyze project context if provided
        context_info = self._analyze_project_context(context)

        # Generate configuration
        with Halo(text=f"Generating {config_type} configuration...", spinner="dots"):
            try:
                content = await ai_provider.generate_config(
                    config_type=config_type,
                    description=description,
                    context=context_info,
                    preset=preset
                )
            except Exception as e:
                raise Exception(f"Failed to generate configuration: {str(e)}")

        # Format content based on config type
        formatted_content = self._format_content(config_type, content)

        # Show preview if requested
        if preview:
            self._show_preview(config_type, formatted_content)

        # Save to file if specified
        if output_file:
            if not preview or self._confirm_save():
                self._save_to_file(output_file, formatted_content)
                print(f"Configuration saved to: {output_file}")

        return formatted_content

    def generate_preset_config(
        self,
        preset_name: str,
        output_dir: str = ".",
        preview: bool = True
    ) -> Dict[str, str]:
        """
        Generate configurations for a preset.

        Args:
            preset_name: Name of the preset
            output_dir: Output directory
            preview: Whether to show preview before saving

        Returns:
            Dict[str, str]: Generated configurations

        Raises:
            ValueError: If preset is invalid
        """
        preset = get_preset_config(preset_name)
        if not preset:
            raise ValueError(f"Unsupported preset: {preset_name}")

        results = {}
        output_path = Path(output_dir)

        for config_type, config_data in preset["configs"].items():
            config_info = get_config_info(config_type)
            if not config_info:
                continue

            # Convert config data to appropriate format
            content = self._dict_to_config_format(config_type, config_data)
            
            # Determine filename
            if config_type == "dockerfile":
                filename = "Dockerfile"
            elif config_type == ".env":
                filename = ".env"
            elif config_type == "gitignore":
                filename = ".gitignore"
            else:
                filename = config_type

            file_path = output_path / filename

            # Show preview if requested
            if preview:
                self._show_preview(config_type, content)

            # Save file
            if not preview or self._confirm_save():
                self._save_to_file(str(file_path), content)
                results[config_type] = str(file_path)
                print(f"Generated: {file_path}")

        return results

    def _format_content(self, config_type: str, content: str) -> str:
        """
        Format content based on configuration type.

        Args:
            config_type: Type of configuration
            content: Raw content from AI

        Returns:
            str: Formatted content
        """
        config_info = get_config_info(config_type)
        if not config_info:
            return content

        # Clean up the content (remove markdown formatting if present)
        content = content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            if len(lines) > 2:
                content = "\n".join(lines[1:-1])

        return content

    def _dict_to_config_format(self, config_type: str, data: Dict[str, Any]) -> str:
        """
        Convert dictionary to configuration format.

        Args:
            config_type: Type of configuration
            data: Configuration data

        Returns:
            str: Formatted configuration
        """
        config_info = get_config_info(config_type)
        if not config_info:
            return str(data)

        file_extension = config_info.get("file_extension", "")

        if file_extension == ".json":
            return json.dumps(data, indent=2)
        elif file_extension == ".yaml" or file_extension == ".yml":
            return yaml.dump(data, default_flow_style=False, indent=2)
        elif file_extension == ".toml":
            return toml.dumps(data)
        elif file_extension == ".ini":
            return self._dict_to_ini(data)
        else:
            # For files without specific format (like .env, Dockerfile, etc.)
            return self._dict_to_text(data, config_type)

    def _dict_to_ini(self, data: Dict[str, Any]) -> str:
        """Convert dictionary to INI format."""
        lines = []
        for section, items in data.items():
            lines.append(f"[{section}]")
            if isinstance(items, dict):
                for key, value in items.items():
                    lines.append(f"{key} = {value}")
            else:
                lines.append(f"{section} = {items}")
            lines.append("")
        return "\n".join(lines)

    def _dict_to_text(self, data: Dict[str, Any], config_type: str) -> str:
        """Convert dictionary to text format for special config types."""
        if config_type == ".env":
            lines = []
            for key, value in data.items():
                lines.append(f"{key}={value}")
            return "\n".join(lines)
        elif config_type == "dockerfile":
            lines = []
            for key, value in data.items():
                if key == "base_image":
                    lines.append(f"FROM {value}")
                elif key == "working_dir":
                    lines.append(f"WORKDIR {value}")
                elif key == "expose_port":
                    lines.append(f"EXPOSE {value}")
                elif key == "command":
                    lines.append(f"CMD {value}")
            return "\n".join(lines)
        elif config_type == "gitignore":
            if isinstance(data, list):
                return "\n".join(data)
            else:
                return str(data)
        else:
            return str(data)

    def _show_preview(self, config_type: str, content: str) -> None:
        """Show preview of generated configuration."""
        print(f"\n[bold blue]Preview of {config_type}:[/bold blue]")
        print("=" * 50)
        print(content)
        print("=" * 50)

    def _confirm_save(self) -> bool:
        """Ask user to confirm saving the configuration."""
        try:
            response = input("\nSave this configuration? (y/N): ").strip().lower()
            return response in ["y", "yes"]
        except KeyboardInterrupt:
            return False

    def _save_to_file(self, file_path: str, content: str) -> None:
        """
        Save content to file.

        Args:
            file_path: Path to save the file
            content: Content to save
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w") as f:
            f.write(content)

    def test_provider(self, provider: str) -> bool:
        """
        Test connection to a provider.

        Args:
            provider: Provider name to test

        Returns:
            bool: True if connection successful
        """
        ai_provider = self.get_provider(provider)
        if not ai_provider:
            return False

        try:
            return ai_provider.test_connection()
        except Exception:
            return False 

    def _analyze_project_context(self, context_path: Optional[str]) -> Optional[str]:
        """Analyze project structure and provide context for AI generation."""
        if not context_path:
            return None
            
        try:
            context_dir = Path(context_path).resolve()
            if not context_dir.exists() or not context_dir.is_dir():
                return None
                
            analysis = []
            analysis.append(f"Project root: {context_dir.name}")
            
            # Analyze project structure
            files = list(context_dir.rglob("*"))
            
            # Count file types
            file_extensions = {}
            for file in files:
                if file.is_file():
                    ext = file.suffix.lower()
                    file_extensions[ext] = file_extensions.get(ext, 0) + 1
            
            # Detect project type
            if file_extensions.get('.py', 0) > 0:
                analysis.append("Project type: Python")
                analysis.append(f"Python files: {file_extensions.get('.py', 0)}")
                
                # Check for common Python project files
                if (context_dir / 'requirements.txt').exists():
                    analysis.append("Has requirements.txt")
                if (context_dir / 'setup.py').exists():
                    analysis.append("Has setup.py")
                if (context_dir / 'pyproject.toml').exists():
                    analysis.append("Has pyproject.toml")
                if (context_dir / 'src').exists():
                    analysis.append("Uses src/ layout")
                if (context_dir / 'tests').exists():
                    analysis.append("Has tests/ directory")
                    
            if file_extensions.get('.js', 0) > 0 or file_extensions.get('.ts', 0) > 0:
                analysis.append("Project type: JavaScript/TypeScript")
                analysis.append(f"JS files: {file_extensions.get('.js', 0)}")
                analysis.append(f"TS files: {file_extensions.get('.ts', 0)}")
                
                # Check for common JS project files
                if (context_dir / 'package.json').exists():
                    analysis.append("Has package.json")
                if (context_dir / 'node_modules').exists():
                    analysis.append("Has node_modules/")
                    
            # Check for framework-specific files
            if (context_dir / 'manage.py').exists():
                analysis.append("Framework: Django")
            elif (context_dir / 'app.py').exists() or (context_dir / 'main.py').exists():
                analysis.append("Framework: Flask/FastAPI")
            elif (context_dir / 'next.config.js').exists():
                analysis.append("Framework: Next.js")
            elif (context_dir / 'angular.json').exists():
                analysis.append("Framework: Angular")
            elif (context_dir / 'vue.config.js').exists():
                analysis.append("Framework: Vue.js")
                
            # Check for Docker files
            if (context_dir / 'Dockerfile').exists():
                analysis.append("Has Dockerfile")
            if (context_dir / 'docker-compose.yml').exists():
                analysis.append("Has docker-compose.yml")
                
            # Check for CI/CD
            if (context_dir / '.github').exists():
                analysis.append("Has GitHub Actions")
            if (context_dir / '.gitlab-ci.yml').exists():
                analysis.append("Has GitLab CI")
                
            # Top-level directories
            dirs = [d for d in context_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
            if dirs:
                analysis.append(f"Main directories: {', '.join(d.name for d in dirs[:5])}")
                
            return "\n".join(analysis)
            
        except Exception as e:
            return f"Error analyzing project: {str(e)}" 