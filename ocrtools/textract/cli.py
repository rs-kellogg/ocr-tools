import json
import typer
import logging
from pathlib import Path
from rich import console as cons
from typing import Dict, Optional, List
from PIL import Image as im
import ocrtools.textract.functions as F

# -----------------------------------------------------------------------------
app = typer.Typer()
console = cons.Console(style="green on black")
CONFIG: Dict[str, str] = {}


# -----------------------------------------------------------------------------
@app.command()
def ocr_pdf_files(
    indir: Path = typer.Argument(..., help="Path to input files"),
    outdir: Path = typer.Option(Path("."), help="Path to output page image files"),
):
    console.print(f"OCR'ing files from: {indir}")
    outdir.mkdir(parents=True, exist_ok=True)

    batch_size = 10
    img_files = sorted(indir.glob("*.pdf"))

    for i in range(0, len(img_files), batch_size):
        # Extract the current batch of files
        batch_files = img_files[i : i + batch_size]
        doc_map = dict()

        # Process the files in the current batch
        for file in batch_files:
            console.print(f"OCR'ing file: {file}")
            doc_map[file] = F.ocr_pdf(file)

        for file in doc_map:
            console.print(f"Saving OCR results for file: {file}")
            doc = doc_map[file]
            doc.text
            json_path = outdir / f"json/{file.stem}.json"
            json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(json_path, "w") as f:
                json.dump(doc.document.response, f)


# -----------------------------------------------------------------------------
@app.command()
def ocr_png_files(
    indir: Path = typer.Argument(..., help="Path to input PNG files"),
    outdir: Path = typer.Option(Path("."), help="Path to output files"),
):
    console.print(f"OCR'ing files from: {indir}")
    outdir.mkdir(parents=True, exist_ok=True)

    batch_size = 10
    img_files = sorted(indir.glob("*.png"))

    for i in range(0, len(img_files), batch_size):
        # Extract the current batch of files
        batch_files = img_files[i : i + batch_size]
        doc_map = dict()

        # Process the files in the current batch
        for png_file in batch_files:
            console.print(f"OCR'ing file: {png_file}")
            doc_map[png_file] = F.ocr_png(png_file)

        for png_file in doc_map:
            console.print(f"Saving OCR results for file: {png_file}")
            doc = doc_map[png_file]
            doc.text
            json_path = outdir / f"json/{png_file.stem}.json"
            json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(json_path, "w") as f:
                json.dump(doc.document.response, f)
            png_path = outdir / f"png/{png_file.stem}.png"
            png_path.parent.mkdir(parents=True, exist_ok=True)
            doc.document.visualize().save(png_path)


# -----------------------------------------------------------------------------
@app.command()
def export_json_tables(
    indir: Path = typer.Argument(..., help="Path to input files"),
    outdir: Path = typer.Option(Path("."), help="Path to output CSV files"),
):
    console.print(f"Extracting tables from: {indir}")
    outdir.mkdir(parents=True, exist_ok=True)
    for json_file in indir.glob("*.json"):
        console.print(f"Extracting tables from: {json_file}")
        F.export_json_tables(json_file, outdir)


# -----------------------------------------------------------------------------
@app.command()
def export_json_text(
    indir: Path = typer.Argument(..., help="Path to input files"),
    outdir: Path = typer.Option(Path("."), help="Path to output text files"),
):
    console.print(f"Extracting tables from: {indir}")
    outdir.mkdir(parents=True, exist_ok=True)
    for json_file in indir.glob("*.json"):
        console.print(f"Extracting tables from: {json_file}")
        F.export_json_text(json_file, outdir)


