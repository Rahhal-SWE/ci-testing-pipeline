# CI Testing Pipeline (pytest + GitHub Actions)

A small Python project demonstrating automated unit testing and CI using GitHub Actions.
It parses structured ping results and produces summary reliability/latency metrics.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install pytest ruff
pytest -q
ruff check .
