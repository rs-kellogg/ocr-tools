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
def ocr_page(img_file: Path, aws_profile: str = "default") -> Document:
    extractor = Textractor(profile_name=aws_profile)
    doc = extractor.analyze_document(
        file_source=Image.open(str(img_file)),
        features=[TextractFeatures.TABLES],
        save_image=True,
    )
    return doc


# -----------------------------------------------------------------------------
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


# -----------------------------------------------------------------------------
def export_textract_tables(json_path: Path, outdir: Path):
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
def export_pages(pdf: Path, outdir: Path, page_start: int, page_end: int):
    doc = fitz.open(pdf)

    if page_start is None:
        page_start = 0
    if page_end is None:
        page_end = len(doc)
    page_end = min(page_end + 1, len(doc))
    assert page_start <= page_end, "page_start must be less than or equal to page_end"

    mat = fitz.Matrix(3, 3)
    for i in range(page_start, page_end):
        page = doc[i - 1]
        pix = page.get_pixmap(matrix=mat)
        pix.save(outdir / f"page-{str(page.number+1).zfill(4)}.png")


# -----------------------------------------------------------------------------
def recoverpix(doc, item):
    xref = item[0]  # xref of PDF image
    smask = item[1]  # xref of its /SMask

    # special case: /SMask or /Mask exists
    if smask > 0:
        pix0 = fitz.Pixmap(doc.extract_image(xref)["image"])
        if pix0.alpha:  # catch irregular situation
            pix0 = fitz.Pixmap(pix0, 0)  # remove alpha channel
        mask = fitz.Pixmap(doc.extract_image(smask)["image"])

        try:
            pix = fitz.Pixmap(pix0, mask)
        except:  # fallback to original base image in case of problems
            pix = fitz.Pixmap(doc.extract_image(xref)["image"])

        if pix0.n > 3:
            ext = "pam"
        else:
            ext = "png"

        return {  # create dictionary expected by caller
            "ext": ext,
            "colorspace": pix.colorspace.n,
            "image": pix.tobytes(ext),
        }

    # special case: /ColorSpace definition exists
    # to be sure, we convert these cases to RGB PNG images
    if "/ColorSpace" in doc.xref_object(xref, compressed=True):
        pix = fitz.Pixmap(doc, xref)
        pix = fitz.Pixmap(fitz.csRGB, pix)
        return {  # create dictionary expected by caller
            "ext": "png",
            "colorspace": 3,
            "image": pix.tobytes("png"),
        }
    return doc.extract_image(xref)


# -----------------------------------------------------------------------------
def save_images(file: Path, imagedir: Path):
    dimlimit = 0  # 100  # each image side must be greater than this
    relsize = 0  # 0.05  # image : image size ratio must be larger than this (5%)
    abssize = 0  # 2048  # absolute image size limit 2 KB: ignore if smaller
    # imgdir = str(imagedir)  # found images are stored in this subfolder

    doc = fitz.open(str(file))

    page_count = doc.page_count  # number of pages

    xreflist = []
    imglist = []
    for pno in range(page_count):
        il = doc.get_page_images(pno)
        imglist.extend([x[0] for x in il])
        for img in il:
            xref = img[0]
            if xref in xreflist:
                continue
            width = img[2]
            height = img[3]
            if min(width, height) <= dimlimit:
                continue
            image = recoverpix(doc, img)
            n = image["colorspace"]
            imgdata = image["image"]

            if len(imgdata) <= abssize:
                continue
            if len(imgdata) / (width * height * n) <= relsize:
                continue
            # print(f"xref: {xref}")
            imgfile = imagedir / f"{xref}.{image['ext']}"
            # imgfile = os.path.join(imgdir, "%05i.%s" % (xref, image["ext"]))
            fout = open(imgfile, "wb")
            fout.write(imgdata)
            fout.close()
            xreflist.append(xref)


# -----------------------------------------------------------------------------
@dataclass
class PaperItem:
    """Class for representing Papers"""

    source: Path
    texts: List[str]
    images: List
    refs: List[str]

    def __init__(self, source: Path):
        self.source = source

    def extract(self, basedir: str, text_only: bool):
        doc = fitz.open(self.source)

        basedir = Path(basedir)
        textdir = basedir / "text"
        if not textdir.exists():
            textdir.mkdir(parents=True)

        textfile = textdir / f"{self.source.stem}.txt"
        textfile.write_text(chr(12).join([page.get_text(sort=True) for page in doc]))

        if not text_only:
            imagedir = basedir / f"images/{self.source.stem}"
            if not imagedir.exists():
                imagedir.mkdir(parents=True)
            save_images(self.source, imagedir)
