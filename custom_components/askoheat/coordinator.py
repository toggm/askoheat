"""DataUpdateCoordinator for askoheat."""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any

import async_timeout
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    AskoHeatModbusApiClient,
    AskoheatModbusApiClientError,
)
from .const import DOMAIN, LOGGER, SCAN_INTERVAL_CONFIG, SCAN_INTERVAL_EMA

if TYPE_CHECKING:
    from datetime import timedelta

    from homeassistant.core import HomeAssistant

    from custom_components.askoheat.api_desc import RegisterInputDescriptor
    from custom_components.askoheat.data import AskoheatDataBlock

    from .data import AskoheatConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class AskoheatDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching state of askoheat through a single API call."""

    config_entry: AskoheatConfigEntry
    _writing: bool = False

    def __init__(self, hass: HomeAssistant, scan_interval: timedelta | None) -> None:
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

    @abstractmethod
    async def async_write(
        self, api_desc: RegisterInputDescriptor, value: object
    ) -> None:
        """Write parameter to Askoheat."""


class AskoheatEMADataUpdateCoordinator(AskoheatDataUpdateCoordinator):
    """Class to manage fetching askoheat energymanager states."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize."""
        super().__init__(hass=hass, scan_interval=SCAN_INTERVAL_EMA)

    async def _async_update_data(self) -> dict[str, Any]:
        """Update ema data via library."""
        # prevent concurrent reads while writing is in progress
        if self._writing:
            return self.data
        try:
            async with async_timeout.timeout(10):
                data = await self.config_entry.runtime_data.client.async_read_ema_data()
                return _map_data_block_to_dict(data)
        except AskoheatModbusApiClientError as exception:
            raise UpdateFailed(exception) from exception

    async def async_write(
        self, api_desc: RegisterInputDescriptor, value: object
    ) -> None:
        """Write parameter ema block of Askoheat."""
        try:
            self._writing = True
            async with async_timeout.timeout(10):
                data = await self.config_entry.runtime_data.client.async_write_ema_data(
                    api_desc, value
                )
                self.data = _map_data_block_to_dict(data)
        except AskoheatModbusApiClientError as exception:
            raise UpdateFailed(exception) from exception
        finally:
            self._writing = False


class AskoheatConfigDataUpdateCoordinator(AskoheatDataUpdateCoordinator):
    """Class to manage fetching askoheat configuration states."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize."""
        super().__init__(hass=hass, scan_interval=SCAN_INTERVAL_CONFIG)

    async def _async_update_data(self) -> dict[str, Any]:
        """Update config data via library."""
        # prevent concurrent reads while writing is in progress
        if self._writing:
            return self.data
        try:
            async with async_timeout.timeout(10):
                data = (
                    await self.config_entry.runtime_data.client.async_read_config_data()
                )
                return _map_data_block_to_dict(data)
        except AskoheatModbusApiClientError as exception:
            raise UpdateFailed(exception) from exception

    async def async_write(
        self, api_desc: RegisterInputDescriptor, value: object
    ) -> None:
        """Write parameter ema block of Askoheat."""
        try:
            self._writing = True
            async with async_timeout.timeout(10):
                data = (
                    await self.config_entry.runtime_data.client.async_write_config_data(
                        api_desc, value
                    )
                )
                self.data = _map_data_block_to_dict(data)
        except AskoheatModbusApiClientError as exception:
            raise UpdateFailed(exception) from exception
        finally:
            self._writing = False


class AskoheatParameterDataUpdateCoordinator(AskoheatDataUpdateCoordinator):
    """Class to manage fetching askoheat parameter states."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize."""
        super().__init__(hass=hass, scan_interval=None)

    async def _async_update_data(self) -> dict[str, Any]:
        """Update parameter data via library."""
        return await self.load_parameters(self.config_entry.runtime_data.client)

    async def load_parameters(self, client: AskoHeatModbusApiClient) -> dict[str, Any]:
        """Load askoheat parameters through provided client."""
        try:
            async with async_timeout.timeout(10):
                data = await client.async_read_par_data()
                return _map_data_block_to_dict(data)
        except AskoheatModbusApiClientError as exception:
            raise UpdateFailed(exception) from exception

    async def async_write(self, _: RegisterInputDescriptor, __: object) -> None:
        """Write parameter par block of Askoheat."""
        raise UpdateFailed("Writing values to parameters not allowed")


def _map_data_block_to_dict(data: AskoheatDataBlock) -> dict[str, Any]:
    """Map askoheat data block to dict."""
    result: dict[str, Any] = {}
    if data.binary_sensors:
        result.update(
            {f"binary_sensor.{k}": data.binary_sensors[k] for k in data.binary_sensors}
        )

    if data.sensors:
        result.update({f"sensor.{k}": data.sensors[k] for k in data.sensors})

    if data.switches:
        result.update({f"switch.{k}": data.switches[k] for k in data.switches})

    if data.number_inputs:
        result.update(
            {f"number.{k}": data.number_inputs[k] for k in data.number_inputs}
        )

    if data.text_inputs:
        result.update({f"text.{k}": data.text_inputs[k] for k in data.text_inputs})

    if data.select_inputs:
        result.update(
            {f"select.{k}": data.select_inputs[k] for k in data.select_inputs}
        )

    if data.time_inputs:
        result.update({f"time.{k}": data.time_inputs[k] for k in data.time_inputs})
    return result
