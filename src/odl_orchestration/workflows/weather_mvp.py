from datetime import datetime
from pathlib import Path
from typing import Optional, List

from odl_orchestration.models.run import RunSummary, RunStepResult
from odl_orchestration.executors.subprocess_executor import SubprocessExecutor
from odl_orchestration.utils.dates import get_timestamp_id
from odl_orchestration.utils.paths import ensure_dir, find_file_by_pattern
from odl_orchestration.reports.run_summary import write_run_summary

class WeatherMVPWorkflow:
    def __init__(
        self,
        catalog_path: Path,
        ingestion_repo_path: Path,
        transformation_repo_path: Path,
        quality_repo_path: Path,
        workspace_dir: Path,
        executor: Optional[SubprocessExecutor] = None
    ):
        self.catalog_path = catalog_path
        self.ingestion_repo_path = ingestion_repo_path
        self.transformation_repo_path = transformation_repo_path
        self.quality_repo_path = quality_repo_path
        self.workspace_dir = workspace_dir
        self.executor = executor or SubprocessExecutor()
        self.run_id = get_timestamp_id()
        self.run_dir = workspace_dir / "runs" / self.run_id
        
    def run(self, dataset_id: str = "meteocat-weather", resource: str = "stations-metadata") -> RunSummary:
        started_at = datetime.now()
        steps: List[RunStepResult] = []
        artifacts: List[str] = []
        status = "SUCCESS"
        
        # Resource to Silver entity mapping
        mapping = {
            "stations-metadata": "stations",
            "variables-metadata": "variables",
            "measured-variable": "measurements"
        }
        
        if resource not in mapping:
            raise ValueError(f"Unsupported resource for Silver mapping: {resource}")
            
        silver_entity = mapping[resource]

        landing_dir = self.run_dir / "landing"
        bronze_dir = self.run_dir / "bronze"
        silver_dir = self.run_dir / "silver"
        reports_dir = self.run_dir / "reports"
        
        ensure_dir(landing_dir)
        ensure_dir(bronze_dir)
        ensure_dir(silver_dir)
        ensure_dir(reports_dir)
        
        # Write ingestion
        ingest_cmd = [
            "odl-ingestion", "ingest",
            "--dataset", dataset_id,
            "--catalog-path", str(self.catalog_path),
            "--target", "local",
            "--output-dir", str(landing_dir),
            "--mode", "sample"
        ]
        
        step_result = self.executor.run_command("ingestion", ingest_cmd)
        steps.append(step_result)
        
        if step_result.status != "SUCCESS":
            status = "FAILED"
        else:
            # Discover landing file
            landing_file = find_file_by_pattern(landing_dir, "sample.json")
            if not landing_file:
                step_result.status = "FAILED"
                step_result.stderr += "\nLanding file sample.json not found."
                status = "FAILED"
            else:
                artifacts.append(str(landing_file))
                
        # Write landing quality
                quality_landing_cmd = [
                    "odl-quality", "check", "landing",
                    "--dataset", dataset_id,
                    "--resource", resource,
                    "--input-path", str(landing_file)
                ]
                step_result = self.executor.run_command("quality-landing", quality_landing_cmd)
                steps.append(step_result)
                
                if step_result.status != "SUCCESS":
                    status = "FAILED"
                else:
                # Write bronze transformation
                    transform_cmd = [
                        "odl-transformation", "transform",
                        "--dataset", dataset_id,
                        "--resource", resource,
                        "--input-path", str(landing_file),
                        "--output-dir", str(bronze_dir)
                    ]
                    step_result = self.executor.run_command("transformation", transform_cmd)
                    steps.append(step_result)
                    
                    if step_result.status != "SUCCESS":
                        status = "FAILED"
                    else:
                        # Discover bronze file
                        bronze_file = find_file_by_pattern(bronze_dir, "records.jsonl")
                        if not bronze_file:
                            step_result.status = "FAILED"
                            step_result.stderr += "\nBronze file records.jsonl not found."
                            status = "FAILED"
                        else:
                            artifacts.append(str(bronze_file))
                            
                            # Write bronze quality
                            quality_bronze_cmd = [
                                "odl-quality", "check", "bronze",
                                "--dataset", dataset_id,
                                "--resource", resource,
                                "--input-path", str(bronze_file)
                            ]
                            step_result = self.executor.run_command("quality-bronze", quality_bronze_cmd)
                            steps.append(step_result)
                            
                            if step_result.status != "SUCCESS":
                                status = "FAILED"
                            else:
                                # Write silver transformation
                                transform_silver_cmd = [
                                    "odl-transformation", "transform-silver",
                                    "--dataset", dataset_id,
                                    "--resource", resource,
                                    "--input-path", str(bronze_file),
                                    "--output-dir", str(silver_dir)
                                ]
                                step_result = self.executor.run_command("transformation-silver", transform_silver_cmd)
                                steps.append(step_result)

                                if step_result.status != "SUCCESS":
                                    status = "FAILED"
                                else:
                                    # Discover silver file
                                    silver_file = find_file_by_pattern(silver_dir, "records.jsonl")
                                    if not silver_file:
                                        step_result.status = "FAILED"
                                        step_result.stderr += "\nSilver file records.jsonl not found."
                                        status = "FAILED"
                                    else:
                                        artifacts.append(str(silver_file))

                                        # Write silver quality
                                        quality_silver_cmd = [
                                            "odl-quality", "check", "silver",
                                            "--dataset", dataset_id,
                                            "--entity", silver_entity,
                                            "--input-path", str(silver_file)
                                        ]
                                        step_result = self.executor.run_command("quality-silver", quality_silver_cmd)
                                        steps.append(step_result)

                                        if step_result.status != "SUCCESS":
                                            status = "FAILED"
        
        finished_at = datetime.now()
        
        summary = RunSummary(
            run_id=self.run_id,
            workflow_name="weather-mvp-local",
            dataset_id=dataset_id,
            resource=resource,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            steps=steps,
            artifacts=artifacts
        )
        
        # Write run summary
        summary_path = write_run_summary(summary, reports_dir)
        summary.artifacts.append(str(summary_path))
        
        return summary
