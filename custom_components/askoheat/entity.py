"""BlueprintEntity class."""

from __future__ import annotations

from typing import TypeVar

from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.askoheat.model import AskoheatEntityDescription

from .const import ATTRIBUTION
from .coordinator import AskoheatDataUpdateCoordinator

E = TypeVar("E", bound=AskoheatEntityDescription)


class AskoheatEntity[E](CoordinatorEntity[AskoheatDataUpdateCoordinator]):
    """AskoheatEntity class."""

    _attr_attribution = ATTRIBUTION
    entity_description: E

    def __init__(
        self,
        coordinator: AskoheatDataUpdateCoordinator,
        entity_description: E,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.entry_id,
                ),
            },
        )
        self.entity_description = entity_description
        self.translation_key = (
            entity_description.translation_key or entity_description.key.value
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
        if descr.icon_by_state is not None and icon_state in descr.icon_by_state:
            self._attr_icon = descr.icon_by_state.get(icon_state)
        else:
            self._attr_icon = descr.icon

        super()._handle_coordinator_update()
        self.async_write_ha_state()
