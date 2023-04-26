import typer
from pathlib import Path
from rich import console as cons
from typing import Dict, Optional


# -----------------------------------------------------------------------------
app = typer.Typer()
console = cons.Console(style="green on black")
CONFIG: Dict[str, str] = {}


# -----------------------------------------------------------------------------
@app.command()
def deskew(
    img_file: Path = typer.Argument(..., help="Path to image file"),
):
    console.print(f"deskewing image file: {img_file}")

