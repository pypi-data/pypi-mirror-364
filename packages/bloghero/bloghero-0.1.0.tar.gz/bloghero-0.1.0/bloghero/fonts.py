"""
Font management and Google Fonts integration.
"""
import os
import requests
from pathlib import Path
from typing import Optional, Dict
from PIL import ImageFont
import json


class FontManager:
    """Manages font loading and Google Fonts integration."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path.home() / ".bloghero" / "fonts"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._font_cache: Dict[str, ImageFont.FreeTypeFont] = {}
        self._google_fonts_api_key: Optional[str] = None
    
    def set_google_fonts_api_key(self, api_key: str):
        """Set Google Fonts API key for downloading fonts."""
        self._google_fonts_api_key = api_key
    
    def get_font(self, family: str, size: int, custom_font_path: Optional[str] = None) -> ImageFont.FreeTypeFont:
        """
        Get a font by family name and size.
        
        Args:
            family: Font family name (e.g., 'Arial', 'Roboto')
            size: Font size in pixels
            custom_font_path: Optional path to custom font file (.ttf, .otf)
            
        Returns:
            PIL ImageFont object
        """
        # If custom font path is provided, use it directly
        if custom_font_path:
            cache_key = f"custom_{Path(custom_font_path).name}_{size}"
            
            if cache_key in self._font_cache:
                return self._font_cache[cache_key]
            
            font = self._load_custom_font(custom_font_path, size)
            if font is not None:
                self._font_cache[cache_key] = font
                return font
            # If custom font fails to load, fall back to family-based loading
        
        cache_key = f"{family}_{size}"
        
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]
        
        # Try to load system font first
        font = self._load_system_font(family, size)
        
        if font is None:
            # Try to download from Google Fonts
            font = self._load_google_font(family, size)
        
        if font is None:
            # Fallback to default font
            font = self._load_default_font(size)
        
        self._font_cache[cache_key] = font
        return font
    
    def _load_custom_font(self, font_path: str, size: int) -> Optional[ImageFont.FreeTypeFont]:
        """Load a custom font from the specified file path."""
        try:
            path = Path(font_path)
            if not path.exists():
                print(f"Warning: Custom font file '{font_path}' does not exist")
                return None
            
            if not path.suffix.lower() in ['.ttf', '.otf', '.ttc']:
                print(f"Warning: Custom font file '{font_path}' is not a supported format (.ttf, .otf, .ttc)")
                return None
            
            # For TTC files, explicitly use index 0
            if path.suffix.lower() == '.ttc':
                return ImageFont.truetype(str(path), size, index=0)
            else:
                return ImageFont.truetype(str(path), size)
        
        except Exception as e:
            print(f"Warning: Failed to load custom font '{font_path}': {e}")
            return None
    
    def _load_system_font(self, family: str, size: int) -> Optional[ImageFont.FreeTypeFont]:
        """Try to load font from system font directories."""
        system_font_paths = self._get_system_font_paths()
        
        # For Arial, try alternative fonts first since ArialHB.ttc may not render properly
        if family.lower() == 'arial':
            alternative_fonts = [
                "Geneva.ttf", "Monaco.ttf", "Helvetica.ttc", 
                "HelveticaNeue.ttc", "Apple Symbols.ttf"
            ]
            for font_dir in system_font_paths:
                for alt_font in alternative_fonts:
                    font_path = font_dir / alt_font
                    if font_path.exists():
                        try:
                            # For TTC files, explicitly use index 0
                            if alt_font.endswith('.ttc'):
                                return ImageFont.truetype(str(font_path), size, index=0)
                            else:
                                return ImageFont.truetype(str(font_path), size)
                        except Exception:
                            continue
        
        # Common font file variations (prioritize .ttf over .ttc)
        font_variations = [
            f"{family}.ttf",
            f"{family}.otf", 
            f"{family}-Regular.ttf",
            f"{family}-Regular.otf",
            f"{family.replace(' ', '')}.ttf",
            f"{family.replace(' ', '')}.otf",
            f"{family.lower()}.ttf",
            f"{family.lower()}.otf",
            f"{family}.ttc",  # Try .ttc files last
            f"{family}HB.ttc",
            f"{family.replace(' ', '')}.ttc",
            f"{family.lower()}.ttc",
        ]
        
        for font_dir in system_font_paths:
            for variation in font_variations:
                font_path = font_dir / variation
                if font_path.exists():
                    try:
                        # For TTC files, explicitly use index 0
                        if variation.endswith('.ttc'):
                            return ImageFont.truetype(str(font_path), size, index=0)
                        else:
                            return ImageFont.truetype(str(font_path), size)
                    except Exception:
                        continue
        
        return None
    
    def _load_google_font(self, family: str, size: int) -> Optional[ImageFont.FreeTypeFont]:
        """Download and load font from Google Fonts."""
        if not self._google_fonts_api_key:
            return None
        
        try:
            # Check if font is already cached
            font_file = self.cache_dir / f"{family.replace(' ', '_')}.ttf"
            
            if not font_file.exists():
                # Download font from Google Fonts
                if not self._download_google_font(family, font_file):
                    return None
            
            return ImageFont.truetype(str(font_file), size)
        
        except Exception:
            return None
    
    def _download_google_font(self, family: str, output_path: Path) -> bool:
        """Download a font from Google Fonts."""
        try:
            # Get font info from Google Fonts API
            api_url = f"https://www.googleapis.com/webfonts/v1/webfonts"
            params = {"key": self._google_fonts_api_key, "family": family}
            
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            
            fonts_data = response.json()
            
            if "items" not in fonts_data or not fonts_data["items"]:
                return False
            
            # Get the first font family
            font_info = fonts_data["items"][0]
            
            # Get regular variant URL
            font_files = font_info.get("files", {})
            font_url = font_files.get("regular") or font_files.get("400")
            
            if not font_url:
                return False
            
            # Download font file
            font_response = requests.get(font_url)
            font_response.raise_for_status()
            
            # Save font file
            with open(output_path, "wb") as f:
                f.write(font_response.content)
            
            return True
        
        except Exception:
            return False
    
    def _load_default_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Load default system font as fallback."""
        try:
            # Try proven working fonts first
            proven_fonts = [
                "/System/Library/Fonts/Geneva.ttf",
                "/System/Library/Fonts/Monaco.ttf", 
                "/System/Library/Fonts/Helvetica.ttc"
            ]
            
            for font_path in proven_fonts:
                try:
                    if Path(font_path).exists():
                        return ImageFont.truetype(font_path, size)
                except Exception:
                    continue
            
            # Try common default fonts on macOS
            default_fonts = [
                "Geneva.ttf", "Monaco.ttf", "Helvetica.ttc",
                "Arial.ttf", "Helvetica.ttf", "DejaVuSans.ttf",
                # macOS specific paths for Arial
                "Arial.ttc", "Helvetica.ttc"
            ]
            system_font_paths = self._get_system_font_paths()
            
            for font_dir in system_font_paths:
                for font_name in default_fonts:
                    font_path = font_dir / font_name
                    if font_path.exists():
                        try:
                            return ImageFont.truetype(str(font_path), size)
                        except Exception:
                            continue
            
            # Try to find any .ttf file as fallback (avoid .ttc if possible)
            for font_dir in system_font_paths:
                for font_path in font_dir.glob("*.ttf"):
                    try:
                        return ImageFont.truetype(str(font_path), size)
                    except Exception:
                        continue
                        
            # Last resort - try .ttc files
            for font_dir in system_font_paths:
                for font_path in font_dir.glob("*.ttc"):
                    try:
                        return ImageFont.truetype(str(font_path), size)
                    except Exception:
                        continue
            
            # Ultimate fallback - create a larger default font
            # PIL's default font is too small, so we'll use a basic fallback
            # that at least respects the size parameter somewhat
            return ImageFont.load_default()
        
        except Exception:
            return ImageFont.load_default()
    
    def _get_system_font_paths(self) -> list[Path]:
        """Get system font directories based on OS."""
        paths = []
        
        # Windows
        if os.name == "nt":
            paths.extend([
                Path("C:/Windows/Fonts"),
                Path(os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts")),
            ])
        
        # macOS
        elif os.name == "posix" and os.uname().sysname == "Darwin":
            paths.extend([
                Path("/System/Library/Fonts"),
                Path("/Library/Fonts"),
                Path(os.path.expanduser("~/Library/Fonts")),
            ])
        
        # Linux
        else:
            paths.extend([
                Path("/usr/share/fonts"),
                Path("/usr/local/share/fonts"),
                Path(os.path.expanduser("~/.fonts")),
                Path(os.path.expanduser("~/.local/share/fonts")),
            ])
        
        # Filter to existing directories
        return [p for p in paths if p.exists()]
    
    def list_available_fonts(self) -> list[str]:
        """List all available fonts on the system."""
        available_fonts = set()
        system_font_paths = self._get_system_font_paths()
        
        for font_dir in system_font_paths:
            if font_dir.exists():
                for font_file in font_dir.glob("*.ttf"):
                    # Extract font name from filename
                    font_name = font_file.stem
                    available_fonts.add(font_name)
                
                for font_file in font_dir.glob("*.otf"):
                    # Extract font name from filename
                    font_name = font_file.stem
                    available_fonts.add(font_name)
        
        return sorted(list(available_fonts))
    
    def clear_cache(self):
        """Clear the font cache."""
        self._font_cache.clear()
        
        # Optionally remove cached font files
        if self.cache_dir.exists():
            for font_file in self.cache_dir.glob("*.ttf"):
                font_file.unlink()
            for font_file in self.cache_dir.glob("*.otf"):
                font_file.unlink()
