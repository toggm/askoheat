"""Sample API Client."""

from __future__ import annotations

from ast import Num
from datetime import datetime, time
from numbers import Number
from typing import TYPE_CHECKING, Any

import numpy as np
from pymodbus.client import AsyncModbusTcpClient as ModbusClient

from custom_components.askoheat.const import (
    LOGGER,
    Baurate,
    BinarySensorAttrKey,
    EnergyMeterType,
    NumberAttrKey,
    SelectAttrKey,
    SensorAttrKey,
    SwitchAttrKey,
    TextAttrKey,
    TimeAttrKey,
)
from custom_components.askoheat.data import AskoheatDataBlock

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

    async def async_read_ema_data(self) -> AskoheatDataBlock:
        """Read EMA states."""
        # http://www.download.askoma.com/askofamily_plus/modbus/askoheat-modbus.html#EM_Block
        data = await self.async_read_input_registers_data(300, 37)
        LOGGER.debug("async_read_ema_data %s", data)
        return self._map_ema_data(data)

    async def async_read_config_data(self) -> AskoheatDataBlock:
        """Read EMA states."""
        # http://www.download.askoma.com/askofamily_plus/modbus/askoheat-modbus.html#Configuration_Block
        data = await self.async_read_input_registers_data(500, 100)
        LOGGER.debug("async_read_config_data %s", data)
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

    def _map_ema_data(self, data: ModbusPDU) -> AskoheatDataBlock:
        """Map modbus result of ema data block."""
        return AskoheatDataBlock(
            binary_sensors=self._map_register_to_status(data.registers[16]),
            sensors={
                SensorAttrKey.HEATER_LOAD: _read_uint16(data.registers[17]),
                SensorAttrKey.LOAD_SETPOINT_VALUE: _read_int16(data.registers[19]),
                SensorAttrKey.LOAD_FEEDIN_VALUE: _read_int16(data.registers[20]),
                SensorAttrKey.ANALOG_INPUT_VALUE: _read_float32(data.registers[23:25]),
                SensorAttrKey.INTERNAL_TEMPERATUR_SENSOR_VALUE: _read_float32(
                    data.registers[25:27]
                ),
                SensorAttrKey.EXTERNAL_TEMPERATUR_SENSOR1_VALUE: _read_float32(
                    data.registers[27:29]
                ),
                SensorAttrKey.EXTERNAL_TEMPERATUR_SENSOR2_VALUE: _read_float32(
                    data.registers[29:31]
                ),
                SensorAttrKey.EXTERNAL_TEMPERATUR_SENSOR3_VALUE: _read_float32(
                    data.registers[31:33]
                ),
                SensorAttrKey.EXTERNAL_TEMPERATUR_SENSOR4_VALUE: _read_float32(
                    data.registers[33:35]
                ),
            },
            switches=self._map_register_to_heater_step(data.registers[18]),
        )

    def _map_config_data(self, data: ModbusPDU) -> AskoheatDataBlock:
        """Map modbus result of config data block."""
        return AskoheatDataBlock(
            number_inputs={
                NumberAttrKey.CON_RELAY_SEC_COUNT_SECONDS: _read_uint16(
                    data.registers[0]
                ),
                NumberAttrKey.CON_PUMP_SEC_COUNT_SECONDS: _read_uint16(
                    data.registers[1]
                ),
                NumberAttrKey.CON_AUTO_HEATER_OFF_MINUTES: _read_uint16(
                    data.registers[3]
                ),
                NumberAttrKey.CON_CASCADE_PRIORIZATION: _read_byte(data.registers[5]),
                NumberAttrKey.CON_HEATBUFFER_VOLUME: _read_uint16(data.registers[7]),
                NumberAttrKey.CON_LEGIO_PROTECTION_TEMPERATURE: _read_byte(
                    data.registers[10]
                ),
                NumberAttrKey.CON_LEGIO_PROTECTION_HEATUP_MINUTES: _read_uint16(
                    data.registers[11]
                ),
                NumberAttrKey.CON_NUMBER_OF_HOUSEHOLD_MEMBERS: _read_byte(
                    data.registers[21]
                ),
                NumberAttrKey.CON_LOAD_FEEDIN_DELAY_SECONDS: _read_uint16(
                    data.registers[39]
                ),
                NumberAttrKey.CON_LOAD_FEEDIN_BASIC_ENERGY_LEVEL: _read_uint16(
                    data.registers[40]
                ),
                NumberAttrKey.CON_TIMEZONE_OFFSET: _read_int16(data.registers[41]),
                NumberAttrKey.CON_RTU_SLAVE_ID: _read_byte(data.registers[50]),
                NumberAttrKey.CON_ANALOG_INPUT_HYSTERESIS: _read_float32(
                    data.registers[56:58]
                ),
                # Analog 0
                NumberAttrKey.CON_ANALOG_INPUT_0_THRESHOLD: _read_float32(
                    data.registers[58:60]
                ),
                NumberAttrKey.CON_ANALOG_INPUT_0_STEP: _read_byte(data.registers[60]),
                NumberAttrKey.CON_ANALOG_INPUT_0_THRESHOLD_TEMPERATURE: _read_byte(
                    data.registers[61]
                ),
                # Analog 1
                NumberAttrKey.CON_ANALOG_INPUT_1_THRESHOLD: _read_float32(
                    data.registers[62:64]
                ),
                NumberAttrKey.CON_ANALOG_INPUT_1_STEP: _read_byte(data.registers[64]),
                NumberAttrKey.CON_ANALOG_INPUT_1_THRESHOLD_TEMPERATURE: _read_byte(
                    data.registers[65]
                ),
                # Analog 2
                NumberAttrKey.CON_ANALOG_INPUT_2_THRESHOLD: _read_float32(
                    data.registers[66:68]
                ),
                NumberAttrKey.CON_ANALOG_INPUT_2_STEP: _read_byte(data.registers[68]),
                NumberAttrKey.CON_ANALOG_INPUT_2_THRESHOLD_TEMPERATURE: _read_byte(
                    data.registers[69]
                ),
                # Analog 3
                NumberAttrKey.CON_ANALOG_INPUT_3_THRESHOLD: _read_float32(
                    data.registers[70:72]
                ),
                NumberAttrKey.CON_ANALOG_INPUT_3_STEP: _read_byte(data.registers[72]),
                NumberAttrKey.CON_ANALOG_INPUT_3_THRESHOLD_TEMPERATURE: _read_byte(
                    data.registers[73]
                ),
                # Analog 4
                NumberAttrKey.CON_ANALOG_INPUT_4_THRESHOLD: _read_float32(
                    data.registers[74:76]
                ),
                NumberAttrKey.CON_ANALOG_INPUT_4_STEP: _read_byte(data.registers[76]),
                NumberAttrKey.CON_ANALOG_INPUT_4_THRESHOLD_TEMPERATURE: _read_byte(
                    data.registers[77]
                ),
                # Analog 5
                NumberAttrKey.CON_ANALOG_INPUT_5_THRESHOLD: _read_float32(
                    data.registers[78:80]
                ),
                NumberAttrKey.CON_ANALOG_INPUT_5_STEP: _read_byte(data.registers[80]),
                NumberAttrKey.CON_ANALOG_INPUT_5_THRESHOLD_TEMPERATURE: _read_byte(
                    data.registers[81]
                ),
                # Analog 6
                NumberAttrKey.CON_ANALOG_INPUT_6_THRESHOLD: _read_float32(
                    data.registers[82:84]
                ),
                NumberAttrKey.CON_ANALOG_INPUT_6_STEP: _read_byte(data.registers[84]),
                NumberAttrKey.CON_ANALOG_INPUT_6_THRESHOLD_TEMPERATURE: _read_byte(
                    data.registers[65]
                ),
                # Analog 7
                NumberAttrKey.CON_ANALOG_INPUT_7_THRESHOLD: _read_float32(
                    data.registers[86:88]
                ),
                NumberAttrKey.CON_ANALOG_INPUT_7_STEP: _read_byte(data.registers[88]),
                NumberAttrKey.CON_ANALOG_INPUT_7_THRESHOLD_TEMPERATURE: _read_byte(
                    data.registers[89]
                ),
                NumberAttrKey.CON_HEAT_PUMP_REQUEST_OFF_STEP: _read_byte(
                    data.registers[90]
                ),
                NumberAttrKey.CON_HEAT_PUMP_REQUEST_ON_STEP: _read_byte(
                    data.registers[91]
                ),
                NumberAttrKey.CON_EMERGENCY_MODE_ON_STOP: _read_byte(
                    data.registers[92]
                ),
                NumberAttrKey.CON_TEMPERATURE_HYSTERESIS: _read_byte(
                    data.registers[93]
                ),
                NumberAttrKey.CON_MINIMAL_TEMPERATURE: _read_byte(data.registers[95]),
                NumberAttrKey.CON_SET_HEATER_STEP_TEMPERATURE_LIMIT: _read_byte(
                    data.registers[96]
                ),
                NumberAttrKey.CON_LOAD_FEEDIN_OR_SETPOINT_TEMPERATURE_LIMIT: _read_byte(
                    data.registers[97]
                ),
                NumberAttrKey.CON_LOW_TARIFF_TEMPERATURE_LIMIT: _read_byte(
                    data.registers[98]
                ),
                NumberAttrKey.CON_HEATPUMP_REQUEST_TEMPERATURE_LIMIT: _read_byte(
                    data.registers[99]
                ),
            },
            switches={
                # input settings register
                # low byte
                SwitchAttrKey.CON_MISSING_CURRENT_FLOW_TRIGGERS_ERROR: _read_flag(
                    data.registers[2], 0
                ),
                SwitchAttrKey.CON_HEATER_LOAD_VALUE_ONLY_IF_CURRENT_FLOWS: _read_flag(
                    data.registers[2], 1
                ),
                SwitchAttrKey.CON_LOAD_FEEDIN_VALUE_ENABLED: _read_flag(
                    data.registers[2], 2
                ),
                SwitchAttrKey.CON_LOAD_SETPOINT_VALUE_ENABLED: _read_flag(
                    data.registers[2], 3
                ),
                SwitchAttrKey.CON_SET_HEATER_STEP_VALUE_ENABLED: _read_flag(
                    data.registers[2], 4
                ),
                SwitchAttrKey.CON_SET_ANALOG_INPUT_ENABLED: _read_flag(
                    data.registers[2], 5
                ),
                SwitchAttrKey.CON_HEATPUMP_REQUEST_INPUT_ENABLED: _read_flag(
                    data.registers[2], 6
                ),
                SwitchAttrKey.CON_EMERGENCY_MODE_ENABLED: _read_flag(
                    data.registers[2], 7
                ),
                # high byte
                SwitchAttrKey.CON_HOLD_MINIMAL_TEMPERATURE_ENABELD: _read_flag(
                    data.registers[2], 8
                ),
                SwitchAttrKey.CON_HOLD_MINIMAL_TEMPERATURE_ENABELD: _read_flag(
                    data.registers[2], 9
                ),
                SwitchAttrKey.CON_SOFTWARE_CONTROL_SMA_SEMP_ENABLED: _read_flag(
                    data.registers[2], 10
                ),
                SwitchAttrKey.CON_SOFTWARE_CONTROL_SENEC_HOME_ENABLED: _read_flag(
                    data.registers[2], 11
                ),
                # auto heater off settings register
                # low byte
                SwitchAttrKey.CON_AUTO_OFF_ENABLED: _read_flag(data.registers[4], 0),
                SwitchAttrKey.CON_RESTART_IF_ENERGYMANAGER_CONNECTION_LOST: _read_flag(
                    data.registers[4], 1
                ),
                SwitchAttrKey.CON_AUTO_OFF_MODBUS_ENABLED: _read_flag(
                    data.registers[4], 4
                ),
                SwitchAttrKey.CON_AUTO_OFF_ANALOG_INPUT_ENABLED: _read_flag(
                    data.registers[4], 5
                ),
                SwitchAttrKey.CON_AUTO_OFF_HEAT_PUMP_REQUEST_ENABLED: _read_flag(
                    data.registers[4], 6
                ),
                SwitchAttrKey.CON_AUTO_OFF_EMERGENCY_MODE_ENABLED: _read_flag(
                    data.registers[4], 7
                ),
                # heatbuffer type register
                SwitchAttrKey.CON_HEATBUFFER_TYPE_TAP_WATER: _read_flag(
                    data.registers[6], 0
                ),
                SwitchAttrKey.CON_HEATBUFFER_TYPE_HEATING_WATER: _read_flag(
                    data.registers[6], 1
                ),
                SwitchAttrKey.CON_HEATBUFFER_TYPE_COMBINED_HEAT_AND_POWER_UNIT: _read_flag(
                    data.registers[6], 2
                ),
                SwitchAttrKey.CON_HEATBUFFER_TYPE_PELLET_FIRING: _read_flag(
                    data.registers[6], 3
                ),
                SwitchAttrKey.CON_HEATBUFFER_TYPE_GAS_BURNER: _read_flag(
                    data.registers[6], 4
                ),
                SwitchAttrKey.CON_HEATBUFFER_TYPE_OIL_BURNER: _read_flag(
                    data.registers[6], 5
                ),
                SwitchAttrKey.CON_HEATBUFFER_TYPE_HEAT_PUMP: _read_flag(
                    data.registers[6], 6
                ),
                SwitchAttrKey.CON_HEATBUFFER_TYPE_OTHER: _read_flag(
                    data.registers[6], 7
                ),
                # heater position register
                SwitchAttrKey.CON_HEATER_POSITION_BOTTOM: _read_flag(
                    data.registers[8], 0
                ),
                SwitchAttrKey.CON_HEATER_POSITION_MIDDLE: _read_flag(
                    data.registers[8], 1
                ),
                SwitchAttrKey.CON_HEATER_POSITION_ASKOWALL: _read_flag(
                    data.registers[8], 7
                ),
                # legio settings register
                # low byte
                SwitchAttrKey.CON_LEGIO_SETTINGS_USE_INTERNAL_TEMP_SENSOR: _read_flag(
                    data.registers[9], 0
                ),
                SwitchAttrKey.CON_LEGIO_SETTINGS_USE_EXTERNAL_TEMP_SENSOR1: _read_flag(
                    data.registers[9], 1
                ),
                SwitchAttrKey.CON_LEGIO_SETTINGS_USE_EXTERNAL_TEMP_SENSOR2: _read_flag(
                    data.registers[9], 2
                ),
                SwitchAttrKey.CON_LEGIO_SETTINGS_USE_EXTERNAL_TEMP_SENSOR3: _read_flag(
                    data.registers[9], 3
                ),
                SwitchAttrKey.CON_LEGIO_SETTINGS_USE_EXTERNAL_TEMP_SENSOR4: _read_flag(
                    data.registers[9], 4
                ),
                # high byte
                SwitchAttrKey.CON_LEGIO_SETTINGS_INTERVAL_DAILY: _read_flag(
                    data.registers[9], 8
                ),
                SwitchAttrKey.CON_LEGIO_SETTINGS_INTERVAL_WEEKLY: _read_flag(
                    data.registers[9], 9
                ),
                SwitchAttrKey.CON_LEGIO_SETTINGS_INTERVAL_FORTNIGHTLY: _read_flag(
                    data.registers[9], 10
                ),
                SwitchAttrKey.CON_LEGIO_SETTINGS_INTERVAL_MONTHLY: _read_flag(
                    data.registers[9], 11
                ),
                SwitchAttrKey.CON_LEGIO_SETTINGS_PREFER_FEEDIN_ENERGY: _read_flag(
                    data.registers[9], 12
                ),
                SwitchAttrKey.CON_LEGIO_SETTINGS_PROTECTION_ENABLED: _read_flag(
                    data.registers[9], 13
                ),
                # house type settings register
                # low byte
                SwitchAttrKey.CON_HOUSE_TYPE_SINGLE_FAMILY_HOUSE: _read_flag(
                    data.registers[20], 0
                ),
                SwitchAttrKey.CON_HOUSE_TYPE_TWO_FAMILY_HOUSE: _read_flag(
                    data.registers[20], 1
                ),
                SwitchAttrKey.CON_HOUSE_TYPE_APPARTMENT_BUILDING: _read_flag(
                    data.registers[20], 2
                ),
                SwitchAttrKey.CON_HOUSE_TYPE_COMMERCIAL_BUILDING: _read_flag(
                    data.registers[20], 7
                ),
                # Summer time int 1/0 as bool
                SwitchAttrKey.CON_SUMMERTIME_ENABLED: _read_int16(data.registers[42])
                == 1,
                # rtu settings register
                # low byte
                SwitchAttrKey.CON_RTU_SEND_TWO_STOP_BITS: _read_flag(
                    data.registers[49], 0
                ),
                SwitchAttrKey.CON_RTU_SEND_PARITY_EVEN: _read_flag(
                    data.registers[49], 1
                ),
                SwitchAttrKey.CON_RTU_SEND_PARITY_ODD: _read_flag(
                    data.registers[49], 2
                ),
                SwitchAttrKey.CON_RTU_SLAVE_MODE_ACTIVE: _read_flag(
                    data.registers[49], 7
                ),
                # high byte
                SwitchAttrKey.CON_RTU_MASTER_MODE_ACTIVE: _read_flag(
                    data.registers[49], 15
                ),
                # temperature settings register
                # low byte
                SwitchAttrKey.CON_USE_INTERNAL_TEMP_SENSOR: _read_flag(
                    data.registers[94], 0
                ),
                SwitchAttrKey.CON_USE_EXTERNAL_TEMP_SENSOR1: _read_flag(
                    data.registers[94], 1
                ),
                SwitchAttrKey.CON_USE_EXTERNAL_TEMP_SENSOR2: _read_flag(
                    data.registers[94], 2
                ),
                SwitchAttrKey.CON_USE_EXTERNAL_TEMP_SENSOR3: _read_flag(
                    data.registers[94], 3
                ),
                SwitchAttrKey.CON_USE_EXTERNAL_TEMP_SENSOR4: _read_flag(
                    data.registers[94], 4
                ),
            },
            time_inputs={
                TimeAttrKey.CON_LEGIO_PROTECTION_PREFERRED_START_TIME: _read_time(
                    data.registers[12:16]
                ),
                TimeAttrKey.CON_LOW_TARIFF_START_TIME: time(
                    hour=_read_byte(data.registers[52]),
                    minute=_read_byte(data.registers[53]),
                ),
                TimeAttrKey.CON_LOW_TARIFF_END_TIME: time(
                    hour=_read_byte(data.registers[54]),
                    minute=_read_byte(data.registers[55]),
                ),
            },
            text_intputs={
                TextAttrKey.CON_WATER_HARDNESS: _read_str(data.registers[16:20]),
                TextAttrKey.CON_INFO_STRING: _read_str(data.registers[22:38]),
            },
            select_inputs={
                SelectAttrKey.CON_RTU_BAUDRATE: Baurate(
                    _read_str(data.registers[46:49])
                ),
                SelectAttrKey.CON_ENERGY_METER_TYPE: EnergyMeterType(
                    _read_byte(data.registers[51])
                ),
            },
        )

    def _map_register_to_status(
        self, register_value: int
    ) -> dict[BinarySensorAttrKey, bool]:
        """Map modbus register status."""
        return {
            # low byte values
            BinarySensorAttrKey.HEATER1_ACTIVE: _read_flag(register_value, 0),
            BinarySensorAttrKey.HEATER2_ACTIVE: _read_flag(register_value, 1),
            BinarySensorAttrKey.HEATER3_ACTIVE: _read_flag(register_value, 2),
            BinarySensorAttrKey.PUMP_ACTIVE: _read_flag(register_value, 3),
            BinarySensorAttrKey.RELAY_BOARD_CONNECTED: _read_flag(register_value, 4),
            # bit 5 ignored
            BinarySensorAttrKey.HEAT_PUMP_REQUEST_ACTIVE: _read_flag(register_value, 6),
            BinarySensorAttrKey.EMERGENCY_MODE_ACTIVE: _read_flag(register_value, 7),
            # high byte values
            BinarySensorAttrKey.LEGIONELLA_PROTECTION_ACTIVE: _read_flag(
                register_value, 8
            ),
            BinarySensorAttrKey.ANALOG_INPUT_ACTIVE: _read_flag(register_value, 9),
            BinarySensorAttrKey.SETPOINT_ACTIVE: _read_flag(register_value, 10),
            BinarySensorAttrKey.LOAD_FEEDIN_ACTIVE: _read_flag(register_value, 11),
            BinarySensorAttrKey.AUTOHEATER_ACTIVE: _read_flag(register_value, 12),
            BinarySensorAttrKey.PUMP_RELAY_FOLLOW_UP_TIME_ACTIVE: _read_flag(
                register_value, 13
            ),
            BinarySensorAttrKey.TEMP_LIMIT_REACHED: _read_flag(register_value, 14),
            BinarySensorAttrKey.ERROR_OCCURED: _read_flag(register_value, 15),
        }

    def _map_register_to_heater_step(
        self, register_value: int
    ) -> dict[SwitchAttrKey, bool]:
        """Map modbus register to status class."""
        return {
            SwitchAttrKey.EMA_SET_HEATER_STEP_HEATER1: _read_flag(register_value, 0),
            SwitchAttrKey.EMA_SET_HEATER_STEP_HEATER2: _read_flag(register_value, 1),
            SwitchAttrKey.EMA_SET_HEATER_STEP_HEATER3: _read_flag(register_value, 2),
        }


def _read_time(register_values: list[int]) -> time | None:
    """Read register values as string and parse as time."""
    time_string = _read_str(register_values)
    try:
        return datetime.strptime(time_string, "%H:%M %p").time  # type: ignore  # noqa: DTZ007, PGH003
    except Exception as err:  # noqa: BLE001
        LOGGER.warning("Could not read time from string %s, %s", time_string, err)


def _read_str(register_values: list[int]) -> str:
    """Read register values as str."""
    return str(
        ModbusClient.convert_from_registers(
            register_values, ModbusClient.DATATYPE.STRING
        )
    )


def _read_byte(register_value: int) -> np.byte:
    """Read register value as byte."""
    return np.byte(
        ModbusClient.convert_from_registers(
            [register_value], ModbusClient.DATATYPE.INT16
        )
    )


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
