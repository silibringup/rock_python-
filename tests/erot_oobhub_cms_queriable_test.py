#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
#This test ensure that CMS register can be accessed both by FSP and BMC (recovery I2C)
from driver import * 
import random

def cms_access(data):
    data_in = data & 0xff
    helper.pinfo(f'cms access with data {hex(data_in)}')
    #FSP writes to RECOVERY_CTRL.CMS register in OOBHUB.
    erot.OOBHUB.RCV_RECOVERY_CTRL_0_0.write(COMPONENT_MEM_SPACE=data_in)
    #FSP reads from RECOVERY_CTRL.CMS register back and compare with golden value
    rd_fsp = erot.OOBHUB.RCV_RECOVERY_CTRL_0_0.read()
    if rd_fsp['COMPONENT_MEM_SPACE'] != data_in:
        helper.perror("FSP read RCV_RECOVERY_CTRL_0_0.COMPONENT_MEM_SPACE Fail, expect 0x%x but read out 0x%x" % (data_in, rd_fsp['COMPONENT_MEM_SPACE']))
    else:
        helper.pinfo(f'FSP read out cms = {hex(rd_fsp["COMPONENT_MEM_SPACE"])}')
    #I2C BFM reads RECOVERY_CTRL.CMS register through recovery I2C controller and compare with golden value
    rd_i2c = helper.erot_rcvy_block_read(slv_addr=0x69, cmd_code=38)
    if rd_i2c & 0xff != data_in:
        helper.perror("I2C read RECOVERY_CTRL_0.Component_mem_space Fail, expect 0x%x but read out 0x%x" % (data_in, rd_i2c&0xff))
    else:
        helper.pinfo(f'I2C read out cms = {hex(rd_i2c&0xff)}')

with Test(sys.argv) as t:
    def parse_args():
        t.parser.add_argument("--unit", action='store', help="Unit To Light On, Support Regular Expression", default='.*')
        t.parser.add_argument("--single", action='store_true', help="single slave or two slaves in this test")
        opts, unknown = t.parser.parse_known_args(sys.argv[1:])
        return opts
  
    options = parse_args() 

    #Test start
    helper.set_loop_back(0)

    for i in range(10):
        data = random.randint(0x0, 0xff)
        cms_access(data)

