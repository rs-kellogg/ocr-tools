import os
import re
from dataclasses import dataclass, InitVar, field
from pathlib import Path
from typing import Iterable, List
import fitz
from PIL import Image
from textractor.entities.document import Document
from textractor.entities.lazy_document import LazyDocument
from textractor import Textractor
from textractor.data.constants import TextractFeatures



# -----------------------------------------------------------------------------
def ocr_png(
    img_file: Path,
    aws_profile: str = "default",
    s3_bucket: str = "s3://kellogg-ocr/temp",
    extract_tables = False,
) -> LazyDocument:
    if extract_tables:
        features = [TextractFeatures.TABLES]
    else:
        features = []
    extractor = Textractor(profile_name=aws_profile)
    doc = extractor.start_document_text_detection(
        file_source=Image.open(str(img_file)),
        s3_output_path=s3_bucket,
        s3_upload_path=s3_bucket,
        save_image=True,
    )
    return doc


# -----------------------------------------------------------------------------
def ocr_pdf(
    pdf_file: Path,
    aws_profile: str = "default",
    s3_bucket: str = "s3://kellogg-ocr/temp",
) -> LazyDocument:
    extractor = Textractor(profile_name=aws_profile)
    doc = extractor.start_document_analysis(
        file_source=str(pdf_file),
        features=[TextractFeatures.TABLES],
        s3_output_path=s3_bucket,
        s3_upload_path=s3_bucket,
        save_image=True,
    )
    return doc

# -----------------------------------------------------------------------------
def export_json_tables(json_path: Path, outdir: Path):
    if type(json_path) == str:
        json_path = Path(json_path)
    if type(outdir) == str:
        outdir = Path(outdir)
    with open(json_path, "r") as f:
        doc = Document.open(f)
        print(f"Found {len(doc.tables)} tables in {json_path.name}")
        for i, table in enumerate(doc.tables):
            csv_file = outdir / f"{json_path.stem}-{i+1}.csv"
            csv_file.parent.mkdir(parents=True, exist_ok=True)
            csv_file.write_text(table.to_csv())


# -----------------------------------------------------------------------------
def export_json_text(json_path: Path, outdir: Path):
    if type(json_path) == str:
        json_path = Path(json_path)
    if type(outdir) == str:
        outdir = Path(outdir)
    with open(json_path, "r") as f:
        doc = Document.open(f)
        print(f"Exporting text from {json_path.name}")
        text_file = outdir / f"{json_path.stem}.txt"
        text_file.parent.mkdir(parents=True, exist_ok=True)
        text_file.write_text(doc.text)
