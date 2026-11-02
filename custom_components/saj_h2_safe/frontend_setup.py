"""Independent read-only monitoring dashboard for SAJ H2 Safe Enhanced.

Never alter the TOU control dashboard, other Lovelace views, stored user
dashboards or inverter configuration. Frontend registration failure must not
prevent the existing monitoring entities from loading.
"""
import logging
from pathlib import Path

from homeassistant.components.http import StaticPathConfig

_LOGGER = logging.getLogger(__name__)
URL = "/saj-h2-safe/v040/saj-safe-monitor-card.js"
PATH = "saj-safe-monitor"
CARD = "custom:saj-safe-monitor-card"


async def async_register_frontend(hass):
    try:
        js = Path(__file__).parent / "frontend" / "saj-safe-monitor-card.js"
        await hass.http.async_register_static_paths(
            [StaticPathConfig(URL, str(js), False)])
        from homeassistant.components.frontend import add_extra_js_url
        add_extra_js_url(hass, URL)
        await async_cleanup_newer_card_resource(hass)
    except Exception:
        _LOGGER.exception("Could not register safe monitoring card; sensors remain available")


async def async_cleanup_newer_card_resource(hass):
    """One-time rollback cleanup for the broken v0.4.2 Lovelace module.

    v0.4.0 uses the original frontend script registration and must not also
    load the later v0.4.1/v0.4.2 Lovelace module. Only touch the exact
    versioned resource urls added by those releases. Never delete any
    user-created dashboard, resource, or custom integration.
    """
    try:
        from homeassistant.components.lovelace import LOVELACE_DATA
        from homeassistant.components.lovelace.const import MODE_STORAGE
        lovelace = hass.data.get(LOVELACE_DATA)
        if lovelace is None or lovelace.resource_mode != MODE_STORAGE:
            return
        resources = lovelace.resources
        await resources.async_get_info()
        old_urls = {
            "/saj-h2-safe/v041/saj-safe-monitor-card.js",
            "/saj-h2-safe/v042/saj-safe-monitor-card.js",
        }
        for resource in list(resources.async_items()):
            if resource.get("url") in old_urls:
                await resources.async_delete_item(resource["id"])
                _LOGGER.info(
                    "Cleaned up incompatible SAJ monitoring resource %s",
                    resource["url"],
                )
    except Exception:
        _LOGGER.exception("SAJ rollback resource cleanup could not complete")


async def async_ensure_dashboard(hass):
    """Create once only. Existing/user-customized dashboards are immutable."""
    try:
        from homeassistant.components import frontend
        from homeassistant.components.lovelace import LOVELACE_DATA
        from homeassistant.components.lovelace.dashboard import (
            DashboardsCollection, LovelaceStorage)
        from homeassistant.components.lovelace.const import MODE_STORAGE

        lovelace = hass.data.get(LOVELACE_DATA)
        if lovelace is None or PATH in lovelace.dashboards:
            return
        collection = DashboardsCollection(hass)
        await collection.async_load()
        if any(x.get("url_path") == PATH for x in collection.async_items()):
            return
        record = await collection.async_create_item({
            "url_path": PATH,
            "title": "SAJ Energy",
            "icon": "mdi:solar-power",
            "show_in_sidebar": True,
        })
        board = LovelaceStorage(hass, record)
        lovelace.dashboards[PATH] = board
        await board.async_save({
            "title": "SAJ Energy",
            "views": [{
                "title": "SAJ Energy",
                "path": "monitor",
                "icon": "mdi:solar-power",
                "type": "panel",
                "cards": [{"type": CARD}],
            }],
        })
        frontend.async_register_built_in_panel(
            hass, "lovelace", frontend_url_path=PATH,
            require_admin=False, show_in_sidebar=True,
            sidebar_title="SAJ Energy", sidebar_icon="mdi:solar-power",
            config={"mode": MODE_STORAGE}, update=False)
        _LOGGER.info("Created minimal independent SAJ Energy monitoring dashboard")
    except Exception:
        _LOGGER.exception(
            "Could not create SAJ Energy dashboard; sensors continue working. "
            "You can manually add custom:saj-safe-monitor-card to any dashboard."
        )
