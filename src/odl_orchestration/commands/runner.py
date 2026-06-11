import typer
from pathlib import Path
from odl_orchestration.workflows.weather_mvp import WeatherMVPWorkflow

app = typer.Typer(help="Run workflows")

@app.command(name="weather-mvp-local")
def weather_mvp_local(
    catalog_path: Path = typer.Option(..., help="Path to the datasets catalog"),
    ingestion_repo_path: Path = typer.Option(..., help="Path to the ingestion repository"),
    transformation_repo_path: Path = typer.Option(..., help="Path to the transformation repository"),
    quality_repo_path: Path = typer.Option(..., help="Path to the quality repository"),
    workspace_dir: Path = typer.Option(Path("./workspace"), help="Path to the workspace directory"),
    dataset: str = typer.Option("meteocat-weather", help="Dataset ID"),
    resource: str = typer.Option("stations-metadata", help="Resource name (stations-metadata, variables-metadata, measured-variable, all)"),
    mode: str = typer.Option("sample", help="Ingestion mode to use for Weather MVP runs. sample is offline/default; real calls the upstream Meteocat API via ingestion."),
    use_contracts: bool = typer.Option(False, help="Enable optional landing contract/schema validation using datasets-catalog contracts.")
) -> None:
    """Run the Weather MVP local workflow."""
    allowed_resources = ["stations-metadata", "variables-metadata", "measured-variable", "all"]
    if resource not in allowed_resources:
        typer.echo(f"Error: Unsupported resource '{resource}'. Allowed values: {', '.join(allowed_resources)}")
        raise typer.Exit(code=1)

    allowed_modes = ["sample", "real"]
    if mode not in allowed_modes:
        typer.echo(f"Error: Unsupported mode '{mode}'. Allowed values: {', '.join(allowed_modes)}")
        raise typer.Exit(code=1)

    typer.echo(f"Starting Weather MVP local workflow for {dataset}/{resource} in {mode} mode...")
    
    workflow = WeatherMVPWorkflow(
        catalog_path=catalog_path,
        ingestion_repo_path=ingestion_repo_path,
        transformation_repo_path=transformation_repo_path,
        quality_repo_path=quality_repo_path,
        workspace_dir=workspace_dir,
        mode=mode,
        use_contracts=use_contracts
    )
    
    summary = workflow.run(dataset_id=dataset, resource=resource)
    
    typer.echo("-" * 40)
    typer.echo(f"Run ID: {summary.run_id}")
    typer.echo(f"Status: {summary.status}")
    typer.echo(f"Started at: {summary.started_at}")
    typer.echo(f"Finished at: {summary.finished_at}")
    typer.echo("-" * 40)
    
    for step in summary.steps:
        typer.echo(f"Step: {step.step_name} -> {step.status}")
        if step.status != "SUCCESS":
            typer.echo(f"Error: {step.stderr}")
            
    if summary.status != "SUCCESS":
        typer.echo("Workflow failed.")
        raise typer.Exit(code=1)
    
    typer.echo("Workflow completed successfully.")
