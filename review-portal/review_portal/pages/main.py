import time
import csv, json
from pathlib import Path
from typing import Optional, cast, Dict, Any
import git
import pandas as pd
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
    ColorCard,
)


HERE = Path(__file__)
DATA_DIR = HERE.parent / f"../public/"
PDF_DIR = DATA_DIR / "pdf"
CSV_DIR = DATA_DIR / "csv"
PNG_DIR = DATA_DIR / "png"

csv_files = list(CSV_DIR.glob("*.csv"))
csv_files.sort()
png_files = list(PNG_DIR.glob("*.png"))
png_files.sort()

current_file_index = solara.reactive(0)
current_file = csv_files[0]
load_file = solara.reactive(True)
text = solara.reactive("")
status = solara.reactive("review")

if not (DATA_DIR / "review_status.csv").exists():
    review_status_df = pd.DataFrame(
        [[status.value, text.value, time.time()]],
        columns=["status", "note", "timestamp"],
        index=[current_file.name],
    )
    review_status_df.to_csv(DATA_DIR / "review_status.csv", index=True, quoting=csv.QUOTE_ALL)
else:
    review_status_df = pd.read_csv(DATA_DIR / "review_status.csv", index_col=0, quoting=csv.QUOTE_ALL)


@solara.component
def Page(name: Optional[str] = "1970"):
    pdf_file = PDF_DIR / f"{name}.pdf"

    def load_metadata():
        global review_status_df
        if current_file.name not in review_status_df.index:
            status.value = "review"
            text.value = ""
            row_df = pd.DataFrame(
                [[status.value, text.value, time.time()]], 
                columns=["status", "note", "timestamp"], 
                index=[current_file.name]
            )
            review_status_df = pd.concat([review_status_df, row_df])
        else:
            status.value = review_status_df.loc[current_file.name]['status']
            text.value = review_status_df.loc[current_file.name]['note']

    def save_metadata():
        global review_status_df
        if current_file.name not in review_status_df.index:
            row_df = pd.DataFrame(
                [[status.value, text.value, time.time()]], 
                columns=["status", "note", "timestamp"], 
                index=[current_file.name]
            )
            review_status_df = pd.concat([review_status_df, row_df])
        else:
            review_status_df.at[current_file.name, 'status'] = status.value
            review_status_df.at[current_file.name, 'note'] = text.value
            review_status_df.at[current_file.name, 'timestamp'] = time.time()
        
        review_status_df.to_csv(DATA_DIR / "review_status.csv", index=True, quoting=csv.QUOTE_ALL)

    def set_current_file(index: int):
        global current_file
        print(f"file_index: {current_file_index.value}, file name: {current_file.name}")
        save_metadata()
        current_file_index.value = index
        current_file = csv_files[current_file_index.value]
        load_metadata()
        load_file.value = True

        # file = csv_files[current_file_index.value]
        # try:
        #     review_status_df.loc[file.name]['status'] = 'complete'
        #     review_status_df.loc[file.name]['note'] = text.value
        #     review_status_df.to_csv(DATA_DIR / "review_status.csv", index=True, quoting=csv.QUOTE_ALL)
        # except KeyError:
        #     review_status_df.loc[file.name] = ["review", "", time.time()]
        #     review_status_df.to_csv(DATA_DIR / "review_status.csv", index=True, quoting=csv.QUOTE_ALL)
        # set_file(file)
        # set_load_file(True)

    def on_left_click():
        set_current_file(max(current_file_index.value - 1, 0))

    def on_right_click():
        set_current_file(min(current_file_index.value + 1, len(csv_files) - 1))

    with solara.Column():
        solara.Title("Table Review App")

        # -------------------------------------------------------------------------------------------------------------
        # Sidebar
        with solara.Sidebar():
            with solara.Card("Select File"):
                with solara.Column():
                    solara.Info(f"file_index: {current_file_index.value}, file name: {current_file.name}")
                    # directory, set_directory = solara.use_state(CSV_DIR)
                    # file, set_file = solara.use_state(csv_files[0])
                    # path, set_path = solara.use_state(csv_files[0].parent)
                    # load_file, set_load_file = solara.use_state(False)

                    # def my_set_file(file):
                    #     set_file(file)
                    #     set_load_file(True)

                    # def reset_path():
                    #     # set_path(None)
                    #     set_file(None)

                    # solara.FileBrowser(
                    #     directory,
                    #     on_directory_change=set_directory,
                    #     on_path_select=set_path,
                    #     on_file_open=my_set_file,
                    # )

        # -------------------------------------------------------------------------------------------------------------
        # Main content
        grid_layout_initial = [
            {"h": 2, "i": "0", "moved": False, "w": 6, "x": 0, "y": 0},
            {"h": 5, "i": "1", "moved": False, "w": 6, "x": 6, "y": 0},
            {"h": 1, "i": "2", "moved": False, "w": 6, "x": 0, "y": 2},
            {"h": 1, "i": "3", "moved": False, "w": 6, "x": 6, "y": 5},
        ]
        grid_layout, set_grid_layout = solara.use_state(grid_layout_initial)

        def on_restore():
            repo = git.Repo(current_file.parent.parent)
            repo.git.checkout([f"csv/{current_file.name}"])
            load_file.value = True

        with solara.VBox() as main:
            with solara.Card(margin=0) as card1:
                solara.Info(f"{pdf_file.name} - {current_file.name}")

            with solara.Card(title="", margin=0) as card2:
                with solara.CardActions():
                        with solara.ToggleButtonsSingle(value=status):
                            solara.Button("", outlined=True, color="primary", icon_name="mdi-glasses", value="review")
                            solara.Button("", outlined=True, color="primary", icon_name="mdi-thumb-up", value="accept")
                            solara.Button("", outlined=True, color="primary", icon_name="mdi-thumb-down", value="reject")
                        
                        solara.Button("", outlined=True, color="primary", icon_name="mdi-arrow-left-bold-box", on_click=on_left_click)
                        solara.Button("", outlined=True, color="primary", icon_name="mdi-arrow-right-bold-box", on_click=on_right_click)
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
