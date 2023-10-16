#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import * 
import re

with Test(sys.argv) as t:

    CLOCK_BASE_ADDR =  0x23000

    helper.pinfo("JTAG J2H PLL Config Test Starts!")
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
    helper.pinfo(f'j2h_unlock sequence start')
    helper.j2h_unlock()
    helper.pinfo(f'j2h_unlock sequence finish')

    #poll L3 reset released
    cnt = 0
    l3_released = 0
    while l3_released == 0 and cnt < 10:
        rd = helper.j2h_read(0x33010, check_ack=False) #erot.RESET.NVEROT_RESET_CFG.SW_L3_RST_0
        cnt += 1
        if rd & 0x1 == 1:
            l3_released = 1
    if l3_released == 0:
        helper.perror(f'L3_reset not released before w/r registers')   
    
    LOG(f'j2h pll config begin')
    helper.j2h_write(CLOCK_BASE_ADDR + 0x1004, 0x0) #erot.CLOCK.NVEROT_CLOCK_SYS_CTL.SW_PLL_1_0 IDDQ=0
    helper.wait_sim_time('us',5)
    helper.j2h_write(CLOCK_BASE_ADDR + 0x1004, 0x2) #erot.CLOCK.NVEROT_CLOCK_SYS_CTL.SW_PLL_1_0 ENABLE=1
    helper.wait_sim_time('us',20)
    
    #poll PLL_LOCK==1
    lock_done = 0 
    cnt = 0
    while lock_done == 0 and cnt < 100:
        rd = helper.j2h_read(CLOCK_BASE_ADDR + 0x304c) #erot.CLOCK.NVEROT_CLOCK_STATUS.PLL_LOCK_STATUS_0 PLL_LOCK
        cnt += 1
        if rd & 0x1 == 1:
            lock_done = 1
    if lock_done == 0:
        helper.perror(f'PLL_LOCK is 0')
        
    helper.j2h_write(CLOCK_BASE_ADDR + 0x1020, 0X1) # erot.CLOCK.NVEROT_CLOCK_SYS_CTL.SW_FUNC_CLK_SW_SWCTRL_RCM_CFG_0 SRC_SEL_SW=1
    
    helper.j2h_write(CLOCK_BASE_ADDR + 0x100c, 0x1a) # erot.CLOCK.NVEROT_CLOCK_SYS_CTL.SW_SYS_CLK_RCM_CFG_0 SRC_SEL_DIV_SW=4
    act_data = helper.j2h_read(CLOCK_BASE_ADDR + 0x100c)
    if act_data != 0x1a:
        helper.perror("erot.CLOCK.NVEROT_CLOCK_SYS_CTL.SW_SYS_CLK_RCM_CFG_0 receive wrong read data from TDO, expected 0x1a while receiving 0x%x" % (act_data))

    helper.j2h_write(CLOCK_BASE_ADDR + 0x1010, 0x1a) # erot.CLOCK.NVEROT_CLOCK_SYS_CTL.SW_BOOT_QSPI_CLK_RCM_CFG_0 SRC_SEL_DIV_SW=4
    act_data = helper.j2h_read(CLOCK_BASE_ADDR + 0x100c)
    if act_data != 0x1a:
        helper.perror("erot.CLOCK.NVEROT_CLOCK_SYS_CTL.SW_BOOT_QSPI_CLK_RCM_CFG receive wrong read data from TDO, expected 0x1a while receiving 0x%x" % (act_data))   

    helper.j2h_write(CLOCK_BASE_ADDR + 0x1014, 0x1a) # erot.CLOCK.NVEROT_CLOCK_SYS_CTL.SW_OOB_I3C_CLK_RCM_CFG_0 SRC_SEL_DIV_SW=4
    act_data = helper.j2h_read(CLOCK_BASE_ADDR + 0x100c)
    if act_data != 0x1a:
        helper.perror("erot.CLOCK.NVEROT_CLOCK_SYS_CTL.SW_OOB_I3C_CLK_RCM_CFG receive wrong read data from TDO, expected 0x1a while receiving 0x%x" % (act_data))
    helper.jtag.Led(0)  # End Testing
    
    helper.pinfo("JTAG J2H PLL Config Test Ends!")   
    

