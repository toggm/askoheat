"""Custom types for askoheat."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from custom_components.askoheat.const import SensorAttrKey

if TYPE_CHECKING:
    from datetime import time
    from enum import ReprEnum

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from custom_components.askoheat.const import (
        BinarySensorAttrKey,
        DeviceKey,
        NumberAttrKey,
        SelectAttrKey,
        SwitchAttrKey,
        TextAttrKey,
        TimeAttrKey,
    )
    from custom_components.askoheat.coordinator import (
        AskoheatConfigDataUpdateCoordinator,
        AskoheatEMADataUpdateCoordinator,
        AskoheatOperationDataUpdateCoordinator,
        AskoheatParameterDataUpdateCoordinator,
    )

    from .api import AskoheatModbusApiClient


type AskoheatConfigEntry = ConfigEntry[AskoheatData]


@dataclass
class AskoheatData:
    """Data for the Askoheat integration."""

    client: AskoheatModbusApiClient
    ema_coordinator: AskoheatEMADataUpdateCoordinator
    config_coordinator: AskoheatConfigDataUpdateCoordinator
    par_coordinator: AskoheatParameterDataUpdateCoordinator
    data_coordinator: AskoheatOperationDataUpdateCoordinator
    integration: Integration
    supported_devices: list[DeviceKey]

    @property
    def device_info(self) -> AskoheatDeviceInfos:
        """Resolve and return askoheat device infos."""
        return AskoheatDeviceInfos(self.par_coordinator.data)


@dataclass
class AskoheatDataBlock:
    """Data returns when querying EMA attributes of askoheat."""

    binary_sensors: dict[BinarySensorAttrKey, bool] | None = None
    sensors: dict[SensorAttrKey, object] | None = None
    switches: dict[SwitchAttrKey, bool] | None = None
    text_inputs: dict[TextAttrKey, str] | None = None
    select_inputs: dict[SelectAttrKey, ReprEnum | None] | None = None
    number_inputs: dict[NumberAttrKey, int | float] | None = None
    time_inputs: dict[TimeAttrKey, time] | None = None


@dataclass
class AskoheatDeviceInfos:
    """Data class describing the askoheat device."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Initialize device infos."""
        self._data = data

    @property
    def serial_number(self) -> str:
        """Return serial number of the device."""
        return str(self._data[f"sensor.{SensorAttrKey.PAR_ID}"])

    @property
    def article_name(self) -> str:
        """Return article name of the device."""
        return str(self._data[f"sensor.{SensorAttrKey.PAR_ARTICLE_NAME}"])

    @property
    def article_number(self) -> str:
        """Return article number of the device."""
        return str(self._data[f"sensor.{SensorAttrKey.PAR_ARTICLE_NUMBER}"])

    @property
    def software_version(self) -> str:
        """Return software version of the device."""
        return str(self._data[f"sensor.{SensorAttrKey.PAR_SOFTWARE_VERSION}"])

    @property
    def hardwareware_version(self) -> str:
        """Return hardware version of the device."""
        return str(self._data[f"sensor.{SensorAttrKey.PAR_HARDWARE_VERSION}"])
