"""Diagnostics support for Askoheat."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import AskoheatConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,  # noqa: ARG001
    entry: AskoheatConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    return {
        "entry_data": dict(entry.data),
        "data": {
            "energy_manager": entry.runtime_data.ema_coordinator.data,
            "config": entry.runtime_data.config_coordinator.data,
            "operation": entry.runtime_data.data_coordinator.data,
            "parameter": entry.runtime_data.par_coordinator.data,
        },
    }
