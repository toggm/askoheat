"""Test the askoheat integration config flow."""

from collections.abc import Iterator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.service_info.dhcp import DhcpServiceInfo
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.askoheat.api import AskoheatModbusApiClientCommunicationError
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


OLD_HOST = "10.0.0.5"
PORT = 502
NEW_HOST = "10.0.0.9"
MAC = "a842e3daa3a0"
MAC_SERIAL = "A8:42:E3:DA:A3:A0"


@pytest.fixture
def mock_api() -> Iterator[MagicMock]:
    """Patch the modbus client used by the config flow and the entry setup."""
    with (
        patch(
            "custom_components.askoheat.config_flow.AskoheatModbusApiClient",
            autospec=True,
        ) as api,
        patch("custom_components.askoheat.async_setup_entry", return_value=True),
    ):
        api.return_value.connect = AsyncMock()
        yield api


def _device_reports(mock_api: MagicMock, serial: str) -> None:
    mock_api.return_value.async_read_par_data = AsyncMock(
        return_value=AskoheatDataBlock(
            sensors={
                SensorAttrKey.PAR_ID: serial,
                SensorAttrKey.PAR_ARTICLE_NAME: "article",
                SensorAttrKey.PAR_ARTICLE_NUMBER: "123",
            },
            binary_sensors={},
        )
    )


def _device_unreachable(mock_api: MagicMock) -> None:
    mock_api.return_value.async_read_par_data = AsyncMock(
        side_effect=AskoheatModbusApiClientCommunicationError
    )


def _add_entry(
    hass: HomeAssistant, unique_id: str, device_serial: str | None = None
) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=unique_id,
        data={CONF_HOST: OLD_HOST, CONF_PORT: PORT},
    )
    entry.add_to_hass(hass)
    if device_serial is not None:
        dr.async_get(hass).async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, f"water_heater_control_unit.{entry.entry_id}")},
            serial_number=device_serial,
        )
    return entry


async def _discover(hass: HomeAssistant, ip: str = NEW_HOST, mac: str = MAC) -> Any:
    return await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_DHCP},
        data=DhcpServiceInfo(ip=ip, hostname="askoheat", macaddress=mac),
    )


async def test_dhcp_known_mac_updates_host(
    hass: HomeAssistant, mock_api: MagicMock
) -> None:
    """The MAC is part of the entry's id: only the address is updated."""
    entry = _add_entry(hass, f"{DOMAIN}_{MAC_SERIAL.lower()}")

    result = await _discover(hass)

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert entry.data[CONF_HOST] == NEW_HOST
    assert entry.data[CONF_PORT] == PORT
    mock_api.assert_not_called()


async def test_dhcp_mac_matches_device_serial_in_registry(
    hass: HomeAssistant, mock_api: MagicMock
) -> None:
    """Entry created with a readable serial, the device reports the MAC now."""
    entry = _add_entry(hass, f"{DOMAIN}_xxc32t", device_serial=MAC_SERIAL)

    result = await _discover(hass)

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert entry.data[CONF_HOST] == NEW_HOST
    mock_api.assert_not_called()


async def test_dhcp_unknown_mac_matches_live_serial(
    hass: HomeAssistant, mock_api: MagicMock
) -> None:
    """MAC unknown, but the device itself reports the serial of an entry."""
    entry = _add_entry(hass, f"{DOMAIN}_xxc32t")
    _device_reports(mock_api, "XXC32T")

    result = await _discover(hass, mac="aabbccddeeff")

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert entry.data[CONF_HOST] == NEW_HOST


async def test_dhcp_reused_address_is_not_matched_by_host(
    hass: HomeAssistant, mock_api: MagicMock
) -> None:
    """Another device on the address of a configured one is a new device."""
    entry = _add_entry(hass, f"{DOMAIN}_xxc32t")
    hass.config_entries.async_update_entry(
        entry, data={CONF_HOST: NEW_HOST, CONF_PORT: PORT}
    )
    _device_reports(mock_api, "OTHER1")

    result = await _discover(hass, mac="aabbccddeeff")

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert entry.data == {CONF_HOST: NEW_HOST, CONF_PORT: PORT}
    assert len(hass.config_entries.async_entries(DOMAIN)) == 1


async def test_dhcp_unreachable_device_can_be_ignored(
    hass: HomeAssistant, mock_api: MagicMock
) -> None:
    """Without identity the flow still has a stable id, so it can be ignored."""
    _device_unreachable(mock_api)

    result = await _discover(hass, mac="aabbccddeeff")
    assert result["type"] is FlowResultType.FORM
    flow = hass.config_entries.flow.async_get(result["flow_id"])
    assert flow["context"]["unique_id"] == f"{DOMAIN}_aabbccddeeff"

    ignored = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_IGNORE},
        data={"unique_id": f"{DOMAIN}_aabbccddeeff", "title": "askoheat"},
    )
    assert ignored["type"] is FlowResultType.CREATE_ENTRY

    again = await _discover(hass, mac="aabbccddeeff")
    assert again["type"] is FlowResultType.ABORT
    assert again["reason"] == "already_configured"


async def test_user_flow_device_with_changed_serial_is_not_duplicated(
    hass: HomeAssistant, mock_api: MagicMock
) -> None:
    """Adding a device again whose reported serial changed updates the entry."""
    entry = _add_entry(hass, f"{DOMAIN}_xxc32t", device_serial=MAC_SERIAL)
    _device_reports(mock_api, MAC_SERIAL)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_HOST: NEW_HOST,
            CONF_PORT: PORT,
            CONF_DEVICE_UNITS: {},
            CONF_FEED_IN: {},
        },
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert entry.data[CONF_HOST] == NEW_HOST
    assert len(hass.config_entries.async_entries(DOMAIN)) == 1
