from pathlib import Path
from typing import Optional, cast
import solara
from review_portal.components.data import datagrid, pdf_viewer


HERE = Path(__file__)
DATA_DIR = HERE.parent/"../public/data/1978"


@solara.component
def Page():
    with solara.Column():
        solara.Title("KRS Review App")

        with solara.Sidebar():
            with solara.Card("Select File"):
                with solara.Column():
                    directory, set_directory = solara.use_state(DATA_DIR/"csv")
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
        
        with solara.Card():
            with solara.CardActions():
                solara.Button("Back", text=True)
                solara.Button("Next", text=True)
        
        gutters = solara.reactive(True)
        gutters_dense = solara.reactive(True)
        with solara.ColumnsResponsive([1, 1], gutters=gutters.value, gutters_dense=gutters_dense.value) as main:
            with solara.Card("1978", margin=0):
                pdf_viewer(344)
            
            # with solara.Card(title="page"):
            #     solara.Image("/static/public/page-1000.png")

            with solara.Card(title="page-343-03-left.csv"):
                df_path = f"{HERE.parent}/../public/data/1978/csv/page-343-03-left.csv"
                datagrid(df_path)