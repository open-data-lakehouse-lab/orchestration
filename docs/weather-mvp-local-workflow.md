# Weather MVP Local Workflow

The Weather MVP local workflow coordinates the ingestion, quality validation, and transformation of weather data from Meteocat.

## Supported Resources and Entities

The workflow supports the following resource-to-entity mappings:

- `stations-metadata` -> `stations`
- `variables-metadata` -> `variables`
- `measured-variable` -> `measurements`

## CLI Usage

The workflow can be run for a single resource or all resources, using either sample (offline) or real ingestion mode:

```bash
# Single resource (sample mode by default)
odl-orchestration run weather-mvp-local --resource stations-metadata

# All resources (real mode)
odl-orchestration run weather-mvp-local --resource all --mode real
```

## Workflow Steps

1.  **Ingestion**: Runs `odl-ingestion` to fetch data for a specific dataset (e.g., `meteocat-weather`) and resource (e.g., `stations-metadata`). It uses either `--mode sample` (offline) or `--mode real` (Meteocat API).
2.  **Quality Landing**: Runs `odl-quality` to validate the generated landing JSON file. If `--use-contracts` is enabled, it also performs contract/schema validation using `datasets-catalog`.
3.  **Bronze Transformation**: Runs `odl-transformation transform` to transform the landing JSON file into bronze JSONL records.
4.  **Quality Bronze**: Runs `odl-quality check bronze` to validate the generated bronze JSONL records.
5.  **Silver Transformation**: Runs `odl-transformation transform-silver` to transform the bronze JSONL records into silver JSONL records.
6.  **Quality Silver**: Runs `odl-quality check silver` to validate the generated silver JSONL records.
7.  **Run Summary**: Generates a final execution report.

The workflow coordinates these steps by executing the corresponding CLI commands. This requires that `odl-ingestion`, `odl-transformation`, and `odl-quality` are installed in the environment. The paths to these repositories are passed as arguments to the workflow to provide local execution context.

## Execution Flow

```text
ingestion (sample|real) -> landing quality -> bronze transformation -> bronze quality -> silver transformation -> silver quality
```

## Ingestion Modes

The workflow supports two ingestion modes via the `--mode` flag:

- **sample** (default/offline): Uses local sample files provided by the ingestion component. Does not require network access or real API keys.
- **real**: Calls the upstream Meteocat API via `odl-ingestion`. This mode requires `METEOCAT_API_KEY` to be set in the environment where the ingestion CLI executes. Orchestration coordinates the run but does not manage or store secrets.

## Optional Landing Contract Validation

The workflow supports optional landing contract/schema validation using `datasets-catalog` contracts. This is an opt-in feature enabled by the `--use-contracts` flag.

```bash
odl-orchestration run weather-mvp-local --resource all --use-contracts
```

When enabled, the `Quality Landing` step includes the `--catalog-path` and `--use-contract` flags when calling `odl-quality`.

## Offline and Real Mode Limitations

- **Sample Ingestion**: Sample/offline ingestion may still use simple sample payloads and does not guarantee real source-specific data semantics for all resources yet.
- **Real Mode**: Real mode depends on the availability of the Meteocat API and a valid API key. If the key is missing, ingestion will fail clearly, and orchestration will report the failure.
- **Sequential Execution**: In `all` mode, resources are processed sequentially.
- **JSONL Foundation**: Silver remains a local JSONL foundation, not a final analytics model.
- **No Parquet**: This implementation does not use or produce Parquet files.
