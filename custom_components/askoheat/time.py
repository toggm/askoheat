"""Askoheat time entity."""

from datetime import time

from homeassistant.components.time import ENTITY_ID_FORMAT, TimeEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.askoheat.api_conf_desc import CONF_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_ema_desc import EMA_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_par_desc import PARAM_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.const import LOGGER
from custom_components.askoheat.coordinator import AskoheatDataUpdateCoordinator
from custom_components.askoheat.model import AskoheatTimeEntityDescription

from .data import AskoheatConfigEntry
from .entity import AskoheatEntity


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: AskoheatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the text platform."""
    async_add_entities(
        AskoheatTime(
            entry=entry,
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description, coordinator in {
            **dict.fromkeys(
                PARAM_REGISTER_BLOCK_DESCRIPTOR.time_inputs,
                entry.runtime_data.par_coordinator,
            ),
            **dict.fromkeys(
                EMA_REGISTER_BLOCK_DESCRIPTOR.time_inputs,
                entry.runtime_data.ema_coordinator,
            ),
            **dict.fromkeys(
                CONF_REGISTER_BLOCK_DESCRIPTOR.time_inputs,
                entry.runtime_data.config_coordinator,
            ),
        }.items()
        if entity_description.device_key is None
        or entity_description.device_key in entry.runtime_data.supported_devices
    )


class AskoheatTime(AskoheatEntity[AskoheatTimeEntityDescription], TimeEntity):
    """Askoheat time entity."""

    entity_description: AskoheatTimeEntityDescription

    def __init__(
        self,
        entry: AskoheatConfigEntry,
        coordinator: AskoheatDataUpdateCoordinator,
        entity_description: AskoheatTimeEntityDescription,
    ) -> None:
        """Initialize the time class."""
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
        self.native_value = data[self.entity_description.data_key]
        super()._handle_coordinator_update()

    async def async_set_value(self, value: time) -> None:
        """Update the current value."""
        if self.entity_description.api_descriptor is None:
            LOGGER.error(
                "Cannot set value, missing api_descriptor on entity %s", self.entity_id
            )
            return
        await self.coordinator.async_write(
            self.entity_description.api_descriptor, value
        )
        self._handle_coordinator_update()
