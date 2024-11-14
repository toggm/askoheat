"""Switch platform for askoheat."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import ENTITY_ID_FORMAT, SwitchEntity
from homeassistant.core import callback

from custom_components.askoheat.api_ema_desc import EMA_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.model import AskoheatSwitchEntityDescription

from .entity import AskoheatEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import AskoheatDataUpdateCoordinator
    from .data import AskoheatConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: AskoheatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    async_add_entities(
        AskoHeatSwitch(
            coordinator=entry.runtime_data.ema_coordinator,
            entity_description=entity_description,
        )
        for entity_description in EMA_REGISTER_BLOCK_DESCRIPTOR.switches
    )


class AskoHeatSwitch(AskoheatEntity[AskoheatSwitchEntityDescription], SwitchEntity):
    """askoheat switch class."""

    def __init__(
        self,
        coordinator: AskoheatDataUpdateCoordinator,
        entity_description: AskoheatSwitchEntityDescription,
    ) -> None:
        """Initialize the switch class."""
        super().__init__(coordinator, entity_description)
        self.entity_id = ENTITY_ID_FORMAT.format(entity_description.key)
        self._attr_unique_id = self.entity_id

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        data = self.coordinator.data
        if data is None:
            return
        self._attr_state = data[self.entity_description.data_key]
        if (
            self.entity_description.on_state is True
            or self.entity_description.on_state is False
        ) and self._attr_state is not None:
            self._attr_state = bool(self._attr_state)  # type: ignore  # noqa: PGH003
        if self.entity_description.inverted:
            self._attr_is_on = self._attr_state != self.entity_description.on_state
        else:
            self._attr_is_on = self._attr_state == self.entity_description.on_state or (
                self.entity_description.on_states is not None
                and self._attr_state in self.entity_description.on_states
            )

        super()._handle_coordinator_update()

    async def async_turn_on(self, **_: Any) -> None:
        """Turn on the switch."""
        await self._set_state(self.entity_description.on_state)

    async def async_turn_off(self, **_: Any) -> None:
        """Turn off the switch."""
        await self._set_state(self.entity_description.off_state)

    async def _set_state(self, state: str | bool) -> None:
        """."""
        # data = await self.coordinator.async_write(
        # self.entity_description.data_key.value.split(".")[1], state
        # )
        # value = get_sensor_data(data, self.entity_description.key.value)
        # if (
        #   self.entity_description.on_state is True
        #  or self.entity_description.on_state is False
        # ):
        # value = bool(value)
        # self._attr_is_on = (
        #   value != self.entity_description.on_state
        #  if self.entity_description.inverted
        # else value == self.entity_description.on_state
        # )
        # self._handle_coordinator_update()
