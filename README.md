# SAJ H2 Safe Enhanced

A clean, **read-only**, self-contained Home Assistant integration for compatible SAJ H2 inverters. All necessary dashboard files, sensor definitions, forecasting, and the installer are **inside this repository**.

**No YAML editing. No extra dashboard cards to download. No other repository required. No inverter writes.**

## What the dashboard shows

| Section | Purpose |
|---|---|
| **Live Energy** | Solar, house, battery, grid and forecast; SOC bar; actual watts and today's accumulated kWh |
| **Historic Data** | Hoverable signed kW graph with **10 minutes**, 6/12/24/48 hours and 7-day intervals; solar/house/battery/grid toggles and actual sample timestamps |
| **Solar Forecast** | Today, remaining, tomorrow, next week; expandable hoverable hourly and seven-day charts; **actual vs projected cumulative kWh** with mouse/touch/keyboard inspection |
| **Home Assistant Energy · Sensor IDs & Copy** | Compact responsive Grid, Solar, Battery, Home sensor guide. Shows the exact live entity IDs with copy buttons |

The dashboard is created automatically under **SAJ Energy** when the integration is configured. Its frontend is bundled and registered automatically. It does not modify or reset user-edited dashboards.

## One-command installation (Home Assistant Docker/Linux)

On the computer hosting your Home Assistant Docker container, paste:

```bash
curl -fL https://raw.githubusercontent.com/userdc-dev/saj-h2-safe-enhanced/main/scripts/install.sh -o /tmp/install-saj-safe.sh &&
bash /tmp/install-saj-safe.sh &&
docker restart homeassistant
```

The installer detects the host directory mounted at **/config** for a Docker container named `homeassistant`. If your container has another name or your setup is different, supply your own Home Assistant **configuration directory** (not the container's internal `/config`):

```bash
bash /tmp/install-saj-safe.sh /path/to/homeassistant/config
```

Example for one particular installation (replace for your own system):

```bash
bash /tmp/install-saj-safe.sh /home/kamrui/compose-files/homeassistant/config &&
docker restart homeassistant
```

The installer copies only `custom_components/saj_h2_safe`. It does **not** remove your existing config entries, entity registry, Home Assistant data, TOU settings, automations or other custom integrations.

### Home Assistant setup (no YAML)

1. Go to **Settings → Devices & services → Add integration → SAJ H2 Safe Monitor**.
2. The setup flow tries to locate a **verified SAJ H2 inverter** on the reachable local /24 network and reuses known compatible Home Assistant connection addresses when possible. If one verified inverter is found, it can configure that device automatically. If discovery cannot reach your network (especially in a Docker bridge), enter its local IP instead.
3. Open the new **SAJ Energy** dashboard from the sidebar. The four sections are ready without manually editing dashboard YAML or JavaScript resources.

**If you already configured SAJ H2 Safe Monitor**, updating the code preserves your integration and adds the new dashboard. Your existing entity IDs stay intact.

### HACS

Add this repository as a **custom integration repository**, download **SAJ H2 Safe Enhanced**, restart Home Assistant and follow the same Add integration step. HACS support is supplied by root `hacs.json` and a valid custom integration package; no separate monitor repository is needed.

## Accuracy and safety

This is a **read-only Modbus function 03 integration**. It does not expose inverter control, charging/discharging commands, operating-mode switches or TOU writes.

- Battery SOC, solar generation, house usage and battery charged/discharged day totals come from the local inverter.
- Grid direction (positive import / negative export) still requires verification with a real utility meter. Estimated import/export kWh only count periods for which power readings were recorded; they are **not certified utility meter data**.
- Actual solar on the cumulative chart is the inverter's daily solar counter recorded by Home Assistant Recorder; gaps are not synthesized.
- The solar forecast uses Open-Meteo tilted irradiance with conservative clear-sky learning. Your Home Assistant configured coordinates are sent to Open-Meteo for weather forecasts; solar usage data are not uploaded.
- Home Assistant retains the existing sensor unique IDs. A handful of new read-only grid energy/power entities are additive, not replacements.
- If Home Assistant Recorder contains no history, the graph displays missing information rather than inventing values.

## Maintenance and development

- [Developer handover](PROJECT_HANDOFF.md)
- [Tests and verification](.github/workflows/validate.yml)
- [One-command installer](scripts/install.sh)

Python decoding and solar-model tests, the standalone JavaScript syntax check and a no-write policy run in GitHub Actions. Passing offline tests does **not** mean compatibility with every SAJ firmware or verification of grid polarity on your property.

**Recommended first test:** Confirm the Live Energy solar and battery values match the SAJ app; open Historic Data → 10 minutes; move the cursor across the chart and check sample timestamps; compare real daily kWh with the inverter app; then verify grid polarity before using the Energy dashboard for bill calculations.
