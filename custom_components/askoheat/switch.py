"""Switch platform for askoheat."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import ENTITY_ID_FORMAT, SwitchEntity
from homeassistant.const import CONF_HOST
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryError
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.httpx_client import get_async_client

from custom_components.askoheat.api_conf_desc import (
    CONF_FEED_IN_ENABLED_SWITCH_ENTITY_DESCRIPTOR,
    CONF_REGISTER_BLOCK_DESCRIPTOR,
)
from custom_components.askoheat.api_ema_desc import (
    EMA_EMERGENCY_MODE_API_DESCRIPTOR,
    EMA_FEED_IN_VALUE_NUMBER_ENTITY_DESCRIPTOR,
    EMA_REGISTER_BLOCK_DESCRIPTOR,
)
from custom_components.askoheat.api_par_desc import PARAM_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.const import (
    CONF_FEED_IN,
    CONF_POWER_ENTITY_ID,
    CONF_POWER_INVERT,
    HTTP_RESPONSE_CODE_OK,
    LOGGER,
    DeviceKey,
    NumberAttrKey,
    SwitchAttrKey,
)
from custom_components.askoheat.model import (
    AskoheatEmergencySwitchEntityDescription,
    AskoheatSwitchEntityDescription,
)

from .entity import AskoheatEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from custom_components.askoheat.coordinator import (
        AskoheatConfigDataUpdateCoordinator,
        AskoheatEMADataUpdateCoordinator,
    )

    from .coordinator import AskoheatDataUpdateCoordinator
    from .data import AskoheatConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: AskoheatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""

    def config_power_entity() -> str | None:
        dev = entry.data.get(CONF_FEED_IN)
        return dev[CONF_POWER_ENTITY_ID] if dev else None

    power_entity_id = config_power_entity()
    async_add_entities(
        AskoheatSwitch(
            entry=entry,
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description, coordinator in {
            **dict.fromkeys(
                PARAM_REGISTER_BLOCK_DESCRIPTOR.switches,
                entry.runtime_data.par_coordinator,
            ),
            **dict.fromkeys(
                EMA_REGISTER_BLOCK_DESCRIPTOR.switches,
                entry.runtime_data.ema_coordinator,
            ),
            **dict.fromkeys(
                CONF_REGISTER_BLOCK_DESCRIPTOR.switches,
                entry.runtime_data.config_coordinator,
            ),
        }.items()
        if entity_description.device_key is None
        or entity_description.device_key in entry.runtime_data.supported_devices
    )
    if power_entity_id is not None and power_entity_id != []:
        if isinstance(power_entity_id, list) and len(power_entity_id) != 1:
            msg = "Cannot track multiple power_entities"
            raise ConfigEntryError(msg)

        def config_power_invert() -> bool:
            dev = entry.data.get(CONF_FEED_IN)
            return dev[CONF_POWER_INVERT] if dev else False

        async_add_entities(
            [
                AskoheatAutoFeedInSwitch(
                    entry=entry,
                    conf_coordinator=entry.runtime_data.config_coordinator,
                    ema_coordinator=entry.runtime_data.ema_coordinator,
                    entity_description=AskoheatSwitchEntityDescription(
                        key=SwitchAttrKey.EMA_AUTO_FEEDIN_SWITCH,
                        device_key=DeviceKey.ENERGY_MANAGER,
                        icon="mdi:solar-power",
                        api_descriptor=None,
                    ),
                    power_entity_id=power_entity_id,
                    invert_power=config_power_invert(),
                )
            ]
        )
    # Add emergency on/off switch
    async_add_entities(
        [
            AskoheatEmergencySwitch(
                entry=entry,
                coordinator=entry.runtime_data.ema_coordinator,
                entity_description=AskoheatEmergencySwitchEntityDescription(
                    key=SwitchAttrKey.CONTROL_EMERGENCY_MODE,
                    device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
                    icon="mdi:car-emergency",
                    api_descriptor=EMA_EMERGENCY_MODE_API_DESCRIPTOR,
                ),
            )
        ]
    )


class AskoheatSwitch(AskoheatEntity[AskoheatSwitchEntityDescription], SwitchEntity):
    """askoheat switch class."""

    entity_description: AskoheatSwitchEntityDescription

    def __init__(
        self,
        entry: AskoheatConfigEntry,
        coordinator: AskoheatDataUpdateCoordinator,
        entity_description: AskoheatSwitchEntityDescription,
    ) -> None:
        """Initialize the switch class."""
        super().__init__(entry, coordinator, entity_description)
        self.entity_id = ENTITY_ID_FORMAT.format(
            f"{self._device_unique_id}_{entity_description.key}"
        )
        self._attr_unique_id = self.entity_id

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            super().available
            and self.entity_description.data_key in self.coordinator.data
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        data = self.coordinator.data
        if data.get(self.entity_description.data_key) is None:
            return
        self._attr_state = data[self.entity_description.data_key]
        if (
            self.entity_description.on_state is True
            or self.entity_description.on_state is False
        ) and self._attr_state is not None:
            self._attr_is_on = bool(self._attr_state)
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
        """Set state of switch."""
        if self.entity_description.api_descriptor is None:
            LOGGER.error(
                "Cannot set state, missing api_descriptor on entity %s", self.entity_id
            )
            return
        await self.coordinator.async_write(
            self.entity_description.api_descriptor, state
        )
        self._handle_coordinator_update()


class AskoheatAutoFeedInSwitch(
    AskoheatEntity[AskoheatSwitchEntityDescription], SwitchEntity
):
    """askoheat auto feed-in switch class."""

    entity_description: AskoheatSwitchEntityDescription

    def __init__(  # noqa: PLR0913
        self,
        entry: AskoheatConfigEntry,
        conf_coordinator: AskoheatConfigDataUpdateCoordinator,
        ema_coordinator: AskoheatEMADataUpdateCoordinator,
        entity_description: AskoheatSwitchEntityDescription,
        power_entity_id: str,
        *,
        invert_power: bool,
    ) -> None:
        """Initialize the auto feed-in switch class."""
        super().__init__(entry, conf_coordinator, entity_description)
        self.entity_id = ENTITY_ID_FORMAT.format(
            f"{self._device_unique_id}_{entity_description.key}"
        )
        self._attr_unique_id = self.entity_id
        self._entry = entry
        self._buffer = 0
        self._buffer_entity_id = (
            f"number.{self._device_unique_id}_{NumberAttrKey.EMA_AUTO_FEEDIN_BUFFER}"
        )
        self._power_entity_id = power_entity_id
        self._invert_power = invert_power
        self._ema_coordinator = ema_coordinator

    async def async_added_to_hass(self) -> None:
        """Subscribe to the events."""
        await super().async_added_to_hass()
        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                [self._power_entity_id, self._buffer_entity_id],
                self.power_entity_change,
            )
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            super().available
            and EMA_FEED_IN_VALUE_NUMBER_ENTITY_DESCRIPTOR.data_key
            in self._ema_coordinator.data
        )

    async def power_entity_change(self, event: Event[EventStateChangedData]) -> None:
        """Power input changed."""
        LOGGER.debug("Power entity (%s) has changed", event.data["entity_id"])
        new_state = event.data["new_state"]
        if new_state is None:
            return

        if not self.available:
            return

        match event.data["entity_id"]:
            case self._buffer_entity_id:
                if new_state and new_state.state != "unknown":
                    self._buffer = int(new_state.state)
                    current_power_value = self.hass.states.get(self._power_entity_id)
                    if self._attr_is_on and current_power_value is not None:
                        await self.send_feed_in(float(current_power_value.state))
            case self._power_entity_id:
                if self._attr_is_on:
                    await self.send_feed_in(float(new_state.state))

    async def send_feed_in(self, power_value: float | None) -> None:
        """Send power value after adding buffer value."""
        api_desc = EMA_FEED_IN_VALUE_NUMBER_ENTITY_DESCRIPTOR.api_descriptor
        if api_desc is None:
            return

        raw_value = power_value or float(0)
        if power_value is not None:
            if self._invert_power:
                raw_value = raw_value * -1
            # add buffer
            raw_value = raw_value + self._buffer
        await self._ema_coordinator.async_write(api_desc, raw_value)

    async def async_turn_on(self, **_: Any) -> None:
        """Turn on the feed-in."""
        self._attr_is_on = True
        self.async_write_ha_state()

        # additionally provide current power value to evaluate if heating should be
        # turned on immediately
        current_power_value = self.hass.states.get(self._power_entity_id)
        if current_power_value is not None:
            await self.send_feed_in(float(current_power_value.state))

    async def async_turn_off(self, **_: Any) -> None:
        """Turn off feed-in."""
        self._attr_is_on = False
        self.async_write_ha_state()

        # additionally initialize with 0 power value
        await self.send_feed_in(None)

    async def _set_state(self, state: str | bool) -> None:
        """Set state of switch."""
        if CONF_FEED_IN_ENABLED_SWITCH_ENTITY_DESCRIPTOR.api_descriptor is None:
            LOGGER.error(
                "Cannot set state, missing api_descriptor on entity %s", self.entity_id
            )
            return
        await self.coordinator.async_write(
            CONF_FEED_IN_ENABLED_SWITCH_ENTITY_DESCRIPTOR.api_descriptor, state
        )
        self._handle_coordinator_update()


class AskoheatEmergencySwitch(AskoheatSwitch):
    """askoheat emergency switch class."""

    def __init__(
        self,
        entry: AskoheatConfigEntry,
        coordinator: AskoheatDataUpdateCoordinator,
        entity_description: AskoheatEmergencySwitchEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(entry, coordinator, entity_description)
        self._host = entry.data.get(CONF_HOST)

    async def __async_set_state(self, set_on: bool) -> None:  # noqa: FBT001
        """Send power value after adding buffer value."""
        client = get_async_client(self.hass, verify_ssl=False)
        command = "on" if set_on else "off"
        url = f"http://{self._host}/{command}"

        LOGGER.debug(f"Call rest command '{url}'")
        res = await client.get(url)

        if res.status_code != HTTP_RESPONSE_CODE_OK:
            LOGGER.warning(
                "Could not send command to askoheat rest interface: {e}", res.text
            )
            return

        if "OFF" in res.text:
            self._attr_is_on = False
            self.async_write_ha_state()
        if "ON" in res.text:
            self._attr_is_on = True
            self.async_write_ha_state()

    async def async_turn_on(self, **_: Any) -> None:
        """Turn on the feed-in."""
        await self.__async_set_state(set_on=True)

    async def async_turn_off(self, **_: Any) -> None:
        """Turn off feed-in."""
        await self.__async_set_state(set_on=False)
