"""
Core functionality for generating hero images by overlaying text on background images.
"""
import random
from typing import Optional, Union
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from .fonts import FontManager
from .utils import parse_color, smart_text_wrap


class HeroImageGenerator:
    """Main class for generating hero images by overlaying text on background images."""
    
    def __init__(self):
        self.font_manager = FontManager()
    
    def generate(
        self,
        background_path: Union[str, Path],
        title: str,
        subtitle: Optional[str] = None,
        title_color: str = "white",
        subtitle_color: str = "white",
        title_size: int = 72,
        subtitle_size: int = 36,
        font_family: str = "Arial",
        font_file: Optional[str] = None,
        position: str = "left",
        max_width: Optional[int] = None,
        line_spacing: int = 10
    ) -> Image.Image:
        """
        Generate a hero image by overlaying text on a background image.
        
        Args:
            background_path: Path to background image file or directory containing images
            title: Main title text
            subtitle: Optional subtitle text
            title_color: Color for title text (default: white)
            subtitle_color: Color for subtitle text (default: white)
            title_size: Font size for title (default: 72)
            subtitle_size: Font size for subtitle (default: 36)
            font_family: Font family to use (default: Arial)
            font_file: Path to custom font file (.ttf, .otf) - overrides font_family if provided
            position: Text position - left, center, or right (default: left)
            max_width: Maximum width for text wrapping in pixels (default: None)
            line_spacing: Spacing between lines for wrapped text (default: 10)
            
        Returns:
            PIL Image object with original background size
        """
        # Resolve background image path
        resolved_bg_path = self._resolve_background_image_path(background_path)
        if not resolved_bg_path:
            raise ValueError(f"No valid background image found at: {background_path}")
        
        # Load background image - keep original size
        background = Image.open(resolved_bg_path)
        
        # Create a copy to work with (preserves original size)
        image = background.copy()
        draw = ImageDraw.Draw(image)
        
        # Parse colors
        title_rgb = parse_color(title_color)
        subtitle_rgb = parse_color(subtitle_color)
        
        # Add text to image
        self._add_text_to_image(
            image, draw, title, subtitle,
            title_rgb, subtitle_rgb,
            title_size, subtitle_size,
            font_family, font_file, position, max_width, line_spacing
        )
        
        return image
    
    def _resolve_background_image_path(self, background_path: Union[str, Path]) -> Optional[Path]:
        """
        Resolve background image path. If it's a directory, select a random image.
        
        Args:
            background_path: Path to image file or directory containing images
            
        Returns:
            Path to the selected image file, or None if no valid image found
        """
        path = Path(background_path)
        
        if not path.exists():
            raise ValueError(f"Background path '{background_path}' does not exist")
        
        if path.is_file():
            # Verify it's an image file
            if path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']:
                return path
            else:
                raise ValueError(f"'{background_path}' is not a supported image format")
        
        elif path.is_dir():
            # Find all image files in the directory
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
            image_files = []
            
            for ext in image_extensions:
                image_files.extend(path.glob(f"*{ext}"))
                image_files.extend(path.glob(f"*{ext.upper()}"))
            
            if not image_files:
                raise ValueError(f"No supported image files found in directory '{background_path}'")
            
            # Select a random image
            selected_image = random.choice(image_files)
            print(f"Selected random background image: {selected_image.name}")
            return selected_image
        
        return None
    
    def _add_text_to_image(
        self,
        image: Image.Image,
        draw: ImageDraw.Draw,
        title: str,
        subtitle: Optional[str],
        title_color: tuple,
        subtitle_color: tuple,
        title_size: int,
        subtitle_size: int,
        font_family: str,
        font_file: Optional[str],
        position: str,
        max_width: Optional[int] = None,
        line_spacing: int = 10
    ):
        """Add title and subtitle text to the image with optional text wrapping and auto-scaling."""
        width, height = image.size
        margin = max(50, width // 20)  # At least 50px margin or 5% of width
        
        # Calculate available height for text (leaving margins at top and bottom)
        available_height = height - (margin * 2)
        
        # Start with original font sizes
        current_title_size = title_size
        current_subtitle_size = subtitle_size
        scale_factor = 1.0
        
        # Iteratively calculate and scale if needed
        while True:
            # Load fonts with current sizes
            title_font = self.font_manager.get_font(font_family, current_title_size, font_file)
            subtitle_font = self.font_manager.get_font(font_family, current_subtitle_size, font_file) if subtitle else None
            
            # Determine maximum text width based on position and max_width parameter
            if max_width:
                # Use user-specified max width, but scale it down if we're scaling fonts
                text_max_width = int(max_width * scale_factor)
            else:
                # Calculate max width based on position
                if position == "left":
                    # For left position, use left half minus margins
                    text_max_width = (width // 2) - (margin * 2)
                else:
                    # For center and right, use most of the width
                    text_max_width = width - (margin * 2)
            
            # Wrap title text if necessary
            title_lines = smart_text_wrap(title, text_max_width, title_font)
            
            # Calculate total title height
            title_line_height = current_title_size + int(line_spacing * scale_factor)
            total_title_height = len(title_lines) * title_line_height - int(line_spacing * scale_factor)  # Remove spacing after last line
            
            # Calculate subtitle height if present
            total_subtitle_height = 0
            subtitle_lines = []
            subtitle_line_height = 0
            if subtitle:
                subtitle_lines = smart_text_wrap(subtitle, text_max_width, subtitle_font)
                subtitle_line_height = current_subtitle_size + int(line_spacing * scale_factor)
                total_subtitle_height = len(subtitle_lines) * subtitle_line_height - int(line_spacing * scale_factor)
            
            # Calculate total text block height (including spacing between title and subtitle)
            spacing_between_blocks = 20 if subtitle else 0
            total_text_height = total_title_height + spacing_between_blocks + total_subtitle_height
            
            # Check if text fits within available height
            if total_text_height <= available_height or scale_factor <= 0.3:  # Don't scale below 30%
                break
            
            # Scale down by 10% and try again
            scale_factor *= 0.9
            current_title_size = int(title_size * scale_factor)
            current_subtitle_size = int(subtitle_size * scale_factor)
        
        # Calculate vertical centering position
        text_start_y = margin + (available_height - total_text_height) // 2
        
        
        # Position title based on position setting
        if position == "center":
            # Center each line individually
            title_x_positions = []
            for line in title_lines:
                line_bbox = draw.textbbox((0, 0), line, font=title_font)
                line_width = line_bbox[2] - line_bbox[0]
                title_x_positions.append((width - line_width) // 2)
        elif position == "right":
            # Right align each line
            title_x_positions = []
            for line in title_lines:
                line_bbox = draw.textbbox((0, 0), line, font=title_font)
                line_width = line_bbox[2] - line_bbox[0]
                title_x_positions.append(width - line_width - margin)
        else:  # left (default)
            # Left align all lines
            title_x_positions = [margin] * len(title_lines)
        
        # Draw title lines starting from vertically centered position
        current_y = text_start_y
        for i, (line, x_pos) in enumerate(zip(title_lines, title_x_positions)):
            draw.text((x_pos, current_y), line, fill=title_color, font=title_font)
            current_y += title_line_height
        
        # Add subtitle if provided
        if subtitle:
            # Position subtitle based on position setting
            if position == "center":
                # Center each line individually
                subtitle_x_positions = []
                for line in subtitle_lines:
                    line_bbox = draw.textbbox((0, 0), line, font=subtitle_font)
                    line_width = line_bbox[2] - line_bbox[0]
                    subtitle_x_positions.append((width - line_width) // 2)
            elif position == "right":
                # Right align each line
                subtitle_x_positions = []
                for line in subtitle_lines:
                    line_bbox = draw.textbbox((0, 0), line, font=subtitle_font)
                    line_width = line_bbox[2] - line_bbox[0]
                    subtitle_x_positions.append(width - line_width - margin)
            else:  # left (default)
                # Left align all lines
                subtitle_x_positions = [margin] * len(subtitle_lines)
            
            # Start subtitle below title with spacing
            subtitle_y = current_y + 20
            
            # Draw subtitle lines
            for i, (line, x_pos) in enumerate(zip(subtitle_lines, subtitle_x_positions)):
                draw.text((x_pos, subtitle_y), line, fill=subtitle_color, font=subtitle_font)
                subtitle_y += subtitle_line_height
