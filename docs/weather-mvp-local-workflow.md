# Weather MVP Local Workflow

The Weather MVP local workflow coordinates the ingestion, quality validation, and transformation of weather data from Meteocat.

## Supported Resources and Entities

The workflow supports the following resource-to-entity mappings:

- `stations-metadata` -> `stations`
- `variables-metadata` -> `variables`
- `measured-variable` -> `measurements`

## CLI Usage

The workflow can be run for a single resource or all resources:

```bash
# Single resource
odl-orchestration run weather-mvp-local --resource stations-metadata

# All resources (sequential)
odl-orchestration run weather-mvp-local --resource all
```

## Workflow Steps

1.  **Ingestion (Sample Mode)**: Runs `odl-ingestion` to fetch sample data for a specific dataset (e.g., `meteocat-weather`) and resource (e.g., `stations-metadata`).
2.  **Quality Landing**: Runs `odl-quality` to validate the generated landing JSON file.
3.  **Bronze Transformation**: Runs `odl-transformation transform` to transform the landing JSON file into bronze JSONL records.
4.  **Quality Bronze**: Runs `odl-quality check bronze` to validate the generated bronze JSONL records.
5.  **Silver Transformation**: Runs `odl-transformation transform-silver` to transform the bronze JSONL records into silver JSONL records.
6.  **Quality Silver**: Runs `odl-quality check silver` to validate the generated silver JSONL records.
7.  **Run Summary**: Generates a final execution report.

The workflow coordinates these steps by executing the corresponding CLI commands. This requires that `odl-ingestion`, `odl-transformation`, and `odl-quality` are installed in the environment. The paths to these repositories are passed as arguments to the workflow to provide local execution context.

## Execution Flow

```text
ingestion sample -> landing quality -> bronze transformation -> bronze quality -> silver transformation -> silver quality
```

## Offline Mode and Limitations

The workflow is designed to run in a sample/offline mode, meaning it does not require real API keys or network access, as it uses sample data provided by the ingestion component.

Current limitations:
- **Sample Ingestion**: Sample/offline ingestion may still use simple sample payloads and does not guarantee real source-specific data semantics for all resources yet.
- **Sequential Execution**: In `all` mode, resources are processed sequentially.
- **JSONL Foundation**: Silver remains a local JSONL foundation, not a final analytics model.
- **No Parquet**: This implementation does not use or produce Parquet files.
