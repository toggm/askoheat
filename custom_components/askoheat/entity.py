# Copyright (c) 2025 Mike Toggweiler @toggm
# SPDX-License-Identifier: MIT

"""BlueprintEntity class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from custom_components.askoheat.model import AskoheatEntityDescription

from .const import ATTRIBUTION, AttributeKeys, DeviceKey
from .coordinator import AskoheatDataUpdateCoordinator

if TYPE_CHECKING:
    from .data import AskoheatConfigEntry


class AskoheatBaseEntity[D: AskoheatEntityDescription[Any, Any]](Entity):
    """Base entity."""

    _attr_has_entity_name = True
    entity_description: D

    def __init__(self, entry: AskoheatConfigEntry, entity_description: D) -> None:
        """Initialize."""
        # store a slugified device unique id to ensure it is valid for entity ids
        self._device_unique_id = slugify(entry.unique_id or "unknown")
        self.entry = entry
        parent_identifier = f"{DeviceKey.WATER_HEATER_CONTROL_UNIT}.{entry.entry_id}"
        device_identifier = f"{entity_description.device_key}.{entry.entry_id}"
        via_device_id: str | None = None
        # Only set via_device_id for child units; the water heater control unit itself
        # must not point to itself as a parent.
        if entity_description.device_key != DeviceKey.WATER_HEATER_CONTROL_UNIT:
            if self.hass is not None:
                via_device_id = dr.async_get_device_id_by_identifier(
                    self.hass,
                    (entry.domain, parent_identifier),
                    config_entry_id=entry.entry_id,
                )
            if via_device_id is None:
                via_device_id = entry.runtime_data.parent_device_id

        self._attr_device_info = DeviceInfo(
            identifiers={(entry.domain, device_identifier)},
            translation_key=entity_description.device_key,
            manufacturer="Askoma AG",
            model=entry.runtime_data.device_info.article_name,
            model_id=entry.runtime_data.device_info.article_number,
            sw_version=entry.runtime_data.device_info.software_version,
            hw_version=entry.runtime_data.device_info.hardwareware_version,
            serial_number=entry.runtime_data.device_info.serial_number,
        )

        if via_device_id is not None:
            self._attr_device_info["via_device_id"] = via_device_id

        self.entity_description = entity_description
        self.translation_key = (
            entity_description.translation_key or entity_description.key.value
        )


class AskoheatEntity[D: AskoheatEntityDescription[Any, Any]](
    CoordinatorEntity[AskoheatDataUpdateCoordinator], AskoheatBaseEntity[D]
):
    """AskoheatEntity class."""

    _attr_attribution = ATTRIBUTION

    _unrecorded_attributes = frozenset({AttributeKeys.API_DESCRIPTOR})

    def __init__(
        self,
        entry: AskoheatConfigEntry,
        coordinator: AskoheatDataUpdateCoordinator,
        entity_description: D,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator=coordinator)
        AskoheatBaseEntity.__init__(
            self=self, entry=entry, entity_description=entity_description
        )
        # Ensure slugified id is used here as well
        self._device_unique_id = slugify(entry.unique_id or "unknown")
        self._attr_extra_state_attributes = {
            AttributeKeys.API_DESCRIPTOR: f"{entity_description.api_descriptor}"
        }

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        # initially initialize values
        self._handle_coordinator_update()

    async def _data_update(self) -> None:
        self._handle_coordinator_update()

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.entry.runtime_data.client.is_ready

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        descr = self.entity_description

        # Calc icon:
        icon_state = self._attr_state
        if hasattr(self, "_attr_is_on"):
            icon_state = self._attr_is_on  # type: ignore  # noqa: PGH003
        if descr.icon_by_state is not None and icon_state in descr.icon_by_state:
            self._attr_icon = descr.icon_by_state.get(icon_state)  # type: ignore  # noqa: PGH003
        else:
            self._attr_icon = descr.icon

        super()._handle_coordinator_update()
