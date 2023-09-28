from pathlib import Path
from typing import Optional, cast
import pandas as pd
from ipydatagrid import DataGrid
import solara
import solara.lab
from solara.alias import rv
from review_portal.components.data import (
    datagrid, 
    pdf_viewer, 
    png_viewer,
    text_input,
    ColorCard,
)


HERE = Path(__file__)
DATA_DIR = HERE.parent/f"../public/"
PDF_DIR = DATA_DIR/"pdf"
CSV_DIR = DATA_DIR/"csv"
PNG_DIR = DATA_DIR/"png"


@solara.component
def Page(name: Optional[str] = '1970'):
    pdf_file = PDF_DIR/f"{name}.pdf"
    csv_files = list(CSV_DIR.glob("*.csv"))
    csv_files.sort()
    png_files = list(PNG_DIR.glob("*.png"))
    png_files.sort()

    with solara.Column():
        solara.Title("KRS Review App")

        # -------------------------------------------------------------------------------------------------------------
        # Sidebar
        with solara.Sidebar():
            with solara.Card():
                with solara.CardActions():
                    solara.Button("", outlined=True, color="primary", icon_name="mdi-arrow-left-bold-box")
                    solara.Button("", outlined=True, color="primary", icon_name="mdi-arrow-right-bold-box")
                    solara.Button("", outlined=True, color="primary", icon_name="save")
                    solara.Button("", outlined=True, color="primary", icon_name="refresh")
                    solara.Button("", outlined=True, color="primary", icon_name="mdi-thumb-up")
                    solara.Button("", outlined=True, color="primary", icon_name="mdi-thumb-down")

            with solara.Card(title="Notes"):
                text_input()

            with solara.Card("Select File"):
                with solara.Column():
                    directory, set_directory = solara.use_state(CSV_DIR)
                    file, set_file = solara.use_state(csv_files[0])
                    path, set_path = solara.use_state(csv_files[0].parent)
                    load_file, set_load_file = solara.use_state(False)
                    
                    def my_set_file(file):
                        print(f"setting file: {file}")
                        set_file(file)
                        set_load_file(True)

                    def reset_path():
                        set_path(None)
                        set_file(None)

                    solara.FileBrowser(
                        directory, 
                        on_directory_change=set_directory, 
                        on_path_select=set_path, 
                        on_file_open=my_set_file,
                    )
                    

        # -------------------------------------------------------------------------------------------------------------
        # Main content
        grid_layout_initial = [
            {"h": 2, "i": "0", "moved": False, "w": 6, "x": 0, "y": 0},
            {"h": 5, "i": "1", "moved": False, "w": 6, "x": 6, "y": 0},
            {"h": 1, "i": "2", "moved": False, "w": 6, "x": 0, "y": 2},
            {"h": 1, "i": "3", "moved": False, "w": 6, "x": 6, "y": 5},
        ]
        grid_layout, set_grid_layout = solara.use_state(grid_layout_initial)
        with solara.VBox() as main:
            def reset_layout():
                set_grid_layout(grid_layout_initial)

            with solara.Card(margin=0) as card1:
                solara.Info(f"{name}")

            with solara.Card(margin=0) as card2:
                if file:
                    solara.Info(f"{file.name}")
                else:
                    solara.Info("No file selected")
            with solara.Card(margin=0) as card3:
                 with solara.lab.Tabs():
                    with solara.lab.Tab("PNG"):
                        png_viewer(f"{name}.pdf", file)
                    with solara.lab.Tab("PDF"):
                        pdf_viewer(f"{name}.pdf", file)

            with solara.Card(margin=0) as card4:
                with solara.VBox():
                    if file and load_file:
                        solara.Info(f"load_file: {load_file}")
                        set_load_file(False)
                    else:
                        datagrid(file)
                        # set_load_file(False)
                        # solara.Info(f"load_file: {load_file}")

            solara.Button("Reset to initial layout", on_click=reset_layout)
            solara.GridDraggable(
                items=[card1, card2, card3, card4], 
                grid_layout=grid_layout, 
                resizable=True, 
                draggable=False, 
                on_grid_layout=set_grid_layout
            )
