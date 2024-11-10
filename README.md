[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge&cacheSeconds=3600)](https://github.com/hacs/integration)
[![size_badge](https://img.shields.io/github/repo-size/gjohansson-ST/attribute_as_sensor?style=for-the-badge&cacheSeconds=3600)](https://github.com/gjohansson-ST/attribute_as_sensor)
[![version_badge](https://img.shields.io/github/v/release/gjohansson-ST/attribute_as_sensor?label=Latest%20release&style=for-the-badge&cacheSeconds=3600)](https://github.com/gjohansson-ST/attribute_as_sensor/releases/latest)
[![download_badge](https://img.shields.io/github/downloads/gjohansson-ST/attribute_as_sensor/total?style=for-the-badge&cacheSeconds=3600)](https://github.com/gjohansson-ST/attribute_as_sensor/releases/latest)


# Home Assistant create an entities attribute as it's own sensor
---
**Title:** "Attribute as Sensor"

**Description:** "Create an entity from another entities attribute."

**Version:** 1.4

**Date created:** 2023-11-19

**Last update:** 2024-11-10

**Join the Discussion on Development:** [https://discord.gg/qyBhBArwHN](https://discord.gg/qyBhBArwHN)

---

## Configuration Options

### Set once

- Name: Name of the new entity
- Entity: From which entity you want to get the attribute
- Attribute: Which attribute you want as it's own sensor

### Options that you can change at any time

- Value template: Use a template to manipulate the retrieved attribute from the source entity
- Icon: Icon to use in frontend
- Device class: Device class (select from list)
- State class: State class (select from list)
- Unit of measurement: UoM to use in frontend (select from list, only temperature, or write your own)

## Installation

### Option 1 (preferred)

Use [HACS](https://hacs.xyz/) to install
Add as [custom repository](https://hacs.xyz/docs/faq/custom_repositories) to HACS

### Option 2

1. Below config-folder create a new folder called`custom_components` if not already exist.
2. Below new `custom_components` folder create a new folder called `attribute_as_sensor`
3. Upload the files/folders in `custom_components/attribute_as_sensor` directory to the newly created folder.
4. Restart before proceeding

## Activate integration in HA

[![Add integrations](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=attribute_as_sensor)

After installation go to "Devices & services" and then "helper" page in HA, press "+ Create helper" and find "Attribute as Sensor"
Follow onscreen information for the required information
No restart needed

## Contributions are more than welcome

If not for code, maybe add a language file for your language.