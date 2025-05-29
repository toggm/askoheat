"""Constants for askoheat."""

from datetime import timedelta
from enum import IntEnum, StrEnum
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
SCAN_INTERVAL_OP_DATA = timedelta(minutes=1)

CONF_FEED_IN = "auto-feed-in"
CONF_DEVICE_UNITS = "devices"
CONF_ANALOG_INPUT_UNIT = "analog_input_unit"
CONF_LEGIONELLA_PROTECTION_UNIT = "legionella_protection_unit"
CONF_MODBUS_MASTER_UNIT = "modbus_master_unit"
CONF_HEATPUMP_UNIT = "heatpump_unit"
CONF_POWER_ENTITY_ID = "power_entity_id"
CONF_POWER_INVERT = "power_invert"

CONF_INPUT_SETTINGS_REGISTER = 2
CONF_AUTO_HEATER_SETTINGS_REGISTER = 4
CONF_HEAT_BUFFER_TYPE_REGISTER = 6
CONF_HEATER_POSITION_REGISTER = 8
CONF_LEGIO_SETTINGS_REGISTER = 9
CONF_HOUSE_TYPE_REGISTER = 20
DATA_LEGIO_STATUS_REGISTER = 27
PAR_TYPE_REGISTER = 16
EMA_STATUS_REGISTER = 16


class NumberAttrKey(StrEnum):
    """Askoheat number entities attribute keys."""

    # 1-7
    SET_HEATER_STEP_VALUE = "set_heater_step"
    # 250-30000 watt
    LOAD_SETPOINT_VALUE = "load_setpoint"
    # -30000-30000 watt
    LOAD_FEEDIN_VALUE = "load_feedin"

    # -----------------------------------------------
    # config block enums
    # -----------------------------------------------
    # 0-16 (default 5)
    CON_RELAY_SEC_COUNT_SECONDS = "relay_switch_on_inhibit_seconds"
    # 0-240 (default 30)
    CON_PUMP_SEC_COUNT_SECONDS = "pump_follow_up_time_seconds"
    # 2-10080
    CON_AUTO_HEATER_OFF_MINUTES = "auto_heater_off_minutes"

    # 0-255
    CON_CASCADE_PRIORIZATION = "cascade_priorization"

    # 0-1000 liter
    CON_HEATBUFFER_VOLUME = "heatbuffer_volume_liter"

    # 50-65
    CON_LEGIO_PROTECTION_TEMPERATURE = "legio_protection_temperature"
    # 0-1440 (default 240)
    CON_LEGIO_PROTECTION_HEATUP_MINUTES = "legio_protection_heatup_minutes"
    # 1-255
    CON_NUMBER_OF_HOUSEHOLD_MEMBERS = "number_of_household_members"
    # 0-10'000 watt
    CON_LOAD_FEEDIN_BASIC_ENERGY_LEVEL = "load_feedin_basic_energy_level"
    # -12 - 12
    CON_TIMEZONE_OFFSET = "timezone_offset"
    # 0-120
    CON_LOAD_FEEDIN_DELAY_SECONDS = "load_feedin_delay_seconds"
    # 0-240
    CON_RTU_SLAVE_ID = "rtu_slave_id"
    CON_ANALOG_INPUT_HYSTERESIS = "analog_input_hysteresis"

    # Analog input 0
    CON_ANALOG_INPUT_0_THRESHOLD = "analog_input_0_threshold"
    CON_ANALOG_INPUT_0_THRESHOLD_STEP = "analog_input_0_threshold_step"
    CON_ANALOG_INPUT_0_THRESHOLD_TEMPERATURE = "analog_input_0_threshold_temperature"

    # Analog input 1
    CON_ANALOG_INPUT_1_THRESHOLD = "analog_input_1_threshold"
    CON_ANALOG_INPUT_1_THRESHOLD_STEP = "analog_input_1_threshold_step"
    CON_ANALOG_INPUT_1_THRESHOLD_TEMPERATURE = "analog_input_1_threshold_temperature"

    # Analog input 2
    CON_ANALOG_INPUT_2_THRESHOLD = "analog_input_2_threshold"
    CON_ANALOG_INPUT_2_THRESHOLD_STEP = "analog_input_2_threshold_step"
    CON_ANALOG_INPUT_2_THRESHOLD_TEMPERATURE = "analog_input_2_threshold_temperature"

    # Analog input 3
    CON_ANALOG_INPUT_3_THRESHOLD = "analog_input_3_threshold"
    CON_ANALOG_INPUT_3_THRESHOLD_STEP = "analog_input_3_threshold_step"
    CON_ANALOG_INPUT_3_THRESHOLD_TEMPERATURE = "analog_input_3_threshold_temperature"

    # Analog input 4
    CON_ANALOG_INPUT_4_THRESHOLD = "analog_input_4_threshold"
    CON_ANALOG_INPUT_4_THRESHOLD_STEP = "analog_input_4_threshold_step"
    CON_ANALOG_INPUT_4_THRESHOLD_TEMPERATURE = "analog_input_4_threshold_temperature"

    # Analog input 5
    CON_ANALOG_INPUT_5_THRESHOLD = "analog_input_5_threshold"
    CON_ANALOG_INPUT_5_THRESHOLD_STEP = "analog_input_5_threshold_step"
    CON_ANALOG_INPUT_5_THRESHOLD_TEMPERATURE = "analog_input_5_threshold_temperature"

    # Analog input 6
    CON_ANALOG_INPUT_6_THRESHOLD = "analog_input_6_threshold"
    CON_ANALOG_INPUT_6_THRESHOLD_STEP = "analog_input_6_threshold_step"
    CON_ANALOG_INPUT_6_THRESHOLD_TEMPERATURE = "analog_input_6_threshold_temperature"

    # Analog input 7
    CON_ANALOG_INPUT_7_THRESHOLD = "analog_input_7_threshold"
    CON_ANALOG_INPUT_7_THRESHOLD_STEP = "analog_input_7_threshold_step"
    CON_ANALOG_INPUT_7_THRESHOLD_TEMPERATURE = "analog_input_7_threshold_temperature"

    # 0-7
    CON_HEATPUMP_REQUEST_OFF_STEP = "heatpump_request_off_step"
    # 0-7
    CON_HEATPUMP_REQUEST_ON_STEP = "heatpump_request_on_step"
    # 0-7
    CON_EMERGENCY_MODE_ON_STEP = "emergency_mode_on_step"

    # 0-95 degree
    CON_TEMPERATURE_HYSTERESIS = "temperature_hysteresis"
    # 0-95 degree
    CON_MINIMAL_TEMPERATURE = "minimal_temperature"
    # 0-95 degree
    CON_SET_HEATER_STEP_TEMPERATURE_LIMIT = "set_heater_step_temp_limit"
    # 0-95 degree
    CON_LOAD_FEEDIN_OR_SETPOINT_TEMPERATURE_LIMIT = "load_feedin_or_setpoint_temp_limit"
    # 0-95 degree
    CON_LOW_TARIFF_TEMPERATURE_LIMIT = "low_tariff_temp_limit"
    # 0-95 degree
    CON_HEATPUMP_REQUEST_TEMPERATURE_LIMIT = "heatpump_request_temp_limit"

    EMA_AUTO_FEEDIN_BUFFER = "auto_feedin_buffer"


class TimeAttrKey(StrEnum):
    """Askoheat time entities attribute keys."""

    # i.e. 12:00 AM
    CON_LEGIO_PROTECTION_PREFERRED_START_TIME = "legio_protection_preferred_start_time"
    CON_LOW_TARIFF_START_TIME = "low_tariff_start_time"
    CON_LOW_TARIFF_END_TIME = "low_tariff_end_time"


class TextAttrKey(StrEnum):
    """Askoheat text entities attribute keys."""

    CON_INFO_STRING = "info_string"


class SelectAttrKey(StrEnum):
    """Askoheat select entities attribute keys."""

    CON_RTU_BAUDRATE = "rtu_baudrate"
    CON_SMART_METER_TYPE = "smart_meter_type"
    CON_ENERGY_METER_TYPE = "energy_meter_type"


class SwitchAttrKey(StrEnum):
    """Askoheat binary switch attribute keys."""

    # -----------------------------------------------
    # config block enums
    # -----------------------------------------------
    # from input settings register -- begin
    # low byte
    CON_MISSING_CURRENT_FLOW_TRIGGERS_ERROR = "missing_current_flow_triggers_error"
    CON_HEATER_LOAD_VALUE_ONLY_IF_CURRENT_FLOWS = (
        "heater_load_value_only_if_current_flows"
    )
    CON_LOAD_FEEDIN_VALUE_ENABLED = "load_feedin_value_enabled"
    CON_LOAD_SETPOINT_VALUE_ENABLED = "load_setpoint_value_enabled"
    CON_SET_HEATER_STEP_VALUE_ENABLED = "set_heater_step_value_enabled"
    CON_SET_ANALOG_INPUT_ENABLED = "analog_input_enabled"
    CON_HEATPUMP_REQUEST_INPUT_ENABLED = "heatpump_request_enabled"
    CON_EMERGENCY_MODE_ENABLED = "emergency_mode_enabled"
    # high byte
    CON_LOW_TARIFF_OPTION_ENABLED = "low_tariff_option_enabled"
    CON_HOLD_MINIMAL_TEMPERATURE_ENABLED = "hold_minimal_temperature_enabled"
    CON_SOFTWARE_CONTROL_SMA_SEMP_ENABLED = "sw_control_sma_semp_enabled"
    CON_SOFTWARE_CONTROL_SENEC_HOME_ENABLED = "sw_control_senec_home_enabled"
    # from input settings register -- end

    # from auto heater off settings register -- begin
    CON_AUTO_OFF_MODBUS_TIMEOUT_ENABLED = "auto_off_modbus_timeout_enabled"
    CON_RESTART_IF_ENERGYMANAGER_CONNECTION_LOST = "restart_if_em_connection_lost"
    CON_AUTO_OFF_MODBUS_ENABLED = "auto_off_modbus_enabled"
    CON_AUTO_OFF_ANALOG_INPUT_ENABLED = "auto_off_analog_input_enabled"
    CON_AUTO_OFF_HEATPUMP_REQUEST_ENABLED = "auto_off_heatpump_request_enabled"
    CON_AUTO_OFF_EMERGENCY_MODE_ENABLED = "auto_off_emergency_mode_enabled"
    # from auto heater off settings register -- end

    # from heatbuffer type settings register -- begin
    CON_HEATBUFFER_TYPE_TAP_WATER = "heatbuffer_type_tap_water"
    CON_HEATBUFFER_TYPE_HEATING_WATER = "heatbuffer_type_heating_water"
    CON_HEATBUFFER_TYPE_COMBINED_HEAT_AND_POWER_UNIT = (
        "heatbuffer_type_combined_heat_and_power_unit"
    )
    CON_HEATBUFFER_TYPE_PELLET_FIRING = "heatbuffer_type_pellet_firing"
    CON_HEATBUFFER_TYPE_GAS_BURNER = "heatbuffer_type_gas_burner"
    CON_HEATBUFFER_TYPE_OIL_BURNER = "heatbuffer_type_oil_burner"
    CON_HEATBUFFER_TYPE_HEATPUMP = "heatbuffer_type_heatpump"
    CON_HEATBUFFER_TYPE_OTHER = "heatbuffer_type_other"
    # from heatbuffer type settings register -- end

    # from heater position register -- begin
    CON_HEATER_POSITION_BOTTOM = "heater_position_bottom"
    CON_HEATER_POSITION_MIDDLE = "heater_position_middle"
    CON_HEATER_POSITION_ASKOWALL = "heater_position_askowall"
    # from heater position register -- end

    # from legio setting register -- begin
    # low byte
    CON_LEGIO_SETTINGS_USE_INTERNAL_TEMP_SENSOR = (
        "legio_settings_use_internal_temp_sensor"
    )
    CON_LEGIO_SETTINGS_USE_EXTERNAL_TEMP_SENSOR1 = (
        "legio_settings_use_external_temp_sensor1"
    )
    CON_LEGIO_SETTINGS_USE_EXTERNAL_TEMP_SENSOR2 = (
        "legio_settings_use_external_temp_sensor2"
    )
    CON_LEGIO_SETTINGS_USE_EXTERNAL_TEMP_SENSOR3 = (
        "legio_settings_use_external_temp_sensor3"
    )
    CON_LEGIO_SETTINGS_USE_EXTERNAL_TEMP_SENSOR4 = (
        "legio_settings_use_external_temp_sensor4"
    )
    # high byte
    CON_LEGIO_SETTINGS_INTERVAL_DAILY = "legio_settings_interval_daily"
    CON_LEGIO_SETTINGS_INTERVAL_WEEKLY = "legio_settings_interval_weekly"
    CON_LEGIO_SETTINGS_INTERVAL_FORTNIGHTLY = "legio_settings_interval_fortnightly"
    CON_LEGIO_SETTINGS_INTERVAL_MONTHLY = "legio_settings_interval_monthly"
    CON_LEGIO_SETTINGS_PREFER_FEEDIN_ENERGY = "legio_settings_prefer_feedin_energy"
    CON_LEGIO_SETTINGS_PROTECTION_ENABLED = "legio_setting_protection_enabled"
    # from legio_settings register -- end

    # from house type register -- begin
    CON_HOUSE_TYPE_SINGLE_FAMILY_HOUSE = "house_type_single_family_house"
    CON_HOUSE_TYPE_TWO_FAMILY_HOUSE = "house_type_two_family_house"
    CON_HOUSE_TYPE_APPARTMENT_BUILDING = "house_type_appartment_building"
    CON_HOUSE_TYPE_COMMERCIAL_BUILDING = "house_type_commercial_building"
    # from house type register -- end

    CON_SUMMER_TIME = "is_summer_time"

    # from rtu settings register -- begin
    # low byte
    CON_RTU_SEND_TWO_STOP_BITS = "rtu_send_two_stop_bits"
    CON_RTU_SEND_PARITY_EVEN = "rtu_send_parity_even"
    CON_RTU_SEND_PARITY_ODD = "rtu_send_parity_odd"
    CON_RTU_SLAVE_MODE_ACTIVE = "rtu_slave_mode_active"
    # high byte
    CON_RTU_MASTER_MODE_ACTIVE = "rtu_master_mode_active"
    # from rtu settings register -- end

    # from temp settings register -- begin
    # low byte
    CON_USE_INTERNAL_TEMP_SENSOR = "use_internal_temp_sensor"
    CON_USE_EXTERNAL_TEMP_SENSOR1 = "use_external_temp_sensor1"
    CON_USE_EXTERNAL_TEMP_SENSOR2 = "use_external_temp_sensor2"
    CON_USE_EXTERNAL_TEMP_SENSOR3 = "use_external_temp_sensor3"
    CON_USE_EXTERNAL_TEMP_SENSOR4 = "use_external_temp_sensor4"
    # from temp settings register -- end

    EMA_AUTO_FEEDIN_SWITCH = "auto_feedin"

    CONTROL_EMERGENCY_MODE = "emergency_mode"


class BinarySensorAttrKey(StrEnum):
    """Askoheat binary sensor attribute keys."""

    # -----------------------------------------------
    # EMA block binary sensors
    # -----------------------------------------------
    # from status register -- begin
    HEATER1_ACTIVE = "status_heater1"
    HEATER2_ACTIVE = "status_heater2"
    HEATER3_ACTIVE = "status_heater3"
    PUMP_ACTIVE = "status_pump"
    RELAY_BOARD_CONNECTED = "status_relay_board_connected"
    EMERGENCY_MODE_ACTIVE = "status_emergency_mode"
    HEATPUMP_REQUEST_ACTIVE = "status_heatpump_request"
    LEGIONELLA_PROTECTION_ACTIVE = "status_legionella_protection"
    ANALOG_INPUT_ACTIVE = "status_analog_input"
    SETPOINT_ACTIVE = "status_setpoint"
    LOAD_FEEDIN_ACTIVE = "status_load_feedin"
    AUTOHEATER_ACTIVE = "status_autoheater"
    PUMP_RELAY_FOLLOW_UP_TIME_ACTIVE = "status_pump_relay_follow_up_time_active"
    TEMP_LIMIT_REACHED = "status_temp_limit_reached"
    ERROR_OCCURRED = "status_error"
    # from status register -- end

    # -----------------------------------------------
    # PAR block binary sensors
    # -----------------------------------------------
    # from type register -- begin
    PAR_TYPE_3_STAGE_VERSION = "type_3_stage_version"
    PAR_TYPE_7_STAGE_VERSION = "type_7_stage_version"
    PAR_HEATER_TYPE_FLANGE = "heater_type_flange"
    PAR_HEATER_TYPE_SCREW_IN = "heater_type_screw_in"
    PAR_WIRED_AS_STAR_CONNECTION = "wired_as_star_connection"
    PAR_WIRED_AS_DELTA_CONECTION = "wired_as_delta_connection"
    PAR_TYPE_OEM_VERSION = "oem_version"
    # from type register -- end

    # -----------------------------------------------
    # DATA block binary sensors
    # -----------------------------------------------
    # from legio status register -- begin
    DATA_LEGIO_STATUS_HEATING_UP = "legio_status_heating_up"
    DATA_LEGIO_STATUS_TEMPERATURE_REACHED = "legio_status_temp_reached"
    DATA_LEGIO_STATUS_TEMP_REACHED_OUTSIDE_INTERVAL = (
        "legio_status_temp_reached_outside_interval"
    )
    DATA_LEGIO_STATUS_UNEXPECTED_TEMP_DROP = "legio_status_unexpected_temp_drop"
    DATA_LEGIO_STATUS_ERROR_NO_VALID_TEMP_SENSOR = (
        "legio_status_error_no_valid_temp_sensor"
    )
    DATA_LEGIO_STATUS_ERROR_CANNOT_REACH_TEMP = "legio_status_error_cannot_reach_temp"
    DATA_LEGIO_STATUS_ERROR_SETTINGS = "legio_status_error_settings"
    # from legio status register -- end


class SensorAttrKey(StrEnum):
    """Askoheat sensor attribute keys."""

    # 250-30000 watt
    HEATER_LOAD = "heater_load"
    # 0-10V
    ANALOG_INPUT_VALUE = "analog_input"
    INTERNAL_TEMPERATUR_SENSOR_VALUE = "internal_temp_sensor"
    EXTERNAL_TEMPERATUR_SENSOR1_VALUE = "external_temp_sensor1"
    EXTERNAL_TEMPERATUR_SENSOR2_VALUE = "external_temp_sensor2"
    EXTERNAL_TEMPERATUR_SENSOR3_VALUE = "external_temp_sensor3"
    EXTERNAL_TEMPERATUR_SENSOR4_VALUE = "external_temp_sensor4"

    # -----------------------------------------------
    # PAR block enums
    # -----------------------------------------------
    PAR_ID = "serial_number"
    PAR_HEATER1_POWER = "heater1_power"
    PAR_HEATER2_POWER = "heater2_power"
    PAR_HEATER3_POWER = "heater3_power"
    PAR_HEATER4_POWER = "heater4_power"
    PAR_HEATER5_POWER = "heater5_power"
    PAR_HEATER6_POWER = "heater6_power"
    PAR_ARTICLE_NUMBER = "article_number"
    PAR_ARTICLE_NAME = "article_name"
    PAR_SOFTWARE_VERSION = "software_version"
    PAR_HARDWARE_VERSION = "hardware_version"
    PAR_NUMBER_OF_STEPS = "number_of_steps"
    PAR_NUMBER_OF_HEATER = "number_of_heater"
    PAR_MAX_POWER = "max_power"

    # -----------------------------------------------
    # DATA block enums
    # -----------------------------------------------
    DATA_OPERATING_TIME_MINUTES = "operating_time"
    DATA_OPERATING_TIME_HEATER1_MINUTES = "operating_time_heater1"
    DATA_OPERATING_TIME_HEATER2_MINUTES = "operating_time_heater2"
    DATA_OPERATING_TIME_HEATER3_MINUTES = "operating_time_heater3"
    DATA_OPERATING_TIME_PUMP_MINUTES = "operating_time_pump"
    DATA_OPERATING_TIME_VALVE_MINUTES = "operating_time_valve"
    DATA_SWITCH_COUNT_RELAY1 = "switch_count_relay1"
    DATA_SWITCH_COUNT_RELAY2 = "switch_count_relay2"
    DATA_SWITCH_COUNT_RELAY3 = "switch_count_relay3"
    DATA_SWITCH_COUNT_RELAY4 = "switch_count_relay4"
    DATA_SINCE_LAST_LEGIO_ACTIVATION_MINUTES = "legio_since_last_activation"
    DATA_LEGIO_PLATEAU_TIMER = "legio_plateau_timer"
    DATA_ANALOG_INPUT_STEP = "analog_input_step"
    DATA_ACTUAL_TEMP_LIMIT = "actual_temp_limit"
    DATA_AUTO_HEATER_OFF_COUNTDOWN_MINUTES = "auto_heater_off_countdown"
    DATA_EMERGENCY_OFF_COUNTDOWN_MINUTES = "emergency_off_countdown"
    DATA_BOOT_COUNT = "boot_count"
    DATA_OPERATING_TIME_SET_HEATER_STEP = "operating_time_set_heater_step"
    DATA_OPERATING_TIME_LOAD_SETPOINT = "operating_time_load_setpoint"
    DATA_OPERATING_TIME_LOAD_FEEDIN = "operating_time_load_feedin"
    DATA_OPERATING_TIME_HEATPUMP_REQUEST = "operating_time_heatpump_request"
    DATA_OPERATING_TIME_ANALOG_INPUT = "operating_time_analog_input"
    DATA_OPERATING_TIME_EMERGENCY_MODE = "operating_time_emergency_mode"
    DATA_OPERATING_TIME_LEGIO_PROTECTION = "operating_time_legio_protection"
    DATA_OPERATING_TIME_LOW_TARIFF = "operating_time_low_tariff"
    DATA_OPERATING_TIME_MINIMAL_TEMP = "operating_time_minimal_temp"
    DATA_OPERATING_TIME_HEATER_STEP1 = "operating_time_heater_step1"
    DATA_OPERATING_TIME_HEATER_STEP2 = "operating_time_heater_step2"
    DATA_OPERATING_TIME_HEATER_STEP3 = "operating_time_heater_step3"
    DATA_OPERATING_TIME_HEATER_STEP4 = "operating_time_heater_step4"
    DATA_OPERATING_TIME_HEATER_STEP5 = "operating_time_heater_step5"
    DATA_OPERATING_TIME_HEATER_STEP6 = "operating_time_heater_step6"
    DATA_OPERATING_TIME_HEATER_STEP7 = "operating_time_heater_step7"
    DATA_COUNT_SET_HEATER_STEP = "count_set_heater_step"
    DATA_COUNT_LOAD_SETPOINT = "count_load_setpoint"
    DATA_COUNT_LOAD_FEEDIN = "count_load_feedin"
    DATA_COUNT_HEATPUMP_REQUEST = "count_heatpump_request"
    DATA_COUNT_ANALOG_INPUT = "count_analog_input"
    DATA_COUNT_EMERGENCY_MODE = "count_emergency_mode"
    DATA_COUNT_LEGIO_PROTECTION = "count_legio_protection"
    DATA_COUNT_LOW_TARIFF = "count_low_tariff"
    DATA_COUNT_MINIMAL_TEMP = "count_minimal_temp"
    DATA_MAX_MEASURED_TEMP = "max_measured_temp"


class Baudrate(StrEnum):
    """Available Baudrates."""

    BAUD_RATE_1200 = "1200"
    BAUD_RATE_2400 = "2400"
    BAUD_RATE_4800 = "4800"
    BAUD_RATE_9600 = "9600"
    BAUD_RATE_14400 = "14400"
    BAUD_RATE_19200 = "19200"
    BAUD_RATE_28800 = "28800"
    BAUD_RATE_38400 = "38400"
    BAUD_RATE_57600 = "57600"
    BAUD_RATE_76800 = "76800"
    BAUD_RATE_115200 = "115200"
    BAUD_RATE_230400 = "230400"


class SmartMeterType(StrEnum):
    """Supported SmartMeter types."""

    SM_NOT_INSTALLED = "not installed"
    SM_ASKOMA_100A = "Askoma smart meter up to 100A"
    SM_ASKOMA_200A = "Askoma smart meter up to 200A"
    SM_EM340 = "Carlo Gavazzi EM340...S1 PFA"
    SM_ASKOMA_RTU_III = "Askoma smart meter RTU III"
    SM_OPEC = "Optec (ECS M3)"
    SM_EASTRON = "Eastron SDM72D-M"
    SM_ALPA_ESS = "ALPHA-ESS Smart Grid Value"
    SM_CHNT = "CHNT DTSU666"
    SM_SONNENKRAFT = "SONNENKRAFT SK-HWR-6/8/10/12"
    SM_FOX_HYBRID_H3 = "FOX HYBRID H3"
    SM_FRONIUS = "FRONIUS MODBUS RTU"
    SM_M_TEC_ENERGY_BUTLER = "M-TEC ENERGY BUTLER RTU"


class EnergyMeterType(IntEnum):
    """Supported EnergyMeter types."""

    EM_NOT_INSTALLED = 0x000
    EM_AUTOMATION_ONE_TYPE_A1EM_BIMOD = 0x001
    EM_AUTOMATION_ONE_TYPE_A1EM_MOD = 0x02
    EM300 = 0x010


class DeviceKey(StrEnum):
    """Device keys."""

    MODBUS_MASTER = "modbus_master"
    HEATPUMP_CONTROL_UNIT = "heatpump_control_unit"
    ANALOG_INPUT_CONTROL_UNIT = "analog_input_control_unit"
    ENERGY_MANAGER = "energy_manager"
    WATER_HEATER_CONTROL_UNIT = "water_heater_control_unit"
    LEGIO_PROTECTION_CONTROL_UNIT = "legio_protection_control_unit"


class AttributeKeys(StrEnum):
    """Additional attributes keys."""

    API_DESCRIPTOR = "api_descriptor"
    FORMATTED = "formatted"


HTTP_RESPONSE_CODE_OK = 200
