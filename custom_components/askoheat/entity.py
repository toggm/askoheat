"""BlueprintEntity class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.askoheat.model import AdkoheatEntityDescription

from .const import ATTRIBUTION, LOGGER
from .coordinator import AskoheatDataUpdateCoordinator

from homeassistant.core import callback


class AskoheatEntity(CoordinatorEntity[AskoheatDataUpdateCoordinator]):
    """AskoheatEntity class."""

    _attr_attribution = ATTRIBUTION
    entity_description: AdkoheatEntityDescription

    def __init__(self, coordinator: AskoheatDataUpdateCoordinator) -> None:
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
