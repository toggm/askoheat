"""The Askoheat models."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.components.switch import SwitchEntityDescription
from homeassistant.const import Platform

from custom_components.askoheat.const import DOMAIN

if TYPE_CHECKING:
    from custom_components.askoheat.const import (
        BinarySensorEMAAttrKey,
        SensorEMAAttrKey,
        SwitchEMAAttrKey,
    )


@dataclass(frozen=True)
class AskoheatBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class describing Askoheat binary sensor entities."""

    key: BinarySensorEMAAttrKey
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
    SwitchEntityDescription,
):
    """Class describing Askoheat switch entities."""

    key: SwitchEMAAttrKey
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
    SensorEntityDescription,
):
    """Class describing Askoheat sensor entities."""

    key: SensorEMAAttrKey
    platform = Platform.SENSOR
    factor: float | None = None
    native_precision: int | None = None
    domain = DOMAIN

    @cached_property
    def data_key(self) -> str:
        """Get data key."""
        return f"sensor.{self.key}"
