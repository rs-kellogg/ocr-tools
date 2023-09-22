import typer
import yaml
from rich import console as cons
from typing import Optional, List
from importlib import resources
from pathlib import Path
from ocrtools import data
from ocrtools import __app_name__, __version__
from ocrtools import preprocess, pdftools

# -----------------------------------------------------------------------------
app = typer.Typer()
app.add_typer(preprocess.cli.app, name="preprocess")
app.add_typer(pdftools.cli.app, name="pdf")
console = cons.Console(style="green on black")


with resources.path(data, "config.yml") as path:
    CONFIG_FILE_PATH = Path(path)
    CONFIG_FILE_PATH.touch(exist_ok=True)

with open(CONFIG_FILE_PATH) as conf_file:
    CONFIG = yaml.load(conf_file, Loader=yaml.FullLoader)
    CONFIG = CONFIG if CONFIG else {}
    preprocess.cli.CONFIG = CONFIG
    pdftools.cli.CONFIG = CONFIG


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"[blue]version: {__app_name__} v{__version__}")
        raise typer.Exit()


# -----------------------------------------------------------------------------
@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> Optional[bool]:
    return version


# -----------------------------------------------------------------------------
@app.command()
def config(
    key: Optional[str] = typer.Option(
        None,
        "--key",
        help="Set the key",
    ),
    value: Optional[str] = typer.Option(
        None,
        "--value",
        help="Set the value",
    ),
    clear: Optional[bool] = typer.Option(
        None,
        "--clear",
        "-c",
        help="Clear all values",
    ),
) -> None:
    global CONFIG
    if clear and key is None:
        CONFIG = {}
    elif clear:
        CONFIG.pop(key, None)
    elif key is not None:
        parts = key.split(".")
        conf = CONFIG
        for idx, p in enumerate(parts):
            if idx == len(parts) - 1:
                conf[p] = value
            else:
                conf[p] = conf.get(p, {})
                conf = conf[p]

    CONFIG_FILE_PATH.write_text(yaml.dump(CONFIG))
    console.print(f"CONFIG_FILE_PATH: {CONFIG_FILE_PATH}")
    console.print(f"[green]CURRENT CONFIG SETTINGS: {CONFIG}")


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app()
