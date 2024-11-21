"""Operating block Api descriptor classes."""

# http://www.download.askoma.com/askofamily_plus/modbus/askoheat-modbus.html#Data_Values_Block
from __future__ import annotations

from homeassistant.components.sensor.const import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import EntityCategory, UnitOfTime

from custom_components.askoheat.api_desc import (
    ByteRegisterInputDescriptor,
    FlagRegisterInputDescriptor,
    RegisterBlockDescriptor,
    StructRegisterInputDescriptor,
    UnsignedInt16RegisterInputDescriptor,
    UnsignedInt32RegisterInputDescriptor,
)
from custom_components.askoheat.const import (
    BinarySensorAttrKey,
    DeviceKey,
    SensorAttrKey,
)
from custom_components.askoheat.model import (
    AskoheatBinarySensorEntityDescription,
    AskoheatDurationSensorEntityDescription,
    AskoheatSensorEntityDescription,
)

DATA_REGISTER_BLOCK_DESCRIPTOR = RegisterBlockDescriptor(
    starting_register=600,
    number_of_registers=98,
    sensors=[
        AskoheatDurationSensorEntityDescription(
            key=SensorAttrKey.DATA_OPERATING_TIME_MINUTES,
            api_descriptor=StructRegisterInputDescriptor(0, 2, ">L"),
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_unit_of_measurement=UnitOfTime.MINUTES,
            icon="mdi:progress-clock",
        ),
        AskoheatDurationSensorEntityDescription(
            key=SensorAttrKey.DATA_OPERATING_TIME_HEATER1_MINUTES,
            api_descriptor=StructRegisterInputDescriptor(2, 2, ">L"),
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_unit_of_measurement=UnitOfTime.MINUTES,
            icon="mdi:progress-clock",
        ),
        AskoheatDurationSensorEntityDescription(
            key=SensorAttrKey.DATA_OPERATING_TIME_HEATER2_MINUTES,
            api_descriptor=StructRegisterInputDescriptor(4, 2, ">L"),
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_unit_of_measurement=UnitOfTime.MINUTES,
            icon="mdi:progress-clock",
        ),
        AskoheatDurationSensorEntityDescription(
            key=SensorAttrKey.DATA_OPERATING_TIME_HEATER3_MINUTES,
            api_descriptor=StructRegisterInputDescriptor(6, 2, ">L"),
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_unit_of_measurement=UnitOfTime.MINUTES,
            icon="mdi:progress-clock",
        ),
        AskoheatDurationSensorEntityDescription(
            key=SensorAttrKey.DATA_OPERATING_TIME_PUMP_MINUTES,
            api_descriptor=StructRegisterInputDescriptor(8, 2, ">L"),
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_unit_of_measurement=UnitOfTime.MINUTES,
            icon="mdi:progress-clock",
        ),
        AskoheatDurationSensorEntityDescription(
            key=SensorAttrKey.DATA_OPERATING_TIME_VALVE_MINUTES,
            api_descriptor=StructRegisterInputDescriptor(10, 2, ">L"),
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_unit_of_measurement=UnitOfTime.MINUTES,
            icon="mdi:counter",
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.DATA_SWITCH_COUNT_RELAY1,
            api_descriptor=UnsignedInt32RegisterInputDescriptor(12),
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.TOTAL_INCREASING,
            entity_registry_enabled_default=False,
            icon="mdi:counter",
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.DATA_SWITCH_COUNT_RELAY2,
            api_descriptor=UnsignedInt32RegisterInputDescriptor(14),
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.TOTAL_INCREASING,
            entity_registry_enabled_default=False,
            icon="mdi:counter",
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.DATA_SWITCH_COUNT_RELAY3,
            api_descriptor=UnsignedInt32RegisterInputDescriptor(16),
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.TOTAL_INCREASING,
            entity_registry_enabled_default=False,
            icon="mdi:counter",
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.DATA_SWITCH_COUNT_RELAY4,
            api_descriptor=UnsignedInt32RegisterInputDescriptor(18),
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.TOTAL_INCREASING,
            entity_registry_enabled_default=False,
            icon="mdi:counter",
        ),
        AskoheatDurationSensorEntityDescription(
            key=SensorAttrKey.DATA_SINCE_LAST_LEGIO_ACTIVATION_MINUTES,
            api_descriptor=StructRegisterInputDescriptor(28, 2, ">L"),
            device_key=DeviceKey.LEGIO_PROTECTION_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTime.MINUTES,
            icon="mdi:progress-clock",
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.DATA_LEGIO_PLATEAU_TIMER,
            api_descriptor=UnsignedInt16RegisterInputDescriptor(30),
            device_key=DeviceKey.LEGIO_PROTECTION_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.DURATION,
            native_unit_of_measurement=UnitOfTime.SECONDS,
            icon="mdi:av-timer",
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.DATA_ANALOG_INPUT_STEP,
            api_descriptor=ByteRegisterInputDescriptor(39),
            device_key=DeviceKey.ANALOG_INPUT_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            native_min_value=0,
            native_max_value=7,
            icon="mdi:stairs",
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.DATA_ACTUAL_TEMP_LIMIT,
            api_descriptor=UnsignedInt16RegisterInputDescriptor(40),
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            native_min_value=0,
            native_max_value=99,
            icon="mdi:water-thermometer",
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.DATA_AUTO_HEATER_OFF_COUNTDOWN_MINUTES,
            api_descriptor=UnsignedInt32RegisterInputDescriptor(41),
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            native_min_value=0,
            native_max_value=1440,
            native_unit_of_measurement=UnitOfTime.MINUTES,
            icon="mdi:progress-clock",
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.DATA_EMERGENCY_OFF_COUNTDOWN_MINUTES,
            api_descriptor=UnsignedInt32RegisterInputDescriptor(43),
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            native_min_value=0,
            native_max_value=1440,
            native_unit_of_measurement=UnitOfTime.MINUTES,
            icon="mdi:progress-clock",
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.DATA_BOOT_COUNT,
            api_descriptor=UnsignedInt32RegisterInputDescriptor(45),
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.TOTAL_INCREASING,
            icon="mdi:counter",
        ),
        AskoheatDurationSensorEntityDescription(
            key=SensorAttrKey.DATA_OPERATING_TIME_SET_HEATER_STEP,
            api_descriptor=StructRegisterInputDescriptor(47, 2, ">L"),
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTime.MINUTES,
            icon="mdi:progress-clock",
        ),
        AskoheatDurationSensorEntityDescription(
            key=SensorAttrKey.DATA_OPERATING_TIME_LOAD_SETPOINT,
            api_descriptor=StructRegisterInputDescriptor(49, 2, ">L"),
            device_key=DeviceKey.ENERGY_MANAGER,
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTime.MINUTES,
            icon="mdi:progress-clock",
        ),
        AskoheatDurationSensorEntityDescription(
            key=SensorAttrKey.DATA_OPERATING_TIME_LOAD_FEEDIN,
            api_descriptor=StructRegisterInputDescriptor(51, 2, ">L"),
            device_key=DeviceKey.ENERGY_MANAGER,
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTime.MINUTES,
            icon="mdi:progress-clock",
        ),
        AskoheatDurationSensorEntityDescription(
            key=SensorAttrKey.DATA_OPERATING_TIME_HEATPUMP_REQUEST,
            api_descriptor=StructRegisterInputDescriptor(53, 2, ">L"),
            device_key=DeviceKey.HEATPUMP_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTime.MINUTES,
            icon="mdi:progress-clock",
        ),
        AskoheatDurationSensorEntityDescription(
            key=SensorAttrKey.DATA_OPERATING_TIME_ANALOG_INPUT,
            api_descriptor=StructRegisterInputDescriptor(55, 2, ">L"),
            device_key=DeviceKey.ANALOG_INPUT_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTime.MINUTES,
            icon="mdi:progress-clock",
        ),
        AskoheatDurationSensorEntityDescription(
            key=SensorAttrKey.DATA_OPERATING_TIME_EMERGENCY_MODE,
            api_descriptor=StructRegisterInputDescriptor(57, 2, ">L"),
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTime.MINUTES,
            icon="mdi:progress-clock",
        ),
        AskoheatDurationSensorEntityDescription(
            key=SensorAttrKey.DATA_OPERATING_TIME_LEGIO_PROTECTION,
            api_descriptor=StructRegisterInputDescriptor(59, 2, ">L"),
            device_key=DeviceKey.LEGIO_PROTECTION_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTime.MINUTES,
            icon="mdi:progress-clock",
        ),
        AskoheatDurationSensorEntityDescription(
            key=SensorAttrKey.DATA_OPERATING_TIME_LOW_TARIFF,
            api_descriptor=StructRegisterInputDescriptor(61, 2, ">L"),
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTime.MINUTES,
            icon="mdi:progress-clock",
        ),
        AskoheatDurationSensorEntityDescription(
            key=SensorAttrKey.DATA_OPERATING_TIME_MINIMAL_TEMP,
            api_descriptor=StructRegisterInputDescriptor(63, 2, ">L"),
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTime.MINUTES,
            icon="mdi:progress-clock",
        ),
        AskoheatDurationSensorEntityDescription(
            key=SensorAttrKey.DATA_OPERATING_TIME_HEATER_STEP1,
            api_descriptor=StructRegisterInputDescriptor(65, 2, ">L"),
            device_key=DeviceKey.ENERGY_MANAGER,
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTime.MINUTES,
            icon="mdi:progress-clock",
        ),
        AskoheatDurationSensorEntityDescription(
            key=SensorAttrKey.DATA_OPERATING_TIME_HEATER_STEP2,
            api_descriptor=StructRegisterInputDescriptor(67, 2, ">L"),
            device_key=DeviceKey.ENERGY_MANAGER,
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTime.MINUTES,
            icon="mdi:progress-clock",
        ),
        AskoheatDurationSensorEntityDescription(
            key=SensorAttrKey.DATA_OPERATING_TIME_HEATER_STEP3,
            api_descriptor=StructRegisterInputDescriptor(69, 2, ">L"),
            device_key=DeviceKey.ENERGY_MANAGER,
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTime.MINUTES,
            icon="mdi:progress-clock",
        ),
        AskoheatDurationSensorEntityDescription(
            key=SensorAttrKey.DATA_OPERATING_TIME_HEATER_STEP4,
            api_descriptor=StructRegisterInputDescriptor(71, 2, ">L"),
            device_key=DeviceKey.ENERGY_MANAGER,
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTime.MINUTES,
            icon="mdi:progress-clock",
        ),
        AskoheatDurationSensorEntityDescription(
            key=SensorAttrKey.DATA_OPERATING_TIME_HEATER_STEP5,
            api_descriptor=StructRegisterInputDescriptor(73, 2, ">L"),
            device_key=DeviceKey.ENERGY_MANAGER,
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTime.MINUTES,
            icon="mdi:progress-clock",
        ),
        AskoheatDurationSensorEntityDescription(
            key=SensorAttrKey.DATA_OPERATING_TIME_HEATER_STEP6,
            api_descriptor=StructRegisterInputDescriptor(75, 2, ">L"),
            device_key=DeviceKey.ENERGY_MANAGER,
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTime.MINUTES,
            icon="mdi:progress-clock",
        ),
        AskoheatDurationSensorEntityDescription(
            key=SensorAttrKey.DATA_OPERATING_TIME_HEATER_STEP7,
            api_descriptor=StructRegisterInputDescriptor(77, 2, ">L"),
            device_key=DeviceKey.ENERGY_MANAGER,
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfTime.MINUTES,
            icon="mdi:progress-clock",
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.DATA_COUNT_SET_HEATER_STEP,
            api_descriptor=UnsignedInt32RegisterInputDescriptor(79),
            device_key=DeviceKey.ENERGY_MANAGER,
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_min_value=0,
            native_max_value=100000,
            icon="mdi:counter",
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.DATA_COUNT_LOAD_SETPOINT,
            api_descriptor=UnsignedInt32RegisterInputDescriptor(81),
            device_key=DeviceKey.ENERGY_MANAGER,
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_min_value=0,
            native_max_value=100000,
            icon="mdi:counter",
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.DATA_COUNT_LOAD_FEEDIN,
            api_descriptor=UnsignedInt32RegisterInputDescriptor(83),
            device_key=DeviceKey.ENERGY_MANAGER,
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_min_value=0,
            native_max_value=100000,
            icon="mdi:counter",
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.DATA_COUNT_HEATPUMP_REQUEST,
            api_descriptor=UnsignedInt32RegisterInputDescriptor(85),
            device_key=DeviceKey.HEATPUMP_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_min_value=0,
            native_max_value=100000,
            icon="mdi:counter",
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.DATA_COUNT_ANALOG_INPUT,
            api_descriptor=UnsignedInt32RegisterInputDescriptor(87),
            device_key=DeviceKey.ANALOG_INPUT_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_min_value=0,
            native_max_value=100000,
            icon="mdi:counter",
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.DATA_COUNT_EMERGENCY_MODE,
            api_descriptor=UnsignedInt32RegisterInputDescriptor(89),
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_min_value=0,
            native_max_value=100000,
            icon="mdi:counter",
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.DATA_COUNT_LEGIO_PROTECTION,
            api_descriptor=UnsignedInt32RegisterInputDescriptor(91),
            device_key=DeviceKey.LEGIO_PROTECTION_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_min_value=0,
            native_max_value=100000,
            icon="mdi:counter",
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.DATA_COUNT_LOW_TARIFF,
            api_descriptor=UnsignedInt32RegisterInputDescriptor(93),
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_min_value=0,
            native_max_value=100000,
            icon="mdi:counter",
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.DATA_COUNT_MINIMAL_TEMP,
            api_descriptor=UnsignedInt32RegisterInputDescriptor(95),
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_min_value=0,
            native_max_value=100000,
            icon="mdi:counter",
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.DATA_MAX_MEASURED_TEMP,
            api_descriptor=ByteRegisterInputDescriptor(97),
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            entity_category=EntityCategory.DIAGNOSTIC,
            state_class=SensorStateClass.MEASUREMENT,
            native_min_value=0,
            native_max_value=255,
            icon="mdi:thermometer-high",
        ),
    ],
    binary_sensors=[
        # legio status flags
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.DATA_LEGIO_STATUS_HEATING_UP,
            api_descriptor=FlagRegisterInputDescriptor(27, 0),
            icon="mdi:thermometer-chevron-up",
            entity_category=EntityCategory.DIAGNOSTIC,
            device_key=DeviceKey.LEGIO_PROTECTION_CONTROL_UNIT,
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.DATA_LEGIO_STATUS_TEMPERATURE_REACHED,
            api_descriptor=FlagRegisterInputDescriptor(27, 1),
            icon="mdi:thermometer-check",
            entity_category=EntityCategory.DIAGNOSTIC,
            device_key=DeviceKey.LEGIO_PROTECTION_CONTROL_UNIT,
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.DATA_LEGIO_STATUS_TEMP_REACHED_OUTSIDE_INTERVAL,
            api_descriptor=FlagRegisterInputDescriptor(27, 2),
            icon="mdi:thermometer-check",
            entity_category=EntityCategory.DIAGNOSTIC,
            device_key=DeviceKey.LEGIO_PROTECTION_CONTROL_UNIT,
        ),
        # bit 3 ignored
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.DATA_LEGIO_STATUS_UNEXPECTED_TEMP_DROP,
            api_descriptor=FlagRegisterInputDescriptor(27, 4),
            icon="mdi:alert-circle",
            entity_category=EntityCategory.DIAGNOSTIC,
            device_key=DeviceKey.LEGIO_PROTECTION_CONTROL_UNIT,
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.DATA_LEGIO_STATUS_ERROR_NO_VALID_TEMP_SENSOR,
            api_descriptor=FlagRegisterInputDescriptor(27, 5),
            icon="mdi:alert-circle",
            entity_category=EntityCategory.DIAGNOSTIC,
            device_key=DeviceKey.LEGIO_PROTECTION_CONTROL_UNIT,
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.DATA_LEGIO_STATUS_ERROR_CANNOT_REACH_TEMP,
            api_descriptor=FlagRegisterInputDescriptor(27, 6),
            icon="mdi:alert-circle",
            entity_category=EntityCategory.DIAGNOSTIC,
            device_key=DeviceKey.LEGIO_PROTECTION_CONTROL_UNIT,
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.DATA_LEGIO_STATUS_ERROR_SETTINGS,
            api_descriptor=FlagRegisterInputDescriptor(27, 7),
            icon="mdi:alert-circle",
            entity_category=EntityCategory.DIAGNOSTIC,
            device_key=DeviceKey.LEGIO_PROTECTION_CONTROL_UNIT,
        ),
    ],
)
