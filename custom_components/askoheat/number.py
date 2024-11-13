"""Number platform for askoheat."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.number import ENTITY_ID_FORMAT, NumberEntity
from homeassistant.core import callback

from custom_components.askoheat.number_entities_config import (
    CONF_NUMBER_ENTITY_DESCRIPTIONS,
)

from .entity import AskoheatEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from custom_components.askoheat.model import (
        AskoheatNumberEntityDescription,
    )

    from .coordinator import AskoheatDataUpdateCoordinator
    from .data import AskoheatConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: AskoheatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    async_add_entities(
        AskoHeatNumber(
            coordinator=entry.runtime_data.config_coordinator,
            entity_description=entity_description,
        )
        for entity_description in CONF_NUMBER_ENTITY_DESCRIPTIONS
    )


class AskoHeatNumber(AskoheatEntity, NumberEntity):
    """askoheat number class."""

    entity_description: AskoheatNumberEntityDescription

    def __init__(
        self,
        coordinator: AskoheatDataUpdateCoordinator,
        entity_description: AskoheatNumberEntityDescription,
    ) -> None:
        """Initialize the number class."""
        super().__init__(coordinator, entity_description)
        self.entity_id = ENTITY_ID_FORMAT.format(entity_description.key)
        self._attr_unique_id = self.entity_id

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        data = self.coordinator.data
        if data is None:
            return
        self._attr_native_value = data[self.entity_description.data_key]

        if self._attr_native_value is not None:
            if self.entity_description.factor is not None:
                self._attr_native_value *= self.entity_description.factor
            if self.entity_description.native_precision is not None:
                self._attr_native_value = round(
                    self._attr_native_value, self.entity_description.native_precision
                )
        self.async_write_ha_state()
        super()._handle_coordinator_update()
