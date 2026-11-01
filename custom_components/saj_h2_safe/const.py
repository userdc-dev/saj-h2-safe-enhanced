DOMAIN = "saj_h2_safe"
DEFAULT_PORT = 502
DEFAULT_SCAN_INTERVAL = 60
# Register addresses informed by stanus74/home-assistant-saj-h2-modbus.
# Read-only Modbus function 03. Ranges filter implausible measurements.
SENSORS = {
    "battery_voltage": (0x4069, "Battery voltage", "V", 0.1, False, 0, 1000),
    "battery_current": (0x406A, "Battery current", "A", 0.01, True, -500, 500),
    "battery_power": (0x406D, "Battery power", "W", 1, True, -32768, 32767),
    "battery_temperature": (0x406E, "Battery temperature", "°C", 0.1, True, -40, 100),
    "battery_soc": (0x406F, "Battery state of charge", "%", 0.01, False, 0, 100),
    "pv1_voltage": (0x4071, "PV1 voltage", "V", 0.1, False, 0, 1000),
    "pv1_power": (0x4073, "PV1 power", "W", 1, False, 0, 30000),
    "pv2_voltage": (0x4074, "PV2 voltage", "V", 0.1, False, 0, 1000),
    "pv2_power": (0x4076, "PV2 power", "W", 1, False, 0, 30000),
}

def decode(raw, signed, scale, low, high):
    if not isinstance(raw, int) or not 0 <= raw <= 65535:
        return None
    if not signed and raw == 0xFFFF:
        return None
    value = (raw - 65536 if signed and raw & 0x8000 else raw) * scale
    if not low <= value <= high:
        return None
    return round(value, 3)
