"""Custom types for askoheat."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from custom_components.askoheat.const import (
    BinarySensorEMAAttrKey,
    SensorEMAAttrKey,
    SwitchEMAAttrKey,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from custom_components.askoheat.coordinator import AskoheatEMADataUpdateCoordinator

    from .api import AskoHeatModbusApiClient


type AskoheatConfigEntry = ConfigEntry[AskoheatData]


@dataclass
class AskoheatData:
    """Data for the Askoheat integration."""

    client: AskoHeatModbusApiClient
    ema_coordinator: AskoheatEMADataUpdateCoordinator
    integration: Integration


@dataclass
class AskoheatEMAData:
    """Data returnes when querying EMA attributes of askoheat."""

    binary_sensors: dict[BinarySensorEMAAttrKey, bool]
    sensors: dict[SensorEMAAttrKey, object]
    switches: dict[SwitchEMAAttrKey, bool]
