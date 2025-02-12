"""Tests for the switch sensor entities."""

from typing import Any

import pytest
from homeassistant.core import HomeAssistant
from pymodbus.pdu.register_message import (
    ReadHoldingRegistersResponse,
)
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.askoheat.api_conf_desc import CONF_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.const import DOMAIN, TextAttrKey
from custom_components.askoheat.model import (
    AskoheatTextEntityDescription,
)

from .testdata import (
    config_register_values,
    fill_test_data,
    generate_test_data,
)

# Text sensor data (flags in registers or bytes)
text_conf_register_values = config_register_values.copy()
text_test_data: dict[TextAttrKey, Any] = {}

fill_test_data(
    CONF_REGISTER_BLOCK_DESCRIPTOR.text_inputs,
    text_conf_register_values,
    text_test_data,
)

text_entities = [
    entity_descriptor
    for entity_descriptor in (CONF_REGISTER_BLOCK_DESCRIPTOR.text_inputs)
    if entity_descriptor.api_descriptor
    and entity_descriptor.entity_registry_enabled_default
]


@pytest.mark.parametrize(
    (
        "read_config_holding_registers_response",
        "entity_descriptor",
    ),
    [
        (
            ReadHoldingRegistersResponse(registers=text_conf_register_values),
            entity_descriptor,
        )
        for entity_descriptor in text_entities
    ],
)
async def test_read_text_sensor_states(
    mock_config_entry: MockConfigEntry,  # noqa: ARG001
    hass: HomeAssistant,
    entity_descriptor: AskoheatTextEntityDescription,
) -> None:
    """Test reading text entity."""
    key = f"text.test_{entity_descriptor.key}"
    state = hass.states.get(key)

    assert state
    expected = text_test_data[entity_descriptor.key]
    assert state.state == expected, (
        f"Expect state {expected} for entity {entity_descriptor.key}, but received {state.state}."  # noqa: E501
    )


@pytest.mark.parametrize("entity_descriptor", text_entities)
async def test_update_text_sensor_states(
    mock_config_entry: MockConfigEntry,  # noqa: ARG001
    hass: HomeAssistant,
    entity_descriptor: AskoheatTextEntityDescription,
) -> None:
    """Test updating text entity."""
    assert DOMAIN in hass.config.components
    entity_id = f"text.test_{entity_descriptor.key}"

    state = hass.states.get(entity_id)
    assert state
    assert state.state == ""

    new_value = generate_test_data(entity_descriptor)

    await hass.services.async_call(
        "text",
        "set_value",
        target={"entity_id": entity_id},
        service_data={"value": new_value},
    )
    await hass.async_block_till_done()
    state = hass.states.get(entity_id)
    assert state
    assert state.state == new_value, (
        f"Expect state {new_value} for entity {entity_descriptor.key}, but received {state.state}."  # noqa: E501
    )
