import typer
import pathlib
import subprocess
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box


_git_console = Console()

git_app = typer.Typer(help="Git helpers")


def _branch(path: pathlib.Path) -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(path), "branch", "--show-current"],
            stderr=subprocess.DEVNULL,
        )
        return out.decode().strip() or None
    except Exception:
        return None


@git_app.command()
def log(
    directory: str = typer.Argument(".", help="Repo dir"),
    num: int = typer.Argument(10, help="Commits to show"),
):
    path = pathlib.Path(directory).resolve()
    br = _branch(path)
    if br:
        _git_console.print(
            Panel(
                f"[bold green]On branch:[/bold green] [yellow]{br}[/yellow]",
                box=box.ROUNDED,
            )
        )
    cmd = [
        "git",
        "-C",
        str(path),
        "log",
        f"-n{num}",
        "--pretty=format:%C(auto)%h%Creset|%C(yellow)%d%Creset|%s|%C(dim)%cr%Creset|%an|%b",
        "--decorate=short",
        "--date=relative",
    ]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode("utf-8")
        lines = [l for l in out.splitlines() if l.strip()]
    except subprocess.CalledProcessError as e:
        _git_console.print(f"[red]Error: {e.output.decode('utf-8')}[/red]")
        return
    tbl = Table(
        show_header=True,
        header_style="bold magenta",
        box=box.SIMPLE_HEAVY,
        padding=(0, 1),
    )
    tbl.add_column("Hash", style="cyan", no_wrap=True)
    tbl.add_column("Ref", style="yellow", no_wrap=True)
    tbl.add_column("Message", style="white")
    tbl.add_column("When", style="dim", no_wrap=True)
    tbl.add_column("Who", style="green", no_wrap=True)
    tbl.add_column("Body", style="white")
    for line in lines:
        parts = line.split("|", maxsplit=5)
        while len(parts) < 6:
            parts.append("")
        tbl.add_row(*[p.strip() for p in parts])
    _git_console.print(tbl)


@git_app.command()
def diff(
    directory: str = typer.Argument(".", help="Repo dir"),
    staged: bool = typer.Option(False, "--staged", "-s", help="Show staged diff"),
    include_untracked: bool = typer.Option(
        True, "--untracked/--no-untracked", "-u", help="Include untracked files"
    ),
):
    path = pathlib.Path(directory).resolve()
    br = _branch(path)
    if br:
        _git_console.print(
            Panel(
                f"[bold green]On branch:[/bold green] [yellow]{br}[/yellow]",
                title="Branch",
            )
        )
    cmd = ["git", "-C", str(path), "diff", "--name-status"]
    if staged:
        cmd.append("--cached")
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8")
    except subprocess.CalledProcessError as e:
        _git_console.print(f"[red]Error: {e.output.decode('utf-8')}[/red]")
        return
    tbl = Table(
        show_header=True,
        header_style="bold magenta",
        box=box.SIMPLE_HEAVY,
        title="Git Diff Status",
    )
    tbl.add_column("Status", style="cyan", no_wrap=True)
    tbl.add_column("File", style="white")
    had = False
    for line in out.strip().splitlines():
        parts = line.split("\t", 1)
        if len(parts) == 2:
            tbl.add_row(parts[0], parts[1])
            had = True
    if include_untracked and not staged:
        try:
            u = subprocess.check_output(
                ["git", "-C", str(path), "ls-files", "--others", "--exclude-standard"],
                stderr=subprocess.DEVNULL,
            )
            for f in u.decode().splitlines():
                tbl.add_row("U", f)
                had = True
        except subprocess.CalledProcessError:
            pass
    if not had:
        tbl.add_row("-", "[dim]No changes[/dim]")
    _git_console.print(tbl)


@git_app.command()
def tree(
    directory: str = typer.Argument(".", help="Repo dir"),
    num: int = typer.Option(20, "--num", "-n", help="Number of commits"),
):
    path = pathlib.Path(directory).resolve()
    br = _branch(path)
    if br:
        _git_console.print(
            Panel(
                f"[bold green]On branch:[/bold green] [yellow]{br}[/yellow]",
                title="Branch",
            )
        )
    cmd = [
        "git",
        "-C",
        str(path),
        "log",
        "--graph",
        "--oneline",
        "--decorate",
        f"-n{num}",
        "--color=never",
    ]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode("utf-8")
    except subprocess.CalledProcessError as e:
        _git_console.print(f"[red]Error: {e.output.decode('utf-8')}[/red]")
        return
    _git_console.print(
        Panel(
            f"[white]{out}[/white]",
            title=f"Git Graph (last {num} commits)",
            subtitle="[dim]Use --num/-n to change depth[/dim]",
            style="cyan",
        )
    )
