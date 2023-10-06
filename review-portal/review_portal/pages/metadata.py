import csv
import solara
import pandas as pd
from .main import HERE, DATA_DIR, PDF_DIR, CSV_DIR, PNG_DIR


@solara.component
def Page():
    with solara.VBox() as main:
        review_status_df = pd.read_csv(DATA_DIR / "review_status.csv", index_col=0, quoting=csv.QUOTE_ALL)
        review_status_df.reset_index(inplace=True)
        df, set_df = solara.use_state(review_status_df)
        with solara.Card(title="Metadata", margin=0) as card:
            with solara.HBox():
                solara.Button("", outlined=True, color="primary", icon_name="save")
                solara.Button("", outlined=True, color="primary", icon_name="refresh")

            solara.DataFrame(df)
