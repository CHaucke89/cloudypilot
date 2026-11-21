# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This is **cloudypilot**, a personal fork of [sunnypilot](https://github.com/sunnypilot/sunnypilot) (itself a fork of [comma.ai's openpilot](https://github.com/commaai/openpilot)), an open source driver assistance system. Fork lineage, oldest to newest:

`commaai/openpilot` → `sunnypilot/sunnypilot` → this repo (`CHaucke89/cloudypilot`)

Remotes: `upstream` (sunnypilot/sunnypilot), `sp-fork` (personal sunnypilot fork), `star` (firestar5683/StarPilot, another fork used for reference), `origin` (this repo).

## Directory layout — read this before navigating

The repo root looks like it duplicates directories, but it doesn't — code is split across two levels on purpose:

- **Repo root** (`SConstruct`, `pyproject.toml`, `tools/`, `scripts/`, `docs/`, `launch_*.sh`) — build system, dev CLI, release tooling, and git submodules (`msgq_repo`, `opendbc_repo`, `panda`, `rednose_repo`, `teleoprtc_repo`, `tinygrad_repo`). Nothing here ships as part of the `openpilot` Python package.
- **`openpilot/`** — the actual `openpilot` package (see `pyproject.toml` → `[tool.hatch.build.targets.wheel] packages = ["openpilot"]`). Contains `cereal`, `common`, `selfdrive`, `system`, `third_party`, `tools` (device-side tools like cabana/replay/sim — different from root `tools/`), plus two fork-layering directories:
  - `openpilot/sunnypilot/` — sunnypilot's additions/overrides on top of stock comma openpilot.
  - `openpilot/cloudypilot/` — **this fork's own additions**, layered on top of sunnypilot the same way sunnypilot layers on top of openpilot (e.g. `system/manager/hash.py` device-authorization logic used by `manager_auth()` in `openpilot/system/manager/manager.py`, `common/version.h`, custom UI assets). When extending fork-specific behavior, prefer adding here rather than editing stock/sunnypilot files directly, and follow the existing pattern of importing from `openpilot.cloudypilot.*` into the stock file at the smallest possible touch point.

When grepping for something, check `openpilot/cloudypilot/` first for fork-specific behavior, then `openpilot/sunnypilot/`, then the rest of `openpilot/` for stock behavior.

## Dev environment

- First-time setup: `tools/op.sh setup`, then `source .venv/bin/activate`.

## The `op` CLI (`tools/op.sh`)

This is the primary dev entrypoint (alias `op` after setup).

- `op switch [REMOTE] <BRANCH>` — hard-resets the working tree and submodules to track a different branch/remote. Destructive (`git reset --hard`, `git clean -df` across submodules) — only invoke this deliberately.

## Testing

- `tools/test_runner.py` (via `op test`) is the unit test runner; CI sets `RAYLIB_BACKEND=headless` for UI tests.
- `openpilot/selfdrive/test/process_replay/test_processes.py` replays reference routes through the full process pipeline and diffs output against known-good logs — CI's main correctness check for `selfdrive` changes; run with `-jN` for parallelism.
- CI workflow reference: `.github/workflows/tests.yaml` (build/lint/unit-tests/process-replay jobs) is the source of truth for exact CI commands if `op` behavior seems unclear.

## Cereal / messaging schema constraints

`cereal` (`openpilot/cereal`) defines the msgq/schema structs shared across processes. If touching anything that changes on-disk log format or IPC structs: **do not modify the definitions of stock messaging fields** (e.g. `selfdriveState.enabled`, `carState.steeringAngleDeg`) — this is required both for upstream compatibility and for training-data eligibility (see `docs/CONTRIBUTING.md`). Add new custom fields/structs instead of repurposing existing ones.

## Submodules

`git submodule update --init --recursive` after cloning/switching branches. Submodules: `panda` (sunnyhaibin/panda), `opendbc_repo` (this fork's own opendbc, pinned via `[tool.uv].override-dependencies` since `panda` normally pins upstream opendbc from git), `msgq_repo`, `rednose_repo`, `teleoprtc_repo`, `tinygrad_repo`, plus `openpilot/sunnypilot/neural_network_data`.

## Code Comments

- Default to no comment. Code shows *how*; comment only to carry *why* — a non-obvious constraint, deliberate deviation, gotcha, or workaround.
- Never narrate the code (e.g., "loop over users"), restate names/types/signatures, or mark block ends.
- Never narrate the change (e.g., "fixed X", "updated to Y").
- Keep docstrings to one short line max; delete multi-paragraph docstrings.
- Comments must stand on their own with any link removed.
