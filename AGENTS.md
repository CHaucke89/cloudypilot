# AGENTS.md

## Repo shape (easy to misread)
- Two-level layout is intentional:
  - **Repo root**: build/dev tooling, scripts, docs, submodules.
  - **`openpilot/`**: the actual shipped Python package (`pyproject.toml` wheel packages only `openpilot`).
- Fork layering inside `openpilot/`:
  - `openpilot/cloudypilot/` = cloudypilot-specific overrides/additions
  - `openpilot/sunnypilot/` = sunnypilot layer
- Prefer implementing fork behavior in `openpilot/cloudypilot/` and wiring it into stock code at minimal touch points.

## Setup and environment
- Python is strict: `>=3.12.3,<3.13`.
- First-time setup: `./tools/op.sh setup` (submodules + deps + LFS + `op` alias).
- Missing submodules or LFS files will break normal build/test flows.

## Canonical commands
- Preferred entrypoint: `./tools/op.sh` (or `op` alias).
- Build: `./tools/op.sh build`
- Lint: `./tools/op.sh lint`
- Tests: `./tools/op.sh test`
- CI-equivalent direct commands:
  - Build: `scons`
  - Lint: `scripts/lint/lint.sh`
  - Tests: `tools/test_runner.py`

## Lint/typecheck gotchas
- `scripts/lint/lint.sh` order: `ruff` → indentation/shebang/large-file/no-merge checks → (`ty` + `codespell` unless `--fast` / `FAST=1`).
- Added files >120KB fail lint.
- Ruff is non-default here: 2-space indent, 160-char line length, quote style `preserve`.
- Banned APIs include `time.time` (use `time.monotonic`) and several direct `pyray.*` calls (see `pyproject.toml`).

## CI reality
- Source of truth: `.github/workflows/tests.yaml`.
- UI tests in CI run with `RAYLIB_BACKEND=headless`.
- CI assumes submodules are initialized and LFS content is present.

## Submodule wiring
- Local editable submodules are wired via `[tool.uv.sources]` in `pyproject.toml` (`msgq_repo`, `opendbc_repo`, `panda`, `rednose_repo`, `teleoprtc_repo`, `tinygrad_repo`).
- `opendbc` is intentionally overridden to this repo’s submodule (`[tool.uv].override-dependencies`).

## Destructive command
- `./tools/op.sh switch ...` is intentionally destructive (`git reset --hard`, `git clean -df`, submodule resets/cleans). Only run when explicitly requested.
