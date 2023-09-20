#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import *


BMC_I2C_SLV_ADDR = 0x69
BMC_I2C_ID = 3

with Test(sys.argv) as t:
    helper.pinfo("Start interacting with FMC ...")
    gdata = 0x1234abcd
    I2C_CMD_DATA1_0 = erot.I2C_IB1.I2C_CMD_DATA1_0
    addr = I2C_CMD_DATA1_0.block.base + I2C_CMD_DATA1_0.offset
    helper.pinfo(f"Write {hex(gdata)} to {hex(addr)}")
    helper.hw_proxy_write(addr, gdata)
    helper.pinfo(f"Read data from {hex(addr)} to check")
    rdata = helper.hw_proxy_read(addr)
    if rdata != gdata:
        helper.perror(f"Mismatch, exp: {hex(gdata)}, act: {hex(rdata)}")
    else:
        helper.pinfo(f"Match {hex(gdata)}@{hex(addr)}")




