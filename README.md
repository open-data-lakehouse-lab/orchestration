# odl-orchestration

Workflow orchestration repository for coordinating ingestion, transformation, validation, publishing and operational workflows across the Open Data Lakehouse Lab platform.

## Purpose

The `orchestration` repository is responsible for local workflow execution. It coordinates ingestion, quality validation, and transformation components to produce a consistent data lakehouse environment locally.

## Orchestration Scope

- Run the Weather MVP flow locally.
- Coordinate ingestion, landing quality, transformation, and bronze quality.
- Produce a local run workspace.
- Produce run summaries.
- Provide CLI-based orchestration workflows.

## Weather MVP Local Workflow

The current implementation supports a sample/offline local workflow:

```text
ingestion sample -> landing quality -> bronze transformation -> bronze quality -> silver transformation -> silver quality
```

This workflow does not require network access or real API keys, as it uses sample data.

## Workspace Layout

The tool generates a workspace with the following structure:

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

## Installation

### Dependencies

Install the project and its development dependencies:

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pip install -e .
```

### Sibling Repositories

This repository coordinates workflows that use sibling packages (`odl-ingestion`, `odl-transformation`, `odl-quality`). These sibling repositories must be installed in editable mode so their CLI commands are available in the environment:

```bash
python3 -m pip install -e ../ingestion
python3 -m pip install -e ../transformation
python3 -m pip install -e ../quality
```

### Path Arguments

The CLI accepts path arguments for sibling repositories (e.g., `--ingestion-repo-path`). Currently, these are used as local workflow context/reference paths. The workflow executes sibling repository commands through their installed CLIs. Future versions may use those paths for stronger validation or direct module execution.

## Usage

### CLI

Show version:

```bash
odl-orchestration version
```

Run the Weather MVP local workflow for a single resource:

```bash
odl-orchestration run weather-mvp-local \
  --resource stations-metadata \
  --catalog-path ../datasets-catalog \
  --ingestion-repo-path ../ingestion \
  --transformation-repo-path ../transformation \
  --quality-repo-path ../quality \
  --workspace-dir ./workspace
```

Run all supported resources sequentially with optional landing contract validation enabled:

```bash
odl-orchestration run weather-mvp-local \
  --resource all \
  --catalog-path ../datasets-catalog \
  --ingestion-repo-path ../ingestion \
  --transformation-repo-path ../transformation \
  --quality-repo-path ../quality \
  --workspace-dir ./workspace \
  --use-contracts
```

Supported resources:
- `stations-metadata` (default)
- `variables-metadata`
- `measured-variable`
- `all` (runs all the above sequentially)

### Landing Contract Validation

The `--use-contracts` option enables optional landing contract/schema validation using the contracts defined in the `datasets-catalog` repository. This is an opt-in feature, and the default orchestration behavior remains lightweight with contract validation disabled. These contracts are draft/minimal/permissive and internal to the laboratory, requiring no network access or API keys.

## Validation

To run ruff, mypy, and pytest:

```bash
bash scripts/validate.sh
```

## License

Unless otherwise noted:

- Software, scripts, Infrastructure as Code, SQL models, configuration files and executable assets are licensed under the [Apache License 2.0](LICENSE).
- Documentation, diagrams and written content are licensed under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).

Original upstream datasets, when referenced, remain governed by their original source licenses and terms.

Refer to [NOTICE](NOTICE) for additional information.
