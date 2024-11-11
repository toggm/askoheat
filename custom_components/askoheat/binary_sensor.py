"""Binary sensor platform for askoheat."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    ENTITY_ID_FORMAT,
    BinarySensorEntity,
)
from homeassistant.core import callback

from custom_components.askoheat.binary_sensor_entities_ema import (
    EMA_BINARY_SENSOR_ENTITY_DESCRIPTIONS,
)

from .entity import AskoheatEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from custom_components.askoheat.model import AskoheatBinarySensorEntityDescription

    from .coordinator import AskoheatDataUpdateCoordinator
    from .data import AskoheatConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: AskoheatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    async_add_entities(
        AskoheatBinarySensor(
            coordinator=entry.runtime_data.ema_coordinator,
            entity_description=entity_description,
        )
        for entity_description in EMA_BINARY_SENSOR_ENTITY_DESCRIPTIONS
    )


class AskoheatBinarySensor(AskoheatEntity, BinarySensorEntity):
    """askoheat binary_sensor class."""

    entity_description: AskoheatBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: AskoheatDataUpdateCoordinator,
        entity_description: AskoheatBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self.entity_id = ENTITY_ID_FORMAT.format(entity_description.key)
        self._attr_unique_id = self.entity_id

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        data = self.coordinator.data
        if data is None:
            return

        self._attr_state = data[self.entity_description.data_key]
        if (
            self.entity_description.on_state is True
            or self.entity_description.on_state is False
        ) and self._attr_state is not None:
            self._attr_state = bool(self._attr_state)  # type: ignore  # noqa: PGH003
        if self.entity_description.inverted:
            self._attr_is_on = self._attr_state != self.entity_description.on_state
        else:
            self._attr_is_on = self._attr_state == self.entity_description.on_state or (
                self.entity_description.on_states is not None
                and self._attr_state in self.entity_description.on_states
            )
        self.async_write_ha_state()

        super()._handle_coordinator_update()
