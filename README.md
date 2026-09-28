### THIS IS A POTENTIALLY "UNSAFE" FORK OF SUNNYPILOT/OPENPILOT

#### Cloudypilot is strictly a personal project and is not associated with sunnypilot or endorsed by its developers in any way

Cloudypilot is a fork of [sunnypilot](https://github.com/sunnypilot/sunnypilot) specifically made for my 2026 Kia EV6. It contains modifications to the safety code (primarily the angle steering limits) that could be considered unsafe by comma and result in a device ban, though Driver Monitoring and longitudinal engagement safety code have not been nerfed/altered.
If comma connect is valuable to you, tread carefully if you decide to install this.
If you do not use comma connect or use an alternative like stable.konik.ai, then you have nothing to worry about...except your life while letting this fork operate a motor vehicle with you in it.

Just kidding, it's not that bad.
Some of the additional features and/or changes in no particular order:

#### Toggles / Controls:
- Override the learned steer ratio value with a custom fixed value
- Custom low-voltage shutdown value - change the minimum car battery voltage that triggers a device shutdown
- Use Imperial units (feet) in the on-road developer UI rather than SI units (meters)
- Steering Arc - background fade effect is broken out to its own toggle
- Konik API toggle - use the stable.konik.ai API rather than connect.comma.ai
- Post-Blinker Delay - delay reengagement of lateral control for 0-10 seconds after the blinker turns off with Pause Lateral Control with Blinker - **this has since been merged into upstream sunnypilot**

#### Misc:
- "Soft" reboot - implemented a workaround to allow soft reboots via ```sudo systemctl restart comma``` without triggering a system reset prompt & added a Soft Reboot button to the Device panel
  - Stock behavior is preserved with a standard hardware reboot (tapping the screen during boot still triggers the reset prompt)
- Implemented "reset to default" functionality for option control items such as the custom Steer Ratio - tap the value itself to reset
- Current active model widget on home screen
- Current branch widget on home screen
- Enter/Exit Always Offroad Mode widget on home screen
- Many UI changes

**Do not install the ```ch-dev``` branch as it is locked to a specific device. Any branch may be broken at any time - this is primarily just for me, but as a big supporter of FOSS, it doesn't feel right to keep this private.**
**If you spot any features or modifications you would like to see upstream in sunnypilot, let me know and I can open a PR if feasible.**

Install at your own risk! Feel free to reach out if you have any issues or questions. It may take some time for me to respond, but I will as soon as I can.

# Licensing

Just as sunnypilot is a heavily modified version of openpilot, cloudypilot is a...moderately modified version of sunnypilot. Credit for the vast majority of the codebase goes to the openpilot and sunnypilot developers.

> "This project uses software from Haibin Wen and SUNNYPILOT LLC and is licensed under a custom license requiring permission for use."
> sunnypilot is released under the MIT License. This repository includes original work as well as significant portions of code derived from openpilot by comma.ai, which is also released under the MIT license with additional disclaimers.

The original openpilot license notice, including comma.ai’s indemnification and alpha software disclaimer, is reproduced below as required:

> openpilot is released under the MIT license. Some parts of the software are released under other licenses as specified.
>
> Any user of this software shall indemnify and hold harmless Comma.ai, Inc. and its directors, officers, employees, agents, stockholders, affiliates, subcontractors and customers from and against all allegations, claims, actions, suits, demands, damages, liabilities, obligations, losses, settlements, judgments, costs and expenses (including without limitation attorneys’ fees and costs) which arise out of, relate to or result from any use of this software by user.
>
> **THIS IS ALPHA QUALITY SOFTWARE FOR RESEARCH PURPOSES ONLY. THIS IS NOT A PRODUCT.
> YOU ARE RESPONSIBLE FOR COMPLYING WITH LOCAL LAWS AND REGULATIONS.
> NO WARRANTY EXPRESSED OR IMPLIED.**
