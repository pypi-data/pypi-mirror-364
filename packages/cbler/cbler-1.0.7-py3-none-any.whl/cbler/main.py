import typer
import pkgutil
import importlib
import cbler.commands


app = typer.Typer(add_completion=False, no_args_is_help=True)
code_app = typer.Typer()
# Load language commands dynamically
for _, modname, _ in pkgutil.iter_modules(cbler.commands.__path__):
    mod = importlib.import_module(f"cbler.commands.{modname}")
    if hasattr(mod, "app"):
        if modname == "git":
            app.add_typer(mod.app, name="git")
        else:
            code_app.add_typer(mod.app, name=modname)
# Register code subcommands
app.add_typer(code_app, name="code")

if __name__ == "__main__":
    app()
