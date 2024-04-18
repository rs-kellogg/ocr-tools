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
def ocr_file(
    file: Path,
    s3_bucket: str,
    aws_profile: str = "default",
    extract_tables: bool = False,
    file_type: str = "pdf",
) -> LazyDocument:
    if file_type == "pdf":
        file_source = str(file)
        save_image = False
    elif file_type == "png":
        file_source = Image.open(str(file))
        save_image = True
    else:
        raise ValueError(f"Invalid file type: {file_type}")

    extractor = Textractor(profile_name=aws_profile)
    if extract_tables:
        doc = extractor.start_document_analysis(
            file_source=file_source,
            features=[TextractFeatures.TABLES],
            s3_upload_path=f"s3://{s3_bucket}",
            s3_output_path=f"s3://{s3_bucket}",
            save_image=save_image,
        )
    else:
        doc = extractor.start_document_text_detection(
            file_source=file_source,
            s3_upload_path=f"s3://{s3_bucket}",
            s3_output_path=f"s3://{s3_bucket}",
            save_image=save_image,
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
        text_file = outdir / f"{json_path.stem}.txt"
        text_file.parent.mkdir(parents=True, exist_ok=True)
        text_file.write_text(doc.text)
