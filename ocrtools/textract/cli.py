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
def ocr_files(
    indir: Path = typer.Argument(..., help="Path to input files"),
    s3bucket: Path = typer.Argument(..., help="Name of S3 bucket"),
    outdir: Path = typer.Option(Path("."), help="Path to output page image files"),
    file_type: str = typer.Option("pdf", help="Type of input files. Currently only supports 'pdf' and 'png'"),
    tables: bool = typer.Option(False, help="Extract tables from the input files"),
):
    console.print(f"OCR'ing files from: {indir}, using S3 bucket: {s3bucket}")
    outdir.mkdir(parents=True, exist_ok=True)

    batch_size = 10
    src_files = sorted(indir.glob(f"*.{file_type}"))

    for i in range(0, len(src_files), batch_size):
        # Extract the current batch of files
        batch_files = src_files[i : i + batch_size]
        doc_map = dict()

        # Process the files in the current batch
        for src_file in batch_files:
            console.print(f"OCR'ing file: {src_file}")
            doc_map[src_file] = F.ocr_file(src_file, s3_bucket=s3bucket, file_type=file_type, extract_tables=tables)

        for file in doc_map:
            console.print(f"Saving OCR results for file: {file}")
            doc = doc_map[file]
            doc.text
            json_path = outdir / f"{file.stem}.json"
            with open(json_path, "w") as f:
                json.dump(doc.document.response, f)

# -----------------------------------------------------------------------------
@app.command()
def export_json_tables(
    indir: Path = typer.Argument(..., help="Path to input files"),
    outdir: Path = typer.Option(Path("./csv"), help="Path to output CSV files"),
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
    console.print(f"Extracting text from: {indir}")
    outdir.mkdir(parents=True, exist_ok=True)
    for json_file in indir.glob("*.json"):
        console.print(f"Extracting text from: {json_file}")
        F.export_json_text(json_file, outdir)


