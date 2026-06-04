import json
from datetime import datetime
from odl_orchestration.models.run import RunSummary, RunStepResult
from odl_orchestration.reports.run_summary import write_run_summary

def test_write_run_summary(tmp_path):
    summary = RunSummary(
        run_id="test-run",
        workflow_name="test-workflow",
        dataset_id="test-dataset",
        resource="test-resource",
        status="SUCCESS",
        started_at=datetime.now(),
        finished_at=datetime.now(),
        steps=[
            RunStepResult(
                step_name="step1",
                command=["cmd1"],
                return_code=0,
                stdout="out",
                stderr="",
                status="SUCCESS",
                started_at=datetime.now(),
                finished_at=datetime.now()
            )
        ],
        artifacts=["file1"]
    )
    
    output_dir = tmp_path / "reports"
    summary_path = write_run_summary(summary, output_dir)
    
    assert summary_path.exists()
    assert summary_path.name == "run-summary.json"
    
    with open(summary_path, "r") as f:
        data = json.load(f)
        assert data["run_id"] == "test-run"
        assert data["workflow_name"] == "test-workflow"
        assert len(data["steps"]) == 1
        assert data["steps"][0]["step_name"] == "step1"
