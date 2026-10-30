"""Config flow for Attribute as Sensor integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

import probatio

from homeassistant.components.sensor import CONF_STATE_CLASS
from homeassistant.const import (
    CONF_ATTRIBUTE,
    CONF_DEVICE_CLASS,
    CONF_ENTITY_CATEGORY,
    CONF_ENTITY_ID,
    CONF_ICON,
    CONF_NAME,
    CONF_UNIT_OF_MEASUREMENT,
    CONF_VALUE_TEMPLATE,
    EntityCategory,
    Platform,
)
from homeassistant.helpers import selector
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaCommonFlowHandler,
    SchemaConfigFlowHandler,
    SchemaFlowFormStep,
    SchemaFlowMenuStep,
)

from .const import DOMAIN

CONFIG_SCHEMA = probatio.Schema(
    {
        probatio.Required(CONF_NAME): selector.TextSelector(),
        probatio.Required(CONF_ENTITY_ID): selector.EntitySelector(
            selector.EntitySelectorConfig(multiple=False),
        ),
    }
)

OPTIONS_SCHEMA = probatio.Schema(
    {
        probatio.Optional(CONF_VALUE_TEMPLATE): selector.TemplateSelector(),
        probatio.Optional(CONF_ICON): selector.IconSelector(),
        probatio.Optional(CONF_DEVICE_CLASS): selector.DeviceClassSelector(
            selector.DeviceClassSelectorConfig(domain=Platform.SENSOR)
        ),
        probatio.Optional(CONF_STATE_CLASS): selector.StateClassSelector(),
        probatio.Optional(CONF_UNIT_OF_MEASUREMENT): selector.UnitOfMeasurementSelector(
            selector.UnitOfMeasurementSelectorConfig(
                context={
                    "filter_device_class": CONF_DEVICE_CLASS,
                    "filter_state_class": CONF_STATE_CLASS,
                }
            )
        ),
        # Sensors can't use the config category
        probatio.Optional(CONF_ENTITY_CATEGORY): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[EntityCategory.DIAGNOSTIC],
                mode=selector.SelectSelectorMode.DROPDOWN,
                translation_key="entity_category",
            )
        ),
    }
)


async def attribute_schema(handler: SchemaCommonFlowHandler) -> probatio.Schema:
    """Return schema for selecting attribute for entity."""
    options = handler.options.copy()
    return handler.parent_handler.add_suggested_values_to_schema(
        probatio.Schema(
            {
                probatio.Required(CONF_ATTRIBUTE): selector.AttributeSelector(
                    selector.AttributeSelectorConfig(entity_id=options[CONF_ENTITY_ID])
                ),
            }
        ).extend(OPTIONS_SCHEMA.schema),
        options,
    )


CONFIG_FLOW: dict[str, SchemaFlowFormStep | SchemaFlowMenuStep] = {
    "user": SchemaFlowFormStep(CONFIG_SCHEMA, next_step="attr"),
    "attr": SchemaFlowFormStep(attribute_schema),
}
OPTIONS_FLOW: dict[str, SchemaFlowFormStep | SchemaFlowMenuStep] = {
    "init": SchemaFlowFormStep(attribute_schema)
}


class ConfigFlowHandler(SchemaConfigFlowHandler, domain=DOMAIN):
    """Handle a config or options flow for Attribute as Entity."""

    MINOR_VERSION = 2

    config_flow = CONFIG_FLOW
    options_flow = OPTIONS_FLOW
    options_flow_reloads = True

    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        """Return config entry title."""
        return cast(str, options["name"]) if "name" in options else ""
