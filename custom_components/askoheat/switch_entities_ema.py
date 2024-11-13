"""Predefined energy manager switches."""

from custom_components.askoheat.const import SwitchAttrKey
from custom_components.askoheat.model import AskoheatSwitchEntityDescription

EMA_SWITCH_ENTITY_DESCRIPTIONS = (
    AskoheatSwitchEntityDescription(
        key=SwitchAttrKey.EMA_SET_HEATER_STEP_HEATER1,
        icon="mdi:heat-wave",
        entity_category=None,
    ),
    AskoheatSwitchEntityDescription(
        key=SwitchAttrKey.EMA_SET_HEATER_STEP_HEATER2,
        icon="mdi:heat-wave",
        entity_category=None,
    ),
    AskoheatSwitchEntityDescription(
        key=SwitchAttrKey.EMA_SET_HEATER_STEP_HEATER3,
        icon="mdi:heat-wave",
        entity_category=None,
    ),
)
