"""Tests for the Attribute as Sensor sensor."""

from typing import Any

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.attribute_as_sensor.const import DOMAIN
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .conftest import SENSOR_ENTITY_ID, SOURCE_ENTITY_ID


@pytest.mark.usefixtures("loaded_entry")
async def test_sensor_follows_attribute(hass: HomeAssistant) -> None:
    """Test the sensor follows the attribute of the source entity."""
    state = hass.states.get(SENSOR_ENTITY_ID)
    assert state.state == "21.5"
    assert state.attributes["entity_id"] == SOURCE_ENTITY_ID

    hass.states.async_set(SOURCE_ENTITY_ID, "on", {"temperature": 22})
    await hass.async_block_till_done()

    assert hass.states.get(SENSOR_ENTITY_ID).state == "22"


@pytest.mark.usefixtures("loaded_entry")
@pytest.mark.parametrize(
    ("source_state", "source_attributes"),
    [
        pytest.param(STATE_UNAVAILABLE, {"temperature": 22}, id="unavailable"),
        pytest.param(STATE_UNKNOWN, {"temperature": 22}, id="unknown"),
        pytest.param("on", {"humidity": 40}, id="missing_attribute"),
    ],
)
async def test_sensor_unavailable(
    hass: HomeAssistant, source_state: str, source_attributes: dict[str, Any]
) -> None:
    """Test the sensor is unavailable when the attribute can't be read."""
    hass.states.async_set(SOURCE_ENTITY_ID, source_state, source_attributes)
    await hass.async_block_till_done()

    assert hass.states.get(SENSOR_ENTITY_ID).state == STATE_UNAVAILABLE

    hass.states.async_set(SOURCE_ENTITY_ID, "on", {"temperature": 22})
    await hass.async_block_till_done()

    assert hass.states.get(SENSOR_ENTITY_ID).state == "22"


@pytest.mark.usefixtures("loaded_entry")
@pytest.mark.parametrize(
    "options",
    [
        {
            "name": "Temperature",
            "entity_id": SOURCE_ENTITY_ID,
            "attribute": "temperature",
            "value_template": "{{ (value | float * 10) | int }}",
        }
    ],
)
async def test_value_template(hass: HomeAssistant) -> None:
    """Test the value template is applied to the attribute."""
    assert hass.states.get(SENSOR_ENTITY_ID).state == "215"


@pytest.mark.usefixtures("loaded_entry")
@pytest.mark.parametrize(
    "options",
    [
        {
            "name": "Temperature",
            "entity_id": SOURCE_ENTITY_ID,
            "attribute": "temperature",
            "icon": "mdi:thermometer",
            "device_class": "temperature",
            "state_class": "measurement",
            "unit_of_measurement": "°C",
            "entity_category": "diagnostic",
        }
    ],
)
async def test_sensor_options(
    hass: HomeAssistant, entity_registry: er.EntityRegistry
) -> None:
    """Test the options are set on the sensor."""
    state = hass.states.get(SENSOR_ENTITY_ID)
    assert state.attributes["icon"] == "mdi:thermometer"
    assert state.attributes["device_class"] == "temperature"
    assert state.attributes["state_class"] == "measurement"
    assert state.attributes["unit_of_measurement"] == "°C"
    assert (
        entity_registry.async_get(SENSOR_ENTITY_ID).entity_category
        is EntityCategory.DIAGNOSTIC
    )


async def test_sensor_linked_to_source_device(
    hass: HomeAssistant,
    device_registry: dr.DeviceRegistry,
    entity_registry: er.EntityRegistry,
    config_entry: MockConfigEntry,
) -> None:
    """Test the sensor is linked to the device of the source entity."""
    source_config_entry = MockConfigEntry(domain="test")
    source_config_entry.add_to_hass(hass)
    device = device_registry.async_get_or_create(
        config_entry_id=source_config_entry.entry_id,
        identifiers={("test", "device")},
    )
    entity_registry.async_get_or_create(
        "sensor",
        "test",
        "unique",
        suggested_object_id="source",
        device_id=device.id,
        config_entry=source_config_entry,
    )
    hass.states.async_set(SOURCE_ENTITY_ID, "on", {"temperature": 21.5})
    config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # The device name is part of the entity ID, so look the sensor up by unique ID
    entity_id = entity_registry.async_get_entity_id(
        "sensor", DOMAIN, config_entry.entry_id
    )
    assert entity_registry.async_get(entity_id).device_id == device.id
    assert device_registry.async_get(device.id).config_entry_id == (
        source_config_entry.entry_id
    )
