"""Tests to ensure slugify produces valid Home Assistant entity id components."""

import re

from homeassistant.util import slugify


def test_slugify_allowed_characters() -> None:
    """Ensure slugify produces only valid characters for entity ids."""
    samples = [
        "08:d1:f9:c4:6b:48",
        "My Device Name",
        "Device-Name/With.Slashes",
        "ÄÖÜ äöü é",
        "device_with_underscores",
    ]

    pattern = re.compile(r"^[a-z0-9_]+$")
    for s in samples:
        out = slugify(s)
        assert out == out.lower()
        assert pattern.match(out), f"slugify output contains invalid chars: {out!r}"


def test_entity_id_format_from_slug() -> None:
    """Ensure slugify output can be used to construct valid entity ids."""
    domain = "number"
    device_uid = "08:d1:f9:c4:6b:48"
    key = "relay_switch_on_inhibit_seconds"

    slug = slugify(device_uid)
    unique_id = f"{slug}_{key}"
    entity_id = f"{domain}.{unique_id}"

    # entity id must be domain.object_id where both parts contain only
    # lowercase letters, numbers and underscores
    assert re.match(r"^[a-z0-9_]+\.[a-z0-9_]+$", entity_id)
