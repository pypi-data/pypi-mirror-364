# coral8/cli.py

import typer
from pathlib import Path
from coral8.core import connect_file, import_file, list_files, inject_symbol
from coral8.exporter import export_data

app = typer.Typer()
# Use a global registry so commands work from any current directory
DATA_DIR = Path.home() / ".coral8"
DATA_DIR.mkdir(exist_ok=True)

@app.command()
def connect(
    filename: str = typer.Argument(..., help="File path to connect"),
    alias: str = typer.Option(None, "--alias", "-a", help="Alias for the file")
):
    """
    Connect a file to your project. Supported: .json, .csv, .py, .txt, .yaml, .xlsx
    """
    try:
        alias_name = alias or Path(filename).stem
        connect_file(filename, alias_name)
        typer.echo(f"✅ Connected: {filename} as '{alias_name}'")
    except Exception as e:
        typer.echo(f"❌ {e}")
        raise typer.Exit(code=1)

@app.command("import")
def import_(
    alias: str = typer.Argument(..., help="Alias to import")
):
    """
    Load and display metadata about a connected file or function.
    """
    try:
        result = import_file(alias)
        typer.echo(f"✅ Loaded data of type {type(result).__name__} from alias '{alias}'")
    except Exception as e:
        typer.echo(f"❌ {e}")
        raise typer.Exit(code=1)

@app.command()
def list():
    """
    Show all connected aliases.
    """
    aliases = list_files()
    if not aliases:
        typer.echo("No files connected.")
        return
    for alias in aliases:
        typer.echo(f"📎 {alias}")

@app.command()
def inject(
    filename: str = typer.Argument(..., help="Python file to extract from"),
    symbol: str = typer.Argument(..., help="Function or class name to inject")
):
    """
    Extract and print a function or class from a Python file.
    """
    try:
        code = inject_symbol(filename, symbol)
        typer.echo(code)
    except Exception as e:
        typer.echo(f"❌ {e}")
        raise typer.Exit(code=1)

@app.command()
def clear(
    alias: str = typer.Argument(..., help="Alias to remove, or 'all' to clear everything")
):
    """
    Remove a connected alias or wipe all connections.
    """
    try:
        if alias.lower() == "all":
            for f in DATA_DIR.iterdir():
                f.unlink()
            typer.echo("🧹 Cleared all connected aliases.")
        else:
            target = DATA_DIR / alias
            if not target.exists():
                typer.echo(f"❌ Alias '{alias}' not found in registry.")
                raise typer.Exit(code=1)
            target.unlink()
            typer.echo(f"✅ Removed alias: {alias}")
    except Exception as e:
        typer.echo(f"❌ {e}")
        raise typer.Exit(code=1)

@app.command()
def export(
    alias: str = typer.Argument(..., help="Alias to export"),
    to: str = typer.Option(..., "--to", "-o", help="Output filename (extension infers format)")
):
    """
    Export a connected data object or function to a file.
    """
    try:
        obj = import_file(alias)
        export_data(obj, to)
        typer.echo(f"✅ Exported alias '{alias}' to '{to}'")
    except Exception as e:
        typer.echo(f"❌ {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()



