"""Adds config flow for Blueprint."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING, Any, cast

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import data_entry_flow
from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
    OptionsFlowWithConfigEntry,
)
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import callback
from homeassistant.helpers import selector

from custom_components.askoheat.coordinator import (
    AskoheatParameterDataUpdateCoordinator,
)
from custom_components.askoheat.data import AskoheatDeviceInfos

from .api import (
    AskoheatModbusApiClient,
    AskoheatModbusApiClientCommunicationError,
    AskoheatModbusApiClientError,
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
    DEFAULT_HOST,
    DEFAULT_PORT,
    DOMAIN,
    LOGGER,
)

if TYPE_CHECKING:
    from homeassistant.components.dhcp import DhcpServiceInfo

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


class OptionalEntitySelector(selector.EntitySelector):
    """Optional entity selector."""

    def __init__(self, config: selector.EntitySelectorConfig | None = None) -> None:
        """Instantiate a selector."""
        super().__init__(config)

    def __call__(self, data: Any) -> str | list[str]:
        """Validate the passed selection."""
        if data is None:
            return []
        return selector.EntitySelector.__call__(self, data)


def _step_user_data_schema(
    data: MappingProxyType[str, Any] | None = None,
) -> vol.Schema:
    LOGGER.debug("_step_user_data_schema: %s", data)
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
                        vol.Optional(
                            CONF_POWER_ENTITY_ID,
                            default=_get_section_entry_or_none(
                                data, CONF_FEED_IN, CONF_POWER_ENTITY_ID
                            ),
                        ): OptionalEntitySelector(
                            selector.EntitySelectorConfig(
                                filter=selector.EntityFilterSelectorConfig(
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


class AskoheatFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for Blueprint."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                client = AskoheatModbusApiClient(
                    host=user_input[CONF_HOST], port=user_input[CONF_PORT]
                )
                await client.connect()
                coordinator = AskoheatParameterDataUpdateCoordinator(self.hass, client)
                parameters = await coordinator.load_parameters(client)

                client.close()
            except AskoheatModbusApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except AskoheatModbusApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                LOGGER.debug(
                    "Successfully connected to askoheat instance, "
                    "received parameters: %s",
                    parameters,
                )
                device_infos = AskoheatDeviceInfos(parameters)
                cleaned_serial_number = (
                    device_infos.serial_number.lower()
                    .replace("-", "_")
                    .replace(".", "_")
                )
                cleaned_article_number = (
                    device_infos.article_number.lower()
                    .replace("-", "_")
                    .replace(".", "_")
                )
                # Use a composite unique id based on article number and serial number
                # to support multiple devices that may report the same serial number.
                unique_id = f"{DOMAIN}_{cleaned_article_number}_{cleaned_serial_number}"
                self._title = title = (
                    f"{device_infos.article_name} {device_infos.article_number} {device_infos.serial_number}"  # noqa: E501
                )

                LOGGER.debug(
                    "Try to register new device with unique id: %s",
                    unique_id,
                )

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
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=_errors,
        )

    async def async_step_dhcp(
        self, discovery_info: DhcpServiceInfo
    ) -> ConfigFlowResult:
        """Prepare configuration for a DHCP discovered Askoheat device."""
        LOGGER.info(
            "Found device with hostname '%s' IP '%s'",
            discovery_info.hostname,
            discovery_info.ip,
        )
        # Validate dhcp result with socket broadcast:
        config = dict[str, Any]()
        config[CONF_HOST] = discovery_info.ip
        config[CONF_PORT] = DEFAULT_PORT

        return self.async_show_form(
            step_id="user",
            data_schema=_step_user_data_schema(MappingProxyType(config)),
            errors={},
        )

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
        if user_input is not None:
            LOGGER.debug("Received user_input:%s", user_input)
            # Update existing configuration data
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=user_input, options=self.config_entry.options
            )
            # Return empty options
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=_step_user_data_schema(
                MappingProxyType(self.config_entry.data)
            ),
        )
