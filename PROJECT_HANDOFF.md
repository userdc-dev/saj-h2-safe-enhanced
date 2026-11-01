# PROJECT HANDOFF — SAJ H2 Safe Enhanced

**Updated:** 2026-11-01 (Australia/Adelaide).  
**Read this FIRST when resuming work on this repo in a new chat.**  
**Status:** v0.2.1 has been installed and tested on the owner's Home Assistant. **v0.3.0 solar forecast is committed to GitHub but has NOT yet been installed or tested on the owner's HA.** Do not falsely claim v0.3.0 works until verified on the device.

This file is the durable memory of our user conversations. Keep it current as changes are confirmed. The user asked that someone knowing only this repo could immediately resume development. Avoid copying personal names, street addresses, credentials, keys, tokens, and other sensitive details into this (potentially public) repository.

## 1. Project goal / user preferences

Build a beautiful, safe, **local-first Home Assistant SAJ H2 integration** akin to the official SAJ smartphone app:
- Live solar, PV1/2/3, house consumption, signed battery power, battery SOC and estimated kWh, operating mode, separate grid import and export, charging/discharging.
- Daily, weekly, monthly, annual and lifetime kWh production/usage, with history graphs.
- Clean, uncluttered **dark-themed SAJ-style** dashboard; flow on **left** and power graph **right**, battery/PV/other smaller cards underneath. Chart labels exactly: **Total PV, House Load, Battery Power, Grid Power** (avoid verbose HA entity names).
- Dynamic formatting in dashboard: below 1000 W display W; at 1000+ W use kW; similarly Wh/kWh for energy. **Do not change numerical HA sensor units to textual values** or long-term statistics will break.
- Add experimental solar estimator inspired by owner's Android SolarCast app, with 7-day/hourly weather forecast and cautious self-correction for actual production, shading, and curtailment.
- Technical instruction style: **VERY SHORT, ONE SSH COMMAND OR ONE ACTION PER MESSAGE**. Wait for the user's “done” or terminal output before the next install action. User appreciates doing GitHub edits directly via GitHub integration. Provide **complete replacement dashboard YAML** via link (not fragments), and minimize manual edits.
- Read-only safety paramount; controls later only after comprehensive verification. Never break the functioning v0.2.1 monitoring setup.

## 2. Hardware, environment and installed configuration

- Inverter: **SAJ H2, nominal 10 kW AC output rating**. Battery: **SAJ B2 40.96 kWh nominal**; previously reported approx 38.5 kWh usable; show stored energy as estimate SOC × 40.96 kWh until BMS capacity is verified. Owner's PV: **30 × 440 W bifacial panels = 13.2 kWp**, described around 13.3 kWp.
- **IMPORTANT physics:** 10 kW AC output does **NOT** mean 10 kW PV generation ceiling; panels may generate more with simultaneous DC-side battery charging. User suggested battery charging might be up to ~10 kW as an example; hardware/routing constraints NOT independently verified. Forecast **PV-side** generation separately from AC delivered and DC battery charge; do not clip total estimated PV at 10 kW. Distinguish predicted irradiation potential from measured generation curtailed by export/battery/firmware limits.
- Debian Kamrui mini PC; Docker Home Assistant service/container **`homeassistant`**. Config directory on host: `/home/kamrui/compose-files/homeassistant/config`; custom component `config/custom_components/saj_h2_safe/`; Docker config is `/config`.
- Modbus TCP: SAJ inverter at a stable private LAN IP configured in the HA integration, port **502**, unit/device ID **1**; do not hardcode a private IP in repo documentation. Original example used a reserved LAN IP and worked.
- HA existing `configuration.yaml` includes `default_config:`, frontend themes, `automation`, `script`, `scene`, `http` trusted proxies, and a separate YAML RF Fan dashboard. **No `template:` stanza.** Current SAJ UI is an independently created dashboard named `SAJ Energy` whose YAML was copied from `dashboards/saj-energy.yaml` into the HA Raw configuration editor. Dashboard YAML edits in GitHub do **not** auto-deploy to HA; user pastes the full file into the raw editor.
- `custom_components` must contain only valid component folders; previously putting a backup like `saj_h2_safe_backup_v0.1.0` directly under `custom_components` caused loader issues. Backups go elsewhere.

## 3. Version milestones / WHAT ACTUALLY WORKS

- **v0.1.0:** initial safe integration. SOC register 0x406F returned raw 4300 for 43.00%; fixed 0.01 scaling in v0.1.1.
- **v0.1.2:** confirmed all 3 MPPT inputs; PV1/PV2/PV3 power sum matched SAJ phone app within sampling delay.
- **v0.1.3:** live home consumption and signed grid power added. Home App screenshot matched within tens of watts.
- **v0.2.0:** live power, estimated battery kWh, operating mode, 32-bit energy counters, daily/monthly/yearly/lifetime, battery charge/discharge, provisional grid import/export indicators, dashboards. Installed and operating. Fixed HA warning: energy device class + `measurement` state class on **estimated battery energy** was invalid; this is a snapshot with no state class.
- **v0.2.1:** live Modbus poll approx **10 seconds**, slow battery mode and energy counters approx **60 seconds**. User verified it feels much faster. For performance, do NOT poll all counters every 5 seconds without justification.
- The user showed the dashboard **Live** and **Energy** views working. 24-hour history was populated for solar/home/battery/grid; daily/monthly/yearly energy counters worked. Weekly/monthly statistics charts initially displayed “No statistics found” because installation was new. DB investigation: 41 statistic IDs, solar/home lifetime counters had **2 five-minute short-term records each and 0 hourly records** at that moment. This is compatible with normal initial recording; do not misdiagnose absent hourly history if just installed.
- **v0.3.0 in GitHub:** added `solar_model.py`, `solar_forecast.py`, forecast sensors, and a Solar Forecast dashboard tab. Built on the panel-group model from the Android app; forecasts Open-Meteo GTI, conservative hour-of-day factors, and actual + predicted remaining daily outlook. **Not yet installed or validated on user's Home Assistant.** First installation step given was download the GitHub main archive, but no response yet confirming execution. Must perform careful testing and iterative fixes before saying it works.
- `.github/workflows/validate.yml` was added for compile/test/ban write methods. **Do not assume its CI jobs succeeded without checking.**

## 4. Confirmed MODBUS and scaling

- Read only with function 03 `read_holding_registers`. Use `pymodbus` v3 async or sync client, device_id=1 on currently installed v3. Avoid all write modes / external controls.
- 0x4069: battery voltage (×0.1 V); 0x406A current (×0.01 A signed); 0x406D signed battery watts; 0x406E temperature (×0.1 °C); 0x406F SOC (×0.01%).
- 0x4071–0x4079: PV1–PV3 voltage/current/power. Example `read_holding_registers(0x4071,count=16,device_id=1)` returned `[2839,124,354,3231,83,267,3424,101,341,0,0,0,0,0,0,0]`: 354+267+341=962 W, similar to SAJ app ~978 W.
- 0x40A0: home load W. 0x40AD: raw signed grid W. Raw `read_holding_registers(0x40A0,count=14)` once returned `[1190,0,0,0,0,1018,172,976,1603,964,1634,0,50,0]` near screenshot load 1.13–1.19 kW, PV about 1 kW, battery ~0.17 kW, grid zero. Positive battery power corresponds to DISCHARGING; negative to CHARGING, verified against screenshots.
- Grid direction **not yet measured at a nonzero value**. UI currently assumes signed grid **positive = import**, **negative = export** with explicit provisional label. SAJ app usually shows zero exchange because self-use battery balances demand. Do not remove “unverified” label or use for billing until compared with app during nonzero flow. Do not cause grid import/export artificially by forcing inverter changes.
- Energy 32-bit high-word-first counters ×0.01 kWh from upstream SAJ mapping:
  - `0x40BF` block: `solar_today` at 0x40BF; next month/year/total every two registers. `battery_charge` starts +8 registers; `battery_discharge` +16.
  - `0x40DF` block: `home` starts there; `grid_sell` +16 (`0x40EF`); `grid_feed_in` +24 (`0x40F7`). Grid energy semantics **unverified**; keep upstream names until cross-check.
  - Example owner readings: `0x40BF` 32 words `[0,1659,0,1659,24,41223,29,59735,0,968,0,968,5,60869,6,28835,0,1614,0,1614,4,61030,5,18451,0,0,0,0,0,0,0,0]`; solar 16.59 kWh that afternoon, agreeing with ~16.38 kWh earlier app reading.
  - `0x40DF` 32 words `[0,2412,0,2412,13,9989,14,45913,0,0,0,0,0,827,0,956,0,6,0,6,13,49667,17,38291,0,113,0,113,3,18566,3,35149]`. Home day ~24.12 kWh; grid counter categories not yet proven. On November 1 daily and monthly totals coincide by definition.
- Mode read register **0x3647 (AppMode)**: sample returned `[0]`, consistent with SAJ Self-consumption.
- Operating mode owner's vocabulary: `0` Self-consumption, `1` Time-of-use, `2` Backup, `3` Off-grid. **Upstream code labels 3 as Passive**. This may be firmware/UI terminology disagreement; current code displays `Off-grid / Passive (firmware label unverified; avoid)`.
- **Safety requirement:** never send mode **2 Backup** or **3 Off-grid/Passive**; both caused problems in owner's experience. Backup can interfere with normal battery charge/discharge cycling and BMS reporting; Off-grid/Passive transitions caused operational trouble. Future permitted controls may eventually allow safely verified Self-consumption/Time-of-use only with explicit user direction, read-back verification, and clearly bounded limits. There must never be automatic mode changes. v0.3.0 still **read-only**.

## 5. Dashboard layout and appearance

- `dashboards/saj-energy.yaml`: 3 views: Live, Energy, Solar Forecast (new in v0.3.0).
- Live uses **panel view** with vertical stack. Top horizontal stack fixed **Live energy flow LEFT** and **Power · 24 hours RIGHT**. Histograph entities have concise `name:` overrides: `Total PV`, `House Load`, `Battery Power`, `Grid Power`.
- Next horizontal row: battery gauge, charging/discharging battery status and stored kWh, PV1/2/3 input card, battery SOC 24-hour graph. Dark theme inherited from user's HA.
- Live flow has Solar, House, Battery, Grid (grid with import and export separately). UI uses Jinja for W→kW and Wh→kWh when threshold crossed. Raw numerical sensors and 24-hour history remain in standard units for statistics.
- Energy view: today/month/year actual kWh and weekly/monthly historical statistics charts. Weekly counter examples in `examples/weekly-utility-meters.yaml`.
- **Keep clean/minimal layout**. User dislikes duplicated explanations, huge tables and verbose legend labels. Screenshot feedback requested flow & graph adjacent, less clutter. Current dashboard was successfully updated to that arrangement.
- New Solar Forecast view is committed to YAML but not yet pasted into HA. Once installed, copy whole updated YAML into HA Raw editor and validate all entity IDs, view rendering and historical actual-versus-projection graph.

## 6. Solar estimator / forecasting details (VERY IMPORTANT)

- Original user-owned Android app: **https://github.com/userdc-dev/personal-solar-estimater**; README calls it **SolarCast**. It implements seven-day hourly GTI irradiance predictions, 87% efficiency, 10 kW AC output cap, panel groups, basic battery scenario. App is an informational reference, not necessarily an installed HA integration.
- Starter group settings from app: **9 panels at 29°, 15 at 27°, 6 at 299°**, all 440 W each, tilt **25°**. These are **initial app defaults to verify against physical roof layout**; don't present angles as measured/confirmed. Compass bearing clockwise from north, converted to Open-Meteo south-zero (-180...180) azimuth.
- New `solar_model.py`: weather irradiation per panel group, multiply group kWp × GTI/1000 × 87% combined losses; **NO cap at 10 kW on total PV-side energy** (fixed after owner clarified DC-coupled battery charging). 10 kW AC output / battery DC routing are separate estimates and require accurate specifications before predictive split.
- New `solar_forecast.py`: async API calls to Open-Meteo once/hr per group, HA site coordinates (privacy disclosure needed), today / remaining / actual+remaining / tomorrow / seven-day / next-hour estimated kWh, hourly and daily attributes, learning from real solar power integrated at 10s intervals. Saves per-local-hour factors persistently in HA Store. Only relatively clear (<~25% cloud) hours with >=45 minutes covered and reasonable forecast eligible; skip high battery SOC>=97%; EWMA factors bounded [0.65,1.15].
- **Important limitation:** weather forecast error, temporary cloud, shading, MPPT constraints, clipping and forced curtailment cannot be distinguished from raw PV output alone. Never claim verified shade detection/curtailment without separate signals and comparisons. Try to separate persistent hour-of-day shade from likely AC export and DC charging constraints. Confirm whether SAJ PV "total" register can measure >10 kW and whether 3 independent MPPT values are stable.
- Current Solar Forecast view is **provisional and requires runtime validation**. Specifically verify Open-Meteo API compatibility/response format, timezone & daylight-saving handling, state names/IDs, entity availability, HA lifecycle API, and statistical non-pollution. Check count of valid hourly records, public API quotas, no repeated weather requests at 10-second cadence, and persisted learning factors.
- **Potential integration concerns to check before/while testing**:
  1. `solar_forecast.py` is new and **untested on running HA**; `aiohttp` network / HA configured lat/lon/timezone could fail. Confirm that network/API errors do not break Modbus monitoring. Weather request timeout uses aiohttp.ClientTimeout.
  2. User's v0.2.1 is last confirmed installation. v0.3.0 changes `__init__.py`, `sensor.py`; new forecast may cause load errors; have rollback instructions.
  3. Forecast learning should avoid updating from incomplete/cloud-affected/curtailed hours; make output accuracy easy to audit against measured daily totals.
  4. **Inspect first forecast sensor entity IDs**, because HA slugification of names with apostrophes may differ. Dashboard file may need edit to exactly match live IDs.
  5. Sensor graph of forecast vs actual is not a like-for-like visual: forecast is total daily/outlook, actual is accumulated daily; annotate appropriately or improve graph.
  6. API hourly time encoding and factor corrections should be checked with DST/timezone and partial first/last hours.
  7. Weekly and past history should not be invented retroactively.

## 7. Install/update/rollback workflow

**Current user state:** user last confirmed fast v0.2.1 updates and attractive live dashboard. We have already committed experimental v0.3.0 files but **the user has not confirmed downloading/installing v0.3.0 yet**.

Preferred each command its own message:
1. `curl -fL https://github.com/userdc-dev/saj-h2-safe-enhanced/archive/refs/heads/main.tar.gz -o /tmp/saj-h2-safe-enhanced.tar.gz`
2. `tar -xzf /tmp/saj-h2-safe-enhanced.tar.gz -C /tmp`
3. `cp -a /tmp/saj-h2-safe-enhanced-main/custom_components/saj_h2_safe/. /home/kamrui/compose-files/homeassistant/config/custom_components/saj_h2_safe/`
4. `docker restart homeassistant`
5. `docker logs homeassistant --since 5m 2>&1 | grep -iE 'saj_h2_safe|solar_forecast|Traceback|Error setting up' | tail -50`
6. Inspect newly appearing sensors, then have user paste full `dashboards/saj-energy.yaml` into SAJ Energy Raw dashboard editor.

**Before first installing an experimental release**, make a backup of the currently working component **outside** `custom_components`, e.g. `/home/kamrui/compose-files/homeassistant/saj_h2_safe_v0.2.1_working_backup`, and consider pinning a GitHub release/tag so rollback does not unintentionally fetch latest main. No backup has been confirmed in this chat. Do NOT overwrite user's working integration without considering recovery.

For debugging low-level Modbus, command example (READ ONLY):
`docker exec homeassistant python -c "from pymodbus.client import ModbusTcpClient; c=ModbusTcpClient('INVERTER_LAN_IP',port=502,timeout=5); c.connect(); r=c.read_holding_registers(0x3647,count=1,device_id=1); print(r.registers if not r.isError() else r); c.close()"`
Use HA configured inverter IP as substituted by user; do not hardcode LAN addresses in documentation. **Do not issue write_register(s), write_coil(s), or off-grid mode commands.**

Home Assistant's "custom integration hasn't been tested" warning is normal. Earlier real warning: `estimated_battery_energy` had ENERGY device_class + MEASUREMENT state_class; fixed in v0.2.0. Short-term statistical records appeared normally, with no hourly records immediately after initial install.

## 8. Immediate next tasks / prioritisation

1. Verify current state with user: **only v0.2.1 installed, v0.3.0 not yet tested**.
2. Audit and test new forecast model and HA integration lifecycle; check GitHub workflow compile/tests and add regression for total PV > 10 kW potential. If necessary fix issues **before installation**.
3. Create backup of working v0.2.1 integration (outside `custom_components`), then install v0.3.0 cautiously, one user command at a time. Inspect HA logs/forecast sensors.
4. Verify physically accurate 9/15/6 group headings, roof tilt, inverter PV input behaviour and battery DC charging limits with owner/documents, adjust assumptions.
5. Install/update Solar Forecast tab, get screenshot, refine clean responsive design and practical hourly/daily bar charts. Avoid long legend labels, duplicate cards, verbose disclaimers.
6. Validate grid import/export sign at naturally occurring nonzero grid flow; map `grid_sell` and `grid_feed_in` counters correctly with SAJ app before billing/energy dashboard use.
7. Add proper diagnostics distinguishing observed shade vs export/AC curtailment if the appropriate measurable inverter state is verified. Preserve raw observations and forecast comparisons for learning audit.
8. Later: opt-in settings UI for roof/panel groups, efficiency, inverter and battery limits, forecast update rate. Keep protections around modes 2/3 and write operations.
9. Improve forecasts against measured day and hour totals over days/weeks; quantify bias/error, don't promise accuracy after only one day.
10. Keep THIS HANDOFF current at every major confirmed milestone; add a clear `Current installed version` vs `Latest GitHub version` distinction.

## 9. Quick source pointers

- Main README: `README.md`.
- Main implementation: `custom_components/saj_h2_safe/__init__.py`, `sensor.py`, `const.py`, `config_flow.py`, `solar_forecast.py`, `solar_model.py`.
- Dashboard: `dashboards/saj-energy.yaml`.
- Optional weekly helpers: `examples/weekly-utility-meters.yaml`.
- Tests: `tests/test_decode.py`, `tests/test_solar_model.py`; CI `.github/workflows/validate.yml`.
- Original register research: `stanus74/home-assistant-saj-h2-modbus`, particularly `modbus_readers.py`, its `register_overview.md` and related constants. Upstream is a technical **reference** only; don't pull in its write-mode functionality without authorization.
- Owner's Android model: `userdc-dev/personal-solar-estimater`.

**Future assistant prompt:** “Read `PROJECT_HANDOFF.md`, `README.md`, current code and dashboard in `userdc-dev/saj-h2-safe-enhanced` before making changes. Respect read-only mode and blocked modes 2/3. Follow one-command-at-a-time SSH workflow. Distinguish GitHub changes from the user's actually installed HA version.”
