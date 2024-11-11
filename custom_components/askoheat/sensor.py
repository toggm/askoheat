"""Sensor platform for askoheat."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from homeassistant.components.sensor import ENTITY_ID_FORMAT, SensorEntity
from homeassistant.core import callback

from custom_components.askoheat.sensor_entities_ema import (
    EMA_SENSOR_ENTITY_DESCRIPTIONS,
)

from .entity import AskoheatEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from custom_components.askoheat.model import AskoheatSensorEntityDescription

    from .coordinator import AskoheatDataUpdateCoordinator
    from .data import AskoheatConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: AskoheatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        AskoheatSensor(
            coordinator=entry.runtime_data.ema_coordinator,
            entity_description=entity_description,
        )
        for entity_description in EMA_SENSOR_ENTITY_DESCRIPTIONS
    )


class AskoheatSensor(AskoheatEntity, SensorEntity):
    """askoheat Sensor class."""

    entity_description: AskoheatSensorEntityDescription

    def __init__(
        self,
        coordinator: AskoheatDataUpdateCoordinator,
        entity_description: AskoheatSensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
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

        self._attr_native_value = data[self.entity_description.data_key]

        if self._attr_native_value is None:
            pass

        elif isinstance(
            self._attr_native_value, float | int | np.floating | np.integer
        ) and (
            self.entity_description.factor is not None
            or self.entity_description.native_precision is not None
        ):
            float_value = float(self._attr_native_value)
            if self.entity_description.factor is not None:
                float_value *= self.entity_description.factor
            if self.entity_description.native_precision is not None:
                float_value = round(
                    float_value, self.entity_description.native_precision
                )
            self._attr_native_value = float_value

        self.async_write_ha_state()
        super()._handle_coordinator_update()
