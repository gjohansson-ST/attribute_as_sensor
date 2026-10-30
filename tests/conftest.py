"""Fixtures for Attribute as Sensor tests."""

from typing import Any

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.attribute_as_sensor.const import DOMAIN
from homeassistant.core import HomeAssistant

SOURCE_ENTITY_ID = "sensor.source"
SENSOR_ENTITY_ID = "sensor.temperature"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Enable custom integrations in all tests."""


@pytest.fixture
def options() -> dict[str, Any]:
    """Return the options of the config entry."""
    return {
        "name": "Temperature",
        "entity_id": SOURCE_ENTITY_ID,
        "attribute": "temperature",
    }


@pytest.fixture
def config_entry(options: dict[str, Any]) -> MockConfigEntry:
    """Return a config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title=options["name"],
        options=options,
        version=1,
        minor_version=2,
    )


@pytest.fixture
async def loaded_entry(
    hass: HomeAssistant, config_entry: MockConfigEntry
) -> MockConfigEntry:
    """Set up the integration with a source entity."""
    hass.states.async_set(SOURCE_ENTITY_ID, "on", {"temperature": 21.5})
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    return config_entry
