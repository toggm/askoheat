"""Custom types for askoheat."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import time
    from enum import ReprEnum

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration
    from numpy import number

    from custom_components.askoheat.const import (
        BinarySensorAttrKey,
        NumberAttrKey,
        SelectAttrKey,
        SensorAttrKey,
        SwitchAttrKey,
        TextAttrKey,
        TimeAttrKey,
    )
    from custom_components.askoheat.coordinator import (
        AskoheatConfigDataUpdateCoordinator,
        AskoheatEMADataUpdateCoordinator,
        AskoheatParameterDataUpdateCoordinator,
    )

    from .api import AskoHeatModbusApiClient


type AskoheatConfigEntry = ConfigEntry[AskoheatData]


@dataclass
class AskoheatData:
    """Data for the Askoheat integration."""

    client: AskoHeatModbusApiClient
    ema_coordinator: AskoheatEMADataUpdateCoordinator
    config_coordinator: AskoheatConfigDataUpdateCoordinator
    par_coordinator: AskoheatParameterDataUpdateCoordinator
    integration: Integration


@dataclass
class AskoheatDataBlock:
    """Data returnes when querying EMA attributes of askoheat."""

    binary_sensors: dict[BinarySensorAttrKey, bool] | None = None
    sensors: dict[SensorAttrKey, object] | None = None
    switches: dict[SwitchAttrKey, bool] | None = None
    text_inputs: dict[TextAttrKey, str] | None = None
    select_inputs: dict[SelectAttrKey, ReprEnum] | None = None
    number_inputs: dict[NumberAttrKey, number] | None = None
    time_inputs: dict[TimeAttrKey, time] | None = None
