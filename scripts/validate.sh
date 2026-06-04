#!/usr/bin/env bash

set -euo pipefail

echo "Running ruff check..."
ruff check .

echo "Running mypy..."
mypy src

echo "Running pytest..."
pytest
