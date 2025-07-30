import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
import subprocess
import pathlib

app = typer.Typer(help="Git utilities for cbler")
console = Console()


def get_git_branches(path: pathlib.Path) -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(path), "branch", "--show-current"],
            stderr=subprocess.DEVNULL,
        )
        return out.decode().strip() or None
    except:
        return None


@app.command()
def log(
    directory: str = typer.Argument(".", help="Directory to search for git repo"),
    num: int = typer.Argument(10, help="Number of commits to show"),
):
    path = pathlib.Path(directory).resolve()
    branch = get_git_branches(path)
    if branch:
        console.print(
            Panel(
                f"[bold green]On branch:[/bold green] [yellow]{branch}[/yellow]",
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
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode("utf-8")
        lines = [l for l in output.splitlines() if l.strip()]
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error running git: {e.output.decode('utf-8')}[/red]")
        return

    table = Table(
        show_header=True,
        header_style="bold magenta",
        box=box.SIMPLE_HEAVY,
        padding=(0, 1),
    )
    table.add_column("Hash", style="cyan", no_wrap=True)
    table.add_column("Ref", style="yellow", no_wrap=True)
    table.add_column("Message", style="white")
    table.add_column("When", style="dim", no_wrap=True)
    table.add_column("Who", style="green", no_wrap=True)
    table.add_column("Body", style="white")

    for line in lines:
        if line.startswith("[red]"):
            console.print(line)
            return
        parts = line.split("|", maxsplit=5)
        if len(parts) == 6:
            table.add_row(*[p.strip() for p in parts])
        else:
            table.add_row(*parts, *["" for _ in range(6 - len(parts))])
    console.print(table)


@app.command()
def diff(
    directory: str = typer.Argument(".", help="Directory to search for git repo"),
    staged: bool = typer.Option(
        False, "--staged", "-s", help="Show staged diff (default: unstaged)"
    ),
    include_untracked: bool = typer.Option(
        False, "--untracked", "-u", help="Include untracked files (U)"
    ),
):
    """
    Show git diff status of files (A=added, M=modified, D=deleted), and optionally untracked (U).
    """
    path = pathlib.Path(directory).resolve()
    branch = get_git_branches(path)
    if branch:
        console.print(
            Panel(
                f"[bold green]On branch:[/bold green] [yellow]{branch}[/yellow]",
                title="Branch",
            )
        )

    # Get tracked changes via name-status
    cmd = ["git", "-C", str(path), "diff", "--name-status"]
    if staged:
        cmd.append("--cached")
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error: {e.output.decode('utf-8')}[/red]")
        return

    table = Table(
        show_header=True,
        header_style="bold magenta",
        box=box.SIMPLE_HEAVY,
        title="Git Diff Status",
    )
    table.add_column("Status", style="cyan", no_wrap=True)
    table.add_column("File", style="white")

    had_entry = False
    print(output)
    for line in output.strip().splitlines():
        parts = line.split("	", 1)
        if len(parts) == 2:
            status, filename = parts
            table.add_row(status, filename)
            had_entry = True
    # Include untracked files
    if include_untracked and not staged:
        try:
            untracked = (
                subprocess.check_output(
                    [
                        "git",
                        "-C",
                        str(path),
                        "ls-files",
                        "--others",
                        "--exclude-standard",
                    ],
                    stderr=subprocess.DEVNULL,
                )
                .decode("utf-8")
                .splitlines()
            )
        except subprocess.CalledProcessError:
            untracked = []
        for f in untracked:
            table.add_row("U", f)
            had_entry = True

    if not had_entry:
        table.add_row("-", "[dim]No changes[/dim]")
    console.print(table)


@app.command()
def tree(
    directory: str = typer.Argument(".", help="Directory to search for git repo"),
    num: int = typer.Option(20, "--num", "-n", help="Number of commits to show"),
):
    path = pathlib.Path(directory).resolve()
    branch = get_git_branches(path)
    if branch:
        console.print(
            Panel(
                f"[bold green]On branch:[/bold green] [yellow]{branch}[/yellow]",
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
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode("utf-8")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error: {e.output.decode('utf-8')}[/red]")
        return

    console.print(
        Panel(
            f"[white]{output}[/white]",
            title=f"Git Graph (last {num} commits)",
            subtitle="[dim]Use --num/-n to change depth[/dim]",
            style="cyan",
        )
    )
