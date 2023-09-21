import os
from pathlib import Path
from typing import Iterable
import fitz
from PIL import Image
from textractor.entities.document import Document
from textractor.entities.lazy_document import LazyDocument
from textractor import Textractor
from textractor.data.constants import TextractFeatures


def ocr_page(img_file: Path, aws_profile: str = "default") -> Document:
    extractor = Textractor(profile_name=aws_profile)
    doc = extractor.analyze_document(
        file_source=Image.open(str(img_file)),
        features=[TextractFeatures.TABLES],
        save_image=True,
    )
    return doc


def ocr_page_async(
        img_file: Path, 
        aws_profile: str = "default",
        s3_bucket: str = "s3://kellogg-ocr/temp",
    ) -> LazyDocument:
    extractor = Textractor(profile_name=aws_profile)
    doc = extractor.start_document_analysis(
        file_source=Image.open(str(img_file)),
        features=[TextractFeatures.TABLES],
        s3_output_path=s3_bucket,
        s3_upload_path=s3_bucket,
        save_image=True,
    )
    return doc


def extract_pages(pdf: Path, outdir: Path, page_start: int, page_end: int):
    doc = fitz.open(pdf)

    if page_start is None:
        page_start = 0
    if page_end is None:
        page_end = len(doc)
    page_end = min(page_end + 1, len(doc))
    assert page_start <= page_end, "page_start must be less than or equal to page_end"

    mat = fitz.Matrix(3, 3)
    for i in range(page_start, page_end):
        page = doc[i-1]
        pix = page.get_pixmap(matrix = mat)
        pix.save(outdir/f"page-{str(page.number+1).zfill(4)}.png")
