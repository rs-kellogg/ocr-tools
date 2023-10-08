import time
import solara
import polars as pl
import ipydatagrid
from IPython.display import display
from .main import HERE, DATA_DIR, PDF_DIR, CSV_DIR, PNG_DIR


@solara.component
def background_patterns():
    df = pl.read_csv(
        DATA_DIR / "background.csv",
        schema={"pattern": pl.Utf8, "color": pl.Utf8},
    ).to_pandas()

    grid = ipydatagrid.DataGrid(
        dataframe=df,
        editable=True,
        layout={"height": f"1000px", "overflow_y": "auto"},
        base_row_size=30,
        base_column_size=120,
    )
    return display(grid)


@solara.component
def Page():
    with solara.Card(title="", margin=0):
        background_patterns()
