"""Tests for the registry migration (issues #194 and #216)."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.askoheat.const import CONFIG_ENTRY_VERSION, DOMAIN

MAC_ENTRY_ID = "askoheat_a8:42:e3:da:a3:a0"
MAC_SLUG = "askoheat_a8_42_e3_da_a3_a0"
KEY = "emergency_mode"
# what <= v1.1.1 registered for a device with a MAC based serial number
LEGACY_UID = f"switch.{MAC_ENTRY_ID}_{KEY}"
LEGACY_ENTITY_ID = f"switch.{MAC_SLUG}_{KEY}"


async def _setup(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


def _switches(registry: er.EntityRegistry, entry: MockConfigEntry) -> list[str]:
    return sorted(
        e.entity_id
        for e in registry.entities.values()
        if e.config_entry_id == entry.entry_id
        and e.domain == "switch"
        and KEY in e.unique_id
        and "enabled" not in e.unique_id
    )


@pytest.fixture
def mac_entry(
    hass: HomeAssistant, mock_config_entry_uninitialized: MockConfigEntry
) -> MockConfigEntry:
    """Config entry of a device reporting a MAC address as serial number."""
    entry = mock_config_entry_uninitialized
    entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(entry, unique_id=MAC_ENTRY_ID, version=1)
    return entry


async def test_untouched_legacy_install_is_not_duplicated(
    hass: HomeAssistant, mac_entry: MockConfigEntry
) -> None:
    """User still on <= v1.1.1: nothing may be renamed, nothing duplicated."""
    registry = er.async_get(hass)
    registry.async_get_or_create(
        "switch",
        DOMAIN,
        LEGACY_UID,
        config_entry=mac_entry,
        suggested_object_id=LEGACY_ENTITY_ID.split(".")[1],
    )

    await _setup(hass, mac_entry)

    assert _switches(registry, mac_entry) == [LEGACY_ENTITY_ID]
    restored = registry.async_get(LEGACY_ENTITY_ID)
    assert restored is not None
    assert restored.unique_id == LEGACY_UID
    assert hass.states.get(LEGACY_ENTITY_ID) is not None
    assert mac_entry.version == CONFIG_ENTRY_VERSION


async def test_user_renamed_entity_id_is_kept(
    hass: HomeAssistant, mac_entry: MockConfigEntry
) -> None:
    """A renamed entity_id (e.g. boiler_eg_*) survives and stays attached."""
    registry = er.async_get(hass)
    registry.async_get_or_create(
        "switch",
        DOMAIN,
        LEGACY_UID,
        config_entry=mac_entry,
        suggested_object_id="boiler_eg_notbetrieb",
    )

    await _setup(hass, mac_entry)

    assert _switches(registry, mac_entry) == ["switch.boiler_eg_notbetrieb"]
    assert hass.states.get("switch.boiler_eg_notbetrieb") is not None


async def test_v120_slugified_unique_id_is_restored(
    hass: HomeAssistant, mac_entry: MockConfigEntry
) -> None:
    """v1.2.0 rewrote the unique_id in place: restore it, keep the entity_id."""
    registry = er.async_get(hass)
    registry.async_get_or_create(
        "switch",
        DOMAIN,
        f"{MAC_SLUG}_{KEY}",  # unprefixed, slugified: v1.2.0 form
        config_entry=mac_entry,
        suggested_object_id="boiler_eg_notbetrieb",
    )

    await _setup(hass, mac_entry)

    assert _switches(registry, mac_entry) == ["switch.boiler_eg_notbetrieb"]
    restored = registry.async_get("switch.boiler_eg_notbetrieb")
    assert restored is not None
    assert restored.unique_id == LEGACY_UID


async def test_v120_duplicate_is_removed_and_original_kept(
    hass: HomeAssistant, mac_entry: MockConfigEntry
) -> None:
    """Original entity plus the `_2` copy created by v1.2.0."""
    registry = er.async_get(hass)
    registry.async_get_or_create(
        "switch",
        DOMAIN,
        LEGACY_UID,
        config_entry=mac_entry,
        suggested_object_id=LEGACY_ENTITY_ID.split(".")[1],
    )
    registry.async_get_or_create(
        "switch",
        DOMAIN,
        f"{MAC_SLUG}_{KEY}",
        config_entry=mac_entry,
        suggested_object_id=LEGACY_ENTITY_ID.split(".")[1],
    )
    assert registry.async_get(f"{LEGACY_ENTITY_ID}_2") is not None

    await _setup(hass, mac_entry)

    assert _switches(registry, mac_entry) == [LEGACY_ENTITY_ID]
    assert registry.async_get(f"{LEGACY_ENTITY_ID}_2") is None
    restored = registry.async_get(LEGACY_ENTITY_ID)
    assert restored is not None
    assert restored.unique_id == LEGACY_UID


@pytest.fixture
def mapping_file(hass: HomeAssistant, mac_entry: MockConfigEntry) -> Iterator[Path]:
    """Return the path of the mapping file written by the v1.2.0 migration."""
    path = Path(hass.config.path(f"mappings_askoheat_{mac_entry.entry_id}.txt"))
    yield path
    path.unlink(missing_ok=True)


async def test_v120_renamed_entity_id_is_restored(
    hass: HomeAssistant, mac_entry: MockConfigEntry, mapping_file: Path
) -> None:
    """v1.2.0 renamed boiler_eg_notbetrieb -> askoheat_*: rename it back."""
    registry = er.async_get(hass)
    registry.async_get_or_create(
        "switch",
        DOMAIN,
        f"{MAC_SLUG}_{KEY}",
        config_entry=mac_entry,
        suggested_object_id=LEGACY_ENTITY_ID.split(".")[1],
    )
    await hass.async_add_executor_job(
        mapping_file.write_text,
        f"switch.boiler_eg_notbetrieb {LEGACY_ENTITY_ID}\n"
        f"switch.{MAC_ENTRY_ID}_other {LEGACY_ENTITY_ID}\n"  # colon: not restorable
        f"{LEGACY_ENTITY_ID} {LEGACY_ENTITY_ID}\n",  # unchanged: ignored
        "utf-8",
    )

    await _setup(hass, mac_entry)

    assert _switches(registry, mac_entry) == ["switch.boiler_eg_notbetrieb"]
    restored = registry.async_get("switch.boiler_eg_notbetrieb")
    assert restored is not None
    assert restored.unique_id == LEGACY_UID


async def test_migration_runs_once(
    hass: HomeAssistant, mac_entry: MockConfigEntry
) -> None:
    """The repair only runs for version 1 entries; a reload leaves ids alone."""
    registry = er.async_get(hass)
    await _setup(hass, mac_entry)
    before = {e.entity_id: e.unique_id for e in registry.entities.values()}
    assert mac_entry.version == CONFIG_ENTRY_VERSION

    await hass.config_entries.async_reload(mac_entry.entry_id)
    await hass.async_block_till_done()

    assert before == {e.entity_id: e.unique_id for e in registry.entities.values()}


async def test_new_install_ids(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,  # noqa: ARG001
) -> None:
    """New installs: valid, slugified entity_ids and prefixed unique_ids."""
    registry = er.async_get(hass)
    entity = registry.async_get(f"switch.test_{KEY}")
    assert entity is not None
    assert entity.unique_id == f"switch.test_{KEY}"
    assert all(":" not in e.entity_id for e in registry.entities.values())
