"""
Command line interface for BlogHero.
"""
import click
from pathlib import Path
from typing import Optional

from .core import HeroImageGenerator


@click.group()
@click.version_option()
def cli():
    """BlogHero - Generate hero images by overlaying text on background images."""
    pass


@cli.command()
@click.argument("background", type=click.Path(exists=True), required=True)
@click.argument("title", required=True)
@click.option("--subtitle", "-s", help="Subtitle text")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--title-color", default="white", help="Title color (default: white)")
@click.option("--subtitle-color", default="white", help="Subtitle color (default: white)")
@click.option("--title-size", type=int, default=72, help="Title font size (default: 72)")
@click.option("--subtitle-size", type=int, default=36, help="Subtitle font size (default: 36)")
@click.option("--font-family", default="Arial", help="Font family (default: Arial)")
@click.option("--font-file", type=click.Path(exists=True), help="Path to custom font file (.ttf, .otf)")
@click.option("--position", type=click.Choice(["left", "center", "right"]), default="left", 
              help="Text position (default: left)")
@click.option("--max-width", type=int, help="Maximum text width for wrapping (pixels)")
@click.option("--line-spacing", type=int, default=10, help="Line spacing for wrapped text (default: 10)")
@click.option("--quality", type=int, default=95, help="JPEG quality (1-100)")
def generate(
    background: str,
    title: str,
    subtitle: Optional[str],
    output: Optional[str],
    title_color: str,
    subtitle_color: str,
    title_size: int,
    subtitle_size: int,
    font_family: str,
    font_file: Optional[str],
    position: str,
    max_width: Optional[int],
    line_spacing: int,
    quality: int,
):
    """Generate a hero image by overlaying text on a background image.
    
    BACKGROUND: Path to background image file or directory containing images
    TITLE: Main title text to overlay
    """
    try:
        # Generate image
        generator = HeroImageGenerator()
        image = generator.generate(
            background_path=background,
            title=title,
            subtitle=subtitle,
            title_color=title_color,
            subtitle_color=subtitle_color,
            title_size=title_size,
            subtitle_size=subtitle_size,
            font_family=font_family,
            font_file=font_file,
            position=position,
            max_width=max_width,
            line_spacing=line_spacing
        )
        
        # Determine output path
        if not output:
            bg_path = Path(background)
            if bg_path.is_file():
                name_base = bg_path.stem
            else:
                name_base = "hero"
            output = f"{name_base}_with_text.jpg"
        
        # Save image
        image.save(output, quality=quality, optimize=True)
        click.echo(f"Hero image saved as: {output}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    cli()
