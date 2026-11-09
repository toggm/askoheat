# Askoheat+ integration

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Community Forum][forum-shield]][forum]

This integration integrates [Askoheat+ devices](http://www.download.askoma.com/askofamily_plus/modbus/askoheat-modbus.html) through modbus.

## There exist a modbus integration in home assistant core, why should I use this custom integration instead?

It's possible to integrate an Askoheat+ device using the core modbus integration but it's cumbersome as you will have to:

- Go through the list of read/write registers manually and pick the once's you'd like to integrate
- Map status registers through helpers to be able to map them to `binary_sensor` states
- Write services to write values back to aksoheat+ device with the conversion needed manually
- all registers listed in the modbus are queried independently, even if it would be possible to scan all the states in one shot

This integration provides support for the following modbus register data blocks defined by the manufacturer and queries all states of a data block with a single query using different predefined scan_intervals:
| Data block | Scan interval |
| --------------------- | ---------------------------------------------------- |
| [Energymanager Block](http://www.download.askoma.com/askofamily_plus/modbus/askoheat-modbus.html#EM_Block)| Polls every 5 seconds for state changes |
| [Parameter Block](http://www.download.askoma.com/askofamily_plus/modbus/askoheat-modbus.html#Parameter_Block) | Read registers once on startup |
| [Configuration Block](http://www.download.askoma.com/askofamily_plus/modbus/askoheat-modbus.html#Configuration_Block)| Polls registers once an hour |
| [Data Values Block](http://www.download.askoma.com/askofamily_plus/modbus/askoheat-modbus.html#Data_Values_Block) | Polls registers once a minute |

Some of the states are exposed in more than one data block and are therefore integrated only once.

## Device units

All the entities created by this integration are assigned to one of the following device units through which you can filter out not needed states based on the local Askoheat water boiler setup:
| Device unit           | Description |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Water heater          | Required. Entities related to core water heater sensors and configuration parameters |
| Energy manager        | Required. Entities related to controlling the water heater through Home assistant as energy manager (i.e. load feed-in, etc.) |
| Analog input          | Optional. Exposes entities related to controlling the askoheat+ water heater through analog input |
| Heatpump              | Optional. Exposes entities related to an integration with a connected heatpump sending heatpump requests |
| Legionalla protection | Optional. Exposes entities related to the integration legionalla protection mechanism |
| Modbus master         | Optional. Exposes entities to use the askoheat water heater as a modbus master connecting to other slave devices |

## Auto feed-in

To use HA to control auto feed-in (solar) mode of the askoheat device, a power sensor needs to be configured in the setup or later configuration of the device integration. An additional parameter
defines if the provided value of the configures power device should get inverted. If not, the askoheat device assumes negative values of the power entity if energy is fed back to the grid and could
be used to heat up the water instead.

In the energy manager device two additional entities are provided to enable controlling the auto feed-in support based.

| Entity Id Pattern                                  | Description |
| -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| number.askoheat_{serial_number}_auto_feedin_buffer | Buffer of feed-back energy use for short term loads. Will be added to the value of the energy fed back (assuming fead-back value has a negative value) |
| switch.askoheat_{serial_number}_auto_feedin        | Switch to enable auto feed-in mode. Will observe the power entity and send changes continuously to the askoheat device |

To enable the feed-in energy to heaten up the water boiler, you need additionally to enable the switch `switch.askoheat_{serial_number}_load_feedin_value_enabled` to directly use feed-in energy or `switch.askoheat_{serial_number}_legio_settings_prefer_feedin_energy` if you want to use the feed-in energy to use for legionelly protection only.

## 1. Installation

### 1.1 HACS (recommended)

Add the custom repo to HACS

1. Go to 'HACS > Integration'
2. Select 'Custom repositories' from the top right menu
3. Under Repository, enter '<https://github.com/toggm/askoheat>'
4. Under Category, select 'Integration'
5. Click 'Add'
   The new integration will appear as a new integration and under 'Explore & Download Repositories' in the bottom right

Install the integration

1. Click on the new integration or find it under 'Explore & Download Repositories' in the bottom right with the search word 'askoheat'.
2. Select 'download' at the bottom right.
3. Restart Home Assistant

### 1.2 Manual installation

Add the integration to Home Assistant

1. Download the latest release of the Askoheat integration from this repository
2. In Home Assistant, create a folder 'config/custom_components'
3. Add the Luxtronik integration to the 'custom_components' folder;
4. Restart Home Assistant;

Install the integration

1. Add the Askoheat integration to Home Assistant (`Settings -> Devices & services -> Add integration`);
2. Restart Home Assistant;

## 2. Adding an Askoheat+ device

#### Autodiscovery

Your askoheat device should be autodiscovered only if the device is using it's standard dhcp name `askoheat.local`.

Press `Configure` and follow the steps to the end by selecting the additional device units you want to be created and monitored through this integration.

A discovered device is recognised by its MAC address or serial number, never by its IP address or hostname. If it is already configured, the discovery is dropped and only the address of the existing device is updated if it changed. Devices which are not yet configured can be ignored with the `Ignore` button.

#### Manual

If you are using multiple askoheat devices, you're using a different hostname or work with static ip addresses you have to add your device manually.

To add the heatpump manually go to `Settings -> Devices & services -> Add integration` and add a new Adkoheat+ device.'

Provide correct hostname and configure the additional device units you want to be created and monitored through this integration.

> ℹ️ If you access you're device by IP address, ensure the IP address is static. This can be configured in your router.

## Removing the integration

This integration follows standard integration removal. No extra steps are required.

## Removing of a device unit
To be able to delete a device unit, you first need to deactivate the device unit in the integration. After deactivating the device unit can get deleted in the device
detail page.

> ℹ️ Be aware that the device units energy manager and water heater can't be deleted.

## Known limitations

It is currently not possible, to turn on the emergency mode through modbus.

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## Troubleshooting

### Sometimes the connection is lost
The hardware of the askoheat device seems to be very sensible. Check the network plug and the outlets for any damage or try a different outlet or cable.

### Cannot connect to the askoheat device after rebooting the device
Check that the device is either configured with a static IP address or your local DNS can still resolve the configured hostname.

## Examples

### Use solar power to heat up the water boiler
The askoheat device support a so called feed-in functionality. The device will itself start to heaten up the water in different power steps, depending on
the solar power fed back to the grid. The integration provides a switch which automatically forwards any changes of the solar power to the device.
As the device does figure out the maximum power level by slowly increasing the levels and checking the feed-in power, it might come to toggling on and off
the power shortly before sunset and after sunrise, you can define an automation which toggles the auto feed-in switch depending on the state of the sun
(i.e. toggle on an hour after sunrise, toggle off an hour before sunset).
More information are available [here](https://github.com/toggm/askoheat/discussions/10)

### Share your examples
Share your examples in the [discussion](https://github.com/toggm/askoheat/discussions/categories/show-and-tell) section

## Entity ids and migration (v1.2.1 and later)

### How entity ids are built
- Every entity gets an `entity_id` of the form `domain.<device id>_<entity key>`, e.g. `sensor.askoheat_xxc32t_heater1_power`. `<device id>` is the unique id of the config entry, which is `askoheat_` plus the serial number the device reports when it is added. Some devices report their MAC address (`a8:42:e3:da:a3:a0`) as serial number; it is slugified for the `entity_id` (`askoheat_a8_42_e3_da_a3_a0`).
- The `unique_id` of an entity (what Home Assistant uses to recognise it) is built from the *raw* device id, as in versions up to 1.1.1, and may therefore contain colons. This is valid. It must not change between versions, otherwise Home Assistant registers every entity a second time (`..._2`).
- The `entity_id` is only used when an entity is registered for the first time. Entities which exist already keep their `entity_id`, including ones you renamed yourself.

### What the integration migrates automatically
On the first start with v1.2.1 or later each config entry is migrated once (config entry version 2):
- **Coming from 1.1.1 or earlier:** nothing is renamed or removed.
- **Coming from 1.2.0 or 1.2.1-beta1** (entities duplicated with `_2`, or `unique_id`s rewritten): the `unique_id`s are restored to the original format. If the original entity still exists, the `_2` duplicate is removed and the original is used again, including its `entity_id`, history and customizations. The history the duplicate collected in between is lost.
- **Entities renamed by v1.2.0:** the mapping file `mappings_askoheat_<entry_id>.txt` in your configuration directory lists `old_entity_id new_entity_id`. Where possible the old `entity_id` is restored. Ids containing colons are invalid and cannot be restored.

Entries migrated to version 2 cannot be loaded by v1.2.0 or older. If you want to go back, restore a backup.

### If you still have duplicated or renamed entities
This happens if the device was removed and added again (it then gets a new device id, e.g. the MAC address instead of a readable name), or if the automatic migration cannot decide. You have three options.

**1. Rename the entities in the UI**
Settings -> Devices & services -> Askoheat -> select the device -> pencil icon -> enter the old name -> *Recreate entity IDs*. Home Assistant derives the ids from the device and entity names (in your language, e.g. `sensor.boiler_eg_stromverbrauch`). These differ from the ids used in the documentation, which are the English entity keys.

**2. Remove the new entities and keep the old ones**
Delete the unavailable (old) or duplicated (`_2`) entities in the UI, then rename the remaining ones, or use the script below.

**3. Batch clean-up and rename with the helper script**
[scripts/askoheat-registry](scripts/askoheat-registry) edits the Home Assistant registry files and only touches Askoheat entries. It needs [`jq`](https://jqlang.org/download/); check with `jq --version` and install it if it is missing:

| Where you run the script | Install `jq` |
| --- | --- |
| Home Assistant OS, in the *Terminal & SSH* / *Advanced SSH & Web Terminal* add-on (Alpine based) | `apk add jq` (for *Advanced SSH & Web Terminal* you can also list `jq` under *Packages* in the add-on configuration so it survives restarts) |
| Debian / Ubuntu / Raspberry Pi OS (Home Assistant Supervised or Container host) | `sudo apt install jq` |
| macOS (e.g. working on a copy of your configuration) | `brew install jq` |
| Anything else | download a binary from the [jq download page](https://jqlang.org/download/) |

**Stop Home Assistant before using `--apply`**, otherwise your changes are overwritten when it shuts down. Without `--apply` every command only prints what would change; with `--apply` a backup (`<file>.bak.<timestamp>`) is created first.

```bash
# show entities / devices (without a prefix all Askoheat entities are listed)
scripts/askoheat-registry -c /config list-entities
scripts/askoheat-registry -c /config list-entities askoheat_a8_42_e3_da_a3_a0
scripts/askoheat-registry -c /config list-devices "Boiler"

# remove entities with a given id prefix (dry run, add --apply to write)
scripts/askoheat-registry -c /config remove-entities askoheat_a8_42_e3_da_a3_a0

# remove a device including all its entities (e.g. a duplicated device)
scripts/askoheat-registry -c /config --apply remove-devices "Legionellen"

# rename the id prefix of all entities, e.g. back to the legacy name
scripts/askoheat-registry -c /config --apply rename-entities askoheat_a8_42_e3_da_a3_a0 boiler_eg

# rename devices
scripts/askoheat-registry -c /config --apply rename-devices "Boiler Einheit" "Boiler EG"
```

The prefix has to match the part of the id after the domain from its start, and you must give the complete prefix you want to replace (`askoheat_a8` would leave `_42_e3_...` behind). `rename-entities` stops if a target id already exists, so remove the duplicates first. It writes `askoheat_renames_<timestamp>.txt` into the configuration directory (`old new` per line).

### YAML automations, scripts and dashboards
Automations and dashboards created in the UI follow renames in the entity registry. Files in YAML are not changed. Use a mapping file with lines `old_entity_id new_entity_id` (written by the integration or by the script above) to replace the ids:

```bash
while read -r old new; do
   grep -RIl "$old" /config | xargs -r sed -i "s/$old/$new/g"
done < mappings.txt
```

---

[askoheat]: https://github.com/toggm/askoheat
[buymecoffee]: https://www.buymeacoffee.com/toggm
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/toggm/askoheat.svg?style=for-the-badge
[commits]: https://github.com/toggm/askoheat/commits/main
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/toggm/askoheat.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-toggm-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/toggm/askoheat.svg?style=for-the-badge
[releases]: https://github.com/toggm/askoheat/releases
