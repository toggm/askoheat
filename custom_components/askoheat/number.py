"""Number platform for askoheat."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.number import (
    ENTITY_ID_FORMAT,
    NumberEntity,
    NumberMode,
    RestoreNumber,
)
from homeassistant.const import (
    UnitOfPower,
)
from homeassistant.core import callback

from custom_components.askoheat.api_conf_desc import CONF_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_ema_desc import EMA_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.const import LOGGER, DeviceKey, NumberAttrKey
from custom_components.askoheat.model import (
    AskoheatNumberEntityDescription,
)

from .entity import AskoheatBaseEntity, AskoheatEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import AskoheatDataUpdateCoordinator
    from .data import AskoheatConfigEntry

EMA_FEED_IN_BUFFER_ENTITY_POSTFIX = "auto_feed_in_buffer"


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: AskoheatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    async_add_entities(
        AskoheatNumber(
            entry=entry,
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description, coordinator in {
            **dict.fromkeys(
                EMA_REGISTER_BLOCK_DESCRIPTOR.number_inputs,
                entry.runtime_data.ema_coordinator,
            ),
            **dict.fromkeys(
                CONF_REGISTER_BLOCK_DESCRIPTOR.number_inputs,
                entry.runtime_data.config_coordinator,
            ),
        }.items()
        if entity_description.device_key is None
        or entity_description.device_key in entry.runtime_data.supported_devices
    )
    async_add_entities(
        [
            AskoheatAutoFeedInBufferNumber(
                entry=entry,
                entity_description=AskoheatNumberEntityDescription(
                    key=NumberAttrKey.EMA_AUTO_FEEDIN_BUFFER,
                    device_key=DeviceKey.ENERGY_MANAGER,
                    native_default_value=0,
                    native_unit_of_measurement=UnitOfPower.WATT,
                    native_min_value=-30000,
                    native_max_value=30000,
                    native_precision=0,
                    native_step=1,
                    mode=NumberMode.BOX,
                    icon="mdi:gate-buffer",
                    api_descriptor=None,
                ),
            )
        ]
    )


class AskoheatNumber(AskoheatEntity[AskoheatNumberEntityDescription], NumberEntity):
    """askoheat number class."""

    entity_description: AskoheatNumberEntityDescription

    def __init__(
        self,
        entry: AskoheatConfigEntry,
        coordinator: AskoheatDataUpdateCoordinator,
        entity_description: AskoheatNumberEntityDescription,
    ) -> None:
        """Initialize the number class."""
        super().__init__(entry, coordinator, entity_description)
        self.entity_id = ENTITY_ID_FORMAT.format(
            f"{self._device_unique_id}_{entity_description.key}"
        )
        self._attr_unique_id = self.entity_id

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            super().available
            and self.entity_description.data_key in self.coordinator.data
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        data = self.coordinator.data
        if data is None or data.get(self.entity_description.data_key) is None:
            return
        self._attr_native_value = data[self.entity_description.data_key]

        if self._attr_native_value is not None:
            if self.entity_description.factor is not None:
                self._attr_native_value *= self.entity_description.factor
            if self.entity_description.native_precision is not None:
                self._attr_native_value = self._attr_native_value.__round__(
                    self.entity_description.native_precision
                )
        super()._handle_coordinator_update()

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        if self.entity_description.api_descriptor is None:
            LOGGER.error(
                "Cannot set native value, missing api_descriptor on entity %s",
                self.entity_id,
            )
            return
        if self.entity_description.factor is not None:
            value = float(value / self.entity_description.factor)
        if self.entity_description.native_step is not None:
            value = (
                round(value / self.entity_description.native_step)
                * self.entity_description.native_step
            )
        await self.coordinator.async_write(
            self.entity_description.api_descriptor, value
        )
        self._handle_coordinator_update()


class AskoheatAutoFeedInBufferNumber(
    AskoheatBaseEntity[AskoheatNumberEntityDescription], RestoreNumber, NumberEntity
):
    """Representation of a buffer entity for the auto-feed-in mechanism."""

    entity_description: AskoheatNumberEntityDescription

    def __init__(
        self,
        entry: AskoheatConfigEntry,
        entity_description: AskoheatNumberEntityDescription,
    ) -> None:
        """Initialize auto-feed-in buffer entity."""
        super().__init__(entry=entry, entity_description=entity_description)
        self.entity_id = ENTITY_ID_FORMAT.format(
            f"{self._device_unique_id}_{entity_description.key}"
        )
        self._attr_unique_id = self.entity_id

    async def async_added_to_hass(self) -> None:
        """Call when entity about to be added to hass."""
        if last_number_data := await self.async_get_last_number_data():
            self._attr_native_value = last_number_data.native_value

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        self._attr_native_value = int(value)
        self.async_write_ha_state()
