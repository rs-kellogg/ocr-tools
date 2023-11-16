from pathlib import Path
import temppathlib
from typing import Optional, cast, Dict, Any, Callable
import pandas as pd
import polars as pl
import solara
import solara.lab
from solara.alias import rv
from IPython.display import IFrame, Image, FileLink, HTML, display
from py2vega.functions.regexp import regexp, test
from ipydatagrid import Expr, DataGrid, TextRenderer, BarRenderer, VegaExpr

HERE = Path(__file__)
DATA_DIR = HERE.parent / f"../public/"


def write_file(df, file: solara.Reactive):
    df.to_csv(file.value, index=True)
    file_value = file.value
    with temppathlib.TemporaryDirectory() as tmp_dir:
        tmp_pth = tmp_dir.path / file_value.name
        df.to_csv(tmp_pth, index=True)
        file.set(tmp_pth)
    file.set(file_value)


def background_color_factory():
    background_df = pl.read_csv(
        DATA_DIR / "background.csv",
        schema={"pattern": pl.Utf8, "color": pl.Utf8},
    )
    value = ""
    num_cases = 0
    for row in background_df.rows(named=True):
        if row["pattern"] != "" and row["color"] != "":
            value += f"if(test('{row['pattern']}', cell.value), '{row['color']}',\n"
            num_cases += 1
        elif row["pattern"] == "" and row["color"] != "":
            value += f"{row['color']}{')'*(num_cases)}"
            break
    return VegaExpr(value=value)


def cell_observer_factory(grid, file: solara.Reactive):
    def cell_changed(e):
        row, column, col_index, value = e["row"], e["column"], e["column_index"], e["value"]
        df = grid.data.copy()
        df.iat[row, col_index] = value
        write_file(df, file)

    return cell_changed


@solara.component
def datagrid(file: solara.Reactive):
    renderer = TextRenderer(
        text_wrap=True,
        text_color="black",
        background_color=background_color_factory(),
    )
    df = pd.read_csv(file.value, index_col=0)
    grid = DataGrid(
        dataframe=df,
        editable=True,
        layout={"height": f"1000px", "overflow_y": "auto"},
        base_row_size=30,
        base_column_size=200,
        default_renderer=renderer,
    )
    grid.on_cell_change(cell_observer_factory(grid, file))
    display(grid)


@solara.component
def dataframe(file: solara.Reactive):
    df = pd.read_csv(file.value, index_col=0)

    column, set_column = solara.use_state(cast(Optional[str], None))
    cell, set_cell = solara.use_state(cast(Dict[str, Any], {}))

    def insert_left_column(column):
        set_column(column)
        idx = df.columns.get_loc(column)
        df.insert(idx, "new", [""] * len(df), allow_duplicates=True)
        write_file(df, file)

    def insert_right_column(column):
        set_column(column)
        idx = df.columns.get_loc(column)
        df.insert(idx + 1, "new", [""] * len(df), allow_duplicates=True)
        write_file(df, file)

    def delete_column(column):
        set_column(column)
        idx = df.columns.get_loc(column)
        df.drop(columns=[column], inplace=True)
        write_file(df, file)

    def insert_before_row(column, row_index):
        set_cell(dict(column=column, row_index=row_index))
        parts = []
        if row_index > 0:
            parts.append(df.iloc[: row_index - 1])
        parts.append(
            pd.DataFrame(
                columns=df.columns,
                index=[df.index[-1] + 1],
            )
        )
        parts.append(df.iloc[row_index:])
        df2 = pd.concat(parts).reset_index(drop=True)
        write_file(df2, file)

    def insert_after_row(column, row_index):
        set_cell(dict(column=column, row_index=row_index))
        iloc1 = df.iloc[: row_index + 1]
        iloc2 = df.iloc[row_index + 1 :]
        additional_row = pd.DataFrame(
            columns=df.columns,
            index=[df.index[-1] + 1],
        )
        df2 = pd.concat([iloc1, additional_row, iloc2]).reset_index(drop=True)
        write_file(df2, file)

    def delete_row(column, row_index):
        set_cell(dict(column=column, row_index=row_index))
        df2 = df.drop(index=[row_index])
        write_file(df2, file)

    column_actions = [
        solara.ColumnAction(icon="mdi-table-column-plus-before", name="", on_click=insert_left_column),
        solara.ColumnAction(icon="mdi-table-column-plus-after", name="", on_click=insert_right_column),
        solara.ColumnAction(icon="mdi-table-column-remove", name="", on_click=delete_column),
    ]
    cell_actions = [
        solara.CellAction(icon="mdi-table-row-plus-before", name="", on_click=insert_before_row),
        solara.CellAction(icon="mdi-table-row-plus-after", name="", on_click=insert_after_row),
        solara.CellAction(icon="mdi-table-row-remove", name="", on_click=delete_row),
    ]
    solara.DataFrame(df, column_actions=column_actions, cell_actions=cell_actions)


@solara.component
def pdf_viewer(name: str, file: Path):
    page_number = int(file.name.split("-")[-2])
    html = f"""
    <iframe
        title="Source Document"
        width="100%"
        height="1000"
        src="static/public/pdf/{name}#page={page_number}"
        scrolling="yes"
    ></iframe>"
    """
    solara.display(HTML(html))


@solara.component
def png_viewer(name: str, file: Path):
    page_number = file.name.split("-")[-2]
    solara.Image(f"/static/public/png/page-{page_number}.png")


@solara.component
def ColorCard(title, color):
    with rv.Card(style_=f"background-color: {color}; width: 100%; height: 100%") as main:
        rv.CardTitle(children=[title])
    return main
