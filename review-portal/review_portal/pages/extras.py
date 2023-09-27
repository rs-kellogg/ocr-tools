import solara

@solara.component
def Page():
    with solara.VBox() as main:
        with solara.Card(title="Test", margin=0) as card:
            solara.Info("Hello World")
