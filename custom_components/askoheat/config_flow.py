"""Adds config flow for Blueprint."""

from __future__ import annotations

import re
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, cast

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import data_entry_flow
from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
    OptionsFlowWithConfigEntry,
)
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import selector
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.askoheat.coordinator import (
    AskoheatParameterDataUpdateCoordinator,
)
from custom_components.askoheat.data import AskoheatDeviceInfos

from .api import (
    AskoheatModbusApiClient,
    AskoheatModbusApiClientCommunicationError,
)
from .const import (
    CONF_ANALOG_INPUT_UNIT,
    CONF_DEVICE_UNITS,
    CONF_FEED_IN,
    CONF_HEATPUMP_UNIT,
    CONF_LEGIONELLA_PROTECTION_UNIT,
    CONF_MODBUS_MASTER_UNIT,
    CONF_POWER_ENTITY_ID,
    CONF_POWER_INVERT,
    CONFIG_ENTRY_VERSION,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DOMAIN,
    LOGGER,
    REPO_URL,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.service_info.dhcp import DhcpServiceInfo

    from .data import AskoheatConfigEntry

PORT_SELECTOR = vol.All(
    selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=1, step=1, max=65535, mode=selector.NumberSelectorMode.BOX
        )
    ),
    vol.Coerce(int),
)


def _get_section_entry_or_none(
    data: MappingProxyType[str, Any] | None, section: str, entry: str
) -> str | None:
    if data is None:
        return None
    section_values = data.get(section)
    if section_values is None:
        return None
    return cast("str | None", section_values.get(entry))


def _step_user_data_schema(
    data: MappingProxyType[str, Any] | None = None,
) -> vol.Schema:
    LOGGER.debug("_step_user_data_schema: %s", data)
    power_entity_default = _get_section_entry_or_none(
        data, CONF_FEED_IN, CONF_POWER_ENTITY_ID
    )

    power_entity_field = (
        vol.Optional(CONF_POWER_ENTITY_ID, default=power_entity_default)
        if power_entity_default is not None
        else vol.Optional(CONF_POWER_ENTITY_ID)
    )

    return vol.Schema(
        {
            vol.Required(
                CONF_HOST, default=data[CONF_HOST] if data else DEFAULT_HOST
            ): cv.string,
            vol.Required(
                CONF_PORT, default=data[CONF_PORT] if data else DEFAULT_PORT
            ): PORT_SELECTOR,
            vol.Required(CONF_FEED_IN): data_entry_flow.section(
                vol.Schema(
                    {
                        power_entity_field: selector.EntitySelector(
                            selector.EntitySelectorConfig(
                                filter=selector.EntityWithDeviceFilterSelectorConfig(
                                    domain=Platform.SENSOR,
                                    device_class=SensorDeviceClass.POWER,
                                ),
                                multiple=False,
                            )
                        ),
                        vol.Required(
                            CONF_POWER_INVERT,
                            default=(
                                False
                                if (
                                    x := _get_section_entry_or_none(
                                        data,
                                        CONF_FEED_IN,
                                        CONF_POWER_INVERT,
                                    )
                                )
                                is None
                                else x
                            ),
                        ): cv.boolean,
                    }
                ),
                {"collapsed": True},
            ),
            vol.Required(CONF_DEVICE_UNITS): data_entry_flow.section(
                vol.Schema(
                    {
                        vol.Required(
                            CONF_LEGIONELLA_PROTECTION_UNIT,
                            default=(
                                True
                                if (
                                    x := _get_section_entry_or_none(
                                        data,
                                        CONF_DEVICE_UNITS,
                                        CONF_LEGIONELLA_PROTECTION_UNIT,
                                    )
                                )
                                is None
                                else x
                            ),
                        ): bool,
                        vol.Required(
                            CONF_HEATPUMP_UNIT,
                            default=(
                                False
                                if (
                                    x := _get_section_entry_or_none(
                                        data,
                                        CONF_DEVICE_UNITS,
                                        CONF_HEATPUMP_UNIT,
                                    )
                                )
                                is None
                                else x
                            ),
                        ): cv.boolean,
                        vol.Required(
                            CONF_ANALOG_INPUT_UNIT,
                            default=(
                                False
                                if (
                                    x := _get_section_entry_or_none(
                                        data,
                                        CONF_DEVICE_UNITS,
                                        CONF_ANALOG_INPUT_UNIT,
                                    )
                                )
                                is None
                                else x
                            ),
                        ): cv.boolean,
                        vol.Required(
                            CONF_MODBUS_MASTER_UNIT,
                            default=(
                                False
                                if (
                                    x := _get_section_entry_or_none(
                                        data,
                                        CONF_DEVICE_UNITS,
                                        CONF_MODBUS_MASTER_UNIT,
                                    )
                                )
                                is None
                                else x
                            ),
                        ): cv.boolean,
                    }
                ),
                {"collapsed": False},
            ),
        }
    )


STEP_USER_DATA_SCHEMA = _step_user_data_schema()


def _normalize_serial(value: object) -> str:
    """Return a comparable form of a serial number or MAC address."""
    return re.sub(r"[^0-9a-z]", "", str(value or "").lower())


def _entry_serials(hass: HomeAssistant, entry: ConfigEntry) -> set[str]:
    """
    Return the normalized serial numbers a config entry is known under.

    The serial the entry was created with (its unique_id never changes) and the
    serial the device reports now (written to the device registry on every
    start). They differ if the device firmware changed the reported serial.
    """
    serials = {_normalize_serial((entry.unique_id or "").removeprefix(f"{DOMAIN}_"))}
    registry = dr.async_get(hass)
    serials.update(
        _normalize_serial(device.serial_number)
        for device in dr.async_entries_for_config_entry(registry, entry.entry_id)
        if device.serial_number
    )
    serials.discard("")
    return serials


class AskoheatFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for Blueprint."""

    VERSION = CONFIG_ENTRY_VERSION

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                device_infos = await self._async_read_device_infos(
                    user_input[CONF_HOST], user_input[CONF_PORT]
                )
            except UpdateFailed as exception:
                LOGGER.exception("Connection failed", exception)
                _errors["base"] = "connection"
            except HomeAssistantError as exception:
                LOGGER.exception("Unknown error", exception)
                _errors["base"] = "unknown"
            else:
                LOGGER.debug(
                    "Successfully connected to askoheat instance with serial %s",
                    device_infos.serial_number,
                )
                cleaned_serial_number = (
                    device_infos.serial_number.lower()
                    .replace("-", "_")
                    .replace(".", "_")
                )
                unique_id = f"{DOMAIN}_{cleaned_serial_number}"
                self._title = title = (
                    f"{device_infos.article_name} {device_infos.article_number} {device_infos.serial_number}"  # noqa: E501
                )

                LOGGER.debug(
                    "Try to register new device with unique id: %s",
                    unique_id,
                )

                # The unique_id of an existing entry is frozen at creation time,
                # but the device may report a different serial since (firmware).
                # Compare with the serials the entries are known under.
                known_entry = self._find_configured_entry(device_infos.serial_number)
                if known_entry is not None and known_entry.unique_id != unique_id:
                    self._update_host(
                        known_entry, user_input[CONF_HOST], user_input[CONF_PORT]
                    )
                    return self.async_abort(reason="already_configured")

                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured(updates=user_input)

                name = f"{title} ({user_input[CONF_HOST]}:{user_input[CONF_PORT]})"

                return self.async_create_entry(
                    title=title,
                    data=user_input,
                    description_placeholders={"name": name},
                )

        return self.async_show_form(
            step_id="user",
            description_placeholders={"repo_url": REPO_URL},
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=_errors,
        )

    async def async_step_dhcp(
        self, discovery_info: DhcpServiceInfo
    ) -> ConfigFlowResult:
        """
        Prepare configuration for a DHCP discovered Askoheat device.

        A device is identified by its MAC address or serial number, never by its
        IP address or hostname: an address may be handed to another device.
        """
        LOGGER.info(
            "Found device with hostname '%s' IP '%s'",
            discovery_info.hostname,
            discovery_info.ip,
        )
        host = discovery_info.ip
        mac = _normalize_serial(discovery_info.macaddress)

        # 1. the MAC address is known: only the address may have changed
        known_entry = self._find_configured_entry(mac)
        if known_entry is not None:
            self._update_host(known_entry, host)
            return self.async_abort(reason="already_configured")

        # 2. stable id so the flow is deduplicated and can be ignored
        await self.async_set_unique_id(f"{DOMAIN}_{mac}")
        self._abort_if_unique_id_configured()

        # 3. ask the device for its serial and compare it with known devices
        try:
            device_infos = await self._async_read_device_infos(host, DEFAULT_PORT)
        except (UpdateFailed, HomeAssistantError, TimeoutError, OSError):
            LOGGER.debug("Cannot read serial number from discovered device %s", host)
        else:
            known_entry = self._find_configured_entry(device_infos.serial_number)
            if known_entry is not None:
                self._update_host(known_entry, host)
                return self.async_abort(reason="already_configured")

        config = dict[str, Any]()
        config[CONF_HOST] = host
        config[CONF_PORT] = DEFAULT_PORT

        return self.async_show_form(
            step_id="user",
            description_placeholders={"repo_url": REPO_URL},
            data_schema=_step_user_data_schema(MappingProxyType(config)),
            errors={},
        )

    async def _async_read_device_infos(
        self, host: str, port: int
    ) -> AskoheatDeviceInfos:
        """Connect to the device and read its parameters."""
        client = AskoheatModbusApiClient(host=host, port=port)
        try:
            await client.connect()
            coordinator = AskoheatParameterDataUpdateCoordinator(self.hass, client)
            parameters = await coordinator.load_parameters(client)
        finally:
            client.close()
        return AskoheatDeviceInfos(parameters)

    def _find_configured_entry(self, serial: str) -> ConfigEntry | None:
        """Return the configured entry of the device with this serial or MAC."""
        wanted = _normalize_serial(serial)
        if not wanted:
            return None
        return next(
            (
                entry
                for entry in self._async_current_entries(include_ignore=False)
                if wanted in _entry_serials(self.hass, entry)
            ),
            None,
        )

    def _update_host(
        self, entry: ConfigEntry, host: str, port: int | None = None
    ) -> None:
        """Update the address of an already identified device."""
        data = {**entry.data, CONF_HOST: host}
        if port is not None:
            data[CONF_PORT] = port
        if data != dict(entry.data):
            LOGGER.info("Askoheat device moved to %s, updating entry", host)
            self.hass.config_entries.async_update_entry(entry, data=data)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: AskoheatConfigEntry) -> OptionsFlow:
        """Get the options flow for this handler."""
        return AskoheatOptionsFlowHandler(config_entry)


class AskoheatOptionsFlowHandler(OptionsFlowWithConfigEntry):
    """Handle an options flow."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle options flow."""
        _errors = {}
        if user_input is not None:
            LOGGER.debug("Received user_input:%s", user_input)
            try:
                client = AskoheatModbusApiClient(
                    host=user_input[CONF_HOST], port=user_input[CONF_PORT]
                )
                await client.connect()
                if not client.is_connected:
                    raise AskoheatModbusApiClientCommunicationError  # noqa: TRY301

                client.close()
            except AskoheatModbusApiClientCommunicationError:
                LOGGER.exception("Connection failed")
                _errors["base"] = "connection"
            except HomeAssistantError as exception:
                LOGGER.exception("Unknown error", exception)
                _errors["base"] = "unknown"
            else:
                LOGGER.debug("Successfully connected")
                # Update existing configuration data
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data=user_input,
                    options=self.config_entry.options,
                )
                # Return empty options
                return self.async_create_entry(title="", data={})
            finally:
                if "client" in locals():
                    client.close()

        return self.async_show_form(
            step_id="init",
            errors=_errors,
            description_placeholders={"repo_url": REPO_URL},
            data_schema=_step_user_data_schema(
                MappingProxyType(self.config_entry.data)
            ),
        )
