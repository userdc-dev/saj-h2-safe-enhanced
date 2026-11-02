# SAJ H2 Safe Enhanced — Developer handover (v0.4.1)

**Last updated:** 2026-11-02  
**Repository:** https://github.com/userdc-dev/saj-h2-safe-enhanced  
**Scope:** A minimal, independent, read-only Home Assistant integration. No manual YAML or additional repositories are required.

## v0.4.1 — Missing projected solar line (2026-11-02)

A field screenshot showed the actual (blue) cumulative solar series but no forecast (yellow) line even though hover revealed valid forecast kWh. Root cause: `forecastChart()` applied a **45-minute gap cutoff to BOTH series**. The expected forecast is one data point per hour, so each yellow point was disconnected and the SVG generator drew no path for singletons. **Fixed:** the projected series uses 90 minutes between adjacent hourly forecast buckets; actual Home Assistant Recorder samples retain the shorter 45-minute gap limit. Added a genuine frontend smoke assertion that the projected SVG includes a yellow path connecting at least two forecast points. Cache-busted the frontend URL to `/saj-h2-safe/v041/saj-safe-monitor-card.js` and incremented manifest to v0.4.1. Keep forecast hourly spacing distinct from actual Recorder data for future charts; don't synthesize missing readings.

## Core requirements — do not regress

The user explicitly requested the Safe Enhanced repository be rebuilt around **only four clean monitoring sections**, matching the appearance and usability of their working control dashboard:

1. **Live Energy:** 5-column Solar, House, Battery, Grid, Forecast table; SOC and stored energy; live power (W/kW); a compact bottom "Today so far" row for cumulative solar, home, battery charged/discharged, grid imported/exported and modeled solar forecast so far.
2. **Historic Data:** solar, home, signed battery and grid power; flexible 10-minute, 6-hour, 12-hour, 24-hour, 48-hour and 7-day ranges; actual Recorder data only; hover/tap/keyboard inspection and timestamps; gaps must remain gaps.
3. **Solar Forecast:** clear today/remaining/tomorrow/7-day kWh summary, expandable hoverable seven-day and hourly estimates, live clear-sky calibration status, and a hoverable *actual vs projected today* cumulative energy chart using the published `today_hourly` physical irradiance forecast series and actual recorded daily inverter counter.
4. **HA Energy · Sensor IDs & Copy:** collapsed by default; four responsive categories Grid, Solar, Battery, Home; exact friendly names and entity IDs in selectable text inputs with copy buttons. Battery charged and discharged energy are separate. Grid signed vs split power and cumulative grid kWh are distinct; estimated grid power sign is provisional.

The entire dashboard is registered automatically using `frontend_setup.py`; new installations get a separate **SAJ Energy** dashboard. Do not overwrite user-created dashboards or the unrelated control dashboard.

## Installation, discovery and compatibility

- `scripts/install.sh`: downloads this repository's main branch; infers the host config directory from a Docker container named `homeassistant` (volume destination `/config`); accepts any user-supplied Home Assistant host config directory; copies **only** `custom_components/saj_h2_safe`; does not delete HA configs/registry or overwrite other integrations; no YAML edits. Restart Home Assistant after installation.
- `hacs.json`: root HACS integration metadata. Install via HACS or the installer; users then select **Settings → Devices & services → Add integration → SAJ H2 Safe Monitor** (no manual YAML).
- `config_flow.py` + `discovery.py`: when adding the integration, first reuse local private addresses from existing compatible Home Assistant config entries. Safely probe at most a single local `/24` subnet with bounded concurrency and Modbus read-only function 03 checks of battery SOC and PV registers. Never treat an open TCP 502 port alone as proof of an SAJ H2. Only auto-select when exactly one verified candidate; show choices for multiple verified devices; allow manual IP input if local Docker networking hides the physical LAN. There is no guarantee of network-level auto-discovery in every Docker or routed topology.
- All old `saj_h2_safe` **entity unique IDs** and sensor definitions remain stable. This is required because `saj-h2-control-enhanced` uses the same read-only coordinator keys and existing dashboards/automations may use those entities. Do not rename the integration domain, restore old dashboard YAML, or require the control repository.
- Installer from the *control repository* already protects independently existing monitors from being overwritten. If editing that other project, retain its "preserve existing monitor" behaviour.

- `SajSafeOptionsFlow` in `config_flow.py` exposes solar panel group counts, wattages, compass directions and tilts, system efficiency, nominal battery capacity, and live poll frequency through **Home Assistant's built-in Configure UI**. Defaults reflect the original user's panel system, but prompt everyone to review them. No YAML. It rejects layouts with zero total panels. `solar_forecast.py` consumes these options on each refresh; changing options reloads the integration. Learned forecast factors are reset if the panel layout/efficiency fingerprint differs from stored learning metadata, preventing incompatible historical adjustments.
## Backend data and safety

- `__init__.py`: existing `SajSafeCoordinator` continues to read the established holding registers with Modbus read-only function 03, 10-second live readings, slower mode/energy counter cache; retains low-level keys and battery SOC checks.
- `const.py`: exact legacy register mappings; battery power sign means positive discharge and negative charge; grid sign **must be verified against a physical import/export** before claiming billing accuracy.
- `grid_totals.py`: new, independent persistent read-only energy counter integrator. Splits measured power-crossing zero into positive import/export kWh, ignores gaps longer than 60s, persists to HA `Store` every two minutes and when unloading. Local today's totals reset by local calendar date. It does **not** backfill unrecorded power data, double-count when offline or invent grid meter totals. Estimates are not certified meter readings.
- `sensor.py`: `SajSafeSensor` and `SajForecastSensor` original unique IDs are preserved. `SajReadOnlyEnergySensor` adds new grid-signed W (measurement), import/export total-increasing kWh, and *today's monitored-interval* kWh aliases. Forecast sensors remain predictions with no `total_increasing` state class.
- `solar_forecast.py` / `solar_model.py`: Open-Meteo tilted irradiance (per installed panel group), conservative live-hour calibration, no inverter writes or demand controls. New `today_hourly` attribute on the existing forecast sensor allows cumulative expected-by-hour plotting alongside HA Recorder's daily actual solar counter. Weather predictions are not metered energy.
- There are **no writable Modbus methods, operating-mode selections, charge/discharge schedules, switches, numbers, buttons, or service calls** in this repository. No control code is imported from the independent Control repository. The read-only monitor may coexist with control components without changing them.
- The user's historic inverter profile is 30 × 440 W bifacial panels in groups 9/15/6, azimuth 29°/27°/299°, tilt 25°, efficiency 87%, 10kW AC inverter, nominal 40.0kWh battery capacity. These are installation-specific example defaults, not universally accurate. The forecast physical generation model is PV-side, not necessarily capped by AC inverter export.

## Frontend design contract

- `frontend/saj-safe-monitor-card.js`: one custom element `custom:saj-safe-monitor-card`, dark-theme native Home Assistant variables, single-column stacked sections, low visual density, four responsive HA Energy guide columns. No manual Lovelace YAML and no external JS libraries.
- Uses `hass.states` and existing registry entity IDs. If entities were renamed, consult `hass.entities` registry metadata (`platform=saj_h2_safe`, unique-ID suffix), then display the **actual** returned entity ID. No guessed IDs in copy fields.
- History uses the Home Assistant Recorder `history/period` API, not generated fake data. Exact sample times and signed W are preserved for hover. The 10-minute view uses 30-second cursor steps and a max 90-second line-gap tolerance; queries refresh periodically.
- Forecast actual-vs-projected retrieves the local-day recorded *solar_today kWh counter* independent of historical kW range, and plots the matching day's hourly PV forecast. Hover reveals values at the selected time. Gaps are not backfilled.
- Collapsed sections hold seven-day/hourly forecast details and the HA Energy reference. Minimal headline cards remain visible. Native, read-only entities are the only sources.
- Do not introduce cost-estimate/tariff editing or inverter controls here. Those belong outside this **monitoring-only** scope.

## Verification

`.github/workflows/validate.yml` checks Python syntax, installer syntax, the JS card, mock-Home-Assistant frontend runtime, original register decoder and physical forecast model, and rejects any writable Modbus method. Keep these tests updated.

**Pending on-device checks:** test local-SA inverter discovery with Home Assistant container networking, auto-dashboard registration on HA boot, tooltip positions/responsiveness on desktop/mobile, forecast daily cumulative alignment, grid meter polarity, and Recorder history coverage. CI tests cannot prove live grid direction or inverter register correctness.

## Old repository content removed

Obsolete `dashboards/saj-energy.yaml` and `examples/weekly-utility-meters.yaml` have been deleted. The root README now documents automatic dashboard creation and one-command installation. No user dashboard is deleted on their HA instance; Home Assistant dashboard changes are only additive to avoid data loss.

**Do not reintroduce YAML setup instructions, hard-code `/home/kamrui` as the universal installation path, or require users to copy JavaScript into `/config/www`.**
