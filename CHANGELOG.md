cloudypilot Version 0.1.0 (2026-11-01)
========================

* Initial release of cloudypilot, a personal fork of sunnypilot
  * Based on sunnypilot master (October 29, 2026), which includes sunnypilot v2026.002.000
  * See CHANGELOG-SP.md for the full sunnypilot and openpilot changelog history
* Vehicle & Controls
  * HKG angle-steering support for 2025+ CAN-FD Hyundai/Kia/Genesis vehicles, including adjusted steering-angle limits
  * Custom Steer Ratio: override the learned steering ratio with a fixed value, with the current learned value shown for reference
  * Blind Spot Audible Alert: play an alert when a vehicle is in the blind spot while the blinker is on, even if lateral control is inactive
  * Minimum Battery Voltage: configurable low-voltage shutdown threshold
* Remote UI
  * Built-in Remote UI streamer: view and control the device from a browser at `http://<device-ip>:8081`
  * Toggle in Developer settings; runs alongside other processes
  * Adaptive frame streaming, resolution scaling, and keyboard input support
  * Remote input is blocked while engaged
  * Installable as a Progressive Web App (PWA)
  * Remote UI dependencies are auto-installed after AGNOS updates
* User Interface
  * Home screen shows the active model, current branch, and Always Offroad controls
  * Soft Reboot button in the Device panel; `sudo systemctl restart comma` no longer triggers the hardware-reset prompt
  * Reset configurable options to their defaults by tapping the current value
  * Screen Saver Animation: choose Bounce, Drop, or Bounce (Rotating)
  * Steering Arc Fade: toggle the steering arc background fade independently
  * Developer UI: option to show altitude in feet
  * cloudypilot branding, boot spinner, path colors, and sidebar
* Connectivity
  * Use Konik API: option to use stable.konik.ai instead of comma connect
* Release
  * `master-prebuilt` branch is automatically built on every push to `master` for faster boot times
