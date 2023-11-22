#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import * 
import math


with Test(sys.argv) as t:

    erot_l0_reset_domain_regs = [
        erot.NV_PMC.SCRATCH_RESET_0_0
    ]

    erot_l1_reset_domain_regs = [
        erot.GPIO.A_VM_01_0,                     # gpio
        erot.SPI_MON0.reg7_end_address_0,        # bypass mon 0
        erot.SPI_MON1.reg7_end_address_0,        # bypass mon 1
        erot.NV_PMC.SCRATCH_RESET_1_0
    ]

    erot_l3_reset_domain_regs = [
        erot.I2C_IB0.I2C_CMD_DATA2_0,            # ib0_i2c
        erot.I2C_IB1.I2C_CMD_DATA2_0,            # ib1_i2c
        erot.IO_EXPANDER.I2C_CMD_DATA2_0,        # io_exp_i2c
        erot.SPI_IB0.COMMAND2_0,                 # ib0_spi
        erot.SPI_IB1.COMMAND2_0,                 # ib1_spi
        erot.OOBHUB_SPI.COMMAND2_0,              # oob_spi
        erot.UART.UARTIBRD_0,                    # uart
        erot.NV_PMC.SCRATCH_RESET_2_0
    ]


    def reg_cfg():
        for l0_reg in erot_l0_reset_domain_regs:
            l0_reg.write(0x5a5a5a5a)
        helper.log("finish L0 reg init")
        for l1_reg in erot_l1_reset_domain_regs:
            l1_reg.write(0x5a5a5a5a)
        helper.log("finish L1 reg init")
        for l3_reg in erot_l3_reset_domain_regs:
            l3_reg.write(0x5a5a5a5a)
        helper.log("finish L3 reg init")

    def l0_rst_domain_reg_check(after_reset):
        for l0_reg in erot_l0_reset_domain_regs:
            rd = l0_reg.read()
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
            rd = l1_reg.read()
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
            rd = l3_reg.read()
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

#    def chk_reg_rst_value(reg):
#        if not isinstance(reg, Rock_reg):
#            helper.perror("parameter is not a Rock_reg")
#            return
#        rd = reg.read()
#        mask = reg.reset_mask & reg.read_mask
#        act = rd.value & mask
#        exp = reg.reset_val & mask
#        if act != exp:
#            helper.perror("Mismatch, %s's value is not as expected" % reg.name)

    def chk_reg_rst_value(reg):
        if not isinstance(reg, Rock_reg):
            helper.perror("parameter is not a Rock_reg")
            return
        count = 0
        timeout = 200
        mask = reg.reset_mask & reg.read_mask
        exp = reg.reset_val & mask
        while count < timeout:
            rd = reg.read()
            act = rd.value & mask
            count += 1
            if act == exp:
                helper.log(f"SW RST check: Poll REG {reg.name} done after {count} times. Reg value = {hex(act)}")
                return
        helper.perror(f"SW RST check: Poll REG {reg.name} timeout after {count} times try. Reg value = {hex(act)}. Exp value = {hex(exp)}")

    def deassert_sw_reset_l1():
        erot.RESET.NVEROT_RESET_CFG.SW_GPIO_CTRL_RST_0.write(RESET_GPIO_CTRL=1)
        erot.RESET.NVEROT_RESET_CFG.SW_SPIMON0_RST_0.write(RESET_SPIMON0=1)
        erot.RESET.NVEROT_RESET_CFG.SW_SPIMON1_RST_0.write(RESET_SPIMON1=1)
        
    def deassert_sw_reset_l3():
        erot.RESET.NVEROT_RESET_CFG.SW_IB0_SPI_RST_0.write(RESET_IB0_SPI=1)
        erot.RESET.NVEROT_RESET_CFG.SW_IB1_SPI_RST_0.write(RESET_IB1_SPI=1)
        erot.RESET.NVEROT_RESET_CFG.SW_OOB_SPI_RST_0.write(RESET_OOB_SPI=1)
        erot.RESET.NVEROT_RESET_CFG.SW_IB0_I2C_RST_0.write(RESET_IB0_I2C=1)
        erot.RESET.NVEROT_RESET_CFG.SW_IB1_I2C_RST_0.write(RESET_IB1_I2C=1)
        erot.RESET.NVEROT_RESET_CFG.SW_IO_EXP_RST_0.write(RESET_IO_EXP=1)
        erot.RESET.NVEROT_RESET_CFG.SW_UART_RST_0.write(RESET_UART=1)


    
    helper.log("Test start")

    # release IP under SW rst
    deassert_sw_reset_l1()
    deassert_sw_reset_l3()

    # check L1 domain SW rst
    helper.log("###############################################################################")
    helper.log("###################### Configure L1 SW reset one-by-one #######################")
    helper.log("###############################################################################")

    helper.log("###################### Check GPIO #######################")
    reg_cfg()
    helper.wait_sim_time("us", 5)
    l0_rst_domain_reg_check(after_reset=0)
    l1_rst_domain_reg_check(after_reset=0)
    l3_rst_domain_reg_check(after_reset=0)
    helper.wait_sim_time("us", 5)
    erot.RESET.NVEROT_RESET_CFG.SW_GPIO_CTRL_RST_0.write(RESET_GPIO_CTRL=0)
    erot.RESET.NVEROT_RESET_CFG.SW_GPIO_CTRL_RST_0.write(RESET_GPIO_CTRL=1)
    chk_reg_rst_value(erot.GPIO.A_VM_01_0)
    helper.log("###################### GPIO done #######################")

    helper.log("###################### Check BYPASS MON0 ######################")
    reg_cfg()
    helper.wait_sim_time("us", 5)
    l0_rst_domain_reg_check(after_reset=0)
    l1_rst_domain_reg_check(after_reset=0)
    l3_rst_domain_reg_check(after_reset=0)
    helper.wait_sim_time("us", 5)
    erot.RESET.NVEROT_RESET_CFG.SW_SPIMON0_RST_0.write(RESET_SPIMON0=0)
    erot.RESET.NVEROT_RESET_CFG.SW_SPIMON0_RST_0.write(RESET_SPIMON0=1)
    chk_reg_rst_value(erot.SPI_MON0.reg7_end_address_0)
    helper.log("###################### BYPASS MON0 done ######################")

    helper.log("###################### Check BYPASS MON1 ######################")
    reg_cfg()
    helper.wait_sim_time("us", 5)
    l0_rst_domain_reg_check(after_reset=0)
    l1_rst_domain_reg_check(after_reset=0)
    l3_rst_domain_reg_check(after_reset=0)
    helper.wait_sim_time("us", 5)
    erot.RESET.NVEROT_RESET_CFG.SW_SPIMON1_RST_0.write(RESET_SPIMON1=0)
    erot.RESET.NVEROT_RESET_CFG.SW_SPIMON1_RST_0.write(RESET_SPIMON1=1)
    chk_reg_rst_value(erot.SPI_MON1.reg7_end_address_0)
    helper.log("###################### BYPASS MON1 done ######################")

    # check L3 domain SW rst
    helper.log("###############################################################################")
    helper.log("###################### Configure L3 SW reset one-by-one #######################")
    helper.log("###############################################################################")

    helper.log("###################### Check ioexpander I2C ######################")
    reg_cfg()
    helper.wait_sim_time("us", 5)
    l0_rst_domain_reg_check(after_reset=0)
    l1_rst_domain_reg_check(after_reset=0)
    l3_rst_domain_reg_check(after_reset=0)
    helper.wait_sim_time("us", 5)
    erot.RESET.NVEROT_RESET_CFG.SW_IO_EXP_RST_0.write(RESET_IO_EXP=0)
    erot.RESET.NVEROT_RESET_CFG.SW_IO_EXP_RST_0.write(RESET_IO_EXP=1)
    chk_reg_rst_value(erot.IO_EXPANDER.I2C_CMD_DATA2_0)
    helper.log("###################### ioexpander I2C done ######################")

    helper.log("###################### Check OOB SPI ######################")
    reg_cfg()
    helper.wait_sim_time("us", 5)
    l0_rst_domain_reg_check(after_reset=0)
    l1_rst_domain_reg_check(after_reset=0)
    l3_rst_domain_reg_check(after_reset=0)
    helper.wait_sim_time("us", 5)
    erot.RESET.NVEROT_RESET_CFG.SW_OOB_SPI_RST_0.write(RESET_OOB_SPI=0)
    erot.RESET.NVEROT_RESET_CFG.SW_OOB_SPI_RST_0.write(RESET_OOB_SPI=1)
    chk_reg_rst_value(erot.OOBHUB_SPI.COMMAND2_0)
    helper.log("###################### OOB SPI done ######################")

    helper.log("###################### Check UART ######################")
    reg_cfg()
    helper.wait_sim_time("us", 5)
    l0_rst_domain_reg_check(after_reset=0)
    l1_rst_domain_reg_check(after_reset=0)
    l3_rst_domain_reg_check(after_reset=0)
    helper.wait_sim_time("us", 5)
    erot.RESET.NVEROT_RESET_CFG.SW_UART_RST_0.write(RESET_UART=0)
    erot.RESET.NVEROT_RESET_CFG.SW_UART_RST_0.write(RESET_UART=1)
    chk_reg_rst_value(erot.UART.UARTIBRD_0)
    helper.log("###################### UART done ######################")

    helper.log("###################### Check IB0 SPI ######################")
    reg_cfg()
    helper.wait_sim_time("us", 5)
    l0_rst_domain_reg_check(after_reset=0)
    l1_rst_domain_reg_check(after_reset=0)
    l3_rst_domain_reg_check(after_reset=0)
    helper.wait_sim_time("us", 5)
    erot.RESET.NVEROT_RESET_CFG.SW_IB0_SPI_RST_0.write(RESET_IB0_SPI=0)
    erot.RESET.NVEROT_RESET_CFG.SW_IB0_SPI_RST_0.write(RESET_IB0_SPI=1)
    chk_reg_rst_value(erot.SPI_IB0.COMMAND2_0)
    helper.log("###################### IB0 SPI done ######################")

    helper.log("###################### Check IB1 SPI ######################")
    reg_cfg()
    helper.wait_sim_time("us", 5)
    l0_rst_domain_reg_check(after_reset=0)
    l1_rst_domain_reg_check(after_reset=0)
    l3_rst_domain_reg_check(after_reset=0)
    helper.wait_sim_time("us", 5)
    erot.RESET.NVEROT_RESET_CFG.SW_IB1_SPI_RST_0.write(RESET_IB1_SPI=0)
    erot.RESET.NVEROT_RESET_CFG.SW_IB1_SPI_RST_0.write(RESET_IB1_SPI=1)
    chk_reg_rst_value(erot.SPI_IB1.COMMAND2_0)
    helper.log("###################### IB1 SPI done ######################")

    # NOT test IB0_I2C on FPGA, since test case is loaded into FPGA thru IB0_I2C
    #reg_cfg()
    #helper.wait_sim_time("us", 5)
    #helper.log("Check IB0 I2C")
    #erot.RESET.NVEROT_RESET_CFG.SW_IB0_I2C_RST_0.write(RESET_IB0_I2C=0)
    #erot.RESET.NVEROT_RESET_CFG.SW_IB0_I2C_RST_0.write(RESET_IB0_I2C=1)
    #chk_reg_rst_value(erot.I2C_IB0.I2C_CMD_DATA2_0)
    #helper.log("IB0 I2C done")

    #helper.log("###################### Check IB1 I2C ######################")
    #reg_cfg()
    #helper.wait_sim_time("us", 5)
    #l0_rst_domain_reg_check(after_reset=0)
    #l1_rst_domain_reg_check(after_reset=0)
    #l3_rst_domain_reg_check(after_reset=0)
    #helper.wait_sim_time("us", 5)
    #erot.RESET.NVEROT_RESET_CFG.SW_IB1_I2C_RST_0.write(RESET_IB1_I2C=0)
    #erot.RESET.NVEROT_RESET_CFG.SW_IB1_I2C_RST_0.write(RESET_IB1_I2C=1)
    #chk_reg_rst_value(erot.I2C_IB1.I2C_CMD_DATA2_0)
    #helper.log("###################### IB1 I2C done ######################")


    helper.log("All SW RST done")

    helper.log("Test done")

