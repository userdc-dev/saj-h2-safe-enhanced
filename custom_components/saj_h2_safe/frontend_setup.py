"""Independent read-only monitoring dashboard for SAJ H2 Safe Enhanced.

Never alter the TOU control dashboard, other Lovelace views, stored user
dashboards or inverter configuration. Frontend registration failure must not
prevent the existing monitoring entities from loading.
"""
import logging
from pathlib import Path

from homeassistant.components.http import StaticPathConfig

_LOGGER = logging.getLogger(__name__)
URL = "/saj-h2-safe/v042/saj-safe-monitor-card.js"
RESOURCE_PREFIX = "/saj-h2-safe/"
PATH = "saj-safe-monitor"
CARD = "custom:saj-safe-monitor-card"


async def async_register_frontend(hass):
    """Serve the bundle and install it as a persistent Lovelace module.

    In storage resource mode, Lovelace resources load *after* frontend custom
    element polyfills. add_extra_js_url can run too early and lose the card's
    customElements registration, especially on mobile. YAML resource mode
    cannot be written to; use extra JS only for that fallback.
    """
    try:
        js = Path(__file__).parent / "frontend" / "saj-safe-monitor-card.js"
        await hass.http.async_register_static_paths(
            [StaticPathConfig(URL, str(js), False)])
    except Exception:
        _LOGGER.exception("Could not serve SAJ monitoring card; sensors remain available")
        return
    await async_ensure_card_resource(hass)


async def async_ensure_card_resource(hass):
    """Register or update ONLY our card resource; do not touch other cards."""
    try:
        from homeassistant.components.lovelace import LOVELACE_DATA
        from homeassistant.components.lovelace.const import MODE_STORAGE
        lovelace = hass.data.get(LOVELACE_DATA)
        if lovelace is None:
            _LOGGER.debug("Lovelace not ready; registering SAJ card after startup")
            return False

        if lovelace.resource_mode != MODE_STORAGE:
            # No YAML editing required; fallback global registration is the
            # only supported programmatic route for YAML resource mode.
            from homeassistant.components.frontend import add_extra_js_url
            add_extra_js_url(hass, URL)
            _LOGGER.info("SAJ monitoring card registered via YAML-mode fallback")
            return True

        collection = lovelace.resources
        # Important: resources are LAZY loaded on many HA releases. Calling
        # async_items() before load can replace the user's existing resources.
        await collection.async_get_info()
        matching = [
            item for item in collection.async_items()
            if str(item.get("url", "")).startswith(RESOURCE_PREFIX)
            and "saj-safe-monitor-card.js" in str(item.get("url", ""))
        ]
        current = next((item for item in matching
                        if item.get("url") == URL and item.get("type") == "module"), None)
        if current is None and matching:
            # Migrate precisely our resource. Do not overwrite unrelated cards.
            original = matching[0]
            await collection.async_update_item(
                original["id"], {"url": URL, "type": "module"})
        elif current is None:
            await collection.async_create_item({"url": URL, "type": "module"})
        _LOGGER.info("SAJ monitoring Lovelace resource ready: %s", URL)
        return True
    except Exception:
        _LOGGER.exception("Could not register SAJ Lovelace resource; retry after startup")
        return False


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
