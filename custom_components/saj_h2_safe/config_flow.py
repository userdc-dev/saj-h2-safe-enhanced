"""SAJ H2 Safe Monitor setup: automatic LAN discovery with manual fallback.

Only the config flow probes the LAN; no unattended subnet scans. Inverter
verification is read-only and rejects unrelated Modbus servers.
"""
import ipaddress
import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, DEFAULT_PORT
from .discovery import discover, valid_saj_host, known_hosts


class SajSafeFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION=1

    async def async_step_user(self,user_input=None):
        """Offer verified automatic candidates first; always allow host fallback."""
        if user_input is not None:
            choice=user_input.get("choice")
            if choice=="manual":
                return await self.async_step_manual()
            if choice=="scan":
                return await self.async_step_discover()
            if choice:
                return await self._create_from_host(choice)
        return await self.async_step_discover()

    async def async_step_discover(self,user_input=None):
        # On a Docker bridge this may scan the bridge subnet rather than the
        # LAN; also try addresses of existing control entries. Manual fallback
        # always remains available.
        candidates=await discover(self.hass)
        if len(candidates)==1:
            return await self._create_from_host(candidates[0])
        if candidates:
            options={host:"SAJ H2 inverter at "+host for host in candidates}
            options["manual"]="Enter IP address manually"
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({vol.Required("choice"):vol.In(options)}),
            )
        return await self.async_step_manual()

    async def async_step_manual(self,user_input=None):
        errors={}
        if user_input is not None:
            host=str(user_input["host"]).strip()
            try:
                ip=ipaddress.ip_address(host)
                if ip.version!=4 or not ip.is_private:
                    errors["base"]="invalid_host"
                elif not await valid_saj_host(host):
                    errors["base"]="cannot_connect"
                else:
                    return await self._create_from_host(host)
            except ValueError:
                errors["base"]="invalid_host"
        return self.async_show_form(
            step_id="manual",
            data_schema=vol.Schema({
                vol.Required("host",default=(known_hosts(self.hass)[0] if known_hosts(self.hass) else "")):str,
            }),errors=errors
        )

    async def _create_from_host(self,host):
        await self.async_set_unique_id(host)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title="SAJ H2 Safe ("+host+")",
            data={"host":host,"port":DEFAULT_PORT},
        )
