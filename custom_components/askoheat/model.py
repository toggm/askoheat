"""The Askoheat models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from functools import cached_property
from typing import TYPE_CHECKING, Any

from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.number import NumberEntityDescription, NumberMode
from homeassistant.components.select import SelectEntityDescription
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.components.switch import SwitchEntityDescription
from homeassistant.components.text import TextEntityDescription
from homeassistant.components.time import TimeEntityDescription
from homeassistant.const import Platform
from homeassistant.helpers.entity import EntityDescription

from custom_components.askoheat.api_desc import (
    ByteRegisterInputDescriptor,
    FlagRegisterInputDescriptor,
    Float32RegisterInputDescriptor,
    IntEnumInputDescriptor,
    RegisterInputDescriptor,
    SignedInt16RegisterInputDescriptor,
    StrEnumInputDescriptor,
    StringRegisterInputDescriptor,
    StructRegisterInputDescriptor,
    TimeRegisterInputDescriptor,
    UnsignedInt16RegisterInputDescriptor,
    UnsignedInt32RegisterInputDescriptor,
)
from custom_components.askoheat.const import (
    DOMAIN,
    BinarySensorAttrKey,
    DeviceKey,
    NumberAttrKey,
    SelectAttrKey,
    SensorAttrKey,
    SwitchAttrKey,
    TextAttrKey,
    TimeAttrKey,
)

if TYPE_CHECKING:
    from datetime import date, datetime
    from decimal import Decimal


@dataclass(frozen=True)
class AskoheatEntityDescription[K: StrEnum, A: RegisterInputDescriptor](
    EntityDescription
):
    """Class describing base askoheat entity."""

    key: K
    api_descriptor: A | None = None
    icon_by_state: dict[date | datetime | Decimal, str] | None = None
    device_key: DeviceKey | None = None


@dataclass(frozen=True)
class AskoheatBinarySensorEntityDescription(
    AskoheatEntityDescription[BinarySensorAttrKey, FlagRegisterInputDescriptor],
    BinarySensorEntityDescription,
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
    AskoheatEntityDescription[
        SwitchAttrKey, FlagRegisterInputDescriptor | ByteRegisterInputDescriptor
    ],
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
class AskoheatEmergencySwitchEntityDescription(AskoheatSwitchEntityDescription):
    """Class describing emergency switch entity."""

    # Override the data_key as we read status from
    # the binary sensors state
    @cached_property
    def data_key(self) -> str:
        """Get data key."""
        return f"binary_sensor.{BinarySensorAttrKey.EMERGENCY_MODE_ACTIVE}"


@dataclass(frozen=True)
class AskoheatSensorEntityDescription(
    AskoheatEntityDescription[
        SensorAttrKey,
        ByteRegisterInputDescriptor
        | UnsignedInt16RegisterInputDescriptor
        | UnsignedInt32RegisterInputDescriptor
        | SignedInt16RegisterInputDescriptor
        | Float32RegisterInputDescriptor
        | StringRegisterInputDescriptor
        | StructRegisterInputDescriptor,
    ],
    SensorEntityDescription,
):
    """Class describing Askoheat sensor entities."""

    key: SensorAttrKey
    platform = Platform.SENSOR
    factor: float | None = None
    native_precision: int | None = None
    domain = DOMAIN

    native_max_value: float | None = None
    native_min_value: float | None = None

    @cached_property
    def data_key(self) -> str:
        """Get data key."""
        return f"sensor.{self.key}"


@dataclass(frozen=True)
class AskoheatDurationSensorEntityDescription(AskoheatSensorEntityDescription):
    """Class describing an askoheat specific duration sensor entity."""


@dataclass(frozen=True)
class AskoheatNumberEntityDescription(
    AskoheatEntityDescription[
        NumberAttrKey,
        ByteRegisterInputDescriptor
        | UnsignedInt16RegisterInputDescriptor
        | SignedInt16RegisterInputDescriptor
        | Float32RegisterInputDescriptor,
    ],
    NumberEntityDescription,
):
    """Class describing Askoheat number entities."""

    key: NumberAttrKey
    platform = Platform.NUMBER
    factor: float | None = None
    native_precision: int | None = None
    domain = DOMAIN
    mode: NumberMode = NumberMode.AUTO
    native_default_value: float | None = None

    @cached_property
    def data_key(self) -> str:
        """Get data key."""
        return f"number.{self.key}"


@dataclass(frozen=True)
class AskoheatTimeEntityDescription(
    AskoheatEntityDescription[
        TimeAttrKey,
        TimeRegisterInputDescriptor,
    ],
    TimeEntityDescription,
):
    """Class describing Askoheat time entities."""

    key: TimeAttrKey
    platform = Platform.TIME
    domain = DOMAIN

    @cached_property
    def data_key(self) -> str:
        """Get data key."""
        return f"time.{self.key}"


@dataclass(frozen=True)
class AskoheatTextEntityDescription(
    AskoheatEntityDescription[
        TextAttrKey,
        StringRegisterInputDescriptor,
    ],
    TextEntityDescription,
):
    """Class describing Askoheat text entities."""

    key: TextAttrKey
    platform = Platform.TEXT
    domain = DOMAIN

    @cached_property
    def data_key(self) -> str:
        """Get data key."""
        return f"text.{self.key}"


@dataclass(frozen=True)
class AskoheatSelectEntityDescription(
    AskoheatEntityDescription[
        SelectAttrKey,
        IntEnumInputDescriptor[Any] | StrEnumInputDescriptor[Any],
    ],
    SelectEntityDescription,
):
    """Class describing Askoheat select entities."""

    key: SelectAttrKey
    platform = Platform.SELECT
    domain = DOMAIN

    @cached_property
    def data_key(self) -> str:
        """Get data key."""
        return f"select.{self.key}"
