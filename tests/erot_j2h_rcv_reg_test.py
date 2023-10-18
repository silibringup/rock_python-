#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import *
import argparse
import re
import os
import random

with Test(sys.argv) as t:
    REG_LIST = [
        {'addr': 0x8aa128, 'reg': erot.OOBHUB.RCV_STATUS_0_0, 'direction': 'READ'}, 
        {'addr': 0x8aa148, 'reg': erot.OOBHUB.RCV_RECOVERY_STATUS_0_0, 'direction': 'READ'},
        {'addr': 0x8aa144, 'reg': erot.OOBHUB.RCV_RECOVERY_CTRL_0_0, 'direction': 'WRITE'},
        {'addr': 0x8aa14c, 'reg': erot.OOBHUB.RCV_INDIRECT_CTRL_0_0, 'direction': 'WRITE'},
        {'addr': 0x8aa150, 'reg': erot.OOBHUB.RCV_INDIRECT_CTRL_1_0, 'direction': 'WRITE'},
        {'addr': 0x8aa15c, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_0, 'direction': 'WRITE'},
        {'addr': 0x8aa160, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_1, 'direction': 'WRITE'},
        {'addr': 0x8aa164, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_2, 'direction': 'WRITE'},
        {'addr': 0x8aa168, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_3, 'direction': 'WRITE'},
        {'addr': 0x8aa16c, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_4, 'direction': 'WRITE'},
        {'addr': 0x8aa170, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_5, 'direction': 'WRITE'},
        {'addr': 0x8aa174, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_6, 'direction': 'WRITE'},
        {'addr': 0x8aa178, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_7, 'direction': 'WRITE'},
        {'addr': 0x8aa17c, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_8, 'direction': 'WRITE'},
        {'addr': 0x8aa180, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_9, 'direction': 'WRITE'},
        {'addr': 0x8aa184, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_10, 'direction': 'WRITE'},
        {'addr': 0x8aa188, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_11, 'direction': 'WRITE'},
        {'addr': 0x8aa18c, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_12, 'direction': 'WRITE'},
        {'addr': 0x8aa190, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_13, 'direction': 'WRITE'},
        {'addr': 0x8aa194, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_14, 'direction': 'WRITE'},
        {'addr': 0x8aa198, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_15, 'direction': 'WRITE'},
        {'addr': 0x8aa19c, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_16, 'direction': 'WRITE'},
        {'addr': 0x8aa1a0, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_17, 'direction': 'WRITE'},
        {'addr': 0x8aa1a4, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_18, 'direction': 'WRITE'},
        {'addr': 0x8aa1a8, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_19, 'direction': 'WRITE'},
        {'addr': 0x8aa1ac, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_20, 'direction': 'WRITE'},
        {'addr': 0x8aa1b0, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_21, 'direction': 'WRITE'},
        {'addr': 0x8aa1b4, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_22, 'direction': 'WRITE'},
        {'addr': 0x8aa1b8, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_23, 'direction': 'WRITE'},
        {'addr': 0x8aa1bc, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_24, 'direction': 'WRITE'},
        {'addr': 0x8aa1c0, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_25, 'direction': 'WRITE'},
        {'addr': 0x8aa1c4, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_26, 'direction': 'WRITE'},
        {'addr': 0x8aa1c8, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_27, 'direction': 'WRITE'},
        {'addr': 0x8aa1cc, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_28, 'direction': 'WRITE'},
        {'addr': 0x8aa1d0, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_29, 'direction': 'WRITE'},
        {'addr': 0x8aa1d4, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_30, 'direction': 'WRITE'},
        {'addr': 0x8aa1d8, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_31, 'direction': 'WRITE'},
        {'addr': 0x8aa1dc, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_32, 'direction': 'WRITE'},
        {'addr': 0x8aa1e0, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_33, 'direction': 'WRITE'},
        {'addr': 0x8aa1e4, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_34, 'direction': 'WRITE'},
        {'addr': 0x8aa1e8, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_35, 'direction': 'WRITE'},
        {'addr': 0x8aa1ec, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_36, 'direction': 'WRITE'},
        {'addr': 0x8aa1f0, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_37, 'direction': 'WRITE'},
        {'addr': 0x8aa1f4, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_38, 'direction': 'WRITE'},
        {'addr': 0x8aa1f8, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_39, 'direction': 'WRITE'},
        {'addr': 0x8aa1fc, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_40, 'direction': 'WRITE'},
        {'addr': 0x8aa200, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_41, 'direction': 'WRITE'},
        {'addr': 0x8aa204, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_42, 'direction': 'WRITE'},
        {'addr': 0x8aa208, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_43, 'direction': 'WRITE'},
        {'addr': 0x8aa20c, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_44, 'direction': 'WRITE'},
        {'addr': 0x8aa210, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_45, 'direction': 'WRITE'},
        {'addr': 0x8aa214, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_46, 'direction': 'WRITE'},
        {'addr': 0x8aa218, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_47, 'direction': 'WRITE'},
        {'addr': 0x8aa21c, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_48, 'direction': 'WRITE'},
        {'addr': 0x8aa220, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_49, 'direction': 'WRITE'},
        {'addr': 0x8aa224, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_50, 'direction': 'WRITE'},
        {'addr': 0x8aa228, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_51, 'direction': 'WRITE'},
        {'addr': 0x8aa22c, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_52, 'direction': 'WRITE'},
        {'addr': 0x8aa230, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_53, 'direction': 'WRITE'},
        {'addr': 0x8aa234, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_54, 'direction': 'WRITE'},
        {'addr': 0x8aa238, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_55, 'direction': 'WRITE'},
        {'addr': 0x8aa23c, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_56, 'direction': 'WRITE'},
        {'addr': 0x8aa240, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_57, 'direction': 'WRITE'},
        {'addr': 0x8aa244, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_58, 'direction': 'WRITE'},
        {'addr': 0x8aa248, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_59, 'direction': 'WRITE'},
        {'addr': 0x8aa24c, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_60, 'direction': 'WRITE'},
        {'addr': 0x8aa250, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_61, 'direction': 'WRITE'},
        {'addr': 0x8aa254, 'reg': erot.OOBHUB.RCV_INDIRECT_DATA_62, 'direction': 'WRITE'},
        {'addr': 0x8aa358, 'reg': erot.OOBHUB.RCV_INDIRECT_CMS_STATUS_0, 'direction': 'WRITE'},
        {'addr': 0x8aa154, 'reg': erot.OOBHUB.RCV_INDIRECT_STATUS_0_0, 'direction': 'READ'},
        {'addr': 0x8aa154, 'reg': erot.OOBHUB.RCV_INDIRECT_STATUS_0_0, 'direction': 'WRITE'},
        {'addr': 0x8aa144, 'reg': erot.OOBHUB.RCV_RECOVERY_CTRL_0_0, 'direction': 'WRITE'},
        {'addr': 0x8aa134, 'reg': erot.OOBHUB.RCV_STATUS_3_0, 'direction': 'READ'},
        {'addr': 0x8aa374, 'reg': erot.OOBHUB.RCV_INDIRECT_CMS2_MEM_RD_ADDR_0, 'direction': 'WRITE'},
        {'addr': 0x8aa378, 'reg': erot.OOBHUB.RCV_INDIRECT_CMS2_MEM_RD_DATA_0, 'direction': 'READ'}
    ]

    def parse_args():
        t.parser.add_argument("--ADDR", help="L1/L2 Address to acess", type=int, default=0x91_400c)
        t.parser.add_argument("--DATA", help="Data to write and read to compare", type=int, default=0xa5a5a5a5)
        t.parser.add_argument("--i", help="input file", type=str, default="dft_j2h_PFNL.log")
        opts, unknown = t.parser.parse_known_args(sys.argv[1:])
        return opts

    options = parse_args() 

        
    helper.pinfo("JTAG J2H Test Starts!")
    helper.wait_sim_time('us', 50)
    if helper.target == "simv_fpga":
        helper.hdl_force('ntb_top.u_nv_fpga_dut.u_nv_top_fpga.u_nv_top_wrapper.u_nv_top.nvjtag_sel', 1)
    if helper.target != "simv_fpga":
        helper.pinfo(f'remove fuse force')
        #helper.hdl_force('ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.opt_nvjtag_protection_enable_final', 0)
        #helper.hdl_force('ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.opt_secure_jtag_secureID_valid', 0)
        #helper.hdl_force('ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.static_chip_option_sense_done', 1)
        #helper.hdl_force('ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.opt_secure_jtag_secureID_valid_inv', 1)
        helper.hdl_force('ntb_top.u_nv_top.nvjtag_sel', 1)
        

    helper.jtag.Led(1)  # Start Testing
    
    helper.jtag.Reset(0)
    helper.jtag.DRScan(100, hex(0x0)) #add some delay as jtag only work when nvjtag_sel stable in real case
    helper.jtag.Reset(1)  

    #unlock j2h interface
    helper.j2h_unlock()

    #poll L3 reset released
    cnt = 0
    l3_released = 0
    while l3_released == 0 and cnt < 10:
        rd = helper.j2h_read(0x33010, check_ack=False) #erot.RESeET.NVEROT_RESET_CFG.SW_L3_RST_0
        cnt += 1
        if rd & 0x1 == 1:
            l3_released = 1
    if l3_released == 0:
        helper.perror(f'L3_reset not released before w/r registers')

    #Access register list
    for i in range(len(REG_LIST)):
        if REG_LIST[i]['reg'] == erot.OOBHUB.RCV_INDIRECT_CTRL_0_0:
            data = random.choice([0x000001, 0x000000])
        else:
            data = random.randint(0x0, 0xffffffff)

        if REG_LIST[i]['direction'] == 'READ':
            REG_LIST[i]['reg'].write(data)
            #poll
            cnt = 0
            matched = 0 
            while matched == 0 and cnt < 10:
                rd = helper.j2h_read(REG_LIST[i]['addr'])
                cnt += 1
                if (rd & REG_LIST[i]['reg'].write_mask) == (data & REG_LIST[i]['reg'].write_mask):
                    matched = 1
                    helper.pinfo(f"J2H read out {REG_LIST[i]['reg']} {hex(rd)}")
            if matched == 0:
                helper.perror(f"J2H read out {REG_LIST[i]['reg']} {hex(rd & REG_LIST[i]['reg'].write_mask)} but expect {hex(data & REG_LIST[i]['reg'].write_mask)}")
            
            #rd = helper.j2h_read(REG_LIST[i]['addr'])
            #if (rd & REG_LIST[i]['reg'].write_mask) != (data & REG_LIST[i]['reg'].write_mask):
            #    helper.perror(f"J2H read out {REG_LIST[i]['reg']} {hex(rd & REG_LIST[i]['reg'].write_mask)} but expect {hex(data & REG_LIST[i]['reg'].write_mask)}")
            #else:
            #    helper.pinfo(f"J2H read out {REG_LIST[i]['reg']} {hex(rd)}")
        elif REG_LIST[i]['direction'] == 'WRITE':
            helper.j2h_write(REG_LIST[i]['addr'], data)
            #poll
            cnt = 0
            matched = 0 
            while matched == 0 and cnt < 10:
                rd = REG_LIST[i]['reg'].read()
                cnt += 1
                if (rd.value & REG_LIST[i]['reg'].write_mask) == (data & REG_LIST[i]['reg'].write_mask):
                    matched = 1
                    helper.pinfo(f"FSP read out {REG_LIST[i]['reg']} {hex(rd.value)}")
            if matched == 0:
                helper.perror(f"FSP read out {REG_LIST[i]['reg']} {hex(rd.value & REG_LIST[i]['reg'].write_mask)} but expect {hex(data & REG_LIST[i]['reg'].write_mask)}")           

            #rd = REG_LIST[i]['reg'].read()
            #if (rd.value & REG_LIST[i]['reg'].write_mask) != (data & REG_LIST[i]['reg'].write_mask):
            #    helper.perror(f"FSP read out {REG_LIST[i]['reg']} {hex(rd.value & REG_LIST[i]['reg'].write_mask)} but expect {hex(data & REG_LIST[i]['reg'].write_mask)}")
            #else:
            #    helper.pinfo(f"FSP read out {REG_LIST[i]['reg']} {hex(rd.value)}")
        else:
            helper.perror(f"invalid keyword of direction {REG_LIST[i]['direction']}")
