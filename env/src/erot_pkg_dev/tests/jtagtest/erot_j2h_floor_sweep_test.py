#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import *
import random
import argparse
import re
import os

LIGHT_ON_LIST = [
    {'name' : 'I2C_IB0',        'reg' : erot.I2C_IB0.I2C_CMD_DATA1_0                    }, 
    {'name' : 'I2C_IB1',        'reg' : erot.I2C_IB1.I2C_CMD_DATA2_0                    }, 
    {'name' : 'IO_EXPANDER',    'reg' : erot.IO_EXPANDER.I2C_CMD_DATA2_0                }, 
    {'name' : 'SPI_IB0',        'reg' : erot.SPI_IB0.COMMAND2_0                         }, 
    {'name' : 'SPI_IB1',        'reg' : erot.SPI_IB1.COMMAND2_0                         }, 
    {'name' : 'OOBHUB_SPI',     'reg' : erot.OOBHUB_SPI.COMMAND2_0                      }, 
]


with Test(sys.argv) as t:
    def validate_unit(unit, exp):
        unit['reg'].write(exp)
        helper.pinfo(f"write {hex(exp)} to {unit['reg'].name}")
        rd = unit['reg'].read()
        if rd.value != exp & unit['reg'].read_mask:
            helper.perror("Reg Read/Write Fail -> %s" % str(unit['reg']))
        else:
            helper.pinfo(f"read {hex(rd.value)} from {unit['reg'].name} matched")
    
    helper.jtag.Reset(0)
    helper.jtag.Reset(1)

    helper.j2h_unlock()

    for i in range(3):
        exp = 0xf0f0f0f0 + i + 1
        for unit in LIGHT_ON_LIST:
            validate_unit(unit, exp)



