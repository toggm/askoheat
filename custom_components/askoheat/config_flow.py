"""Adds config flow for Blueprint."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING, Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries, data_entry_flow
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers import selector

from custom_components.askoheat.coordinator import (
    AskoheatParameterDataUpdateCoordinator,
)

from .api import (
    AskoHeatModbusApiClient,
    AskoheatModbusApiClientCommunicationError,
    AskoheatModbusApiClientError,
)
from .const import (
    CONF_ANALOG_INPUT_UNIT,
    CONF_DEVICE_UNITS,
    CONF_HEATPUMP_UNIT,
    CONF_LEGIONELLA_PROTECTION_UNIT,
    CONF_MODBUS_MASTER_UNIT,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DOMAIN,
    LOGGER,
    SensorAttrKey,
)

if TYPE_CHECKING:
    from homeassistant.components.dhcp import DhcpServiceInfo

PORT_SELECTOR = vol.All(
    selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=1, step=1, max=65535, mode=selector.NumberSelectorMode.BOX
        )
    ),
    vol.Coerce(int),
)


def _step_user_data_schema(
    data: MappingProxyType[str, Any] | None = None,
) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_HOST, default=data[CONF_HOST] if data else DEFAULT_HOST
            ): cv.string,
            vol.Required(
                CONF_PORT, default=data[CONF_PORT] if data else DEFAULT_PORT
            ): PORT_SELECTOR,
            CONF_DEVICE_UNITS: data_entry_flow.section(
                vol.Schema(
                    {
                        vol.Required(
                            CONF_LEGIONELLA_PROTECTION_UNIT,
                            default=data[CONF_DEVICE_UNITS][
                                CONF_LEGIONELLA_PROTECTION_UNIT
                            ]
                            if data
                            else True,
                        ): cv.boolean,
                        vol.Required(
                            CONF_HEATPUMP_UNIT,
                            default=data[CONF_DEVICE_UNITS][
                                CONF_LEGIONELLA_PROTECTION_UNIT
                            ]
                            if data
                            else False,
                        ): cv.boolean,
                        vol.Required(
                            CONF_ANALOG_INPUT_UNIT,
                            default=data[CONF_DEVICE_UNITS][
                                CONF_LEGIONELLA_PROTECTION_UNIT
                            ]
                            if data
                            else False,
                        ): cv.boolean,
                        vol.Required(
                            CONF_MODBUS_MASTER_UNIT,
                            default=data[CONF_DEVICE_UNITS][
                                CONF_LEGIONELLA_PROTECTION_UNIT
                            ]
                            if data
                            else False,
                        ): cv.boolean,
                    }
                ),
                {"collapsed": False},
            ),
        }
    )


STEP_USER_DATA_SCHEMA = _step_user_data_schema()


class AskoheatFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Blueprint."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> data_entry_flow.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                client = AskoHeatModbusApiClient(
                    host=user_input[CONF_HOST], port=user_input[CONF_PORT]
                )
                await client.connect()
                coordinator = AskoheatParameterDataUpdateCoordinator(self.hass)
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
                article_name = parameters[f"sensor.{SensorAttrKey.PAR_ARTICLE_NAME}"]
                article_number = parameters[
                    f"sensor.{SensorAttrKey.PAR_ARTICLE_NUMBER}"
                ]
                serial_number = parameters[f"sensor.{SensorAttrKey.PAR_ID}"]
                cleaned_serial_number = (
                    serial_number.lower().replace("-", "_").replace(".", "_")
                )
                unique_id = f"{DOMAIN}_{cleaned_serial_number}"

                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                self._title = title = f"{article_name} {article_number} {serial_number}"
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
    ) -> data_entry_flow.FlowResult:
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
