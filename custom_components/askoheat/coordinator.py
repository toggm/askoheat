"""DataUpdateCoordinator for askoheat."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import async_timeout
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    AskoheatModbusApiClientError,
)
from .const import DOMAIN, LOGGER, SCAN_INTERVAL_EMA

if TYPE_CHECKING:
    from datetime import timedelta

    from homeassistant.core import HomeAssistant

    from custom_components.askoheat.data import AskoheatEMAData

    from .data import AskoheatConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class AskoheatDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching state of askoheat through a single API call."""

    config_entry: AskoheatConfigEntry

    def __init__(self, hass: HomeAssistant, scan_interval: timedelta) -> None:
        """Initialize."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=scan_interval,
            # Set always_update to `False` if the data returned from the
            # api can be compared via `__eq__` to avoid duplicate updates
            # being dispatched to listeners
            always_update=True,
        )


class AskoheatEMADataUpdateCoordinator(AskoheatDataUpdateCoordinator):
    """Class to manage fetching askoheat energymanager states."""

    config_entry: AskoheatConfigEntry
    data: AskoheatEMAData

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize."""
        super().__init__(hass=hass, scan_interval=SCAN_INTERVAL_EMA)

    async def _async_update_data(self) -> dict[str, Any]:
        """Update ema data via library."""
        try:
            async with async_timeout.timeout(10):
                data = await self.config_entry.runtime_data.client.async_read_ema_data()
                result: dict[str, Any] = {}
                result.update(
                    {
                        f"binary_sensor.{k}": data.binary_sensors[k]
                        for k in data.binary_sensors
                    }
                )
                result.update({f"sensor.{k}": data.sensors[k] for k in data.sensors})
                result.update({f"switch.{k}": data.switches[k] for k in data.switches})
                return result
        except AskoheatModbusApiClientError as exception:
            raise UpdateFailed(exception) from exception
