"""Solar model smoke tests: python3 tests/test_solar_model.py."""
from pathlib import Path
import importlib.util
from datetime import datetime, timezone
root = Path(__file__).resolve().parents[1]
path = root / "custom_components/saj_h2_safe/solar_model.py"
spec = importlib.util.spec_from_file_location("saj_solar_model", path)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)

assert len(model.PANEL_GROUPS) == 3
assert sum(x[0] * x[1] for x in model.PANEL_GROUPS) == 13200
assert model.INVERTER_AC_KW == 10.0
assert model.api_azimuth(180) == 0
assert model.api_azimuth(90) == -90
assert model.api_azimuth(270) == 90
# Irradiance yields >10 kWh from ~13 kWp panels in an exceptionally strong
# irradiance hour; must NOT clip PV generation at the 10 kW AC output limit.
end = int(datetime(2026, 11, 2, 2, tzinfo=timezone.utc).timestamp())
series = [{
    "time": [end],
    "global_tilted_irradiance": [1200],
    "cloud_cover": [0],
} for _ in model.PANEL_GROUPS]
hour = model.hour_records(series)[end]
assert hour["base_kwh"] > 10
assert hour["kwh"] > 10
assert model.learn_factor(1.0, 0.2, 4.0, 80, 3600) is None
assert model.learn_factor(1.0, 0.2, 4.0, 0, 3600) is None
assert model.learn_factor(1.0, 0.2, 4.0, 0, 3600, 99) is None
assert model.learn_factor(1.0, 3.5, 4.0, 0, 3500) < 1.0
print("Solar forecast model smoke tests passed")
