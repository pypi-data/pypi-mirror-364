# BlogHero

A simple Python library and CLI tool for generating hero images by overlaying text on background images. Create professional-looking cover images by adding custom titles and subtitles to your background images.

## Features

- 🎨 **Text overlay on background images** - Add titles and subtitles to any image
- 🖼️ **Flexible background support** - Use image files or random selection from directories
- 🎯 **Smart positioning** - Left, center, or right text alignment
- 🌈 **Color customization** - Support for named colors, hex codes, and RGB values
- 📏 **Size preservation** - Output images maintain original background dimensions
- ⚡ **CLI and Python API** - Use in automation workflows or as a library
- 🎛️ **Configurable typography** - Adjust font sizes and families

## Installation

```bash
pip install bloghero
```

Or install from source:

```bash
git clone https://github.com/yourusername/bloghero.git
cd bloghero
poetry install
```

## Quick Start

### Command Line Interface

Generate a hero image with a background file:

```bash
bloghero generate path/to/background.jpg "My Awesome Blog Post"
```

With subtitle and custom styling:

```bash
bloghero generate path/to/background.jpg "My Awesome Blog Post" \
  --subtitle "A detailed guide to something amazing" \
  --position center \
  --title-color blue \
  --output hero.jpg
```

Use a directory of background images (random selection):

```bash
bloghero generate path/to/backgrounds/ "Random Background Post" \
  --subtitle "Will pick a random image from the directory"
```

### Python API

```python
from bloghero import HeroImageGenerator

generator = HeroImageGenerator()

# Basic usage with background image
image = generator.generate(
    background_path="path/to/background.jpg",
    title="My Blog Post Title"
)
image.save("hero.jpg")

# Advanced usage with all options
image = generator.generate(
    background_path="path/to/backgrounds/",  # Directory for random selection
    title="Advanced Blog Post",
    subtitle="With custom styling",
    title_color="white",
    subtitle_color="lightgray",
    title_size=80,
    subtitle_size=40,
    font_family="Arial",
    position="center"
)
image.save("advanced_hero.jpg", quality=95)
```

## CLI Commands

### Generate Images

```bash
# Basic generation with background image
bloghero generate background.jpg "Title" --output hero.jpg

# With styling options
bloghero generate background.jpg "Title" \
  --subtitle "Subtitle" \
  --title-color white \
  --subtitle-color lightgray \
  --title-size 80 \
  --subtitle-size 40 \
  --position center \
  --quality 95

# Using directory for random background selection
bloghero generate /path/to/backgrounds/ "Title" \
  --subtitle "Random background from directory"

# Different positioning options
bloghero generate bg.jpg "Left aligned" --position left
bloghero generate bg.jpg "Center aligned" --position center
bloghero generate bg.jpg "Right aligned" --position right

# Color options
bloghero generate bg.jpg "Title" --title-color "#ff0000"  # Hex color
bloghero generate bg.jpg "Title" --title-color "rgb(255,0,0)"  # RGB
bloghero generate bg.jpg "Title" --title-color "red"  # Named color
```

## Configuration Options

### Colors

Supported color formats:

- **Named colors**: `white`, `black`, `red`, `green`, `blue`, `yellow`, `cyan`, `magenta`, `gray`, `orange`, `purple`, `brown`, `pink`, `lime`, `navy`, `silver`, `gold`
- **Hex colors**: `#ffffff`, `#fff`, `ffffff`, `fff`
- **RGB values**: `rgb(255, 255, 255)`

### Positioning

- **left**: Text positioned in the left half of the image (default)
- **center**: Text centered on the image
- **right**: Text positioned in the right half of the image

### Font Sizes

- **title-size**: Font size for main title (default: 72)
- **subtitle-size**: Font size for subtitle (default: 36)

### Background Images

**Single image file:**

```bash
bloghero generate /path/to/image.jpg "Title"
```

**Directory (random selection):**

```bash
bloghero generate /path/to/images/ "Title"
```

Supported image formats: JPEG, PNG, BMP, TIFF

## Examples

### Basic Hero Image Generation

```bash
poetry run bloghero generate examples/background/image1.jpg \
    "Bloghero generates hero images for blog posts" \
    --output examples/output.png
```

![Example Hero Image](examples/output.png)

### Basic Text Overlay

```python
from bloghero import HeroImageGenerator

generator = HeroImageGenerator()
image = generator.generate(
    background_path="background.jpg",
    title="Hello World"
)
image.save("output.jpg")
```

### With Subtitle and Styling

```python
image = generator.generate(
    background_path="background.jpg",
    title="My Blog Post",
    subtitle="A comprehensive guide",
    title_color="white",
    subtitle_color="lightgray",
    position="center",
    title_size=80,
    subtitle_size=40
)
```

### Random Background from Directory

```python
image = generator.generate(
    background_path="images/",  # Directory with background images
    title="Random Background",
    subtitle="Randomly selected from directory"
)
```

## CLI Reference

### Command: generate

```bash
bloghero generate BACKGROUND TITLE [OPTIONS]
```

**Arguments:**

- `BACKGROUND`: Path to background image file or directory
- `TITLE`: Main title text to overlay

**Options:**

- `-s, --subtitle TEXT`: Subtitle text
- `-o, --output PATH`: Output file path
- `--title-color TEXT`: Title color (default: white)
- `--subtitle-color TEXT`: Subtitle color (default: white)
- `--title-size INTEGER`: Title font size (default: 72)
- `--subtitle-size INTEGER`: Subtitle font size (default: 36)
- `--font-family TEXT`: Font family (default: Arial)
- `--position [left|center|right]`: Text position (default: left)
- `--quality INTEGER`: JPEG quality 1-100 (default: 95)

## API Reference

### HeroImageGenerator

```python
from bloghero import HeroImageGenerator

generator = HeroImageGenerator()
image = generator.generate(
    background_path: str,           # Required: background image or directory
    title: str,                     # Required: main title text
    subtitle: Optional[str] = None, # Optional subtitle
    title_color: str = "white",     # Title color
    subtitle_color: str = "white",  # Subtitle color
    title_size: int = 72,           # Title font size
    subtitle_size: int = 36,        # Subtitle font size
    font_family: str = "Arial",     # Font family
    position: str = "left"          # Text position: left/center/right
) -> PIL.Image.Image
```

## Requirements

- Python 3.11+
- Pillow (PIL)
- Click
- Pydantic

## License

MIT License - see LICENSE file for details.
