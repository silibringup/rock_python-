import struct
import argparse
from driver.components.Component import Component


class EROTComponent(Component):
    COMMON = 0
    COMMON_FINISH = 0
    COMMON_SET_LOOP_BACK = 1
    COMMON_HDL_DEPOSIT = 2
    COMMON_HDL_FORCE = 3
    COMMON_HDL_READ = 4
    COMMON_WAIT_SIM_TIME = 5
    
    CAR = 1
    SIM_PRIV = 2
    SIM_PRIV_SYSCTRL = 10
    SIM_PRIV_FSP = 11
    SIM_PRIV_OOBHUB = 12

    SIM_PRIV_WRITE = 0
    SIM_PRIV_READ = 1
    SIM_PRIV_BURST_READ = 2
    SIM_PRIV_BURST_OPERATION = 3

    JTAG = 3
    JTAG_RESET = 0
    JTAG_LED = 1
    JTAG_TAP = 2
    JTAG_IRSCAN = 3
    JTAG_DRSCAN = 4
    JTAG_WAIT = 5

    AP1_I2C = 4
    AP2_I2C = 5
    BMC_I2C = 6

    AP0_SPI = 7
    AP1_SPI = 8
    BMC_SPI = 9

    I2C_READ = 1
    I2C_WRITE = 0

    def __init__(self, link, *args, **kwargs):
        super(EROTComponent, self).__init__(link, *args, **kwargs)

    def pack_value(self, v):
        return bytearray(struct.pack("<I", v))

    def unpack_value(self, v):
        return struct.unpack("<I", v)
