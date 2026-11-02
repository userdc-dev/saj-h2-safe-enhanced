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

    @staticmethod
    def async_get_options_flow(config_entry):
        return SajSafeOptionsFlow()

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



class SajSafeOptionsFlow(config_entries.OptionsFlow):
    """All forecast/system settings are editable in the native HA UI.

    Dashboard remains monitoring-only with no YAML or inverter writes.
    """
    async def async_step_init(self,user_input=None):
        errors={}
        if user_input is not None:
            if any(int(user_input.get(f"panel_{i}_count",0))>0 for i in (1,2,3)):
                return self.async_create_entry(title="",data=user_input)
            errors["base"]="at_least_one_panel"
        from .solar_model import PANEL_GROUPS
        options=self.config_entry.options
        schema={}
        for i,defaults in enumerate(PANEL_GROUPS,1):
            n,w,az,tilt=defaults
            for key,value,upper in (
                ("count",n,100),("watts",w,800),
                ("azimuth",az,360),("tilt",tilt,90)):
                name=f"panel_{i}_{key}"
                # Counts 0 allowed for unused panel orientations.
                lower=0 if key=="count" else (1 if key=="watts" else 0)
                schema[vol.Required(name,default=options.get(name,value))]=vol.All(
                    vol.Coerce(int),vol.Range(min=lower,max=upper))
        schema[vol.Required(
            "efficiency_percent",default=options.get("efficiency_percent",87)
        )]=vol.All(vol.Coerce(int),vol.Range(min=1,max=100))
        schema[vol.Required(
            "battery_capacity_kwh",default=options.get("battery_capacity_kwh",40.0)
        )]=vol.All(vol.Coerce(float),vol.Range(min=1,max=100))
        schema[vol.Required(
            "live_scan_interval",default=options.get("live_scan_interval",10)
        )]=vol.All(vol.Coerce(int),vol.Range(min=5,max=60))
        return self.async_show_form(
            step_id="init",data_schema=vol.Schema(schema),errors=errors,
            description_placeholders={
                "notice":"Review example panel counts and orientations for your actual installation. Read-only configuration."
            }
        )
