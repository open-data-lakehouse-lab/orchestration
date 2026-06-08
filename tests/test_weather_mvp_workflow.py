from unittest.mock import MagicMock
from datetime import datetime
from odl_orchestration.workflows.weather_mvp import WeatherMVPWorkflow
from odl_orchestration.models.run import RunStepResult

def test_weather_mvp_workflow_success(tmp_path):
    catalog_path = tmp_path / "catalog"
    ingestion_repo_path = tmp_path / "ingestion"
    transformation_repo_path = tmp_path / "transformation"
    quality_repo_path = tmp_path / "quality"
    workspace_dir = tmp_path / "workspace"
    
    mock_executor = MagicMock()
    
    workflow = WeatherMVPWorkflow(
        catalog_path=catalog_path,
        ingestion_repo_path=ingestion_repo_path,
        transformation_repo_path=transformation_repo_path,
        quality_repo_path=quality_repo_path,
        workspace_dir=workspace_dir,
        executor=mock_executor
    )
    
    # Simulate file creation by ingestion and transformation
    def side_effect(step_name, command):
        if step_name == "ingestion":
            landing_file = workflow.run_dir / "landing/sample.json"
            landing_file.parent.mkdir(parents=True, exist_ok=True)
            landing_file.touch()
        elif step_name == "transformation":
            bronze_file = workflow.run_dir / "bronze/records.jsonl"
            bronze_file.parent.mkdir(parents=True, exist_ok=True)
            bronze_file.touch()
        elif step_name == "transformation-silver":
            silver_file = workflow.run_dir / "silver/records.jsonl"
            silver_file.parent.mkdir(parents=True, exist_ok=True)
            silver_file.touch()
        return RunStepResult(
            step_name=step_name,
            command=command,
            return_code=0,
            stdout="",
            stderr="",
            status="SUCCESS",
            started_at=datetime.now(),
            finished_at=datetime.now()
        )

    mock_executor.run_command.side_effect = side_effect
    
    summary = workflow.run()
    
    assert summary.status == "SUCCESS"
    assert len(summary.steps) == 6
    assert len(summary.artifacts) == 4 # landing, bronze, silver, summary
    # Silver artifact should be there
    assert any("silver" in artifact for artifact in summary.artifacts)
    assert mock_executor.run_command.call_count == 6

    # Verify silver quality entity for stations-metadata
    quality_silver_call = [call for call in mock_executor.run_command.call_args_list if call[0][0] == "quality-silver"][0]
    assert "--entity" in quality_silver_call[0][1]
    assert quality_silver_call[0][1][quality_silver_call[0][1].index("--entity") + 1] == "stations"

def test_weather_mvp_workflow_mappings(tmp_path):
    catalog_path = tmp_path / "catalog"
    ingestion_repo_path = tmp_path / "ingestion"
    transformation_repo_path = tmp_path / "transformation"
    quality_repo_path = tmp_path / "quality"
    workspace_dir = tmp_path / "workspace"
    
    mock_executor = MagicMock()
    
    workflow = WeatherMVPWorkflow(
        catalog_path=catalog_path,
        ingestion_repo_path=ingestion_repo_path,
        transformation_repo_path=transformation_repo_path,
        quality_repo_path=quality_repo_path,
        workspace_dir=workspace_dir,
        executor=mock_executor
    )

    def side_effect(step_name, command):
        if step_name == "ingestion":
            landing_file = workflow.run_dir / "landing/sample.json"
            landing_file.parent.mkdir(parents=True, exist_ok=True)
            landing_file.touch()
        elif step_name == "transformation":
            bronze_file = workflow.run_dir / "bronze/records.jsonl"
            bronze_file.parent.mkdir(parents=True, exist_ok=True)
            bronze_file.touch()
        elif step_name == "transformation-silver":
            silver_file = workflow.run_dir / "silver/records.jsonl"
            silver_file.parent.mkdir(parents=True, exist_ok=True)
            silver_file.touch()
        return RunStepResult(
            step_name=step_name,
            command=command,
            return_code=0,
            stdout="",
            stderr="",
            status="SUCCESS",
            started_at=datetime.now(),
            finished_at=datetime.now()
        )

    mock_executor.run_command.side_effect = side_effect

    # Test variables-metadata mapping
    mock_executor.run_command.reset_mock()
    summary = workflow.run(resource="variables-metadata")
    assert summary.status == "SUCCESS"
    quality_silver_call = [call for call in mock_executor.run_command.call_args_list if call[0][0] == "quality-silver"][0]
    assert quality_silver_call[0][1][quality_silver_call[0][1].index("--entity") + 1] == "variables"

    # Test measured-variable mapping
    mock_executor.run_command.reset_mock()
    summary = workflow.run(resource="measured-variable")
    assert summary.status == "SUCCESS"
    quality_silver_call = [call for call in mock_executor.run_command.call_args_list if call[0][0] == "quality-silver"][0]
    assert quality_silver_call[0][1][quality_silver_call[0][1].index("--entity") + 1] == "measurements"

def test_weather_mvp_workflow_unsupported_resource(tmp_path):
    catalog_path = tmp_path / "catalog"
    workspace_dir = tmp_path / "workspace"
    
    workflow = WeatherMVPWorkflow(
        catalog_path=catalog_path,
        ingestion_repo_path=tmp_path / "ingestion",
        transformation_repo_path=tmp_path / "transformation",
        quality_repo_path=tmp_path / "quality",
        workspace_dir=workspace_dir
    )
    
    import unittest
    with unittest.TestCase().assertRaisesRegex(ValueError, "Unsupported resource: unsupported-resource"):
        workflow.run(resource="unsupported-resource")

def test_weather_mvp_workflow_all_resources(tmp_path):
    catalog_path = tmp_path / "catalog"
    workspace_dir = tmp_path / "workspace"
    
    mock_executor = MagicMock()
    
    workflow = WeatherMVPWorkflow(
        catalog_path=catalog_path,
        ingestion_repo_path=tmp_path / "ingestion",
        transformation_repo_path=tmp_path / "transformation",
        quality_repo_path=tmp_path / "quality",
        workspace_dir=workspace_dir,
        executor=mock_executor
    )

    def side_effect(step_name, command):
        if "ingestion" in step_name:
            landing_file = workflow.run_dir / "landing/sample.json"
            landing_file.parent.mkdir(parents=True, exist_ok=True)
            landing_file.touch()
        elif "transformation-silver" in step_name:
            # We need to simulate the scoped paths for all resources
            # stations-metadata -> stations
            # variables-metadata -> variables
            # measured-variable -> measurements
            entity = "stations"
            if "variables-metadata" in step_name:
                entity = "variables"
            if "measured-variable" in step_name:
                entity = "measurements"
            
            silver_file = workflow.run_dir / f"silver/silver/weather/meteocat/{entity}/records.jsonl"
            silver_file.parent.mkdir(parents=True, exist_ok=True)
            silver_file.touch()
        elif "transformation" in step_name:
            resource = "stations-metadata"
            if "variables-metadata" in step_name:
                resource = "variables-metadata"
            if "measured-variable" in step_name:
                resource = "measured-variable"
            
            bronze_file = workflow.run_dir / f"bronze/bronze/weather/meteocat/{resource}/records.jsonl"
            bronze_file.parent.mkdir(parents=True, exist_ok=True)
            bronze_file.touch()
            
        return RunStepResult(
            step_name=step_name,
            command=command,
            return_code=0,
            stdout="",
            stderr="",
            status="SUCCESS",
            started_at=datetime.now(),
            finished_at=datetime.now()
        )

    mock_executor.run_command.side_effect = side_effect
    
    summary = workflow.run(resource="all")
    
    assert summary.status == "SUCCESS"
    assert summary.resource == "all"
    # 3 resources * 6 steps = 18 steps
    assert len(summary.steps) == 18
    # 18 steps, but only ingestion, transformation, transformation-silver add unique artifacts.
    # landing/sample.json is shared (3 times but same path)
    # bronze/resource/records.jsonl (3 unique)
    # silver/entity/records.jsonl (3 unique)
    # 1 (landing) + 3 (bronze) + 3 (silver) + 1 (summary) = 8 unique artifact paths
    assert len(set(summary.artifacts)) == 8
    
    # Check step names
    assert summary.steps[0].step_name == "stations-metadata:ingestion"
    assert summary.steps[6].step_name == "variables-metadata:ingestion"
    assert summary.steps[12].step_name == "measured-variable:ingestion"

def test_weather_mvp_workflow_failure(tmp_path):
    catalog_path = tmp_path / "catalog"
    ingestion_repo_path = tmp_path / "ingestion"
    transformation_repo_path = tmp_path / "transformation"
    quality_repo_path = tmp_path / "quality"
    workspace_dir = tmp_path / "workspace"
    
    mock_executor = MagicMock()
    
    failed_result = RunStepResult(
        step_name="ingestion",
        command=[],
        return_code=1,
        stdout="",
        stderr="Ingestion failed",
        status="FAILED",
        started_at=datetime.now(),
        finished_at=datetime.now()
    )
    mock_executor.run_command.return_value = failed_result
    
    workflow = WeatherMVPWorkflow(
        catalog_path=catalog_path,
        ingestion_repo_path=ingestion_repo_path,
        transformation_repo_path=transformation_repo_path,
        quality_repo_path=quality_repo_path,
        workspace_dir=workspace_dir,
        executor=mock_executor
    )
    
    summary = workflow.run()
    
    assert summary.status == "FAILED"
    assert len(summary.steps) == 1
    assert summary.steps[0].step_name == "ingestion"
