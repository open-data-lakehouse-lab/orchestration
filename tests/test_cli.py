from typer.testing import CliRunner
from odl_orchestration.cli import app
from unittest.mock import patch, MagicMock
from datetime import datetime
from odl_orchestration.models.run import RunSummary

runner = CliRunner()

def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "odl-orchestration version" in result.output

def test_run_weather_mvp_local_help():
    result = runner.invoke(app, ["run", "weather-mvp-local", "--help"])
    assert result.exit_code == 0
    assert "Run the Weather MVP local workflow" in result.output

@patch("odl_orchestration.commands.runner.WeatherMVPWorkflow")
def test_run_weather_mvp_local_success(mock_workflow_class):
    mock_workflow = MagicMock()
    mock_workflow_class.return_value = mock_workflow
    
    mock_summary = RunSummary(
        run_id="test-run",
        workflow_name="weather-mvp-local",
        dataset_id="meteocat-weather",
        resource="stations-metadata",
        status="SUCCESS",
        started_at=datetime.now(),
        finished_at=datetime.now(),
        steps=[],
        artifacts=[]
    )
    mock_workflow.run.return_value = mock_summary
    
    result = runner.invoke(app, [
        "run", "weather-mvp-local",
        "--catalog-path", ".",
        "--ingestion-repo-path", ".",
        "--transformation-repo-path", ".",
        "--quality-repo-path", ".",
        "--workspace-dir", "./workspace"
    ])
    
    assert result.exit_code == 0
    assert "Workflow completed successfully" in result.output

@patch("odl_orchestration.commands.runner.WeatherMVPWorkflow")
def test_run_weather_mvp_local_failure(mock_workflow_class):
    mock_workflow = MagicMock()
    mock_workflow_class.return_value = mock_workflow
    
    mock_summary = RunSummary(
        run_id="test-run",
        workflow_name="weather-mvp-local",
        dataset_id="meteocat-weather",
        resource="stations-metadata",
        status="FAILED",
        started_at=datetime.now(),
        finished_at=datetime.now(),
        steps=[],
        artifacts=[]
    )
    mock_workflow.run.return_value = mock_summary
    
    result = runner.invoke(app, [
        "run", "weather-mvp-local",
        "--catalog-path", ".",
        "--ingestion-repo-path", ".",
        "--transformation-repo-path", ".",
        "--quality-repo-path", ".",
        "--workspace-dir", "./workspace"
    ])
    
    assert result.exit_code == 1
    assert "Workflow failed" in result.output
