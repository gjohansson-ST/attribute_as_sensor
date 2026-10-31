"""Tests for the Attribute as Sensor config flow."""

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.attribute_as_sensor.const import DOMAIN
from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from .conftest import SENSOR_ENTITY_ID, SOURCE_ENTITY_ID


async def test_user_flow(hass: HomeAssistant) -> None:
    """Test creating a helper through the config flow."""
    hass.states.async_set(SOURCE_ENTITY_ID, "on", {"temperature": 21.5})

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"name": "Temperature", "entity_id": SOURCE_ENTITY_ID}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "attr"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "attribute": "temperature",
            "device_class": "temperature",
            "state_class": "measurement",
            "unit_of_measurement": "°C",
        },
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Temperature"
    assert result["options"] == {
        "name": "Temperature",
        "entity_id": SOURCE_ENTITY_ID,
        "attribute": "temperature",
        "device_class": "temperature",
        "state_class": "measurement",
        "unit_of_measurement": "°C",
    }
    assert hass.states.get(SENSOR_ENTITY_ID).state == "21.5"


async def test_options_flow(hass: HomeAssistant, loaded_entry: MockConfigEntry) -> None:
    """Test changing the options reloads the sensor with the new options."""
    hass.states.async_set(SOURCE_ENTITY_ID, "on", {"temperature": 21.5, "humidity": 40})

    result = await hass.config_entries.options.async_init(loaded_entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"attribute": "humidity", "unit_of_measurement": "%"}
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert loaded_entry.options == {
        "name": "Temperature",
        "entity_id": SOURCE_ENTITY_ID,
        "attribute": "humidity",
        "unit_of_measurement": "%",
    }
    state = hass.states.get(SENSOR_ENTITY_ID)
    assert state.state == "40"
    assert state.attributes["unit_of_measurement"] == "%"
