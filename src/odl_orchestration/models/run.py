from datetime import datetime
from typing import List
from pydantic import BaseModel, Field

class RunStepResult(BaseModel):
    step_name: str
    command: List[str]
    return_code: int
    stdout: str
    stderr: str
    status: str
    started_at: datetime
    finished_at: datetime

class RunSummary(BaseModel):
    run_id: str
    workflow_name: str
    dataset_id: str
    resource: str
    status: str
    started_at: datetime
    finished_at: datetime
    steps: List[RunStepResult] = Field(default_factory=list)
    artifacts: List[str] = Field(default_factory=list)
