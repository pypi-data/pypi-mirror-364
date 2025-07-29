import ast
from pathlib import Path

def extract_function(path: Path, func_name: str) -> str:
    tree = ast.parse(path.read_text())
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            return ast.unparse(node)
    raise ValueError(f"Function '{func_name}' not found.")

def inject_function(source_path: Path, target_path: Path, func_name: str) -> str:
    # Parse source file and extract symbol
    symbol_code = extract_function(source_path, func_name)

    # Read and check target file
    if not target_path.exists():
        raise FileNotFoundError(f"Target file '{target_path}' does not exist.")

    target_text = target_path.read_text()

    # Prevent duplication
    if func_name in target_text:
        return f"⚠️  Symbol '{func_name}' already exists in '{target_path.name}', skipping."

    # Append safely
    with target_path.open("a", encoding="utf-8") as f:
        f.write("\n\n" + symbol_code + "\n")

    return f"✅ Grafted '{func_name}' into '{target_path.name}'"
