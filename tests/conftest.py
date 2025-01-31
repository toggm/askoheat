"""Fixtures for testing."""

from typing import Any
from unittest import mock

import pytest
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from pymodbus.pdu.register_message import (
    ReadHoldingRegistersResponse,
    ReadInputRegistersResponse,
)
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.askoheat import AskoheatModbusApiClient, data
from custom_components.askoheat.api_conf_desc import CONF_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_desc import RegisterBlockDescriptor
from custom_components.askoheat.api_ema_desc import EMA_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_op_desc import DATA_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_par_desc import PARAM_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.const import (
    CONF_ANALOG_INPUT_UNIT,
    CONF_DEVICE_UNITS,
    CONF_HEATPUMP_UNIT,
    CONF_LEGIONELLA_PROTECTION_UNIT,
    CONF_MODBUS_MASTER_UNIT,
    DOMAIN,
    LOGGER,
    DeviceKey,
)
from custom_components.askoheat.coordinator import (
    AskoheatConfigDataUpdateCoordinator,
    AskoheatEMADataUpdateCoordinator,
    AskoheatOperationDataUpdateCoordinator,
    AskoheatParameterDataUpdateCoordinator,
)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(
    enable_custom_integrations: bool,  # noqa: ARG001, FBT001
) -> None:
    """Enable custom integration."""
    return


@pytest.fixture
def read_config_holding_registers_response() -> ReadHoldingRegistersResponse:
    """Fixture returning object representing default config holding register."""
    return ReadHoldingRegistersResponse(
        registers=[0 for _ in range(CONF_REGISTER_BLOCK_DESCRIPTOR.number_of_registers)]
    )


@pytest.fixture
def read_par_input_registers_response() -> ReadInputRegistersResponse:
    """Fixture returning object representing default parameter input register."""
    return ReadInputRegistersResponse(
        registers=[
            0 for _ in range(PARAM_REGISTER_BLOCK_DESCRIPTOR.number_of_registers)
        ]
    )


@pytest.fixture
def read_data_input_registers_response() -> ReadInputRegistersResponse:
    """Fixture returning object representing default operation/data input register."""
    return ReadInputRegistersResponse(
        registers=[0 for _ in range(DATA_REGISTER_BLOCK_DESCRIPTOR.number_of_registers)]
    )


@pytest.fixture
def read_ema_input_registers_response() -> ReadInputRegistersResponse:
    """Fixture returning object representing default ema input register."""
    return ReadInputRegistersResponse(
        registers=[0 for _ in range(EMA_REGISTER_BLOCK_DESCRIPTOR.number_of_registers)]
    )


@pytest.fixture
def mock_api_client(
    read_config_holding_registers_response: ReadHoldingRegistersResponse,
    read_par_input_registers_response: ReadInputRegistersResponse,
    read_data_input_registers_response: ReadInputRegistersResponse,
    read_ema_input_registers_response: ReadInputRegistersResponse,
) -> Any:
    """Fixture to pymodbus AsyncModbusTcpClient."""

    def dispatch_read_input_registers(
        address: int,
        count: int,  # noqa: ARG001
    ) -> ReadInputRegistersResponse:
        match address:
            case PARAM_REGISTER_BLOCK_DESCRIPTOR.starting_register:
                return read_par_input_registers_response
            case DATA_REGISTER_BLOCK_DESCRIPTOR.starting_register:
                return read_data_input_registers_response
            case EMA_REGISTER_BLOCK_DESCRIPTOR.starting_register:
                return read_ema_input_registers_response
            case _:
                return ReadInputRegistersResponse()

    def dispatch_write_input_registers(address: int, values: list[int]) -> None:
        def _in_register(address: int, register: RegisterBlockDescriptor) -> bool:
            return (
                address > register.starting_register
                and address < register.starting_register + register.number_of_registers
            )

        def _replace_values(source: list[int], dest: list[int], address: int) -> None:
            for index in range(len(source)):
                dest[address + index] = source[index]

        match address:
            case address if _in_register(address, CONF_REGISTER_BLOCK_DESCRIPTOR):
                _replace_values(
                    source=values,
                    dest=read_config_holding_registers_response.registers,
                    address=address - CONF_REGISTER_BLOCK_DESCRIPTOR.starting_register,
                )
            case address if _in_register(address, EMA_REGISTER_BLOCK_DESCRIPTOR):
                _replace_values(
                    source=values,
                    dest=read_ema_input_registers_response.registers,
                    address=address - EMA_REGISTER_BLOCK_DESCRIPTOR.starting_register,
                )
            case _:
                LOGGER.error("Unsupported register at address %s", address)

    patched = mock.patch.multiple(
        "custom_components.askoheat.api.AsyncModbusTcpClient",
        connect=mock.AsyncMock(),
        connected=True,
        read_holding_registers=mock.AsyncMock(
            return_value=read_config_holding_registers_response
        ),
        read_input_registers=mock.AsyncMock(side_effect=dispatch_read_input_registers),
        write_registers=mock.AsyncMock(side_effect=dispatch_write_input_registers),
    )
    patched.__enter__()
    return patched


@pytest.fixture(autouse=False)
def mock_device_infos() -> Any:
    """Fixture to mock the device info."""
    patched = mock.patch(
        "custom_components.askoheat.AskoheatData.device_info",
        return_value=data.AskoheatDeviceInfos(data={}),
    )
    patched.__enter__()
    yield patched
    patched.__exit__(None, None, None)


@pytest.fixture
async def mock_config_entry(
    mock_api_client: AskoheatModbusApiClient, hass: HomeAssistant
) -> MockConfigEntry:
    """Fixture to mock config entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: "192.199.1.2",
            CONF_PORT: 502,
            CONF_DEVICE_UNITS: {
                CONF_LEGIONELLA_PROTECTION_UNIT: True,
                CONF_ANALOG_INPUT_UNIT: True,
                CONF_MODBUS_MASTER_UNIT: True,
                CONF_HEATPUMP_UNIT: True,
            },
        },
        unique_id="test",
    )
    entry.runtime_data = data.AskoheatData(
        client=mock_api_client,
        integration=mock.MagicMock(),
        ema_coordinator=AskoheatEMADataUpdateCoordinator(
            hass=hass, client=mock_api_client
        ),
        config_coordinator=AskoheatConfigDataUpdateCoordinator(
            hass=hass, client=mock_api_client
        ),
        par_coordinator=AskoheatParameterDataUpdateCoordinator(
            hass=hass, client=mock_api_client
        ),
        data_coordinator=AskoheatOperationDataUpdateCoordinator(
            hass=hass, client=mock_api_client
        ),
        supported_devices=list(DeviceKey),
    )

    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    return entry
