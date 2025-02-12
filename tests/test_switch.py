"""Tests for the switch sensor entities."""

from typing import Any

import pytest
from homeassistant.const import (
    STATE_OFF,
    STATE_ON,
)
from homeassistant.core import HomeAssistant
from pymodbus.pdu.register_message import (
    ReadHoldingRegistersResponse,
)
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.askoheat.api_conf_desc import CONF_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_desc import (
    ByteRegisterInputDescriptor,
    FlagRegisterInputDescriptor,
)
from custom_components.askoheat.const import DOMAIN, SwitchAttrKey
from custom_components.askoheat.model import (
    AskoheatSwitchEntityDescription,
)

from .testdata import (
    config_register_values,
    fill_test_data,
)

# Switch sensor data (flags in registers or bytes)
switch_conf_register_values = config_register_values.copy()
switch_test_data: dict[SwitchAttrKey, Any] = {}

fill_test_data(
    CONF_REGISTER_BLOCK_DESCRIPTOR.switches,
    switch_conf_register_values,
    switch_test_data,
)


def __expected_value(
    entity_descriptor: AskoheatSwitchEntityDescription,
) -> str | None:
    register_value = switch_test_data[entity_descriptor.key]
    return_value = None
    match entity_descriptor.api_descriptor:
        case FlagRegisterInputDescriptor():
            return_value = (
                "on"
                if (
                    register_value == entity_descriptor.on_state
                    and not entity_descriptor.inverted
                )
                or (
                    register_value == entity_descriptor.off_state
                    and entity_descriptor.inverted
                )
                else "off"
            )
        case ByteRegisterInputDescriptor():
            return_value = (
                "on"
                if (int(register_value) == 1 and not entity_descriptor.inverted)
                or (int(register_value) == 0 and entity_descriptor.inverted)
                else "off"
            )
    return return_value


switch_entities = [
    entity_descriptor
    for entity_descriptor in (CONF_REGISTER_BLOCK_DESCRIPTOR.switches)
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
            ReadHoldingRegistersResponse(registers=switch_conf_register_values),
            entity_descriptor,
        )
        for entity_descriptor in switch_entities
    ],
)
async def test_read_switch_sensor_states(
    mock_config_entry: MockConfigEntry,  # noqa: ARG001
    hass: HomeAssistant,
    entity_descriptor: AskoheatSwitchEntityDescription,
) -> None:
    """Test reading switch sensor."""
    key = f"switch.test_{entity_descriptor.key}"
    state = hass.states.get(key)

    expected = __expected_value(entity_descriptor)
    assert state
    assert state.state is expected, (
        f"Expect state {expected} for entity {entity_descriptor.key}, but received {state.state}."  # noqa: E501
    )


@pytest.mark.parametrize("entity_descriptor", switch_entities)
async def test_update_switch_sensor_states(
    mock_config_entry: MockConfigEntry,  # noqa: ARG001
    hass: HomeAssistant,
    entity_descriptor: AskoheatSwitchEntityDescription,
) -> None:
    """Test updating switch sensor."""
    assert DOMAIN in hass.config.components
    entity_id = f"switch.test_{entity_descriptor.key}"

    state = hass.states.get(entity_id)
    assert state
    assert state.state == STATE_OFF
    await hass.services.async_call(
        "switch", "turn_on", service_data={"entity_id": entity_id}
    )
    await hass.async_block_till_done()
    state = hass.states.get(entity_id)
    assert state
    assert state.state == STATE_ON
    await hass.services.async_call(
        "switch", "turn_off", service_data={"entity_id": entity_id}
    )
    await hass.async_block_till_done()
    state = hass.states.get(entity_id)
    assert state
    assert state.state == STATE_OFF
