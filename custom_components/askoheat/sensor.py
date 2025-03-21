"""Sensor platform for askoheat."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, Any, cast

import numpy as np
from homeassistant.components.sensor import ENTITY_ID_FORMAT, SensorEntity
from homeassistant.const import UnitOfTime
from homeassistant.core import callback

from custom_components.askoheat.api_conf_desc import CONF_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_ema_desc import EMA_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_op_desc import DATA_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_par_desc import PARAM_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.const import AttributeKeys
from custom_components.askoheat.model import (
    AskoheatDurationSensorEntityDescription,
    AskoheatSensorEntityDescription,
)

from .entity import AskoheatEntity

if TYPE_CHECKING:
    from decimal import Decimal

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import StateType

    from .coordinator import AskoheatDataUpdateCoordinator
    from .data import AskoheatConfigEntry


def _instanciate(
    entry: AskoheatConfigEntry,
    coordinator: AskoheatDataUpdateCoordinator,
    entity_description: AskoheatSensorEntityDescription,
) -> AskoheatSensor:
    match entity_description:
        case AskoheatDurationSensorEntityDescription():
            return AskoheatDurationSensor(
                entry=entry,
                coordinator=coordinator,
                entity_description=entity_description,
            )
        case _:
            return AskoheatSensor(
                entry=entry,
                coordinator=coordinator,
                entity_description=entity_description,
            )


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: AskoheatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        _instanciate(
            entry=entry,
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description, coordinator in {
            **dict.fromkeys(
                PARAM_REGISTER_BLOCK_DESCRIPTOR.sensors,
                entry.runtime_data.par_coordinator,
            ),
            **dict.fromkeys(
                EMA_REGISTER_BLOCK_DESCRIPTOR.sensors,
                entry.runtime_data.ema_coordinator,
            ),
            **dict.fromkeys(
                CONF_REGISTER_BLOCK_DESCRIPTOR.sensors,
                entry.runtime_data.config_coordinator,
            ),
            **dict.fromkeys(
                DATA_REGISTER_BLOCK_DESCRIPTOR.sensors,
                entry.runtime_data.data_coordinator,
            ),
        }.items()
        if entity_description.device_key is None
        or entity_description.device_key in entry.runtime_data.supported_devices
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

        raw_value = data[self.entity_description.data_key]

        if raw_value is None:
            self._attr_native_value = None

        else:
            converted_value = self._convert_value(raw_value)

            if isinstance(converted_value, float | int | np.floating | np.integer) and (
                self.entity_description.factor is not None
                or self.entity_description.native_precision is not None
            ):
                float_value = float(converted_value)
                if self.entity_description.factor is not None:
                    float_value *= self.entity_description.factor
                if self.entity_description.native_precision is not None:
                    float_value = float_value.__round__(
                        self.entity_description.native_precision
                    )

                self._attr_native_value = float_value
            else:
                self._attr_native_value = converted_value

        super()._handle_coordinator_update()

    def _convert_value(self, value: Any) -> StateType | date | datetime | Decimal:
        return cast("StateType | date | datetime | Decimal", value)


class AskoheatDurationSensor(AskoheatSensor):
    """askoheat Sensor class representing a duration."""

    _unrecorded_attributes = frozenset({AttributeKeys.FORMATTED})

    def __init__(
        self,
        entry: AskoheatConfigEntry,
        coordinator: AskoheatDataUpdateCoordinator,
        entity_description: AskoheatSensorEntityDescription,
    ) -> None:
        """Initialize the duration sensor class."""
        super().__init__(entry, coordinator, entity_description)
        self._attr_extra_state_attributes[AttributeKeys.FORMATTED] = None

    def _convert_value(self, value: Any) -> StateType | date | datetime | Decimal:
        time_as_int = int(value)
        minutes = int(time_as_int / 2**0) & 0xFF
        hours = int(time_as_int / 2**8) & 0xFF
        days = int(time_as_int / 2**16) & 0xFFFF

        # write formatted value additionally to attributes
        self._attr_extra_state_attributes[AttributeKeys.FORMATTED] = timedelta(
            days=days, hours=hours, minutes=minutes
        ).__str__()

        match self.entity_description.native_unit_of_measurement:
            case UnitOfTime.DAYS:
                converted_value = (minutes / (60 * 24)) + (hours / 24) + days
            case UnitOfTime.HOURS:
                converted_value = (minutes / 60) + hours + (days * 24)
            case _:
                # by default convert to minutes
                converted_value = minutes + (hours * 60) + (days * 24 * 60)

        return converted_value
