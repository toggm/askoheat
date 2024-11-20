"""Modbus API Client."""

from __future__ import annotations

from datetime import time
from enum import ReprEnum
from typing import TYPE_CHECKING, Any, TypeVar, cast

import numpy as np
from numpy import number
from pymodbus.client import AsyncModbusTcpClient as ModbusClient

from custom_components.askoheat.api_conf_desc import CONF_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_desc import (
    ByteRegisterInputDescriptor,
    FlagRegisterInputDescriptor,
    Float32RegisterInputDescriptor,
    IntEnumInputDescriptor,
    RegisterBlockDescriptor,
    RegisterInputDescriptor,
    SignedIntRegisterInputDescriptor,
    StrEnumInputDescriptor,
    StringRegisterInputDescriptor,
    TimeRegisterInputDescriptor,
    UnsignedIntRegisterInputDescriptor,
)
from custom_components.askoheat.api_ema_desc import EMA_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_par_desc import PARAMETER_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.const import (
    LOGGER,
)
from custom_components.askoheat.data import AskoheatDataBlock

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

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

    async def async_read_par_data(self) -> AskoheatDataBlock:
        """Read PAR states."""
        data = await self.__async_read_input_registers_data(
            PARAMETER_REGISTER_BLOCK_DESCRIPTOR.starting_register,
            PARAMETER_REGISTER_BLOCK_DESCRIPTOR.number_of_registers,
        )
        LOGGER.debug("async_read_par_data %s", data)
        return self.__map_data(PARAMETER_REGISTER_BLOCK_DESCRIPTOR, data)

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
            "async write config parameter at %i, value=%r",
            api_desc.starting_register,
            value,
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
            case FlagRegisterInputDescriptor(_, bit):
                # first re-read value as this register might have changed
                current_value = await read_current_register_value()
                result = _prepare_flag(
                    register_value=current_value, flag=value, index=bit
                )
            case ByteRegisterInputDescriptor():
                result = _prepare_byte(value)
            case UnsignedIntRegisterInputDescriptor():
                result = _prepare_uint16(value)
            case SignedIntRegisterInputDescriptor():
                result = _prepare_int16(value)
            case Float32RegisterInputDescriptor():
                result = _prepare_float32(value)
            case StringRegisterInputDescriptor():
                result = _prepare_str(value)
            case TimeRegisterInputDescriptor(value):
                result = _prepare_time(value)
            case StrEnumInputDescriptor():
                result = _prepare_str(value.value)  # type: ignore  # noqa: PGH003
            case IntEnumInputDescriptor():
                result = _prepare_byte(value.value)  # type: ignore  # noqa: PGH003
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
        text_inputs = {
            k: v
            for k, v in {
                item.key: _read_register_string_input(data, item.api_descriptor)  # type: ignore  # noqa: PGH003
                for item in descr.text_inputs
            }.items()
            if v is not None
        }
        time_inputs = {
            k: v
            for k, v in {
                item.key: _read_register_time_input(data, item.api_descriptor)  # type: ignore  # noqa: PGH003
                for item in descr.time_inputs
            }.items()
            if v is not None
        }
        select_inputs = {
            k: v
            for k, v in {
                item.key: _read_register_enum_input(data, item.api_descriptor)  # type: ignore  # noqa: PGH003
                for item in descr.select_inputs
            }.items()
            if v is not None
        }
        return AskoheatDataBlock(
            binary_sensors=binary_sensors,
            sensors=sensors,
            switches=switches,
            number_inputs=number_inputs,
            text_inputs=text_inputs,
            time_inputs=time_inputs,
            select_inputs=select_inputs,
        )


def _read_register_input(data: ModbusPDU, desc: RegisterInputDescriptor) -> object:
    match desc:
        case FlagRegisterInputDescriptor(starting_register, bit):
            result = _read_flag(data.registers[starting_register], bit)
        case IntEnumInputDescriptor(starting_register, factory):
            result = factory(_read_byte(data.registers[starting_register]))
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
        case StrEnumInputDescriptor(starting_register, number_of_words, factory):
            result = factory(
                _read_str(
                    data.registers[
                        starting_register : starting_register + number_of_words
                    ]
                )
            )
        case StringRegisterInputDescriptor(starting_register, number_of_words):
            result = _read_str(
                data.registers[starting_register : starting_register + number_of_words]
            )
        case TimeRegisterInputDescriptor(starting_register):
            result = _read_time(
                register_value_hours=data.registers[starting_register],
                register_value_minutes=data.registers[starting_register + 1],
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


def _read_register_string_input(
    data: ModbusPDU, desc: RegisterInputDescriptor
) -> str | None:
    result = _read_register_input(data, desc)
    if isinstance(result, str):
        return result

    LOGGER.error(
        "Cannot read str input from descriptor %r, unsupported value %r",
        desc,
        result,
    )
    return None


def _read_register_time_input(
    data: ModbusPDU, desc: RegisterInputDescriptor
) -> time | None:
    result = _read_register_input(data, desc)
    if isinstance(result, time):
        return result

    LOGGER.error(
        "Cannot read time input from descriptor %r, unsupported value %r",
        desc,
        result,
    )
    return None


def _read_register_enum_input(
    data: ModbusPDU, desc: RegisterInputDescriptor
) -> ReprEnum | None:
    result = _read_register_input(data, desc)
    if isinstance(result, ReprEnum):
        return result

    LOGGER.error(
        "Cannot read enum input from descriptor %r, unsupported value %r",
        desc,
        result,
    )
    return None


def _read_time(register_value_hours: int, register_value_minutes: int) -> time | None:
    """Read register values as string and parse as time."""
    hours = _read_uint16(register_value_hours)
    minutes = _read_uint16(register_value_minutes)
    return time(hour=hours, minute=minutes)


def _prepare_time(value: object) -> list[int]:
    """Prepare time represented as two register values for writing to registers."""
    if not isinstance(value, time):
        LOGGER.error(
            "Cannot convert value %s as time, wrong datatype %r", value, type(value)
        )
        return []
    time_value = cast(time, value)
    return _prepare_uint16(time_value.hour).__add__(_prepare_uint16(time_value.minute))


T = TypeVar("T")


def _read_str(register_values: list[int]) -> str:
    """Read register values as str."""
    # custom implementation as strings are represented with little endian
    byte_list = bytearray()
    for x in register_values:
        byte_list.extend(int.to_bytes(x, 2, "little"))
    if byte_list[-1:] == b"\00":
        byte_list = byte_list[:-1]
    return byte_list.decode("utf-8")


def _prepare_str(value: object) -> list[int]:
    """Prepare string value for writing to registers."""
    if not isinstance(value, str):
        LOGGER.error(
            "Cannot convert value %s as string, wrong datatype %r", value, type(value)
        )
        return []
    str_value = cast(str, value)
    byte_list = str_value.encode("utf-8")
    size = int(len(byte_list) / 2)
    result = []
    for index in range(size):
        b = byte_list[index * 2 : index * 2 + 1]
        result.append(int.from_bytes(b, "little"))
    return result


def _read_byte(register_value: int) -> np.byte:
    """Read register value as byte."""
    return np.byte(
        ModbusClient.convert_from_registers(
            [register_value], ModbusClient.DATATYPE.INT16
        )
    )


def _prepare_byte(value: object) -> list[int]:
    """Prepare byte value for writing to registers."""
    if not isinstance(value, number | float | bool):
        LOGGER.error(
            "Cannot convert value %s as byte, wrong datatype %r", value, type(value)
        )
        return []

    # special case, map true to 1 and false to 0
    if isinstance(value, bool):
        value = 1 if value else 0

    return ModbusClient.convert_to_registers(int(value), ModbusClient.DATATYPE.INT16)


def _read_int16(register_value: int) -> np.int16:
    """Read register value as int16."""
    return np.int16(
        ModbusClient.convert_from_registers(
            [register_value], ModbusClient.DATATYPE.INT16
        )
    )


def _prepare_int16(value: object) -> list[int]:
    """Prepare signed int value for writing to registers."""
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
    """Prepare unsigned int value for writing to registers."""
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
    """Prepare float32 value writing to registers."""
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
    """Prepare flag value as mask with current value for writing to a register."""
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
