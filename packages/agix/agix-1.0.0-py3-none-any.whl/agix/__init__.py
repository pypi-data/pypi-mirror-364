"""AGI core package."""

import logging

if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)

__version__ = "0.8.3"

__all__ = [
    "agents",
    "architecture",
    "cli",
    "control",
    "dashboard",
    "environments",
    "learning",
    "memory",
    "perception",
    "reasoning",
]
