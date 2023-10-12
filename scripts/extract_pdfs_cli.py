import typer
from rich import console as cons
from typing import Optional, Tuple, List
from pathlib import Path
import fitz
import re
from dataclasses import dataclass, InitVar, field
from tqdm import tqdm
import logging


# -----------------------------------------------------------------------------
app = typer.Typer()
console = cons.Console(style="green on black")


# -----------------------------------------------------------------------------
def clean_pdf(doc: fitz.Document):
    omit_pattern = re.compile(r"for peer review only", re.IGNORECASE)
    omit_pattern2 = re.compile(r"bmj open", re.IGNORECASE)
    omit_pattern3 = re.compile(r"page\s+\d+\s+of\s+\d+", re.IGNORECASE)
    omit_pattern4 = re.compile(r"^\s*\d+\s*$", re.MULTILINE)

    doc2 = fitz.Document()
    for page in doc:
        new_page = doc2.new_page(
            -1, width=page.rect.width, height=page.rect.height,
        )
        page_dict = page.get_text("dict", sort=False)
        for block in page_dict['blocks'][:-1]:
            if "lines" not in block:
                continue
            for line in block['lines']:
                for span in line['spans']:
                    bbox = span['bbox']
                    size = span['size']
                    font = span['font']
                    text = span['text']
                    match = omit_pattern.search(text)
                    if match:
                        continue
                    match = omit_pattern2.search(text)
                    if match:
                        continue
                    match = omit_pattern3.search(text)
                    if match:
                        continue
                    match = omit_pattern4.search(text)
                    if match:
                        continue
                    # print(f"writing {text} at {bbox} with {size} and {font}")
                    res = new_page.insert_textbox(
                        fitz.Rect(bbox[0], bbox[1], bbox[2], bbox[3]), 
                        text, 
                        fontsize=size, 
                        fontname="times-roman"
                    )
                    if res < 0:
                        res = new_page.insert_textbox(
                            fitz.Rect(bbox[0], bbox[1], bbox[2]-res, bbox[3]-res), 
                            text, 
                            fontsize=size, 
                            fontname="times-roman"
                        )
    return doc2

# -----------------------------------------------------------------------------
# def extract_text(page):
#     rect = fitz.Rect(
#         0.07 * page.rect.width,
#         0.07 * page.rect.height,
#         page.rect.width - 0.07 * page.rect.width,
#         page.rect.height - 0.07 * page.rect.height,
#     )
#     if page.rotation != 0:
#         rect = fitz.Rect(
#         30, 0, 
#         page.rect.height - 50, 
#         page.rect.width - 30
#     )
#     text = page.get_textbox(rect)
#     text = re.sub(
#         r'For\s+peer\s+review\s+only', '\n', text, re.IGNORECASE
#     )
#     text = re.sub(
#         r'http://bmjopen.bmj.com/site/about/guidelines.xhtml', '\n', text, re.IGNORECASE
#     )
#     return text


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
    for pno in range(1, page_count):
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
            imgfile = imagedir/f"{xref}.{image['ext']}"
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

    def extract(self, basedir: str):
        doc = clean_pdf(fitz.open(self.source))
        basedir = Path(basedir)
        pdfdir = basedir/"pdf"
        if not pdfdir.exists():
            pdfdir.mkdir(parents=True)
        pdffile = pdfdir/f"{self.source.stem}.pdf"
        doc.save(pdffile)

        textdir = basedir/"text"
        if not textdir.exists():
            textdir.mkdir(parents=True)        
        textfile = textdir/f"{self.source.stem}.txt"
        textfile.write_text(chr(12).join([page.get_text() for page in doc]))
        
        imagedir = basedir/f"images/{self.source.stem}"
        if not imagedir.exists():
            imagedir.mkdir(parents=True)
        save_images(self.source, imagedir)     


# -----------------------------------------------------------------------------
@app.command()
def clean(
    in_dir: Path = typer.Argument(..., help="Path to input PDF files"),
    out_dir: Optional[Path] = typer.Option(
        Path("."),
        "--dir",
        help="The directory where the extracted output files will be created.",
    ),
):
    if not out_dir.exists():
        out_dir.mkdir(parents=True)
    for pdf in in_dir.glob("*.pdf"):
        console.print(f"cleaning file: {pdf.name}")
        try:
            doc = clean_pdf(fitz.open(pdf))
            doc.save(out_dir/f"{pdf.stem}.pdf")
        except Exception as e:
            continue
    
# -----------------------------------------------------------------------------
@app.command()
def extract(
    in_dir: Path = typer.Argument(..., help="Path to input PDF files"),
    out_dir: Optional[Path] = typer.Option(
        Path("."),
        "--dir",
        help="The directory where the extracted output files will be created.",
    ),
):
    if not out_dir.exists():
        out_dir.mkdir(parents=True)
        
    logging.basicConfig(
        filename=f'{out_dir}/extract.log',           
        level=logging.INFO,  
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')

    logger = logging.getLogger()

    for pdf in in_dir.glob("*.pdf"):
        console.print(f"processing file: {pdf.name}")
        logger.info(pdf.name)
        try:
            paper = PaperItem(pdf)
            paper.extract(out_dir)
        except Exception as e:
            logger.error(f"exception: {type(e)}")
            continue

# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app()
