import typer
from cbler.code_cmd import code_app
from cbler.git_cmd import git_app

app = typer.Typer(
    add_completion=False, no_args_is_help=True, help="cbler: concat & git helpers"
)
app.add_typer(code_app, name="code", help="Concatenate source files")
app.add_typer(git_app, name="git", help="Git utilities")

if __name__ == "__main__":  # pragma: no cover
    app()
