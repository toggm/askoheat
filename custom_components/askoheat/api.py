"""Sample API Client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
from pymodbus.client import AsyncModbusTcpClient as ModbusClient

from custom_components.askoheat.const import (
    LOGGER,
    BinarySensorEMAAttrKey,
    SensorEMAAttrKey,
    SwitchEMAAttrKey,
)
from custom_components.askoheat.data import AskoheatEMAData

if TYPE_CHECKING:
    from pymodbus.pdu import ModbusPDU


class AskoheatModbusApiClientError(Exception):
    """Exception to indicate a general API error."""


class AskoheatModbusApiClientCommunicationError(
    AskoheatModbusApiClientError,
):
    """Exception to indicate a communication error."""


class AskoHeatModbusApiClient:
    """Sample API Client."""

    def __init__(self, host: str, port: int) -> None:
        """Askoheat Modbus API Client."""
        self._host = host
        self._port = port
        self._client = ModbusClient(host=host, port=port)

    async def connect(self) -> Any:
        """Connect to modbus client."""
        return await self._client.connect()

    def close(self) -> None:
        """Close comnection to modbus client."""
        self._client.close()

    async def async_read_ema_data(self) -> AskoheatEMAData:
        """Read EMA states."""
        # http://www.download.askoma.com/askofamily_plus/modbus/askoheat-modbus.html#EM_Block
        data = await self.async_read_input_registers_data(300, 37)
        LOGGER.info("async_read_ema_data %s", data)
        return self._map_ema_data(data)

    async def async_read_input_registers_data(
        self, address: int, count: int
    ) -> ModbusPDU:
        """Read holding registers through modbus."""
        if not self._client.connected:
            msg = "cannot read holding registers, not connected"
            raise AskoheatModbusApiClientCommunicationError(msg)

        return await self._client.read_input_registers(address=address, count=count)

    async def async_read_holding_registers_data(
        self, address: int, count: int
    ) -> ModbusPDU:
        """Read input registers through modbus."""
        if not self._client.connected:
            msg = "cannot read input registers, not connected"
            raise AskoheatModbusApiClientCommunicationError(msg)

        return await self._client.read_holding_registers(address=address, count=count)

    def _map_ema_data(self, data: ModbusPDU) -> AskoheatEMAData:
        """Map modbus result to EMA data structure."""
        return AskoheatEMAData(
            binary_sensors=self._map_register_to_status(data.registers[16]),
            sensors={
                SensorEMAAttrKey.HEATER_LOAD: _read_uint16(data.registers[17]),
                SensorEMAAttrKey.LOAD_SETPOINT_VALUE: _read_int16(data.registers[19]),
                SensorEMAAttrKey.LOAD_FEEDIN_VALUE: _read_int16(data.registers[20]),
                SensorEMAAttrKey.ANALOG_INPUT_VALUE: _read_float32(
                    data.registers[23:25]
                ),
                SensorEMAAttrKey.INTERNAL_TEMPERATUR_SENSOR_VALUE: _read_float32(
                    data.registers[25:27]
                ),
                SensorEMAAttrKey.EXTERNAL_TEMPERATUR_SENSOR1_VALUE: _read_float32(
                    data.registers[27:29]
                ),
                SensorEMAAttrKey.EXTERNAL_TEMPERATUR_SENSOR2_VALUE: _read_float32(
                    data.registers[29:31]
                ),
                SensorEMAAttrKey.EXTERNAL_TEMPERATUR_SENSOR3_VALUE: _read_float32(
                    data.registers[31:33]
                ),
                SensorEMAAttrKey.EXTERNAL_TEMPERATUR_SENSOR4_VALUE: _read_float32(
                    data.registers[33:35]
                ),
            },
            switches=self._map_register_to_heater_step(data.registers[18]),
        )

    def _map_register_to_status(
        self, register_value: int
    ) -> dict[BinarySensorEMAAttrKey, bool]:
        """Map modbus register status."""
        return {
            # low byte values
            BinarySensorEMAAttrKey.HEATER1_ACTIVE: _read_flag(register_value, 0),
            BinarySensorEMAAttrKey.HEATER2_ACTIVE: _read_flag(register_value, 1),
            BinarySensorEMAAttrKey.HEATER3_ACTIVE: _read_flag(register_value, 2),
            BinarySensorEMAAttrKey.PUMP_ACTIVE: _read_flag(register_value, 3),
            BinarySensorEMAAttrKey.RELAY_BOARD_CONNECTED: _read_flag(register_value, 4),
            # bit 5 ignored
            BinarySensorEMAAttrKey.HEAT_PUMP_REQUEST_ACTIVE: _read_flag(
                register_value, 6
            ),
            BinarySensorEMAAttrKey.EMERGENCY_MODE_ACTIVE: _read_flag(register_value, 7),
            # high byte values
            BinarySensorEMAAttrKey.LEGIONELLA_PROTECTION_ACTIVE: _read_flag(
                register_value, 8
            ),
            BinarySensorEMAAttrKey.ANALOG_INPUT_ACTIVE: _read_flag(register_value, 9),
            BinarySensorEMAAttrKey.SETPOINT_ACTIVE: _read_flag(register_value, 10),
            BinarySensorEMAAttrKey.LOAD_FEEDIN_ACTIVE: _read_flag(register_value, 11),
            BinarySensorEMAAttrKey.AUTOHEATER_OFF_ACTIVE: _read_flag(
                register_value, 12
            ),
            BinarySensorEMAAttrKey.PUMP_RELAY_FOLLOW_UP_TIME_ACTIVE: _read_flag(
                register_value, 13
            ),
            BinarySensorEMAAttrKey.TEMP_LIMIT_REACHED: _read_flag(register_value, 14),
            BinarySensorEMAAttrKey.ERROR_OCCURED: _read_flag(register_value, 15),
        }

    def _map_register_to_heater_step(
        self, register_value: int
    ) -> dict[SwitchEMAAttrKey, bool]:
        """Map modbus register to status class."""
        return {
            SwitchEMAAttrKey.SET_HEATER_STEP_HEATER1: _read_flag(register_value, 0),
            SwitchEMAAttrKey.SET_HEATER_STEP_HEATER2: _read_flag(register_value, 1),
            SwitchEMAAttrKey.SET_HEATER_STEP_HEATER3: _read_flag(register_value, 2),
        }


def _read_int16(register_value: int) -> np.int16:
    """Read register value as int16."""
    return np.int16(
        ModbusClient.convert_from_registers(
            [register_value], ModbusClient.DATATYPE.INT16
        )
    )


def _read_uint16(register_value: int) -> np.uint16:
    """Read register value as uint16."""
    return np.uint16(
        ModbusClient.convert_from_registers(
            [register_value], ModbusClient.DATATYPE.UINT16
        )
    )


def _read_float32(register_values: list[int]) -> np.float32:
    """Read register value as uint16."""
    return np.float32(
        ModbusClient.convert_from_registers(
            register_values, ModbusClient.DATATYPE.FLOAT32
        )
    )


def _read_flag(register_value: int, index: int) -> bool:
    """Validate if bit at provided index is set."""
    return (register_value >> index) & 0x01 == 0x01
