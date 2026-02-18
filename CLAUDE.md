# CLAUDE.md — example-ai-collaboration

**ORGAN II** (Art) · `organvm-ii-poiesis/example-ai-collaboration`
**Status:** ACTIVE · **Branch:** `main`

## What This Repo Is

Human-AI co-creation framework: the AI-conductor model as artistic practice, with attribution tracking and process documentation

## Stack

**Languages:** Python
**Build:** Python (pip/setuptools)
**Testing:** pytest (likely)

## Directory Structure

```
📁 .github/
📁 docs/
    adr
    process-template.md
📁 examples/
📁 src/
    __init__.py
    attribution.py
    conductor.py
    export.py
    metrics.py
    session.py
📁 tests/
    __init__.py
    test_attribution.py
    test_conductor.py
    test_export.py
    test_metrics.py
    test_session.py
📁 workflows/
  .gitignore
  CHANGELOG.md
  LICENSE
  README.md
  pyproject.toml
  seed.yaml
```

## Key Files

- `README.md` — Project documentation
- `pyproject.toml` — Python project config
- `seed.yaml` — ORGANVM orchestration metadata
- `src/` — Main source code
- `tests/` — Test suite

## Development

```bash
pip install -e .    # Install in development mode
pytest              # Run tests
```

## ORGANVM Context

This repository is part of the **ORGANVM** eight-organ creative-institutional system.
It belongs to **ORGAN II (Art)** under the `organvm-ii-poiesis` GitHub organization.

**Registry:** [`registry-v2.json`](https://github.com/meta-organvm/organvm-corpvs-testamentvm/blob/main/registry-v2.json)
**Corpus:** [`organvm-corpvs-testamentvm`](https://github.com/meta-organvm/organvm-corpvs-testamentvm)
