"""Predefined energy managementt askoheat sensors."""

from homeassistant.components.binary_sensor import BinarySensorDeviceClass

from custom_components.askoheat.const import BinarySensorAttrKey
from custom_components.askoheat.model import AskoheatBinarySensorEntityDescription

EMA_BINARY_SENSOR_ENTITY_DESCRIPTIONS = (
    AskoheatBinarySensorEntityDescription(
        key=BinarySensorAttrKey.HEATER1_ACTIVE,
        icon="mdi:power-plug",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    AskoheatBinarySensorEntityDescription(
        key=BinarySensorAttrKey.HEATER2_ACTIVE,
        icon="mdi:power-plug",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    AskoheatBinarySensorEntityDescription(
        key=BinarySensorAttrKey.HEATER3_ACTIVE,
        icon="mdi:power-plug",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    AskoheatBinarySensorEntityDescription(
        key=BinarySensorAttrKey.PUMP_ACTIVE,
        icon="mdi:pump",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    AskoheatBinarySensorEntityDescription(
        key=BinarySensorAttrKey.RELAY_BOARD_CONNECTED,
        icon="mdi:connection",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    AskoheatBinarySensorEntityDescription(
        key=BinarySensorAttrKey.HEAT_PUMP_REQUEST_ACTIVE,
        icon="mdi:heat-pump",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    AskoheatBinarySensorEntityDescription(
        key=BinarySensorAttrKey.EMERGENCY_MODE_ACTIVE,
        icon="mdi:car-emergency",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    AskoheatBinarySensorEntityDescription(
        key=BinarySensorAttrKey.LEGIONELLA_PROTECTION_ACTIVE,
        icon="mdi:shield-sun",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    AskoheatBinarySensorEntityDescription(
        key=BinarySensorAttrKey.ANALOG_INPUT_ACTIVE,
        icon="mdi:sine-wave",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    AskoheatBinarySensorEntityDescription(
        key=BinarySensorAttrKey.SETPOINT_ACTIVE,
        icon="mdi:finance",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    AskoheatBinarySensorEntityDescription(
        key=BinarySensorAttrKey.LOAD_FEEDIN_ACTIVE,
        icon="mdi:solar-power",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    AskoheatBinarySensorEntityDescription(
        key=BinarySensorAttrKey.AUTOHEATER_ACTIVE,
        icon="mdi:water-boiler-auto",
        inverted=True,
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    AskoheatBinarySensorEntityDescription(
        key=BinarySensorAttrKey.PUMP_RELAY_FOLLOW_UP_TIME_ACTIVE,
        icon="mdi:water-boiler-auto",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    AskoheatBinarySensorEntityDescription(
        key=BinarySensorAttrKey.TEMP_LIMIT_REACHED,
        icon="mdi:water-boiler-auto",
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    AskoheatBinarySensorEntityDescription(
        key=BinarySensorAttrKey.ERROR_OCCURED,
        icon="mdi:water-thermometer",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
)
