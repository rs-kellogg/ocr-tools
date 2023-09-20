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
    
