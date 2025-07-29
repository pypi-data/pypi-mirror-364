# loader.py
from pathlib import Path
import csv
import json

def parse_file(path: str):
    """
    Naïve parser: 
     - .txt/.txr → list of lines
     - .csv       → list of dicts
     - .json      → loaded JSON
    """
    p = Path(path)
    ext = p.suffix.lower()
    if ext in ('.txt', '.txr'):
        return p.read_text(encoding='utf-8').splitlines()
    elif ext == '.csv':
        with p.open(newline='', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    elif ext == '.json':
        return json.load(p.open(encoding='utf-8'))
    else:
        raise ValueError(f"Unsupported format: {ext}")
