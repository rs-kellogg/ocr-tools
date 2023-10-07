import csv
import solara
import pandas as pd
from .main import HERE, DATA_DIR, PDF_DIR, CSV_DIR, PNG_DIR


status = solara.reactive("review")


@solara.component
def Page():
    review_status_df = pd.read_csv(DATA_DIR / "review_status.csv", index_col=0, quoting=csv.QUOTE_ALL)
    review_status_df.reset_index(inplace=True)
    df, set_df = solara.use_state(review_status_df)
    with solara.Card(title="", margin=0) as card:
        with solara.CardActions():
            with solara.ToggleButtonsSingle(value=status):
                solara.Button("", outlined=True, color="primary", icon_name="mdi-glasses", value="review")
                solara.Button("", outlined=True, color="primary", icon_name="mdi-thumb-up", value="accept")
                solara.Button("", outlined=True, color="primary", icon_name="mdi-thumb-down", value="reject")

    solara.DataFrame(df)
