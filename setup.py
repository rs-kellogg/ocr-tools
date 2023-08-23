#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

requirements = [
    "typer[all]",
    "typer-cli",
    "rich",
    "pyyaml",
    "scipy",
    "pandas",
    "scikit-learn",
    "scikit-image",
    "PyMuPDF",
    "pdf2image",
    "pdfplumber",
    "Pillow",
    "opencv-python",
    "pdf2image",
    "pytesseract",
    "deskew",
    "boto3",
    "amazon-textract-textractor",
    "amazon-textract-helper",
    "amazon-textract-caller",
    "amazon-textract-geofinder",
    "amazon-textract-response-parser",
    "amazon-textract-prettyprinter",
    "sentence-transformers",
    "solara",
]


test_requirements = [
    "pytest>=3",
]

setup(
    author="Kellogg Research Support",
    author_email="rs@kellogg.northwestern.edu",
    description="OCR tools",
    entry_points={
        "console_scripts": [
            "ocrtools=ocrtools.cli:app",
        ],
    },
    install_requires=requirements,
    include_package_data=True,
    name="ocrtools",
    packages=find_packages(
        include=["ocrtools", "ocrtools.*"]
    ),
    package_data={"ocrtools": ["data/*"]},
    test_suite="tests",
    tests_require=test_requirements,
    version="0.1.0",
)
