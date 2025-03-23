"""Tests for the switch sensor entities."""

from math import isclose
from random import randint

import pytest
from homeassistant.const import (
    STATE_OFF,
    STATE_ON,
)
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.askoheat.const import (
    CONF_POWER_ENTITY_ID,
    CONF_POWER_INVERT,
    NumberAttrKey,
    SwitchAttrKey,
)


@pytest.mark.parametrize(
    (
        "conf_feedin",
        "power_entity_id",
        "invert",
        "buffer_value",
        "power_value",
    ),
    [
        (
            {
                CONF_POWER_ENTITY_ID: "input_number.test_energy",
                CONF_POWER_INVERT: invert,
            },
            "input_number.test_energy",
            invert,
            buffer_value,
            power_value,
        )
        for buffer_value in [randint(1, 200) for _ in range(2)]  # noqa: S311
        for power_value in [randint(-1000, 1000) for _ in range(2)]  # noqa: S311
        for invert in [True, False]
    ],
)
async def test_auto_feed_in_switch_sensor_state(  # noqa: PLR0913, PLR0915
    mock_config_entry_uninitialized: MockConfigEntry,
    hass: HomeAssistant,
    power_entity_id: str,
    invert: bool,  # noqa: FBT001
    buffer_value: int,
    power_value: int,
) -> None:
    """Test behaviour of auto feed-in switch sensor."""
    # initialize dummy power sensor
    assert await async_setup_component(
        hass,
        "input_number",
        {
            "input_number": {
                "test_energy": {
                    "name": "test_energy",
                    "unit_of_measurement": "W",
                    "min": "-1000",
                    "initial": "0",
                    "max": "1000",
                }
            }
        },
    )
    await hass.async_block_till_done()
    state = hass.states.get(power_entity_id)
    assert state
    assert float(state.state) == float(0)

    # initialize config entry
    mock_config_entry_uninitialized.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry_uninitialized.entry_id)
    await hass.async_block_till_done()

    # ensure buffer was initialized
    buffer_entity_id = f"number.test_{NumberAttrKey.EMA_AUTO_FEEDIN_BUFFER}"
    state = hass.states.get(buffer_entity_id)
    assert state
    assert state.state == "unknown"

    # set buffer entity value
    await hass.services.async_call(
        "number",
        "set_value",
        target={"entity_id": buffer_entity_id},
        service_data={"value": buffer_value},
    )
    # set power entity value
    await hass.services.async_call(
        "input_number",
        "set_value",
        target={"entity_id": power_entity_id},
        service_data={"value": power_value},
    )
    await hass.async_block_till_done()

    # validate output is set to 0
    feed_in_entity_id = f"number.test_{NumberAttrKey.LOAD_FEEDIN_VALUE}"
    state = hass.states.get(feed_in_entity_id)
    assert state
    assert float(state.state) == float(0)

    # enable switch
    switch_entity_id = f"switch.test_{SwitchAttrKey.EMA_AUTO_FEEDIN_SWITCH}"
    await hass.services.async_call(
        "switch",
        "turn_on",
        service_data={"entity_id": switch_entity_id},
    )
    await hass.async_block_till_done()

    state = hass.states.get(switch_entity_id)
    assert state
    assert state.state == STATE_ON

    # update other sensors
    mock_config_entry_uninitialized.runtime_data.ema_coordinator.async_update_listeners()
    await hass.async_block_till_done()

    # validate output
    expected_value = (
        power_value + buffer_value if not invert else -power_value + buffer_value
    )

    state = hass.states.get(feed_in_entity_id)
    assert state
    assert isclose(float(state.state), expected_value), (
        f"Expect state {expected_value} for entity {feed_in_entity_id}, but received {state.state}. power_value={power_value}, buffer_value={buffer_value}, invert={invert}."  # noqa: E501
    )

    # change buffer will recalculate feed-in
    buffer_value = buffer_value + 1
    await hass.services.async_call(
        "number",
        "set_value",
        target={"entity_id": buffer_entity_id},
        service_data={"value": buffer_value},
    )
    await hass.async_block_till_done()
    # update other sensors
    mock_config_entry_uninitialized.runtime_data.ema_coordinator.async_update_listeners()
    await hass.async_block_till_done()

    expected_value = (
        power_value + buffer_value if not invert else -power_value + buffer_value
    )

    state = hass.states.get(feed_in_entity_id)
    assert state
    assert isclose(float(state.state), expected_value), (
        f"Expect state after increasing buffer value {expected_value} for entity {feed_in_entity_id}, but received {state.state}."  # noqa: E501
    )

    # change power value will recalculate feed-in
    power_value = power_value - 1
    await hass.services.async_call(
        "input_number",
        "set_value",
        target={"entity_id": power_entity_id},
        service_data={"value": power_value},
    )
    await hass.async_block_till_done()
    # update other sensors
    mock_config_entry_uninitialized.runtime_data.ema_coordinator.async_update_listeners()
    await hass.async_block_till_done()

    expected_value = (
        power_value + buffer_value if not invert else -power_value + buffer_value
    )

    state = hass.states.get(feed_in_entity_id)
    assert state
    assert isclose(float(state.state), expected_value), (
        f"Expect state after increasing power value {expected_value} for entity {feed_in_entity_id}, but received {state.state}."  # noqa: E501
    )

    # disable switch
    await hass.services.async_call(
        "switch",
        "turn_off",
        service_data={"entity_id": switch_entity_id},
    )
    await hass.async_block_till_done()

    state = hass.states.get(switch_entity_id)
    assert state
    assert state.state == STATE_OFF

    # update other sensors
    mock_config_entry_uninitialized.runtime_data.ema_coordinator.async_update_listeners()
    await hass.async_block_till_done()

    # validate output is set again to 0
    state = hass.states.get(feed_in_entity_id)
    assert state
    assert float(state.state) == float(0)
