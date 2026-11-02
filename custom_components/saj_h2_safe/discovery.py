"""Read-only discovery of candidate SAJ H2 devices.

Only scan the single local /24 (when identifiable) and already known HA
config entry addresses. No external network probing and no inverter writes.
A real SAJ-like SOC + PV register response is required before presenting a
candidate; TCP port 502 alone is never sufficient.
"""
import asyncio
import inspect
import ipaddress
import logging
import socket
from pymodbus.client import AsyncModbusTcpClient

_LOGGER=logging.getLogger(__name__)
MAX_CONCURRENT=24


def known_hosts(hass):
    candidates=[]
    for entry in hass.config_entries.async_entries():
        if entry.domain not in ("saj_h2_safe","saj_h2_control_enhanced"):
            continue
        host=entry.data.get("host")
        try:
            ip=ipaddress.ip_address(host)
            if ip.version==4 and ip.is_private:
                candidates.append(str(ip))
        except (TypeError,ValueError):
            pass
    return sorted(set(candidates))


def local_subnet():
    """HA's primary LAN IP may be Docker-NAT, so never claim full coverage."""
    try:
        sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        try:
            sock.connect(("1.1.1.1",53))
            local=ipaddress.ip_address(sock.getsockname()[0])
        finally:
            sock.close()
        if local.is_private and not local.is_loopback:
            return ipaddress.ip_network(str(local)+"/24",strict=False)
    except OSError:
        pass
    return None


async def valid_saj_host(host):
    client=AsyncModbusTcpClient(host,port=502,timeout=.65,retries=0)
    try:
        if not await client.connect():
            return False
        method=client.read_holding_registers
        device={"device_id":1} if "device_id" in inspect.signature(method).parameters else {"slave":1}
        # SOC is a hundredth of one percent: 0..10000, plus valid PV1
        response=await method(address=0x406F,count=1,**device)
        if response is None or response.isError() or len(response.registers)!=1:
            return False
        soc=response.registers[0]
        if not 0<=soc<=10000:return False
        solar=await method(address=0x4071,count=3,**device)
        return bool(solar and not solar.isError() and len(solar.registers)==3
                    and solar.registers[0]!=0xFFFF)
    except (OSError,TimeoutError,ValueError,RuntimeError) as exc:
        _LOGGER.debug("SAJ discovery probe %s: %s",host,exc)
        return False
    finally:
        client.close()


async def discover(hass,include_local_subnet=True):
    """Return verified candidates. Called only from user config flow."""
    addresses=known_hosts(hass)
    if include_local_subnet:
        subnet=await hass.async_add_executor_job(local_subnet)
        if subnet and subnet.num_addresses<=256:
            addresses+=list(map(str,subnet.hosts()))
    addresses=list(dict.fromkeys(addresses))
    semaphore=asyncio.Semaphore(MAX_CONCURRENT)
    async def check(host):
        async with semaphore:
            return host if await valid_saj_host(host) else None
    matches=await asyncio.gather(*(check(h) for h in addresses),return_exceptions=True)
    return [v for v in matches if isinstance(v,str)]
