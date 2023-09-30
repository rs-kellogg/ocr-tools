from IPython.display import IFrame, Image, FileLink, HTML
from pathlib import Path
from typing import Optional, cast, Dict, Any, Callable
import reacton.bqplot as bqp
import solara
import solara.lab
from solara.alias import rv
import solara.website
import ipywidgets as w
from ipydatagrid import TextRenderer, DataGrid
import pandas as pd
from py2vega.functions.regexp import regexp, test
from ipydatagrid import Expr, DataGrid, TextRenderer, BarRenderer, VegaExpr


def cell_observer_factory(grid):
    def cell_changed(e):
        if e["row"] == (len(grid.data) - 1) and e["column"] == "amount":
            return
        amounts = grid.data["amount"]
        summed_amount = amounts[1:-2].sum()
        given_total = amounts[-2:-1].sum()
        diff = given_total - summed_amount
        grid.set_cell_value("amount", len(grid.data) - 1, diff)

    return cell_changed


def background_color(cell):
    if test(r"^[A-Z].*", cell.value):
        return "lightgreen"
    elif test(r"\$", cell.value):
        return "pink"
    elif test(r".{40,}", cell.value):
        return "pink"
    else:
        return "pink"


@solara.component
def datagrid(file: Path):        
    df = pd.read_csv(file)
    # if "Unnamed: 0" in df.columns:
    #     df = df.drop(columns=["Unnamed: 0"])
    grid = DataGrid.element(
        dataframe=df,
        editable=True,
        layout={"height": f"1000px", "overflow_y": "auto"},
        base_row_size=30,
        base_column_size=120,
    )

@solara.component
def dataframe(file: Path, set_load_file: Callable):    
    df = pd.read_csv(file)

    column, set_column = solara.use_state(cast(Optional[str], None))
    cell, set_cell = solara.use_state(cast(Dict[str, Any], {}))

    def insert_left_column(column):
        set_column(column)
        idx = df.columns.get_loc(column)
        df.insert(idx, "new", [""]*len(df), allow_duplicates=True)
        df.to_csv(file, index=False)
        set_load_file(True)

    def insert_right_column(column):
        set_column(column)
        idx = df.columns.get_loc(column)
        df.insert(idx+1, "new", [""]*len(df), allow_duplicates=True)
        df.to_csv(file, index=False)
        set_load_file(True)

    def delete_column(column):
        set_column(column)
        idx = df.columns.get_loc(column)
        df.drop(columns=[column], inplace=True)
        df.to_csv(file, index=False)
        set_load_file(True)

    def insert_before_row(column, row_index):
        set_cell(dict(column=column, row_index=row_index))
        columns = df.columns
        index = df.index
        iloc1 = df.iloc[:row_index-1]
        iloc2 = df.iloc[row_index:]
        additional_row = pd.DataFrame(
            columns = columns, 
            index = [index[-1] + 1],
        )
        df2 = pd.concat([
            iloc1, 
            additional_row, 
            iloc2
        ]).reset_index(drop=True)
        df2.to_csv(file, index=False)
        set_load_file(True)
        
    def insert_after_row(column, row_index):
        set_cell(dict(column=column, row_index=row_index))
        columns = df.columns
        index = df.index
        iloc1 = df.iloc[:row_index+1]
        iloc2 = df.iloc[row_index+1:]
        additional_row = pd.DataFrame(
            columns = columns, 
            index = [index[-1] + 1],
        )
        df2 = pd.concat([
            iloc1, 
            additional_row, 
            iloc2
        ]).reset_index(drop=True)
        df2.to_csv(file, index=False)
        set_load_file(True)
                            
    def delete_row(column, row_index):
        set_cell(dict(column=column, row_index=row_index))
        df2 = df.drop(index=[row_index])
        df2.to_csv(file, index=False)
        set_load_file(True)

    column_actions = [
        solara.ColumnAction(icon="mdi-table-column-plus-before", name="", on_click=insert_left_column),
        solara.ColumnAction(icon="mdi-table-column-plus-after", name="", on_click=insert_right_column),
        solara.ColumnAction(icon="mdi-table-column-remove", name="", on_click=delete_column)
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


text = solara.reactive("")
continuous_update = solara.reactive(True)


@solara.component
def text_input():
    solara.InputText("Enter some text", value=text, continuous_update=continuous_update.value)
    with solara.Row():
        solara.Button("Clear", on_click=lambda: text.set(""))
        solara.Button("Save", on_click=lambda: text.set(""))


@solara.component
def ColorCard(title, color):
    with rv.Card(style_=f"background-color: {color}; width: 100%; height: 100%") as main:
        rv.CardTitle(children=[title])
    return main
