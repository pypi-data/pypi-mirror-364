import json
import csv
import yaml        # YAML support
import openpyxl    # Excel support
import ast
from pathlib import Path

# Directory where files are bridged
DATA_DIR = Path(".coral8")


# ─── Updated Connect ────────────────────────────────────────────────────────────
def connect_file(source_path: str, alias: str = None):
    src = Path(source_path).resolve()
    if not src.exists():
        raise FileNotFoundError(f"File '{source_path}' not found. Please check the path.")

    DATA_DIR.mkdir(exist_ok=True)  # ← inside now

    filename = alias or src.name
    dst = DATA_DIR / filename
    print(f"✅ Bridged: {filename}")

    try:
        dst.write_bytes(src.read_bytes())
    except Exception as e:
        raise RuntimeError(f"Failed to bridge file '{filename}': {e}")

# ─── Rest of core.py (unchanged) ────────────────────────────────────────────────
def import_file(name: str):
    file_path = DATA_DIR / name
    if not file_path.exists():
        raise FileNotFoundError(f"File '{name}' not found in bridged files.")

    ext = file_path.suffix.lower()
    try:
        if ext == ".json":
            return json.loads(file_path.read_text(encoding="utf-8"))
        elif ext == ".csv":
            with file_path.open(newline="", encoding="utf-8") as f:
                return list(csv.DictReader(f))
        elif ext in (".yml", ".yaml"):
            with file_path.open(encoding="utf-8") as f:
                return yaml.safe_load(f)
        elif ext == ".xlsx":
            wb = openpyxl.load_workbook(file_path)
            sheet = wb.active
            return [row for row in sheet.iter_rows(values_only=True)]
        elif ext == ".txt":
            return file_path.read_text(encoding="utf-8").splitlines()
        elif ext == ".py":
            return file_path.read_text(encoding="utf-8")
        else:
            raise ValueError(f"Unsupported file type '{ext}' for file '{name}'.")
    except Exception as e:
        raise ValueError(f"Error loading file '{name}': {e}")

def list_files():
    return [f.name for f in DATA_DIR.iterdir() if f.is_file()]

def inject_symbol(filename: str, symbol: str):
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"File '{filename}' not found in bridged files.")
    if path.suffix != ".py":
        raise ValueError("inject only works on Python files.")

    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == symbol:
            return ast.unparse(node)
    raise ValueError(f"Symbol '{symbol}' not found in {filename}.")

def remove_file(name: str):
    if name.lower() == "all":
        for f in DATA_DIR.iterdir():
            if f.is_file():
                f.unlink()
        print("🧹 Scrubbed all bridged files.")
    else:
        target = DATA_DIR / name
        if not target.exists():
            raise FileNotFoundError(f"File '{name}' not found in bridged files.")
        target.unlink()
        print(f"✅ Scrubbed: {name}")




