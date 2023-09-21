import json
import typer
from pathlib import Path
from rich import console as cons
from typing import Dict, Optional
from PIL import Image as im
import ocrtools.pdftools.functions as F

# -----------------------------------------------------------------------------
app = typer.Typer()
console = cons.Console(style="green on black")
CONFIG: Dict[str, str] = {}


# -----------------------------------------------------------------------------
@app.command()
def extract_pages(
    pdf_file: Path = typer.Argument(..., help="Path to input PDF file"),
    outdir: Path = typer.Option(Path("."), help="Path to output page image files"),
    start: Optional[int] = typer.Option(None, help="Starting page number"),
    end: Optional[int] = typer.Option(None, help="Ending page number"),
):
    console.print(f"extracting pages from: {pdf_file}")
    outdir.mkdir(parents=True, exist_ok=True)
    F.extract_pages(pdf_file, outdir, start, end)
    

# -----------------------------------------------------------------------------
@app.command()
def ocr_pages(
    indir: Path = typer.Argument(..., help="Path to input files"),
    outdir: Path = typer.Option(Path("."), help="Path to output page image files"),
):
    console.print(f"OCR'ing pages from: {indir}")
    outdir.mkdir(parents=True, exist_ok=True)
    doc_map = dict()
    for img_file in indir.glob("*.png"):
        console.print(f"OCR'ing page: {img_file}")
        doc_map[img_file] = F.ocr_page_async(img_file)

    for img_file in doc_map:
        console.print(f"saving OCR results for page: {img_file}")
        doc = doc_map[img_file]
        doc.text
        json_path = outdir/f"json/{img_file.stem}.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, "w") as f:
            json.dump(doc.document.response, f)
        png_path = outdir/f"png/{img_file.stem}.png"
        png_path.parent.mkdir(parents=True, exist_ok=True)
        doc.document.visualize().save(png_path)
 