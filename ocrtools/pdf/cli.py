import json
import typer
import fitz
import logging
from pathlib import Path
from rich import console as cons
from typing import Dict, Optional, List


# -----------------------------------------------------------------------------
app = typer.Typer()
console = cons.Console(style="green on black")
CONFIG: Dict[str, str] = {}


# -----------------------------------------------------------------------------
@app.command()
def extract_text(
    indir: Path = typer.Argument(..., help="Path to input files"),
    outdir: Path = typer.Option(Path("."), help="Path to output page image files"),
):
    console.print(f"Extracting text from PDFs in {indir}")    
    outdir.mkdir(parents=True, exist_ok=True)

    for file in indir.glob("*.pdf"):
        console.print(f"file: {file.name}")
        with fitz.open(file) as doc:  # open document
            text = chr(12).join([page.get_text(sort=True) for page in doc])
            (outdir/f"{file.stem}.txt").write_bytes(text.encode())