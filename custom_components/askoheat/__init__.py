# Copyright (c) 2025 Mike Toggweiler @toggm
# SPDX-License-Identifier: MIT

"""
Custom integration to integrate askoheat+ hot water heating with Home Assistant.

For more details about this integration, please refer to
https://github.com/toggm/askoheat
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.loader import async_get_loaded_integration
from homeassistant.util import slugify

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


def _migrate_entity_registry(hass: HomeAssistant, entry: AskoheatConfigEntry) -> None:
    """
    Migrate entity registry entries for this config entry to slugified ids.

    This is synchronous on purpose — the entity registry APIs used here are
    synchronous. Keep the function small to reduce complexity in
    `async_setup_entry`.
    """
    try:
        registry = er.async_get(hass)
        for entity_entry in list(registry.entities.values()):
            if entity_entry.config_entry_id != entry.entry_id:
                continue
            old_entity_id = entity_entry.entity_id
            old_uid = entity_entry.unique_id or ""
            # Only migrate if old unique id contains colons (raw MAC) or the
            # entity_id contains colons
            if ":" not in old_uid and ":" not in (old_entity_id or ""):
                continue

            # Derive parts from the existing unique_id if possible, otherwise
            # fall back to parsing the entity_id.
            after = None
            if "." in old_uid:
                after = old_uid.split(".", 1)[1]
            elif "." in old_entity_id:
                after = old_entity_id.split(".", 1)[1]
            else:
                after = old_uid or old_entity_id

            idx = after.rfind("_")
            if idx == -1:
                device_part = after
                key_part = ""
            else:
                device_part = after[:idx]
                key_part = after[idx + 1 :]

            slug_device = slugify(device_part)
            domain = (
                old_entity_id.split(".", 1)[0]
                if old_entity_id and "." in old_entity_id
                else entry.domain
            )
            new_entity_id = (
                f"{domain}.{slug_device}_{key_part}"
                if key_part
                else f"{domain}.{slug_device}"
            )
            new_unique_id = f"{slug_device}_{key_part}" if key_part else slug_device

            if new_entity_id == old_entity_id and new_unique_id == old_uid:
                continue

            try:
                registry.async_update_entity(
                    old_entity_id,
                    new_entity_id=new_entity_id,
                    new_unique_id=new_unique_id,
                )
                LOGGER.info("Migrated entity_id %s -> %s", old_entity_id, new_entity_id)
                # record mapping to a file in HA config directory so users can
                # apply YAML replacements easily. Use entry_id to avoid
                # collisions when multiple config entries exist.
                try:
                    mapping_path = hass.config.path(
                        f"mappings_askoheat_{entry.entry_id}.txt"
                    )
                    with Path(mapping_path).open("a", encoding="utf-8") as mf:
                        mf.write(f"{old_entity_id} {new_entity_id}\n")
                except OSError as err:
                    LOGGER.exception(
                        "Unable to write mapping file %s: %s", mapping_path, err
                    )
            except (ValueError, KeyError) as err:
                LOGGER.exception("Failed to migrate entity %s: %s", old_entity_id, err)
    except (AttributeError, RuntimeError, KeyError, ValueError) as err:
        LOGGER.exception("Entity registry migration failed: %s", err)


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

    par_coordinator = AskoheatParameterDataUpdateCoordinator(hass=hass, client=client)
    ema_coordinator = AskoheatEMADataUpdateCoordinator(hass=hass, client=client)
    config_coordinator = AskoheatConfigDataUpdateCoordinator(hass=hass, client=client)
    data_coordinator = AskoheatOperationDataUpdateCoordinator(hass=hass, client=client)

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

    parent_identifier = (
        entry.domain,
        f"{DeviceKey.WATER_HEATER_CONTROL_UNIT}.{entry.entry_id}",
    )
    parent_device = dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={parent_identifier},
        manufacturer="Askoma AG",
        model=entry.runtime_data.device_info.article_name,
        model_id=entry.runtime_data.device_info.article_number,
        sw_version=entry.runtime_data.device_info.software_version,
        hw_version=entry.runtime_data.device_info.hardwareware_version,
        serial_number=entry.runtime_data.device_info.serial_number,
    )
    entry.runtime_data.parent_device_id = parent_device.id

    # perform entity registry migration in a small helper to reduce complexity
    _migrate_entity_registry(hass, entry)

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
