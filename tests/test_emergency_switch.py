"""Tests for the switch sensor entities."""

import pytest
import respx
from homeassistant.core import HomeAssistant
from pymodbus.pdu.register_message import (
    ReadInputRegistersResponse,
)
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.askoheat.const import EMA_STATUS_REGISTER
from tests.conftest import HOST

from .testdata import (
    ema_register_values,
)

switch_entity_id = "switch.test_emergency_mode"


@respx.mock
async def test_turn_emergency_switch_on(
    mock_config_entry: MockConfigEntry,  # noqa: ARG001
    hass: HomeAssistant,
) -> None:
    """Test that turn off will call the correct endpoint."""
    respx.get(f"http://{HOST}/on").respond(status_code=200, text="ON")

    state = hass.states.get(switch_entity_id)
    assert state
    assert state.state == "off"

    await hass.services.async_call(
        "switch",
        "turn_on",
        target={"entity_id": switch_entity_id},
    )
    await hass.async_block_till_done()

    state = hass.states.get(switch_entity_id)
    assert state
    assert state.state == "on"


@respx.mock
async def test_turn_emergency_switch_off(
    mock_config_entry: MockConfigEntry,  # noqa: ARG001
    hass: HomeAssistant,
) -> None:
    """Test that turn off will call the correct endpoint."""
    respx.get(f"http://{HOST}/on").respond(status_code=200, text="OFF")

    await hass.services.async_call(
        "switch",
        "turn_off",
        target={"entity_id": switch_entity_id},
    )
    await hass.async_block_till_done()

    state = hass.states.get(switch_entity_id)
    assert state
    assert state.state == "off"


@respx.mock
async def test_turn_emergency_switch_set_state_based_on_result(
    mock_config_entry: MockConfigEntry,  # noqa: ARG001
    hass: HomeAssistant,
) -> None:
    """Test that turn off will call the correct endpoint."""
    respx.get(f"http://{HOST}/on").respond(status_code=200, text="OFF")

    switch_entity_id = "switch.test_emergency_mode"
    state = hass.states.get(switch_entity_id)
    assert state
    assert state.state == "off"

    await hass.services.async_call(
        "switch",
        "turn_on",
        target={"entity_id": switch_entity_id},
    )
    await hass.async_block_till_done()

    state = hass.states.get(switch_entity_id)
    assert state
    assert state.state == "off"


@respx.mock
async def test_turn_emergency_switch_keep_state_if_call_failed(
    mock_config_entry: MockConfigEntry,  # noqa: ARG001
    hass: HomeAssistant,
) -> None:
    """Test that turn off will call the correct endpoint."""
    respx.get(f"http://{HOST}/on").respond(status_code=400)

    state = hass.states.get(switch_entity_id)
    assert state
    assert state.state == "off"

    await hass.services.async_call(
        "switch",
        "turn_on",
        target={"entity_id": switch_entity_id},
    )
    await hass.async_block_till_done()

    state = hass.states.get(switch_entity_id)
    assert state
    assert state.state == "off"


binary_data_ema_register_values = ema_register_values.copy()
binary_data_ema_register_values[EMA_STATUS_REGISTER] = 0xFFF


@pytest.mark.parametrize(
    ("read_ema_input_registers_response"),
    [ReadInputRegistersResponse(registers=binary_data_ema_register_values)],
)
async def test_emergency_switch_initialize_from_binary_sensor(
    mock_config_entry: MockConfigEntry,  # noqa: ARG001
    hass: HomeAssistant,
) -> None:
    """Test that turn off will call the correct endpoint."""
    state = hass.states.get(switch_entity_id)
    assert state
    assert state.state == "on"
