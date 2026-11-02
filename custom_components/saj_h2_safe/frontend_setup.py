"""Independent read-only monitoring dashboard for SAJ H2 Safe Enhanced.

Never alter the TOU control dashboard, other Lovelace views, stored user
dashboards or inverter configuration. Frontend registration failure must not
prevent the existing monitoring entities from loading.
"""
import logging
from pathlib import Path

from homeassistant.components.http import StaticPathConfig

_LOGGER = logging.getLogger(__name__)
URL = "/saj-h2-safe/v041/saj-safe-monitor-card.js"
PATH = "saj-safe-monitor"
CARD = "custom:saj-safe-monitor-card"


async def async_register_frontend(hass):
    try:
        js = Path(__file__).parent / "frontend" / "saj-safe-monitor-card.js"
        await hass.http.async_register_static_paths(
            [StaticPathConfig(URL, str(js), False)])
        from homeassistant.components.frontend import add_extra_js_url
        add_extra_js_url(hass, URL)
    except Exception:
        _LOGGER.exception("Could not register safe monitoring card; sensors remain available")


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
