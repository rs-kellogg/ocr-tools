from IPython.display import IFrame, Image, FileLink, HTML
from pathlib import Path
from typing import Optional, cast
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
        if e['row'] == (len(grid.data)-1) and e['column'] == 'amount':
            return
        amounts = grid.data['amount']
        summed_amount = amounts[1:-2].sum()
        given_total = amounts[-2:-1].sum()
        diff = given_total - summed_amount
        grid.set_cell_value('amount', len(grid.data)-1, diff)
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
    company_renderer = TextRenderer(
        text_color="black", 
        background_color=Expr(background_color),
    )

    amount_renderer = TextRenderer(
        text_color="black", 
        background_color=Expr(background_color),
        format=","
    )

    # renderers={'amount': amount_renderer, 'company': company_renderer}
    # col_widths = {"company": 300}

    df = pd.read_csv(file)
    df = df.drop(columns=['Unnamed: 0'])
    with solara.VBox() as main:
        solara.DataFrame(df)
        DataGrid.element(
            dataframe=df,
            editable=True,
            layout={"height": f"1000px", "overflow_y": "auto"},
            base_row_size=30,
            base_column_size=120,
            # default_renderer=company_renderer,
            # renderers=renderers,
            # column_widths=col_widths,
        )
    return main


@solara.component
def pdf_viewer(name: str, file: Path):
    page_number = int(file.name.split('-')[-2])
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
    page_number = file.name.split('-')[-2]
    print(f"png_viewer: {file.name}: {page_number}")
    solara.Image(f"/static/public/png/page-{page_number}.png")


text = solara.reactive("")
continuous_update = solara.reactive(True)

@solara.component
def text_input():
    solara.InputText("Enter some text", value=text, continuous_update=continuous_update.value)
    with solara.Row():
        solara.Button("Clear", on_click=lambda: text.set(""))    


@solara.component
def ColorCard(title, color):
    with rv.Card(style_=f"background-color: {color}; width: 100%; height: 100%") as main:
        rv.CardTitle(children=[title])
    return main