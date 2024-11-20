"""
Custom integration to integrate askoheat+ hot water heating with Home Assistant.

For more details about this integration, please refer to
https://github.com/toggm/askoheat
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.loader import async_get_loaded_integration

from .coordinator import (
    AskoheatConfigDataUpdateCoordinator,
    AskoheatEMADataUpdateCoordinator,
    AskoheatParameterDataUpdateCoordinator,
)
from .data import AskoheatData

from .api import AskoHeatModbusApiClient

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import AskoheatConfigEntry


PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.TIME,
    Platform.TEXT,
    Platform.SELECT,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: AskoheatConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    par_coordinator = AskoheatParameterDataUpdateCoordinator(hass=hass)
    ema_coordinator = AskoheatEMADataUpdateCoordinator(
        hass=hass,
    )
    config_coordinator = AskoheatConfigDataUpdateCoordinator(hass=hass)
    entry.runtime_data = AskoheatData(
        client=AskoHeatModbusApiClient(
            host=entry.data[CONF_HOST],
            port=entry.data[CONF_PORT],
        ),
        integration=async_get_loaded_integration(hass, entry.domain),
        ema_coordinator=ema_coordinator,
        config_coordinator=config_coordinator,
        par_coordinator=par_coordinator,
    )
    await entry.runtime_data.client.connect()

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await par_coordinator.async_config_entry_first_refresh()
    await ema_coordinator.async_config_entry_first_refresh()
    await config_coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: AskoheatConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    entry.runtime_data.client.close()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: AskoheatConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
