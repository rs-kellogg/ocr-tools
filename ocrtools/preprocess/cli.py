import typer
from pathlib import Path
from rich import console as cons
from typing import Dict, Optional
from PIL import Image as im
from ocrtools.preprocess import functions as F


# -----------------------------------------------------------------------------
app = typer.Typer()
console = cons.Console(style="green on black")
CONFIG: Dict[str, str] = {}


# -----------------------------------------------------------------------------
@app.command()
def deskew(
    img_file: Path = typer.Argument(..., help="Path to input image file"),
    out_file: Path = typer.Option(None, help="Path to output image file"),
):
    console.print(f"deskewing image file: {img_file}")
    img = im.open(img_file)
    img = F.deskew(img)
    if out_file is None:
        out_file = img_file.parent / f"{img_file.stem}_deskewed{img_file.suffix}"
    img.save(out_file)
    console.print(f"saved deskewed image to: {out_file}")
