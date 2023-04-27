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
    "numpy",
    "Pillow",
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
    keywords="wrangler",
    name="wrangler",
    packages=find_packages(
        include=["ocrtools", "ocrtools.*"]
    ),
    package_data={"ocrtools": ["data/*"]},
    test_suite="tests",
    tests_require=test_requirements,
    version="0.1.0",
)
