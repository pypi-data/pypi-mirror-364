import ast
from pathlib import Path

def extract_function(path: Path, func_name: str) -> str:
    tree = ast.parse(path.read_text())
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            return ast.unparse(node)
    raise ValueError(f"Function '{func_name}' not found.")
