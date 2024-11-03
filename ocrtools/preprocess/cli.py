import typer
from pathlib import Path
from rich import console as cons
from typing import Dict, Optional
from PIL import Image as im
from ocrtools.preprocess import functions as F
from skimage import io
import numpy as np
import cv2


# -----------------------------------------------------------------------------
app = typer.Typer()
console = cons.Console(style="green on black")
CONFIG: Dict[str, str] = {}


# -----------------------------------------------------------------------------
@app.command()
def extract_png_pages(
    pdf_file: Path = typer.Argument(..., help="Path to input PDF file"),
    outdir: Path = typer.Option(Path("."), help="Path to output page image files"),
    start: Optional[int] = typer.Option(None, help="Starting page number"),
    end: Optional[int] = typer.Option(None, help="Ending page number"),
):
    console.print(f"extracting pages from: {pdf_file}")
    outdir.mkdir(parents=True, exist_ok=True)
    F.export_png_pages(pdf_file, outdir, start, end)


# -----------------------------------------------------------------------------
@app.command()
def deskew(
    img_file: Path = typer.Argument(..., help="Path to input image file"),
    out: Path = typer.Option(None, help="Path to output image file"),
):
    console.print(f"deskewing image file: {img_file}")
    if out is None:
        out = img_file.parent / f"{img_file.stem}_deskewed{img_file.suffix}"
    
    img = im.open(img_file)
    img = F.deskew(img)
    img.save(out)

    console.print(f"saved deskewed image to: {out}")
