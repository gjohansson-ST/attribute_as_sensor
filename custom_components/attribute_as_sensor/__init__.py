"""The Attribute as Sensor component."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ENTITY_ID, CONF_VALUE_TEMPLATE
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError, TemplateError
from homeassistant.helpers.device import (
    async_remove_stale_devices_links_keep_entity_device,
)
from homeassistant.helpers.template import Template

from .const import PLATFORMS


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Attribute as sensor from a config entry."""

    async_remove_stale_devices_links_keep_entity_device(
        hass,
        entry.entry_id,
        entry.options[CONF_ENTITY_ID],
    )

    if value_template := entry.options.get(CONF_VALUE_TEMPLATE):
        value_template = Template(value_template, hass)
        try:
            value_template.ensure_valid()
        except TemplateError as ex:
            raise ConfigEntryError from ex

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(config_entry_update_listener))

    return True


async def config_entry_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener, called when the config entry options are changed."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
