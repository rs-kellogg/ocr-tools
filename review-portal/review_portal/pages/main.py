from pathlib import Path
from typing import Optional, cast
import solara
import solara.lab
from review_portal.components.data import (
    datagrid, 
    pdf_viewer, 
    text_input,
)



HERE = Path(__file__)


@solara.component
def Page(name: Optional[str] = '1970'):
    DATA_DIR = HERE.parent/f"../public/"
    PDF_DIR = DATA_DIR/"pdf"
    CSV_DIR = DATA_DIR/"csv"
    PNG_DIR = DATA_DIR/"png"
    
    pdf_file = PDF_DIR/f"{name}.pdf"
    csv_files = list(CSV_DIR.glob("*.csv"))
    csv_files.sort()
    png_files = list(PNG_DIR.glob("*.png"))
    png_files.sort()

    with solara.Column():
        solara.Title("KRS Review App")

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
                    file, set_file = solara.use_state(cast(Optional[Path], None))
                    path, set_path = solara.use_state(cast(Optional[Path], None))
                    def reset_path():
                        set_path(None)
                        set_file(None)
                    solara.FileBrowser(
                        directory, 
                        on_directory_change=set_directory, 
                        on_path_select=set_path, 
                        on_file_open=set_file
                    )
        
        gutters = solara.reactive(True)
        gutters_dense = solara.reactive(True)
        with solara.ColumnsResponsive([1, 1], gutters=gutters.value, gutters_dense=gutters_dense.value) as main:
            csv_file = csv_files[0]
            page_num = csv_file.stem.split('-')[-2]
            
            with solara.Card(name, margin=0):
                with solara.lab.Tabs():
                    with solara.lab.Tab("PDF"):
                        pdf_viewer(f"{name}.pdf", int(page_num))
                    with solara.lab.Tab("PNG"):
                        solara.Image(f"/static/public/png/page-{page_num}.png")

            with solara.Card(title=f"Page: {page_num}"):
                datagrid(csv_file)