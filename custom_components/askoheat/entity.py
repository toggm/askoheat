"""BlueprintEntity class."""

from __future__ import annotations

from typing import TypeVar

from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.askoheat.model import AskoheatEntityDescription

from .const import ATTRIBUTION, CONF_DEVICE_UNIQUE_ID, LOGGER, DeviceKey
from .coordinator import AskoheatDataUpdateCoordinator
from .data import AskoheatConfigEntry

E = TypeVar("E", bound=AskoheatEntityDescription)


class AskoheatEntity[E](CoordinatorEntity[AskoheatDataUpdateCoordinator]):
    """AskoheatEntity class."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION
    entity_description: E

    def __init__(
        self,
        entry: AskoheatConfigEntry,
        coordinator: AskoheatDataUpdateCoordinator,
        entity_description: E,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._device_unique_id = entry.unique_id or "unkown"
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    coordinator.config_entry.domain,
                    f"{entity_description.device_key}.{coordinator.config_entry.entry_id}",  # type: ignore  # noqa: PGH003
                ),
            },
            translation_key=entity_description.device_key,  # type: ignore  # noqa: PGH003
            via_device=(
                coordinator.config_entry.domain,
                DeviceKey.WATER_HEATER_CONTROL_UNIT,
            ),
        )
        self.entity_description = entity_description
        self.translation_key = (
            entity_description.translation_key or entity_description.key.value  # type: ignore  # noqa: PGH003
        )

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        # initially initialize values
        self._handle_coordinator_update()

    async def _data_update(self) -> None:
        self._handle_coordinator_update()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        descr = self.entity_description

        # Calc icon:
        icon_state = self._attr_state
        if hasattr(self, "_attr_is_on"):
            icon_state = self._attr_is_on  # type: ignore  # noqa: PGH003
        if descr.icon_by_state is not None and icon_state in descr.icon_by_state:  # type: ignore  # noqa: PGH003
            self._attr_icon = descr.icon_by_state.get(icon_state)  # type: ignore  # noqa: PGH003
        else:
            self._attr_icon = descr.icon  # type: ignore  # noqa: PGH003

        super()._handle_coordinator_update()
        self.async_write_ha_state()
