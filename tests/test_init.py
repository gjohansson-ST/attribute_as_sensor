"""Tests for setting up Attribute as Sensor."""

from typing import Any

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.attribute_as_sensor.const import DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .conftest import SENSOR_ENTITY_ID, SOURCE_ENTITY_ID


async def test_setup_and_unload(
    hass: HomeAssistant, loaded_entry: MockConfigEntry
) -> None:
    """Test setting up and unloading a config entry."""
    assert loaded_entry.state is ConfigEntryState.LOADED
    assert hass.states.get(SENSOR_ENTITY_ID).state == "21.5"

    assert await hass.config_entries.async_unload(loaded_entry.entry_id)
    await hass.async_block_till_done()

    assert loaded_entry.state is ConfigEntryState.NOT_LOADED


@pytest.mark.parametrize(
    "options",
    [
        {
            "name": "Temperature",
            "entity_id": SOURCE_ENTITY_ID,
            "attribute": "temperature",
            "value_template": "{{ value | int ",
        }
    ],
)
async def test_invalid_template(
    hass: HomeAssistant, loaded_entry: MockConfigEntry
) -> None:
    """Test an invalid value template fails the setup."""
    assert loaded_entry.state is ConfigEntryState.SETUP_ERROR
    assert hass.states.get(SENSOR_ENTITY_ID) is None


async def test_migrate_minor_version(
    hass: HomeAssistant, options: dict[str, Any]
) -> None:
    """Test migrating a config entry from minor version 1."""
    hass.states.async_set(SOURCE_ENTITY_ID, "on", {"temperature": 21.5})
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Temperature",
        options=options,
        version=1,
        minor_version=1,
    )
    config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.state is ConfigEntryState.LOADED
    assert config_entry.minor_version == 2
    assert config_entry.options == options


async def test_source_entity_removed(
    hass: HomeAssistant, entity_registry: er.EntityRegistry, options: dict[str, Any]
) -> None:
    """Test the helper is removed when its source entity is removed."""
    source = entity_registry.async_get_or_create(
        "sensor", "test", "unique", suggested_object_id="source"
    )
    assert source.entity_id == SOURCE_ENTITY_ID
    hass.states.async_set(SOURCE_ENTITY_ID, "on", {"temperature": 21.5})
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Temperature",
        options=options,
        version=1,
        minor_version=2,
    )
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    entity_registry.async_remove(SOURCE_ENTITY_ID)
    await hass.async_block_till_done()

    assert hass.config_entries.async_get_entry(config_entry.entry_id) is None
