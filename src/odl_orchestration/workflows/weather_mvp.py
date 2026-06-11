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
        mode: str = "sample",
        use_contracts: bool = False,
        executor: Optional[SubprocessExecutor] = None
    ):
        self.catalog_path = catalog_path
        self.ingestion_repo_path = ingestion_repo_path
        self.transformation_repo_path = transformation_repo_path
        self.quality_repo_path = quality_repo_path
        self.workspace_dir = workspace_dir
        self.mode = mode
        self.use_contracts = use_contracts
        self.executor = executor or SubprocessExecutor()
        self.run_id = get_timestamp_id()
        self.run_dir = workspace_dir / "runs" / self.run_id
        
    def run(self, dataset_id: str = "meteocat-weather", resource: str = "stations-metadata") -> RunSummary:
        started_at = datetime.now()
        steps: List[RunStepResult] = []
        artifacts: List[str] = []
        
        # Mapping definition
        mapping = {
            "stations-metadata": "stations",
            "variables-metadata": "variables",
            "measured-variable": "measurements"
        }
        
        resources_to_run = []
        if resource == "all":
            resources_to_run = ["stations-metadata", "variables-metadata", "measured-variable"]
        else:
            if resource not in mapping:
                raise ValueError(f"Unsupported resource: {resource}")
            resources_to_run = [resource]
            
        status = "SUCCESS"
        
        landing_dir = self.run_dir / "landing"
        bronze_dir = self.run_dir / "bronze"
        silver_dir = self.run_dir / "silver"
        reports_dir = self.run_dir / "reports"
        
        ensure_dir(landing_dir)
        ensure_dir(bronze_dir)
        ensure_dir(silver_dir)
        ensure_dir(reports_dir)
        
        for res in resources_to_run:
            silver_entity = mapping[res]
            # In all mode, we use resource-specific step names
            step_prefix = f"{res}:" if resource == "all" else ""
            
            res_status, res_steps, res_artifacts = self._run_resource(
                dataset_id=dataset_id,
                resource=res,
                silver_entity=silver_entity,
                landing_dir=landing_dir,
                bronze_dir=bronze_dir,
                silver_dir=silver_dir,
                step_prefix=step_prefix
            )
            
            steps.extend(res_steps)
            artifacts.extend(res_artifacts)
            
            if res_status != "SUCCESS":
                status = "FAILED"
                break
        
        finished_at = datetime.now()
        
        summary = RunSummary(
            run_id=self.run_id,
            workflow_name="weather-mvp-local",
            dataset_id=dataset_id,
            resource=resource,
            mode=self.mode,
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

    def _run_resource(
        self,
        dataset_id: str,
        resource: str,
        silver_entity: str,
        landing_dir: Path,
        bronze_dir: Path,
        silver_dir: Path,
        step_prefix: str = ""
    ) -> tuple[str, List[RunStepResult], List[str]]:
        steps: List[RunStepResult] = []
        artifacts: List[str] = []
        
        # 1. Ingestion
        ingest_cmd = [
            "odl-ingestion", "ingest",
            "--dataset", dataset_id,
            "--catalog-path", str(self.catalog_path),
            "--target", "local",
            "--output-dir", str(landing_dir),
            "--mode", self.mode
        ]

        if self.mode == "real":
            ingest_cmd.extend(["--meteocat-resource", resource])
        
        step_result = self.executor.run_command(f"{step_prefix}ingestion", ingest_cmd)
        steps.append(step_result)
        
        if step_result.status != "SUCCESS":
            return "FAILED", steps, artifacts

        # Discover landing file
        # Preferred behavior: <resource>.json, then sample.json, then fallback to any .json
        landing_file_patterns = [
            f"{resource}.json",
            "sample.json",
            "*.json"
        ]
        
        landing_file = None
        for pattern in landing_file_patterns:
            landing_file = find_file_by_pattern(landing_dir, pattern)
            if landing_file:
                break
        
        if not landing_file:
            step_result.status = "FAILED"
            step_result.stderr += f"\nLanding file for {resource} not found (searched {landing_file_patterns})."
            return "FAILED", steps, artifacts
        
        artifacts.append(str(landing_file))
                
        # 2. Quality Landing
        quality_landing_cmd = [
            "odl-quality", "check", "landing",
            "--dataset", dataset_id,
            "--resource", resource,
            "--input-path", str(landing_file)
        ]
        
        if self.use_contracts:
            quality_landing_cmd.extend([
                "--catalog-path", str(self.catalog_path),
                "--use-contract"
            ])
            
        step_result = self.executor.run_command(f"{step_prefix}quality-landing", quality_landing_cmd)
        steps.append(step_result)
        
        if step_result.status != "SUCCESS":
            return "FAILED", steps, artifacts
            
        # 3. Transformation (Bronze)
        transform_cmd = [
            "odl-transformation", "transform",
            "--dataset", dataset_id,
            "--resource", resource,
            "--input-path", str(landing_file),
            "--output-dir", str(bronze_dir)
        ]
        step_result = self.executor.run_command(f"{step_prefix}transformation", transform_cmd)
        steps.append(step_result)
        
        if step_result.status != "SUCCESS":
            return "FAILED", steps, artifacts

        # Discover bronze file - scoped to resource
        # We need to account for both records.jsonl and <resource>.jsonl if ingestion changed it,
        # but for now transformation still outputs records.jsonl.
        bronze_file = find_file_by_pattern(bronze_dir / "bronze" / "weather" / "meteocat" / resource, "records.jsonl")
        if not bronze_file:
            # Fallback for compatibility if structure is different than expected
            bronze_file = find_file_by_pattern(bronze_dir, "records.jsonl")
            
        if not bronze_file:
            step_result.status = "FAILED"
            step_result.stderr += f"\nBronze file for {resource} not found."
            return "FAILED", steps, artifacts
        
        artifacts.append(str(bronze_file))
        
        # 4. Quality Bronze
        quality_bronze_cmd = [
            "odl-quality", "check", "bronze",
            "--dataset", dataset_id,
            "--resource", resource,
            "--input-path", str(bronze_file)
        ]
        step_result = self.executor.run_command(f"{step_prefix}quality-bronze", quality_bronze_cmd)
        steps.append(step_result)
        
        if step_result.status != "SUCCESS":
            return "FAILED", steps, artifacts
            
        # 5. Transformation Silver
        transform_silver_cmd = [
            "odl-transformation", "transform-silver",
            "--dataset", dataset_id,
            "--resource", resource,
            "--input-path", str(bronze_file),
            "--output-dir", str(silver_dir)
        ]
        step_result = self.executor.run_command(f"{step_prefix}transformation-silver", transform_silver_cmd)
        steps.append(step_result)

        if step_result.status != "SUCCESS":
            return "FAILED", steps, artifacts

        # Discover silver file - scoped to entity
        silver_file = find_file_by_pattern(silver_dir / "silver" / "weather" / "meteocat" / silver_entity, "records.jsonl")
        if not silver_file:
            # Fallback
            silver_file = find_file_by_pattern(silver_dir, "records.jsonl")
            
        if not silver_file:
            step_result.status = "FAILED"
            step_result.stderr += f"\nSilver file for {silver_entity} not found."
            return "FAILED", steps, artifacts
        
        artifacts.append(str(silver_file))

        # 6. Quality Silver
        quality_silver_cmd = [
            "odl-quality", "check", "silver",
            "--dataset", dataset_id,
            "--entity", silver_entity,
            "--input-path", str(silver_file)
        ]
        step_result = self.executor.run_command(f"{step_prefix}quality-silver", quality_silver_cmd)
        steps.append(step_result)

        if step_result.status != "SUCCESS":
            return "FAILED", steps, artifacts
            
        return "SUCCESS", steps, artifacts
