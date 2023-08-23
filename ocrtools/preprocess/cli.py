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
def deskew(
    img_file: Path = typer.Argument(..., help="Path to input image file"),
    output: Path = typer.Option(None, help="Path to output image file"),
):
    console.print(f"deskewing image file: {img_file}")
    if output is None:
        output = img_file.parent / f"{img_file.stem}_deskewed{img_file.suffix}"
    # img = im.open(img_file)
    # img = F.deskew(img)
    # img.save(output)

    # image = io.imread(img_file)
    # rotated = F.deskew2(image)
    # io.imsave(output, rotated.astype(np.uint8))

    image = cv2.imread(str(img_file))
    rotated = F.deskew3(image)
    io.imsave(output, rotated.astype(np.uint8))

    console.print(f"saved deskewed image to: {output}")
