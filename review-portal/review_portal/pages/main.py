import datetime as dt
import csv, json
from pathlib import Path
import temppathlib
from typing import Optional, cast, Dict, Any
import git
import pandas as pd
import polars as pl
from ipydatagrid import Expr, DataGrid, TextRenderer
from py2vega.functions.regexp import regexp, test
import reacton
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

# ---------------------------------------------------------------------------------------------------------------------
# png files
png_files = list(PNG_DIR.glob("*.png"))
png_files.sort()

# ---------------------------------------------------------------------------------------------------------------------
# review metadata
review_schema = {"file": pl.Utf8, "status": pl.Utf8, "note": pl.Utf8, "timestamp": pl.Utf8}
review_status_df = solara.reactive(
    pl.read_csv(
        DATA_DIR / "review_status.csv",
        schema=review_schema
    )
)


def test_file_exists(df: pl.DataFrame, file_name: str):
    return file_name in df.select(pl.col("file")).to_series()


def get_row(df: pl.DataFrame, file_name: str):
    return df.row(by_predicate=pl.col("file").is_in([file_name]), named=True)


def get_field(df: pl.DataFrame, file_name: str, field: str, default: str):
    return get_row(df, file_name)[field] if test_file_exists(df, file_name) else default


def append_row(df: pl.DataFrame, file_name: str, status: str, note: str):
    if test_file_exists(df, file_name):
        df = df.filter(pl.col("file") != file_name)
    df_row = pl.DataFrame({"file": [file_name], "status": [status], "note": [note], "timestamp": [str(dt.datetime.now())]}, schema=review_schema)
    return df.extend(df_row)


# ---------------------------------------------------------------------------------------------------------------------
# reactive variables
current_file_index = solara.reactive(0)
current_file = solara.reactive(csv_files[current_file_index.value])
text = solara.reactive(get_field(review_status_df.value, current_file.value.name, "note", ""))
status = solara.reactive(get_field(review_status_df.value, current_file.value.name, "status", "review"))


# ---------------------------------------------------------------------------------------------------------------------
# functions
def load_metadata():
    text.value = get_field(review_status_df.value, current_file.value.name, "note", "")
    status.value = get_field(review_status_df.value, current_file.value.name, "status", "review")


def save_metadata():
    review_status_df.set(
        append_row(review_status_df.value, current_file.value.name, status.value, text.value)
    )
    review_status_df.value.write_csv(DATA_DIR / "review_status.csv")


def set_current_file(index: int):
    save_metadata()
    current_file_index.set(index)
    current_file.set(csv_files[current_file_index.value])
    load_metadata()


def on_restore():
    repo = git.Repo(current_file.value.parent.parent)
    repo.git.checkout([f"csv/{current_file.value.name}"])
    file_value = current_file.value
    with temppathlib.TemporaryDirectory() as tmp_dir:
        tmp_pth = tmp_dir.path / file_value.name
        tmp_pth.write_text(file_value.read_text())
        current_file.set(tmp_pth)
    current_file.set(file_value)


# ---------------------------------------------------------------------------------------------------------------------
@solara.component
def Page(name: Optional[str] = "1970"):
    solara.Title("Review Tables")

    # -----------------------------------------------------------------------------------------------------------------
    # Sidebar
    with solara.Sidebar():
        with solara.Card("Select File"):
            filter_status = solara.use_reactive("all")
            with solara.Column():
                with solara.ToggleButtonsSingle(value=filter_status):
                    solara.Button("All", outlined=True, color="primary", icon_name="", value="all")
                    solara.Button("", outlined=True, color="primary", icon_name="mdi-glasses", value="review")
                    solara.Button("", outlined=True, color="primary", icon_name="mdi-thumb-up", value="accept")
                    solara.Button("", outlined=True, color="primary", icon_name="mdi-thumb-down", value="reject")

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
            solara.Info(f"{name} - {current_file.value.name}")

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
                    png_viewer(f"{name}.pdf", current_file.value)
                with solara.lab.Tab("PDF"):
                    pdf_viewer(f"{name}.pdf", current_file.value)

        with solara.Card(margin=0) as card4:
            with solara.VBox():
                dg = datagrid(current_file)
                dg.key(f"dg1-{current_file}")   
                dataframe(current_file)

        solara.Button("Reset to initial layout", on_click=lambda: set_grid_layout(grid_layout_initial))
        solara.GridDraggable(items=[card1, card2, card3, card4], grid_layout=grid_layout, resizable=True, draggable=False, on_grid_layout=set_grid_layout)
