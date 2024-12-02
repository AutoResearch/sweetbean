"""Generate the code reference pages and navigation."""

from pathlib import Path
from typing import List

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

ignore = [
    Path("./src/sweetbean/_const.py"),
    Path("./src/sweetbean/util/parse.py"),
    Path("./src/sweetbean/stimulus/_Template_.py"),
    Path("./src/sweetbean/stimulus/Stimulus.py"),
]

source_paths = sorted(Path("./").rglob("**/src"))
special_paths: List[Path] = []  # [Path("./docs/docstrings.py")]


def source_file_generator(src_paths):
    """Generate the paths and src directory paths of each python file."""
    for src_path in src_paths:
        for path in sorted(src_path.rglob("**/*.py")):
            yield path, src_path


def get_reference_file_string(p):
    """

    Args:
        p: a tuple of module names which combine to make an identifier

    Returns:
        A markdown string with the full combined module name (excluding any __init__ part) as
        the L1-title and the mkdocstrings "::: <identifier>" below

    Examples:
        >>> print(get_reference_file_string(("a",)))
        # a
        <BLANKLINE>
        ::: a

        >>> print(get_reference_file_string(("__init__",)))
        Traceback (most recent call last):
        ...
        AssertionError: __init__ must have a parent

        >>> print(get_reference_file_string(("a", "b")))
        # a.b
        <BLANKLINE>
        ::: a.b

        >>> print(get_reference_file_string(("a", "b", "__init__")))
        # a.b
        <BLANKLINE>
        ::: a.b.__init__

    """
    if p[-1] == "__init__":
        ident = ".".join(p[:-1])
        assert ident != "", "__init__ must have a parent"
    else:
        ident = ".".join(p)
    title = ident.replace("_", "\\_")
    s = f"# {title}\n\n::: {ident}"
    return s


for path, src_path in source_file_generator(source_paths):
    if path in ignore:
        continue
    module_path = path.relative_to(src_path).with_suffix("")
    doc_path = path.relative_to(src_path).with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    parts = tuple(module_path.parts)

    if parts[-1] == "__init__":
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")

    nav[parts] = doc_path.as_posix()

    docstring_stub = get_reference_file_string(parts)

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        fd.write(docstring_stub)

    mkdocs_gen_files.set_edit_path(full_doc_path, path)

with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
#
# for path in source_paths + special_paths:
#     if path in ignore:
#         continue
#     module_path = path.relative_to(".").with_suffix("")
#     doc_path = path.relative_to(".").with_suffix(".md")
#     full_doc_path = Path("reference", doc_path)
#
#     parts = tuple(module_path.parts)
#
#     if parts[-1] == "__init__":
#         parts = parts[:-1]
#         doc_path = doc_path.with_name("index.md")
#         full_doc_path = full_doc_path.with_name("index.md")
#     elif parts[-1] == "__main__":
#         continue
#
#     nav[parts] = doc_path.as_posix()
#     print('parts:', parts)
#     with mkdocs_gen_files.open(full_doc_path, "w") as fd:
#         ident = ".".join(parts)
#         fd.write(f"::: {ident}")
#
#     mkdocs_gen_files.set_edit_path(full_doc_path, path)
#
# with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
#     nav_file.writelines(nav.build_literate_nav())
