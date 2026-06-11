# Orchestration Design

The `orchestration` repository is responsible for local workflow execution in the Open Data Lakehouse Lab project.

## Local-first orchestration

The current implementation focuses on a lightweight, local-first orchestration approach. It coordinates the execution of different components (ingestion, transformation, quality) that are available as sibling repositories.

## CLI-based coordination

Orchestration is achieved by calling the Command Line Interfaces (CLIs) of the sibling repositories using a subprocess executor. This keeps the orchestration layer independent of the internal implementation details of each component.

The sibling repositories (`odl-ingestion`, `odl-transformation`, `odl-quality`) must be installed in editable mode within the same environment so their CLI commands are reachable.

## Sibling Repository Paths

The workflow accepts paths to sibling repositories as arguments. In the current implementation, these paths serve as local context and reference. The actual execution relies on the CLIs installed in the environment. This design allows for future enhancements where the paths could be used for direct module discovery, stronger validation, or configuration overrides.

## Weather MVP Workflow

The Weather MVP workflow currently supports multiple resources:
- `stations-metadata`
- `variables-metadata`
- `measured-variable`

It also provides an `all` mode that runs these three resources sequentially.

## Ingestion Modes

The workflow supports two ingestion modes:

- **sample** (default): Uses local sample data files provided by the ingestion component. This is the default mode and requires no network or API keys.
- **real**: Calls the upstream Meteocat API via the ingestion component. This mode requires a `METEOCAT_API_KEY` to be present in the environment where the ingestion CLI is executed.

Orchestration is responsible for passing the correct mode and resource-specific parameters to the ingestion component.

### Per-resource steps
For each resource, the workflow executes:
1. `ingestion`
2. `quality-landing` (optionally including contract validation if `--use-contracts` is enabled)
3. `transformation` (Bronze)
4. `quality-bronze`
5. `transformation-silver`
6. `quality-silver`

In `all` mode, step names are prefixed with the resource name (e.g., `stations-metadata:ingestion`) to ensure uniqueness in the run summary.

## Run Workspace

Each workflow run produces a dedicated workspace directory. This workspace contains:
- `landing/`: Data ingested from source (sample mode).
- `bronze/`: Data transformed to bronze format.
- `silver/`: Data transformed to silver format.
- `reports/`: Run summaries and other execution reports.

## Run Summaries

At the end of each run, a `run-summary.json` file is produced. It contains detailed information about the execution, including the status of each step, start and end times, and paths to generated artifacts.

## Why no full orchestrator is selected yet

While tools like Airflow, Dagster, or Prefect are powerful, they introduce significant complexity and infrastructure requirements. At this stage of the project, a simple CLI-based orchestrator is sufficient and keeps the project lightweight and easy to run locally without external dependencies. Richer orchestrators may be evaluated and integrated as the project matures.
