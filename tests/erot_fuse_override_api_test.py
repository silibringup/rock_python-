#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import *

###################################################
# This test intends to cover:
# 1. *req_addr[0] and *req_addr[25] from 4 masters
# 2. *_resp_pri_error from fabric to master
###################################################
with Test(sys.argv) as t:
    helper.log("test start")
    #jtag unlock
    helper.wait_sim_time("us", 50)
    helper.hdl_force('ntb_top.u_nv_fpga_dut.u_nv_top_fpga.u_nv_top_wrapper.u_nv_top.nvjtag_sel', 1)

    helper.jtag.Reset(0)
    helper.jtag.DRScan(100, hex(0x0)) #add some delay as jtag only work when nvjtag_sel stable in real case
    helper.jtag.Reset(1)


    helper.pinfo(f'j2h_unlock sequence start')
    helper.j2h_unlock()
    helper.pinfo(f'j2h_unlock sequence finish')

    helper.jtag.DRScan(100, hex(0x0)) #add some delay as jtag only work when nvjtag_sel stable in real case
    
    opt_security_mode_addr = 5468 + erot.FUSE.base
    opt_data = helper.j2h_read(opt_security_mode_addr)
    helper.log(f"the opt_security_mode_addr value is {opt_data}")

    test_api.fuse_opts_override("opt_secure_pri_source_isolation_en", 1, debug_mode=1)
    test_api.fuse_opts_override("opt_en_reserved_1", 10100101101010101010101010101010, debug_mode=1)
    test_api.fuse_opts_override("opt_fsp_peregrine_reserved", 10100101, debug_mode=1)
    helper.log("test finish")
