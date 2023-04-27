import numpy as np
import PIL
from PIL import Image as im
from pathlib import Path
from scipy.ndimage import interpolation as inter


def find_score(arr, angle):
    data = inter.rotate(arr, angle, reshape=False, order=0)
    hist = np.sum(data, axis=1)
    score = np.sum((hist[1:] - hist[:-1]) ** 2)
    return hist, score


def deskew(img: PIL.Image, delta=1, limit=5) -> im:
    # convert to binary
    wd, ht = img.size
    pix = np.array(img.convert('1').getdata(), np.uint8)
    bin_img = (pix.reshape((ht, wd)) / 255.0)

    # find angles
    angles = np.arange(-limit, limit+delta, delta)
    scores = []
    for angle in angles:
        hist, score = find_score(bin_img, angle)
        scores.append(score)
    best_score = max(scores)
    best_angle = angles[scores.index(best_score)]
    best_angle_text = 'Best angle: {}'.format(best_angle)
    print(best_angle_text)

    # correct skew
    data = inter.rotate(bin_img, best_angle, reshape=False, order=0)
    img = im.fromarray((255 * data).astype("uint8")).convert("RGB")

    return img
