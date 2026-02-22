# canvodpy — Claude Code Instructions

## Skills — always apply automatically

These skills are active for this project. Apply them automatically without being asked.

| Skill | Apply when |
|---|---|
| `marimo-notebook` | Writing or editing marimo notebooks (`.py` marimo files) |
| `xarray` | Working with `xarray.Dataset` / `DataArray`, coordinates, dims, attrs |
| `zarr-python` | Working with Zarr stores, Icechunk, chunking, encoding |
| `python-testing-patterns` | Writing or reviewing `pytest` tests |
| `pydantic` | Working with Pydantic models, validators, `BaseModel` |
| `uv-package-manager` | Running `uv`, editing `pyproject.toml`, managing deps |

## Project overview

`canvodpy` is a Python monorepo for processing GNSS observation data into
Vegetation Optical Depth (VOD) products. Key packages:

- `canvod-readers` — RINEX v2/v3 and SBF binary file readers → `xarray.Dataset`
- `canvod-store` — Icechunk/Zarr storage layer (`MyIcechunkStore`)
- `canvod-vod` — VOD retrieval algorithms
- `canvod-grids` — Spatial grid operations
- `canvod-auxiliary` — Auxiliary data pipeline (orbits, troposphere, etc.)

## Conventions

- Monorepo managed with `uv` workspaces
- Type checking: `uv run ty check`
- Linting/formatting: `uv run ruff check` / `uv run ruff format`
- Tests: `uv run pytest`; integration tests marked `@pytest.mark.integration`
- Dataset structure: `(epoch, sid)` dims, `"File Hash"` attr required
- Pydantic models use `frozen=False` with `@cached_property` for lazy computation
