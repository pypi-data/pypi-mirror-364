"""
Utility functions for BlogHero.
"""
import hashlib
from pathlib import Path
from typing import Union, Tuple
from PIL import Image


def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure a directory exists, creating it if necessary."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def generate_cache_key(*args) -> str:
    """Generate a cache key from arguments."""
    content = "_".join(str(arg) for arg in args)
    return hashlib.md5(content.encode()).hexdigest()


def validate_image_size(width: int, height: int) -> Tuple[int, int]:
    """Validate and clamp image dimensions."""
    width = max(100, min(4000, width))
    height = max(100, min(4000, height))
    return width, height


def optimize_image_for_web(image: Image.Image, max_file_size: int = 500_000) -> Image.Image:
    """Optimize image for web usage while maintaining quality."""
    # Start with high quality
    quality = 95
    
    while quality > 60:
        # Save to memory and check size
        from io import BytesIO
        buffer = BytesIO()
        image.save(buffer, format='JPEG', quality=quality, optimize=True)
        
        if buffer.tell() <= max_file_size:
            break
        
        quality -= 5
    
    return image


def get_text_dimensions(text: str, font) -> Tuple[int, int]:
    """Get text dimensions for layout calculations."""
    try:
        from PIL import ImageDraw
        # Create a temporary image to measure text
        temp_img = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(temp_img)
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    except Exception:
        # Fallback estimation
        return len(text) * 12, 20


def parse_color(color: str) -> Tuple[int, int, int]:
    """Parse a color string into RGB tuple.
    
    Supports:
    - Named colors: 'white', 'black', 'red', etc.
    - Hex colors: '#ffffff', '#fff', 'ffffff', 'fff'
    - RGB strings: 'rgb(255, 255, 255)'
    """
    color = color.strip().lower()
    
    # Named colors
    named_colors = {
        'white': (255, 255, 255),
        'black': (0, 0, 0),
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'cyan': (0, 255, 255),
        'magenta': (255, 0, 255),
        'gray': (128, 128, 128),
        'grey': (128, 128, 128),
        'orange': (255, 165, 0),
        'purple': (128, 0, 128),
        'brown': (165, 42, 42),
        'pink': (255, 192, 203),
        'lime': (0, 255, 0),
        'navy': (0, 0, 128),
        'silver': (192, 192, 192),
        'gold': (255, 215, 0),
    }
    
    if color in named_colors:
        return named_colors[color]
    
    # RGB format: rgb(r, g, b)
    if color.startswith('rgb(') and color.endswith(')'):
        rgb_values = color[4:-1].split(',')
        if len(rgb_values) == 3:
            try:
                return tuple(int(v.strip()) for v in rgb_values)
            except ValueError:
                pass
    
    # Hex format
    if color.startswith('#'):
        return hex_to_rgb(color)
    elif len(color) in (3, 6) and all(c in '0123456789abcdef' for c in color):
        return hex_to_rgb('#' + color)
    
    # Default to white if parsing fails
    return (255, 255, 255)


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex color."""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def blend_colors(color1: Tuple[int, int, int], color2: Tuple[int, int, int], ratio: float) -> Tuple[int, int, int]:
    """Blend two RGB colors by a given ratio (0.0 to 1.0)."""
    ratio = max(0.0, min(1.0, ratio))
    
    r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
    g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
    b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
    
    return (r, g, b)


def get_contrast_color(background: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Get contrasting text color (black or white) for a given background."""
    # Calculate luminance
    luminance = (0.299 * background[0] + 0.587 * background[1] + 0.114 * background[2]) / 255
    
    # Return black for light backgrounds, white for dark backgrounds
    return (0, 0, 0) if luminance > 0.5 else (255, 255, 255)


def smart_text_wrap(text: str, max_width: int, font) -> list[str]:
    """Intelligently wrap text to fit within a given width."""
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        text_width, _ = get_text_dimensions(test_line, font)
        
        if text_width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                # Word is too long, force break
                lines.append(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines


def load_image_safe(path: Union[str, Path]) -> Image.Image:
    """Safely load an image with error handling."""
    try:
        image = Image.open(path)
        # Convert to RGB if necessary
        if image.mode not in ('RGB', 'RGBA'):
            image = image.convert('RGB')
        return image
    except Exception as e:
        raise ValueError(f"Could not load image from {path}: {e}")


def create_thumbnail(image: Image.Image, max_size: Tuple[int, int]) -> Image.Image:
    """Create a thumbnail while maintaining aspect ratio."""
    image_copy = image.copy()
    image_copy.thumbnail(max_size, Image.Resampling.LANCZOS)
    return image_copy
