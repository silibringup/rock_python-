#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
import os
import time
from driver import *

BMC_I2C_SLV_ADDR = 0x69
BMC_I2C_ID = 3

def check_cms2():
    helper.pinfo("Start checking CMS2 ...")

    # Byte 0: Component Memory Space (CMS)
    # Byte 1: Reserved
    # Byte 2~5: Indirect memory offset (IMO)
    helper.SMBus_write(OOB.SMCommand.INDIRECT_CTRL, [0x2, 0x0, 0x0, 0x0, 0x0])
    ACK = 0x4
    cms2_bytes = bytes()
    while helper.SMBus_poll(ACK, 0xff, OOB.SMCommand.INDIRECT_STATUS, 1):
        nbr_byte, rd_data = helper.erot_rcvy_block_read(slv_addr=BMC_I2C_SLV_ADDR, cmd_code=OOB.SMCommand.INDIRECT_DATA, ret_bytes_nbr=True)
        if nbr_byte == 0:
            break
        rd_data = rd_data.to_bytes(nbr_byte, 'little')
        cms2_bytes += rd_data

    has_ik_csr = int(cms2_bytes[268])
    if has_ik_csr != 0x55:
        helper.perror(f"cms2.has_ik_csr mismatch. exp = 0x55, act = {hex(has_ik_csr)}")

    helper.pinfo("Checking CMS2 completed")

with Test(sys.argv) as t:
    # recovery process is called before test by --rcv_boot
    check_cms2()

