import pandas as pd
import numpy as np
import solara
import ipydatagrid

df = solara.reactive(pd.DataFrame(np.random.rand(10,4)))

@solara.component
def Page():
    def set_data():
        df.set(pd.DataFrame(np.random.rand(10,4)))

    solara.Button(label='Random Data', on_click=set_data)
    dg = ipydatagrid.DataGrid.element(dataframe=df.value)
    dg.key(f'datagrid-{df}')
    
Page()
