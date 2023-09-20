#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import * 
import math


with Test(sys.argv) as t:
    
    erot_l0_reset_domain_regs = [
        erot.NV_PMC.SCRATCH_RESET_0_0
    ]

    erot_l1_reset_domain_regs = [
        erot.NV_PMC.SCRATCH_RESET_1_0,
    ]

    erot_l3_reset_domain_regs = [
        erot.NV_PMC.SCRATCH_RESET_2_0
    ]


    def reg_cfg():
        for l0_reg in erot_l0_reset_domain_regs:
            l0_reg.debug_write(0x5a5a5a5a)
        helper.log("finish L1 reg init")
        for l1_reg in erot_l1_reset_domain_regs:
            l1_reg.debug_write(0x5a5a5a5a)
        helper.log("finish L1 reg init")
        for l3_reg in erot_l3_reset_domain_regs:
            l3_reg.debug_write(0x5a5a5a5a)
        helper.log("finish L3 reg init")

    def l0_rst_domain_reg_check():
        rd = erot.NV_PMC.SCRATCH_RESET_0_0.debug_read()
        mask = erot.NV_PMC.SCRATCH_RESET_0_0.read_mask
        act = rd.value & mask
        exp = 0x5a5a5a5a & mask
        if act != exp:
            helper.perror("Mismatch, erot.NV_PMC.SCRATCH_RESET_0_0's value is not update to desired value")
        helper.log("L0 reset domain reg check done")



    def l1_rst_domain_reg_check():
        for l1_reg in erot_l1_reset_domain_regs:
            rd = l1_reg.debug_read()
            mask = l1_reg.read_mask
            act = rd.value & mask
            exp = 0x5a5a5a5a & mask
            if act != exp:
                helper.perror("Mismatch, %s's value is not as expected" % l1_reg.name)
        helper.log("L1 reset domain reg check done")


    def l3_rst_domain_reg_check(after_reset):
        for l3_reg in erot_l3_reset_domain_regs:
            rd = l3_reg.debug_read()
            if not after_reset:
                mask = l3_reg.read_mask
                act = rd.value & mask
                exp = 0x5a5a5a5a & mask
            else:
                mask = l3_reg.reset_mask & l3_reg.read_mask
                act = rd.value & mask
                exp = l3_reg.reset_val & mask
            if act != exp:
                helper.perror("Mismatch, %s's value is not as expected" % l3_reg.name)
        helper.log("L3 reset domain reg check done")


    

    helper.log("Test start")
    helper.wait_sim_time("us", 50)
    helper.hdl_force('ntb_top.u_nv_fpga_dut.u_nv_top_fpga.u_nv_top_wrapper.u_nv_top.nvjtag_sel', 1)

    helper.jtag.Reset(0)
    helper.jtag.DRScan(100, hex(0x0)) #add some delay as jtag only work when nvjtag_sel stable in real case
    helper.jtag.Reset(1)  

    #unlock j2h interface
    helper.pinfo(f'j2h_unlock sequence start')
    helper.j2h_unlock()
    helper.pinfo(f'j2h_unlock sequence finish') 


    reg_cfg()
    helper.wait_sim_time("us", 5)
   
    erot.RESET.NVEROT_RESET_CFG.SW_L3_RST_0.write(RESET_LEVEL3=0)

    helper.wait_sim_time("us", 50)

    l0_rst_domain_reg_check()
    l1_rst_domain_reg_check()
    l3_rst_domain_reg_check(after_reset=1)

    helper.log("Configure L3 SW reset one-by-one")





