# cloudypilot additions to sunnylink's settings_ui.json, applied at load time so the
# upstream definition (and its settings_ui_src/ compiler roundtrip) stays untouched.

STEER_RATIO_SECTION = {
  "id": "steer_ratio",
  "title": "Steer Ratio",
  "description": "Custom steering ratio tuning and presets",
  "items": [
    {
      "key": "UseCustomSR",
      "widget": "toggle",
      "title": "Enable Custom Steer Ratio",
      "description": "Enable custom steering ratio tuning to override default vehicle steering ratio.",
      "sub_items": [
        {
          "key": "CustomSR",
          "widget": "option",
          "title": "Steer Ratio",
          "description": "Adjust the steering ratio.",
          "min": 10.0,
          "max": 20.0,
          "step": 0.1,
          "enablement": [
            {
              "type": "offroad_only"
            },
            {
              "type": "param",
              "key": "UseCustomSR",
              "equals": True
            }
          ]
        }
      ]
    }
  ]
}

# (panel id, section to insert, id of the section to insert after)
SECTIONS_CP = [
  ("steering", STEER_RATIO_SECTION, "torque"),
]


def apply_settings_ui_cp(schema: dict) -> None:
  panels = {panel["id"]: panel for panel in schema.get("panels", [])}
  for panel_id, section, after_id in SECTIONS_CP:
    panel = panels.get(panel_id)
    if panel is None:
      continue
    sections = panel.setdefault("sections", [])
    if any(s["id"] == section["id"] for s in sections):
      continue
    ids = [s["id"] for s in sections]
    idx = ids.index(after_id) + 1 if after_id in ids else len(sections)
    sections.insert(idx, section)
