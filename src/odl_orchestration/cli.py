import typer
from odl_orchestration.commands import runner

app = typer.Typer(help="Open Data Lakehouse Lab Orchestration CLI")

@app.command()
def version() -> None:
    """Show the version of the orchestration tool."""
    typer.echo("odl-orchestration version 0.1.0")

app.add_typer(runner.app, name="run")

if __name__ == "__main__":
    app()
