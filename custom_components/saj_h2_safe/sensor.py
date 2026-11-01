"""Read-only SAJ H2 measurement and energy sensors."""
from homeassistant.components.sensor import (
    SensorEntity, SensorDeviceClass, SensorStateClass,
)
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, SENSORS, ENERGY_KEYS

_CLASSES = {
    "W": SensorDeviceClass.POWER,
    "V": SensorDeviceClass.VOLTAGE,
    "A": SensorDeviceClass.CURRENT,
    "°C": SensorDeviceClass.TEMPERATURE,
    "%": SensorDeviceClass.BATTERY,
    "kWh": SensorDeviceClass.ENERGY,
}
_DIAGNOSTIC_KEYS = {
    "battery_voltage", "battery_current", "battery_temperature",
    "pv1_voltage", "pv2_voltage", "pv3_voltage", "grid_power",
}
# Counters are labelled by period. Weekly rollups are provided by Home
# Assistant utility_meter using the lifetime ('total') energy counters.

class SajSafeSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, coordinator, key):
        super().__init__(coordinator)
        self.key = key
        if key in SENSORS:
            _, name, unit, *_ = SENSORS[key]
            state_class = SensorStateClass.MEASUREMENT
        elif key == "operating_mode":
            name, unit, state_class = "Operating mode", None, None
        else:
            _, name = ENERGY_KEYS[key]
            unit = "kWh"
            state_class = (
                SensorStateClass.TOTAL_INCREASING if key.endswith("_total")
                else SensorStateClass.TOTAL
            )

        self._attr_name = name
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{key}"
        self._attr_native_unit_of_measurement = unit
        if unit is not None:
            self._attr_device_class = _CLASSES[unit]
        if state_class is not None:
            self._attr_state_class = state_class
        if key in _DIAGNOSTIC_KEYS:
            self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.entry.entry_id)},
            "name": "SAJ H2 Safe Monitor",
            "manufacturer": "SAJ",
            "model": "H2 (register profile under verification)",
        }

    @property
    def native_value(self):
        if not self.coordinator.last_update_success or self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self.key)

async def async_setup_entry(hass, entry, async_add_entities):
    keys = [*SENSORS, "operating_mode", *ENERGY_KEYS]
    async_add_entities([SajSafeSensor(entry.runtime_data, key) for key in keys])
