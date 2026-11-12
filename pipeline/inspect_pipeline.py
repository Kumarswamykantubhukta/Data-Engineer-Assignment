
import ast
from pathlib import Path

FILES = [
    "ingestion.py",
    "greenhouse.py",
    "lever.py",
    "hackernews.py",
    "hackernews_parser.py",
    "filtering.py",
    "deduplication.py",
    "incremental.py",
    "evidence_validator.py",
    "extractor.py",
    "repository.py",
    "exporter.py",
]

for filename in FILES:
    path = Path("pipeline") / filename

    print(f"\n{'=' * 60}")
    print(filename)
    print("=" * 60)

    tree = ast.parse(path.read_text(encoding="utf-8"))

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = ast.unparse(node.args)
            print(f"\n{node.name}({args})")
            print(ast.get_docstring(node) or "No docstring")
