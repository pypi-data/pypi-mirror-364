"""
Data models for BlogHero.
"""
from typing import Optional
from pydantic import BaseModel, Field


class TextConfig(BaseModel):
    """Configuration for text overlay."""
    title: str = Field(..., description="Main title text")
    subtitle: Optional[str] = Field(None, description="Subtitle text")
    title_color: str = Field("white", description="Title color")
    subtitle_color: str = Field("white", description="Subtitle color")
    title_size: int = Field(72, description="Title font size in points", ge=12, le=200)
    subtitle_size: int = Field(36, description="Subtitle font size in points", ge=8, le=100)
    font_family: str = Field("Arial", description="Font family name")
    position: str = Field("left", description="Text position on image")


class ImageGeneration(BaseModel):
    """Configuration for image generation."""
    background_path: str = Field(..., description="Path to background image or directory")
    output_path: Optional[str] = Field(None, description="Output file path")
    quality: int = Field(95, description="JPEG quality", ge=1, le=100)
    
    # Include text configuration
    text: TextConfig = Field(..., description="Text overlay configuration")
