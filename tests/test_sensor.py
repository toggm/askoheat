"""Tests for the binary sensor entities."""

import string
from math import trunc
from random import choice, randint, random
from typing import Any

import numpy as np
import pytest
from homeassistant.core import HomeAssistant
from pymodbus.client import ModbusTcpClient
from pymodbus.pdu.register_message import (
    ReadHoldingRegistersResponse,
    ReadInputRegistersResponse,
)
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.askoheat.api_conf_desc import CONF_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_desc import (
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
    AskoheatSensorEntityDescription,
)

from .testdata import (
    config_register_values,
    data_register_values,
    ema_register_values,
    par_register_values,
)


def __randomword(length: int) -> str:
    letters = string.ascii_lowercase
    return "".join(choice(letters) for i in range(length))  # noqa: S311


# prepare sensor data
sensor_entities = [
    entity_descriptor
    for entity_descriptor in (
        DATA_REGISTER_BLOCK_DESCRIPTOR.sensors
        + PARAM_REGISTER_BLOCK_DESCRIPTOR.sensors
        + EMA_REGISTER_BLOCK_DESCRIPTOR.sensors
        + DATA_REGISTER_BLOCK_DESCRIPTOR.sensors
    )
    if entity_descriptor.api_descriptor
    and entity_descriptor.entity_registry_enabled_default
]


def __random_int(
    entity_descriptor: AskoheatSensorEntityDescription, iinfo: np.iinfo
) -> int:
    min_value = int(entity_descriptor.native_min_value or iinfo.min)
    max_value = int(entity_descriptor.native_max_value or iinfo.max)
    return randint(min_value, max_value)  # noqa: S311


def __random_float(entity_descriptor: AskoheatSensorEntityDescription) -> float:
    # Be aware that the modbus FLOAT32 datatype is only represented by 2 bytes.
    # Therefore it doesn't support higher numbers than a float16,
    # even if the name is misleading
    min_value = float(entity_descriptor.native_min_value or np.finfo(np.float16).min)
    max_value = (
        float(entity_descriptor.native_max_value or np.finfo(np.float16).max) - 1
    )
    value_range = max_value - min_value

    return (random() * value_range) + min_value + random()  # noqa: S311


def __generate_test_data(entity_descriptor: AskoheatSensorEntityDescription) -> Any:
    match entity_descriptor.api_descriptor:
        case Float32RegisterInputDescriptor():
            return __random_float(entity_descriptor)
        case UnsignedInt16RegisterInputDescriptor():
            return __random_int(entity_descriptor, np.iinfo(np.uint16))
        case UnsignedInt32RegisterInputDescriptor():
            return __random_int(entity_descriptor, np.iinfo(np.uint32))
        case SignedInt16RegisterInputDescriptor():
            return __random_int(entity_descriptor, np.iinfo(np.int16))
        case StringRegisterInputDescriptor(_, number_of_words):
            return __randomword(trunc(number_of_words / 2))


def __convert_to_modbus_register(
    entity_descriptor: AskoheatSensorEntityDescription, value: Any
) -> list[int]:
    match entity_descriptor.api_descriptor:
        case Float32RegisterInputDescriptor():
            return ModbusTcpClient.convert_to_registers(
                float(value), ModbusTcpClient.DATATYPE.FLOAT32
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


sensor_data_register_values = data_register_values.copy()
sensor_par_register_values = par_register_values.copy()
sensor_ema_register_values = ema_register_values.copy()
sensor_conf_register_values = config_register_values.copy()

sensor_test_data = {}


def __fill_sensor_data(
    sensors: list[AskoheatSensorEntityDescription], register: list[int]
) -> None:
    for entity_descriptor in sensors:
        if entity_descriptor.api_descriptor:
            value = __generate_test_data(entity_descriptor)
            sensor_test_data[entity_descriptor.key] = value

            register_values = __convert_to_modbus_register(entity_descriptor, value)
            for index, register_value in enumerate(register_values):
                register[entity_descriptor.api_descriptor.starting_register + index] = (
                    register_value
                )


__fill_sensor_data(CONF_REGISTER_BLOCK_DESCRIPTOR.sensors, sensor_conf_register_values)
__fill_sensor_data(DATA_REGISTER_BLOCK_DESCRIPTOR.sensors, sensor_data_register_values)
__fill_sensor_data(PARAM_REGISTER_BLOCK_DESCRIPTOR.sensors, sensor_par_register_values)
__fill_sensor_data(EMA_REGISTER_BLOCK_DESCRIPTOR.sensors, sensor_ema_register_values)


@pytest.mark.parametrize(
    (
        "read_config_holding_registers_response",
        "read_data_input_registers_response",
        "read_par_input_registers_response",
        "read_ema_input_registers_response",
        "entity_descriptor",
    ),
    [
        (
            ReadHoldingRegistersResponse(registers=sensor_conf_register_values),
            ReadInputRegistersResponse(registers=sensor_data_register_values),
            ReadInputRegistersResponse(registers=sensor_par_register_values),
            ReadInputRegistersResponse(registers=sensor_ema_register_values),
            entity_descriptor,
        )
        for entity_descriptor in sensor_entities
    ],
)
async def test_read_sensor_states(
    mock_config_entry: MockConfigEntry,  # noqa: ARG001
    hass: HomeAssistant,
    entity_descriptor: AskoheatSensorEntityDescription,
) -> None:
    """Test reading sensor."""
    key = f"sensor.test_{entity_descriptor.key}"
    state = hass.states.get(key)
    assert state

    expected = (
        0
        if sensor_test_data[entity_descriptor.key] is None
        else sensor_test_data[entity_descriptor.key]
    )

    if entity_descriptor.factor is not None:
        expected *= entity_descriptor.factor

    # for entity descriptors provided a precision we expect a rounded value
    if entity_descriptor.native_precision is not None:
        expected = expected.__round__(entity_descriptor.native_precision)

    assert state.state == str(expected), (
        f"Expect state {expected}({type(expected)}) for entity {entity_descriptor.key}, but received {state.state}({type(state.state)})."  # noqa: E501
    )
