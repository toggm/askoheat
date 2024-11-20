"""Adds config flow for Blueprint."""

from __future__ import annotations

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
    CONF_DEVICE_UNIQUE_ID,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DOMAIN,
    LOGGER,
    SensorAttrKey,
)

PORT_SELECTOR = vol.All(
    selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=1, step=1, max=65535, mode=selector.NumberSelectorMode.BOX
        )
    ),
    vol.Coerce(int),
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): PORT_SELECTOR,
    }
)


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
                article_name = parameters[f"sensors.{SensorAttrKey.PAR_ARTICLE_NAME}"]
                article_number = parameters[
                    f"sensors.{SensorAttrKey.PAR_ARTICLE_NUMBER}"
                ]
                serial_number = parameters[f"sensors.{SensorAttrKey.PAR_ID}"]
                unique_id = serial_number.lower().replace("-", "_")

                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                self._title = title = f"{article_name} {article_number} {serial_number}"
                name = f"{title} ({user_input[CONF_HOST]}:{user_input[CONF_PORT]})"

                self.context["data"][CONF_DEVICE_UNIQUE_ID] = unique_id

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
