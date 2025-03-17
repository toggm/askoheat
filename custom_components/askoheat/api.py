"""Modbus API Client."""

from __future__ import annotations

import struct
from datetime import time
from enum import ReprEnum
from typing import (
    TYPE_CHECKING,
    Any,
    SupportsFloat,
    SupportsInt,
    cast,
)

from homeassistant.exceptions import HomeAssistantError
from numpy import number
from pymodbus.client import AsyncModbusTcpClient

from custom_components.askoheat.api_conf_desc import CONF_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_desc import (
    ByteRegisterInputDescriptor,
    FlagRegisterInputDescriptor,
    Float32RegisterInputDescriptor,
    IntEnumInputDescriptor,
    RegisterBlockDescriptor,
    RegisterInputDescriptor,
    SignedInt16RegisterInputDescriptor,
    StrEnumInputDescriptor,
    StringRegisterInputDescriptor,
    StructRegisterInputDescriptor,
    TimeRegisterInputDescriptor,
    UnsignedInt16RegisterInputDescriptor,
    UnsignedInt32RegisterInputDescriptor,
)
from custom_components.askoheat.api_ema_desc import EMA_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_op_desc import DATA_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_par_desc import PARAM_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.const import DOMAIN, LOGGER
from custom_components.askoheat.data import AskoheatDataBlock

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

    from pymodbus.pdu import ModbusPDU


class AskoheatModbusApiClientError(HomeAssistantError):
    """Exception to indicate a general API error."""


class AskoheatModbusApiClientCommunicationError(
    AskoheatModbusApiClientError,
):
    """Exception to indicate a communication error."""


class AskoheatModbusApiClient:
    """Sample API Client."""

    def __init__(self, host: str, port: int) -> None:
        """Askoheat Modbus API Client."""
        self._host = host
        self._port = port
        self._client = self._create_client(host=host, port=port)
        self._last_communication_success = True

    def _create_client(self, host: str, port: int) -> AsyncModbusTcpClient:
        return AsyncModbusTcpClient(host=host, port=port)

    async def connect(self) -> Any:
        """Connect to modbus client."""
        return await self._client.connect()

    @property
    def is_connected(self) -> bool:
        """Return connection status."""
        return self._client.connected

    @property
    def is_ready(self) -> bool:
        """Return true if connected and no communication error occurred."""
        return self.is_connected and self._last_communication_success

    def last_communication_failed(self) -> None:
        """Mark last communication with the API as failed."""
        self._last_communication_success = False

    def close(self) -> None:
        """Close comnection to modbus client."""
        self._client.close()

    async def async_read_ema_data(self) -> AskoheatDataBlock:
        """Read EMA states."""
        data = await self.__async_read_input_registers_data(
            EMA_REGISTER_BLOCK_DESCRIPTOR.starting_register,
            EMA_REGISTER_BLOCK_DESCRIPTOR.number_of_registers,
        )
        if len(data.registers) != EMA_REGISTER_BLOCK_DESCRIPTOR.number_of_registers:
            msg = "Unexpected number of registers read."
            LOGGER.error(
                "%s: number of registers=%s, expected=%s",
                msg,
                len(data.registers),
                EMA_REGISTER_BLOCK_DESCRIPTOR.number_of_registers,
            )
            raise AskoheatModbusApiClientCommunicationError(
                translation_domain=DOMAIN, translation_key=msg
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
            PARAM_REGISTER_BLOCK_DESCRIPTOR.starting_register,
            PARAM_REGISTER_BLOCK_DESCRIPTOR.number_of_registers,
        )
        if len(data.registers) != PARAM_REGISTER_BLOCK_DESCRIPTOR.number_of_registers:
            msg = "Unexpected number of registers read."
            LOGGER.error(
                "%s: number of registers=%s, expected=%s",
                msg,
                len(data.registers),
                PARAM_REGISTER_BLOCK_DESCRIPTOR.number_of_registers,
            )
            raise AskoheatModbusApiClientCommunicationError(
                translation_domain=DOMAIN, translation_key=msg
            )
        LOGGER.debug("async_read_par_data %s", data)
        return self.__map_data(PARAM_REGISTER_BLOCK_DESCRIPTOR, data)

    async def async_read_config_data(self) -> AskoheatDataBlock:
        """Read config states."""
        data = await self.__async_read_holding_registers_data(
            CONF_REGISTER_BLOCK_DESCRIPTOR.starting_register,
            CONF_REGISTER_BLOCK_DESCRIPTOR.number_of_registers,
        )
        if len(data.registers) != CONF_REGISTER_BLOCK_DESCRIPTOR.number_of_registers:
            msg = "Unexpected number of registers read."
            LOGGER.error(
                "%s: number of registers=%s, expected=%s",
                msg,
                len(data.registers),
                CONF_REGISTER_BLOCK_DESCRIPTOR.number_of_registers,
            )
            raise AskoheatModbusApiClientCommunicationError(
                translation_domain=DOMAIN, translation_key=msg
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

    async def async_read_op_data(self) -> AskoheatDataBlock:
        """Read OP data states."""
        data = await self.__async_read_input_registers_data(
            DATA_REGISTER_BLOCK_DESCRIPTOR.starting_register,
            DATA_REGISTER_BLOCK_DESCRIPTOR.number_of_registers,
        )
        if len(data.registers) != DATA_REGISTER_BLOCK_DESCRIPTOR.number_of_registers:
            msg = "Unexpected number of registers read."
            raise AskoheatModbusApiClientCommunicationError(
                translation_domain=DOMAIN, translation_key=msg
            )
        LOGGER.debug("async_read_op_data %s", data)
        return self.__map_data(DATA_REGISTER_BLOCK_DESCRIPTOR, data)

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
            msg = "not_connected"
            raise AskoheatModbusApiClientCommunicationError(
                translation_domain=DOMAIN, translation_key=msg
            )

        try:
            return await self._client.read_input_registers(address=address, count=count)
        finally:
            self._last_communication_success = True

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
            msg = "not_connected"
            raise AskoheatModbusApiClientCommunicationError(
                translation_domain=DOMAIN, translation_key=msg
            )

        try:
            return await self._client.read_holding_registers(
                address=address, count=count
            )
        finally:
            self._last_communication_success = True

    async def __async_write_register_values(
        self, address: int, values: list[int]
    ) -> None:
        """Write a register value through modbus."""
        if not self._client.connected:
            msg = "not_connected"
            raise AskoheatModbusApiClientCommunicationError(
                translation_domain=DOMAIN, translation_key=msg
            )

        try:
            await self._client.write_registers(address=address, values=values)
        finally:
            self._last_communication_success = True

    async def _prepare_register_value(
        self,
        desc: RegisterInputDescriptor,
        value: object,
        read_current_register_value: Callable[..., Coroutine[Any, Any, int]],
    ) -> list[int]:
        match desc:
            case FlagRegisterInputDescriptor(_, bit):
                # first re-read value as this register might have changed
                current_value = await read_current_register_value()
                result = _prepare_flag(
                    register_value=current_value, flag=value, index=bit
                )
            case ByteRegisterInputDescriptor():
                result = _prepare_byte(value)
            case UnsignedInt16RegisterInputDescriptor():
                result = _prepare_uint16(value)
            case UnsignedInt32RegisterInputDescriptor():
                result = _prepare_uint32(value)
            case SignedInt16RegisterInputDescriptor():
                result = _prepare_int16(value)
            case Float32RegisterInputDescriptor():
                result = _prepare_float32(value)
            case StringRegisterInputDescriptor():
                result = _prepare_str(value)
            case TimeRegisterInputDescriptor():
                result = _prepare_time(value)
            case StrEnumInputDescriptor():
                result = _prepare_str(value.value)  # type: ignore  # noqa: PGH003
            case IntEnumInputDescriptor():
                result = _prepare_byte(value.value)  # type: ignore  # noqa: PGH003
            case StructRegisterInputDescriptor(_, _, structure):
                result = _prepare_struct(value, structure)
            case _:
                LOGGER.error("Cannot read number input from descriptor %r", desc)
                result = []
        return cast("list[int]", result)

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
        select_inputs = dict(
            {
                item.key: _read_register_enum_input(data, item.api_descriptor)  # type: ignore  # noqa: PGH003
                for item in descr.select_inputs
            }.items()
        )
        return AskoheatDataBlock(
            binary_sensors=binary_sensors,
            sensors=sensors,
            switches=switches,
            number_inputs=number_inputs,
            text_inputs=text_inputs,
            time_inputs=time_inputs,
            select_inputs=select_inputs,
        )


def _read_register_input(  # noqa: PLR0912
    data: ModbusPDU, desc: RegisterInputDescriptor
) -> Any:
    result: Any = None
    match desc:
        case FlagRegisterInputDescriptor(starting_register, bit):
            result = _read_flag(data.registers[starting_register], bit)
        case IntEnumInputDescriptor(starting_register, factory):
            try:
                value = _read_byte(data.registers[starting_register])
                result = None if value is None else factory(int(value))
            except ValueError as err:
                LOGGER.warning(err)
                result = None
        case ByteRegisterInputDescriptor(starting_register):
            result = _read_byte(data.registers[starting_register])
        case UnsignedInt16RegisterInputDescriptor(starting_register):
            result = _read_uint16(data.registers[starting_register])
        case UnsignedInt32RegisterInputDescriptor(starting_register):
            result = _read_uint32(
                data.registers[starting_register : starting_register + 2]
            )
        case UnsignedInt32RegisterInputDescriptor(starting_register):
            result = _read_uint32(
                data.registers[starting_register : starting_register + 2]
            )
        case SignedInt16RegisterInputDescriptor(starting_register):
            result = _read_int16(data.registers[starting_register])
        case Float32RegisterInputDescriptor(starting_register):
            result = _read_float32(
                data.registers[starting_register : starting_register + 2]
            )
        case StrEnumInputDescriptor(starting_register, number_of_words, factory):
            try:
                result = factory(
                    _read_str(
                        data.registers[
                            starting_register : starting_register + number_of_words
                        ]
                    )
                )
            except ValueError as err:
                LOGGER.warning(err)
                result = None

        case StringRegisterInputDescriptor(starting_register, number_of_words):
            result = _read_str(
                data.registers[starting_register : starting_register + number_of_words]
            )
        case TimeRegisterInputDescriptor(starting_register):
            result = _read_time(
                register_value_hours=data.registers[starting_register],
                register_value_minutes=data.registers[starting_register + 1],
            )
        case StructRegisterInputDescriptor(starting_register, bytes, structure):
            result = _read_struct(
                data.registers[starting_register : starting_register + bytes], structure
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

    if isinstance(result, int):
        return bool(result == 1)

    if result is not None:
        LOGGER.error(
            "Cannot read bool input from descriptor %r, unsupported value %r",
            desc,
            result,
        )
    return None


def _read_register_number_input(
    data: ModbusPDU, desc: RegisterInputDescriptor
) -> int | float | None:
    result = _read_register_input(data, desc)
    if isinstance(result, int | float):
        return result

    if result is not None:
        LOGGER.error(
            "Cannot read number input from descriptor %r, unsupported value %r",
            desc,
            type(result),
        )
    return None


def _read_register_string_input(
    data: ModbusPDU, desc: RegisterInputDescriptor
) -> str | None:
    result = _read_register_input(data, desc)
    if isinstance(result, str):
        return result

    if result is not None:
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

    if result is not None:
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

    if result is not None:
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
    if hours is not None and minutes is not None:
        return time(hour=hours, minute=minutes)
    return None


def _prepare_time(value: object) -> list[int]:
    """Prepare time represented as two register values for writing to registers."""
    if not isinstance(value, time):
        LOGGER.error(
            "Cannot convert value %s as time, wrong datatype %r", value, type(value)
        )
        return []
    time_value = value
    return _prepare_uint16(time_value.hour).__add__(_prepare_uint16(time_value.minute))


def _read_str(register_values: list[int]) -> str:
    """Read register values as str."""
    # custom implementation as strings are represented with little endian
    byte_list = bytearray()
    for x in register_values:
        byte_list.extend(int.to_bytes(x, 2, "little"))
    while byte_list[-1:] == b"\00":
        byte_list = byte_list[:-1]
    return byte_list.decode().strip(" ")


def _prepare_str(value: object) -> list[int]:
    """Prepare string value for writing to registers."""
    if not isinstance(value, str):
        LOGGER.error(
            "Cannot convert value %s as string, wrong datatype %r", value, type(value)
        )
        return []
    str_value = value
    byte_list = str_value.encode()
    size = float.__ceil__(len(byte_list) / 2)
    result = []
    for index in range(size):
        b = byte_list[index * 2 : index * 2 + 2]
        result.append(int.from_bytes(b, "little"))

    return result


def _read_byte(register_value: int) -> int | None:
    """Read register value as byte."""
    value = AsyncModbusTcpClient.convert_from_registers(
        [register_value], AsyncModbusTcpClient.DATATYPE.INT16
    )
    if not isinstance(value, SupportsInt):
        LOGGER.error(
            "Cannot read register value %s as byte, wrong result %r", value, type(value)
        )
        return None
    return int(value)


def _prepare_byte(value: object) -> list[int]:
    """Prepare byte value for writing to registers."""
    if not isinstance(value, number | float | bool | int):
        LOGGER.error(
            "Cannot convert value %s as byte, wrong datatype %r", value, type(value)
        )
        return []

    # special case, map true to 1 and false to 0
    if isinstance(value, bool):
        value = 1 if value else 0

    return AsyncModbusTcpClient.convert_to_registers(
        int(value), AsyncModbusTcpClient.DATATYPE.INT16
    )


def _read_int16(register_value: int) -> int | None:
    """Read register value as int16."""
    value = AsyncModbusTcpClient.convert_from_registers(
        [register_value], AsyncModbusTcpClient.DATATYPE.INT16
    )
    if not isinstance(value, SupportsInt):
        LOGGER.error(
            "Cannot read register value %s as int16, wrong result type %r",
            value,
            type(value),
        )
        return None

    return int(value)


def _prepare_int16(value: object) -> list[int]:
    """Prepare signed int value for writing to registers."""
    if not isinstance(value, number | float | int):
        LOGGER.error(
            "Cannot convert value %s as signed int, wrong datatype %r",
            value,
            type(value),
        )
        return []
    return AsyncModbusTcpClient.convert_to_registers(
        int(value), AsyncModbusTcpClient.DATATYPE.INT16
    )


def _read_uint16(register_value: int) -> int | None:
    """Read register value as uint16."""
    value = AsyncModbusTcpClient.convert_from_registers(
        [register_value], AsyncModbusTcpClient.DATATYPE.UINT16
    )
    if not isinstance(value, SupportsInt):
        LOGGER.error(
            "Cannot read register value %s as uint16, wrong result type %r",
            value,
            type(value),
        )
        return None

    return int(value)


def _prepare_uint16(value: object) -> list[int]:
    """Prepare unsigned int 16 value for writing to registers."""
    if not isinstance(value, number | float | int):
        LOGGER.error(
            "Cannot convert value %s as unsigned int, wrong datatype %r",
            value,
            type(value),
        )
        return []

    return AsyncModbusTcpClient.convert_to_registers(
        int(value), AsyncModbusTcpClient.DATATYPE.UINT16
    )


def _read_uint32(register_values: list[int]) -> int | None:
    """Read register value as uint32."""
    value = AsyncModbusTcpClient.convert_from_registers(
        register_values, AsyncModbusTcpClient.DATATYPE.UINT32
    )
    if not isinstance(value, SupportsInt):
        LOGGER.error(
            "Cannot read register value %s as uint32, wrong result type %r",
            value,
            type(value),
        )
        return None
    return int(value)


def _prepare_uint32(value: object) -> list[int]:
    """Prepare unsigned int 32 value for writing to registers."""
    if not isinstance(value, number | float | int):
        LOGGER.error(
            "Cannot convert value %s as unsigned int, wrong datatype %r",
            value,
            type(value),
        )
        return []

    return AsyncModbusTcpClient.convert_to_registers(
        int(value), AsyncModbusTcpClient.DATATYPE.UINT32
    )


def _read_float32(register_values: list[int]) -> float | None:
    """Read register value as uint16."""
    value = AsyncModbusTcpClient.convert_from_registers(
        register_values, AsyncModbusTcpClient.DATATYPE.FLOAT32
    )
    if not isinstance(value, SupportsFloat):
        LOGGER.error(
            "Cannot read register value %s as float32, wrong result type %r",
            value,
            type(value),
        )
        return None
    return float(value)


def _prepare_float32(value: object) -> list[int]:
    """Prepare float32 value writing to registers."""
    if not isinstance(value, number | float | int):
        LOGGER.error(
            "Cannot convert value %s as float32, wrong datatype %r", value, type(value)
        )
        return []
    return AsyncModbusTcpClient.convert_to_registers(
        float(value), AsyncModbusTcpClient.DATATYPE.FLOAT32
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

    # subtract flag from current registers value by inverting the value through XOR
    # with 0xFFFF and a binary and with the current value
    return [register_value & (0xFFFF ^ (True << index))]


def _read_struct(register_values: list[int], structure: str | bytes) -> Any | None:
    """Read register values and unpack using python struct."""
    byte_string = b"".join([x.to_bytes(2, byteorder="big") for x in register_values])
    if byte_string == b"nan\x00":
        return None

    try:
        val = struct.unpack(structure, byte_string)
    except struct.error as err:
        recv_size = len(register_values) * 2
        msg = f"Received {recv_size} bytes, unpack error {err}"
        LOGGER.error(msg)
        return None
    if len(val) == 1:
        return val[0]
    return val


def _prepare_struct(value: object, structure: str | bytes) -> list[int]:
    """Pack value based on python struct for writing to registers."""
    as_bytes = struct.pack(structure, value)
    return [
        int.from_bytes(as_bytes[i : i + 2], "big") for i in range(0, len(as_bytes), 2)
    ]
