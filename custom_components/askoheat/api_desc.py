"""Api descriptor classes."""

from __future__ import annotations

import typing
from abc import ABC
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from custom_components.askoheat.model import (
        AskoheatBinarySensorEntityDescription,
        AskoheatNumberEntityDescription,
        AskoheatSensorEntityDescription,
        AskoheatSwitchEntityDescription,
    )


class SwitchAttrKey(StrEnum):
    """Askoheat binary switch attribute keys."""


@dataclass(frozen=True)
class RegisterInputDescriptor(ABC):  # noqa: B024
    """Description of a register based input."""

    starting_register: typing.Final[int] = field()


@dataclass(frozen=True)
class FlagRegisterInputDescriptor(RegisterInputDescriptor):
    """Input register representing a a flag as a bit mask of an int value."""

    bit: int


@dataclass(frozen=True)
class ByteRegisterInputDescriptor(RegisterInputDescriptor):
    """Input register representing a byte."""


@dataclass(frozen=True)
class Float32RegisterInputDescriptor(RegisterInputDescriptor):
    """Input register representing a float32."""


@dataclass(frozen=True)
class SignedIntRegisterInputDescriptor(RegisterInputDescriptor):
    """Input register representing a signed int."""


@dataclass(frozen=True)
class UnsignedIntRegisterInputDescriptor(RegisterInputDescriptor):
    """Input register representing an unsigned int."""


@dataclass(frozen=True)
class StringRegisterInputDescriptor(RegisterInputDescriptor):
    """Input register representing a string."""

    number_of_bytes: int


@dataclass(frozen=True)
class RegisterBlockDescriptor:
    """Based askoheat modbus block (range of registers) descriptor."""

    starting_register: int
    number_of_registers: int

    binary_sensors: list[AskoheatBinarySensorEntityDescription] = field(
        default_factory=list
    )
    sensors: list[AskoheatSensorEntityDescription] = field(default_factory=list)
    switches: list[AskoheatSwitchEntityDescription] = field(default_factory=list)
    number_inputs: list[AskoheatNumberEntityDescription] = field(default_factory=list)

    def absolute_register_index(self, desc: RegisterInputDescriptor) -> int:
        """Return absolute index of register."""
        return self.starting_register + desc.starting_register

    # TODO: add more type of inputs as soon as supported
    # text_inputs: list[TextAttrKey, RegisterInputDescriptor] = field(
    #    default_factory=dict
    # )
    # select_inputs: dict[SelectAttrKey, RegisterInputDescriptor] = field(
    #    default_factory=dict
    # )
    # time_inputs: dict[TimeAttrKey, RegisterInputDescriptor] = field(
    #    default_factory=dict
    # )
