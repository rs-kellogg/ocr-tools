import math
import fitz
import numpy as np
import PIL
from PIL import Image as im
from pathlib import Path
from scipy.ndimage import interpolation as inter
from skimage import io
from skimage.color import rgb2gray
from skimage.transform import rotate
import cv2
from typing import Union, Tuple
from deskew import determine_skew


def find_score(arr, angle):
    data = inter.rotate(arr, angle, reshape=False, order=0)
    hist = np.sum(data, axis=1)
    score = np.sum((hist[1:] - hist[:-1]) ** 2)
    return hist, score


def deskew(img: PIL.Image, delta=1, limit=5) -> im:
    # convert to binary
    wd, ht = img.size
    pix = np.array(img.convert("1").getdata(), np.uint8)
    bin_img = pix.reshape((ht, wd)) / 255.0

    # find angles
    angles = np.arange(-limit, limit + delta, delta)
    scores = []
    for angle in angles:
        hist, score = find_score(bin_img, angle)
        scores.append(score)
    best_score = max(scores)
    best_angle = angles[scores.index(best_score)]
    best_angle_text = "Best angle: {}".format(best_angle)
    print(best_angle_text)

    # correct skew
    data = inter.rotate(bin_img, best_angle, reshape=False, order=0)
    img = im.fromarray((255 * data).astype("uint8")).convert("RGB")
    return img


# -----------------------------------------------------------------------------
def export_png_pages(pdf: Path, outdir: Path, page_start: int, page_end: int):
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
