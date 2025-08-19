"""
Custom integration to integrate askoheat+ hot water heating with Home Assistant.

For more details about this integration, please refer to
https://github.com/toggm/askoheat
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.loader import async_get_loaded_integration

from custom_components.askoheat.const import DeviceKey

from .api import AskoheatModbusApiClient
from .const import (
    CONF_ANALOG_INPUT_UNIT,
    CONF_DEVICE_UNITS,
    CONF_HEATPUMP_UNIT,
    CONF_LEGIONELLA_PROTECTION_UNIT,
    CONF_MODBUS_MASTER_UNIT,
    DOMAIN,
    LOGGER,
)
from .coordinator import (
    AskoheatConfigDataUpdateCoordinator,
    AskoheatEMADataUpdateCoordinator,
    AskoheatOperationDataUpdateCoordinator,
    AskoheatParameterDataUpdateCoordinator,
)
from .data import AskoheatData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers import device_registry as dr

    from .data import AskoheatConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.TIME,
    Platform.TEXT,
    Platform.SELECT,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: AskoheatConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    client = AskoheatModbusApiClient(
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
    )

    await client.connect()

    if not client.is_connected:
        msg = "Could not connect to modbus client"
        LOGGER.error(msg)
        raise ConfigEntryNotReady(msg)

    LOGGER.debug(
        "Connect modbus client %s:%s",
        entry.data[CONF_HOST],
        entry.data[CONF_PORT],
    )

    par_coordinator = AskoheatParameterDataUpdateCoordinator(
        hass=hass, client=client, config_entry=entry
    )
    ema_coordinator = AskoheatEMADataUpdateCoordinator(
        hass=hass, client=client, config_entry=entry
    )
    config_coordinator = AskoheatConfigDataUpdateCoordinator(
        hass=hass, client=client, config_entry=entry
    )
    data_coordinator = AskoheatOperationDataUpdateCoordinator(
        hass=hass, client=client, config_entry=entry
    )

    # default devices
    supported_devices = [DeviceKey.WATER_HEATER_CONTROL_UNIT, DeviceKey.ENERGY_MANAGER]
    # add devices based on configuration
    additional_devices = entry.data.get(CONF_DEVICE_UNITS) or {}
    if additional_devices.get(CONF_LEGIONELLA_PROTECTION_UNIT):
        supported_devices.append(DeviceKey.LEGIO_PROTECTION_CONTROL_UNIT)
    if additional_devices.get(CONF_ANALOG_INPUT_UNIT):
        supported_devices.append(DeviceKey.ANALOG_INPUT_CONTROL_UNIT)
    if additional_devices.get(CONF_MODBUS_MASTER_UNIT):
        supported_devices.append(DeviceKey.MODBUS_MASTER)
    if additional_devices.get(CONF_HEATPUMP_UNIT):
        supported_devices.append(DeviceKey.HEATPUMP_CONTROL_UNIT)

    entry.runtime_data = AskoheatData(
        client=client,
        integration=async_get_loaded_integration(hass, entry.domain),
        ema_coordinator=ema_coordinator,
        config_coordinator=config_coordinator,
        par_coordinator=par_coordinator,
        data_coordinator=data_coordinator,
        supported_devices=supported_devices,
    )

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await par_coordinator.async_config_entry_first_refresh()
    await ema_coordinator.async_config_entry_first_refresh()
    await config_coordinator.async_config_entry_first_refresh()
    await data_coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_remove_config_entry_device(
    hass: HomeAssistant,  # noqa: ARG001
    config_entry: AskoheatConfigEntry,
    device_entry: dr.DeviceEntry,
) -> bool:
    """Remove a config entry from a device."""
    return any(
        device_unit
        for device_unit in [
            identifier[1].split(".")[0]
            for identifier in device_entry.identifiers
            if identifier[0] == DOMAIN
        ]
        # Cannot remove core units
        if device_unit
        not in (DeviceKey.ENERGY_MANAGER, DeviceKey.WATER_HEATER_CONTROL_UNIT)
        # nor if the device is still selected in the configuration
        and config_entry.data.get(CONF_DEVICE_UNITS)
        and config_entry.data[CONF_DEVICE_UNITS].get(device_unit) is not True
    )


async def async_unload_entry(
    hass: HomeAssistant,
    entry: AskoheatConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    entry.runtime_data.client.close()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: AskoheatConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
