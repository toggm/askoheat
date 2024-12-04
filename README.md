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
- Write services to write values back to aksoheat+ device with the convertion needed manually
- all registers listed in the modbus are queried independantly, even if it would be possible to scan all the states in one shot

This integration provides support for the following modbus register data blocks defined by the manufacturer and queries all states of a data block with a single query using different predefined scan_intervals:
| Data block | Scan interval |
| --------------------- | ---------------------------------------------------- |
| [Energymanager Block](http://www.download.askoma.com/askofamily_plus/modbus/askoheat-modbus.html#EM_Block)| Polls every 5 seconds for state changes |
| [Paramter Block](http://www.download.askoma.com/askofamily_plus/modbus/askoheat-modbus.html#Parameter_Block) | Read registers once on startup |
| [Configuration Block](http://www.download.askoma.com/askofamily_plus/modbus/askoheat-modbus.html#Configuration_Block)| Polls registers once an hour |
| [Data Values Block](http://www.download.askoma.com/askofamily_plus/modbus/askoheat-modbus.html#Data_Values_Block) | Polls registers once a minute |

Some of the states are exposed in more than one data block and are therefore integrated only once.

## Device units

All the entities created by this integration are assigned to one of the following device units through which you can filter out not needed states based on the local Askoheat water boiler setup:
| Device unit           | Description |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Water heater          | Required. Entities related to core water heater sensors and configuration parameters |
| Energy manager        | Required. Entities related to controlling the water heater through Home assistant as energy manager (i.e. load feed-in, etc.) |
| Analog input          | Optional. Exposes entities related to contrlling the askoheat+ water heater through analog input |
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
| switch.askoheat_{serial_number}_auto_feedin        | Switch to enable auto feed-in mode. Will observe the power entity and send changes continously to the askoheat device |


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

#### Manual

If you are using multiple askoheat devices, you're using a different hostname or work with static ip addresses you have to add your device manually.

To add the heatpump manually go to `Settings -> Devices & services -> Add integration` and add a new Adkoheat+ device.'

Provide correct hostname and configure the additional device units you want to be created and monitored through this integration.

> ℹ️ If you access you're device by IP address, ensure the IP address is static. This can be configured in your router.

## Removing the integration

This integration follows standard integration removal. No extra steps are required.

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

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
