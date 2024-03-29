import csv
from pathlib import Path
from importlib import resources
from review_portal import components
import solara
import polars as pl
import ipydatagrid
from IPython.display import display
from .main import HERE, DATA_DIR, PDF_DIR, CSV_DIR, PNG_DIR


load_file = solara.reactive(False)

# ---------------------------------------------------------------------------------------------------------------------
# colors
with resources.path(components, "colors.txt") as path:
    colors = Path(path).read_text().splitlines()
    colors.sort()
color = solara.reactive(colors[0])


# ---------------------------------------------------------------------------------------------------------------------
# components
@solara.component
def background_patterns():
    schema = {"pattern": pl.Utf8, "color": pl.Utf8}
    patterns_df = pl.read_csv(
        DATA_DIR / "background.csv",
        schema=schema,
    )

    def cell_observer_factory(grid, file, load_file):
        def cell_changed(e):
            grid.data.iat[e["row"], e["column_index"]] = e["value"]
            grid.data.to_csv(file, index=False, quoting=csv.QUOTE_ALL)
            load_file.value = True

        return cell_changed

    grid = ipydatagrid.DataGrid(
        dataframe=patterns_df.to_pandas(),
        editable=True,
        layout={"height": f"1000px", "overflow_y": "auto"},
        base_row_size=30,
        base_column_size=180,
    )
    grid.on_cell_change(cell_observer_factory(grid, file=DATA_DIR / "background.csv", load_file=load_file))
    return display(grid)


@solara.component
def Page():
    with solara.Columns():
        with solara.VBox():
            with solara.Card():
                # with solara.CardActions():
                #     solara.Button(label="", icon_name="mdi-table-row-plus-after", outlined=True, color="primary")
                #     solara.Button(label="", icon_name="mdi-table-row-remove", outlined=True, color="primary")
                #     solara.Button(label="", icon_name="refresh", outlined=True, color="primary")
                solara.Select(label="Color Choices", value=color, values=colors)
                solara.Markdown(f"**Selected**: {color.value}")
            with solara.Card(title="", margin=0):
                if load_file.value:
                    solara.Info(f"loading patterns file")
                    load_file.value = False
                else:
                    background_patterns()
