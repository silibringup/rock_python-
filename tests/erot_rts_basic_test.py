#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import *

with Test(sys.argv) as t:
    def write_measurement(index_value):
        #write sequence
        helper.log(f"Write measurement to index: {index_value}")
        
        #seq1: poll store_measurment == 0
        helper.log("START TO POLL STORE_MEASURMENT == 0 ...")    
        erot.RTS.MCR_0.poll(STORE_MEASUREMENT=0)
        rd = erot.RTS.MCR_0.read()
        helper.log(f"POLL DONE - MCR_0 = {rd}")

        #seq2: write MER(Measurement Entry Registers)
        helper.log("START TO WRITE MER 0 ~ 11 ...")
        erot.RTS.MER_0.write(0x3d5e447e)
        erot.RTS.MER_1.write(0x9fd7b1aa)
        erot.RTS.MER_2.write(0xecc7aba7)
        erot.RTS.MER_3.write(0xbcc77ab9)
        erot.RTS.MER_4.write(0xcbdf28af)
        erot.RTS.MER_5.write(0x86af805a)
        erot.RTS.MER_6.write(0x208de39b)
        erot.RTS.MER_7.write(0x6dd7cce6)
        erot.RTS.MER_8.write(0x9fac8021)
        erot.RTS.MER_9.write(0x0812b1b8)
        erot.RTS.MER_10.write(0x7ec42d3b)
        erot.RTS.MER_11.write(0x56a458f1)
        rd = erot.RTS.MER_11.read()
        helper.log(f"WRITING DONE - MER_11 = {rd}")

        #seq3: write MCR(Measurement Control Register)
        helper.log("START TO WRITE MCR ...")
        erot.RTS.MCR_0.write(STORE_MEASUREMENT = 1, INDEX = index_value)

        #seq4: poll trigger_status == 0; seq5: poll store_measurement == 0
        helper.log("START TO POLL TRIGGER_STATUS, STORE_MEASUREMENT == 0, 0 ...")    
        erot.RTS.MCR_0.poll(TRIGGER_STATUS=0, STORE_MEASUREMENT=0)
        rd = erot.RTS.MCR_0.read()
        helper.log(f"POLL DONE - MCR_0 = {rd}")


    def read_measurement(index_value, check_zero):
        #read sequence
        #seq1: poll store_measurment == 0
        helper.log("START TO POLL STORE_MEASUREMENT == 0 ...")    
        erot.RTS.MCR_0.poll(STORE_MEASUREMENT=0)
        rd = erot.RTS.MCR_0.read()
        helper.log(f"POLL DONE - MCR_0 = {rd}") 

        # seq2: poll MRR_READ == 0
        helper.log("START TO POLL MRR_0.READ == 0 ...")   
        erot.RTS.MRR_0.poll(READ='INIT')
        rd = erot.RTS.MRR_0.read()
        helper.log(f"POLL DONE - MRR_0 = {rd}")
 
        #seq3: write MRR_INDEX, MRR_READ, MRR_READ_SHADOW
        helper.log("WRITE 1 TO MRR READ...")
        erot.RTS.MRR_0.write(READ = 1, INDEX = index_value)    
 
        #seq4: poll MRR_READ == 0
        helper.log("START TO POLL MRR_READ == 0 ...")   
        erot.RTS.MRR_0.poll(READ='INIT')
        rd = erot.RTS.MRR_0.read()
        helper.log(f"POLL DONE - MRR_0 = {rd}")
 
        #seq5: read MRV, MSRCNT
        helper.log(f"Read MRV of index: {index_value}")

        reg_check_list = [
            erot.RTS.MRV_0,
            erot.RTS.MRV_1,
            erot.RTS.MRV_2,
            erot.RTS.MRV_3,
            erot.RTS.MRV_4,
            erot.RTS.MRV_5,
            erot.RTS.MRV_6,
            erot.RTS.MRV_7,
            erot.RTS.MRV_8,
            erot.RTS.MRV_9,
            erot.RTS.MRV_10,
            erot.RTS.MRV_11,
            erot.RTS.MSRCNT_0 #
            ]

        for reg in reg_check_list:
            if check_zero:
                test_api.fuse_check_reg_log(reg, 'VALUE', exp=0)
            else:
                check_not_zero(reg)

    def check_not_zero(reg):
        rd = reg.read()
        if rd['VALUE'] == 0:
            helper.perror("REG [%s] CHECK FAIL: EXP NOT ZERO, ACT = [0x%x]" % (reg.name, rd['VALUE']))
        else:
            helper.log("REG [%s] CHECK PASS: [0x%x]" % (reg.name, rd['VALUE']))

    def deassert_sw_reset_l1():
        erot.RESET.NVEROT_RESET_CFG.SW_GPIO_CTRL_RST_0.update(RESET_GPIO_CTRL=1)
        erot.RESET.NVEROT_RESET_CFG.SW_SPIMON0_RST_0.update(RESET_SPIMON0=1)
        erot.RESET.NVEROT_RESET_CFG.SW_SPIMON1_RST_0.update(RESET_SPIMON1=1)
        
    def deassert_sw_reset_l3():  
        erot.RESET.NVEROT_RESET_CFG.SW_IB0_SPI_RST_0.update(RESET_IB0_SPI=1)
        erot.RESET.NVEROT_RESET_CFG.SW_IB1_SPI_RST_0.update(RESET_IB1_SPI=1)
        erot.RESET.NVEROT_RESET_CFG.SW_OOB_SPI_RST_0.update(RESET_OOB_SPI=1)
        erot.RESET.NVEROT_RESET_CFG.SW_IB0_I2C_RST_0.update(RESET_IB0_I2C=1)
        erot.RESET.NVEROT_RESET_CFG.SW_IB1_I2C_RST_0.update(RESET_IB1_I2C=1)
        erot.RESET.NVEROT_RESET_CFG.SW_IO_EXP_RST_0.update(RESET_IO_EXP=1)
        erot.RESET.NVEROT_RESET_CFG.SW_UART_RST_0.update(RESET_UART=1)


    rot_start_value = 0x0
    cum_start_value = 0x1
    cum_cnt_value = 0x5
    rot_cnt_value = 0x20

    # the assertion check fails on rand stall and is out of date
    if 'fpga' not in helper.target:
        helper.hdl_force('ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_EROT_rts.u_rts_core.timeout_err', 0x0)

    erot.RTS.MSR_ROT_CTRL_0.write(ROT_START = rot_start_value, ROT_CNT = rot_cnt_value)
    rd = erot.RTS.MSR_ROT_CTRL_0.read()
    helper.log(f"MSR_ROT_CTRL_0 = {rd}")
    erot.RTS.MSR_CUM_CTRL_0.write(CUM_START = cum_start_value, CUM_CNT = cum_cnt_value)
    rd = erot.RTS.MSR_CUM_CTRL_0.read()
    helper.log(f"MSR_CUM_CTRL_0 = {rd}")


    for i in range(32):
        write_measurement(index_value = i)
    
    for i in range(32):
        if i >= rot_start_value and i < (rot_start_value + rot_cnt_value):
            read_measurement(index_value = i, check_zero = 0)
        else:
            read_measurement(index_value = i, check_zero = 1)            
    
    if 'fpga' not in helper.target:
        helper.log("Assert L3 reset")
        erot.RESET.NVEROT_RESET_CFG.SW_L3_RST_0.write(RESET_LEVEL3=0)
        helper.wait_sim_time("us",10)

        for i in range(32):
            if i >= cum_start_value and i < (cum_start_value + cum_cnt_value):
                read_measurement(index_value = i, check_zero = 0)
            else:
                read_measurement(index_value = i, check_zero = 1)

        helper.log("Start to toggle fuse2reset_security_monitor_nvjtag_sel")
        helper.hdl_force("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.fuse2reset_security_monitor_nvjtag_sel", 1)
        helper.wait_sim_time("ns", 31)
        helper.hdl_force("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.fuse2reset_security_monitor_nvjtag_sel", 0)
        helper.wait_sim_time("us", 50)
        deassert_sw_reset_l1()
        deassert_sw_reset_l3()
        helper.wait_sim_time("us", 5)
        '''
        helper.log("Assert L0 reset")       
        helper.hdl_force("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_reset.L0_rst_", 0)
        helper.wait_sim_time("ns", 100)
        helper.hdl_force("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_reset.L0_rst_", 1)
        '''

        for i in range(32):
            read_measurement(index_value = i, check_zero = 1)

