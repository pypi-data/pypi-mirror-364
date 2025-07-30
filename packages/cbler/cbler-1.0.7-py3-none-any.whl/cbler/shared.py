import os
import pathlib
import subprocess
import pyperclip
from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel
from rich.table import Table
from rich import box
from cbler.filters import FilterOptions

console = Console()


def report_results(
    copied: list[str],
    skipped: list[str],
    base_path: pathlib.Path,
    operation: str = "Copied",
):
    """Pretty-print the tree of copied files and a summary panel."""
    tree = Tree(f"[bold green]{operation} files from [yellow]{base_path}[/yellow]")
    for rel in sorted(copied):
        _add_path_to_tree(tree, rel)
    console.print(
        tree if copied else "[red]No files matched the filters. Nothing copied.[/red]"
    )
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Result", style="cyan", justify="center")
    table.add_column("Count", style="yellow", justify="right")
    table.add_row("[green]Copied[/green]", str(len(copied)))
    table.add_row("[red]Skipped[/red]", str(len(skipped)))
    console.print(Panel(table, title="[bold]Summary[/bold]", subtitle=":rocket:"))


def _add_path_to_tree(tree: Tree, rel_path: str):
    """Add a relative path to a Rich Tree, creating directory nodes as needed."""
    parts = rel_path.split("/")
    branch = tree
    for part in parts[:-1]:
        existing = next(
            (c for c in branch.children if isinstance(c, Tree) and c.label == part),
            None,
        )
        branch = existing or branch.add(part)
    branch.add(f"[bold white]{parts[-1]}[/bold white]")


def get_git_repo_root(path: pathlib.Path) -> pathlib.Path | None:
    """Return the git repo root for the given path, or None if not a git repo."""
    try:
        out = subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
        )
        return pathlib.Path(out.decode().strip())
    except:
        return None


def get_git_changed_files(repo_root: pathlib.Path) -> set[str]:
    """Return set of files changed (unstaged) in the git repo."""
    try:
        out = subprocess.check_output(
            ["git", "-C", str(repo_root), "diff", "--name-only"],
            stderr=subprocess.DEVNULL,
        )
        return set(out.decode().splitlines())
    except:
        return set()


def run_code_filter(
    path: str,
    filters: FilterOptions,
    extract_funcs: dict[str, callable],
    script_exts: tuple[str, ...],
    object_exts: tuple[str, ...] = (),
):
    """
    Walk files under `path`, apply `filters`, extract via `extract_funcs`,
    copy concatenated output to clipboard, and report via Rich.

    extract_funcs keys: 'script', 'object'.
    """
    base = pathlib.Path(path).resolve()
    changed = set()
    if filters.git_diff:
        repo = get_git_repo_root(base)
        if repo:
            changed = get_git_changed_files(repo)
    copied, skipped, output = [], [], []

    def split(vals: list[str] | None) -> list[str]:
        return [p for e in (vals or []) for p in e.split()]

    pf, npf = split(filters.prefix), split(filters.not_prefix)
    sf, nsf = split(filters.suffix), split(filters.not_suffix)
    cf, ncf = split(filters.contains), split(filters.not_contains)
    pcf, npcf = split(filters.path_contains), split(filters.not_path_contains)
    parcf, nparcf = split(filters.parent_contains), split(filters.not_parent_contains)

    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in {"venv", ".venv", "__pycache__", ".git"}]
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), base).replace("\\", "/")
            if filters.git_diff and rel not in changed:
                skipped.append(rel)
                continue
            if pf and not any(rel.startswith(p) for p in pf):
                skipped.append(rel)
                continue
            if npf and any(rel.startswith(p) for p in npf):
                skipped.append(rel)
                continue
            if sf and not any(rel.endswith(s) for s in sf):
                skipped.append(rel)
                continue
            if nsf and any(rel.endswith(s) for s in nsf):
                skipped.append(rel)
                continue
            if cf and not any(p in rel for p in cf):
                skipped.append(rel)
                continue
            if ncf and any(p in rel for p in ncf):
                skipped.append(rel)
                continue
            if pcf and not any(p in rel for p in pcf):
                skipped.append(rel)
                continue
            if npcf and any(p in rel for p in npcf):
                skipped.append(rel)
                continue
            parent = pathlib.Path(rel).parent.name
            if parcf and not any(p == parent for p in parcf):
                skipped.append(rel)
                continue
            if nparcf and any(p == parent for p in nparcf):
                skipped.append(rel)
                continue
            if f.endswith(script_exts):
                output.append(
                    f"// Script: {rel}\n"
                    + extract_funcs["script"](os.path.join(root, f))
                )
                copied.append(rel)
            elif f.endswith(object_exts):
                output.append(
                    f"// Object: {rel}\n"
                    + extract_funcs["object"](os.path.join(root, f))
                )
                copied.append(rel)
            else:
                skipped.append(rel)

    final = "\n\n".join(output)
    pyperclip.copy(final)
    report_results(copied, skipped, base)
