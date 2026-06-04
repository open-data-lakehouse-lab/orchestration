# Orchestration Design

The `orchestration` repository is responsible for local workflow execution in the Open Data Lakehouse Lab project.

## Local-first orchestration

The current implementation focuses on a lightweight, local-first orchestration approach. It coordinates the execution of different components (ingestion, transformation, quality) that are available as sibling repositories.

## CLI-based coordination

Orchestration is achieved by calling the Command Line Interfaces (CLIs) of the sibling repositories using a subprocess executor. This keeps the orchestration layer independent of the internal implementation details of each component.

The sibling repositories (`odl-ingestion`, `odl-transformation`, `odl-quality`) must be installed in editable mode within the same environment so their CLI commands are reachable.

## Sibling Repository Paths

The workflow accepts paths to sibling repositories as arguments. In the current implementation, these paths serve as local context and reference. The actual execution relies on the CLIs installed in the environment. This design allows for future enhancements where the paths could be used for direct module discovery, stronger validation, or configuration overrides.

## Subprocess Executor

The `SubprocessExecutor` is a simple wrapper around Python's `subprocess.run`. It captures stdout, stderr, and exit codes, providing a structured result for each execution step.

## Run Workspace

Each workflow run produces a dedicated workspace directory. This workspace contains:
- `landing/`: Data ingested from source (sample mode).
- `bronze/`: Data transformed to bronze format.
- `reports/`: Run summaries and other execution reports.

## Run Summaries

At the end of each run, a `run-summary.json` file is produced. It contains detailed information about the execution, including the status of each step, start and end times, and paths to generated artifacts.

## Why no full orchestrator is selected yet

While tools like Airflow, Dagster, or Prefect are powerful, they introduce significant complexity and infrastructure requirements. At this stage of the project, a simple CLI-based orchestrator is sufficient and keeps the project lightweight and easy to run locally without external dependencies. Richer orchestrators may be evaluated and integrated as the project matures.
