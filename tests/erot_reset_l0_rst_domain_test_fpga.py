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
        helper.log("finish L0 reg init")
        for l1_reg in erot_l1_reset_domain_regs:
            l1_reg.debug_write(0x5a5a5a5a)
        helper.log("finish L1 reg init")
        for l3_reg in erot_l3_reset_domain_regs:
            l3_reg.debug_write(0x5a5a5a5a)
        helper.log("finish L3 reg init")

    def l0_rst_domain_reg_check(after_reset):
        for l0_reg in erot_l0_reset_domain_regs:
            rd = l0_reg.debug_read()
            if not after_reset:
                mask = l0_reg.read_mask
                act = rd.value & mask
                exp = 0x5a5a5a5a & mask
            else:
                mask = l0_reg.reset_mask & l0_reg.read_mask
                act = rd.value & mask
                exp = l0_reg.reset_val & mask
            if act != exp:
                helper.perror("Mismatch, %s's value is not as expected" % l0_reg.name)
            helper.log(f'reg name: {l0_reg.name}, act: {hex(act)}, exp: {hex(exp)}')
        helper.log("L0 reset domain reg check done")

    def l1_rst_domain_reg_check(after_reset):
        for l1_reg in erot_l1_reset_domain_regs:
            rd = l1_reg.debug_read()
            if not after_reset:
                mask = l1_reg.read_mask
                act = rd.value & mask
                exp = 0x5a5a5a5a & mask
            else:
                mask = l1_reg.reset_mask & l1_reg.read_mask
                act = rd.value & mask
                exp = l1_reg.reset_val & mask
            if act != exp:
                helper.perror("Mismatch, %s's value is not as expected" % l1_reg.name)
            helper.log(f'reg name: {l1_reg.name}, act: {hex(act)}, exp: {hex(exp)}')
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
            helper.log(f'reg name: {l3_reg.name}, act: {hex(act)}, exp: {hex(exp)}')
        helper.log("L3 reset domain reg check done")

    def chk_reg_rst_value(reg):
        if not isinstance(reg, Rock_reg):
            helper.perror("parameter is not a Rock_reg")
            return
        rd = reg.debug_read()
        mask = reg.reset_mask & reg.read_mask
        act = rd.value & mask
        exp = reg.reset_val & mask
        if act != exp:
            helper.perror("Mismatch, %s's value is not as expected" % reg.name)

    def deassert_sw_reset_l1():
        erot.RESET.NVEROT_RESET_CFG.SW_GPIO_CTRL_RST_0.debug_write(RESET_GPIO_CTRL=1)
        erot.RESET.NVEROT_RESET_CFG.SW_SPIMON0_RST_0.debug_write(RESET_SPIMON0=1)
        erot.RESET.NVEROT_RESET_CFG.SW_SPIMON1_RST_0.debug_write(RESET_SPIMON1=1)
        
    def deassert_sw_reset_l3():
        erot.RESET.NVEROT_RESET_CFG.SW_IB0_SPI_RST_0.debug_write(RESET_IB0_SPI=1)
        erot.RESET.NVEROT_RESET_CFG.SW_IB1_SPI_RST_0.debug_write(RESET_IB1_SPI=1)
        erot.RESET.NVEROT_RESET_CFG.SW_OOB_SPI_RST_0.debug_write(RESET_OOB_SPI=1)
        erot.RESET.NVEROT_RESET_CFG.SW_IB0_I2C_RST_0.debug_write(RESET_IB0_I2C=1)
        erot.RESET.NVEROT_RESET_CFG.SW_IB1_I2C_RST_0.debug_write(RESET_IB1_I2C=1)
        erot.RESET.NVEROT_RESET_CFG.SW_IO_EXP_RST_0.debug_write(RESET_IO_EXP=1)
        erot.RESET.NVEROT_RESET_CFG.SW_UART_RST_0.debug_write(RESET_UART=1)

    def ck_ok_assert_l0_rst():
        helper.jtag.Reset(0)
        helper.jtag.Reset(1)
        ir_scan_out = helper.jtag_IRScan(10, 0x018) #Cycle 13
        dr_scan_out = helper.jtag_DRScan(19, 0x00000) #Cycle 30
        ir_scan_out = helper.jtag_IRScan(16, 0x0600) #Cycle 121
        dr_scan_out = helper.jtag_DRScan(19, 0x00080) #Cycle 143
        ir_scan_out = helper.jtag_IRScan(16, 0x0520) #Cycle 167
        ir_scan_out = helper.jtag_IRScan(25, 0x00a1520) #Cycle 189
        dr_scan_out = helper.jtag_DRScan(11, 0x220) #Cycle 220
        dr_scan_out = helper.jtag_DRScan(121, 0x0600000000000000003000000000220) #Cycle 236
        ir_scan_out = helper.jtag_IRScan(25, 0x00a1520) #Cycle 181307
        dr_scan_out = helper.jtag_DRScan(121, 0x0600000000000000003000000000220) #Cycle 181338
        ir_scan_out = helper.jtag_IRScan(25, 0x0120280) #Cycle 181468
        dr_scan_out = helper.jtag_DRScan(7, 0x40) #Cycle 181499
        dr_scan_out = helper.jtag_DRScan(15, 0x00c0) #Cycle 181511
        ir_scan_out = helper.jtag_IRScan(16, 0x0840) #Cycle 181535
        dr_scan_out = helper.jtag_DRScan(17, 0x1ffff) #Cycle 181557
        ir_scan_out = helper.jtag_IRScan(10, 0x014) #Cycle 181583
        ir_scan_out = helper.jtag_IRScan(16, 0x8800) #Cycle 181599
        dr_scan_out = helper.jtag_DRScan(7, 0x40) #Cycle 181621
        dr_scan_out = helper.jtag_DRScan(457, 0x0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000040) #Cycle 181633
        ir_scan_out = helper.jtag_IRScan(16, 0x0740) #Cycle 182099
        dr_scan_out = helper.jtag_DRScan(3076, 0x2000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001) #Cycle 182121
        ir_scan_out = helper.jtag_IRScan(10, 0x01d) #Cycle 185206
        dr_scan_out = helper.jtag_DRScan(3076, 0x4000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001) #Cycle 185222
        ir_scan_out = helper.jtag_IRScan(10, 0x01d) #Cycle 244307
        dr_scan_out = helper.jtag_DRScan(3076, 0x6000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001) #Cycle 244323
        ir_scan_out = helper.jtag_IRScan(10, 0x01d) #Cycle 247408
        dr_scan_out = helper.jtag_DRScan(3076, 0x8000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001) #Cycle 247424
        ir_scan_out = helper.jtag_IRScan(10, 0x025) #Cycle 250519
        dr_scan_out = helper.jtag_DRScan(9, 0x001) #Cycle 250535
        ir_scan_out = helper.jtag_IRScan(10, 0x014) #Cycle 250553
        ir_scan_out = helper.jtag_IRScan(16, 0x0530) #Cycle 250569
        ir_scan_out = helper.jtag_IRScan(34, 0x0d8364d90) #Cycle 250591
        dr_scan_out = helper.jtag_DRScan(13, 0x1ff0) #Cycle 250631
        ir_scan_out = helper.jtag_IRScan(34, 0x3e5f97e50) #Cycle 250649
        ir_scan_out = helper.jtag_IRScan(10, 0x3e5) #Cycle 250689
        dr_scan_out = helper.jtag_DRScan(21, 0x000000) #Cycle 250705
        ir_scan_out = helper.jtag_IRScan(10, 0x3e5) #Cycle 251735
        dr_scan_out = helper.jtag_DRScan(21, 0x000000) #Cycle 251751
        ir_scan_out = helper.jtag_IRScan(10, 0x014) #Cycle 251781
        ir_scan_out = helper.jtag_IRScan(16, 0x3600) #Cycle 251797
        dr_scan_out = helper.jtag_DRScan(7, 0x70) #Cycle 251819
        ir_scan_out = helper.jtag_IRScan(34, 0x3e4f97e50) #Cycle 251831
        dr_scan_out = helper.jtag_DRScan(57, 0x000010000400010) #Cycle 251871
        ir_scan_out = helper.jtag_IRScan(34, 0x014f97e40) #Cycle 252437
        ir_scan_out = helper.jtag_IRScan(25, 0x00ae3e0) #Cycle 252477
        dr_scan_out = helper.jtag_DRScan(22, 0x100001) #Cycle 252508
        ir_scan_out = helper.jtag_IRScan(10, 0x014) #Cycle 252600
        ir_scan_out = helper.jtag_IRScan(16, 0x0510) #Cycle 252616
        ir_scan_out = helper.jtag_IRScan(25, 0x00ac150) #Cycle 252638
        ir_scan_out = helper.jtag_IRScan(10, 0x017) #Cycle 252669
        ir_scan_out = helper.jtag_IRScan(10, 0x014) #Cycle 252685
        LOG("CK_OK assert L0_rst_")


    def ck_ok_deassert_l0_rst():
        helper.jtag.Reset(0)
        helper.jtag.Reset(1)
        ir_scan_out = helper.jtag_IRScan(10, 0x018) #Cycle 13
        dr_scan_out = helper.jtag_DRScan(19, 0x00000) #Cycle 30
        ir_scan_out = helper.jtag_IRScan(16, 0x0600) #Cycle 121
        dr_scan_out = helper.jtag_DRScan(19, 0x00080) #Cycle 143
        ir_scan_out = helper.jtag_IRScan(16, 0x0520) #Cycle 167
        ir_scan_out = helper.jtag_IRScan(25, 0x00a1520) #Cycle 189
        dr_scan_out = helper.jtag_DRScan(11, 0x220) #Cycle 220
        dr_scan_out = helper.jtag_DRScan(121, 0x0600000000000000003000000000220) #Cycle 236
        ir_scan_out = helper.jtag_IRScan(25, 0x00a1520) #Cycle 181307
        dr_scan_out = helper.jtag_DRScan(121, 0x0600000000000000003000000000220) #Cycle 181338
        ir_scan_out = helper.jtag_IRScan(25, 0x0120280) #Cycle 181468
        dr_scan_out = helper.jtag_DRScan(7, 0x40) #Cycle 181499
        dr_scan_out = helper.jtag_DRScan(15, 0x00c0) #Cycle 181511
        ir_scan_out = helper.jtag_IRScan(16, 0x0840) #Cycle 181535
        dr_scan_out = helper.jtag_DRScan(17, 0x1ffff) #Cycle 181557
        ir_scan_out = helper.jtag_IRScan(10, 0x014) #Cycle 181583
        ir_scan_out = helper.jtag_IRScan(16, 0x8800) #Cycle 181599
        dr_scan_out = helper.jtag_DRScan(7, 0x40) #Cycle 181621
        dr_scan_out = helper.jtag_DRScan(457, 0x0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000040) #Cycle 181633
        ir_scan_out = helper.jtag_IRScan(16, 0x0740) #Cycle 182099
        dr_scan_out = helper.jtag_DRScan(3076, 0x2000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001) #Cycle 182121
        ir_scan_out = helper.jtag_IRScan(10, 0x01d) #Cycle 185206
        dr_scan_out = helper.jtag_DRScan(3076, 0x4000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001) #Cycle 185222
        ir_scan_out = helper.jtag_IRScan(10, 0x01d) #Cycle 244307
        dr_scan_out = helper.jtag_DRScan(3076, 0x6000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001) #Cycle 244323
        ir_scan_out = helper.jtag_IRScan(10, 0x01d) #Cycle 247408
        dr_scan_out = helper.jtag_DRScan(3076, 0x8000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001) #Cycle 247424
        ir_scan_out = helper.jtag_IRScan(10, 0x025) #Cycle 250519
        dr_scan_out = helper.jtag_DRScan(9, 0x001) #Cycle 250535
        ir_scan_out = helper.jtag_IRScan(10, 0x014) #Cycle 250553
        ir_scan_out = helper.jtag_IRScan(16, 0x0530) #Cycle 250569
        ir_scan_out = helper.jtag_IRScan(34, 0x0d8364d90) #Cycle 250591
        dr_scan_out = helper.jtag_DRScan(13, 0x1ff0) #Cycle 250631
        ir_scan_out = helper.jtag_IRScan(34, 0x3e5f97e50) #Cycle 250649
        ir_scan_out = helper.jtag_IRScan(10, 0x3e5) #Cycle 250689
        dr_scan_out = helper.jtag_DRScan(21, 0x000000) #Cycle 250705
        ir_scan_out = helper.jtag_IRScan(10, 0x3e5) #Cycle 251735
        dr_scan_out = helper.jtag_DRScan(21, 0x000000) #Cycle 251751
        ir_scan_out = helper.jtag_IRScan(10, 0x014) #Cycle 251781
        ir_scan_out = helper.jtag_IRScan(16, 0x3600) #Cycle 251797
        dr_scan_out = helper.jtag_DRScan(7, 0x70) #Cycle 251819
        ir_scan_out = helper.jtag_IRScan(34, 0x3e4f97e50) #Cycle 251831
        dr_scan_out = helper.jtag_DRScan(57, 0x000010000400010) #Cycle 251871
        ir_scan_out = helper.jtag_IRScan(34, 0x015054150) #Cycle 252480
        ir_scan_out = helper.jtag_IRScan(10, 0x017) #Cycle 252520
        ir_scan_out = helper.jtag_IRScan(10, 0x014) #Cycle 252536
        LOG("CK_OK de-assert L0_rst_")


    
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
    l0_rst_domain_reg_check(after_reset=0)
    l1_rst_domain_reg_check(after_reset=0)
    l3_rst_domain_reg_check(after_reset=0)
    helper.wait_sim_time("us", 5)
   
    helper.log("##############################################################")
    helper.log("###################### Trigger L0_rst_ #######################")
    helper.log("##############################################################")

    # JTAG override CK_OK to trigger l0_rst_
    ck_ok_assert_l0_rst()
    helper.wait_sim_time("us", 5)

    # FIXME, check SYS_STATUS_NONSECURE[26:24]==3'b000
    # if LDO have to drop voltage to assert erot_vdd_good, then SYS_STATUS_NONSECURE cannot be read.
    # then we could only check SW reg default value, better to change to other L0_rst_ trigger

    # JTAG override CK_OK to release l0_rst_
    ck_ok_deassert_l0_rst()
    helper.wait_sim_time("us", 5)

    # FIXME, check SYS_STATUS_NONSECURE[26:24]==3'b111

    helper.wait_sim_time("us", 50)

    l0_rst_domain_reg_check(after_reset=1)
    l1_rst_domain_reg_check(after_reset=1)
    l3_rst_domain_reg_check(after_reset=1)

    helper.log("Test done")
