"""Modbus API Client."""

from __future__ import annotations

from datetime import time
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Coroutine, TypeVar, cast

import numpy as np
from numpy import number
from pymodbus.client import AsyncModbusTcpClient as ModbusClient

from custom_components.askoheat.api_conf_desc import CONF_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_desc import (
    ByteRegisterInputDescriptor,
    FlagRegisterInputDescriptor,
    Float32RegisterInputDescriptor,
    RegisterBlockDescriptor,
    RegisterInputDescriptor,
    SignedIntRegisterInputDescriptor,
    StringRegisterInputDescriptor,
    UnsignedIntRegisterInputDescriptor,
)
from custom_components.askoheat.api_ema_desc import EMA_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.const import (
    LOGGER,
    Baurate,
    BinarySensorAttrKey,
    EnergyMeterType,
    SelectAttrKey,
    SwitchAttrKey,
    TextAttrKey,
    TimeAttrKey,
)
from custom_components.askoheat.data import AskoheatDataBlock

if TYPE_CHECKING:
    from collections.abc import Callable

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
        data = await self.__async_read_input_registers_data(
            EMA_REGISTER_BLOCK_DESCRIPTOR.starting_register,
            EMA_REGISTER_BLOCK_DESCRIPTOR.number_of_registers,
        )
        LOGGER.debug("async_read_ema_data %s", data)
        return self.__map_data(EMA_REGISTER_BLOCK_DESCRIPTOR, data)

    async def async_write_ema_data(
        self, api_desc: RegisterInputDescriptor, value: object
    ) -> AskoheatDataBlock:
        """Write EMA parameter."""
        LOGGER.debug(
            f"async write ema parameter at {api_desc.starting_register}, value={value}"
        )
        register_values = await self._prepare_register_value(
            api_desc,
            value,
            lambda: self.__async_read_single_input_register(
                EMA_REGISTER_BLOCK_DESCRIPTOR.absolute_register_index(api_desc)
            ),
        )
        if len(register_values) > 0:
            await self.__async_write_register_values(
                EMA_REGISTER_BLOCK_DESCRIPTOR.absolute_register_index(api_desc),
                register_values,
            )
        return await self.async_read_ema_data()

    async def async_read_config_data(self) -> AskoheatDataBlock:
        """Read EMA states."""
        data = await self.__async_read_holding_registers_data(
            CONF_REGISTER_BLOCK_DESCRIPTOR.starting_register,
            CONF_REGISTER_BLOCK_DESCRIPTOR.number_of_registers,
        )
        LOGGER.debug("async_read_config_data %s", data)
        return self.__map_data(CONF_REGISTER_BLOCK_DESCRIPTOR, data)

    async def async_write_config_data(
        self, api_desc: RegisterInputDescriptor, value: object
    ) -> AskoheatDataBlock:
        """Write EMA parameter."""
        LOGGER.debug(
            f"async write config parameter at {api_desc.starting_register}, value={value}"
        )
        register_values = await self._prepare_register_value(
            api_desc,
            value,
            lambda: self.__async_read_single_holding_register(
                CONF_REGISTER_BLOCK_DESCRIPTOR.absolute_register_index(api_desc)
            ),
        )
        if len(register_values) > 0:
            await self.__async_write_register_values(
                CONF_REGISTER_BLOCK_DESCRIPTOR.absolute_register_index(api_desc),
                register_values,
            )
        return await self.async_read_config_data()

    async def __async_read_single_input_register(
        self,
        address: int,
    ) -> int:
        return (await self.__async_read_input_registers_data(address, 1)).registers[0]

    async def __async_read_input_registers_data(
        self, address: int, count: int
    ) -> ModbusPDU:
        """Read holding registers through modbus."""
        if not self._client.connected:
            msg = "cannot read holding registers, not connected"
            raise AskoheatModbusApiClientCommunicationError(msg)

        return await self._client.read_input_registers(address=address, count=count)

    async def __async_read_single_holding_register(
        self,
        address: int,
    ) -> int:
        return (await self.__async_read_holding_registers_data(address, 1)).registers[0]

    async def __async_read_holding_registers_data(
        self, address: int, count: int
    ) -> ModbusPDU:
        """Read input registers through modbus."""
        if not self._client.connected:
            msg = "cannot read input registers, not connected"
            raise AskoheatModbusApiClientCommunicationError(msg)

        return await self._client.read_holding_registers(address=address, count=count)

    async def __async_write_register_values(
        self, address: int, values: list[bytes | int]
    ) -> ModbusPDU:
        """Write a register value throug modbus."""
        if not self._client.connected:
            msg = "cannot write register value, not connected"
            raise AskoheatModbusApiClientCommunicationError(msg)

        return await self._client.write_registers(address=address, values=values)

    async def _prepare_register_value(
        self,
        desc: RegisterInputDescriptor,
        value: object,
        read_current_register_value: Callable[..., Coroutine[Any, Any, int]],
    ) -> list[int | bytes]:
        match desc:
            case FlagRegisterInputDescriptor(starting_register, bit):
                # first re-read value as this register might have changed
                current_value = await read_current_register_value()
                result = _prepare_flag(
                    register_value=current_value, flag=value, index=bit
                )
            case ByteRegisterInputDescriptor(starting_register):
                result = _prepare_byte(value)
            case UnsignedIntRegisterInputDescriptor(starting_register):
                result = _prepare_uint16(value)
            case SignedIntRegisterInputDescriptor(starting_register):
                result = _prepare_int16(value)
            case Float32RegisterInputDescriptor(starting_register):
                result = _prepare_float32(value)
            case StringRegisterInputDescriptor(starting_register, number_of_bytes):
                # TODO Support
                # result = _read_str(
                #    data.registers[
                #        starting_register : starting_register + number_of_bytes + 1
                #    ]
                # )
                result = []
            case _:
                LOGGER.error("Cannot read number input from descriptor %r", desc)
                result = []
        return cast(list[int | bytes], result)

    def __map_data(
        self, descr: RegisterBlockDescriptor, data: ModbusPDU
    ) -> AskoheatDataBlock:
        binary_sensors = {
            k: v
            for k, v in {
                item.key: _read_register_boolean_input(data, item.api_descriptor)  # type: ignore  # noqa: PGH003
                for item in descr.binary_sensors
            }.items()
            if v is not None
        }
        number_inputs = {
            k: v
            for k, v in {
                item.key: _read_register_number_input(data, item.api_descriptor)  # type: ignore  # noqa: PGH003
                for item in descr.number_inputs
            }.items()
            if v is not None
        }
        sensors = {
            k: v
            for k, v in {
                item.key: _read_register_input(data, item.api_descriptor)  # type: ignore  # noqa: PGH003
                for item in descr.sensors
            }.items()
            if v is not None
        }
        switches = {
            k: v
            for k, v in {
                item.key: _read_register_boolean_input(data, item.api_descriptor)  # type: ignore  # noqa: PGH003
                for item in descr.switches
            }.items()
            if v is not None
        }
        return AskoheatDataBlock(
            binary_sensors=binary_sensors,
            sensors=sensors,
            switches=switches,
            number_inputs=number_inputs,
        )

    def __map_config_data(self, data: ModbusPDU) -> AskoheatDataBlock:
        """Map modbus result of config data block."""
        return AskoheatDataBlock(
            number_inputs={},
            switches={},
            # TODO: Move/merge to api_conf_desc.py
            time_inputs={
                TimeAttrKey.CON_LEGIO_PROTECTION_PREFERRED_START_TIME: _read_time(
                    register_value_hours=data.registers[12],
                    register_value_minutes=data.registers[13],
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
            # TODO: Move/merge to api_conf_desc.py
            text_inputs={
                TextAttrKey.CON_INFO_STRING: _read_str(data.registers[22:38]),
            },
            # TODO: Move/merge to api_conf_desc.py
            select_inputs={
                SelectAttrKey.CON_RTU_BAUDRATE: _read_enum(
                    data.registers[46:49], Baurate
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


def _read_register_input(data: ModbusPDU, desc: RegisterInputDescriptor) -> object:
    match desc:
        case FlagRegisterInputDescriptor(starting_register, bit):
            result = _read_flag(data.registers[starting_register], bit)
        case ByteRegisterInputDescriptor(starting_register):
            result = _read_byte(data.registers[starting_register])
        case UnsignedIntRegisterInputDescriptor(starting_register):
            result = _read_uint16(data.registers[starting_register])
        case SignedIntRegisterInputDescriptor(starting_register):
            result = _read_int16(data.registers[starting_register])
        case Float32RegisterInputDescriptor(starting_register):
            result = _read_float32(
                data.registers[starting_register : starting_register + 2]
            )
        case StringRegisterInputDescriptor(starting_register, number_of_bytes):
            result = _read_str(
                data.registers[
                    starting_register : starting_register + number_of_bytes + 1
                ]
            )
        case _:
            LOGGER.error("Cannot read number input from descriptor %r", desc)
            result = None
    return result


def _read_register_boolean_input(
    data: ModbusPDU, desc: RegisterInputDescriptor
) -> bool | None:
    result = _read_register_input(data, desc)
    if isinstance(result, bool):
        return result

    if isinstance(result, number):
        return result == 1

    LOGGER.error(
        "Cannot read bool input from descriptor %r, unsupported value %r",
        desc,
        result,
    )
    return None


def _read_register_number_input(
    data: ModbusPDU, desc: RegisterInputDescriptor
) -> number | None:
    result = _read_register_input(data, desc)
    if isinstance(result, number):
        return result

    LOGGER.error(
        "Cannot read number input from descriptor %r, unsupported value %r",
        desc,
        result,
    )
    return None


def _read_time(register_value_hours: int, register_value_minutes: int) -> time | None:
    """Read register values as string and parse as time."""
    hours = _read_uint16(register_value_hours)
    minutes = _read_uint16(register_value_minutes)
    return time(hour=hours, minute=minutes)


T = TypeVar("T")


def _read_enum(register_values: list[int], factory: Callable[[str], T]) -> T:
    """Read register values as enum."""
    str_value = _read_str(register_values)
    return factory(str_value)


def _read_str(register_values: list[int]) -> str:
    """Read register values as str."""
    # custom implementation as strings a represented with little endian
    byte_list = bytearray()
    for x in register_values:
        byte_list.extend(int.to_bytes(x, 2, "little"))
    if byte_list[-1:] == b"\00":
        byte_list = byte_list[:-1]
    return byte_list.decode("utf-8")


def _read_byte(register_value: int) -> np.byte:
    """Read register value as byte."""
    return np.byte(
        ModbusClient.convert_from_registers(
            [register_value], ModbusClient.DATATYPE.INT16
        )
    )


def _prepare_byte(value: object) -> list[int]:
    """Prepare byte value to be able to write to a register."""
    if not isinstance(value, number | float):
        LOGGER.error(
            "Cannot convert value %s as byte, wrong datatype %r", value, type(value)
        )
        return []

    return ModbusClient.convert_to_registers(int(value), ModbusClient.DATATYPE.INT16)


def _read_int16(register_value: int) -> np.int16:
    """Read register value as int16."""
    return np.int16(
        ModbusClient.convert_from_registers(
            [register_value], ModbusClient.DATATYPE.INT16
        )
    )


def _prepare_int16(value: object) -> list[int]:
    """Prepare signed int value to be able to write to a register."""
    if not isinstance(value, number | float):
        LOGGER.error(
            "Cannot convert value %s as signed int, wrong datatype %r",
            value,
            type(value),
        )
        return []
    return ModbusClient.convert_to_registers(int(value), ModbusClient.DATATYPE.INT16)


def _read_uint16(register_value: int) -> np.uint16:
    """Read register value as uint16."""
    return np.uint16(
        ModbusClient.convert_from_registers(
            [register_value], ModbusClient.DATATYPE.UINT16
        )
    )


def _prepare_uint16(value: object) -> list[int]:
    """Prepare unsigned int value to be able to write to a register."""
    if not isinstance(value, number | float):
        LOGGER.error(
            "Cannot convert value %s as unsigned int, wrong datatype %r",
            value,
            type(value),
        )
        return []

    return ModbusClient.convert_to_registers(int(value), ModbusClient.DATATYPE.UINT16)


def _read_float32(register_values: list[int]) -> np.float32:
    """Read register value as uint16."""
    return np.float32(
        ModbusClient.convert_from_registers(
            register_values, ModbusClient.DATATYPE.FLOAT32
        )
    )


def _prepare_float32(value: object) -> list[int]:
    """Prepare float32 value to be able to write to a register."""
    if not isinstance(value, number | float):
        LOGGER.error(
            "Cannot convert value %s as float32, wrong datatype %r", value, type(value)
        )
        return []
    return ModbusClient.convert_to_registers(
        float(value), ModbusClient.DATATYPE.FLOAT32
    )


def _read_flag(register_value: int, index: int) -> bool:
    """Validate if bit at provided index is set."""
    return (register_value >> index) & 0x01 == 0x01


def _prepare_flag(register_value: int, flag: object, index: int) -> list[int]:
    """Prepare flag value to be able to write to a register, mask with current value."""
    if not isinstance(flag, bool):
        LOGGER.error(
            "Cannot convert value %s as flag, wrong datatype %r",
            flag,
            type(flag),
        )
        return []

    if flag:
        # or mask to set the value to true
        return [(flag << index) | register_value]

    # minus flag from current registers value
    return [register_value - (True << index)]
