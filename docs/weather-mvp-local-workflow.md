# Weather MVP Local Workflow

The Weather MVP local workflow coordinates the ingestion, quality validation, and transformation of weather data from Meteocat.

## Workflow Steps

1.  **Ingestion (Sample Mode)**: Runs `odl-ingestion` to fetch sample data for a specific dataset (e.g., `meteocat-weather`) and resource (e.g., `stations-metadata`).
2.  **Quality Landing**: Runs `odl-quality` to validate the generated landing JSON file.
3.  **Transformation**: Runs `odl-transformation` to transform the landing JSON file into bronze JSONL records.
4.  **Quality Bronze**: Runs `odl-quality` to validate the generated bronze JSONL records.
5.  **Run Summary**: Generates a final execution report.

The workflow coordinates these steps by executing the corresponding CLI commands. This requires that `odl-ingestion`, `odl-transformation`, and `odl-quality` are installed in the environment. The paths to these repositories are passed as arguments to the workflow to provide local execution context.

## Execution Flow

```text
ingestion sample -> landing quality -> transformation -> bronze quality
```

## Offline Mode

The workflow is designed to run in a sample/offline mode, meaning it does not require real API keys or network access, as it uses sample data provided by the ingestion component.
