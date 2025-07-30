import typer
from typing import List, Optional
from cbler.filters import FilterOptions, PY_DEFAULTS
from cbler.shared import run_code_filter

app = typer.Typer(invoke_without_command=True)


@app.callback()
def main(
    path: str = typer.Argument(".", help="Path to Python project"),
    prefix: Optional[List[str]] = typer.Option(
        PY_DEFAULTS.prefix, "--prefix", help="Only include files with these prefixes"
    ),
    not_prefix: Optional[List[str]] = typer.Option(
        PY_DEFAULTS.not_prefix, "--not-prefix", help="Exclude files with these prefixes"
    ),
    suffix: Optional[List[str]] = typer.Option(
        PY_DEFAULTS.suffix, "--suffix", help="Only include files with these suffixes"
    ),
    not_suffix: Optional[List[str]] = typer.Option(
        PY_DEFAULTS.not_suffix, "--not-suffix", help="Exclude files with these suffixes"
    ),
    contains: Optional[List[str]] = typer.Option(
        PY_DEFAULTS.contains, "--contains", help="Filename contains (regex ok)"
    ),
    not_contains: Optional[List[str]] = typer.Option(
        PY_DEFAULTS.not_contains,
        "--not-contains",
        help="Filename does NOT contain (regex ok)",
    ),
    path_contains: Optional[List[str]] = typer.Option(
        PY_DEFAULTS.path_contains,
        "--path-contains",
        help="Relative path contains (regex ok)",
    ),
    not_path_contains: Optional[List[str]] = typer.Option(
        PY_DEFAULTS.not_path_contains,
        "--not-path-contains",
        help="Relative path does NOT contain (regex ok)",
    ),
    parent_contains: Optional[List[str]] = typer.Option(
        PY_DEFAULTS.parent_contains,
        "--parent-contains",
        help="Direct parent folder matches (regex ok)",
    ),
    not_parent_contains: Optional[List[str]] = typer.Option(
        PY_DEFAULTS.not_parent_contains,
        "--not-parent-contains",
        help="Direct parent folder does NOT match (regex ok)",
    ),
    regex: bool = typer.Option(
        PY_DEFAULTS.regex, "--regex", help="Use regex for filters"
    ),
    git_diff: bool = typer.Option(
        PY_DEFAULTS.git_diff, "--git-diff", help="Only include files changed by git"
    ),
):
    """
    Concatenate Python files based on filters and copy to clipboard.
    """

    def extract_py_code(filepath: str) -> str:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    filters = FilterOptions(
        regex=regex,
        git_diff=git_diff,
        prefix=prefix,
        not_prefix=not_prefix,
        suffix=suffix,
        not_suffix=not_suffix,
        contains=contains,
        not_contains=not_contains,
        path_contains=path_contains,
        not_path_contains=not_path_contains,
        parent_contains=parent_contains,
        not_parent_contains=not_parent_contains,
    )
    run_code_filter(
        path,
        filters,
        extract_funcs={"script": extract_py_code, "object": lambda p: ""},
        script_exts=(".py",),
        object_exts=(),
    )
