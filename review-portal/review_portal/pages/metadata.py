import time
import solara
import polars as pl
import ipydatagrid
from IPython.display import display
from .main import HERE, DATA_DIR, PDF_DIR, CSV_DIR, PNG_DIR


review_schema = {"file": pl.Utf8, "status": pl.Utf8, "note": pl.Utf8, "timestamp": pl.Utf8}
review_status_df = pl.read_csv(
    DATA_DIR / "review_status.csv",
    schema=review_schema,
).select(pl.col("file"), pl.col("timestamp"), pl.col("status"), pl.col("note"))

status = solara.reactive("all")

@solara.component
def DataGrid():
    def filter_status(status):
        print(f"calling filter_status: {status.value}")
        if status.value == "all":
            df = review_status_df
        else:
            df = review_status_df.filter(pl.col("status").is_in([status.value]))
        return df.to_pandas()

    grid = ipydatagrid.DataGrid(
        dataframe=filter_status(status),
        editable=False,
        layout={"height": f"1000px", "overflow_y": "auto"},
        base_row_size=30,
        base_column_size=120,
    )
    return display(grid)


@solara.component
def Page():
    with solara.Card(title="", margin=0):
        with solara.CardActions():
            with solara.ToggleButtonsSingle(value=status):
                solara.Button("All", outlined=True, color="primary", icon_name="", value="all")
                solara.Button("", outlined=True, color="primary", icon_name="mdi-glasses", value="review")
                solara.Button("", outlined=True, color="primary", icon_name="mdi-thumb-up", value="accept")
                solara.Button("", outlined=True, color="primary", icon_name="mdi-thumb-down", value="reject")

    with solara.Card(title="", margin=0):
        if status.value:
            solara.Info(f"{status.value}")
            with solara.Card():
                DataGrid()
