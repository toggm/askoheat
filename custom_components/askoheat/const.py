"""Constants for askoheat."""

from datetime import timedelta
from enum import StrEnum
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "askoheat"
ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"

DEFAULT_HOST = "askoheat.local"
DEFAULT_PORT = 502
DEFAULT_SCAN_INTERVAL = 5

# per coordinator scan intervals
SCAN_INTERVAL_EMA = timedelta(seconds=5)
SCAN_INTERVAL_CONFIG = timedelta(hours=1)
SCAN_INTERVAL_DATA = timedelta(minutes=1)


class SwitchEMAAttrKey(StrEnum):
    """Askoheat EMA binary switch attribute keys."""

    SET_HEATER_STEP_HEATER1 = "set_heater_step_heater1"
    SET_HEATER_STEP_HEATER2 = "set_heater_step_heater2"
    SET_HEATER_STEP_HEATER3 = "set_heater_step_heater3"


class BinarySensorEMAAttrKey(StrEnum):
    """Askoheat EMA binary sensor attribute keys."""

    # from status register
    HEATER1_ACTIVE = "status.heater1"
    HEATER2_ACTIVE = "status.heater2"
    HEATER3_ACTIVE = "status.heater3"
    PUMP_ACTIVE = "status.pump"
    RELAY_BOARD_CONNECTED = "status.relay_board_connected"
    EMERGENCY_MODE_ACTIVE = "status.emergency_mode"
    HEAT_PUMP_REQUEST_ACTIVE = "status.heat_pump_request"
    LEGIONELLA_PROTECTION_ACTIVE = "status.legionella_protection"
    ANALOG_INPUT_ACTIVE = "status.analog_input"
    SETPOINT_ACTIVE = "status.setpoint"
    LOAD_FEEDIN_ACTIVE = "status.load_feedin"
    AUTOHEATER_OFF_ACTIVE = "status.autoheater_off"
    PUMP_RELAY_FOLLOW_UP_TIME_ACTIVE = "status.pump_relay_follow_up_time_active"
    TEMP_LIMIT_REACHED = "status.temp_limit_reached"
    ERROR_OCCURED = "status.error"


class SensorEMAAttrKey(StrEnum):
    """Askoheat EMA sensor attribute keys."""

    # 250-30000 watt
    HEATER_LOAD = "heater_load"
    # 250-30000 watt
    LOAD_SETPOINT_VALUE = "load_setpoint"
    # -30000-30000 watt
    LOAD_FEEDIN_VALUE = "load_feedin"
    # 0-10V
    ANALOG_INPUT_VALUE = "analog_input"
    INTERNAL_TEMPERATUR_SENSOR_VALUE = "internal_temp_sensor"
    EXTERNAL_TEMPERATUR_SENSOR1_VALUE = "external_temp_sensor1"
    EXTERNAL_TEMPERATUR_SENSOR2_VALUE = "external_temp_sensor2"
    EXTERNAL_TEMPERATUR_SENSOR3_VALUE = "external_temp_sensor3"
    EXTERNAL_TEMPERATUR_SENSOR4_VALUE = "external_temp_sensor4"
