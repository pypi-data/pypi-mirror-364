from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel
from rich.table import Table
from rich import box
import pathlib

_console = Console()


def print_tree(paths: list[str], base: pathlib.Path, title: str) -> None:
    tree = Tree(f"[bold green]{title} from [yellow]{base}[/yellow]")
    for rel in sorted(paths):
        _add_to_tree(tree, rel)
    _console.print(
        tree if paths else "[red]No files matched the filters. Nothing copied.[/red]"
    )


def _add_to_tree(tree: Tree, rel_path: str) -> None:
    parts = rel_path.split("/")
    branch = tree
    for part in parts[:-1]:
        found = next(
            (c for c in branch.children if isinstance(c, Tree) and c.label == part),
            None,
        )
        branch = found or branch.add(part)
    branch.add(f"[bold white]{parts[-1]}[/bold white]")


def print_summary(copied: int, skipped: int) -> None:
    tbl = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    tbl.add_column("Result", style="cyan", justify="center")
    tbl.add_column("Count", style="yellow", justify="right")
    tbl.add_row("[green]Copied[/green]", str(copied))
    tbl.add_row("[red]Skipped[/red]", str(skipped))
    _console.print(Panel(tbl, title="[bold]Summary[/bold]", subtitle=":rocket:"))
