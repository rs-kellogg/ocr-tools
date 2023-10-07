import csv
import solara
import pandas as pd
from .main import HERE, DATA_DIR, PDF_DIR, CSV_DIR, PNG_DIR

csv_files = list(CSV_DIR.glob("*.csv"))
csv_files.sort()

current_file_index = solara.reactive(0)


@solara.component
def Page():
    def on_click():
        if current_file_index.value is None:
            current_file_index.value = 0
        current_file_index.value += 1

    solara.Button(f"Index {current_file_index.value}", color="primary", on_click=on_click)
    solara.Info(f"File name: {csv_files[current_file_index.value].name}")
