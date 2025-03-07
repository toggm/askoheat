"""Tests for the binary sensor entities."""

from datetime import timedelta
from decimal import Decimal
from math import isclose
from typing import Any

import pytest
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from pymodbus.pdu.register_message import (
    ReadHoldingRegistersResponse,
    ReadInputRegistersResponse,
)
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.askoheat.api_conf_desc import CONF_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_ema_desc import EMA_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_op_desc import DATA_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_par_desc import PARAM_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.const import AttributeKeys, SensorAttrKey
from custom_components.askoheat.model import (
    AskoheatDurationSensorEntityDescription,
    AskoheatSensorEntityDescription,
)

from .testdata import (
    config_register_values,
    data_register_values,
    ema_register_values,
    fill_test_data,
    par_register_values,
)

# prepare sensor data
sensor_entities = [
    entity_descriptor
    for entity_descriptor in (
        CONF_REGISTER_BLOCK_DESCRIPTOR.sensors
        + PARAM_REGISTER_BLOCK_DESCRIPTOR.sensors
        + EMA_REGISTER_BLOCK_DESCRIPTOR.sensors
        + DATA_REGISTER_BLOCK_DESCRIPTOR.sensors
    )
    if entity_descriptor.api_descriptor
    and entity_descriptor.entity_registry_enabled_default
]


sensor_data_register_values = data_register_values.copy()
sensor_par_register_values = par_register_values.copy()
sensor_ema_register_values = ema_register_values.copy()
sensor_conf_register_values = config_register_values.copy()

sensor_test_data: dict[SensorAttrKey, Any] = {}

fill_test_data(
    CONF_REGISTER_BLOCK_DESCRIPTOR.sensors,
    sensor_conf_register_values,
    sensor_test_data,
)
fill_test_data(
    DATA_REGISTER_BLOCK_DESCRIPTOR.sensors,
    sensor_data_register_values,
    sensor_test_data,
)
fill_test_data(
    PARAM_REGISTER_BLOCK_DESCRIPTOR.sensors,
    sensor_par_register_values,
    sensor_test_data,
)
fill_test_data(
    EMA_REGISTER_BLOCK_DESCRIPTOR.sensors, sensor_ema_register_values, sensor_test_data
)


@pytest.mark.parametrize(
    (
        "read_config_holding_registers_response",
        "read_data_input_registers_response",
        "read_par_input_registers_response",
        "read_ema_input_registers_response",
        "entity_descriptor",
    ),
    [
        (
            ReadHoldingRegistersResponse(registers=sensor_conf_register_values),
            ReadInputRegistersResponse(registers=sensor_data_register_values),
            ReadInputRegistersResponse(registers=sensor_par_register_values),
            ReadInputRegistersResponse(registers=sensor_ema_register_values),
            entity_descriptor,
        )
        for entity_descriptor in sensor_entities
    ],
)
async def test_read_sensor_states(
    mock_config_entry: MockConfigEntry,  # noqa: ARG001
    hass: HomeAssistant,
    entity_descriptor: AskoheatSensorEntityDescription,
) -> None:
    """Test reading sensor."""
    key = f"sensor.test_{entity_descriptor.key}"
    state = hass.states.get(key)
    assert state

    expected = (
        0
        if sensor_test_data[entity_descriptor.key] is None
        else sensor_test_data[entity_descriptor.key]
    )

    if entity_descriptor.factor is not None:
        expected *= entity_descriptor.factor

    # for entity descriptors provided a precision we expect a rounded value
    if entity_descriptor.native_precision is not None:
        expected = expected.__round__(entity_descriptor.native_precision)

    if isinstance(entity_descriptor, AskoheatDurationSensorEntityDescription):
        days = int(expected) >> 16
        hours = int(expected) >> 8 & 0xFF
        minutes = int(expected) & 0xFF

        expected_duration = 0
        expected_unit = ""
        match entity_descriptor.native_unit_of_measurement:
            case UnitOfTime.DAYS:
                expected_duration = days
                expected_unit = "days"
            case UnitOfTime.HOURS:
                expected_duration = days * 24 + hours
                expected_unit = "hours"
            case _:
                expected_duration = days * 24 * 60 + hours * 60 + minutes
                expected_unit = "minutes"
        assert int(state.state) == expected_duration, (
            f"Expect {expected_duration} {expected_unit} from duration {expected} for entity {entity_descriptor.key}, but received {state.state}."  # noqa: E501
        )
        expected_duration_str = timedelta(
            days=days, hours=hours, minutes=minutes
        ).__str__()
        assert state.attributes[AttributeKeys.FORMATTED] == expected_duration_str, (
            f"Expected formatted duration in states attributes to be {expected_duration_str}. but received {state.attributes[AttributeKeys.FORMATTED]} ."  # noqa: E501
        )
    elif isinstance(expected, float):
        assert isclose(float(state.state), expected), (
            f"Expect state {expected}({type(expected)}) for entity {entity_descriptor.key} to be close to {state.state}({type(state.state)})."  # noqa: E501
        )
    elif isinstance(expected, int):
        assert Decimal(state.state) == Decimal(expected), (
            f"Expect state {expected!s}({type(expected)}) for entity {entity_descriptor.key}, but received {state.state}({type(state.state)})."  # noqa: E501
        )
    else:
        assert state.state == str(expected), (
            f"Expect state {expected!s}({type(expected)}) for entity {entity_descriptor.key}, but received {state.state}({type(state.state)})."  # noqa: E501
        )
