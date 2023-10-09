from pathlib import Path
from importlib import resources
from review_portal import components
import solara
import polars as pl
import ipydatagrid
from IPython.display import display
from .main import HERE, DATA_DIR, PDF_DIR, CSV_DIR, PNG_DIR


with resources.path(components, "colors.txt") as path:
    colors = Path(path).read_text().splitlines()
color = solara.reactive(colors[0])


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
    with solara.Columns():
        with solara.VBox():
            with solara.Row():
                solara.Button(label="", icon_name="mdi-table-row-plus-after", outlined=True, color="primary")
                solara.Button(label="", icon_name="mdi-table-row-remove", outlined=True, color="primary")
                solara.Button(label="", icon_name="save", outlined=True, color="primary")
                solara.Button(label="", icon_name="refresh", outlined=True, color="primary")
            with solara.Card():
                solara.Select(label="Color Choices", value=color, values=colors)
                solara.Markdown(f"**Selected**: {color.value}")
            with solara.Card(title="", margin=0):
                background_patterns()

       