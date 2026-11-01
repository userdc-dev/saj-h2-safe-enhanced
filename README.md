# SAJ H2 Safe Enhanced — v0.1.1 (experimental)

An independently written, **read-only** Home Assistant SAJ H2 integration informed by the published register mappings in [stanus74/home-assistant-saj-h2-modbus](https://github.com/stanus74/home-assistant-saj-h2-modbus).

## Safety

- **No Modbus write methods, buttons, switches, numbers, or controls.**
- Reads only two short measurement blocks using Modbus function 03.
- Battery SOC at 0x406F is decoded using a **0.01** multiplier; raw 4300 matched the owner's SAJ application reading of 43%.
- Implausible measurements and unavailable register sentinel values become `unknown`; failed polling makes entities unavailable rather than fabricating zeros.
- A single polling lock and 5-second network timeout; default polling is every 60 seconds.
- Solar voltage, solar power, current, temperature, and other readings **still need independent validation** against the SAJ app on this particular inverter.
- This integration does not disable writes performed by any *other* installed integration or third-party software.
- **Not approved by SAJ; not tested on physical hardware by the developer.** Do not rely on it for protective or safety-critical automation.

## Install or update from your Kamrui server over SSH

Run from a shell on the Home Assistant Docker host:

```bash
cd /home/kamrui/compose-files/homeassistant/config
mkdir -p custom_components/saj_h2_safe
curl -fL https://github.com/userdc-dev/saj-h2-safe-enhanced/archive/refs/heads/main.tar.gz -o /tmp/saj-h2-safe-enhanced.tar.gz
tar -xzf /tmp/saj-h2-safe-enhanced.tar.gz -C /tmp
cp -a /tmp/saj-h2-safe-enhanced-main/custom_components/saj_h2_safe/. custom_components/saj_h2_safe/
docker restart homeassistant
```

**First-time setup:** Home Assistant → Settings → Devices & services → Add Integration → SAJ H2 Safe Monitor. The current build uses a manually provided local Modbus IP and port 502. Automatic IP discovery and DHCP-change recovery have **not** been implemented yet. Prefer a router DHCP reservation in the meantime.

**Existing installation:** These commands update the integration's code in place; the configured integration and entity IDs should remain intact.

After restart, verify battery SOC and all other sensors against the official SAJ app. Your verified SAJ Modbus endpoint at the time of investigation was 172.16.1.4:502; this may change if DHCP reassigns its address.

## Source acknowledgement

Register locations and naming were informed by the upstream MIT-licensed project [stanus74/home-assistant-saj-h2-modbus](https://github.com/stanus74/home-assistant-saj-h2-modbus). This repository does not copy upstream write controls.

## Tests

```bash
python3 tests/test_decode.py
```
