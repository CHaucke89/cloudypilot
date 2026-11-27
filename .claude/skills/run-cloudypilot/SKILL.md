---
name: run-cloudypilot
description: Run, drive and screenshot the cloudypilot comma 3x UI headless (home, sidebar tiles, settings panels, toggles, Remote UI). Use when asked to run/start/launch the UI, take a screenshot, tap through settings, or check a UI change works in the real app.
---

# Run cloudypilot (comma 3x UI)

The UI is the raylib Python app in `openpilot/selfdrive/ui`. In a headless container the
driver `.claude/skills/run-cloudypilot/driver.py` launches it (BIG UI, 2160x1080) inside a
temporary params prefix, feeds fake `deviceState`/`pandaStates`/GPS, and reads commands on
stdin: tap, swipe, screenshot, set params, dump the widget tree. Touches go through
cloudypilot's own `TouchInjector` socket, the same path Remote UI uses.

All paths are relative to the repo root.

## Prerequisites

Nothing extra to install: the container already has `libegl1`/`libgles2`/mesa, and with
`DISPLAY` unset raylib picks its `headless` (EGL) backend on its own, so no Xvfb.

## Setup and build

```bash
tools/op.sh setup                      # ~3 min: submodules, uv venv, LFS
source .venv/bin/activate
scons -j$(nproc) msgq_repo/ openpilot/cereal/ openpilot/common/   # all the UI needs
```

`op.sh setup` prints a 404 for `big_driving_tinygrad.pkl` from the Gitea LFS server, then
gets it from GitHub; that is fine (`git lfs fsck --pointers` says OK).

## Run (agent path): the driver

One-shot, commands piped in (exits after the last line):

```bash
source .venv/bin/activate
python .claude/skills/run-cloudypilot/driver.py <<'EOF' 2>/dev/null | grep '^drv>'
ss home
settings TOGGLES
tree ListItem
tap 675 720
get IsLdwEnabled
swipe 1330 900 1330 300
ss toggles-scrolled
home
quit
EOF
```

Screenshots land in `/tmp/cloudypilot-ui/` (`--out DIR` to change) at native 2160x1080.
Driver replies start with `drv>`; everything else is raylib/DBus noise.

Interactive, under tmux (keep the UI up between commands):

```bash
mkdir -p /tmp/cloudypilot-ui
tmux new-session -d -s ui -c "$PWD" "bash -c 'source .venv/bin/activate && python .claude/skills/run-cloudypilot/driver.py 2>/dev/null | grep --line-buffered \"^drv>\"'"
tmux send-keys -t ui 'param SidebarShowConnect 0' Enter 'param SidebarShowLoad 1' Enter 'ss tiles' Enter
tmux capture-pane -pt ui | grep drv
tmux send-keys -t ui 'quit' Enter
```

### Commands

| Command | What it does |
|---|---|
| `ss [name]` | screenshot (`.png` added; relative names go to `--out`) |
| `tap X Y` | press + release at UI pixel coords |
| `longpress X Y [sec]` | hold, default 0.8 s |
| `swipe X1 Y1 X2 Y2 [sec]` | drag; this is how lists scroll |
| `wheel DY` | mouse wheel, positive scrolls down |
| `key NAME` / `type TEXT` | keyboard (`Enter`, `Escape`, `Backspace`, `ArrowLeft`...) |
| `settings [PANEL]` / `home` | open a settings panel / go back home |
| `panels` | list panel names (DEVICE ... PERSONALIZE, DEVELOPER) |
| `param KEY VALUE` / `get KEY` | write / read a param (value parsed by the key's type) |
| `tree [FILTER]` | widgets drawn last frame: class, label, rect, center |
| `find TEXT` / `tapon TEXT` | locate / tap a drawn widget by its label |
| `wait SEC` | keep rendering |
| `eval PYTHON` | names: `main`, `ui_state`, `gui_app`, `params`, `rl`, `device`, `PanelType`, `MainState` |
| `quit` | finish queued input, then exit |

Flags: `--param KEY=VALUE` (repeatable, set before the UI starts), `--onboarding` (keep the
terms/training screens), `--prime N` (default 0 shows the Device/Quick Toggles home cards),
`--no-fake` (no fake device messages), `--remote` (see below).

Typical loop: `ss`, look at the image, `tree` to get exact centers, `tap`, `ss` again, and
`get` the param the control writes to prove it took effect.

## Run: Remote UI in a browser

```bash
tmux new-session -d -s srv -c "$PWD" "bash -c 'source .venv/bin/activate && python openpilot/cloudypilot/system/remote_ui/stream_server.py'"
tmux new-session -d -s ui -c "$PWD" "bash -c 'source .venv/bin/activate && python .claude/skills/run-cloudypilot/driver.py --remote 2>/dev/null | grep --line-buffered \"^drv>\"'"
sleep 12   # the server waits 10 s for wlan0 first
curl -s -o /dev/null -w '%{http_code}\n' --noproxy localhost http://localhost:8081/   # 200
```

Then drive the page with Playwright (run from any directory, `NO_PROXY=localhost`):

```js
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
  await p.goto('http://localhost:8081/');
  await p.waitForTimeout(2500);
  await p.mouse.click(85, 95, { delay: 100 });   // settings gear; canvas is at y=40..680
  await p.waitForTimeout(1500);
  await p.screenshot({ path: '/tmp/cloudypilot-ui/browser-settings.png' });
  await b.close();
})();
```

`tmux send-keys -t ui 'eval main._current_mode' Enter` confirms the click landed
(`MainState.SETTINGS`). Stop with `quit` in `ui`, then `tmux kill-server`.

## Run (human path)

On the device, manager starts `openpilot/selfdrive/ui/ui.py`. It opens a window and gives no
handle for input or screenshots, so headless it is no use; the driver wraps the same
`MainLayout` instead.

## Test

```bash
RAYLIB_BACKEND=headless python tools/test_runner.py openpilot/selfdrive/ui   # 51 passed, 1 skipped, ~8 s
ruff check .claude/skills/run-cloudypilot/driver.py && ty check .claude/skills/run-cloudypilot/driver.py
```

Bare `pytest` is not in the venv; use `tools/test_runner.py`.

## Gotchas

- Coordinates are UI pixels on the 2160x1080 screen. Image viewers often downscale the
  screenshot (e.g. to 2000x1000); multiply back before tapping.
- The UI returns home ~10 s after the last touch; the driver sets
  `device.set_override_interactive_timeout(3600)` so it stays put.
- A bare `OpenpilotPrefix()` has no param defaults (manager writes them), so default-on
  toggles read False. The driver writes every key's default first, like `manager.py` does.
- The sidebar shows at most 4 tiles (`MAX_TILES`), first 4 enabled in tile order. Temp,
  Vehicle, Connect and Sunnylink are on by default, so `SidebarShowLoad 1` alone shows
  nothing new; turn `SidebarShowConnect`/`SidebarShowSunnylink` off first. Param changes
  made while running are picked up live.
- The sidebar gear, sidebar tiles and Quick Toggle labels are drawn directly, not as
  widgets, so `tree`/`tapon` can't see them. Gear is at (145, 92).
- `tapon <title>` on a settings row taps the row's center, which doesn't flip its toggle.
  Use `tree` and tap the `ToggleAction*` center (x 675 on the Toggles panel).
- The first ~1.5 s after `ready` is used to let fake `deviceState` reach the sidebar;
  screenshots taken earlier show `--` and offline tiles.
- Before #49, Remote UI dropped a press and release that arrived in the same poll, so a
  plain Playwright `mouse.click` did nothing. The `{ delay: 100 }` above works either way.
- In the tmux command, quote `"^drv>"`: unquoted, `>` redirects output to a file named `^drv`.

## Troubleshooting

- `Failed to connect to system D-Bus` / `FileNotFoundError` tracebacks from
  `wifi_manager.py`: harmless, no D-Bus in the container.
- `stream_server.py` prints `DriveState: cereal unavailable, not gating input here`:
  harmless here (it imports `cereal` rather than `openpilot.cereal`).
- `curl localhost:8081` returns `000`: the server is still in its 10 s `wlan0` wait.
