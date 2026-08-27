# CI Testing Pipeline

[![CI](https://github.com/sifrstack/ci-testing-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/sifrstack/ci-testing-pipeline/actions/workflows/ci.yml)

A focused Python project demonstrating how automated tests and lint checks protect code quality on every change.

## What the project demonstrates

- Parsing structured ping result lines into typed Python objects
- Validating expected input and rejecting malformed data
- Calculating success rate, average latency, and p95 latency
- Writing unit tests with pytest
- Enforcing code quality with Ruff
- Running the same checks automatically with GitHub Actions

## Requirements

- Python 3.10 or newer

## Run locally

```bash
git clone https://github.com/sifrstack/ci-testing-pipeline.git
cd ci-testing-pipeline

python -m venv .venv
source .venv/bin/activate
pip install pytest ruff
```

Run the test suite and lint checks:

```bash
pytest -q
ruff check .
```

## Example functionality

The core module accepts structured lines such as:

```text
host=1.1.1.1 status=OK latency_ms=12.3
host=google.com status=FAIL
```

It converts them into validated results and produces summary metrics including total checks, success rate, average latency, and p95 latency.

## Project structure

```text
ci-testing-pipeline/
├── src/
│   └── metrics.py   # Parsing, validation, and metric calculations
├── tests/           # pytest unit tests
├── .github/workflows/ci.yml
└── pyproject.toml
```

## Continuous integration

The workflow runs for pushes and pull requests to `main`. Each run:

1. Checks out the repository
2. Sets up Python
3. Installs pytest and Ruff
4. Runs `ruff check .`
5. Runs `pytest -q`

A failed lint rule or unit test stops the workflow, making regressions visible before changes are merged.

## Why I built it

This repository is intentionally small so the testing and CI workflow stays easy to inspect. It demonstrates the foundations used in larger software projects: repeatable checks, fast feedback, and documented development commands.
