<img width="784" height="330" alt="cloudy_cropped" src="https://github.com/user-attachments/assets/d30bf073-b8f1-4ba7-bcc6-d2f457529b85" />

# cloudypilot

cloudypilot is a personal fork of [sunnypilot](https://github.com/sunnypilot/sunnypilot), itself a fork of [openpilot](https://github.com/commaai/openpilot). It is developed primarily for a 2026 Kia EV6 and is shared publicly as a free and open-source project.

> **This is a potentially unsafe fork.** cloudypilot is not affiliated with, endorsed by, or supported by sunnypilot, comma.ai, or the openpilot developers.

## Safety first

cloudypilot includes changes to safety-critical code, including steering-angle limits. While this does not explicitly break any of comma's rules, tread carefully if using this fork and uploading to comma connect. Driver-monitoring and longitudinal-engagement safety code have not been intentionally weakened or removed.

This software operates a motor vehicle. Use it only if you understand the risks, follow all local laws, and can maintain constant attention and control. **Install and use cloudypilot entirely at your own risk.** It is alpha-quality research software, not a product, and comes with no warranty.

## Installation

cloudypilot's master branch can be installed using the following URL: `installer.hauckelabs.dev'

## Features and changes

### Controls

- Override the learned steering-ratio value with a custom fixed value.
- Configure the low-voltage shutdown threshold.
- Use imperial units (feet) in the on-road developer UI.
- Toggle the Steering Arc background fade effect independently.
- Select the stable.konik.ai API instead of comma Connect.
- Configure a 0–10 second post-blinker delay before lateral control re-engages when **Pause Lateral Control with Blinker** is enabled. This feature has since been merged upstream into sunnypilot.

### Other changes

- Add a **Soft Reboot** button to the Device panel and support `sudo systemctl restart comma` without triggering the hardware-reset prompt. Standard hardware reboot behavior is preserved.
- Reset configurable options to their defaults by tapping the current value.
- Show the active model, current branch, and Always Offroad Mode controls on the home screen.
- Stream and interact with the device remotely the built-in Remote UI streamer (more info below).
- Include additional user-interface changes.

## Remote UI Stream

cloudypilot incorporates the [raylib implementation of the openpilot remote UI streamer](https://github.com/CHaucke89/op-remote-ui). The server is controlled by the `Remote UI` toggle in Developer settings
and runs alongside the other openpilot/sunnypilot/cloudypilot processes. Verify it's running by connecting to the device through SSH and attaching to the comma tmux session with `tmux a`.

Make sure you're connected to the same Wifi network as the device and head to `http://<device-ip>:8081` in your browser to view and interact with the comma device remotely. The log file is located at `/tmp/cloudypilot_stream_server.log`.

## Use Remote UI as a Web App (PWA)

The remote UI page includes PWA metadata and can be installed to a home screen or desktop for a more app-like, fullscreen experience.

### Before installing

- Make sure the stream server is running and reachable on your local network.
- Open: `http://<device-ip>:8081`
- Rotate phones to landscape for best usability.

### iPhone / iPad (Safari)

1. Open `http://<device-ip>:8081` in Safari.
2. Tap the Share button.
3. Tap **Add to Home Screen**.
4. Launch from the new home-screen icon.

Notes:

- Installing from the home screen gives the best fullscreen behavior.
- If the UI appears stale after an update, close and reopen the app.

### Android (Chrome / Samsung Internet / Other Chromium browsers)

1. Open `http://<device-ip>:8081`.
2. Open the browser menu.
3. Tap **Install app** / **Add to Home screen** (varies by device/browser).
4. Launch from the app drawer or home screen.

### Desktop (Chrome / Edge)

1. Open `http://<device-ip>:8081`.
2. Click the install icon in the address bar, or open the browser menu and choose **Install** / **Apps**.
3. Launch the installed app window from your OS app launcher.

### macOS (Safari)

1. Open `http://<device-ip>:8081` in Safari.
2. Use **File** -> **Add to Dock**.
3. Launch from Dock as a standalone web app.

### Quick troubleshooting

- No live updates (only first frame): restart the stream server and reopen the app.
- Inputs work but video is frozen: close all open remote UI tabs/windows, then reconnect once.
- Scale/layout looks wrong after rotation: rotate back, wait one second, then rotate again.

## Branch guidance

Do **not** install the `ch-dev` branch; it will only run on one specific device. The `master` branch is the only branch that should be installed on a device or used for development. Alternatively, to speed up boot time considerably, the `master-prebuilt` branch is automatically built on every push to the master branch, so it is always up-to-date. The prebuilt branch should only be used for device installation as much of the source code is no longer present. This project is primarily maintained for personal use, but feel free to use anything you find here however you see fit!

If you find a feature that would be useful upstream in sunnypilot, open an issue or reach out! A pull request can be made, if feasible.

## Related documentation

- [Vehicle support](docs/CARS.md)
- [Safety documentation](docs/SAFETY.md)
- [Limitations](docs/LIMITATIONS.md)
- [Contributing](docs/CONTRIBUTING.md)

## Licensing and attribution

cloudypilot contains original work and substantial portions derived from sunnypilot and openpilot. Credit for the vast majority of the codebase belongs to their respective developers.

> This project uses software from Haibin Wen and SUNNYPILOT LLC and is licensed under a custom license requiring permission for use.
>
> sunnypilot is released under the MIT License. This repository includes original work as well as significant portions of code derived from openpilot by comma.ai, which is also released under the MIT license with additional disclaimers.

The original openpilot license notice, including comma.ai's indemnification and alpha-software disclaimer, is reproduced below as required:

> openpilot is released under the MIT license. Some parts of the software are released under other licenses as specified.
>
> Any user of this software shall indemnify and hold harmless Comma.ai, Inc. and its directors, officers, employees, agents, stockholders, affiliates, subcontractors and customers from and against all allegations, claims, actions, suits, demands, damages, liabilities, obligations, losses, settlements, judgments, costs and expenses (including without limitation attorneys’ fees and costs) which arise out of, relate to or result from any use of this software by user.
>
> **THIS IS ALPHA QUALITY SOFTWARE FOR RESEARCH PURPOSES ONLY. THIS IS NOT A PRODUCT.**
>
> **YOU ARE RESPONSIBLE FOR COMPLYING WITH LOCAL LAWS AND REGULATIONS.**
>
> **NO WARRANTY EXPRESSED OR IMPLIED.**
