"""Support for displaying attributes as Sensor."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    CONF_STATE_CLASS,
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_ATTRIBUTE,
    CONF_DEVICE_CLASS,
    CONF_ENTITY_ID,
    CONF_ICON,
    CONF_UNIT_OF_MEASUREMENT,
    CONF_VALUE_TEMPLATE,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import Event, HomeAssistant, State, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device import async_device_info_to_link_from_entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_state_report_event,
)
from homeassistant.helpers.template import Template

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize config entry."""
    registry = er.async_get(hass)
    entity_id = er.async_validate_entity_id(
        registry, config_entry.options[CONF_ENTITY_ID]
    )
    attribute = config_entry.options[CONF_ATTRIBUTE]
    icon = config_entry.options.get(CONF_ICON)
    device_class = config_entry.options.get(CONF_DEVICE_CLASS)
    state_class = config_entry.options.get(CONF_STATE_CLASS)
    uom = config_entry.options.get(CONF_UNIT_OF_MEASUREMENT)

    if value_template := config_entry.options.get(CONF_VALUE_TEMPLATE):
        value_template = Template(value_template, hass)

    async_add_entities(
        [
            AttributeSensor(
                hass,
                entity_id,
                attribute,
                icon,
                device_class,
                state_class,
                uom,
                config_entry.title,
                config_entry.entry_id,
                value_template,
            )
        ]
    )


class AttributeSensor(SensorEntity):
    """Representation of an Attribute as Sensor sensor."""

    _attr_should_poll = False

    def __init__(
        self,
        hass: HomeAssistant,
        entity_id: str,
        attribute: str,
        icon: str | None,
        device_class: SensorDeviceClass | None,
        state_class: SensorStateClass | None,
        uom: str | None,
        name: str,
        unique_id: str | None,
        value_template: Template | None,
    ) -> None:
        """Initialize the sensor."""
        self._attr_unique_id = unique_id
        self._entity_id = entity_id
        self._attribute = attribute
        self._attr_name = name
        self._attr_device_info = async_device_info_to_link_from_entity(
            hass,
            entity_id,
        )

        self._attr_device_class = device_class
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = uom
        self._attr_state_class = state_class

        self._value_template = value_template

        self._has_logged = False

    async def async_added_to_hass(self) -> None:
        """Handle added to Hass."""
        self.async_on_remove(
            async_track_state_change_event(
                self.hass, self._entity_id, self._async_attribute_sensor_state_listener
            )
        )
        self.async_on_remove(
            async_track_state_report_event(
                self.hass, self._entity_id, self._async_attribute_sensor_state_listener
            )
        )

        # Replay current state of source entities
        state = self.hass.states.get(self._entity_id)
        state_event = Event("", {"entity_id": self._entity_id, "new_state": state})
        self._async_attribute_sensor_state_listener(state_event, update_state=False)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes of the sensor."""
        return {ATTR_ENTITY_ID: self._entity_id}

    @callback
    def _async_attribute_sensor_state_listener(
        self, event: Event, update_state: bool = True
    ) -> None:
        """Handle the sensor state changes."""
        new_state: State | None = event.data.get("new_state")
        _LOGGER.debug("Received new state: %s", new_state)

        self._attr_available = new_state != STATE_UNAVAILABLE

        self._attr_native_value = None
        if (
            new_state is None
            or new_state.state is None
            or new_state.state in [STATE_UNAVAILABLE, STATE_UNKNOWN]
        ):
            if not update_state:
                _LOGGER.debug("Ignoring state update")
                return

        if self._attribute not in new_state.attributes:
            if not self._has_logged:
                _LOGGER.error(
                    "Attribute (%s) not found in state attributes for entity %s",
                    self._attribute,
                    self._entity_id,
                )
            self._has_logged = True
            self._attr_native_value = STATE_UNAVAILABLE
            self.async_write_ha_state()
            return

        self._has_logged = False
        if new_state and self._attribute in new_state.attributes:
            _LOGGER.debug("State attributes: %s", new_state.attributes)

            value = new_state.attributes[self._attribute]
            if self._value_template is not None:
                value = self._value_template.async_render_with_possible_json_value(
                    new_state.attributes[self._attribute], None
                )
            self._attr_native_value = value
            _LOGGER.debug(
                "Setting attribute (%s) value: %s",
                self._attribute,
                self._attr_native_value,
            )

        self.async_write_ha_state()
        return
