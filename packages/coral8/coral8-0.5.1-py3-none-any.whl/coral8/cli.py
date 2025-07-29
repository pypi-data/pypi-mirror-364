import typer
from pathlib import Path
from coral8.core import (
    connect_file as bridge_file,
    import_file as peek_file,
    list_files as vault_files,
    inject_symbol as graft_symbol,
    remove_file as scrub_file,
)

app = typer.Typer(help="coral8: zero-config file loader & simple bridge tool")

DATA_DIR = Path(".coral8")
DATA_DIR.mkdir(exist_ok=True)

@app.command()
def bridge(
    filename: str = typer.Argument(..., help="Path to the file to bridge"),
    alias: str = typer.Option(None, "--alias", "-a", help="Optional alias for the file"),
):
    """
    Bridge a file to your project. Supported: .json, .csv, .py, .txt, .yaml, .xlsx
    """
    try:
        bridge_file(filename, alias)
    except FileNotFoundError as e:
        typer.echo(f"❌ {e}")
        raise typer.Exit(code=1)
    except ValueError as e:
        typer.echo(f"❌ {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"❌ Unexpected error: {e}")
        raise typer.Exit(code=1)

@app.command()
def peek(
    name: str = typer.Argument(..., help="Name or alias of the bridged file to preview"),
):
    """
    Load and display metadata about a bridged file.
    """
    try:
        result = peek_file(name)
        typer.echo(f"✅ Loaded data of type {type(result).__name__} from '{name}'")
    except FileNotFoundError as e:
        typer.echo(f"❌ {e}")
        raise typer.Exit(code=1)
    except ValueError as e:
        typer.echo(f"❌ {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"❌ Unexpected error: {e}")
        raise typer.Exit(code=1)

@app.command()
def vault():
    """
    Show all bridged files.
    """
    try:
        files = vault_files()
        if not files:
            typer.echo("No files bridged.")
            return
        for f in files:
            typer.echo(f"📎 {f}")
    except Exception as e:
        typer.echo(f"❌ Error listing files: {e}")
        raise typer.Exit(code=1)

@app.command()
def graft(
    filename: str = typer.Argument(..., help="Source .py file to graft from"),
    symbol: str = typer.Argument(..., help="Function or class name to graft"),
):
    """
    Extract and print a function or class from a bridged Python file.
    """
    try:
        code = graft_symbol(filename, symbol)
        typer.echo(code)
    except FileNotFoundError as e:
        typer.echo(f"❌ {e}")
        raise typer.Exit(code=1)
    except ValueError as e:
        typer.echo(f"❌ {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"❌ Unexpected error: {e}")
        raise typer.Exit(code=1)

@app.command()
def scrub(
    name: str = typer.Argument(..., help="File name to scrub, or 'all' to remove all"),
):
    """
    Remove a bridged file or wipe all connections.
    """
    try:
        scrub_file(name)
    except FileNotFoundError as e:
        typer.echo(f"❌ {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"❌ Unexpected error: {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()




