import csv
import solara
import polars as pl
from .main import HERE, DATA_DIR, PDF_DIR, CSV_DIR, PNG_DIR


review_schema = {"file": pl.Utf8, "status": pl.Utf8, "note": pl.Utf8, "timestamp": pl.Utf8}
review_status_df = pl.read_csv(
    DATA_DIR / "review_status.csv",
    schema=review_schema,
)

status = solara.reactive("all")


@solara.component
def Page():
    def filter_status(status):
        if status.value == "all":
            df = review_status_df
        else:
            df = review_status_df.filter(pl.col("status").is_in([status.value]))
        return df.to_pandas()
        
    with solara.Card(title="", margin=0):
        with solara.CardActions():
            with solara.ToggleButtonsSingle(value=status):
                solara.Button("All", outlined=True, color="primary", icon_name="", value="all")
                solara.Button("", outlined=True, color="primary", icon_name="mdi-glasses", value="review")
                solara.Button("", outlined=True, color="primary", icon_name="mdi-thumb-up", value="accept")
                solara.Button("", outlined=True, color="primary", icon_name="mdi-thumb-down", value="reject")

        solara.Info(f"status: {status}")

    with solara.Card(title="", margin=0):
        if status:
            solara.DataFrame(filter_status(status))
