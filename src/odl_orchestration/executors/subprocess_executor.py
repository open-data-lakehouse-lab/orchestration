import subprocess
from datetime import datetime
from typing import List
from odl_orchestration.models.run import RunStepResult

class SubprocessExecutor:
    def run_command(self, step_name: str, command: List[str]) -> RunStepResult:
        started_at = datetime.now()
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False
            )
            finished_at = datetime.now()
            status = "SUCCESS" if result.returncode == 0 else "FAILED"
            
            return RunStepResult(
                step_name=step_name,
                command=command,
                return_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                status=status,
                started_at=started_at,
                finished_at=finished_at
            )
        except Exception as e:
            finished_at = datetime.now()
            return RunStepResult(
                step_name=step_name,
                command=command,
                return_code=-1,
                stdout="",
                stderr=str(e),
                status="FAILED",
                started_at=started_at,
                finished_at=finished_at
            )
