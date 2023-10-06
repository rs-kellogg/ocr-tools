import csv
import solara
import pandas as pd
from .main import HERE, DATA_DIR, PDF_DIR, CSV_DIR, PNG_DIR


@solara.component
def Page():
    with solara.VBox() as main:
        solara.Button("Hello", color="primary")
