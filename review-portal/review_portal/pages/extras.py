import solara
import pandas as pd
from .main import HERE, DATA_DIR, PDF_DIR, CSV_DIR, PNG_DIR


review_status_df = pd.read_csv(DATA_DIR / "review_status.csv")


@solara.component
def Page():
    with solara.VBox() as main:
        with solara.Card(title="Test", margin=0) as card:
            solara.Info(f"{review_status_df}")
