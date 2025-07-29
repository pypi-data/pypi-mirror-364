"""
BlogHero - Generate hero images by overlaying text on background images.

A simple tool for adding text overlays to background images.
"""

from .core import HeroImageGenerator
from .models import TextConfig, ImageGeneration
from .cli import cli

__version__ = "0.1.0"
__author__ = "Yegor Tokmakov"
__email__ = "yegor@tokmakov.biz"

__all__ = [
    "HeroImageGenerator",
    "TextConfig",
    "ImageGeneration",
    "cli",
]
