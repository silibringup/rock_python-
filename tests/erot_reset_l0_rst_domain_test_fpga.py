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

    def sys_status_poll(exp_value):
        count = 0
        timeout = 100000
        while count < timeout:
            chain_value, l0_reset = test_api.jtag_reg_read('l0_reset')
            helper.log(f"SYS_STATUS_NONSECURE chain value: {hex(chain_value)}")
            helper.log(f'l0_reset: {str(l0_reset)}')

            chain_value, l1_reset = test_api.jtag_reg_read('l1_reset')
            helper.log(f"SYS_STATUS_NONSECURE chain value: {hex(chain_value)}")
            helper.log(f'l1_reset: {str(l1_reset)}')

            chain_value, l3_reset = test_api.jtag_reg_read('l3_reset')
            helper.log(f"SYS_STATUS_NONSECURE chain value: {hex(chain_value)}")
            helper.log(f'l3_reset: {str(l3_reset)}')

            SYS_STATUS_NONSECURE = str(l3_reset) + str(l1_reset) + str(l0_reset)
            helper.log(f"SYS_STATUS_NONSECURE[26:24] = {SYS_STATUS_NONSECURE}")
            count += 1
            if( SYS_STATUS_NONSECURE == exp_value ):
                helper.log(f"Poll SYS_STATUS_NONSECURE[26:24] done @ {count} times try. Act value = {SYS_STATUS_NONSECURE}")
                return
            elif count == 99999:
                helper.perror(f"Poll SYS_STATUS_NONSECURE[26:24] timeout after {count} times try. Act value = {SYS_STATUS_NONSECURE}. Exp value = {exp_value} ")
                return
            helper.wait_rpi_time(1) # wait 1us
 

    helper.log("###################################################################################################")
    helper.log("####################################### L0_rst_ Test Starts! ######################################")
    helper.log("###################################################################################################")

    #############################################################################################################
    ################################# simv force, would be ignored on real silicon ##############################
    #############################################################################################################
    helper.wait_sim_time("us", 50)
    helper.hdl_force('ntb_top.u_nv_fpga_dut.u_nv_top_fpga.u_nv_top_wrapper.u_nv_top.nvjtag_sel', 1)

    #############################################################################################################
    ################################################ J2H unlock #################################################
    #############################################################################################################
    helper.jtag.Reset(0)
    helper.jtag.DRScan(100, hex(0x0)) #add some delay as jtag only work when nvjtag_sel stable in real case
    helper.jtag.Reset(1)  
    helper.log(f'j2h_unlock sequence start')
    helper.j2h_unlock()
    helper.log(f'j2h_unlock sequence finish') 

    #############################################################################################################
    ################################################# J2H write #################################################
    #############################################################################################################
    helper.log("write J2H reg")
    reg_cfg()

    l0_rst_domain_reg_check(after_reset=0)
    l1_rst_domain_reg_check(after_reset=0)
    l3_rst_domain_reg_check(after_reset=0)
    helper.log("write J2H reg done")
   
    #############################################################################################################
    ############################################## trigger L0_rst_ ##############################################
    #############################################################################################################
    helper.log("###################### Assert L0_rst_ #######################")

    # JTAG override CK_OK to trigger l0_rst_
    test_api.jtag_mux_ovr('vrefro_ck_ok_trig_l0_rst', 0x0, 1)

    #############################################################################################################
    ########################################### read SYS_STATUS_NONSECURE #######################################
    #############################################################################################################
    helper.log("poll JTAG reg SYS_STATUS_NONSECURE[26:24] == 3'b000")
    sys_status_poll("000")
    helper.log("L0_rst_ triggered successfully")

    #############################################################################################################
    ############################################## release L0_rst_ ##############################################
    #############################################################################################################
    helper.log("###################### De-assert L0_rst_ #######################")

    # JTAG override CK_OK to release l0_rst_
    test_api.jtag_mux_ovr('vrefro_ck_ok_trig_l0_rst', 0x0, 0)

    #############################################################################################################
    ########################################### read SYS_STATUS_NONSECURE #######################################
    #############################################################################################################
    helper.log("poll JTAG reg SYS_STATUS_NONSECURE[26:24] == 3'b111")
    sys_status_poll("111")
    helper.log("L0_rst_ released successfully")

    #############################################################################################################
    ################################################# J2H read ##################################################
    #############################################################################################################
    helper.log("read J2H reg")
    l0_rst_domain_reg_check(after_reset=1)
    l1_rst_domain_reg_check(after_reset=1)
    l3_rst_domain_reg_check(after_reset=1)
    helper.log("J2H reg check done")

    helper.log("###################################################################################################")
    helper.log("######################################## L0_rst_ Test Ends! #######################################")
    helper.log("###################################################################################################")
