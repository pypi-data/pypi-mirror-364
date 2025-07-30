import typer
import re
import pathlib
from typing import List, Optional
from cbler.filters import FilterOptions, GML_DEFAULTS
from cbler.shared import run_code_filter

app = typer.Typer(invoke_without_command=True)


@app.callback()
def main(
    path: str = typer.Argument(".", help="Path to GameMaker project"),
    prefix: Optional[List[str]] = typer.Option(
        GML_DEFAULTS.prefix,
        "--prefix",
        "-p",
        help="Only include files with these prefixes",
    ),
    not_prefix: Optional[List[str]] = typer.Option(
        GML_DEFAULTS.not_prefix,
        "--not-prefix",
        "-P",
        help="Exclude files with these prefixes",
    ),
    suffix: Optional[List[str]] = typer.Option(
        GML_DEFAULTS.suffix,
        "--suffix",
        "-s",
        help="Only include files with these suffixes",
    ),
    not_suffix: Optional[List[str]] = typer.Option(
        GML_DEFAULTS.not_suffix,
        "--not-suffix",
        "-S",
        help="Exclude files with these suffixes",
    ),
    contains: Optional[List[str]] = typer.Option(
        GML_DEFAULTS.contains, "--contains", "-c", help="Filename contains (regex ok)"
    ),
    not_contains: Optional[List[str]] = typer.Option(
        GML_DEFAULTS.not_contains,
        "--not-contains",
        "-C",
        help="Filename does NOT contain (regex ok)",
    ),
    path_contains: Optional[List[str]] = typer.Option(
        GML_DEFAULTS.path_contains,
        "--path-contains",
        help="Relative path contains (regex ok)",
    ),
    not_path_contains: Optional[List[str]] = typer.Option(
        GML_DEFAULTS.not_path_contains,
        "--not-path-contains",
        help="Relative path does NOT contain (regex ok)",
    ),
    parent_contains: Optional[List[str]] = typer.Option(
        GML_DEFAULTS.parent_contains,
        "--parent-contains",
        help="Direct parent folder matches (regex ok)",
    ),
    not_parent_contains: Optional[List[str]] = typer.Option(
        GML_DEFAULTS.not_parent_contains,
        "--not-parent-contains",
        help="Direct parent folder does NOT match (regex ok)",
    ),
    regex: bool = typer.Option(
        GML_DEFAULTS.regex, "--regex", help="Use regex for filters"
    ),
    git_diff: bool = typer.Option(
        GML_DEFAULTS.git_diff,
        "--git-diff",
        "-g",
        help="Only include files changed by git",
    ),
):
    """
    Concatenate GML (.gml) and YY (.yy) code based on filters and copy to clipboard.
    """

    def extract_gml_code(filepath: str) -> str:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def extract_yy_code(filepath: str) -> str:
        try:
            data = open(filepath, "r", encoding="utf-8").read()
            matches = re.findall(r'"code"\s*:\s*"([^"]+)"', data)
            if matches:
                return "\n\n".join(
                    f"// Extracted Script {i + 1}:\n{code}"
                    for i, code in enumerate(matches)
                )
            return f"// Object: {pathlib.Path(filepath).stem} (No code found)"
        except Exception as e:
            return f"// ⚠️ Error reading {filepath}: {e}"

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
        extract_funcs={"script": extract_gml_code, "object": extract_yy_code},
        script_exts=(".gml",),
        object_exts=(".yy",),
    )
