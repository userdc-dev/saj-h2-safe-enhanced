"""Read-only battery and PV sensor entities."""
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, SENSORS

_CLASSES = {"W": SensorDeviceClass.POWER, "V": SensorDeviceClass.VOLTAGE,
    "A": SensorDeviceClass.CURRENT, "°C": SensorDeviceClass.TEMPERATURE,
    "%": SensorDeviceClass.BATTERY}

class SajSafeSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, key):
        super().__init__(coordinator)
        self.key = key
        _, name, unit, *_ = SENSORS[key]
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = _CLASSES[unit]
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.entry.entry_id)},
            "name": "SAJ H2 Safe Monitor", "manufacturer": "SAJ",
            "model": "H2 (unverified profile)"
        }

    @property
    def native_value(self):
        if not self.coordinator.last_update_success or self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self.key)

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([SajSafeSensor(entry.runtime_data, key) for key in SENSORS])
