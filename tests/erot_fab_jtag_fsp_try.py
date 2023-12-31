#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import * 

with Test(sys.argv) as t:
    OOBHUB_FABRIC_BASE = 0x2000000000000000
    #jtag unlock
    helper.log("Test start")
    helper.wait_sim_time("us", 50)
    helper.hdl_force('ntb_top.u_nv_fpga_dut.u_nv_top_fpga.u_nv_top_wrapper.u_nv_top.nvjtag_sel', 1)

    helper.jtag.Reset(0)
    helper.jtag.DRScan(100, hex(0x0)) #add some delay as jtag only work when nvjtag_sel stable in real case
    helper.jtag.Reset(1)


    helper.pinfo(f'j2h_unlock sequence start')
    helper.j2h_unlock()
    helper.pinfo(f'j2h_unlock sequence finish')

    helper.jtag.DRScan(100, hex(0x0)) #add some delay as jtag only work when nvjtag_sel stable in real case
    
    helper.log("start to use fsp write")
    reg = erot.L1_CSR.CLOCK_SYS_CTL_BLF_WRITE_CTL_0
    masked_write_value = 0xabcdefad & reg.write_mask
    helper.log("write data is %x" % (masked_write_value))
    reg.write(masked_write_value)

    helper.log("start to use fsp read")
    test_read_value = reg.read()
    masked_value = test_read_value.value & reg.read_mask

    helper.log("read data is %x" % (masked_value))
