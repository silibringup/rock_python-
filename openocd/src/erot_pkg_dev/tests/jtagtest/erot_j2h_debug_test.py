#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
#erot_top sim: vrun run_test -u erot_top -py erot_j2h_debug_test.py --platform JTAG -pyarg "--log_level DEBUG" -w
#fpga sim: nvrun run_test -u erot_fpga -py erot_j2h_debug_test.py --platform JTAG -pyarg "--log_level DEBUG" -pyarg "--target simv_fpga" -pyarg "--disable_peripheral_init_agent True" -w
from driver import *
import argparse
import re
import os

#If waiting at idle state is not needed, run with '--wait False'
with Test(sys.argv) as t:
    def parse_args():
        t.parser.add_argument("--ADDR", help="L1/L2 Address to acess", type=int, default=0x91_400c)
        t.parser.add_argument("--DATA", help="Data to write and read to compare", type=int, default=0xa5a5a5a5)
        t.parser.add_argument("--i", help="input file", type=str, default="dft_j2h_PFNL.log")
        opts, unknown = t.parser.parse_known_args(sys.argv[1:])
        return opts

    options = parse_args() 

    #cur_path = os.path.dirname(os.path.abspath(__file__))
    #file_in = cur_path + '/' + options.i
          
    helper.pinfo("JTAG J2H Debug Test Starts!")

    if helper.target == "simv_fpga":
        helper.hdl_force('ntb_top.u_nv_fpga_dut.u_nv_top_fpga.u_nv_top_wrapper.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.opt_nvjtag_protection_enable_final', 0)
        helper.hdl_force('ntb_top.u_nv_fpga_dut.u_nv_top_fpga.u_nv_top_wrapper.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.opt_secure_jtag_secureID_valid', 0)
        helper.hdl_force('ntb_top.u_nv_fpga_dut.u_nv_top_fpga.u_nv_top_wrapper.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.static_chip_option_sense_done', 1)
        helper.hdl_force('ntb_top.u_nv_fpga_dut.u_nv_top_fpga.u_nv_top_wrapper.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.opt_secure_jtag_secureID_valid_inv', 1)
        helper.hdl_force('ntb_top.u_nv_fpga_dut.u_nv_top_fpga.u_nv_top_wrapper.u_nv_top.nvjtag_sel', 1)
    if helper.target != "simv_fpga":
        helper.hdl_force('ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.opt_nvjtag_protection_enable_final', 0)
        helper.hdl_force('ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.opt_secure_jtag_secureID_valid', 0)
        helper.hdl_force('ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.static_chip_option_sense_done', 1)
        helper.hdl_force('ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.opt_secure_jtag_secureID_valid_inv', 1)
        helper.hdl_force('ntb_top.u_nv_top.nvjtag_sel', 1)

    helper.jtag.Led(1)  # Start Testing
    
    helper.jtag.Reset(0)
    helper.jtag.Reset(1)   

    #unlock j2h interface
    helper.j2h_unlock()
      
    #J2H write to sysctrl register
    helper.j2h_write(0x1080, 0x5a5a5a5a)
    #J2H read from sysctrl register
    act_data = helper.j2h_read(0x1080)
    if act_data != 0x5a5a5a5a:
        helper.perror("Receive wrong read data from TDO, expected 0x5a5a5a5a while receiving 0x%x" % (act_data))

    #J2H write to i2c0 register
    helper.j2h_write(0x91400c, 0x5a5a5a5a)
    #J2H read from i2c0 register
    act_data = helper.j2h_read(0x91400c)
    if act_data != 0x5a5a5a5a:
        helper.perror("Receive wrong read data from TDO, expected 0x5a5a5a5a while receiving 0x%x" % (act_data))
    

    #J2H write
    helper.j2h_write(options.ADDR, options.DATA)
    #J2H read
    act_data = helper.j2h_read(options.ADDR)
    if act_data != options.DATA:
        helper.perror("Receive wrong read data from TDO, expected 0x%x while receiving 0x%x" % (options.DATA, act_data))
    
    helper.jtag.Led(0)  # End Testing
    
    helper.pinfo("JTAG J2H Debug Test Ends!")


