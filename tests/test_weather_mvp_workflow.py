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
    assert summary.mode == "sample"
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

def test_weather_mvp_workflow_use_contracts(tmp_path):
    catalog_path = tmp_path / "catalog"
    workspace_dir = tmp_path / "workspace"
    
    mock_executor = MagicMock()
    
    def side_effect(step_name, command):
        if "ingestion" in step_name:
            landing_file = workflow.run_dir / "landing/sample.json"
            landing_file.parent.mkdir(parents=True, exist_ok=True)
            landing_file.touch()
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

    # Test with use_contracts=True
    workflow = WeatherMVPWorkflow(
        catalog_path=catalog_path,
        ingestion_repo_path=tmp_path / "ingestion",
        transformation_repo_path=tmp_path / "transformation",
        quality_repo_path=tmp_path / "quality",
        workspace_dir=workspace_dir,
        use_contracts=True,
        executor=mock_executor
    )
    
    workflow.run(resource="stations-metadata")
    
    quality_landing_call = [call for call in mock_executor.run_command.call_args_list if call[0][0] == "quality-landing"][0]
    cmd = quality_landing_call[0][1]
    assert "--catalog-path" in cmd
    assert str(catalog_path) in cmd
    assert "--use-contract" in cmd

    # Test with use_contracts=False
    mock_executor.run_command.reset_mock()
    workflow = WeatherMVPWorkflow(
        catalog_path=catalog_path,
        ingestion_repo_path=tmp_path / "ingestion",
        transformation_repo_path=tmp_path / "transformation",
        quality_repo_path=tmp_path / "quality",
        workspace_dir=workspace_dir,
        use_contracts=False,
        executor=mock_executor
    )
    
    workflow.run(resource="stations-metadata")
    
    quality_landing_call = [call for call in mock_executor.run_command.call_args_list if call[0][0] == "quality-landing"][0]
    cmd = quality_landing_call[0][1]
    assert "--catalog-path" not in cmd
    assert "--use-contract" not in cmd

def test_weather_mvp_workflow_all_resources_use_contracts(tmp_path):
    catalog_path = tmp_path / "catalog"
    workspace_dir = tmp_path / "workspace"
    
    mock_executor = MagicMock()
    
    def side_effect(step_name, command):
        if "ingestion" in step_name:
            landing_file = workflow.run_dir / "landing/sample.json"
            landing_file.parent.mkdir(parents=True, exist_ok=True)
            landing_file.touch()
        elif "transformation-silver" in step_name:
            entity = "stations"
            if "variables-metadata" in step_name:
                entity = "variables"
            elif "measured-variable" in step_name:
                entity = "measurements"

            silver_file = workflow.run_dir / f"silver/silver/weather/meteocat/{entity}/records.jsonl"
            silver_file.parent.mkdir(parents=True, exist_ok=True)
            silver_file.touch()
        elif "transformation" in step_name:
            resource = "stations-metadata"
            if "variables-metadata" in step_name:
                resource = "variables-metadata"
            elif "measured-variable" in step_name:
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

    workflow = WeatherMVPWorkflow(
        catalog_path=catalog_path,
        ingestion_repo_path=tmp_path / "ingestion",
        transformation_repo_path=tmp_path / "transformation",
        quality_repo_path=tmp_path / "quality",
        workspace_dir=workspace_dir,
        use_contracts=True,
        executor=mock_executor
    )
    
    workflow.run(resource="all")
    
    quality_landing_calls = [call for call in mock_executor.run_command.call_args_list if "quality-landing" in call[0][0]]
    assert len(quality_landing_calls) == 3
    for call in quality_landing_calls:
        cmd = call[0][1]
        assert "--catalog-path" in cmd
        assert str(catalog_path) in cmd
        assert "--use-contract" in cmd

def test_weather_mvp_workflow_modes(tmp_path):
    catalog_path = tmp_path / "catalog"
    workspace_dir = tmp_path / "workspace"
    mock_executor = MagicMock()
    
    def side_effect(step_name, command):
        # Determine resource from command if real, or default to stations-metadata
        res = "stations-metadata"
        if "--meteocat-resource" in command:
            res = command[command.index("--meteocat-resource") + 1]
            
        if "ingestion" in step_name:
            # Create a file that matches what we expect
            # Real mode might write <resource>.json
            landing_file = workflow.run_dir / f"landing/{res}.json"
            landing_file.parent.mkdir(parents=True, exist_ok=True)
            landing_file.touch()
        elif "transformation" in step_name and "transformation-silver" not in step_name:
            bronze_file = workflow.run_dir / "bronze/records.jsonl"
            bronze_file.parent.mkdir(parents=True, exist_ok=True)
            bronze_file.touch()
        elif "transformation-silver" in step_name:
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

    # 1. Test real mode single resource
    workflow = WeatherMVPWorkflow(
        catalog_path=catalog_path,
        ingestion_repo_path=tmp_path / "ingestion",
        transformation_repo_path=tmp_path / "transformation",
        quality_repo_path=tmp_path / "quality",
        workspace_dir=workspace_dir,
        mode="real",
        executor=mock_executor
    )
    
    summary = workflow.run(resource="variables-metadata")
    assert summary.status == "SUCCESS"
    assert summary.mode == "real"
    
    ingest_call = [call for call in mock_executor.run_command.call_args_list if "ingestion" in call[0][0]][0]
    cmd = ingest_call[0][1]
    assert "--mode" in cmd
    assert "real" in cmd
    assert "--meteocat-resource" in cmd
    assert "variables-metadata" in cmd

    # 2. Test real mode all resources
    mock_executor.run_command.reset_mock()
    summary = workflow.run(resource="all")
    assert summary.status == "SUCCESS"
    assert summary.mode == "real"
    
    ingest_calls = [call for call in mock_executor.run_command.call_args_list if "ingestion" in call[0][0]]
    assert len(ingest_calls) == 3
    
    resources = ["stations-metadata", "variables-metadata", "measured-variable"]
    for i, res in enumerate(resources):
        cmd = ingest_calls[i][0][1]
        assert "--mode" in cmd
        assert "real" in cmd
        assert "--meteocat-resource" in cmd
        assert res in cmd

    # 3. Test artifact discovery with sample.json in real mode (fallback)
    # We create a NEW workflow with a unique workspace to ensure clean state
    mock_executor.run_command.reset_mock()
    workspace_dir_sample = tmp_path / "workspace_sample"
    workflow_sample = WeatherMVPWorkflow(
        catalog_path=catalog_path,
        ingestion_repo_path=tmp_path / "ingestion",
        transformation_repo_path=tmp_path / "transformation",
        quality_repo_path=tmp_path / "quality",
        workspace_dir=workspace_dir_sample,
        mode="real",
        executor=mock_executor
    )
    
    def side_effect_sample(step_name, command):
        if "ingestion" in step_name:
            landing_file = workflow_sample.run_dir / "landing/sample.json"
            landing_file.parent.mkdir(parents=True, exist_ok=True)
            landing_file.touch()
        elif "transformation" in step_name and "transformation-silver" not in step_name:
            bronze_file = workflow_sample.run_dir / "bronze/records.jsonl"
            bronze_file.parent.mkdir(parents=True, exist_ok=True)
            bronze_file.touch()
        elif "transformation-silver" in step_name:
            silver_file = workflow_sample.run_dir / "silver/records.jsonl"
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
    mock_executor.run_command.side_effect = side_effect_sample
    
    summary = workflow_sample.run(resource="stations-metadata")
    assert summary.status == "SUCCESS"
    assert any("sample.json" in art for art in summary.artifacts)

def test_weather_mvp_workflow_artifact_fallback(tmp_path):
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
            # Create a generic file that should be picked up by *.json fallback
            landing_file = workflow.run_dir / "landing/any-file.json"
            landing_file.parent.mkdir(parents=True, exist_ok=True)
            landing_file.touch()
        elif "transformation" in step_name and "transformation-silver" not in step_name:
            bronze_file = workflow.run_dir / "bronze/records.jsonl"
            bronze_file.parent.mkdir(parents=True, exist_ok=True)
            bronze_file.touch()
        elif "transformation-silver" in step_name:
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
    
    summary = workflow.run(resource="stations-metadata")
    assert summary.status == "SUCCESS"
    assert any("any-file.json" in art for art in summary.artifacts)
