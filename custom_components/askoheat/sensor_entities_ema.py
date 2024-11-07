"""Predefined energy managementt askoheat sensors."""

from homeassistant.components.sensor.const import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfElectricPotential, UnitOfPower, UnitOfTemperature

from custom_components.askoheat.const import SensorEMAAttrKey
from custom_components.askoheat.model import AskoheatSensorEntityDescription

EMA_SENSOR_ENTITY_DESCRIPTIONS = (
    AskoheatSensorEntityDescription(
        key=SensorEMAAttrKey.ANALOG_INPUT_VALUE,
        translation_key=SensorEMAAttrKey.ANALOG_INPUT_VALUE,
        icon="mdi:gauge",
        native_precision=0,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
    ),
    AskoheatSensorEntityDescription(
        key=SensorEMAAttrKey.HEATER_LOAD,
        translation_key=SensorEMAAttrKey.HEATER_LOAD,
        icon="mdi:lightning-bold",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    AskoheatSensorEntityDescription(
        key=SensorEMAAttrKey.LOAD_FEEDIN_VALUE,
        translation_key=SensorEMAAttrKey.LOAD_FEEDIN_VALUE,
        icon="mdi:solar-power",
        native_precision=0,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    AskoheatSensorEntityDescription(
        key=SensorEMAAttrKey.LOAD_SETPOINT_VALUE,
        translation_key=SensorEMAAttrKey.LOAD_SETPOINT_VALUE,
        icon="mdi:lightning-bolt",
        native_precision=0,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    AskoheatSensorEntityDescription(
        key=SensorEMAAttrKey.INTERNAL_TEMPERATUR_SENSOR_VALUE,
        translation_key=SensorEMAAttrKey.INTERNAL_TEMPERATUR_SENSOR_VALUE,
        icon="mdi:thermometer",
        native_precision=1,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    AskoheatSensorEntityDescription(
        key=SensorEMAAttrKey.EXTERNAL_TEMPERATUR_SENSOR1_VALUE,
        translation_key=SensorEMAAttrKey.EXTERNAL_TEMPERATUR_SENSOR1_VALUE,
        icon="mdi:thermometer",
        native_precision=1,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    AskoheatSensorEntityDescription(
        key=SensorEMAAttrKey.EXTERNAL_TEMPERATUR_SENSOR2_VALUE,
        translation_key=SensorEMAAttrKey.EXTERNAL_TEMPERATUR_SENSOR2_VALUE,
        icon="mdi:thermometer",
        native_precision=1,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    AskoheatSensorEntityDescription(
        key=SensorEMAAttrKey.EXTERNAL_TEMPERATUR_SENSOR3_VALUE,
        translation_key=SensorEMAAttrKey.EXTERNAL_TEMPERATUR_SENSOR3_VALUE,
        icon="mdi:thermometer",
        native_precision=1,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    AskoheatSensorEntityDescription(
        key=SensorEMAAttrKey.EXTERNAL_TEMPERATUR_SENSOR4_VALUE,
        translation_key=SensorEMAAttrKey.EXTERNAL_TEMPERATUR_SENSOR4_VALUE,
        icon="mdi:thermometer",
        native_precision=1,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
)
