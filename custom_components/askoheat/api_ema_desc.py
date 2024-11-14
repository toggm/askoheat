"""Energymanager block Api descriptor classes."""
# http://www.download.askoma.com/askofamily_plus/modbus/askoheat-modbus.html#EM_Block

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.number import NumberMode
from homeassistant.components.sensor.const import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfElectricPotential,
    UnitOfPower,
    UnitOfTemperature,
)

from custom_components.askoheat.api_desc import (
    ByteRegisterInputDescriptor,
    FlagRegisterInputDescriptor,
    Float32RegisterInputDescriptor,
    RegisterBlockDescriptor,
    SignedIntRegisterInputDescriptor,
    UnsignedIntRegisterInputDescriptor,
)
from custom_components.askoheat.const import (
    BinarySensorAttrKey,
    NumberAttrKey,
    SensorAttrKey,
)
from custom_components.askoheat.model import (
    AskoheatBinarySensorEntityDescription,
    AskoheatNumberEntityDescription,
    AskoheatSensorEntityDescription,
)

EMA_REGISTER_BLOCK_DESCRIPTOR = RegisterBlockDescriptor(
    starting_register=300,
    number_of_registers=37,
    binary_sensors=[
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.HEATER1_ACTIVE,
            icon="mdi:power-plug",
            device_class=BinarySensorDeviceClass.RUNNING,
            api_descriptor=FlagRegisterInputDescriptor(starting_register=16, bit=0),
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.HEATER2_ACTIVE,
            icon="mdi:power-plug",
            device_class=BinarySensorDeviceClass.RUNNING,
            api_descriptor=FlagRegisterInputDescriptor(starting_register=16, bit=1),
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.HEATER3_ACTIVE,
            icon="mdi:power-plug",
            device_class=BinarySensorDeviceClass.RUNNING,
            api_descriptor=FlagRegisterInputDescriptor(starting_register=16, bit=2),
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.PUMP_ACTIVE,
            icon="mdi:pump",
            device_class=BinarySensorDeviceClass.RUNNING,
            api_descriptor=FlagRegisterInputDescriptor(starting_register=16, bit=3),
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.RELAY_BOARD_CONNECTED,
            icon="mdi:connection",
            device_class=BinarySensorDeviceClass.PROBLEM,
            api_descriptor=FlagRegisterInputDescriptor(starting_register=16, bit=4),
        ),
        # bit 5 ignored
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.HEAT_PUMP_REQUEST_ACTIVE,
            icon="mdi:heat-pump",
            device_class=BinarySensorDeviceClass.RUNNING,
            api_descriptor=FlagRegisterInputDescriptor(starting_register=16, bit=6),
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.EMERGENCY_MODE_ACTIVE,
            icon="mdi:car-emergency",
            device_class=BinarySensorDeviceClass.RUNNING,
            api_descriptor=FlagRegisterInputDescriptor(starting_register=16, bit=7),
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.LEGIONELLA_PROTECTION_ACTIVE,
            icon="mdi:shield-sun",
            device_class=BinarySensorDeviceClass.RUNNING,
            api_descriptor=FlagRegisterInputDescriptor(starting_register=16, bit=8),
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.ANALOG_INPUT_ACTIVE,
            icon="mdi:sine-wave",
            device_class=BinarySensorDeviceClass.RUNNING,
            api_descriptor=FlagRegisterInputDescriptor(starting_register=16, bit=9),
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.SETPOINT_ACTIVE,
            icon="mdi:finance",
            device_class=BinarySensorDeviceClass.RUNNING,
            api_descriptor=FlagRegisterInputDescriptor(starting_register=16, bit=10),
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.LOAD_FEEDIN_ACTIVE,
            icon="mdi:solar-power",
            device_class=BinarySensorDeviceClass.RUNNING,
            api_descriptor=FlagRegisterInputDescriptor(starting_register=16, bit=11),
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.AUTOHEATER_ACTIVE,
            icon="mdi:water-boiler-auto",
            inverted=True,
            device_class=BinarySensorDeviceClass.RUNNING,
            api_descriptor=FlagRegisterInputDescriptor(starting_register=16, bit=12),
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.PUMP_RELAY_FOLLOW_UP_TIME_ACTIVE,
            icon="mdi:water-boiler-auto",
            device_class=BinarySensorDeviceClass.RUNNING,
            api_descriptor=FlagRegisterInputDescriptor(starting_register=16, bit=13),
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.TEMP_LIMIT_REACHED,
            icon="mdi:water-boiler-auto",
            device_class=BinarySensorDeviceClass.RUNNING,
            api_descriptor=FlagRegisterInputDescriptor(starting_register=16, bit=14),
        ),
        AskoheatBinarySensorEntityDescription(
            key=BinarySensorAttrKey.ERROR_OCCURED,
            icon="mdi:water-thermometer",
            device_class=BinarySensorDeviceClass.PROBLEM,
            api_descriptor=FlagRegisterInputDescriptor(starting_register=16, bit=15),
        ),
    ],
    sensors=[
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.HEATER_LOAD,
            icon="mdi:lightning-bolt",
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.POWER,
            native_unit_of_measurement=UnitOfPower.WATT,
            entity_category=None,
            api_descriptor=UnsignedIntRegisterInputDescriptor(17),
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.ANALOG_INPUT_VALUE,
            icon="mdi:gauge",
            native_precision=0,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.VOLTAGE,
            native_unit_of_measurement=UnitOfElectricPotential.VOLT,
            entity_category=None,
            api_descriptor=Float32RegisterInputDescriptor(23),
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.INTERNAL_TEMPERATUR_SENSOR_VALUE,
            icon="mdi:thermometer",
            native_precision=1,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            entity_category=None,
            api_descriptor=Float32RegisterInputDescriptor(25),
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.EXTERNAL_TEMPERATUR_SENSOR1_VALUE,
            icon="mdi:thermometer",
            native_precision=1,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            entity_category=None,
            api_descriptor=Float32RegisterInputDescriptor(27),
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.EXTERNAL_TEMPERATUR_SENSOR2_VALUE,
            icon="mdi:thermometer",
            native_precision=1,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            entity_category=None,
            api_descriptor=Float32RegisterInputDescriptor(29),
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.EXTERNAL_TEMPERATUR_SENSOR3_VALUE,
            icon="mdi:thermometer",
            native_precision=1,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            entity_category=None,
            api_descriptor=Float32RegisterInputDescriptor(31),
        ),
        AskoheatSensorEntityDescription(
            key=SensorAttrKey.EXTERNAL_TEMPERATUR_SENSOR4_VALUE,
            icon="mdi:thermometer",
            native_precision=1,
            state_class=SensorStateClass.MEASUREMENT,
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            entity_category=None,
            api_descriptor=Float32RegisterInputDescriptor(33),
        ),
    ],
    number_inputs=[
        AskoheatNumberEntityDescription(
            key=NumberAttrKey.SET_HEADER_STEP_VALUE,
            icon="mdi:lightning-bolt",
            native_min_value=0,
            native_max_value=7,
            native_step=1,
            entity_category=None,
            mode=NumberMode.SLIDER,
            api_descriptor=ByteRegisterInputDescriptor(18),
        ),
        AskoheatNumberEntityDescription(
            key=NumberAttrKey.LOAD_SETPOINT_VALUE,
            icon="mdi:lightning-bolt",
            native_min_value=250,
            native_max_value=30000,
            native_precision=0,
            native_unit_of_measurement=UnitOfPower.WATT,
            entity_category=None,
            api_descriptor=SignedIntRegisterInputDescriptor(19),
        ),
        AskoheatNumberEntityDescription(
            key=NumberAttrKey.LOAD_FEEDIN_VALUE,
            icon="mdi:solar-power",
            native_min_value=-30000,
            native_max_value=30000,
            native_precision=0,
            native_unit_of_measurement=UnitOfPower.WATT,
            entity_category=None,
            api_descriptor=SignedIntRegisterInputDescriptor(20),
        ),
    ],
)
