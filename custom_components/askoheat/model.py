"""The Askoheat models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from functools import cached_property
from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.components.switch import SwitchEntityDescription
from homeassistant.const import Platform
from homeassistant.helpers.entity import EntityDescription

from custom_components.askoheat.const import DOMAIN

if TYPE_CHECKING:
    from custom_components.askoheat.const import (
        BinarySensorAttrKey,
        SensorAttrKey,
        SwitchAttrKey,
    )


@dataclass(frozen=True)
class AdkoheatEntityDescription(EntityDescription):
    """Class describing base askoheat entity."""

    icon_by_state: dict[date | datetime | Decimal, str] | None = None


@dataclass(frozen=True)
class AskoheatBinarySensorEntityDescription(
    AdkoheatEntityDescription, BinarySensorEntityDescription
):
    """Class describing Askoheat binary sensor entities."""

    key: BinarySensorAttrKey
    platform = Platform.BINARY_SENSOR
    on_state: str | bool = True
    on_states: list[str] | None = None
    off_state: str | bool = False
    inverted: bool = False
    domain = DOMAIN

    @cached_property
    def data_key(self) -> str:
        """Get data key."""
        return f"binary_sensor.{self.key}"


@dataclass(frozen=True)
class AskoheatSwitchEntityDescription(
    AdkoheatEntityDescription,
    SwitchEntityDescription,
):
    """Class describing Askoheat switch entities."""

    key: SwitchAttrKey
    platform = Platform.SWITCH
    on_state: str | bool = True
    on_states: list[str] | None = None
    off_state: str | bool = False
    inverted = False
    domain = DOMAIN

    @cached_property
    def data_key(self) -> str:
        """Get data key."""
        return f"switch.{self.key}"


@dataclass(frozen=True)
class AskoheatSensorEntityDescription(
    AdkoheatEntityDescription,
    SensorEntityDescription,
):
    """Class describing Askoheat sensor entities."""

    key: SensorAttrKey
    platform = Platform.SENSOR
    factor: float | None = None
    native_precision: int | None = None
    domain = DOMAIN

    @cached_property
    def data_key(self) -> str:
        """Get data key."""
        return f"sensor.{self.key}"
