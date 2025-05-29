"""Energymanager block Api descriptor classes."""

# http://www.download.askoma.com/askofamily_plus/modbus/askoheat-modbus.html#EM_Block

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.number import NumberMode
from homeassistant.components.sensor.const import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfElectricPotential, UnitOfPower, UnitOfTemperature

from custom_components.askoheat.api_desc import (
    ByteRegisterInputDescriptor,
    FlagRegisterInputDescriptor,
    Float32RegisterInputDescriptor,
    RegisterBlockDescriptor,
    SignedInt16RegisterInputDescriptor,
    UnsignedInt16RegisterInputDescriptor,
)
from custom_components.askoheat.const import (
    EMA_STATUS_REGISTER,
    BinarySensorAttrKey,
    DeviceKey,
    NumberAttrKey,
    SensorAttrKey,
)
from custom_components.askoheat.model import (
    AskoheatBinarySensorEntityDescription,
    AskoheatNumberEntityDescription,
    AskoheatSensorEntityDescription,
)

EMA_FEED_IN_VALUE_NUMBER_ENTITY_DESCRIPTOR = AskoheatNumberEntityDescription(
    key=NumberAttrKey.LOAD_FEEDIN_VALUE,
    device_key=DeviceKey.ENERGY_MANAGER,
    icon="mdi:solar-power",
    native_min_value=-30000,
    native_max_value=30000,
    native_precision=0,
    native_unit_of_measurement=UnitOfPower.WATT,
    entity_category=None,
    api_descriptor=SignedInt16RegisterInputDescriptor(20),
)

EMA_EMERGENCY_MODE_API_DESCRIPTOR = FlagRegisterInputDescriptor(
    starting_register=EMA_STATUS_REGISTER, bit=7
)

EMA_REGISTER_BLOCK_DESCRIPTOR = RegisterBlockDescriptor(
    starting_register=300,
    number_of_registers=37,
    binary_sensors=[
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.HEATER1_ACTIVE,
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            icon="mdi:power-plug",
            device_class=BinarySensorDeviceClass.RUNNING,
            api_descriptor=FlagRegisterInputDescriptor(
                starting_register=EMA_STATUS_REGISTER, bit=0
            ),
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.HEATER2_ACTIVE,
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            icon="mdi:power-plug",
            device_class=BinarySensorDeviceClass.RUNNING,
            api_descriptor=FlagRegisterInputDescriptor(
                starting_register=EMA_STATUS_REGISTER, bit=1
            ),
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.HEATER3_ACTIVE,
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            icon="mdi:power-plug",
            device_class=BinarySensorDeviceClass.RUNNING,
            api_descriptor=FlagRegisterInputDescriptor(
                starting_register=EMA_STATUS_REGISTER, bit=2
            ),
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.PUMP_ACTIVE,
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            icon="mdi:pump",
            device_class=BinarySensorDeviceClass.RUNNING,
            api_descriptor=FlagRegisterInputDescriptor(
                starting_register=EMA_STATUS_REGISTER, bit=3
            ),
            entity_registry_enabled_default=False,
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.RELAY_BOARD_CONNECTED,
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            icon="mdi:connection",
            device_class=BinarySensorDeviceClass.PROBLEM,
            api_descriptor=FlagRegisterInputDescriptor(
                starting_register=EMA_STATUS_REGISTER, bit=4
            ),
            entity_registry_enabled_default=False,
        ),
        # bit 5 ignored
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.HEATPUMP_REQUEST_ACTIVE,
            device_key=DeviceKey.HEATPUMP_CONTROL_UNIT,
            icon="mdi:heat-pump",
            device_class=BinarySensorDeviceClass.RUNNING,
            api_descriptor=FlagRegisterInputDescriptor(
                starting_register=EMA_STATUS_REGISTER, bit=6
            ),
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.EMERGENCY_MODE_ACTIVE,
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            icon="mdi:car-emergency",
            device_class=BinarySensorDeviceClass.RUNNING,
            api_descriptor=EMA_EMERGENCY_MODE_API_DESCRIPTOR,
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.LEGIONELLA_PROTECTION_ACTIVE,
            device_key=DeviceKey.LEGIO_PROTECTION_CONTROL_UNIT,
            icon="mdi:shield-sun",
            device_class=BinarySensorDeviceClass.RUNNING,
            api_descriptor=FlagRegisterInputDescriptor(
                starting_register=EMA_STATUS_REGISTER, bit=8
            ),
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.ANALOG_INPUT_ACTIVE,
            device_key=DeviceKey.ANALOG_INPUT_CONTROL_UNIT,
            icon="mdi:sine-wave",
            device_class=BinarySensorDeviceClass.RUNNING,
            api_descriptor=FlagRegisterInputDescriptor(
                starting_register=EMA_STATUS_REGISTER, bit=9
            ),
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.SETPOINT_ACTIVE,
            device_key=DeviceKey.ENERGY_MANAGER,
            icon="mdi:finance",
            device_class=BinarySensorDeviceClass.RUNNING,
            api_descriptor=FlagRegisterInputDescriptor(
                starting_register=EMA_STATUS_REGISTER, bit=10
            ),
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.LOAD_FEEDIN_ACTIVE,
            device_key=DeviceKey.ENERGY_MANAGER,
            icon="mdi:solar-power",
            device_class=BinarySensorDeviceClass.RUNNING,
            api_descriptor=FlagRegisterInputDescriptor(
                starting_register=EMA_STATUS_REGISTER, bit=11
            ),
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.AUTOHEATER_ACTIVE,
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            icon="mdi:water-boiler-auto",
            inverted=True,
            device_class=BinarySensorDeviceClass.RUNNING,
            api_descriptor=FlagRegisterInputDescriptor(
                starting_register=EMA_STATUS_REGISTER, bit=12
            ),
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.PUMP_RELAY_FOLLOW_UP_TIME_ACTIVE,
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            icon="mdi:water-boiler-auto",
            device_class=BinarySensorDeviceClass.RUNNING,
            api_descriptor=FlagRegisterInputDescriptor(
                starting_register=EMA_STATUS_REGISTER, bit=13
            ),
            entity_registry_enabled_default=False,
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.TEMP_LIMIT_REACHED,
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            icon="mdi:water-boiler-auto",
            device_class=BinarySensorDeviceClass.RUNNING,
            api_descriptor=FlagRegisterInputDescriptor(
                starting_register=EMA_STATUS_REGISTER, bit=14
            ),
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.ERROR_OCCURRED,
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            icon="mdi:alert-circle",
            device_class=BinarySensorDeviceClass.PROBLEM,
            api_descriptor=FlagRegisterInputDescriptor(
                starting_register=EMA_STATUS_REGISTER, bit=15
            ),
        ),
    ],
    sensors=[
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.HEATER_LOAD,
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            icon="mdi:lightning-bolt",
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.POWER,
            native_precision=0,
            native_unit_of_measurement=UnitOfPower.WATT,
            entity_category=None,
            api_descriptor=UnsignedInt16RegisterInputDescriptor(17),
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.ANALOG_INPUT_VALUE,
            device_key=DeviceKey.ANALOG_INPUT_CONTROL_UNIT,
            icon="mdi:gauge",
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.VOLTAGE,
            native_unit_of_measurement=UnitOfElectricPotential.VOLT,
            entity_category=None,
            api_descriptor=Float32RegisterInputDescriptor(23),
            native_min_value=0,
            native_max_value=10,
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.INTERNAL_TEMPERATUR_SENSOR_VALUE,
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            icon="mdi:thermometer",
            native_precision=1,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            entity_category=None,
            api_descriptor=Float32RegisterInputDescriptor(25),
            native_min_value=0,
            native_max_value=120,
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.EXTERNAL_TEMPERATUR_SENSOR1_VALUE,
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            icon="mdi:thermometer",
            native_precision=1,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            entity_category=None,
            api_descriptor=Float32RegisterInputDescriptor(27),
            entity_registry_enabled_default=False,
            native_min_value=0,
            native_max_value=120,
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.EXTERNAL_TEMPERATUR_SENSOR2_VALUE,
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            icon="mdi:thermometer",
            native_precision=1,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            entity_category=None,
            api_descriptor=Float32RegisterInputDescriptor(29),
            entity_registry_enabled_default=False,
            native_min_value=0,
            native_max_value=120,
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.EXTERNAL_TEMPERATUR_SENSOR3_VALUE,
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            icon="mdi:thermometer",
            native_precision=1,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            entity_category=None,
            api_descriptor=Float32RegisterInputDescriptor(31),
            entity_registry_enabled_default=False,
            native_min_value=0,
            native_max_value=120,
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.EXTERNAL_TEMPERATUR_SENSOR4_VALUE,
            device_key=DeviceKey.WATER_HEATER_CONTROL_UNIT,
            icon="mdi:thermometer",
            native_precision=1,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            entity_category=None,
            api_descriptor=Float32RegisterInputDescriptor(33),
            entity_registry_enabled_default=False,
            native_min_value=0,
            native_max_value=120,
        ),
    ],
    number_inputs=[
        AskoheatNumberEntityDescription(
            key=NumberAttrKey.SET_HEATER_STEP_VALUE,
            device_key=DeviceKey.ENERGY_MANAGER,
            icon="mdi:lightning-bolt",
            native_min_value=0,
            native_max_value=7,
            native_precision=0,
            native_step=1,
            entity_category=None,
            mode=NumberMode.SLIDER,
            api_descriptor=ByteRegisterInputDescriptor(18),
        ),
        AskoheatNumberEntityDescription(
            key=NumberAttrKey.LOAD_SETPOINT_VALUE,
            device_key=DeviceKey.ENERGY_MANAGER,
            icon="mdi:lightning-bolt",
            native_min_value=250,
            native_max_value=30000,
            native_precision=0,
            native_step=1,
            native_unit_of_measurement=UnitOfPower.WATT,
            entity_category=None,
            api_descriptor=SignedInt16RegisterInputDescriptor(19),
            entity_registry_enabled_default=False,
        ),
        EMA_FEED_IN_VALUE_NUMBER_ENTITY_DESCRIPTOR,
    ],
)
