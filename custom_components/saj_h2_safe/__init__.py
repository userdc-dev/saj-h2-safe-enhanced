"""SAJ H2 Safe Enhanced — read-only Modbus poller."""
from datetime import timedelta
import asyncio
import inspect
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pymodbus.client import AsyncModbusTcpClient
from .const import (
    DEFAULT_SCAN_INTERVAL, DEFAULT_BATTERY_CAPACITY_KWH, SENSORS,
    ENERGY_KEYS, MODE_LABELS, decode, decode_energy, derived_values,
)

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]

class SajSafeCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        self.entry = entry
        self._lock = asyncio.Lock()
        self.failures = 0
        super().__init__(
            hass, _LOGGER, name="SAJ H2 Safe Enhanced",
            update_interval=timedelta(
                seconds=max(30, entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL))
            ),
        )

    async def _async_update_data(self):
        # Only read_holding_registers (Modbus function 03) is used.
        # Never auto-write, reconfigure the inverter, or publish fake zeros.
        async with self._lock:
            client = AsyncModbusTcpClient(
                self.entry.data["host"], port=self.entry.data["port"],
                timeout=5, retries=0,
            )
            try:
                if not await client.connect():
                    raise UpdateFailed("Cannot connect to SAJ inverter")
                read = client.read_holding_registers
                kw = {"device_id": 1} if "device_id" in inspect.signature(read).parameters else {"slave": 1}

                async def fetch(address, count):
                    response = await read(address=address, count=count, **kw)
                    if response is None or response.isError() or len(response.registers) != count:
                        raise ValueError(f"Modbus response invalid for {address:#06x}")
                    return response.registers

                result = {}
                # The original established three groups must succeed.
                for address, count in ((0x4069, 7), (0x4071, 9), (0x40A0, 14)):
                    words = await fetch(address, count)
                    result.update({address + n: value for n, value in enumerate(words)})

                parsed = {}
                for key, (address, _, _, factor, signed, low, high) in SENSORS.items():
                    if address is not None:
                        parsed[key] = decode(result[address], signed, factor, low, high)

                if parsed["battery_soc"] is None:
                    raise UpdateFailed("Battery SOC invalid; data discarded")

                capacity = self.entry.options.get(
                    "battery_capacity_kwh",
                    self.entry.data.get("battery_capacity_kwh", DEFAULT_BATTERY_CAPACITY_KWH),
                )
                derived_values(parsed, capacity)

                # Read-only mode codes: unmapped codes are displayed explicitly.
                try:
                    code = (await fetch(0x3647, 1))[0]
                    parsed["operating_mode"] = MODE_LABELS.get(code, f"Unknown (code {code})")
                except Exception as exc:
                    _LOGGER.debug("Operating mode unavailable: %s", exc)
                    parsed["operating_mode"] = None

                # Optional energy counter blocks. Failure of either block must
                # not suppress live readings or reuse stale energy data.
                for start in (0x40BF, 0x40DF):
                    try:
                        words = await fetch(start, 32)
                        result.update({start + n: value for n, value in enumerate(words)})
                    except Exception as exc:
                        _LOGGER.debug("Optional energy block %04X unavailable: %s", start, exc)

                for key, (address, _) in ENERGY_KEYS.items():
                    if address in result and address + 1 in result:
                        parsed[key] = decode_energy(result[address], result[address + 1])
                    else:
                        parsed[key] = None

                self.failures = 0
                return parsed
            except UpdateFailed:
                self.failures += 1
                raise
            except Exception as exc:
                self.failures += 1
                raise UpdateFailed(f"SAJ read failed: {type(exc).__name__}: {exc}") from exc
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
