"""SAJ H2 Safe Monitor: deliberately read-only; no Modbus writes."""
from datetime import timedelta
import asyncio
import inspect
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pymodbus.client import AsyncModbusTcpClient
from .const import DEFAULT_SCAN_INTERVAL, SENSORS, aggregate_solar_power, decode

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]

class SajSafeCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        self.entry = entry
        self._lock = asyncio.Lock()
        self.failures = 0
        super().__init__(
            hass, _LOGGER, name="SAJ H2 Safe Monitor",
            update_interval=timedelta(seconds=entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL))
        )

    async def _async_update_data(self):
        # Serialize polling; use one bounded connection per poll.
        async with self._lock:
            client = AsyncModbusTcpClient(
                self.entry.data["host"], port=self.entry.data["port"],
                timeout=5, retries=0
            )
            try:
                if not await client.connect():
                    raise UpdateFailed("Cannot connect to SAJ Modbus device")
                read = client.read_holding_registers
                sig = inspect.signature(read).parameters
                unit_kw = {"device_id": 1} if "device_id" in sig else {"slave": 1}
                result = {}
                # Only measurement registers. PV1, PV2, PV3 are read together.
                for address, count in ((0x4069, 7), (0x4071, 9)):
                    response = await read(address=address, count=count, **unit_kw)
                    if response is None or response.isError() or len(response.registers) != count:
                        raise UpdateFailed(f"Invalid Modbus response for {address:#06x}")
                    result.update({address + idx: value for idx, value in enumerate(response.registers)})
                parsed = {}
                for key, (address, _, _, factor, signed, low, high) in SENSORS.items():
                    if address is not None:
                        parsed[key] = decode(result[address], signed, factor, low, high)
                parsed["total_pv_power"] = aggregate_solar_power(parsed)
                if parsed["battery_soc"] is None:
                    raise UpdateFailed("Battery SOC invalid or unsupported; no values published")
                self.failures = 0
                return parsed
            except UpdateFailed:
                self.failures += 1
                raise
            except Exception as exc:
                self.failures += 1
                raise UpdateFailed(f"SAJ read failed: {type(exc).__name__}") from exc
            finally:
                client.close()

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = SajSafeCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
