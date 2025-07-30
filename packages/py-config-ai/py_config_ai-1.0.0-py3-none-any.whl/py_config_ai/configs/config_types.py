"""
Configuration types and schemas for py-config-ai.

This module defines the supported configuration types and their metadata.
"""

from typing import Dict, List, Any, Optional


SUPPORTED_CONFIGS = {
    # Python configurations
    "pyproject.toml": {
        "name": "pyproject.toml",
        "description": "Python project configuration (PEP 518)",
        "file_extension": ".toml",
        "category": "python",
        "examples": ["build-system", "tool.black", "tool.isort", "tool.ruff"]
    },
    "black": {
        "name": "Black",
        "description": "Python code formatter configuration",
        "file_extension": ".toml",
        "category": "python",
        "examples": ["line-length", "target-version", "include", "exclude"]
    },
    "isort": {
        "name": "isort",
        "description": "Python import sorter configuration",
        "file_extension": ".toml",
        "category": "python",
        "examples": ["profile", "line_length", "known_first_party"]
    },
    "ruff": {
        "name": "Ruff",
        "description": "Fast Python linter and formatter",
        "file_extension": ".toml",
        "category": "python",
        "examples": ["target-version", "line-length", "select", "ignore"]
    },
    "flake8": {
        "name": "Flake8",
        "description": "Python style guide enforcement",
        "file_extension": ".ini",
        "category": "python",
        "examples": ["max-line-length", "ignore", "exclude"]
    },
    "pylint": {
        "name": "Pylint",
        "description": "Python static code analysis",
        "file_extension": ".rc",
        "category": "python",
        "examples": ["max-line-length", "disable", "good-names"]
    },
    "mypy": {
        "name": "MyPy",
        "description": "Python static type checker",
        "file_extension": ".toml",
        "category": "python",
        "examples": ["python_version", "warn_return_any", "disallow_untyped_defs"]
    },
    
    # JavaScript/TypeScript configurations
    ".prettierrc": {
        "name": "Prettier",
        "description": "JavaScript/TypeScript code formatter",
        "file_extension": ".json",
        "category": "javascript",
        "examples": ["semi", "singleQuote", "tabWidth", "trailingComma"]
    },
    ".eslintrc": {
        "name": "ESLint",
        "description": "JavaScript/TypeScript linter",
        "file_extension": ".json",
        "category": "javascript",
        "examples": ["extends", "rules", "env", "parserOptions"]
    },
    "tsconfig.json": {
        "name": "TypeScript",
        "description": "TypeScript compiler configuration",
        "file_extension": ".json",
        "category": "javascript",
        "examples": ["compilerOptions", "include", "exclude", "strict"]
    },
    
    # Other configurations
    "markdownlint.json": {
        "name": "MarkdownLint",
        "description": "Markdown linter configuration",
        "file_extension": ".json",
        "category": "markup",
        "examples": ["default", "MD013", "MD033", "MD041"]
    },
    "stylelint": {
        "name": "Stylelint",
        "description": "CSS/SCSS linter configuration",
        "file_extension": ".json",
        "category": "css",
        "examples": ["extends", "rules", "ignoreFiles"]
    },
    "dockerfile": {
        "name": "Dockerfile",
        "description": "Docker container configuration",
        "file_extension": "",
        "category": "docker",
        "examples": ["FROM", "WORKDIR", "COPY", "RUN", "EXPOSE"]
    },
    ".env": {
        "name": "Environment Variables",
        "description": "Environment variables template",
        "file_extension": "",
        "category": "env",
        "examples": ["DATABASE_URL", "API_KEY", "DEBUG", "PORT"]
    },
    "docker-compose.yml": {
        "name": "Docker Compose",
        "description": "Multi-container Docker application",
        "file_extension": ".yml",
        "category": "docker",
        "examples": ["version", "services", "volumes", "networks"]
    },
    "nginx.conf": {
        "name": "Nginx",
        "description": "Nginx web server configuration",
        "file_extension": ".conf",
        "category": "web",
        "examples": ["server", "location", "upstream", "events"]
    },
    "gitignore": {
        "name": "Git Ignore",
        "description": "Git ignore patterns",
        "file_extension": "",
        "category": "git",
        "examples": ["*.pyc", "__pycache__", ".env", "node_modules"]
    }
}


def get_config_info(config_type: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a specific configuration type.

    Args:
        config_type: The configuration type name

    Returns:
        Optional[Dict[str, Any]]: Configuration info or None if not found
    """
    return SUPPORTED_CONFIGS.get(config_type)


def list_configs_by_category(category: Optional[str] = None) -> List[str]:
    """
    List configuration types, optionally filtered by category.

    Args:
        category: Optional category filter

    Returns:
        List[str]: List of configuration type names
    """
    if category is None:
        return list(SUPPORTED_CONFIGS.keys())
    
    return [
        config_type for config_type, info in SUPPORTED_CONFIGS.items()
        if info["category"] == category
    ]


def get_categories() -> List[str]:
    """
    Get all available configuration categories.

    Returns:
        List[str]: List of category names
    """
    categories = set()
    for info in SUPPORTED_CONFIGS.values():
        categories.add(info["category"])
    return sorted(list(categories))


def validate_config_type(config_type: str) -> bool:
    """
    Validate if a configuration type is supported.

    Args:
        config_type: The configuration type to validate

    Returns:
        bool: True if supported, False otherwise
    """
    return config_type in SUPPORTED_CONFIGS 