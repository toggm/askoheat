"""Test data."""

import string
from math import trunc
from random import choice, randint, random
from typing import Any

import numpy as np
from pymodbus.client import ModbusTcpClient

from custom_components.askoheat.api_conf_desc import CONF_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_desc import (
    ByteRegisterInputDescriptor,
    FlagRegisterInputDescriptor,
    Float32RegisterInputDescriptor,
    SignedInt16RegisterInputDescriptor,
    StringRegisterInputDescriptor,
    UnsignedInt16RegisterInputDescriptor,
    UnsignedInt32RegisterInputDescriptor,
)
from custom_components.askoheat.api_ema_desc import EMA_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_op_desc import DATA_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_par_desc import PARAM_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.model import (
    AskoheatBinarySensorEntityDescription,
    AskoheatEntityDescription,
    AskoheatNumberEntityDescription,
    AskoheatSensorEntityDescription,
    AskoheatSwitchEntityDescription,
)

data_register_values = [
    0 for _ in range(DATA_REGISTER_BLOCK_DESCRIPTOR.number_of_registers)
]

par_register_values = [
    0 for _ in range(PARAM_REGISTER_BLOCK_DESCRIPTOR.number_of_registers)
]

ema_register_values = [
    0 for _ in range(EMA_REGISTER_BLOCK_DESCRIPTOR.number_of_registers)
]

config_register_values = [
    0 for _ in range(CONF_REGISTER_BLOCK_DESCRIPTOR.number_of_registers)
]


# Binary sensor data (flags in registers)
def random_boolean() -> bool:
    """."""
    return choice([True, False])  # noqa: S311


def randomword(length: int) -> str:
    """."""
    letters = string.ascii_lowercase
    return "".join(choice(letters) for i in range(length))  # noqa: S311


def random_byte(
    entity_descriptor: AskoheatNumberEntityDescription
    | AskoheatSensorEntityDescription,
) -> int:
    """."""
    min_value = int(
        entity_descriptor.native_min_value
        if entity_descriptor.native_min_value is not None
        else 0
    )
    max_value = int(
        entity_descriptor.native_max_value
        if entity_descriptor.native_max_value is not None
        else 255
    )
    return randint(min_value, max_value)  # noqa: S311


def random_int(
    entity_descriptor: AskoheatSensorEntityDescription
    | AskoheatNumberEntityDescription,
    iinfo: np.iinfo,
) -> int:
    """."""
    min_value = int(
        entity_descriptor.native_min_value
        if entity_descriptor.native_min_value is not None
        else iinfo.min
    )
    max_value = int(
        entity_descriptor.native_max_value
        if entity_descriptor.native_max_value is not None
        else iinfo.max
    )
    return randint(min_value, max_value)  # noqa: S311


# Max and min float32 values convertible to a binary representation
# https://en.wikipedia.org/wiki/Single-precision_floating-point_format#Precision_limitations_on_decimal_values_(between_1_and_16777216)
max_float32_value = 2 ^ 20
min_float32_value = -max_float32_value


def round_partial(value: float, resolution: float) -> float:
    """."""
    return round(value / resolution) * resolution


def random_float(
    entity_descriptor: AskoheatNumberEntityDescription
    | AskoheatSensorEntityDescription,
) -> float:
    """."""
    min_value = float(
        entity_descriptor.native_min_value
        if entity_descriptor.native_min_value is not None
        else min_float32_value
    )
    max_value = (
        float(
            entity_descriptor.native_max_value
            if entity_descriptor.native_max_value is not None
            else max_float32_value
        )
        - 1
    )
    value_range = max_value - min_value
    decimal_part = random()  # noqa: S311
    value = (random() * value_range) + min_value + decimal_part  # noqa: S311

    # round a fixed interval of 2^-3 as digits with a max of 2^20
    # are limited to this interval only
    return round_partial(value, 2 ^ -3)


def generate_sensor_test_data(
    entity_descriptor: AskoheatSensorEntityDescription,
) -> Any:
    """."""
    match entity_descriptor.api_descriptor:
        case Float32RegisterInputDescriptor():
            return random_float(entity_descriptor)
        case ByteRegisterInputDescriptor():
            return random_byte(entity_descriptor)
        case UnsignedInt16RegisterInputDescriptor():
            return random_int(entity_descriptor, np.iinfo(np.uint16))
        case UnsignedInt32RegisterInputDescriptor():
            return random_int(entity_descriptor, np.iinfo(np.uint32))
        case SignedInt16RegisterInputDescriptor():
            return random_int(entity_descriptor, np.iinfo(np.int16))
        case StringRegisterInputDescriptor(_, number_of_words):
            return randomword(trunc(number_of_words / 2))


def generate_number_test_data(
    entity_descriptor: AskoheatNumberEntityDescription,
) -> Any:
    """."""
    match entity_descriptor.api_descriptor:
        case ByteRegisterInputDescriptor():
            return random_byte(entity_descriptor)
        case Float32RegisterInputDescriptor():
            return random_float(entity_descriptor)
        case UnsignedInt16RegisterInputDescriptor():
            return random_int(entity_descriptor, np.iinfo(np.uint16))
        case UnsignedInt32RegisterInputDescriptor():
            return random_int(entity_descriptor, np.iinfo(np.uint32))
        case SignedInt16RegisterInputDescriptor():
            return random_int(entity_descriptor, np.iinfo(np.int16))


def generate_switch_test_data(
    entity_descriptor: AskoheatSwitchEntityDescription,
) -> Any:
    """."""
    match entity_descriptor.api_descriptor:
        case FlagRegisterInputDescriptor():
            return random_boolean()
        case ByteRegisterInputDescriptor():
            return 1 if random_boolean() else 0


def generate_binary_sensor_test_data(
    entity_descriptor: AskoheatBinarySensorEntityDescription,
) -> Any:
    """."""
    match entity_descriptor.api_descriptor:
        case FlagRegisterInputDescriptor():
            return random_boolean()


def convert_to_modbus_register(  # noqa: PLR0911
    entity_descriptor: AskoheatEntityDescription,
    current_register_value: int,
    value: Any,
) -> list[int]:
    """."""
    match entity_descriptor.api_descriptor:
        case Float32RegisterInputDescriptor():
            return ModbusTcpClient.convert_to_registers(
                float(value), ModbusTcpClient.DATATYPE.FLOAT32
            )
        case ByteRegisterInputDescriptor():
            return ModbusTcpClient.convert_to_registers(
                int(value), ModbusTcpClient.DATATYPE.INT16
            )
        case UnsignedInt16RegisterInputDescriptor():
            return ModbusTcpClient.convert_to_registers(
                int(value), ModbusTcpClient.DATATYPE.UINT16
            )
        case UnsignedInt32RegisterInputDescriptor():
            return ModbusTcpClient.convert_to_registers(
                int(value), ModbusTcpClient.DATATYPE.UINT32
            )
        case SignedInt16RegisterInputDescriptor():
            return ModbusTcpClient.convert_to_registers(
                int(value), ModbusTcpClient.DATATYPE.INT16
            )
        case FlagRegisterInputDescriptor(_, bit):
            # or with current register value
            if value:
                # or mask to set the value to true
                return [(value << bit) | current_register_value]

            # subtract flag from current registers value
            return [current_register_value & (0xFFFF ^ (True << bit))]
        case StringRegisterInputDescriptor():
            byte_list = value.encode()
            size = float.__ceil__(len(byte_list) / 2)
            result = []
            for index in range(size):
                b = byte_list[index * 2 : index * 2 + 2]
                result.append(int.from_bytes(b, "little"))
            return result
        case _:
            return []


def prepare_register_values(
    entity_descriptor: AskoheatEntityDescription, register: list[int], value: Any
) -> None:
    """."""
    if entity_descriptor.api_descriptor:
        register_values = convert_to_modbus_register(
            entity_descriptor,
            register[entity_descriptor.api_descriptor.starting_register],
            value,
        )
        for index, register_value in enumerate(register_values):
            register[entity_descriptor.api_descriptor.starting_register + index] = (
                register_value
            )
