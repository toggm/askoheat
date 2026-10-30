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
    CONFIG_ENTRY_VERSION,
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


def _restore_legacy_unique_ids(hass: HomeAssistant, entry: AskoheatConfigEntry) -> None:
    """
    Restore the unique_ids registered up to v1.1.1.

    Up to v1.1.1 the unique_id was `<domain>.<entry unique_id>_<key>`, built from
    the raw (possibly MAC based, with colons) config entry unique_id. v1.2.0
    rewrote it to a slugified form without the domain prefix, which made Home
    Assistant register every entity a second time (`..._2`).

    Entities that still carry the 1.2.0 form get their legacy unique_id back. If
    the original entry still exists next to it, the duplicate is removed so the
    original (entity_id, history, customizations) is used again. The entity_id
    is never changed here.
    """
    registry = er.async_get(hass)
    raw_device = entry.unique_id or "unknown"
    slug_device = slugify(raw_device)
    for entity_entry in list(registry.entities.values()):
        if (
            entity_entry.config_entry_id != entry.entry_id
            or entity_entry.platform != DOMAIN
        ):
            continue
        domain = entity_entry.domain
        legacy_prefix = f"{domain}.{raw_device}_"
        uid = entity_entry.unique_id or ""
        if uid.startswith(legacy_prefix):
            continue
        rest = uid.removeprefix(f"{domain}.")
        if not rest.startswith(f"{slug_device}_"):
            continue
        legacy_uid = f"{legacy_prefix}{rest.removeprefix(f'{slug_device}_')}"
        original_id = registry.async_get_entity_id(domain, DOMAIN, legacy_uid)
        if original_id is not None and original_id != entity_entry.entity_id:
            LOGGER.info(
                "Removing duplicate entity %s, keeping %s",
                entity_entry.entity_id,
                original_id,
            )
            registry.async_remove(entity_entry.entity_id)
        else:
            registry.async_update_entity(
                entity_entry.entity_id, new_unique_id=legacy_uid
            )


def _read_mapping_file(path: Path) -> list[tuple[str, str]]:
    """Read `old_entity_id new_entity_id` pairs written by v1.2.0."""
    if not path.is_file():
        return []
    pairs = []
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[0] != parts[1]:  # noqa: PLR2004
            pairs.append((parts[0], parts[1]))
    return pairs


def _restore_renamed_entity_ids(
    hass: HomeAssistant,
    entry: AskoheatConfigEntry,
    pairs: list[tuple[str, str]],
) -> None:
    """Undo entity_id renames done by the v1.2.0 migration, where possible."""
    registry = er.async_get(hass)
    for old_id, new_id in pairs:
        current = registry.async_get(new_id)
        # old ids with colons are invalid and cannot be restored
        if (
            ":" in old_id
            or current is None
            or current.config_entry_id != entry.entry_id
            or registry.async_get(old_id) is not None
        ):
            continue
        registry.async_update_entity(new_id, new_entity_id=old_id)
        LOGGER.info("Restored entity_id %s -> %s", new_id, old_id)


async def async_migrate_entry(hass: HomeAssistant, entry: AskoheatConfigEntry) -> bool:
    """
    Migrate the config entry to the current version.

    Version 2: the registry is brought back to the unique_ids used up to v1.1.1
    (see `_restore_legacy_unique_ids`) and entity_ids renamed by v1.2.0 are
    restored from the mapping file it wrote.
    """
    if entry.version > CONFIG_ENTRY_VERSION:
        return False
    if entry.version < CONFIG_ENTRY_VERSION:
        mapping_path = Path(hass.config.path(f"mappings_askoheat_{entry.entry_id}.txt"))
        pairs = await hass.async_add_executor_job(_read_mapping_file, mapping_path)
        _restore_legacy_unique_ids(hass, entry)
        _restore_renamed_entity_ids(hass, entry, pairs)
        hass.config_entries.async_update_entry(entry, version=CONFIG_ENTRY_VERSION)
    return True


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
