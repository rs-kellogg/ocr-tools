import pandas as pd
import numpy as np
import solara
import reacton
import ipydatagrid

df = solara.reactive(pd.DataFrame(np.random.rand(10,4)))

@solara.component
def Page():
    def set_data():
        df.set(pd.DataFrame(np.random.rand(10,4)))

    solara.Button(label='Random Data', on_click=set_data)
    dg = ipydatagrid.DataGrid.element(dataframe=df.value, editable=True)
    dg.key(f'datagrid-{df}')

    def attach_event_handler():
        # get a reference to the real widget
        dg_widget = reacton.get_widget(dg)
        def cell_changed(e):
            dg_widget.data.iat[e["row"], e["column_index"]] = e["value"]
            print(dg_widget.data)
            dg_widget.data.to_csv("temp.csv", index=True)

        def cleanup():
            dg_widget.on_click(cell_changed, remove=True)
        
        # add the event handler, and return the cleanup
        dg_widget.on_cell_change(cell_changed)
        return cleanup

    reacton.use_effect(attach_event_handler)
    return dg

Page()