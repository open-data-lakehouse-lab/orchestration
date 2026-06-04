# Run Workspace

The orchestration tool manages a dedicated workspace for workflow executions.

## Structure

```text
<workspace-dir>/
  runs/
    <run-id>/
      landing/
      bronze/
      reports/
        run-summary.json
```

## Components

- **`<run-id>`**: A unique identifier for each run, typically based on a timestamp (`YYYYMMDD-HHMMSS`).
- **`landing/`**: Contains the raw data files produced by the ingestion step.
- **`bronze/`**: Contains the transformed records in JSONL format.
- **`reports/`**: Contains the execution summary and any other generated reports.

## Artifacts

All generated files are considered artifacts and their paths are recorded in the `run-summary.json` file.
