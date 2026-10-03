# cloudypilot

cloudypilot is a personal fork of [sunnypilot](https://github.com/sunnypilot/sunnypilot), itself a fork of [openpilot](https://github.com/commaai/openpilot). It is developed primarily for a 2026 Kia EV6 and is shared publicly as a free and open-source project.

> **This is a potentially unsafe fork.** cloudypilot is not affiliated with, endorsed by, or supported by sunnypilot, comma.ai, or the openpilot developers.

## Safety first

cloudypilot includes changes to safety-critical code, including steering-angle limits. These changes may be considered unsafe by comma.ai and could result in a device ban. Driver-monitoring and longitudinal-engagement safety code have not been intentionally weakened or removed.

This software operates a motor vehicle. Use it only if you understand the risks, follow all local laws, and can maintain constant attention and control. **Install and use cloudypilot entirely at your own risk.** It is alpha-quality research software, not a product, and comes with no warranty.

If comma Connect is important to you, consider these risks carefully before installing. cloudypilot also includes an option to use the stable.konik.ai API instead of connect.comma.ai.

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
- Stream the live on-device UI to a web browser with the built-in Remote UI server.
- Include additional user-interface changes.

## Remote UI Stream

cloudypilot incorporates the [raylib implementation of the openpilot remote UI streamer](https://github.com/CHaucke89/op-remote-ui). The server is controlled by the `Remote UI` toggle in Developer settings
and runs alongside the other openpilot/sunnypilot/cloudypilot processes. Verify it's running by connecting to the device through SSH and attaching to the comma tmux session with `tmux a`.

Make sure you're connected to the same Wifi network as the device and head to `http://<device-ip>:8081` in your browser to view and interact with the comma device remotely. The log file is located at `/tmp/cloudypilot_stream_server.log`.

## Branch guidance

Do **not** install the `ch-dev` branch; it is locked to a specific device. Any branch may be broken at any time. This project is primarily maintained for personal use, but feel free to use anything you find here however you see fit!

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
