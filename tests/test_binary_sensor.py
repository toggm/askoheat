"""Tests for the binary sensor entities."""

from functools import reduce
from random import choice

import pytest
from homeassistant.core import HomeAssistant
from pymodbus.pdu.register_read_message import (
    ReadInputRegistersResponse,
)
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.askoheat.api_op_desc import DATA_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_par_desc import PARAM_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.const import (
    DATA_LEGIO_STATUS_REGISTER,
    LOGGER,
    PAR_TYPE_REGISTER,
)

binary_register_test_values = [choice([True, False]) for _ in range(16)]  # noqa: S311
binary_register_test_values_as_int = reduce(
    lambda x, y: x | y,
    # shift bitwise
    [
        0 | (binary_register_test_values[index] << index)
        for index in range(len(binary_register_test_values))
    ],
)

data_register_values = [
    0 if index != DATA_LEGIO_STATUS_REGISTER else binary_register_test_values_as_int
    for index in range(DATA_REGISTER_BLOCK_DESCRIPTOR.number_of_registers)
]

par_register_values = [
    0 if index != PAR_TYPE_REGISTER else binary_register_test_values_as_int
    for index in range(PARAM_REGISTER_BLOCK_DESCRIPTOR.number_of_registers)
]


@pytest.mark.parametrize(
    "read_data_input_registers_response",
    [ReadInputRegistersResponse(values=data_register_values)],
)
@pytest.mark.parametrize(
    "read_par_input_registers_response",
    [ReadInputRegistersResponse(values=par_register_values)],
)
async def test_read_binary_sensor_states(
    mock_config_entry: MockConfigEntry,
    hass: HomeAssistant,
) -> None:
    """Test reading binary sensor."""
    LOGGER.info("Test %s", mock_config_entry.runtime_data.client)

    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    for entity_descriptor in (
        DATA_REGISTER_BLOCK_DESCRIPTOR.binary_sensors
        + PARAM_REGISTER_BLOCK_DESCRIPTOR.binary_sensors
    ):
        if (
            entity_descriptor.api_descriptor
            and entity_descriptor.entity_registry_enabled_default
        ):
            expected = (
                "on"
                if binary_register_test_values[entity_descriptor.api_descriptor.bit]
                else "off"
            )
            key = f"binary_sensor.test_{entity_descriptor.key}"
            state = hass.states.get(key)
            LOGGER.debug("Test:%s = %s", key, state)
            assert state
            assert state.state is expected
