#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import *

with Test(sys.argv) as t:
    def parse_args():
        t.parser.add_argument("--IRWIDTH", help="Update IR Lengths", type=int, default=8)
        t.parser.add_argument("--IRINSTR_IDCODE", help="IR To Read IDCODE in hex string, e.g., ffab", type=str, default="0x2")
        t.parser.add_argument("--IRVALUE_IDCODE", help="Golden IDCODE", type=int, default=0x101a73d7)
        opts, unknown = t.parser.parse_known_args(sys.argv[1:])
        return opts

    options = parse_args() 
    
    helper.pinfo("JTAG IDCODE Test Starts!")
    golden_idcode = options.IRVALUE_IDCODE

    #Work Around to Let Test Runnable 
    if helper.target == "simv_fpga":
        helper.hdl_force('ntb_top.u_nv_fpga_dut.u_nv_top_fpga.u_nv_top_wrapper.u_nv_top.u_sra_top0.top_pads.u_GPIOB_pad_wrapper.GPIOB_pads.nvjtag_sel', 1)
    else:
        helper.hdl_force('ntb_top.u_nv_top.u_sra_top0.top_pads.u_GPIOB_pad_wrapper.GPIOB_pads.nvjtag_sel', 1)

    helper.jtag.Led(1)  # Start Testing
    
    helper.jtag.Reset(0)
    helper.jtag.Reset(1)
    
    helper.jtag.Tap(options.IRWIDTH)
    
    helper.pinfo("IRSCAN for Reading IDCODE %s " % options.IRINSTR_IDCODE)
    helper.jtag.IRScan(options.IRWIDTH, options.IRINSTR_IDCODE)

    helper.pinfo("Loading IDCODE")
    actual_idcode_byte_list = helper.jtag.DRScan(32, '0x00000000')
    actual_idcode           = int.from_bytes(actual_idcode_byte_list,'little')
    
    if actual_idcode != golden_idcode:
        helper.perror("Received a wrong IDCODE, expected %s while receiving %s" % (hex(golden_idcode), hex(actual_idcode)))
    else:
        helper.pinfo("Reading Expected IDCODE %s " % hex(actual_idcode) )
    helper.jtag.Led(0)  # End Testing
    
    helper.pinfo("JTAG IDCODE Test Ends!")


