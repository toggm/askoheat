"""Test the askoheat integration config flow."""

from unittest.mock import AsyncMock, patch

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.askoheat.const import (
    CONF_ANALOG_INPUT_UNIT,
    CONF_DEVICE_UNITS,
    CONF_FEED_IN,
    CONF_HEATPUMP_UNIT,
    CONF_LEGIONELLA_PROTECTION_UNIT,
    CONF_MODBUS_MASTER_UNIT,
    CONF_POWER_ENTITY_ID,
    CONF_POWER_INVERT,
    DOMAIN,
    SensorAttrKey,
)
from custom_components.askoheat.data import AskoheatDataBlock


async def test_config_flow_with_defaults(hass: HomeAssistant) -> None:
    """Test the config flow with default values."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result.get("type") is FlowResultType.FORM
    assert result.get("step_id") == "user"

    with (
        patch(
            "custom_components.askoheat.config_flow.AskoheatModbusApiClient",
            autospec=True,
        ) as mock_api,
        patch(
            "custom_components.askoheat.async_setup_entry",
            return_value=True,
        ) as mock_setup_entry,
    ):
        par_data = AskoheatDataBlock(
            sensors={
                SensorAttrKey.PAR_ID: "1234",
                SensorAttrKey.PAR_ARTICLE_NAME: "test_article",
                SensorAttrKey.PAR_ARTICLE_NUMBER: "abc-123",
            },
            binary_sensors={},
        )
        mock_api.return_value.connect = AsyncMock()
        mock_api.return_value.async_read_par_data = AsyncMock(return_value=par_data)

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "10.0.0.131",
                CONF_PORT: 501,
                CONF_DEVICE_UNITS: {},
                CONF_FEED_IN: {},
            },
        )
        assert result2.get("type") is FlowResultType.CREATE_ENTRY
        assert result2.get("title") == "test_article abc-123 1234"
        assert result2.get("data") == {
            CONF_HOST: "10.0.0.131",
            CONF_PORT: 501,
            CONF_FEED_IN: {
                CONF_POWER_ENTITY_ID: [],
                CONF_POWER_INVERT: False,
            },
            CONF_DEVICE_UNITS: {
                CONF_LEGIONELLA_PROTECTION_UNIT: True,  # defaults to true
                CONF_ANALOG_INPUT_UNIT: False,
                CONF_MODBUS_MASTER_UNIT: False,
                CONF_HEATPUMP_UNIT: False,
            },
        }
        await hass.async_block_till_done()
        assert len(mock_setup_entry.mock_calls) == 1


async def test_full_config_flow(hass: HomeAssistant) -> None:
    """Test the full config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result.get("type") is FlowResultType.FORM
    assert result.get("step_id") == "user"

    with (
        patch(
            "custom_components.askoheat.config_flow.AskoheatModbusApiClient",
            autospec=True,
        ) as mock_api,
        patch(
            "custom_components.askoheat.async_setup_entry",
            return_value=True,
        ) as mock_setup_entry,
    ):
        par_data = AskoheatDataBlock(
            sensors={
                SensorAttrKey.PAR_ID: "1234",
                SensorAttrKey.PAR_ARTICLE_NAME: "test_article",
                SensorAttrKey.PAR_ARTICLE_NUMBER: "abc-123",
            },
            binary_sensors={},
        )
        mock_api.return_value.connect = AsyncMock()
        mock_api.return_value.async_read_par_data = AsyncMock(return_value=par_data)

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_HOST: "10.0.0.131",
                CONF_PORT: 501,
                CONF_DEVICE_UNITS: {
                    CONF_LEGIONELLA_PROTECTION_UNIT: False,
                    CONF_ANALOG_INPUT_UNIT: True,
                    CONF_MODBUS_MASTER_UNIT: True,
                    CONF_HEATPUMP_UNIT: True,
                },
                CONF_FEED_IN: {
                    CONF_POWER_ENTITY_ID: "sensor.my_power_entity",
                    CONF_POWER_INVERT: True,
                },
            },
        )
        assert result2.get("type") is FlowResultType.CREATE_ENTRY
        assert result2.get("title") == "test_article abc-123 1234"
        assert result2.get("data") == {
            CONF_HOST: "10.0.0.131",
            CONF_PORT: 501,
            CONF_FEED_IN: {
                CONF_POWER_ENTITY_ID: "sensor.my_power_entity",
                CONF_POWER_INVERT: True,
            },
            CONF_DEVICE_UNITS: {
                CONF_LEGIONELLA_PROTECTION_UNIT: False,
                CONF_ANALOG_INPUT_UNIT: True,
                CONF_MODBUS_MASTER_UNIT: True,
                CONF_HEATPUMP_UNIT: True,
            },
        }
        await hass.async_block_till_done()
        assert len(mock_setup_entry.mock_calls) == 1
