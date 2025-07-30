"""
py-config-ai: AI-powered configuration file generator for developers.

A comprehensive tool that uses natural language processing and AI to generate
configuration files for various development tools and frameworks. Features
context-aware generation, multiple AI provider support, and intelligent
project analysis.

Author: Sherin Joseph Roy (sherin.joseph2217@gmail.com)
GitHub: https://github.com/Sherin-SEF-AI/py-config-ai
Website: https://sherin-sef-ai.github.io/
"""

__version__ = "1.0.0"
__author__ = "Sherin Joseph Roy"
__email__ = "sherin.joseph2217@gmail.com"
__url__ = "https://github.com/Sherin-SEF-AI/py-config-ai"
__description__ = "AI-powered configuration file generator for developers"

from .core.generator import ConfigGenerator
from .core.key_manager import KeyManager

__all__ = ["ConfigGenerator", "KeyManager"] 