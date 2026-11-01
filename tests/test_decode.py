"""Run without Home Assistant: python3 tests/test_decode.py."""
import importlib.util
from pathlib import Path
s = importlib.util.spec_from_file_location(
    "saj_const", Path(__file__).resolve().parents[1] /
    "custom_components/saj_h2_safe/const.py"
)
m = importlib.util.module_from_spec(s)
s.loader.exec_module(m)
assert m.decode(4300, False, .01, 0, 100) == 43
assert m.decode(10100, False, .01, 0, 100) is None
assert m.decode(65535, False, 1, 0, 100) is None
assert m.decode(65535, True, 1, -2, 2) == -1
assert m.decode_energy(0, 1659) == 16.59
assert m.decode_energy(0, 2412) == 24.12
assert m.decode_energy(0xFFFF, 0xFFFF) is None
assert m.decode_energy(24, 41223) == round((24 * 65536 + 41223) / 100, 2)
assert m.ENERGY_KEYS["solar_today"][0] == 0x40BF
assert m.ENERGY_KEYS["home_today"][0] == 0x40DF
assert m.ENERGY_KEYS["grid_sell_today"][0] == 0x40EF
assert m.ENERGY_KEYS["grid_feed_in_today"][0] == 0x40F7
assert m.MODE_LABELS[0] == "Self-consumption"
assert m.MODE_LABELS[1] == "Time-of-use"
assert "Backup" in m.MODE_LABELS[2]
assert "Off-grid" in m.MODE_LABELS[3]
assert m.BLOCKED_MODE_CODES == frozenset({2, 3})
sample = [2839, 124, 354, 3231, 83, 267, 3424, 101, 341]
readings = {
    k: m.decode(sample[addr - 0x4071], signed, factor, low, high)
    for k, (addr, _, _, factor, signed, low, high) in m.SENSORS.items()
    if addr is not None and 0x4071 <= addr <= 0x4079
}
readings.update({"battery_soc": 42, "grid_power": -250})
assert m.derived_values(readings)["total_pv_power"] == 962
assert readings["battery_stored_energy"] == 17.2
assert readings["grid_import"] == 0
assert readings["grid_export"] == 250
readings["pv3_power"] = None
assert m.aggregate_solar_power(readings) is None
print("All SAJ H2 Safe Enhanced decoding checks passed.")
