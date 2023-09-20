from pathlib import Path
from typing import Iterable
import fitz


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
