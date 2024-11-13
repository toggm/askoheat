"""Predefined energy managementt askoheat sensors."""

from homeassistant.components.sensor.const import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfElectricPotential,
    UnitOfPower,
    UnitOfTemperature,
)

from custom_components.askoheat.const import SensorAttrKey
from custom_components.askoheat.model import AskoheatSensorEntityDescription

EMA_SENSOR_ENTITY_DESCRIPTIONS = (
    AskoheatSensorEntityDescription(
        key=SensorAttrKey.ANALOG_INPUT_VALUE,
        icon="mdi:gauge",
        native_precision=0,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        entity_category=None,
    ),
    AskoheatSensorEntityDescription(
        key=SensorAttrKey.HEATER_LOAD,
        icon="mdi:lightning-bolt",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        entity_category=None,
    ),
    AskoheatSensorEntityDescription(
        key=SensorAttrKey.LOAD_FEEDIN_VALUE,
        icon="mdi:solar-power",
        native_precision=0,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        entity_category=None,
    ),
    AskoheatSensorEntityDescription(
        key=SensorAttrKey.LOAD_SETPOINT_VALUE,
        icon="mdi:lightning-bolt",
        native_precision=0,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        entity_category=None,
    ),
    AskoheatSensorEntityDescription(
        key=SensorAttrKey.INTERNAL_TEMPERATUR_SENSOR_VALUE,
        icon="mdi:thermometer",
        native_precision=1,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_category=None,
    ),
    AskoheatSensorEntityDescription(
        key=SensorAttrKey.EXTERNAL_TEMPERATUR_SENSOR1_VALUE,
        icon="mdi:thermometer",
        native_precision=1,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_category=None,
    ),
    AskoheatSensorEntityDescription(
        key=SensorAttrKey.EXTERNAL_TEMPERATUR_SENSOR2_VALUE,
        icon="mdi:thermometer",
        native_precision=1,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_category=None,
    ),
    AskoheatSensorEntityDescription(
        key=SensorAttrKey.EXTERNAL_TEMPERATUR_SENSOR3_VALUE,
        icon="mdi:thermometer",
        native_precision=1,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_category=None,
    ),
    AskoheatSensorEntityDescription(
        key=SensorAttrKey.EXTERNAL_TEMPERATUR_SENSOR4_VALUE,
        icon="mdi:thermometer",
        native_precision=1,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_category=None,
    ),
)
