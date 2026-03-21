## THIS IS AN "UNSAFE" FORK AND WILL GET YOUR DEVICE BANNED FROM COMMA'S SERVERS
### This fork is strictly a personal project and is not endorsed by or associated with sunnypilot or its developers in any way
This is a personal fork of [sunnypilot](https://github.com/sunnypilot/sunnypilot) specifically made for my Kia EV6 that very much falls under the [Bad/Unsafe Forks category](https://github.com/commaai/openpilot/wiki/Forks#badunsafe-forks). If you do not want to be banned from comma connect, do NOT use this with uploads enabled and be sure to delete all rlogs before switching back to a safe fork and re-enabling uploads. If you do not use comma connect or use an alternative like konik.ai, then you have nothing to worry about...except your life while letting this fork operate a motor vehicle with you in it.

Just kidding, it's not that bad.
Some of the additional features and/or changes in no particular order:

### Toggles:
- Always-Off Driver Monitoring (mutually exclusive with Always-On Driver Monitoring) - used for testing purposes only. **Please do not drive with driver monitoring disabled.**
- Dynamic "damp factor" when using stock longitudinal control
- Dynamic maximum steering torque & steer deltas
- Use Imperial units (feet) in the on-road developer UI rather than SI units (meters)
- Permanent seatbelt latch - allows engaging while the driver's seatbelt is unlatched
- Modified torque tune logic - Offline and Live tuning can be enabled or disabled independent of one another
  - Live tuning can be enabled or disabled and values can be modified while onroad
  - Live tuning can be enabled or disabled regardless of automatic self tune being enabled

### Other Stuff:
- Increased default maximum steering torque
- Increased default steer delta values
- Current active model widget on home screen with a button to open the Models settings page
- Current branch widget on home screen with a button to open the Software settings page
- Enter/Exit Always Offroad Mode widget on home screen
- "Soft" reboot - all standard reboots are replaced with soft reboots (```sudo systemctl restart comma```) and a Soft Reboot button is added to the Device settings page
- Various UI changes, mainly colors
- Git LFS removed/not used (all files are present in the repo)
- Any branch may be broken at any time - this is a free time hobby and only meant for myself, but as an avid supporter of open source software, it doesn't feel right to make this repo private.

If you decide to install this, you do so at your own risk!


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
