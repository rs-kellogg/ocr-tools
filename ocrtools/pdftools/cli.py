import json
import typer
import logging
from pathlib import Path
from rich import console as cons
from typing import Dict, Optional, List
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
    F.export_pages(pdf_file, outdir, start, end)


# -----------------------------------------------------------------------------
@app.command()
def ocr_pages(
    indir: Path = typer.Argument(..., help="Path to input files"),
    outdir: Path = typer.Option(Path("."), help="Path to output page image files"),
):
    console.print(f"OCR'ing pages from: {indir}")
    outdir.mkdir(parents=True, exist_ok=True)

    batch_size = 10
    img_files = sorted(indir.glob("*.png"))

    for i in range(0, len(img_files), batch_size):
        # Extract the current batch of files
        batch_files = img_files[i : i + batch_size]
        doc_map = dict()

        # Process the files in the current batch
        for img_file in batch_files:
            console.print(f"OCR'ing page: {img_file}")
            doc_map[img_file] = F.ocr_page_async(img_file)

        for img_file in doc_map:
            console.print(f"Saving OCR results for page: {img_file}")
            doc = doc_map[img_file]
            doc.text
            json_path = outdir / f"json/{img_file.stem}.json"
            json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(json_path, "w") as f:
                json.dump(doc.document.response, f)
            png_path = outdir / f"png/{img_file.stem}.png"
            png_path.parent.mkdir(parents=True, exist_ok=True)
            doc.document.visualize().save(png_path)


@app.command()
def export_tables(
    indir: Path = typer.Argument(..., help="Path to input files"),
    outdir: Path = typer.Option(Path("."), help="Path to output CSV files"),
):
    console.print(f"Extracting tables from: {indir}")
    outdir.mkdir(parents=True, exist_ok=True)
    for json_file in indir.glob("*.json"):
        console.print(f"Extracting tables from: {json_file}")
        F.extract_tables(json_file, outdir)


# -----------------------------------------------------------------------------
@app.command()
def extract_text(
    in_dir: Path = typer.Argument(..., help="Path to input PDF files"),
    out_dir: Optional[Path] = typer.Option(
        Path("."),
        "--dir",
        help="The directory where the extracted output files will be created.",
    ),
):
    logging.basicConfig(filename=f"{out_dir}/extract.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    logger = logging.getLogger()

    for pdf in in_dir.glob("*.pdf"):
        console.print(f"processing file: {pdf.name}")
        logger.info(pdf.name)
        try:
            paper = F.PaperItem(pdf)
            paper.extract(out_dir, text_only=True)
        except Exception as e:
            logger.error(f"exception: {type(e)}")
            continue
