"""Test data."""

from custom_components.askoheat.api_conf_desc import CONF_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_ema_desc import EMA_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_op_desc import DATA_REGISTER_BLOCK_DESCRIPTOR
from custom_components.askoheat.api_par_desc import PARAM_REGISTER_BLOCK_DESCRIPTOR

data_register_values = [
    0 for _ in range(DATA_REGISTER_BLOCK_DESCRIPTOR.number_of_registers)
]

par_register_values = [
    0 for _ in range(PARAM_REGISTER_BLOCK_DESCRIPTOR.number_of_registers)
]

ema_register_values = [
    0 for _ in range(EMA_REGISTER_BLOCK_DESCRIPTOR.number_of_registers)
]

config_register_values = [
    0 for _ in range(CONF_REGISTER_BLOCK_DESCRIPTOR.number_of_registers)
]
