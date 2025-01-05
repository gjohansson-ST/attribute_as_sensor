"""Config flow for Attribute as Sensor integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

import voluptuous as vol
from homeassistant.components.sensor import (
    CONF_STATE_CLASS,
    CONF_UNIT_OF_MEASUREMENT,
    DEVICE_CLASSES,
    STATE_CLASSES,
)
from homeassistant.const import (
    CONF_ATTRIBUTE,
    CONF_DEVICE_CLASS,
    CONF_ENTITY_ID,
    CONF_ICON,
    CONF_NAME,
    CONF_VALUE_TEMPLATE,
    UnitOfTemperature,
)
from homeassistant.helpers import selector
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaCommonFlowHandler,
    SchemaConfigFlowHandler,
    SchemaFlowFormStep,
    SchemaFlowMenuStep,
)

from .const import DOMAIN

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): selector.TextSelector(),
        vol.Required(CONF_ENTITY_ID): selector.EntitySelector(
            selector.EntitySelectorConfig(multiple=False),
        ),
    }
)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_VALUE_TEMPLATE): selector.TemplateSelector(),
        vol.Optional(CONF_ICON): selector.IconSelector(),
        vol.Optional(CONF_DEVICE_CLASS): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=DEVICE_CLASSES, mode=selector.SelectSelectorMode.DROPDOWN
            )
        ),
        vol.Optional(CONF_STATE_CLASS): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=STATE_CLASSES, mode=selector.SelectSelectorMode.DROPDOWN
            )
        ),
        vol.Optional(CONF_UNIT_OF_MEASUREMENT): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[UnitOfTemperature.CELSIUS, UnitOfTemperature.FAHRENHEIT],
                custom_value=True,
            )
        ),
    }
)


async def attribute_schema(handler: SchemaCommonFlowHandler) -> vol.Schema:
    """Return schema for selecting attribute for entity."""
    options = handler.options.copy()

    return vol.Schema(
        {
            vol.Required(CONF_ATTRIBUTE): selector.AttributeSelector(
                selector.AttributeSelectorConfig(entity_id=options[CONF_ENTITY_ID])
            ),
        }
    ).extend(OPTIONS_SCHEMA.schema)


CONFIG_FLOW: dict[str, SchemaFlowFormStep | SchemaFlowMenuStep] = {
    "user": SchemaFlowFormStep(CONFIG_SCHEMA, next_step="attr"),
    "attr": SchemaFlowFormStep(attribute_schema),
}
OPTIONS_FLOW: dict[str, SchemaFlowFormStep | SchemaFlowMenuStep] = {
    "init": SchemaFlowFormStep(OPTIONS_SCHEMA)
}


class ConfigFlowHandler(SchemaConfigFlowHandler, domain=DOMAIN):
    """Handle a config or options flow for Attribute as Entity."""

    config_flow = CONFIG_FLOW
    options_flow = OPTIONS_FLOW

    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        """Return config entry title."""
        return cast(str, options["name"]) if "name" in options else ""
