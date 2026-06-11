# Run Workspace

The orchestration tool manages a dedicated workspace for workflow executions.

## Structure

```text
<workspace-dir>/
  runs/
    <run-id>/
      landing/
      bronze/
      silver/
      reports/
        run-summary.json
```

## Components

- **`<run-id>`**: A unique identifier for each run, typically based on a timestamp (`YYYYMMDD-HHMMSS`).
- **`landing/`**: Contains the raw data files produced by the ingestion step. Depending on the ingestion mode and resource, it may contain `sample.json`, `<resource>.json`, `stations-metadata.json`, `variables-metadata.json`, or `measured-variable.json`.
- **`bronze/`**: Contains the transformed records in JSONL format from landing. Files are organized by resource: `bronze/weather/meteocat/<resource>/.../records.jsonl`.
- **`silver/`**: Contains the transformed records in JSONL format from bronze. Files are organized by entity: `silver/weather/meteocat/<entity>/.../records.jsonl`.
- **`reports/`**: Contains the execution summary and any other generated reports.

## Artifacts

All generated files are considered artifacts and their paths are recorded in the `run-summary.json` file.
