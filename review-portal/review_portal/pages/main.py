import datetime as dt
import csv, json
from pathlib import Path
from typing import Optional, cast, Dict, Any
import git
import pandas as pd
import polars as pl
from ipydatagrid import Expr, DataGrid, TextRenderer
from py2vega.functions.regexp import regexp, test
import solara
import solara.lab
from solara.alias import rv
from IPython.display import display
from review_portal.components.data import (
    datagrid,
    dataframe,
    pdf_viewer,
    png_viewer,
)

# ---------------------------------------------------------------------------------------------------------------------
# data paths
HERE = Path(__file__)
DATA_DIR = HERE.parent / f"../public/"
PDF_DIR = DATA_DIR / "pdf"
CSV_DIR = DATA_DIR / "csv"
PNG_DIR = DATA_DIR / "png"

# ---------------------------------------------------------------------------------------------------------------------
# csv files
csv_files = list(CSV_DIR.glob("*.csv"))
csv_files.sort()
current_file = csv_files[0]

# ---------------------------------------------------------------------------------------------------------------------
# png files
png_files = list(PNG_DIR.glob("*.png"))
png_files.sort()

# ---------------------------------------------------------------------------------------------------------------------
# review metadata
review_schema = {
        "file": pl.Utf8, "status": pl.Utf8, "note": pl.Utf8, "timestamp":pl.Utf8
}

review_status_df = pl.read_csv(
    DATA_DIR / "review_status.csv",
    schema=review_schema,
)

def test_file_exists(df, file_name):
    return file_name in df.select(pl.col("file")).to_series()

def get_row(df, file_name):
    return df.row(by_predicate=pl.col("file").is_in([file_name]), named=True)

def get_field(df, file_name, field, default):
    if test_file_exists(df, file_name):
        row = get_row(df, file_name)
        return row[field]
    return default

def append_row(df, file_name, status, note):
    if test_file_exists(df, file_name):
        df = df.filter(pl.col("file") != file_name)
    df_row = pl.DataFrame(
        {
            "file": [file_name],
            "status": [status],
            "note": [note],
            "timestamp": [str(dt.datetime.now())]
        },
        schema=review_schema
    )
    return df.extend(df_row)


# ---------------------------------------------------------------------------------------------------------------------
# reactive variables
current_file_index = solara.reactive(0)
load_file = solara.reactive(True)
text = solara.reactive(get_field(review_status_df, current_file.name, "note", ""))
status = solara.reactive(get_field(review_status_df, current_file.name, "status", "review"))


# ---------------------------------------------------------------------------------------------------------------------
# functions
def load_metadata():
    global review_status_df
    text.value = get_field(review_status_df, current_file.name, "note", "")
    status.value = get_field(review_status_df, current_file.name, "status", "review")


def save_metadata():
    global review_status_df
    review_status_df = append_row(review_status_df, current_file.name, status.value, text.value)
    review_status_df.write_csv(DATA_DIR / "review_status.csv")


def set_current_file(index: int):
    global current_file
    save_metadata()
    current_file_index.value = index
    current_file = csv_files[current_file_index.value]
    load_metadata()
    load_file.value = True


def on_restore():
    repo = git.Repo(current_file.parent.parent)
    repo.git.checkout([f"csv/{current_file.name}"])
    load_file.value = True


# ---------------------------------------------------------------------------------------------------------------------
@solara.component
def Page(name: Optional[str] = "1970"):
    solara.Title("Review Tables")

    # -----------------------------------------------------------------------------------------------------------------
    # Sidebar
    with solara.Sidebar():
        with solara.Card("Select File"):
            with solara.Column():
                solara.Info(f"file_index: {current_file_index.value}, file name: {current_file.name}")

                def set_file(file):
                    current_file_index.value = csv_files.index(file)
                    set_current_file(current_file_index.value)

                solara.FileBrowser(
                    CSV_DIR,
                    on_file_open=set_file,
                )

    # -----------------------------------------------------------------------------------------------------------------
    # Main content
    grid_layout_initial = [
        {"h": 2, "i": "0", "moved": False, "w": 6, "x": 0, "y": 0},
        {"h": 5, "i": "1", "moved": False, "w": 6, "x": 6, "y": 0},
        {"h": 1, "i": "2", "moved": False, "w": 6, "x": 0, "y": 2},
        {"h": 1, "i": "3", "moved": False, "w": 6, "x": 6, "y": 5},
    ]
    grid_layout, set_grid_layout = solara.use_state(grid_layout_initial)

    with solara.VBox() as main:
        with solara.Card(margin=0) as card1:
            solara.Info(f"{name} - {current_file.name}")

        with solara.Card(title="", margin=0) as card2:
            with solara.CardActions():
                with solara.ToggleButtonsSingle(value=status):
                    solara.Button("", outlined=True, color="primary", icon_name="mdi-glasses", value="review")
                    solara.Button("", outlined=True, color="primary", icon_name="mdi-thumb-up", value="accept")
                    solara.Button("", outlined=True, color="primary", icon_name="mdi-thumb-down", value="reject")

                solara.Button(
                    "",
                    outlined=True,
                    color="primary",
                    icon_name="mdi-arrow-left-bold-box",
                    on_click=lambda: set_current_file(max(current_file_index.value - 1, 0)),
                )
                solara.Button(
                    "",
                    outlined=True,
                    color="primary",
                    icon_name="mdi-arrow-right-bold-box",
                    on_click=lambda: set_current_file(min(current_file_index.value + 1, len(csv_files) - 1)),
                )
                solara.Button("", outlined=True, color="primary", icon_name="save", on_click=save_metadata)
                solara.Button("", outlined=True, color="primary", icon_name="refresh", on_click=on_restore)
                solara.Button("Clear Notes", on_click=lambda: text.set(""))
            solara.InputText("Notes", value=text, continuous_update=True)

        with solara.Card(margin=0) as card3:
            with solara.lab.Tabs():
                with solara.lab.Tab("PNG"):
                    png_viewer(f"{name}.pdf", current_file)
                with solara.lab.Tab("PDF"):
                    pdf_viewer(f"{name}.pdf", current_file)

        with solara.Card(margin=0) as card4:
            if current_file and load_file.value:
                solara.Info(f"loading file: {current_file}")
                load_file.value = False
            else:
                with solara.lab.Tabs():
                    with solara.lab.Tab("Edit Cells"):
                        datagrid(current_file, load_file)
                    with solara.lab.Tab("Add/Remove"):
                        dataframe(current_file, load_file)

        solara.Button("Reset to initial layout", on_click=lambda: set_grid_layout(grid_layout_initial))
        solara.GridDraggable(items=[card1, card2, card3, card4], grid_layout=grid_layout, resizable=True, draggable=False, on_grid_layout=set_grid_layout)
