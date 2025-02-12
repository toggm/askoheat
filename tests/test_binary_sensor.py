"""Tests for the binary sensor entities."""

from typing import Any

import pytest
from homeassistant.core import HomeAssistant
from pymodbus.pdu.register_message import (
    ReadInputRegistersResponse,
)
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.askoheat.api_ema_desc import EMA_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_op_desc import DATA_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_par_desc import PARAM_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.const import BinarySensorAttrKey
from custom_components.askoheat.model import AskoheatBinarySensorEntityDescription

from .testdata import (
    data_register_values,
    ema_register_values,
    fill_test_data,
    par_register_values,
)

binary_data_register_values = data_register_values.copy()
binary_data_par_register_values = par_register_values.copy()
binary_data_ema_register_values = ema_register_values.copy()
binary_sensor_test_data: dict[BinarySensorAttrKey, Any] = {}

fill_test_data(
    DATA_REGISTER_BLOCK_DESCRIPTOR.binary_sensors,
    binary_data_register_values,
    binary_sensor_test_data,
)
fill_test_data(
    EMA_REGISTER_BLOCK_DESCRIPTOR.binary_sensors,
    binary_data_ema_register_values,
    binary_sensor_test_data,
)
fill_test_data(
    PARAM_REGISTER_BLOCK_DESCRIPTOR.binary_sensors,
    binary_data_par_register_values,
    binary_sensor_test_data,
)


@pytest.mark.parametrize(
    (
        "read_data_input_registers_response",
        "read_par_input_registers_response",
        "read_ema_input_registers_response",
        "entity_descriptor",
    ),
    [
        (
            ReadInputRegistersResponse(registers=binary_data_register_values),
            ReadInputRegistersResponse(registers=binary_data_par_register_values),
            ReadInputRegistersResponse(registers=binary_data_ema_register_values),
            entity_descriptor,
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
) -> None:
    """Test reading binary sensor."""
    key = f"binary_sensor.test_{entity_descriptor.key}"
    state = hass.states.get(key)
    assert state

    register_value = binary_sensor_test_data[entity_descriptor.key]
    expected = (
        "on"
        if (
            register_value == entity_descriptor.on_state
            and not entity_descriptor.inverted
        )
        or (
            register_value == entity_descriptor.off_state and entity_descriptor.inverted
        )
        else "off"
    )

    assert state.state is expected, (
        f"Expect state {expected} for entity {entity_descriptor.key}, but received {state.state}."  # noqa: E501
    )
