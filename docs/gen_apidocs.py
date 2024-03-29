"""Generate API docs"""

from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

for path in Path("head_hunter").rglob("*.py"):
    if path.name.startswith("_") and path.name != "__init__.py":
        continue
    if ".ipynb_checkpoints" in path.parts:
        continue

    doc_file_path = Path("reference") / path.with_suffix(".md")
    py_path = path.with_suffix("").parts

    if path.name == "__init__.py":
        doc_file_path = doc_file_path.with_name("index.md")
        py_path = py_path[:-1]

    with mkdocs_gen_files.open(doc_file_path, "w") as doc_file:
        doc_file.write(f":::{'.'.join(py_path)}\n")

    mkdocs_gen_files.set_edit_path(doc_file_path, path)
    nav[py_path] = doc_file_path.relative_to(Path("reference")).as_posix()

with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
