from pathlib import Path

import click

from src.core import QRGenerator
from src.exceptions import QRGenException


@click.group()
def cli():
    """Advanced QR Code Generator with Logo Embedding"""
    pass


@cli.command()
@click.argument("content", type=str)
@click.argument("output", type=click.Path(path_type=Path))
@click.option("--fill-color", default="black", help="QR code color (name or hex)")
@click.option("--back-color", default="white", help="Background color")
@click.option("--logo", type=click.Path(exists=True, path_type=Path), help="Path to logo image to embed")
@click.option("--version", default=1, type=click.IntRange(1, 40), help="QR code version (1-40, controls size)")
@click.option(
    "--error-correction",
    default="H",
    type=click.Choice(["L", "M", "Q", "H"], case_sensitive=False),
    help="Error correction level",
)
@click.option("--box-size", default=10, type=int, help="Pixels per QR module")
@click.option("--border", default=4, type=int, help="Border size in modules")
def generate(content, output, fill_color, back_color, logo, version, error_correction, box_size, border):
    """Generate customizable QR code with optional logo"""
    try:
        QRGenerator(
            content=content,
            output_path=str(output),
            fill_color=fill_color,
            back_color=back_color,
            logo_path=str(logo) if logo else None,
            version=version,
            error_correction=error_correction,
            box_size=box_size,
            border=border,
        ).generate()
        click.secho(f"✓ QR code successfully generated at: {output}", fg="green")
    except QRGenException as e:
        click.secho(f"✗ Error: {e}", fg="red", err=True)
        raise click.Abort()
