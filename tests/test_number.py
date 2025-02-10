"""Tests for the switch sensor entities."""

from math import isclose

import pytest
from homeassistant.core import HomeAssistant
from pymodbus.pdu.register_message import (
    ReadHoldingRegistersResponse,
    ReadInputRegistersResponse,
)
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.askoheat.api_conf_desc import CONF_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_ema_desc import EMA_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.const import DOMAIN
from custom_components.askoheat.model import (
    AskoheatNumberEntityDescription,
)

from .testdata import (
    config_register_values,
    ema_register_values,
    generate_number_test_data,
    prepare_register_values,
)

# Number sensor data (flags in registers or bytes)
number_conf_register_values = config_register_values.copy()
number_ema_register_values = ema_register_values.copy()
number_test_data = {}


def __fill_switch_data(
    entities: list[AskoheatNumberEntityDescription], register: list[int]
) -> None:
    for entity_descriptor in entities:
        if entity_descriptor.api_descriptor:
            value = generate_number_test_data(entity_descriptor)
            number_test_data[entity_descriptor.key] = value
            prepare_register_values(entity_descriptor, register, value)


__fill_switch_data(
    CONF_REGISTER_BLOCK_DESCRIPTOR.number_inputs, number_conf_register_values
)
__fill_switch_data(
    EMA_REGISTER_BLOCK_DESCRIPTOR.number_inputs, number_ema_register_values
)

number_entities = [
    entity_descriptor
    for entity_descriptor in (
        CONF_REGISTER_BLOCK_DESCRIPTOR.number_inputs
        + EMA_REGISTER_BLOCK_DESCRIPTOR.number_inputs
    )
    if entity_descriptor.api_descriptor
    and entity_descriptor.entity_registry_enabled_default
]


@pytest.mark.parametrize(
    (
        "read_config_holding_registers_response",
        "read_ema_input_registers_response",
        "entity_descriptor",
    ),
    [
        (
            ReadHoldingRegistersResponse(registers=number_conf_register_values),
            ReadInputRegistersResponse(registers=number_ema_register_values),
            entity_descriptor,
        )
        for entity_descriptor in number_entities
    ],
)
async def test_read_number_input_states(
    mock_config_entry: MockConfigEntry,  # noqa: ARG001
    hass: HomeAssistant,
    entity_descriptor: AskoheatNumberEntityDescription,
) -> None:
    """Test reading number input."""
    assert DOMAIN in hass.config.components
    key = f"number.test_{entity_descriptor.key}"

    expected = (
        0
        if number_test_data[entity_descriptor.key] is None
        else number_test_data[entity_descriptor.key]
    )

    if entity_descriptor.factor is not None:
        expected *= entity_descriptor.factor

    # for entity descriptors provided a precision we expect a rounded value
    if entity_descriptor.native_precision is not None:
        expected = expected.__round__(entity_descriptor.native_precision)

    state = hass.states.get(key)
    assert state

    assert isclose(float(state.state), expected), (
        f"Expect state {expected}({type(expected)}) for entity {entity_descriptor.key} to be close to {state.state}({type(state.state)}."  # noqa: E501
    )


@pytest.mark.parametrize("entity_descriptor", number_entities)
async def test_update_number_sensor_states(
    mock_config_entry: MockConfigEntry,  # noqa: ARG001
    hass: HomeAssistant,
    entity_descriptor: AskoheatNumberEntityDescription,
) -> None:
    """Test updating number sensor."""
    assert DOMAIN in hass.config.components
    entity_id = f"number.test_{entity_descriptor.key}"

    state = hass.states.get(entity_id)
    assert state
    assert isclose(float(state.state), float(0))

    new_number = float(generate_number_test_data(entity_descriptor))

    await hass.services.async_call(
        "number",
        "set_value",
        target={"entity_id": entity_id},
        service_data={"value": new_number},
    )
    await hass.async_block_till_done()
    state = hass.states.get(entity_id)
    assert state

    expected = float(state.state)

    assert isclose(expected, new_number)
