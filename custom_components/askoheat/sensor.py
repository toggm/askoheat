"""Sensor platform for askoheat."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from homeassistant.components.sensor import ENTITY_ID_FORMAT, SensorEntity
from homeassistant.core import callback

from custom_components.askoheat.api_conf_desc import CONF_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_ema_desc import EMA_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_par_desc import PARAMETER_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.model import AskoheatSensorEntityDescription

from .entity import AskoheatEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

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
            entry=entry,
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description, coordinator in {
            **{
                entity_description: entry.runtime_data.par_coordinator
                for entity_description in PARAMETER_REGISTER_BLOCK_DESCRIPTOR.sensors
            },
            **{
                entity_description: entry.runtime_data.ema_coordinator
                for entity_description in EMA_REGISTER_BLOCK_DESCRIPTOR.sensors
            },
            **{
                entity_description: entry.runtime_data.config_coordinator
                for entity_description in CONF_REGISTER_BLOCK_DESCRIPTOR.sensors
            },
        }.items()
    )


class AskoheatSensor(AskoheatEntity[AskoheatSensorEntityDescription], SensorEntity):
    """askoheat Sensor class."""

    entity_description: AskoheatSensorEntityDescription

    def __init__(
        self,
        entry: AskoheatConfigEntry,
        coordinator: AskoheatDataUpdateCoordinator,
        entity_description: AskoheatSensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(entry, coordinator, entity_description)
        self.entity_id = ENTITY_ID_FORMAT.format(
            f"{self._device_unique_id}_{entity_description.key}"
        )
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

        super()._handle_coordinator_update()
