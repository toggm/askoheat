"""Askoheat time entity."""

from functools import cached_property

from homeassistant.components.select import ENTITY_ID_FORMAT, SelectEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.askoheat.api_conf_desc import CONF_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_ema_desc import EMA_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.const import LOGGER
from custom_components.askoheat.coordinator import AskoheatDataUpdateCoordinator
from custom_components.askoheat.model import (
    AskoheatSelectEntityDescription,
)

from .data import AskoheatConfigEntry
from .entity import AskoheatEntity


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: AskoheatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select platform."""
    async_add_entities(
        AskoheatSelect(
            coordinator=entry.runtime_data.ema_coordinator,
            entity_description=entity_description,
        )
        for entity_description in EMA_REGISTER_BLOCK_DESCRIPTOR.select_inputs
    )
    async_add_entities(
        AskoheatSelect(
            coordinator=entry.runtime_data.config_coordinator,
            entity_description=entity_description,
        )
        for entity_description in CONF_REGISTER_BLOCK_DESCRIPTOR.select_inputs
    )


class AskoheatSelect(AskoheatEntity[AskoheatSelectEntityDescription], SelectEntity):
    """Askoheat select entity."""

    def __init__(
        self,
        coordinator: AskoheatDataUpdateCoordinator,
        entity_description: AskoheatSelectEntityDescription,
    ) -> None:
        """Initialize the select class."""
        super().__init__(coordinator, entity_description)
        self.entity_id = ENTITY_ID_FORMAT.format(entity_description.key)
        self._attr_unique_id = self.entity_id
        self.current_option = None

    @cached_property
    def _entity_translation_key_base(self) -> str | None:
        """Return translation key for entity name."""
        if self.translation_key is None:
            return None
        return (
            f"component.{self.platform.platform_name}.entity.{self.platform.domain}"
            f".{self.translation_key}"
        )

    @cached_property
    def _options_to_enum(self) -> dict[str, object]:
        return {
            self.platform.object_id_platform_translations.get(
                f"{self._entity_translation_key_base}.state.{e}"
            )
            or str(e): e
            for e in self.entity_description.api_descriptor.values  # type: ignore  # noqa: PD011, PGH003
        }

    @cached_property
    def _enum_to_options(self) -> dict[object, str]:
        return {e: v for v, e in self._options_to_enum.items()}

    @cached_property
    def options(self) -> list[str]:
        """Return a set of selectable options."""
        self.options = list(self._options_to_enum)
        return self.options

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        data = self.coordinator.data
        if data is None:
            return
        enum = data[self.entity_description.data_key]
        self.current_option = self._enum_to_options[enum]
        super()._handle_coordinator_update()

    async def async_select_option(self, value: str) -> None:
        """Update the current value."""
        if self.entity_description.api_descriptor is None:
            LOGGER.error(
                "Cannot set value, missing api_descriptor on entity %s", self.entity_id
            )
            return
        enum = self._options_to_enum[value]
        await self.coordinator.async_write(self.entity_description.api_descriptor, enum)
        self._handle_coordinator_update()