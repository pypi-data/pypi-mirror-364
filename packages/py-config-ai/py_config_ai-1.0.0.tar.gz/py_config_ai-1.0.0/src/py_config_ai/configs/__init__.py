"""Configuration templates and schemas for py-config-ai."""

from .config_types import SUPPORTED_CONFIGS, get_config_info
from .presets import PRESETS, get_preset_config

__all__ = [
    "SUPPORTED_CONFIGS",
    "get_config_info",
    "PRESETS",
    "get_preset_config",
] 