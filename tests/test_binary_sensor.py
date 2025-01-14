"""Tests for the binary sensor entities."""

from functools import reduce
from random import choice

import pytest
from homeassistant.core import HomeAssistant
from pymodbus.pdu.register_message import (
    ReadInputRegistersResponse,
)
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.askoheat.api_ema_desc import EMA_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_op_desc import DATA_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_par_desc import PARAM_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.const import (
    DATA_LEGIO_STATUS_REGISTER,
    EMA_STATUS_REGISTER,
    PAR_TYPE_REGISTER,
)
from custom_components.askoheat.model import AskoheatBinarySensorEntityDescription

from .testdata import data_register_values, ema_register_values, par_register_values

# Binary sensor data (flags in registers)
binary_register_test_values = [choice([True, False]) for _ in range(16)]  # noqa: S311
binary_register_test_values_as_int = reduce(
    lambda x, y: x | y,
    # shift bitwise
    [
        0 | (binary_register_test_values[index] << index)
        for index in range(len(binary_register_test_values))
    ],
)
binary_data_register_values = data_register_values.copy()
binary_data_register_values[DATA_LEGIO_STATUS_REGISTER] = (
    binary_register_test_values_as_int
)
binary_data_par_register_values = par_register_values.copy()
binary_data_par_register_values[PAR_TYPE_REGISTER] = binary_register_test_values_as_int

binary_data_ema_register_values = ema_register_values.copy()
binary_data_ema_register_values[EMA_STATUS_REGISTER] = (
    binary_register_test_values_as_int
)


@pytest.mark.parametrize(
    (
        "read_data_input_registers_response",
        "read_par_input_registers_response",
        "read_ema_input_registers_response",
        "entity_descriptor",
        "expected",
    ),
    [
        (
            ReadInputRegistersResponse(registers=binary_data_register_values),
            ReadInputRegistersResponse(registers=binary_data_par_register_values),
            ReadInputRegistersResponse(registers=binary_data_ema_register_values),
            entity_descriptor,
            (
                "on"
                if (
                    binary_register_test_values[entity_descriptor.api_descriptor.bit]
                    and not entity_descriptor.inverted
                )
                or (
                    not binary_register_test_values[
                        entity_descriptor.api_descriptor.bit
                    ]
                    and entity_descriptor.inverted
                )
                else "off"
            ),
        )
        for entity_descriptor in (
            DATA_REGISTER_BLOCK_DESCRIPTOR.binary_sensors
            + PARAM_REGISTER_BLOCK_DESCRIPTOR.binary_sensors
            + EMA_REGISTER_BLOCK_DESCRIPTOR.binary_sensors
        )
        if entity_descriptor.api_descriptor
        and entity_descriptor.entity_registry_enabled_default
    ],
)
async def test_read_binary_sensor_states(
    mock_config_entry: MockConfigEntry,  # noqa: ARG001
    hass: HomeAssistant,
    entity_descriptor: AskoheatBinarySensorEntityDescription,
    expected: str,
) -> None:
    """Test reading binary sensor."""
    key = f"binary_sensor.test_{entity_descriptor.key}"
    state = hass.states.get(key)
    assert state
    assert state.state is expected, (
        f"Expect state {expected} for entity {entity_descriptor.key}, but received {state.state}."  # noqa: E501
    )
