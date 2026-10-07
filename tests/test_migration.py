"""Tests for migration of entity ids and unique_ids."""

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.askoheat.const import DOMAIN


async def test_slugify_and_migration(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Ensure slugify is used and migration renames entity registry entries."""
    # Create an entity registry entry that mimics the old format with colons
    from homeassistant.helpers import entity_registry as er

    registry = er.async_get(hass)

    old_entity_id = "sensor.askoheat_08:d1:f9:c4:6b:48_test_sensor"
    # unique_id historically was set to the entity_id as well
    old_unique_id = old_entity_id

    # Register this fake entity in the registry under the test config entry
    entry = mock_config_entry
    entity = registry.async_get_or_create(
        domain="sensor",
        platform=DOMAIN,
        unique_id=old_unique_id,
        config_entry=entry,
        suggested_object_id="askoheat_08:d1:f9:c4:6b:48_test_sensor",
    )

    assert entity is not None
    # Now re-run async_setup_entry which includes migration logic
    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    # After migration, find the registry entry for this config entry and object
    migrated = None
    for e in registry.entities.values():
        if (
            e.config_entry_id == entry.entry_id
            and e.platform == DOMAIN
            and "askoheat_08" in (e.entity_id or "")
        ):
            migrated = e
            break

    assert migrated is not None
    # ensure no raw colons remain in entity_id/unique_id
    assert ":" not in (migrated.entity_id or "")
    assert ":" not in (migrated.unique_id or "")
    # expect the object id suffix remains (test_sensor)
    assert (migrated.entity_id or "").endswith("_test_sensor")


async def test_deterministic_entity_id(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,  # noqa: ARG001
) -> None:
    """Ensure the integration creates deterministic, slugified entity_ids."""
    # Validate one of the entities loaded by the integration uses slugified id
    # For example a time entity from test fixtures
    # Look up one entity created by the integration and assert no colons
    entities = [
        e for e in hass.states.async_all() if e.entity_id.startswith("time.test_")
    ]
    assert entities
    for e in entities:
        assert ":" not in e.entity_id
