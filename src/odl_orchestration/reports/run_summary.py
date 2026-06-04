from pathlib import Path
from odl_orchestration.models.run import RunSummary
from odl_orchestration.utils.paths import ensure_dir

def write_run_summary(summary: RunSummary, output_dir: Path) -> Path:
    """Writes the run summary to a JSON file."""
    ensure_dir(output_dir)
    output_path = output_dir / "run-summary.json"
    
    with open(output_path, "w") as f:
        # Use Pydantic's model_dump_json for proper serialization of datetimes
        f.write(summary.model_dump_json(indent=2))
        
    return output_path
