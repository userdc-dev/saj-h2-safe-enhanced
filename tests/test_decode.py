import importlib.util
from pathlib import Path

s = importlib.util.spec_from_file_location(
    "saj_const", Path(__file__).resolve().parents[1] /
    "custom_components/saj_h2_safe/const.py"
)
m = importlib.util.module_from_spec(s)
s.loader.exec_module(m)
assert m.decode(65535, False, 1, 0, 100) is None
assert m.decode(65535, True, 1, -2, 2) == -1
assert m.decode(101, False, 1, 0, 100) is None
assert m.decode(75, False, 1, 0, 100) == 75
assert m.decode(65534, True, 0.01, -500, 500) == -0.02
assert m.decode(4300, False, 0.01, 0, 100) == 43.0
assert m.decode(10100, False, 0.01, 0, 100) is None
sample = [2839, 124, 354, 3231, 83, 267, 3424, 101, 341]
readings = {key: m.decode(sample[address - 0x4071], signed, scale, lo, hi)
    for key, (address, _, _, scale, signed, lo, hi) in m.SENSORS.items()
    if address is not None and 0x4071 <= address < 0x407A}
assert readings["pv3_voltage"] == 342.4
assert readings["pv3_power"] == 341
assert m.aggregate_solar_power(readings) == 962
readings["pv3_power"] = None
assert m.aggregate_solar_power(readings) is None
print("decode checks passed")
