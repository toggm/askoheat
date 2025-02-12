"""Tests for the switch sensor entities."""

from time import strftime, struct_time
from typing import Any

import pytest
from homeassistant.core import HomeAssistant
from pymodbus.pdu.register_message import (
    ReadHoldingRegistersResponse,
)
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.askoheat.api_conf_desc import CONF_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.const import DOMAIN, TimeAttrKey
from custom_components.askoheat.model import (
    AskoheatTimeEntityDescription,
)

from .testdata import (
    config_register_values,
    fill_test_data,
    generate_test_data,
)

# Time sensor data (flags in registers or bytes)
time_conf_register_values = config_register_values.copy()
time_test_data: dict[TimeAttrKey, Any] = {}

fill_test_data(
    CONF_REGISTER_BLOCK_DESCRIPTOR.time_inputs,
    time_conf_register_values,
    time_test_data,
)

time_entities = [
    entity_descriptor
    for entity_descriptor in (CONF_REGISTER_BLOCK_DESCRIPTOR.time_inputs)
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
            ReadHoldingRegistersResponse(registers=time_conf_register_values),
            entity_descriptor,
        )
        for entity_descriptor in time_entities
    ],
)
async def test_read_time_sensor_states(
    mock_config_entry: MockConfigEntry,  # noqa: ARG001
    hass: HomeAssistant,
    entity_descriptor: AskoheatTimeEntityDescription,
) -> None:
    """Test reading time entity."""
    key = f"time.test_{entity_descriptor.key}"
    state = hass.states.get(key)

    assert state
    time = time_test_data[entity_descriptor.key]
    # expect time will be updated without seconds part
    expected_time_value = strftime("%H:%M:00", time)
    assert state.state == expected_time_value, (
        f"Expect state {expected_time_value} for entity {entity_descriptor.key}, but received {state.state}."  # noqa: E501
    )


@pytest.mark.parametrize("entity_descriptor", time_entities)
async def test_update_time_sensor_states(
    mock_config_entry: MockConfigEntry,  # noqa: ARG001
    hass: HomeAssistant,
    entity_descriptor: AskoheatTimeEntityDescription,
) -> None:
    """Test updating time entity."""
    assert DOMAIN in hass.config.components
    entity_id = f"time.test_{entity_descriptor.key}"

    state = hass.states.get(entity_id)
    assert state
    assert state.state == "00:00:00"

    new_time: struct_time = generate_test_data(entity_descriptor)
    new_time_value = strftime("%H:%M:%S", new_time)
    # expect time will be updated without seconds part
    expected_time_value = strftime("%H:%M:00", new_time)

    await hass.services.async_call(
        "time",
        "set_value",
        target={"entity_id": entity_id},
        service_data={"time": new_time_value},
    )
    await hass.async_block_till_done()
    state = hass.states.get(entity_id)
    assert state
    assert state.state == expected_time_value, (
        f"Expect state {expected_time_value} for entity {entity_descriptor.key}, but received {state.state}."  # noqa: E501
    )
