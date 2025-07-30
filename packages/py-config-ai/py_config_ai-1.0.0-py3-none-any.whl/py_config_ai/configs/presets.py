"""
Preset configurations for py-config-ai.

This module provides predefined configurations for common project types.
"""

from typing import Dict, Any, Optional, List


PRESETS = {
    "fastapi": {
        "name": "FastAPI",
        "description": "FastAPI web application with modern Python tooling",
        "configs": {
            "pyproject.toml": {
                "build-system": {
                    "requires": ["setuptools>=61.0", "wheel"],
                    "build-backend": "setuptools.build_meta"
                },
                "tool": {
                    "black": {
                        "line-length": 88,
                        "target-version": ["py38"],
                        "include": "\\.pyi?$"
                    },
                    "isort": {
                        "profile": "black",
                        "multi_line_output": 3,
                        "line_length": 88
                    },
                    "ruff": {
                        "target-version": "py38",
                        "line-length": 88,
                        "select": ["E", "F", "I", "N", "W", "B", "A", "C4", "UP", "ARG", "SIM", "TCH", "Q"],
                        "ignore": ["E501", "B008", "C901"]
                    },
                    "mypy": {
                        "python_version": "3.8",
                        "warn_return_any": True,
                        "disallow_untyped_defs": True,
                        "check_untyped_defs": True
                    }
                }
            },
            ".env": {
                "DATABASE_URL": "postgresql://user:password@localhost/dbname",
                "SECRET_KEY": "your-secret-key-here",
                "DEBUG": "True",
                "PORT": "8000"
            },
            "dockerfile": {
                "base_image": "python:3.11-slim",
                "working_dir": "/app",
                "expose_port": 8000,
                "command": "uvicorn main:app --host 0.0.0.0 --port 8000"
            }
        }
    },
    "django": {
        "name": "Django",
        "description": "Django web application with comprehensive tooling",
        "configs": {
            "pyproject.toml": {
                "tool": {
                    "black": {
                        "line-length": 88,
                        "target-version": ["py38"]
                    },
                    "isort": {
                        "profile": "black",
                        "known_django": "django",
                        "sections": ["FUTURE", "STDLIB", "DJANGO", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]
                    },
                    "ruff": {
                        "target-version": "py38",
                        "line-length": 88,
                        "select": ["E", "F", "I", "N", "W", "B", "A", "C4", "UP", "ARG", "SIM", "TCH", "Q"],
                        "ignore": ["E501", "B008", "C901", "DJ001", "DJ003"]
                    }
                }
            },
            ".env": {
                "DEBUG": "True",
                "SECRET_KEY": "your-django-secret-key",
                "DATABASE_URL": "sqlite:///db.sqlite3",
                "ALLOWED_HOSTS": "localhost,127.0.0.1"
            },
            "dockerfile": {
                "base_image": "python:3.11-slim",
                "working_dir": "/app",
                "expose_port": 8000,
                "command": "python manage.py runserver 0.0.0.0:8000"
            }
        }
    },
    "react": {
        "name": "React",
        "description": "React application with modern JavaScript tooling",
        "configs": {
            ".prettierrc": {
                "semi": True,
                "singleQuote": True,
                "tabWidth": 2,
                "trailingComma": "es5",
                "printWidth": 80,
                "bracketSpacing": True,
                "arrowParens": "avoid"
            },
            ".eslintrc": {
                "extends": [
                    "react-app",
                    "react-app/jest"
                ],
                "rules": {
                    "no-unused-vars": "warn",
                    "no-console": "warn"
                }
            },
            "tsconfig.json": {
                "compilerOptions": {
                    "target": "es5",
                    "lib": ["dom", "dom.iterable", "es6"],
                    "allowJs": True,
                    "skipLibCheck": True,
                    "esModuleInterop": True,
                    "allowSyntheticDefaultImports": True,
                    "strict": True,
                    "forceConsistentCasingInFileNames": True,
                    "noFallthroughCasesInSwitch": True,
                    "module": "esnext",
                    "moduleResolution": "node",
                    "resolveJsonModule": True,
                    "isolatedModules": True,
                    "noEmit": True,
                    "jsx": "react-jsx"
                },
                "include": ["src"]
            }
        }
    },
    "node": {
        "name": "Node.js",
        "description": "Node.js application with modern JavaScript tooling",
        "configs": {
            ".prettierrc": {
                "semi": True,
                "singleQuote": True,
                "tabWidth": 2,
                "trailingComma": "es5",
                "printWidth": 80
            },
            ".eslintrc": {
                "extends": ["eslint:recommended"],
                "env": {
                    "node": True,
                    "es2021": True
                },
                "parserOptions": {
                    "ecmaVersion": 12,
                    "sourceType": "module"
                },
                "rules": {
                    "no-unused-vars": "warn",
                    "no-console": "off"
                }
            },
            ".env": {
                "NODE_ENV": "development",
                "PORT": "3000",
                "DATABASE_URL": "mongodb://localhost:27017/dbname"
            }
        }
    },
    "python-library": {
        "name": "Python Library",
        "description": "Python library with comprehensive development tooling",
        "configs": {
            "pyproject.toml": {
                "build-system": {
                    "requires": ["setuptools>=61.0", "wheel"],
                    "build-backend": "setuptools.build_meta"
                },
                "tool": {
                    "black": {
                        "line-length": 88,
                        "target-version": ["py38"]
                    },
                    "isort": {
                        "profile": "black",
                        "multi_line_output": 3
                    },
                    "ruff": {
                        "target-version": "py38",
                        "line-length": 88,
                        "select": ["E", "F", "I", "N", "W", "B", "A", "C4", "UP", "ARG", "SIM", "TCH", "Q"],
                        "ignore": ["E501", "B008", "C901"]
                    },
                    "mypy": {
                        "python_version": "3.8",
                        "warn_return_any": True,
                        "disallow_untyped_defs": True,
                        "check_untyped_defs": True,
                        "disallow_untyped_decorators": True
                    },
                    "pytest": {
                        "testpaths": ["tests"],
                        "python_files": ["test_*.py"],
                        "addopts": [
                            "--strict-markers",
                            "--cov=src",
                            "--cov-report=term-missing",
                            "--cov-report=html"
                        ]
                    }
                }
            },
            ".gitignore": [
                "*.pyc",
                "__pycache__/",
                "*.so",
                ".coverage",
                "htmlcov/",
                ".pytest_cache/",
                "build/",
                "dist/",
                "*.egg-info/"
            ]
        }
    }
}


def get_preset_config(preset_name: str) -> Optional[Dict[str, Any]]:
    """
    Get configuration for a specific preset.

    Args:
        preset_name: The preset name

    Returns:
        Optional[Dict[str, Any]]: Preset configuration or None if not found
    """
    return PRESETS.get(preset_name)


def list_presets() -> List[str]:
    """
    Get all available preset names.

    Returns:
        List[str]: List of preset names
    """
    return list(PRESETS.keys())


def get_preset_info(preset_name: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a specific preset.

    Args:
        preset_name: The preset name

    Returns:
        Optional[Dict[str, Any]]: Preset info or None if not found
    """
    preset = PRESETS.get(preset_name)
    if preset:
        return {
            "name": preset["name"],
            "description": preset["description"],
            "configs": list(preset["configs"].keys())
        }
    return None


def validate_preset(preset_name: str) -> bool:
    """
    Validate if a preset name is supported.

    Args:
        preset_name: The preset name to validate

    Returns:
        bool: True if supported, False otherwise
    """
    return preset_name in PRESETS 