# Examples

This directory contains examples of how to use the orchestration tool.

## Configuration Files

The `configs/` directory contains example YAML configuration files that can be used to run workflows.

### Weather MVP Local

The `weather-mvp-local.example.yml` file shows the parameters needed to run the Weather MVP local workflow.

## Running with CLI

You can run the Weather MVP local workflow using the CLI:

```bash
odl-orchestration run weather-mvp-local \
  --catalog-path ../datasets-catalog \
  --ingestion-repo-path ../ingestion \
  --transformation-repo-path ../transformation \
  --quality-repo-path ../quality \
  --workspace-dir ./workspace
```
