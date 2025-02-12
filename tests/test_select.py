"""Tests for the switch sensor entities."""

from typing import TYPE_CHECKING, Any

import pytest
from homeassistant.core import HomeAssistant
from pymodbus.pdu.register_message import (
    ReadHoldingRegistersResponse,
)
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.askoheat.api_conf_desc import CONF_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.const import DOMAIN, SelectAttrKey
from custom_components.askoheat.model import (
    AskoheatSelectEntityDescription,
)

from .testdata import (
    config_register_values,
    fill_test_data,
    generate_test_data,
)

if TYPE_CHECKING:
    from enum import Enum

# Select entity data (flags in registers or bytes)
select_conf_register_values = config_register_values.copy()
select_test_data: dict[SelectAttrKey, Any] = {}

fill_test_data(
    CONF_REGISTER_BLOCK_DESCRIPTOR.select_inputs,
    select_conf_register_values,
    select_test_data,
)

select_entities = [
    entity_descriptor
    for entity_descriptor in (CONF_REGISTER_BLOCK_DESCRIPTOR.select_inputs)
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
            ReadHoldingRegistersResponse(registers=select_conf_register_values),
            entity_descriptor,
        )
        for entity_descriptor in select_entities
    ],
)
async def test_read_select_entity_states(
    mock_config_entry: MockConfigEntry,  # noqa: ARG001
    hass: HomeAssistant,
    entity_descriptor: AskoheatSelectEntityDescription,
) -> None:
    """Test reading select entity."""
    key = f"select.test_{entity_descriptor.key}"
    state = hass.states.get(key)

    assert state
    expected = select_test_data[entity_descriptor.key]
    assert state.state == expected, (
        f"Expect state {expected} for entity {entity_descriptor.key}, but received {state.state}."  # noqa: E501
    )


@pytest.mark.parametrize("entity_descriptor", select_entities)
async def test_update_select_entity_states(
    mock_config_entry: MockConfigEntry,  # noqa: ARG001
    hass: HomeAssistant,
    entity_descriptor: AskoheatSelectEntityDescription,
) -> None:
    """Test updating select entity."""
    assert DOMAIN in hass.config.components
    entity_id = f"select.test_{entity_descriptor.key}"

    state = hass.states.get(entity_id)
    assert state
    # initial state doesn't match one of the select entity options,
    # therefore we expect 'unknown'
    assert state.state == "unknown"

    new_value: Enum = generate_test_data(entity_descriptor)

    await hass.services.async_call(
        "select",
        "select_option",
        target={"entity_id": entity_id},
        service_data={"option": new_value.value},
        blocking=True,
    )

    await hass.async_block_till_done()
    state = hass.states.get(entity_id)
    assert state
    assert state.state == new_value.value, (
        f"Expect state {new_value.value} for entity {entity_id}, but received {state.state}."  # noqa: E501
    )
