from pathlib import Path
from typing import Optional, cast, Dict, Any, Callable
import pandas as pd
import solara
import solara.lab
from solara.alias import rv
from IPython.display import IFrame, Image, FileLink, HTML, display
from py2vega.functions.regexp import regexp, test
from ipydatagrid import Expr, DataGrid, TextRenderer, BarRenderer, VegaExpr


def background_color(cell):
    if test(r"^[A-Z].*", cell.value):
        return "lightgreen"
    elif test(r"\$", cell.value):
        return "pink"
    elif test(r".{40,}", cell.value):
        return "pink"
    else:
        return "white"


def cell_observer_factory(grid, file, load_file):
    def cell_changed(e):
        grid.data.iat[e['row'], e['column_index']] = e['value']
        grid.data.to_csv(file, index=True)
        load_file.value = True
    return cell_changed   


@solara.component
def datagrid(file: Path, load_file):
    renderer = TextRenderer(
        text_wrap=True, text_color="black", background_color=Expr(background_color),
    )
    df = pd.read_csv(file, index_col=0)
    grid = DataGrid(
        dataframe=df,
        editable=True,
        layout={"height": f"1000px", "overflow_y": "auto"},
        base_row_size=30,
        base_column_size=120,
        default_renderer=renderer,
    )
    grid.on_cell_change(cell_observer_factory(grid, file, load_file))
    display(grid)


@solara.component
def dataframe(file: Path, load_file):
    df = pd.read_csv(file, index_col=0)

    column, set_column = solara.use_state(cast(Optional[str], None))
    cell, set_cell = solara.use_state(cast(Dict[str, Any], {}))

    def insert_left_column(column):
        set_column(column)
        idx = df.columns.get_loc(column)
        df.insert(idx, "new", [""] * len(df), allow_duplicates=True)
        df.to_csv(file, index=True)
        load_file.value = True

    def insert_right_column(column):
        set_column(column)
        idx = df.columns.get_loc(column)
        df.insert(idx + 1, "new", [""] * len(df), allow_duplicates=True)
        df.to_csv(file, index=True)
        load_file.value = True

    def delete_column(column):
        set_column(column)
        idx = df.columns.get_loc(column)
        df.drop(columns=[column], inplace=True)
        df.to_csv(file, index=True)
        load_file.value = True

    def insert_before_row(column, row_index):
        set_cell(dict(column=column, row_index=row_index))
        parts = []
        if row_index > 0:
            parts.append(df.iloc[: row_index - 1])
        parts.append(pd.DataFrame(
            columns=df.columns,
            index=[df.index[-1] + 1],
        ))
        parts.append(df.iloc[row_index:])
        df2 = pd.concat(parts).reset_index(drop=True)
        df2.to_csv(file, index=True)
        load_file.value = True

    def insert_after_row(column, row_index):
        set_cell(dict(column=column, row_index=row_index))
        iloc1 = df.iloc[: row_index + 1]
        iloc2 = df.iloc[row_index + 1 :]
        additional_row = pd.DataFrame(
            columns=df.columns,
            index=[df.index[-1] + 1],
        )
        df2 = pd.concat([iloc1, additional_row, iloc2]).reset_index(drop=True)
        df2.to_csv(file, index=True)
        load_file.value = True

    def delete_row(column, row_index):
        set_cell(dict(column=column, row_index=row_index))
        df2 = df.drop(index=[row_index])
        df2.to_csv(file, index=True)
        load_file.value = True

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
