# SAJ H2 Safe Enhanced v0.2.1 — Experimental, read-only

Custom local Modbus integration for Home Assistant, developed using the public register mappings in
[stanus74/home-assistant-saj-h2-modbus](https://github.com/stanus74/home-assistant-saj-h2-modbus) and
actual H2 data from the device owner's SAJ app.

## Current features

- **Live:** total solar (PV1 + PV2 + PV3), home consumption, battery SOC, battery power, battery activity, and grid power.
- **Battery:** operating mode (register 0x3647, with unknown codes labelled), nominal-capacity-derived stored energy, voltage, current, temperature.
- **Grid:** raw signed power; separate positive/negative sensors labelled **direction unverified** until a non-zero grid-flow comparison.
- **Energy:** solar, home, battery charge/discharge, plus two SAJ-named grid counter types; today, month, year and lifetime in kWh.
- **Week:** built-in Home Assistant statistics-graph uses weekly changes to the lifetime counters. Optional weekly utility-meter examples are in `examples/`.
- **Dashboard:** `dashboards/saj-energy.yaml`, using only built-in HA cards (no HACS UI dependency).

## Safety and accuracy

- No write functions, numbers, switches, buttons, or inverter-modifying services.
- Modbus function 03 reads only. Socket timeout 5 seconds, retry count zero, default live polling 10 seconds; energy totals and mode every 60 seconds.
- Bad data is rejected; auxiliary blocks may show unavailable without disabling the core live sensors.
- Battery raw SOC 4300 was confirmed as 43.00%. Three PV inputs were confirmed by comparing 962 W to 978 W in the app.
- The register `0x40BF` gave 16.59 kWh solar today, close to the official app's earlier 16.38 kWh.
- `0x40DF` gave 24.12 kWh house consumption (needs app verification).
- App operating mode `0` is labelled Self-consumption based on the upstream control mapping and observation; other mappings need on-device validation.
- **Estimated battery energy** is SOC × **40.96 kWh nominal**, based on this owner's installed SAJ B2 40.96 kWh battery. It is NOT a BMS-measured usable-capacity value. To change the nominal capacity, set `battery_capacity_kwh` in integration entry data/options; UI editing is a future feature.
- **Grid import/export polarity and sell/feed-in counters are not confirmed.** Do not use those derived entities for billing, automation, or Energy Dashboard billing calculations until verified.
- Existing third-party inverter integrations or SAJ cloud controls are not disabled by this read-only integration.

## Operating-mode safety policy (this installation)

The owner's inverter reports AppMode at `0x3647`:
- `0` — Self-consumption (display only).
- `1` — Time-of-use (display only).
- `2` — Backup (display only; owner reports undesired side effects affecting battery cycling / BMS reporting).
- `3` — **Off-grid / Passive (ambiguous firmware terminology)**. The owner calls it Off-grid; the upstream implementation calls value 3 Passive. Display only; do not transmit.
- Unknown values appear explicitly as unknown, not as a guessed mode.

**Never expose commands that set modes 2 or 3** on this installation. In addition, never attempt off-grid or passive transitions through alternative registers. Only consider safe, separately verified controls for modes 0/1 in a later opt-in release. The current branch remains entirely **read-only**, with no device writes.

## Install / update from Kamrui server SSH

```bash
cd /home/kamrui/compose-files/homeassistant/config
curl -fL https://github.com/userdc-dev/saj-h2-safe-enhanced/archive/refs/heads/main.tar.gz -o /tmp/saj-h2-safe-enhanced.tar.gz
tar -xzf /tmp/saj-h2-safe-enhanced.tar.gz -C /tmp
cp -a /tmp/saj-h2-safe-enhanced-main/custom_components/saj_h2_safe/. custom_components/saj_h2_safe/
docker restart homeassistant
```

**Do not place backups in `custom_components`**: Home Assistant tries to load every subfolder as an integration.

The initial configuration is SAJ device IP, port 502, original saved 60-second poll setting is overridden by the new live 10-second polling default; optional `live_scan_interval` may be set to 5–60 seconds. Automatic discovery and DHCP failover are not implemented; reserve its IP in your router.

## Dashboard setup

Settings → Dashboards → Add Dashboard → New dashboard, then open its raw YAML editor and paste
[`dashboards/saj-energy.yaml`](dashboards/saj-energy.yaml). Some entity IDs may need adjustment
if you already renamed devices or entities. The dashboard is a starter interface, not a custom frontend card.

The "Energy" tab includes today/month/year totals and weekly/monthly history bar charts.
**Weekly graphs appear only after Home Assistant has recorded sufficient historical statistics**.
For a weekly number that resets each week, merge [weekly utility-meter helpers](examples/weekly-utility-meters.yaml)
into your Home Assistant configuration, then restart; those weekly counters start when created
and do not retroactively reconstruct history.

## Testing

```bash
python3 tests/test_decode.py
python3 -m compileall -q custom_components/saj_h2_safe
```

Tests check static decoder correctness, not complete compatibility or behaviour with every H2/firmware.
This is not manufacturer-supported and should not power safety-critical automations.
