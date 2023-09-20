#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
import driver.helpers.helper as hp
from driver.helpers.regobj import *

class TestAPIs:
    __instance = None

    @classmethod
    def __new__(cls, *args):
        if cls.__instance is None:
            cls.__instance = object.__new__(*args)
        return cls.__instance

    def init(self,helper=None):
        self.helper = helper

    def log(self,s):
        self.helper.log(s)

    def test_init(self):
        self.log('start to do test initiation')
        if self.helper.target == "simv_top":   
            self.helper.hdl_force('ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_fabric_l1.u_fabric_l1_input_shim.zzz_assert_vip_req_ack_7x__inf_assume_req_fabric_fv_jtag_in_req_.vip_disable',1)
        self.helper.wait_sim_time("us", 1)    ## wait for riscv reset release after peregrine reset release
        self.clk_init()
        self.reset_init()
        #self.padctl_init()

    def clk_init(self):
        self.log('start to do clk initiation')
        if self.helper.target == "simv_fpga":
            self.log("simv_fpga need not to config clk, quit")
            return
        if self.helper.platform == "SIM_HEADLESS":
            self.helper.wait_sim_time("us", 5)
            while True:
                L3_rst = self.helper.hdl_read('ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_reset.L3_rst_')
                if L3_rst == 1:
                    break;
                self.helper.wait_sim_time("us", 1)

        self.log('vrefro config begin')
        erot.CLOCK.NVEROT_CLOCK_VREFRO_CTL.SW_VREFRO_0.update(FREQADJ=0x1c)
        self.log('vrefro config done')
        self.log('pll config begin')
        erot.CLOCK.NVEROT_CLOCK_SYS_CTL.SW_PLL_1_0.update(IDDQ=0)
        self.helper.wait_sim_time('us',5)
        erot.CLOCK.NVEROT_CLOCK_SYS_CTL.SW_PLL_1_0.update(ENABLE=1)
        self.helper.wait_sim_time('us',20)
        erot.CLOCK.NVEROT_CLOCK_STATUS.PLL_LOCK_STATUS_0.poll(PLL_LOCK=1)
        erot.CLOCK.NVEROT_CLOCK_SYS_CTL.SW_FUNC_CLK_SW_SWCTRL_RCM_CFG_0.update(SRC_SEL_SW=1)
        erot.CLOCK.NVEROT_CLOCK_SYS_CTL.SW_SYS_CLK_RCM_CFG_0.update(SRC_SEL_DIV_SW=4)
        erot.CLOCK.NVEROT_CLOCK_SYS_CTL.SW_BOOT_QSPI_CLK_RCM_CFG_0.update(SRC_SEL_DIV_SW=4)
        erot.CLOCK.NVEROT_CLOCK_SYS_CTL.SW_OOB_I3C_CLK_RCM_CFG_0.update(SRC_SEL_DIV_SW=4)
        self.log('pll config done')
        erot.CLOCK.NVEROT_CLOCK_IO_CTL.SW_QSPI0_CLK_RCM_CFG_0.update(SRC_SEL_DIV_SW=4)
        erot.CLOCK.NVEROT_CLOCK_IO_CTL.SW_QSPI1_CLK_RCM_CFG_0.update(SRC_SEL_DIV_SW=4)
        erot.CLOCK.NVEROT_CLOCK_IO_CTL.SW_INB0_I3C_CLK_RCM_CFG_0.update(SRC_SEL_DIV_SW=4)
        erot.CLOCK.NVEROT_CLOCK_IO_CTL.SW_INB1_I3C_CLK_RCM_CFG_0.update(SRC_SEL_DIV_SW=4)
        erot.CLOCK.NVEROT_CLOCK_IO_CTL.SW_OOB_SPI_CLK_RCM_CFG_0.update(SRC_SEL_DIV_SW=4)
        erot.CLOCK.NVEROT_CLOCK_IO_CTL.SW_INB0_SPI_CLK_RCM_CFG_0.update(SRC_SEL_DIV_SW=4)
        erot.CLOCK.NVEROT_CLOCK_IO_CTL.SW_INB1_SPI_CLK_RCM_CFG_0.update(SRC_SEL_DIV_SW=4)
#        erot.CLOCK.NVEROT_CLOCK_IO_CTL.SW_UART_CLK_RCM_CFG_0.update(SRC_SEL_DIV_SW=4)
        self.helper.wait_sim_time("us", 50)

    def oobhub_icd_init(self):
        erot.OOBHUB.PEREGRINE_RISCV_DBGCTL_0.update(START_IN_ICD=1)
        erot.OOBHUB.PEREGRINE_RISCV_BCR_CTRL_0.update(CORE_SELECT=1)
        erot.OOBHUB.PEREGRINE_RISCV_CPUCTL_0.update(STARTCPU=1)
    
    def oobhub_icd_write(self,addr,data,check_error_resp=1):
        erot.OOBHUB.PEREGRINE_RISCV_ICD_ADDR0_0.update(ADDR=addr&0xffffffff)
        erot.OOBHUB.PEREGRINE_RISCV_ICD_ADDR1_0.update(ADDR=(addr&0xffffffff00000000)>>32)
        erot.OOBHUB.PEREGRINE_RISCV_ICD_WDATA0_0.update(DATA=data&0xffffffff)
        erot.OOBHUB.PEREGRINE_RISCV_ICD_WDATA1_0.update(DATA=(data&0xffffffff00000000)>>32)
        erot.OOBHUB.PEREGRINE_RISCV_ICD_CMD_0.update(OPC='WDM',SZ='W')

        erot.OOBHUB.PEREGRINE_RISCV_ICD_CMD_0.poll(BUSY=0)
        rd = erot.OOBHUB.PEREGRINE_RISCV_ICD_CMD_0.read()
        if rd['ERROR'] == 1 and check_error_resp == 1:
            self.helper.perror('icd cfg read icd_cmd return error for addr 0x%x, wdata 0x%x'%(addr,data))
        if check_error_resp == 0:
            return rd['ERROR']
    
    def oobhub_icd_read(self,addr,check_error_resp=1):
        erot.OOBHUB.PEREGRINE_RISCV_ICD_ADDR0_0.update(ADDR=addr&0xffffffff)
        erot.OOBHUB.PEREGRINE_RISCV_ICD_ADDR1_0.update(ADDR=(addr&0xffffffff00000000)>>32)
        erot.OOBHUB.PEREGRINE_RISCV_ICD_CMD_0.update(OPC='RDM',SZ='W')

        erot.OOBHUB.PEREGRINE_RISCV_ICD_CMD_0.poll(BUSY=0)
        rd = erot.OOBHUB.PEREGRINE_RISCV_ICD_CMD_0.read()
        if rd['ERROR'] == 1 and check_error_resp == 1:
            self.helper.perror('icd cfg read icd_cmd return error for addr 0x%x'%(addr))

        rd_lo = erot.OOBHUB.PEREGRINE_RISCV_ICD_RDATA0_0.read()
        rd_hi = erot.OOBHUB.PEREGRINE_RISCV_ICD_RDATA1_0.read()
        if check_error_resp == 0:
            output = dict()
            output["err_resp"] = rd['ERROR']
            output["value"] = rd_lo['DATA'] + (rd_hi['DATA']<<32)
            return output
        else:
            return rd_lo['DATA'] + (rd_hi['DATA']<<32)

    def power_on_seq(self):
        # 1.8v power rail
        self.helper.hdl_force('ntb_top.vsr1',1)
        self.helper.hdl_force('ntb_top.pdm_io',1)
        self.helper.hdl_force('ntb_top.fuse_vqps',1)
        self.helper.wait_sim_time('ns',10)
        # 0.8v power rail
        self.helper.hdl_force('ntb_top.vsr2',1)
        self.helper.wait_sim_time('ns',100)
        # 3.3v pwoer rail
        self.helper.hdl_force('ntb_top.pdm_io',0)
        self.helper.hdl_force('ntb_top.vsr0',1)
        self.helper.hdl_force('ntb_top.erot_vdd_good',1)
    
    def power_down_seq(self, larger_gap_pdm_io_vsr2=1):
        # 3.3v pwoer rail
        self.helper.hdl_force('ntb_top.pdm_io',1)
        self.helper.hdl_force('ntb_top.vsr0',0)
        self.helper.hdl_force('ntb_top.erot_vdd_good',0)
        if larger_gap_pdm_io_vsr2 == 1:
            self.helper.wait_sim_time('ns',101)
        else:
            self.helper.wait_sim_time('ns',100)
        # 0.8v power rail
        self.helper.hdl_force('ntb_top.vsr2',0)
        self.helper.wait_sim_time('ns',10)
        # 1.8v power rail
        self.helper.hdl_force('ntb_top.vsr1',0)
        self.helper.hdl_force('ntb_top.pdm_io',0)
        self.helper.hdl_force('ntb_top.fuse_vqps',0)

    def reset_init(self):
        erot.RESET.NVEROT_RESET_CFG.SW_GPIO_CTRL_RST_0.update(RESET_GPIO_CTRL=1)
        erot.RESET.NVEROT_RESET_CFG.SW_SPIMON0_RST_0.update(RESET_SPIMON0=1)
        erot.RESET.NVEROT_RESET_CFG.SW_SPIMON1_RST_0.update(RESET_SPIMON1=1)
        #erot.RESET.NVEROT_RESET_CFG.SW_QSPI0_RST_0.update(RESET_QSPI0=1)
        #erot.RESET.NVEROT_RESET_CFG.SW_QSPI1_RST_0.update(RESET_QSPI1=1)
        erot.RESET.NVEROT_RESET_CFG.SW_IB0_SPI_RST_0.update(RESET_IB0_SPI=1)
        erot.RESET.NVEROT_RESET_CFG.SW_IB1_SPI_RST_0.update(RESET_IB1_SPI=1)
        erot.RESET.NVEROT_RESET_CFG.SW_OOB_SPI_RST_0.update(RESET_OOB_SPI=1)
        erot.RESET.NVEROT_RESET_CFG.SW_IB0_I2C_RST_0.update(RESET_IB0_I2C=1)
        erot.RESET.NVEROT_RESET_CFG.SW_IB1_I2C_RST_0.update(RESET_IB1_I2C=1)
        erot.RESET.NVEROT_RESET_CFG.SW_IO_EXP_RST_0.update(RESET_IO_EXP=1)
        erot.RESET.NVEROT_RESET_CFG.SW_UART_RST_0.update(RESET_UART=1)

        erot.RESET.NVEROT_RESET_CFG.SW_GPIO_CTRL_RST_0.poll(RESET_GPIO_CTRL=1)
        erot.RESET.NVEROT_RESET_CFG.SW_SPIMON0_RST_0.poll(RESET_SPIMON0=1)
        erot.RESET.NVEROT_RESET_CFG.SW_SPIMON1_RST_0.poll(RESET_SPIMON1=1)
        #erot.RESET.NVEROT_RESET_CFG.SW_QSPI0_RST_0.poll(RESET_QSPI0=1)
        #erot.RESET.NVEROT_RESET_CFG.SW_QSPI1_RST_0.poll(RESET_QSPI1=1)
        erot.RESET.NVEROT_RESET_CFG.SW_IB0_SPI_RST_0.poll(RESET_IB0_SPI=1)
        erot.RESET.NVEROT_RESET_CFG.SW_IB1_SPI_RST_0.poll(RESET_IB1_SPI=1)
        erot.RESET.NVEROT_RESET_CFG.SW_OOB_SPI_RST_0.poll(RESET_OOB_SPI=1)
        erot.RESET.NVEROT_RESET_CFG.SW_IB0_I2C_RST_0.poll(RESET_IB0_I2C=1)
        erot.RESET.NVEROT_RESET_CFG.SW_IB1_I2C_RST_0.poll(RESET_IB1_I2C=1)
        erot.RESET.NVEROT_RESET_CFG.SW_IO_EXP_RST_0.poll(RESET_IO_EXP=1)
        erot.RESET.NVEROT_RESET_CFG.SW_UART_RST_0.poll(RESET_UART=1)

    def qspi0_init(self):
        self.log('start to initialize QSPI0 I/O')
        erot.PADCTRL_E.EROT_QSPI0_CLK_0.update(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_CS0_N_0.update(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_CS1_N_0.update(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_IO0_0.update(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_IO1_0.update(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_IO2_0.update(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_IO3_0.update(TRISTATE=0)

        erot.PADCTRL_E.EROT_QSPI0_CLK_0.poll(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_CS0_N_0.poll(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_CS1_N_0.poll(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_IO0_0.poll(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_IO1_0.poll(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_IO2_0.poll(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_IO3_0.poll(TRISTATE=0)

    def qspi1_init(self):
        self.log('start to initialize QSPI1 I/O')
        erot.PADCTRL_W.EROT_QSPI1_CLK_0.update(TRISTATE=0)
        erot.PADCTRL_W.EROT_QSPI1_CS0_N_0.update(TRISTATE=0)
        erot.PADCTRL_W.EROT_QSPI1_CS1_N_0.update(TRISTATE=0)
        erot.PADCTRL_W.EROT_QSPI1_IO0_0.update(TRISTATE=0)
        erot.PADCTRL_W.EROT_QSPI1_IO1_0.update(TRISTATE=0)
        erot.PADCTRL_W.EROT_QSPI1_IO2_0.update(TRISTATE=0)
        erot.PADCTRL_W.EROT_QSPI1_IO3_0.update(TRISTATE=0) 

        erot.PADCTRL_W.EROT_QSPI1_CLK_0.poll(TRISTATE=0)
        erot.PADCTRL_W.EROT_QSPI1_CS0_N_0.poll(TRISTATE=0)
        erot.PADCTRL_W.EROT_QSPI1_CS1_N_0.poll(TRISTATE=0)
        erot.PADCTRL_W.EROT_QSPI1_IO0_0.poll(TRISTATE=0)
        erot.PADCTRL_W.EROT_QSPI1_IO1_0.poll(TRISTATE=0)
        erot.PADCTRL_W.EROT_QSPI1_IO2_0.poll(TRISTATE=0)
        erot.PADCTRL_W.EROT_QSPI1_IO3_0.poll(TRISTATE=0)

    def boot_qspi_init(self):
        self.log('start to initialize BOOT_QSPI I/O')
        erot.PADCTRL_N.BOOT_QSPI_CLK_0.update(TRISTATE=0)
        erot.PADCTRL_N.BOOT_QSPI_CS_N_0.update(TRISTATE=0)
        erot.PADCTRL_N.BOOT_QSPI_IO0_0.update(TRISTATE=0)
        erot.PADCTRL_N.BOOT_QSPI_IO1_0.update(TRISTATE=0)
        erot.PADCTRL_N.BOOT_QSPI_IO2_0.update(TRISTATE=0)
        erot.PADCTRL_N.BOOT_QSPI_IO3_GP29_0.update(TRISTATE=0)

        erot.PADCTRL_N.BOOT_QSPI_CLK_0.poll(TRISTATE=0)
        erot.PADCTRL_N.BOOT_QSPI_CS_N_0.poll(TRISTATE=0)
        erot.PADCTRL_N.BOOT_QSPI_IO0_0.poll(TRISTATE=0)
        erot.PADCTRL_N.BOOT_QSPI_IO1_0.poll(TRISTATE=0)
        erot.PADCTRL_N.BOOT_QSPI_IO2_0.poll(TRISTATE=0)
        erot.PADCTRL_N.BOOT_QSPI_IO3_GP29_0.poll(TRISTATE=0)

    def boot_qspi_clk_init(self):      
        erot.BOOT_QSPI.QSPI.GLOBAL_TRIM_CNTRL_0.update(SEL=1)     
        erot.BOOT_QSPI.QSPI.GLOBAL_TRIM_CNTRL_0.poll(SEL=1)

    def ap0_qspi_init(self):
        self.log('start to initialize AP0 I/O')
        erot.PADCTRL_E.AP0_QSPI_CLK_0.update(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_CS0_N_0.update(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_CS1_N_0.update(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_IO0_0.update(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_IO1_0.update(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_IO2_0.update(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_IO3_0.update(TRISTATE=0)

        erot.PADCTRL_E.AP0_QSPI_CLK_0.poll(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_CS0_N_0.poll(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_CS1_N_0.poll(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_IO0_0.poll(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_IO1_0.poll(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_IO2_0.poll(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_IO3_0.poll(TRISTATE=0)

    def ap1_qspi_init(self):
        self.log('start to initialize AP1 I/O')
        erot.PADCTRL_W.AP1_QSPI_CLK_0.update(TRISTATE=0)
        erot.PADCTRL_W.AP1_QSPI_CS0_N_0.update(TRISTATE=0)
        erot.PADCTRL_W.AP1_QSPI_CS1_N_0.update(TRISTATE=0)
        erot.PADCTRL_W.AP1_QSPI_IO0_0.update(TRISTATE=0)
        erot.PADCTRL_W.AP1_QSPI_IO1_0.update(TRISTATE=0)
        erot.PADCTRL_W.AP1_QSPI_IO2_0.update(TRISTATE=0)
        erot.PADCTRL_W.AP1_QSPI_IO3_0.update(TRISTATE=0)

        erot.PADCTRL_W.AP1_QSPI_CLK_0.poll(TRISTATE=0)
        erot.PADCTRL_W.AP1_QSPI_CS0_N_0.poll(TRISTATE=0)
        erot.PADCTRL_W.AP1_QSPI_CS1_N_0.poll(TRISTATE=0)
        erot.PADCTRL_W.AP1_QSPI_IO0_0.poll(TRISTATE=0)
        erot.PADCTRL_W.AP1_QSPI_IO1_0.poll(TRISTATE=0)
        erot.PADCTRL_W.AP1_QSPI_IO2_0.poll(TRISTATE=0)
        erot.PADCTRL_W.AP1_QSPI_IO3_0.poll(TRISTATE=0)

    def oob_dspi_init(self):
        self.log('start to initialize OOB DSPI I/O')  
        erot.PADCTRL_S.EROT_OOB_DSPI_CLK_0.update(TRISTATE=0)       
        erot.PADCTRL_S.EROT_OOB_DSPI_CS_N_0.update(TRISTATE=0) 
        erot.PADCTRL_S.EROT_OOB_DSPI_IO0_0.update(TRISTATE=0)          
        erot.PADCTRL_S.EROT_OOB_DSPI_IO1_0.update(TRISTATE=0)
        
        erot.PADCTRL_S.EROT_OOB_DSPI_CLK_0.poll(TRISTATE=0)       
        erot.PADCTRL_S.EROT_OOB_DSPI_CS_N_0.poll(TRISTATE=0) 
        erot.PADCTRL_S.EROT_OOB_DSPI_IO0_0.poll(TRISTATE=0)          
        erot.PADCTRL_S.EROT_OOB_DSPI_IO1_0.poll(TRISTATE=0)     

    def ap_i2c_init(self): 
        self.log('start to do ap i2c/i3c padctl initiation')
        erot.PADCTRL_E.AP0_I3C_SCL_0.update(TRISTATE=0)
        erot.PADCTRL_E.AP0_I3C_SDA_0.update(TRISTATE=0)
        erot.PADCTRL_W.AP1_I3C_SCL_0.update(TRISTATE=0)
        erot.PADCTRL_W.AP1_I3C_SDA_0.update(TRISTATE=0)
        erot.PADCTRL_S.MISC_I2C_SCL_GP24_0.update(TRISTATE=0)
        erot.PADCTRL_S.MISC_I2C_SDA_GP25_0.update(TRISTATE=0)

    def uart_init(self):
        self.log('start to do uart padctl initiation')
        erot.PADCTRL_S.UART_TX_0.update(TRISTATE=0)
        erot.PADCTRL_S.UART_RX_0.update(TRISTATE=0)

    def ap_spi_init(self):
        self.log('start to do ap spi padctl initiation')
        #SPI0
        erot.PADCTRL_E.AP0_QSPI_CLK_0.update(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_CS0_N_0.update(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_CS1_N_0.update(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_IO0_0.update(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_IO1_0.update(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_IO2_0.update(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_IO3_0.update(TRISTATE=0)
        #SPI1
        erot.PADCTRL_W.AP1_QSPI_CLK_0.update(TRISTATE=0)
        erot.PADCTRL_W.AP1_QSPI_CS0_N_0.update(TRISTATE=0)
        erot.PADCTRL_W.AP1_QSPI_CS1_N_0.update(TRISTATE=0)
        erot.PADCTRL_W.AP1_QSPI_IO0_0.update(TRISTATE=0)
        erot.PADCTRL_W.AP1_QSPI_IO1_0.update(TRISTATE=0)
        erot.PADCTRL_W.AP1_QSPI_IO2_0.update(TRISTATE=0)
        erot.PADCTRL_W.AP1_QSPI_IO3_0.update(TRISTATE=0)

    def padctl_init(self):
        self.log('start to do padctl initiation')
        erot.PADCTRL_E.AP0_I3C_SCL_0.update(TRISTATE=0)
        erot.PADCTRL_E.AP0_I3C_SDA_0.update(TRISTATE=0)
        erot.PADCTRL_W.AP1_I3C_SCL_0.update(TRISTATE=0)
        erot.PADCTRL_W.AP1_I3C_SDA_0.update(TRISTATE=0)
        erot.PADCTRL_S.EROT_OOB_I3C_SCL_0.update(TRISTATE=0)
        erot.PADCTRL_S.EROT_OOB_I3C_SDA_0.update(TRISTATE=0)
        erot.PADCTRL_S.MISC_I2C_SCL_GP24_0.update(TRISTATE=0)
        erot.PADCTRL_S.MISC_I2C_SDA_GP25_0.update(TRISTATE=0)
        erot.PADCTRL_S.HW_STRAP_GP28_0.update(TRISTATE=0)
        erot.PADCTRL_S.OBS0_GP26_0.update(TRISTATE=0)
        erot.PADCTRL_S.OBS1_GP27_0.update(TRISTATE=0)
        erot.PADCTRL_S.UART_TX_0.update(TRISTATE=0)
        erot.PADCTRL_S.UART_RX_0.update(TRISTATE=0)
        #QSPI0
        erot.PADCTRL_E.EROT_QSPI0_CLK_0.update(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_CS0_N_0.update(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_CS1_N_0.update(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_IO0_0.update(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_IO1_0.update(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_IO2_0.update(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_IO3_0.update(TRISTATE=0)
        #QSPI1
        erot.PADCTRL_W.EROT_QSPI1_CLK_0.update(TRISTATE=0)
        erot.PADCTRL_W.EROT_QSPI1_CS0_N_0.update(TRISTATE=0)
        erot.PADCTRL_W.EROT_QSPI1_CS1_N_0.update(TRISTATE=0)
        erot.PADCTRL_W.EROT_QSPI1_IO0_0.update(TRISTATE=0)
        erot.PADCTRL_W.EROT_QSPI1_IO1_0.update(TRISTATE=0)
        erot.PADCTRL_W.EROT_QSPI1_IO2_0.update(TRISTATE=0)
        erot.PADCTRL_W.EROT_QSPI1_IO3_0.update(TRISTATE=0)    
        #SPI0
        erot.PADCTRL_E.AP0_QSPI_CLK_0.update(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_CS0_N_0.update(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_CS1_N_0.update(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_IO0_0.update(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_IO1_0.update(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_IO2_0.update(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_IO3_0.update(TRISTATE=0)
        #SPI1
        erot.PADCTRL_W.AP1_QSPI_CLK_0.update(TRISTATE=0)
        erot.PADCTRL_W.AP1_QSPI_CS0_N_0.update(TRISTATE=0)
        erot.PADCTRL_W.AP1_QSPI_CS1_N_0.update(TRISTATE=0)
        erot.PADCTRL_W.AP1_QSPI_IO0_0.update(TRISTATE=0)
        erot.PADCTRL_W.AP1_QSPI_IO1_0.update(TRISTATE=0)
        erot.PADCTRL_W.AP1_QSPI_IO2_0.update(TRISTATE=0)
        erot.PADCTRL_W.AP1_QSPI_IO3_0.update(TRISTATE=0)

 

    def gpio_cfg_padctl_init_1(self):
        erot.PADCTRL_E.AP0_BOOT_CTRL_0_N_GP01_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_E.AP0_BOOT_CTRL_1_N_GP02_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_E.EROT_REQ_AP0_N_GP03_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_E.EROT_GNT_AP0_N_GP04_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_E.AP0_FW_INTR_N_GP05_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_E.AP0_MUX_CTRL_N_GP06_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_E.AP0_PGOOD_GP07_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_E.AP0_RESET_N_GP08_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_E.AP0_RESET_IND_N_GP09_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_E.AP0_RESET_MON_N_GP10_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_E.AP0_SPI_PWR_KILL_GP11_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_W.AP1_BOOT_CTRL_0_N_GP12_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_W.AP1_BOOT_CTRL_1_N_GP13_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_W.EROT_REQ_AP1_N_GP14_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_W.EROT_GNT_AP1_N_GP15_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_W.AP1_FW_INTR_N_GP16_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_W.AP1_MUX_CTRL_N_GP17_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_W.AP1_PGOOD_GP18_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_W.AP1_RESET_N_GP19_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_W.AP1_RESET_IND_N_GP20_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_W.AP1_RESET_MON_N_GP21_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_W.AP1_SPI_PWR_KILL_GP22_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_S.EROT_LED_GP23_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_S.MISC_I2C_SCL_GP24_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_S.MISC_I2C_SDA_GP25_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1) 
        erot.PADCTRL_S.OBS0_GP26_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_S.OBS1_GP27_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_S.HW_STRAP_GP28_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_N.BOOT_QSPI_IO3_GP29_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_S.EROT_ERROR_N_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        #GPIO
        erot.PADCTRL_E.AP0_BOOT_CTRL_0_N_GP01_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_E.AP0_BOOT_CTRL_1_N_GP02_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_E.EROT_REQ_AP0_N_GP03_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_E.EROT_GNT_AP0_N_GP04_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_E.AP0_FW_INTR_N_GP05_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_E.AP0_MUX_CTRL_N_GP06_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_E.AP0_PGOOD_GP07_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_E.AP0_RESET_N_GP08_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_E.AP0_RESET_IND_N_GP09_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_E.AP0_RESET_MON_N_GP10_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_E.AP0_SPI_PWR_KILL_GP11_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_W.AP1_BOOT_CTRL_0_N_GP12_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_W.AP1_BOOT_CTRL_1_N_GP13_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_W.EROT_REQ_AP1_N_GP14_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_W.EROT_GNT_AP1_N_GP15_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_W.AP1_FW_INTR_N_GP16_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_W.AP1_MUX_CTRL_N_GP17_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_W.AP1_PGOOD_GP18_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_W.AP1_RESET_N_GP19_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_W.AP1_RESET_IND_N_GP20_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_W.AP1_RESET_MON_N_GP21_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_W.AP1_SPI_PWR_KILL_GP22_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_S.EROT_LED_GP23_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_S.MISC_I2C_SCL_GP24_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_S.MISC_I2C_SDA_GP25_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1) 
        erot.PADCTRL_S.OBS0_GP26_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_S.OBS1_GP27_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_S.HW_STRAP_GP28_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_N.BOOT_QSPI_IO3_GP29_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_S.EROT_ERROR_N_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)

    def gpio_cfg_padctl_init_2(self):
        erot.PADCTRL_E.AP0_BOOT_CTRL_0_N_GP01_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_E.AP0_BOOT_CTRL_1_N_GP02_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_E.EROT_REQ_AP0_N_GP03_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_E.EROT_GNT_AP0_N_GP04_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_E.AP0_FW_INTR_N_GP05_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_E.AP0_MUX_CTRL_N_GP06_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_E.AP0_PGOOD_GP07_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_E.AP0_RESET_N_GP08_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_E.AP0_RESET_IND_N_GP09_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_E.AP0_RESET_MON_N_GP10_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_E.AP0_SPI_PWR_KILL_GP11_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_W.AP1_BOOT_CTRL_0_N_GP12_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_W.AP1_BOOT_CTRL_1_N_GP13_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_W.EROT_REQ_AP1_N_GP14_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_W.EROT_GNT_AP1_N_GP15_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_W.AP1_FW_INTR_N_GP16_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_W.AP1_MUX_CTRL_N_GP17_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_W.AP1_PGOOD_GP18_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_W.AP1_RESET_N_GP19_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_W.AP1_RESET_IND_N_GP20_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_W.AP1_RESET_MON_N_GP21_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_W.AP1_SPI_PWR_KILL_GP22_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_S.EROT_LED_GP23_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_S.MISC_I2C_SCL_GP24_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_S.MISC_I2C_SDA_GP25_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0) 
        erot.PADCTRL_S.OBS0_GP26_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_S.OBS1_GP27_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_S.HW_STRAP_GP28_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_N.BOOT_QSPI_IO3_GP29_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_S.EROT_ERROR_N_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)

        #GPIO
        erot.PADCTRL_E.AP0_BOOT_CTRL_0_N_GP01_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_E.AP0_BOOT_CTRL_1_N_GP02_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_E.EROT_REQ_AP0_N_GP03_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_E.EROT_GNT_AP0_N_GP04_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_E.AP0_FW_INTR_N_GP05_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_E.AP0_MUX_CTRL_N_GP06_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_E.AP0_PGOOD_GP07_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_E.AP0_RESET_N_GP08_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_E.AP0_RESET_IND_N_GP09_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_E.AP0_RESET_MON_N_GP10_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_E.AP0_SPI_PWR_KILL_GP11_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_W.AP1_BOOT_CTRL_0_N_GP12_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_W.AP1_BOOT_CTRL_1_N_GP13_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_W.EROT_REQ_AP1_N_GP14_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_W.EROT_GNT_AP1_N_GP15_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_W.AP1_FW_INTR_N_GP16_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_W.AP1_MUX_CTRL_N_GP17_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_W.AP1_PGOOD_GP18_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_W.AP1_RESET_N_GP19_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_W.AP1_RESET_IND_N_GP20_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_W.AP1_RESET_MON_N_GP21_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_W.AP1_SPI_PWR_KILL_GP22_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_S.EROT_LED_GP23_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_S.MISC_I2C_SCL_GP24_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_S.MISC_I2C_SDA_GP25_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0) 
        erot.PADCTRL_S.OBS0_GP26_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_S.OBS1_GP27_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_S.HW_STRAP_GP28_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_N.BOOT_QSPI_IO3_GP29_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_S.EROT_ERROR_N_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)

    def gpio_cfg_padctl_init_3(self):
        erot.PADCTRL_W.EROT_GNT_AP1_N_GP15_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_S.EROT_ERROR_N_0.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)
        erot.PADCTRL_W.EROT_GNT_AP1_N_GP15_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
        erot.PADCTRL_S.EROT_ERROR_N_0.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=0)

# IFF APIs
    def iff_push_finish_check(self):
        self.iff_push_done()
        self.iff_finish()
        self.iff_check_err()
    
    def iff_push_done(self):
        reg = erot.FUSE.PUSH_0
        self.helper.log("START TO POLL FUSE IFF CMD PUSH DONE")
        reg.poll(interval=50000, IFF_DONE="YES")
        self.helper.log("POLL DONE FUSE IFF CMD PUSH")

    def iff_finish(self):
        reg = erot.FSP.SYSCTRL_IFF_FINISH_0
        self.helper.log("START TO POLL FSP REG [%s]" % reg.name)
        reg.poll(interval=50000, VALUE=1) # NO ENUM FOR THE FIELD
        self.helper.log("PLL DONE IFF OPERATIONS FINISHED")

    def iff_check_err(self):
        reg_err = erot.NV_PMC.IFF_ERROR_0
        err_rd = reg_err.read() 
        if (err_rd.value & reg_err.read_mask) != 0:
            self.helper.perror("[IFF CMD STATUS] FINISH WITH ERROR: REG [%s]\n%r" % (reg_err.name, err_rd))
        else:
            self.helper.log("[IFF CMD STATUS] FINISH WITH NO ERROR")

    def iff_poll_error(self, error_field):
        reg_err = erot.NV_PMC.IFF_ERROR_0
        self.helper.log("START TO POLL IFF ERROR [%s] FROM BLOCK [%s] REG [%s]" % (error_field, reg_err.block.name, reg_err.name))  
        reg_err.poll(interval=500, **{error_field: "TRUE"}) 
        self.helper.log("POLL DONE IFF ERROR: [%s]" % str(error_field))  

# SEC FAULT APIs
    def sec_fault_cfg(self, fault_field, enable_list): # 3 types of responses
        reg_config = [erot.NV_PMC.SEC_FAULT_CONFIG_INTERRUPT_0, erot.NV_PMC.SEC_FAULT_CONFIG_FUNCTION_LOCKDOWN_0, erot.NV_PMC.SEC_FAULT_CONFIG_DEVICE_LOCKDOWN_0]
        for reg, en in zip(reg_config, enable_list):
            reg.update(**{fault_field: en})
        self.helper.log("DONE SW CONFIGURING SEC FAULT REG for [%s]: INTERRUPT, FUNC_LOCKDOWN, DEVICE_LOCKDOWN = %r" % (fault_field, enable_list))

    def sec_fault_cfg_en(self, fault_field, resp_idx): # for enabling one of the three
        reg_config = [erot.NV_PMC.SEC_FAULT_CONFIG_INTERRUPT_0, erot.NV_PMC.SEC_FAULT_CONFIG_FUNCTION_LOCKDOWN_0, erot.NV_PMC.SEC_FAULT_CONFIG_DEVICE_LOCKDOWN_0]
        reg_config[resp_idx].write(**{fault_field: 0x1}) # enum different for fields so not supported here
        self.helper.log("DONE SW CONFIGURING SEC FAULT REG for [%s]: INDEX OF [INTERRUPT, FUNC_LOCKDOWN, DEVICE_LOCKDOWN] IS [%d]" % (fault_field, resp_idx))

    def sec_fault_check_cfg_dflt(self, fault_field, is_fused):
        reg_cfg_en = [erot.NV_PMC.SEC_FAULT_CONFIG_INTERRUPT_0, erot.NV_PMC.SEC_FAULT_CONFIG_DEVICE_LOCKDOWN_0]
        reg_cfg_dis = [erot.NV_PMC.SEC_FAULT_CONFIG_FUNCTION_LOCKDOWN_0, ]
        for reg in reg_cfg_en:
            self.fuse_check_reg_log(reg, fault_field, is_fused)
        for reg in reg_cfg_dis:
            self.fuse_check_reg_log(reg, fault_field, exp=0)

    def sec_fault_check_faults(self, fault_field, err_name, is_active_high, is_cleared):
        self.sec_fault_check_err(err_name, is_active_high, is_cleared)
        self.sec_fault_check_err_reg(fault_field, is_cleared)
    
    def sec_fault_check_err(self, err_name, is_active_high, is_cleared):
        exp = is_cleared ^ is_active_high
        err_path = self.sec_fault_get_err_path(err_name)
        act = self.helper.hdl_read(err_path)
        if exp != act: 
            self.helper.perror("ERROR SIGNAL [%s] CHECK FAIL: ACT = [%d], IS_CLEARED = [%d]" % (err_name, act, is_cleared))
        else:
            self.helper.log("ERROR SIGNAL [%s] CHECK PASS: ACT = [%d], IS_CLEARED = [%d]" % (err_name, act, is_cleared))
    
    def sec_fault_check_err_reg(self, fault_field, is_cleared):
        reg_state = erot.NV_PMC.SEC_FAULT_STATUS_0
        self.helper.log("TO CHECK SEC FAULT [%s]: IS_CLEARED = [%s]" % (fault_field, 'YES' if is_cleared else 'NO'))
        self.helper.log("START TO POLL BLOCK [%s] REG [%s] FIELD [%s] VALUE [%d]" % (reg_state.block.name, reg_state.name, fault_field, 0 if is_cleared else 1))
        exp = 'DISABLED' if is_cleared else 'ENABLED'
        reg_state.poll(interval=100, **{fault_field: exp})
        self.helper.log("POLL DONE FIELD [%s]:\n%r" % (fault_field, reg_state.read()))

    def sec_fault_check_intrr(self, is_cleared): 
        self.helper.log("TO CHECK INTERRUPT RESPONSE: IS_CLEARED = [%s]" % ('YES' if is_cleared else 'NO'))
        # check_fsp_turtle
        self.helper.log("TO CHECK FSP TURTLE MODE")
        reg_turt, exp = erot.FSP.RISCV_FAULT_CONTAINMENT_SRCSTAT_0, 0x0 if is_cleared else 0x1 # ('NO_FAULT','FAULTED' )
        self.fuse_check_reg_log(reg_turt, 'ENGINE_IN3', exp)
        # check_oobhub_status
        self.helper.log("TO CHECK OOBHUB DEVICE STATUS")
        reg_state, exp_st = erot.OOBHUB.RCV_STATUS_0_0, 0 if is_cleared else 15 # 'FATAL_ERROR' or 'STATUS_PENDING'
        self.fuse_check_reg_log(reg_state, 'DEVICE_STATUS', exp_st)

    def sec_fault_check_err_rpt(self, fault_field, err_bit, resp_idx, iff_posit, is_cleared): # err_bit refer to GFD instead of manual
        self.sec_fault_check_l0_rpt(fault_field, resp_idx, is_cleared)
        self.sec_fault_check_oobh_rpt(err_bit, resp_idx, iff_posit, is_cleared)

    def sec_fault_check_l0_rpt(self, fault_field, resp_idx, is_cleared): 
        resp_field = ['RESPONSE_INTERRUPT', 'RESPONSE_FUNCTION_LOCKDOWN', 'RESPONSE_DEVICE_LOCKDOWN']
        reg_l0 = erot.NV_PMC.SEC_FAULT_L0_STATUS_0
        exp = 0x0 if is_cleared else 0x1
        self.fuse_check_reg_log(reg_l0, fault_field, exp) # 'ENABLED'
        self.fuse_check_reg_log(reg_l0, resp_field[resp_idx], exp)

    def sec_fault_check_oobh_rpt(self, err_bit, resp_idx, iff_posit, is_cleared):
        reg_dbg_4, reg_dbg_5 = erot.OOBHUB.RCV_STATUS_4_0, erot.OOBHUB.RCV_STATUS_5_0
        resp_bit = 25 - resp_idx
        exp = 0x0 if is_cleared else 0x1
        self.fuse_check_reg_log(reg_dbg_4, 'VENDOR_STATUS_SEC_FAULT', exp<<err_bit | exp<<resp_bit) # no enum for field
        self.fuse_check_reg_log(reg_dbg_5, 'VENDOR_STATUS_SEC_FAULT', 0X0) # not in use
        self.fuse_check_reg_log(reg_dbg_5, 'VENDOR_STATUS_SEC_FAULT_IFF', iff_posit)  # not be cleared by sw unless l3 rst

    def sec_fault_check_dflt_rpt_not_clear(self, fault_field, err_bit): # if not related to iff
        reg_l0 = erot.NV_PMC.SEC_FAULT_L0_STATUS_0
        exp = 0x1
        self.fuse_check_reg_log(reg_l0, fault_field, exp) # 'ENABLED'
        self.fuse_check_reg_log(reg_l0, 'RESPONSE_INTERRUPT', exp)
        self.fuse_check_reg_log(reg_l0, 'RESPONSE_DEVICE_LOCKDOWN', exp)
        reg_dbg_4, reg_dbg_5 = erot.OOBHUB.RCV_STATUS_4_0, erot.OOBHUB.RCV_STATUS_5_0
        self.fuse_check_reg_log(reg_dbg_4, 'VENDOR_STATUS_SEC_FAULT', exp<<err_bit | exp<<23 | exp<<25) # no enum for field
        self.fuse_check_reg_log(reg_dbg_5, 'VENDOR_STATUS_SEC_FAULT', 0X0) # not in use
        self.fuse_check_reg_log(reg_dbg_5, 'VENDOR_STATUS_SEC_FAULT_IFF', 0x0)

    def sec_fault_poll_err(self, err_name, exp):
        self.helper.log("START TO POLL SEC FAULT SIGNAL: [%s]" % err_name)
        err_path = self.sec_fault_get_err_path(err_name)
        self.helper.hdl_wait(err_path, exp)
        self.helper.log("POLL DONE SEC FAULT SIGNAL: [%s]" % err_name)

    def sec_fault_poll_l1_l3_rst(self):
        self.sec_fault_wait_l1_rst_assert()
        self.sec_fault_wait_l3_rst_assert()
        self.sec_fault_wait_l1_rst_deassert()
        self.sec_fault_wait_l3_rst_deassert()

    def sec_fault_wait_l1_rst_assert(self):
        self.helper.log("START TO WAIT [L1] RST ASSERT")
        self.helper.hdl_wait("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_reset.L1_rst_", 0x0) 
        self.helper.log("[L1] RST ASSERTED")

    def sec_fault_wait_l1_rst_deassert(self):
        self.helper.log("START TO WAIT [L1] RST RELEASED")
        self.helper.hdl_wait("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_reset.L1_rst_", 0x1)
        self.helper.log("[L1] RST RELEASED")
    
    def sec_fault_poll_l3_rst(self):
        self.sec_fault_wait_l3_rst_assert()
        self.sec_fault_wait_l3_rst_deassert()

    def sec_fault_wait_l3_rst_assert(self):
        self.helper.log("START TO WAIT [L3] RST ASSERT")
        self.helper.hdl_wait("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_reset.L3_rst_", 0x0) 
        self.helper.log("[L3] RST ASSERTED")

    def sec_fault_wait_l3_rst_deassert(self):
        self.helper.log("START TO WAIT [L3] RST RELEASED")
        self.helper.hdl_wait("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_reset.L3_rst_", 0x1)
        self.helper.log("[L3] RST RELEASED")

    def sec_fault_trig_l0_rst(self):
        self.power_down_seq(larger_gap_pdm_io_vsr2=1)
        self.power_on_seq()
        self.helper.log("POWER DOWN -> POWER ON SEQUENCE DONE")
        self.helper.hdl_wait("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_reset.L3_rst_", 0x1)
        self.helper.log("[L3] RST RELEASED")

    def sec_fault_wait_ucode_restore(self):
        self.helper.log("start to wait 100 us for ucode to restore")
        self.helper.wait_sim_time("us", 100)
        self.helper.log("100 us passed - suppose reg model is ready")

    def sec_fault_get_err_path(self, err_signal_name):
        return 'ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_sysctrl.'+ err_signal_name

# FUSE APIs
    def fuse_sense_done(self):
        self.log('start to poll fuse_sense_done')
        erot.FUSE.FUSECTRL_0.poll(FUSE_SENSE_DONE='YES')
        self.log('poll done fuse_sense_done')
    
    def fuse_init_sense(self):
        self.log('start to poll fuse_init_sense_done')
        erot.FUSE.FUSECTRL_0.poll(interval=50000, FUSE_INIT_SENSE_DONE='YES')
        self.log('poll done fuse_init_sense_done')

    def fuse_get_addr(self, fuse_hash_path, fuse_name):
        with open(fuse_hash_path) as f:
            fuse_info = json.load(f)
            if fuse_name not in fuse_info['generic']:
                self.helper.perror("FUSE [%s] NOT FOUND IN HASH !" % fuse_name)
            else:
                info = fuse_info['generic'][fuse_name]
                row, lsb, msb = int(info['row_index']['0']['row']), int(info['row_index']['0']['lsb']), int(info['row_index']['0']['msb'])
                self.helper.log("[DEBUG] TARGET FUSE [%s] ROW INDEX: [%d] LSB: [%d] MSB: [%d]" % (fuse_name, row, lsb, msb))
                return [row, lsb, msb]
    
    def fuse_burn_0(self):
        self.helper.log("BURN ENABLE_FUSE_PROGRAM AS PRE-PRO TO AVOID SKIP FUSING")
        self.fuse_burn(fuse_en=1, addr=0, wdata=0x1)

    def fuse_burn(self, fuse_en, addr, wdata):
        self.helper.hdl_force("ntb_top.u_nv_top.fuse_en", fuse_en)   
        self.fuse_burn_set_addr(addr)
        self.fuse_burn_data(wdata)
        self.fuse_burn_check()

    def fuse_burn_and_check(self, addr, wdata):
        reg_ctl = erot.FUSE.FUSECTRL_0
        self.fuse_burn_set_addr(addr)
        # Write NV_FUSE_ZB_FUSECTRL_BURN_AND_CHECK to 1 to enable the burn and check function
        reg_ctl.update(BURN_AND_CHECK="ENABLE")
        self.fuse_burn_data(wdata)
        # Read NV_FUSE_ZB_FUSECTRL_BURN_AND_CHECK_STATUS to see whether the process is executed successfully. If succeed, go for the next burn process
        self.fuse_check_reg_log(reg_ctl, 'BURN_AND_CHECK_STATUS', exp=0x1)
        self.fuse_burn_check()

    def fuse_burn_set_addr(self, addr):
        reg_ctl = erot.FUSE.FUSECTRL_0
        self.fuse_check_reg_log(reg_ctl, 'PS09_SET', 0x0)
        self.fuse_check_reg_log(reg_ctl, 'PS09_RESET', 0x1)
        reg_ctl.update(PS09_SET='DEASSERT', PS09_RESET='DEASSERT')
        self.helper.log("DONE WRITING PS09_SET='DEASSERT', PS09_RESET='DEASSERT'")
        reg_ctl.update(PS09_SET='ASSERT', PS09_RESET='DEASSERT')
        self.helper.log("DONE WRITING PS09_SET='ASSERT', PS09_RESET='DEASSERT': POWER OF BURNING ENABLED")
        self.helper.wait_sim_time("us", 10)
        self.helper.log("START TO BURN FUSE ADDR 0x%x" % addr)
        erot.FUSE.FUSEADDR_0.write(addr)

    def fuse_burn_data(self, wdata):
        reg_ctl = erot.FUSE.FUSECTRL_0
        erot.FUSE.FUSEWDATA_0.write(wdata) 
        reg_ctl.update(CMD='WRITE')
        self.helper.log("START POLLING FUSECTRL_0 STATE IDLE")
        reg_ctl.poll(STATE="IDLE") 
        self.helper.log("DONE POLLING FUSECTRL_0 STATE IDLE")

    def fuse_burn_check(self):
        reg_ctl = erot.FUSE.FUSECTRL_0
        reg_ctl.update(PS09_SET='DEASSERT', PS09_RESET='DEASSERT') 
        reg_ctl.update(PS09_SET='DEASSERT', PS09_RESET='ASSERT')
        self.fuse_check_reg_log(reg_ctl, 'PS09_SET', 0x0)
        self.fuse_check_reg_log(reg_ctl, 'PS09_RESET', 0x1)
    
    def fuse_resense(self, is_ctrl):
        reg_ctrl = erot.FUSE.FUSECTRL_0
        self.helper.log("START TO TRIGGER %s SECTION RESENSE" % ('CTRL' if is_ctrl else 'FULL'))
        if is_ctrl:
            reg_ctrl.write(CMD='SENSE_CTRL') # Control section resense: program FUSECTRL.CMD to SENSE_CTRL
        else:
            erot.FUSE.PRIV2INTFC_0.write(START_DATA=1) # Full Resense: program PRIV2INTFC_START to 1
        self.helper.log("START POLLING REG [%s] STATE IDLE" % reg_ctrl.name) 
        reg_ctrl.poll(interval=5000,STATE='IDLE') # Resense done: poll done FUSECTRL_STATE = "IDLE"
        self.helper.log("DONE POLLING REG [%s]  STATE IDLE: RESENSE FINISHED" % reg_ctrl.name)

    def fuse_fsp_push_done(self):
        reg = erot.FUSE.PUSH_0
        self.helper.log("START TO POLL FUSE FSP SECTION PUSH DONE")
        reg.poll(interval=5000, FSP_DONE='YES')
        self.helper.log("POLL DONE FUSE FSP SECTION PUSH")

    def fuse_check_fsp_push_status(self):
        reg_status = erot.FSP.KEYSTORE_FUSE_STATUS_0
        self.helper.log("START TO POLL BLOCK %s REG %s SENSED" % (reg_status.block.name, reg_status.name))
        reg_status.poll(interval=500, SENSED=1) # no enum
        rstatus = reg_status.read()
        # check fields
        if rstatus['FUSE_RD_ERR'] | rstatus['OEM_INTEGRITY_CHECK_ERR'] | rstatus['NV_INTEGRITY_CHECK_ERR'] != 0:
            self.helper.perror("CHECK BLOCK %s REG %s FAIL: EXP ALL 0s; ACT IS %r" % (reg_status.block.name, reg_status.name, rstatus))
        else:
            self.helper.log("CHECK BLOCK %s REG %s PASS: %r" % (reg_status.block.name, reg_status.name, rstatus))

    def fuse_check_fsp_row(self, fsp_row_idx, exp):
        # read FSP ram data: totally 520 rows in sr01
        self.helper.log("[DEBUG] INTO FSP ROW %d" % fsp_row_idx)
        reg_idx, reg_status, reg_val = erot.FSP.KEYSTORE_FUSE_ACCESS_INDEX_0, erot.FSP.KEYSTORE_FUSE_ACCESS_STATUS_0, erot.FSP.KEYSTORE_FUSE_ACCESS_VALUE_0
        # write addr to _INDEX
        reg_idx.write(INDEX=(fsp_row_idx<<2))
        # poll status done 
        self.helper.log("START TO POLL REG %s ACCESS_DONE" % reg_status.name)
        reg_status.poll(interval=500, ACCESS_DONE=1) # no enum
        # check VALUE_VALID
        rstatus = reg_status.read()
        if rstatus['VALUE_VALID'] != 0x1:
            self.helper.perror("FSP ROW %d DETECTED INVALID DATA" % fsp_row_idx)
        else:
            self.helper.log("FSP ROW %d DONE CHECKING VALUE_VALID" % fsp_row_idx)
        # read val and compare
        rdata = reg_val.read()
        if rdata['DATA'] != exp:
            self.helper.perror("FSP ROW %d CHECK FAIL: ACT = 0x%x; EXP = 0x%x" % (fsp_row_idx, rdata['DATA'], exp))
        else:
            self.helper.log("FSP ROW %d CHECK PASS: VALUE = 0x%x" % (fsp_row_idx, rdata['DATA']))

    def fuse_force_l1_rst(self):
        self.helper.log("START TO FORCE erot_reset_n FROM ntb_top TO TRIGGER [L1] RESET")
        self.helper.hdl_force('ntb_top.erot_reset_n', 0)
        self.helper.hdl_wait("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_reset.L1_rst_", 0x0)
        self.helper.log("[L1] RST ASSERTED")
        self.sec_fault_wait_l3_rst_assert()
        self.helper.log("WAITING FOR 100 NS TO RELEASE [L1] RST")
        self.helper.wait_sim_time("ns", 100)
        self.helper.hdl_force('ntb_top.erot_reset_n', 1)
        self.helper.hdl_wait("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_reset.L1_rst_", 0x1)
        self.helper.log("[L1] RST RELEASED")
        self.sec_fault_wait_l3_rst_deassert()

    def fuse_sw_trig_l3_rst(self):
        self.helper.log("START TO WRITE REG [SW_L3_RST_0] TO TRIGGER [L3] RESET")
        erot.RESET.NVEROT_RESET_CFG.SW_L3_RST_0.write(RESET_LEVEL3=0) # no enum
        self.sec_fault_poll_l3_rst()

    def fuse_check_reg_log(self, reg, field_name, exp): # this api not support enum yet
        rd = reg.read()
        act = rd[field_name]
        if act != exp:
            self.helper.perror("BLOCK [%s] REG [%s] FIELD [%s] VALUE CHECK FAIL: EXP = [0x%x]; ACT = [0x%x]\n%r" % (reg.block.name, reg.name, field_name, exp, act, rd))
        else:
            self.helper.log("BLOCK [%s] REG [%s] FIELD [%s] VALUE CHECK PASS:\n%r" % (reg.block.name, reg.name, field_name, rd))

    def fuse_check_rst_val(self, reg, error_is_info=False):
        self.helper.log("TO CHECK BLOCK [%s] REG [%s] RESET VALUE" % (reg.block.name, reg.name))
        mask = reg.reset_mask & reg.read_mask
        if mask == 0:
            self.helper.log("SKIP AS NON-READABLE OR NO RESET VALUE")
            return
        act_reg = reg.read()
        if isinstance(act_reg.value, str):
            if error_is_info:
                self.helper.log("[MISMATCH] READING REG { %s } RETURNS '%s' !" % (reg.name, act_reg.value))
            else:
                self.helper.perror("READING REG { %s } RETURNS '%s' !" % (reg.name, act_reg.value))
        else:
            act, exp = act_reg.value & mask, reg.reset_val & mask
            if act != exp:
                if error_is_info:
                    self.helper.log("[MISMATCH] REG { %s } RESET VAL: EXP = [0x%x], ACT = [0x%x]\n%r\n" % (reg.name, exp, act, act_reg))
                else:
                    self.helper.perror("REG { %s } RESET CHECK FAIL: EXP = [0x%x], ACT = [0x%x]\n%r\n" % (reg.name, exp, act, act_reg))
            else:
                self.helper.log("RESET VALUE PASS:\n%r" % act_reg)

    def fuse_hdl_check(self, path, exp):
        self.helper.log("TO EXAMINE SIGNAL PATH [%s]" % path)
        act = self.helper.hdl_read(path)
        if act != exp:
            self.helper.perror("SIGNAL HDL CHECK FAIL: EXP = [0x%x], ACT = [0x%x]" % (exp, act))
        else:
            self.helper.log("SIGNAL HDL CHECK PASS: [0x%x]" % act)

# end fuse api

    def block_write(self, addr, smb_cmd, byte, data):
        #pre-step: define master and slave
        mst = erot.I2C_IB0
        send = 1
        no_ack = 0
        cmd2 = 0 #write
        cmd1 = 0 #write
        length = byte+1 #in bytes 
        two_slv_en = 0

        #seq1: configure two slave's registers         
        #seq2: configure master register and trigger transaction
        mst.I2C_CMD_ADDR0_0.write(addr<<1)
        mst.I2C_CMD_DATA1_0.write(data*(2**16)+length*(2**8)+smb_cmd)
        mst_cnfg = (send<<9)+(no_ack<<8)+(cmd2<<7)+(cmd1<<6)+(two_slv_en<<4)+(length<<1)
        print ("mst_cnfg = %d" % mst_cnfg)
        mst.I2C_CNFG_0.write(mst_cnfg)    

        #seq3: wait for bus idle and check mst_cnfg
        #wait for master bus idle
        rd = mst.I2C_STATUS_0.read()
        while rd['BUSY'] == 0x1 :
            rd = mst.I2C_STATUS_0.read()
            print("Waiting for bus idle...")

        #seq4: clear cmd data
        mst.I2C_CMD_DATA1_0.write(0x0)
        print("clear cmd data register after write done")
        #wait for some time in case out of order response
        self.helper.wait_sim_time("ns",1000)

    def block_write_packet(self, addr, smb_cmd, byte, data):
        mst = erot.I2C_IB0
        #initialization
        mst.I2C_CMD_ADDR0_0.write(0)
        mst.I2C_CMD_ADDR1_0.write(0)
        mst.I2C_CMD_DATA1_0.write(0)
        mst.I2C_CMD_DATA2_0.write(0)
        mst.I2C_CLKEN_OVERRIDE_0.write(0)
        mst.I2C_DEBUG_CONTROL_0.write(0)
        mst.I2C_INTERRUPT_SET_REGISTER_0.write(0)
        mst.I2C_INTERFACE_TIMING_0_0.write(0x0204)
        mst.I2C_INTERFACE_TIMING_1_0.write(0x04070404)
        mst.I2C_HS_INTERFACE_TIMING_0_0.write(0x0308)
        mst.I2C_HS_INTERFACE_TIMING_1_0.write(0x0b0b0b)
        #configure fifo trigger level
        mst.MST_FIFO_CONTROL_0.write(TX_FIFO_TRIG = 0x3)
        #configure packet mode
        mst.I2C_CNFG_0.write(MULTI_MASTER_MODE = 0, PACKET_MODE_EN = 1)
        #activate configuration
        mst.I2C_CONFIG_LOAD_0.write(TIMEOUT_CONFIG_LOAD = 0x1,SLV_CONFIG_LOAD = 0,MSTR_CONFIG_LOAD = 0x1)
        rd = mst.I2C_CONFIG_LOAD_0.read()
        print(rd)
        print("check config load")
        while rd['TIMEOUT_CONFIG_LOAD'] | rd['MSTR_CONFIG_LOAD'] == 0x1 :
            rd = mst.I2C_CONFIG_LOAD_0.read()
            print ("Wait for setting master's register")

        #enable interrupt
        mst.INTERRUPT_MASK_REGISTER_0.write(ARB_LOST_INT_EN = 1,NOACK_INT_EN=1, TFIFO_OVF_INT_EN=1,ALL_PACKETS_XFER_COMPLETE_INT_EN=1,PACKET_XFER_COMPLETE_INT_EN=1,TFIFO_DATA_REQ_INT_EN=1)

        #word_0
        mst.INTERRUPT_MASK_REGISTER_0.write(TFIFO_DATA_REQ_INT_EN = 1) 
        rd = mst.I2C_INTERRUPT_SOURCE_REGISTER_0.read()
        print("check TFIFO DATA REQ")
        while rd['TFIFO_DATA_REQ'] == 0:
            rd = mst.I2C_INTERRUPT_SOURCE_REGISTER_0.read()
            print("reading TFIFO_DATA_REQ from I2C_INTERRUPT_SOURCE_REGISTER_0")        
        mst.INTERRUPT_MASK_REGISTER_0.write(TFIFO_DATA_REQ_INT_EN = 0)   
        ProtHdrSz = 0
        PktId = 0
        Controller_ID = 0
        Protocol = 1
        PktType = 0
        word_0 = ProtHdrSz*(2**28)+PktId*(2**16)+Controller_ID*(2**12)+Protocol*(2**4)+PktType
        print(f"word_0 = {hex(word_0)}")
        mst.I2C_TX_PACKET_FIFO_0.write(word_0)

        #word_1
        mst.INTERRUPT_MASK_REGISTER_0.write(TFIFO_DATA_REQ_INT_EN = 1) 
        rd = mst.I2C_INTERRUPT_SOURCE_REGISTER_0.read()
        while rd['TFIFO_DATA_REQ'] == 0:
            rd = mst.I2C_INTERRUPT_SOURCE_REGISTER_0.read()
            print("reading TFIFO_DATA_REQ from I2C_INTERRUPT_SOURCE_REGISTER_0")
        mst.INTERRUPT_MASK_REGISTER_0.write(TFIFO_DATA_REQ_INT_EN = 0)
        PayloadSize = byte+1
        word_1 = PayloadSize
        print(f"word_1 = {hex(word_1)}")
        mst.I2C_TX_PACKET_FIFO_0.write(word_1)

        #word_2
        mst.INTERRUPT_MASK_REGISTER_0.write(TFIFO_DATA_REQ_INT_EN = 1) 
        rd = mst.I2C_INTERRUPT_SOURCE_REGISTER_0.read()
        while rd['TFIFO_DATA_REQ'] == 0:
            rd = mst.I2C_INTERRUPT_SOURCE_REGISTER_0.read()
            print("reading TFIFO_DATA_REQ from I2C_INTERRUPT_SOURCE_REGISTER_0")
        mst.INTERRUPT_MASK_REGISTER_0.write(TFIFO_DATA_REQ_INT_EN = 0)
        HS_MODE = 0
        CONTINUE_ON_NACK = 0
        SEND_START_BYTE = 0
        READ_WRITE = 0
        Address_mode = 0
        IE = 0
        REPEAT_START_STOP = 0
        ContinueXfer = 0
        HS_MASTER_ADDR = 0
        SLAVE_ADDR = addr*2+READ_WRITE
        word_2 = HS_MODE*(2**22)+CONTINUE_ON_NACK*(2**21)+SEND_START_BYTE*(2**20)+READ_WRITE*(2**19)+Address_mode*(2**18)+IE*(2**17)+REPEAT_START_STOP*(2**16)+ContinueXfer*(2**15)+HS_MASTER_ADDR*(2**12)+SLAVE_ADDR
        print(f"word_2 = {hex(word_2)}")
        mst.I2C_TX_PACKET_FIFO_0.write(word_2)

       #payload
        mst.INTERRUPT_MASK_REGISTER_0.write(TFIFO_DATA_REQ_INT_EN = 1) 
        rd = mst.I2C_INTERRUPT_SOURCE_REGISTER_0.read()
        while rd['TFIFO_DATA_REQ'] == 0:
            rd = mst.I2C_INTERRUPT_SOURCE_REGISTER_0.read()
            print("reading TFIFO_DATA_REQ from I2C_INTERRUPT_SOURCE_REGISTER_0")
        mst.INTERRUPT_MASK_REGISTER_0.write(TFIFO_DATA_REQ_INT_EN = 0)
        rd = mst.INTERRUPT_STATUS_REGISTER_0.read()
        mst.I2C_TX_PACKET_FIFO_0.write(data*(2**16)+byte*(2**8)+smb_cmd)

        if byte > 2:
            mst.INTERRUPT_MASK_REGISTER_0.write(TFIFO_DATA_REQ_INT_EN = 1) 
            rd = mst.I2C_INTERRUPT_SOURCE_REGISTER_0.read()
            while rd['TFIFO_DATA_REQ'] == 0:
                rd = mst.I2C_INTERRUPT_SOURCE_REGISTER_0.read()
                print("reading TFIFO_DATA_REQ from I2C_INTERRUPT_SOURCE_REGISTER_0")
            mst.INTERRUPT_MASK_REGISTER_0.write(TFIFO_DATA_REQ_INT_EN = 0)
            rd = mst.INTERRUPT_STATUS_REGISTER_0.read()
            print(f"data = {data//(2**16)}")
            mst.I2C_TX_PACKET_FIFO_0.write(data//(2**16))
        req_time = 500
        while (rd['PACKET_XFER_COMPLETE'] == 0) & (req_time > 0):
            print("waiting for transfer completed")
            print(f"req_time = {req_time}")
            rd = mst.INTERRUPT_STATUS_REGISTER_0.read()
            req_time = req_time - 1
        if req_time == 0:
            helper.perror("can not transfer packet")

########################################################################################
#Config QSPI initiator API
    #send 1-1-X write command with 
    def config_qspi_cmb_cmd(self,spi,opcode,no_addr,address,address_size):
        spi.GLOBAL_CONFIG_0.update(CMB_SEQ_EN=1)
        spi.CMB_SEQ_CMD_CFG_0.update(COMMAND_SIZE=7,NO_ADDR_PHASE=no_addr)
        spi.CMB_SEQ_CMD_0.write(opcode)
        spi.CMB_SEQ_ADDR_CFG_0.update(ADDRESS_SIZE=address_size-1,ADDRESS_EN_LE_Byte=1)
        spi.CMB_SEQ_ADDR_0.write(address) 
        spi.INTR_MASK_0.update(RDY_INTR_MASK=0)    
    
    def config_4B_write_data(self,spi,data):
        spi.DMA_BLK_SIZE_0.write(0)
        spi.TX_FIFO_0.write(data)
  
    def config_16B_write_data(self,spi,data0,data1,data2,data3):
        spi.DMA_BLK_SIZE_0.write(3)
        spi.TX_FIFO_0.write(data0)
        spi.TX_FIFO_0.write(data1)        
        spi.TX_FIFO_0.write(data2)
        spi.TX_FIFO_0.write(data3)

    def config_32B_write_data(self,spi,data0,data1,data2,data3):
        spi.DMA_BLK_SIZE_0.write(7)
        spi.TX_FIFO_0.write(data0)
        spi.TX_FIFO_0.write(data1)        
        spi.TX_FIFO_0.write(data2)
        spi.TX_FIFO_0.write(data3)
        spi.TX_FIFO_0.write(data3)
        spi.TX_FIFO_0.write(data2)        
        spi.TX_FIFO_0.write(data1)
        spi.TX_FIFO_0.write(data0)
    
    def read_16B_data(self,spi):
        rd = spi.RX_FIFO_0.read()
        rd = spi.RX_FIFO_0.read()
        rd = spi.RX_FIFO_0.read()
        rd = spi.RX_FIFO_0.read()  

    def read_flash_data_for_check(self,spi,data):
        rd = spi.RX_FIFO_0.read()   
        if rd.value != data:
            self.helper.perror("Reg Read/Write Fail -> %s" % str(spi.RX_FIFO_0))

    def read_32B_data(self,spi):
        rd = spi.RX_FIFO_0.read()
        rd = spi.RX_FIFO_0.read()
        rd = spi.RX_FIFO_0.read()
        rd = spi.RX_FIFO_0.read()
        rd = spi.RX_FIFO_0.read()
        rd = spi.RX_FIFO_0.read()
        rd = spi.RX_FIFO_0.read()
        rd = spi.RX_FIFO_0.read()

    def send_cmd(self,spi,tx_en,rx_en,bit_length,data_line,dummy_cycle,cs):
        spi.COMMAND_0.update(M_S='MASTER',CS_SEL=cs,BIT_LENGTH=bit_length,Tx_EN=tx_en,Rx_EN=rx_en,PACKED='ENABLE',INTERFACE_WIDTH=data_line,En_LE_Byte=0,En_LE_Bit=0)
        spi.MISC_0.update(NUM_OF_DUMMY_CLK_CYCLES=dummy_cycle)
        spi.COMMAND_0.update(PIO='PIO')
        spi.TRANSFER_STATUS_0.poll(timeout=100,RDY=1)
        spi.TRANSFER_STATUS_0.write(RDY=1)    

    def send_write_1_1_x_cmd(self,spi,opcode,address,address_size,data_line,data_byte,data0,data1,data2,data3):
        self.config_qspi_cmb_cmd(spi,opcode,0,address,address_size)
        if data_byte == 3 :
            self.config_16B_write_data(spi,data0,data1,data2,data3)
        else:
            self.config_32B_write_data(spi,data0,data1,data2,data3)
        self.send_cmd(spi,1,0,31,data_line,0,0)

    def send_write_1_0_x_cmd(self,spi,opcode,data_line,data,bit_length):
        self.config_qspi_cmb_cmd(spi,opcode,1,0,1)
        self.config_4B_write_data(spi,data)    
        self.send_cmd(spi,1,0,bit_length-1,data_line,0,0)

    def send_write_1_1_0_cmd(self,spi,opcode,data_line,data,bit_length):
        self.config_qspi_cmb_cmd(spi,opcode,1,0,1)
        self.config_4B_write_data(spi,data)    
        spi.COMMAND_0.update(M_S='MASTER',BIT_LENGTH=bit_length-1,Tx_EN=1,Rx_EN=0,PACKED='ENABLE',INTERFACE_WIDTH=data_line,En_LE_Byte=1,En_LE_Bit=0)
        spi.MISC_0.update(NUM_OF_DUMMY_CLK_CYCLES=0)
        spi.COMMAND_0.update(PIO='PIO')
        spi.TRANSFER_STATUS_0.poll(timeout=100,RDY=1)
        spi.TRANSFER_STATUS_0.write(RDY=1)  

    def send_read_1_1_x_cmd(self,spi,opcode,address,address_size,data_line,data_byte,dummy_cycle):
        self.config_qspi_cmb_cmd(spi,opcode,0,address,address_size)  
        spi.DMA_BLK_SIZE_0.write(data_byte)
        self.send_cmd(spi,0,1,31,data_line,dummy_cycle,0) 
        if data_byte == 3 :
            self.read_16B_data(spi)
        else:
            self.read_32B_data(spi)

    def send_read_1_1_x_cmd_flash(self,spi,opcode,address,address_size,data_line,data_byte,dummy_cycle):
        self.config_qspi_cmb_cmd(spi,opcode,0,address,address_size)  
        spi.DMA_BLK_SIZE_0.write(data_byte)
        self.send_cmd(spi,0,1,31,data_line,dummy_cycle,0) 

    def send_read_1_0_x_cmd(self,spi,opcode,data_line,bit_length,dummy_cycle):
        self.config_qspi_cmb_cmd(spi,opcode,1,0,1)
        spi.DMA_BLK_SIZE_0.write(0)          
        self.send_cmd(spi,0,1,bit_length-1,data_line,dummy_cycle,0)
        rd = spi.RX_FIFO_0.read()          

    def send_read_1_0_x_cmd_cs1(self,spi,opcode,data_line,bit_length,dummy_cycle):
        self.config_qspi_cmb_cmd(spi,opcode,1,0,1)
        spi.DMA_BLK_SIZE_0.write(0)          
        self.send_cmd(spi,0,1,bit_length-1,data_line,dummy_cycle,1)
        rd = spi.RX_FIFO_0.read() 

    def send_read_1_1_x_cmd_cs1(self,spi,opcode,address,address_size,data_line,data_byte,dummy_cycle):
        self.config_qspi_cmb_cmd(spi,opcode,0,address,address_size)  
        spi.DMA_BLK_SIZE_0.write(data_byte)
        self.send_cmd(spi,0,1,31,data_line,dummy_cycle,1) 
        if data_byte == 3 :
            self.read_16B_data(spi)
        else:
            self.read_32B_data(spi)

    def send_1_0_0_cmd(self,spi,data,size):
        spi.GLOBAL_CONFIG_0.update(CMB_SEQ_EN=0)
        spi.CMB_SEQ_CMD_CFG_0.update(COMMAND_SIZE=0)
        spi.CMB_SEQ_CMD_0.write(0x0)
        spi.CMB_SEQ_ADDR_CFG_0.update(ADDRESS_SIZE=0)
        spi.CMB_SEQ_ADDR_0.write(0x0)
        spi.INTR_MASK_0.update(RDY_INTR_MASK=0)
        spi.DMA_BLK_SIZE_0.write(0)
        spi.MISC_0.update(NUM_OF_DUMMY_CLK_CYCLES=0)        
        spi.TX_FIFO_0.write(data)
        spi.COMMAND_0.update(M_S='MASTER',BIT_LENGTH=size-1,Rx_EN='DISABLE',Tx_EN='ENABLE',PACKED='ENABLE',INTERFACE_WIDTH='SINGLE',En_LE_Byte=1,En_LE_Bit=0)
        spi.COMMAND_0.update(PIO='PIO')
        spi.TRANSFER_STATUS_0.poll(timeout=100,RDY=1)
        spi.TRANSFER_STATUS_0.write(RDY=1) 

    def send_read_1_1_x_socv(self,spi,opcode,address,address_size,data_line,data_byte,dummy_cycle,cs):
        self.config_qspi_cmb_cmd(spi,opcode,0,address,address_size)  
        spi.DMA_BLK_SIZE_0.write(data_byte)
        self.send_cmd(spi,0,1,31,data_line,dummy_cycle,cs)

    def send_write_1_1_x_socv(self,spi,opcode,address,address_size,data_line,data_byte,data0,data1,data2,data3,cs):
        self.config_qspi_cmb_cmd(spi,opcode,0,address,address_size)
        if data_byte == 3 :
            self.config_16B_write_data(spi,data0,data1,data2,data3)
        else:
            self.config_32B_write_data(spi,data0,data1,data2,data3)
        self.send_cmd(spi,1,0,31,data_line,0,cs)

    def send_1_0_0_socv(self,spi,data,size,cs):
        spi.GLOBAL_CONFIG_0.update(CMB_SEQ_EN=0)
        spi.CMB_SEQ_CMD_CFG_0.update(COMMAND_SIZE=0)
        spi.CMB_SEQ_CMD_0.write(0x0)
        spi.CMB_SEQ_ADDR_CFG_0.update(ADDRESS_SIZE=0)
        spi.CMB_SEQ_ADDR_0.write(0x0)
        spi.INTR_MASK_0.update(RDY_INTR_MASK=0)
        spi.DMA_BLK_SIZE_0.write(0)
        spi.MISC_0.update(NUM_OF_DUMMY_CLK_CYCLES=0)        
        spi.TX_FIFO_0.write(data)
        spi.COMMAND_0.update(M_S='MASTER',CS_SEL=cs,BIT_LENGTH=size-1,Rx_EN='DISABLE',Tx_EN='ENABLE',PACKED='ENABLE',INTERFACE_WIDTH='SINGLE',En_LE_Byte=1,En_LE_Bit=0)
        spi.COMMAND_0.update(PIO='PIO')
        spi.TRANSFER_STATUS_0.poll(timeout=100,RDY=1)
        spi.TRANSFER_STATUS_0.write(RDY=1)     


###########################################################################################################################################
    #check output cs value of bypass monitor
    def check_cs_result(self,spi,cs,cs_golden_value):
        monitor_cs_path = 'ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_bypmon0.nverot_bypmon_spi_cs_'+cs+'_out_'
        cs_value = self.helper.hdl_read(monitor_cs_path)
        if cs_value != cs_golden_value:
            self.helper.perror("cs value wrong %s" % str(cs_value))

    #check output interrupt of bypass monitor
    def check_intr_result(self,spi,intr_golden_value):
        monitor_intr_path = 'ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_bypmon0.nverot_bypmon_interrupt'
        intr_value = self.helper.hdl_read(monitor_intr_path)
        if intr_value != intr_golden_value:
            self.helper.perror("intr value wrong %s" % str(intr_value))  

    #check clock gate of bypass monitor
    def check_clk_result(self,flash,value):
        cnt_path = 'ntb_top.qspi_flashes['+flash+'].u_flash_sck_cnter.sck_cnt[31:0]'   
        cnt = self.helper.hdl_read(hdl_path=cnt_path)  
        if cnt != value:
            self.helper.perror("Cnt value wrong %s" % str(cnt))
            self.helper.perror("Expected cnt value should be %s" % str(value))
            self.helper.perror("Path of cnt is %s" % str(cnt_path))           

    #check tx clock gate of bypass monitor
    def check_tx_clk_result(self,flash,value):
        cnt_path = 'ntb_top.qspi_flashes['+flash+'].u_flash_sck_cnter.sck_tx_cnt[31:0]'   
        cnt = self.helper.hdl_read(hdl_path=cnt_path)  
        if cnt != value:
            self.helper.perror("Cnt value wrong %s" % str(cnt))
            self.helper.perror("Expected tx_cnt value should be %s" % str(value))
            self.helper.perror("Path of cnt is %s" % str(cnt_path)) 

    #check rx clock gate of bypass monitor
    def check_rx_clk_result(self,flash,value):
        cnt_path = 'ntb_top.qspi_flashes['+flash+'].u_flash_sck_cnter.sck_rx_cnt[31:0]'   
        cnt = self.helper.hdl_read(hdl_path=cnt_path)  
        if cnt != value:
            self.helper.perror("Cnt value wrong %s" % str(cnt))
            self.helper.perror("Expected rx_cnt value should be %s" % str(value))
            self.helper.perror("Path of cnt is %s" % str(cnt_path))     

    #resume bypass monitor for unrecoverable error, and clear interrupt
    def resume_bm(self,bm,resume_enable,int_clear):
        bm.clear_ctrl_0.update(resume=resume_enable,int_clr=int_clear)

    #snap shot the log_buffer for FW to read command information
    def log_snap(self,bm,snap):
        bm.clear_ctrl_0.update(log_snap=snap)

    #clear log buffer information
    def log_clear(self,bm,log_clr):
        bm.clear_ctrl_0.update(log_buf_clr=log_clr)  

    #check common_log_buffer
    def check_common_log_buffer(self,bm,reg_num,value_0,value_1,value_2):
        reg0 = 'log_buffer_'+reg_num+'_0_0'
        log_reg0 = bm.get_reg_by_name(reg0)
        reg1 = 'log_buffer_'+reg_num+'_1_0'
        log_reg1 = bm.get_reg_by_name(reg1)
        reg2 = 'log_buffer_'+reg_num+'_2_0'
        log_reg2 = bm.get_reg_by_name(reg2)

        cmd_og_addr = log_reg0.read()
        print(cmd_og_addr.value)
        if cmd_og_addr.value != value_0:
            self.helper.perror("Reg %s Read wrong" % str(log_reg0))
            self.helper.perror("Expect value should be %s" % str(hex(value_0)))

        cmd_incr_addr = log_reg1.read()
        print(cmd_incr_addr.value)
        if cmd_incr_addr.value != value_1:
            self.helper.perror("Reg %s Read wrong" % str(log_reg1))
            self.helper.perror("Expect value should be %s" % str(hex(value_1)))

        cmd_info = log_reg2.read()
        print(cmd_info.value)
        if cmd_info.value != value_2:
            self.helper.perror("Reg %s Read wrong" % str(log_reg2))
            self.helper.perror("Expect value should be %s" % str(hex(value_2)))

    #check common_log_buffer_x_0
    def check_common_log_buffer_0(self,bm,reg_num,value_0):
        reg0 = 'log_buffer_'+reg_num+'_0_0'
        log_reg0 = bm.get_reg_by_name(reg0)
        cmd_og_addr = log_reg0.read()
        print(cmd_og_addr.value)
        if cmd_og_addr.value != value_0:
            self.helper.perror("Reg %s Read wrong" % str(log_reg0))
            self.helper.perror("Expect value should be %s" % str(hex(value_0)))

    #check common_log_buffer_x_1
    def check_common_log_buffer_1(self,bm,reg_num,value_1):
        reg1 = 'log_buffer_'+reg_num+'_1_0'
        log_reg1 = bm.get_reg_by_name(reg1)
        cmd_incr_addr = log_reg1.read()
        print(cmd_incr_addr.value)
        if cmd_incr_addr.value != value_1:
            self.helper.perror("Reg %s Read wrong" % str(log_reg1))
            self.helper.perror("Expect value should be %s" % str(hex(value_1)))

    #check common_log_buffer_x_2
    def check_common_log_buffer_2(self,bm,reg_num,value_2):
        reg2 = 'log_buffer_'+reg_num+'_2_0'
        log_reg2 = bm.get_reg_by_name(reg2)
        cmd_info = log_reg2.read()
        print(cmd_info.value)
        if cmd_info.value != value_2:
            self.helper.perror("Reg %s Read wrong" % str(log_reg2))
            self.helper.perror("Expect value should be %s" % str(hex(value_2)))

    #check common_log_buffer_snap
    def check_common_log_buffer_snap(self,bm,reg_num,value_0,value_1,value_2):
        reg0 = 'log_buffer_snap_'+reg_num+'_0_0'
        log_reg0 = bm.get_reg_by_name(reg0)
        reg1 = 'log_buffer_snap_'+reg_num+'_1_0'
        log_reg1 = bm.get_reg_by_name(reg1)
        reg2 = 'log_buffer_snap_'+reg_num+'_2_0'
        log_reg2 = bm.get_reg_by_name(reg2)

        cmd_og_addr = log_reg0.read()
        print(cmd_og_addr.value)
        if cmd_og_addr.value != value_0:
            self.helper.perror("Reg %s Read wrong" % str(log_reg0))
            self.helper.perror("Expect value should be %s" % str(hex(value_0)))

        cmd_incr_addr = log_reg1.read()
        print(cmd_incr_addr.value)
        if cmd_incr_addr.value != value_1:
            self.helper.perror("Reg %s Read wrong" % str(log_reg1))
            self.helper.perror("Expect value should be %s" % str(hex(value_1)))

        cmd_info = log_reg2.read()
        print(cmd_info.value)
        if cmd_info.value != value_2:
            self.helper.perror("Reg %s Read wrong" % str(log_reg2))
            self.helper.perror("Expect value should be %s" % str(hex(value_2)))

    #check common_log_buffer_snap_0
    def check_common_log_buffer_snap_0(self,bm,reg_num,value_0):
        reg0 = 'log_buffer_snap_'+reg_num+'_0_0'
        log_reg0 = bm.get_reg_by_name(reg0)
        cmd_og_addr = log_reg0.read()
        print(cmd_og_addr.value)
        if cmd_og_addr.value != value_0:
            self.helper.perror("Reg %s Read wrong" % str(log_reg0))
            self.helper.perror("Expect value should be %s" % str(hex(value_0)))

    #check common_log_buffer_snap_1
    def check_common_log_buffer_snap_1(self,bm,reg_num,value_1):
        reg1 = 'log_buffer_snap_'+reg_num+'_1_0'
        log_reg1 = bm.get_reg_by_name(reg1)
        cmd_incr_addr = log_reg1.read()
        print(cmd_incr_addr.value)
        if cmd_incr_addr.value != value_1:
            self.helper.perror("Reg %s Read wrong" % str(log_reg1))
            self.helper.perror("Expect value should be %s" % str(hex(value_1)))

    #check common_log_buffer_snap_2
    def check_common_log_buffer_snap_2(self,bm,reg_num,value_2):
        reg2 = 'log_buffer_snap_'+reg_num+'_2_0'
        log_reg2 = bm.get_reg_by_name(reg2)
        cmd_info = log_reg2.read()
        print(cmd_info.value)
        if cmd_info.value != value_2:
            self.helper.perror("Reg %s Read wrong" % str(log_reg2))
            self.helper.perror("Expect value should be %s" % str(hex(value_2)))

    #check erase_log_buffer
    def check_erase_log_buffer(self,bm,reg_num,value_0,value_1,value_2):
        reg0 = 'ers_log_buf_'+reg_num+'_0_0'
        log_reg0 = bm.get_reg_by_name(reg0)
        reg1 = 'ers_log_buf_'+reg_num+'_1_0'
        log_reg1 = bm.get_reg_by_name(reg1)
        reg2 = 'ers_log_buf_'+reg_num+'_2_0'
        log_reg2 = bm.get_reg_by_name(reg2)

        cmd_og_addr = log_reg0.read()
        print(cmd_og_addr.value)
        if cmd_og_addr.value != value_0:
            self.helper.perror("Reg %s Read wrong" % str(log_reg0))
            self.helper.perror("Expect value should be %s" % str(hex(value_0)))

        cmd_incr_addr = log_reg1.read()
        print(cmd_incr_addr.value)
        if cmd_incr_addr.value != value_1:
            self.helper.perror("Reg %s Read wrong" % str(log_reg1))
            self.helper.perror("Expect value should be %s" % str(hex(value_1)))

        cmd_info = log_reg2.read()
        print(cmd_info.value)
        if cmd_info.value != value_2:
            self.helper.perror("Reg %s Read wrong" % str(log_reg2))
            self.helper.perror("Expect value should be %s" % str(hex(value_2)))

    #check erase_log_buffer_x_0
    def check_erase_log_buffer_0(self,bm,reg_num,value_0):
        reg0 = 'ers_log_buf_'+reg_num+'_0_0'
        log_reg0 = bm.get_reg_by_name(reg0)
        cmd_og_addr = log_reg0.read()
        print(cmd_og_addr.value)
        if cmd_og_addr.value != value_0:
            self.helper.perror("Reg %s Read wrong" % str(log_reg0))
            self.helper.perror("Expect value should be %s" % str(hex(value_0)))

    #check erase_log_buffer_x_1
    def check_erase_log_buffer_1(self,bm,reg_num,value_1):
        reg1 = 'ers_log_buf_'+reg_num+'_1_0'
        log_reg1 = bm.get_reg_by_name(reg1)
        cmd_incr_addr = log_reg1.read()
        print(cmd_incr_addr.value)
        if cmd_incr_addr.value != value_1:
            self.helper.perror("Reg %s Read wrong" % str(log_reg1))
            self.helper.perror("Expect value should be %s" % str(hex(value_1)))

    #check erase_log_buffer_x_2
    def check_erase_log_buffer_2(self,bm,reg_num,value_2):
        reg2 = 'ers_log_buf_'+reg_num+'_2_0'
        log_reg2 = bm.get_reg_by_name(reg2)
        cmd_info = log_reg2.read()
        print(cmd_info.value)
        if cmd_info.value != value_2:
            self.helper.perror("Reg %s Read wrong" % str(log_reg2))
            self.helper.perror("Expect value should be %s" % str(hex(value_2)))

    #check erase_log_buffer_snap
    def check_erase_log_buffer_snap(self,bm,reg_num,value_0,value_1,value_2):
        reg0 = 'ers_log_buf_snap_'+reg_num+'_0_0'
        log_reg0 = bm.get_reg_by_name(reg0)
        reg1 = 'ers_log_buf_snap_'+reg_num+'_1_0'
        log_reg1 = bm.get_reg_by_name(reg1)
        reg2 = 'ers_log_buf_snap_'+reg_num+'_2_0'
        log_reg2 = bm.get_reg_by_name(reg2)

        cmd_og_addr = log_reg0.read()
        print(cmd_og_addr.value)
        if cmd_og_addr.value != value_0:
            self.helper.perror("Reg %s Read wrong" % str(log_reg0))
            self.helper.perror("Expect value should be %s" % str(hex(value_0)))

        cmd_incr_addr = log_reg1.read()
        print(cmd_incr_addr.value)
        if cmd_incr_addr.value != value_1:
            self.helper.perror("Reg %s Read wrong" % str(log_reg1))
            self.helper.perror("Expect value should be %s" % str(hex(value_1)))

        cmd_info = log_reg2.read()
        print(cmd_info.value)
        if cmd_info.value != value_2:
            self.helper.perror("Reg %s Read wrong" % str(log_reg2))
            self.helper.perror("Expect value should be %s" % str(hex(value_2)))

    #check erase_log_buffer_snap_0
    def check_erase_log_buffer_snap_0(self,bm,reg_num,value_0):
        reg0 = 'ers_log_buf_snap_'+reg_num+'_0_0'
        log_reg0 = bm.get_reg_by_name(reg0)
        cmd_og_addr = log_reg0.read()
        print(cmd_og_addr.value)
        if cmd_og_addr.value != value_0:
            self.helper.perror("Reg %s Read wrong" % str(log_reg0))
            self.helper.perror("Expect value should be %s" % str(hex(value_0)))

    #check erase_log_buffer_snap_1
    def check_erase_log_buffer_snap_1(self,bm,reg_num,value_1):
        reg1 = 'ers_log_buf_snap_'+reg_num+'_1_0'
        log_reg1 = bm.get_reg_by_name(reg1)
        cmd_incr_addr = log_reg1.read()
        print(cmd_incr_addr.value)
        if cmd_incr_addr.value != value_1:
            self.helper.perror("Reg %s Read wrong" % str(log_reg1))
            self.helper.perror("Expect value should be %s" % str(hex(value_1)))

    #check erase_log_buffer_snap_2
    def check_erase_log_buffer_snap_2(self,bm,reg_num,value_2):
        reg2 = 'ers_log_buf_snap_'+reg_num+'_2_0'
        log_reg2 = bm.get_reg_by_name(reg2)
        cmd_info = log_reg2.read()
        print(cmd_info.value)
        if cmd_info.value != value_2:
            self.helper.perror("Reg %s Read wrong" % str(log_reg2))
            self.helper.perror("Expect value should be %s" % str(hex(value_2)))

    def check_log_ptr(self,bm,golden_value):
        ptr_value = bm.log_ptr_0.read()
        print(ptr_value.value)
        if ptr_value.value != golden_value:
            self.helper.perror("Reg PTR Read wrong %s" % str(ptr_value))
            self.helper.perror("Expect value should be %s" % str(hex(golden_value)))           

    def check_ers_log_cnt(self,bm,golden_value):
        cnt = bm.erase_log_count_0.read()
        print(cnt.value)
        if cnt.value != golden_value:
            self.helper.perror("Reg ers_log_cnt Read wrong %s" % str(cnt))
            self.helper.perror("Expect value should be %s" % str(hex(golden_value)))  

    def check_ers_log_cnt_snap(self,bm,golden_value):
        cnt = bm.erase_count_snap_0.read()
        print(cnt.value)
        if cnt.value != golden_value:
            self.helper.perror("Reg ers_log_cnt_snap Read wrong %s" % str(cnt))
            self.helper.perror("Expect value should be %s" % str(hex(golden_value))) 

    def check_com_log_cnt(self,bm,golden_value):
        cnt = bm.common_log_count_0.read()
        print(cnt.value)
        if cnt.value != golden_value:
            self.helper.perror("Reg common_log_cnt Read wrong %s" % str(cnt))
            self.helper.perror("Expect value should be %s" % str(hex(golden_value)))

    def check_com_log_cnt_snap(self,bm,golden_value):
        cnt = bm.common_count_snap_0.read()
        print(cnt.value)
        if cnt.value != golden_value:
            self.helper.perror("Reg common_log_cnt_snap Read wrong %s" % str(cnt))
            self.helper.perror("Expect value should be %s" % str(hex(golden_value)))
    
    def check_dbg0(self,bm,golden_value):
        rd = bm.dbg_0_0.read()
        print(rd.value)
        if rd.value != golden_value:
            self.helper.perror("Reg DBG_0 Read wrong ")
            self.helper.perror("Expect value should be %s" % str(hex(golden_value)))

    def check_dbg1(self,bm,golden_value):
        rd = bm.dbg_1_0.read()
        print(rd.value)
        if rd.value != golden_value:
            self.helper.perror("Reg DBG_1 Read wrong ")
            self.helper.perror("Expect value should be %s" % str(hex(golden_value)))

    def check_dbg2(self,bm,golden_value):
        rd = bm.dbg_2_0.read()
        print(rd.value)
        if rd.value != golden_value:
            self.helper.perror("Reg DBG_2 Read wrong ")
            self.helper.perror("Expect value should be %s" % str(hex(golden_value)))

    def check_int_raw(self,bm,golden_value):
        rd = bm.int_raw_0.read()
        if rd.value != golden_value:
            self.helper.perror("Reg INT_RAW Read wrong ")
            self.helper.perror("Expect value should be %s" % str(hex(golden_value)))   

    def config_int_en(self,bm,log_err,recov_err,non_recov_err):
        bm.int_en_0.update(log_wo_err=log_err,recov_err=recov_err,non_recov_err=non_recov_err)

    def check_int_status(self,bm,golden_value):
        rd = bm.int_raw_0.read()
        print(rd.value)
        rd_1 = bm.int_status_0.read()
        print(rd_1.value)
        if rd_1.value != golden_value:
            self.helper.perror("Reg INT_STATUS is %s which mismatch with golden value" % str(hex(rd_1.value)))   
            self.helper.perror("Expect value should be %s" % str(hex(golden_value)))            
        if rd.value != rd_1.value:
            self.helper.perror("Reg INT_STATUS is %s mismatch with INT_RAW when INT_EN = 1" % str(hex(rd_1.value))) 
            self.helper.perror("Value of reg INT_RAW is %s" % str(hex(rd.value))) 
            
    def wait_write_done(self,flash_num):
        flash_n = str(flash_num)
        wip_path = 'ntb_top.qspi_flashes['+flash_n+'].u_macron_flash.WIP'
        while True:
            self.helper.wait_sim_time("us", 10)
            WIP_valid = self.helper.hdl_read(wip_path)
            if WIP_valid == 0:
                print("Sector Erase/Program done")
                break   

    def wait_socv_flash_write_done(self,flash_num):
        flash_n = str(flash_num)
        wip_path = 'ntb_top.qspi_flashes['+flash_n+'].u_micron_flash.MT25Q_die0.stat.SR[0]'
        while True:
            self.helper.wait_sim_time("us", 10)
            WIP_valid = self.helper.hdl_read(wip_path)
            if WIP_valid == 0:
                print("Sector Erase/Program done")
                break   
            
    def connect_to_micron_flash(self):
        self.helper.hdl_force("ntb_top.u_clk_rst_if.use_micron_flash", 1)

    def enable_vip_connection(self):
        self.helper.hdl_force("ntb_top.u_clk_rst_if.enable_qspi_vip",7)

    def config_bm_mode(self,bm,monitor_mode,flash_en,cs_swap,addr_mode):
        bm.bmon_cfg_0.update(mon_mode=monitor_mode,ap_flash_acc_en=flash_en,ap_flash_cs_sel=cs_swap,addr_mode_4b = addr_mode)
    
    def back_door_read_flash(self,flash_num,addr,golden_value):
        flash_n = str(flash_num)
        addr_start  = str(addr)
        addr_incr_1 = str(addr+1)
        addr_incr_2 = str(addr+2)
        addr_incr_3 = str(addr+3)
        path = 'ntb_top.qspi_flashes['+flash_n+'].u_macron_flash.mxArray['+addr_start+'][7:0]'   
        rd = self.helper.hdl_read(path)
        path_1 = 'ntb_top.qspi_flashes['+flash_n+'].u_macron_flash.mxArray['+addr_incr_1+'][7:0]'   
        rd_1 = self.helper.hdl_read(path_1)
        path_2 = 'ntb_top.qspi_flashes['+flash_n+'].u_macron_flash.mxArray['+addr_incr_2+'][7:0]'   
        rd_2 = self.helper.hdl_read(path_2)
        path_3 = 'ntb_top.qspi_flashes['+flash_n+'].u_macron_flash.mxArray['+addr_incr_3+'][7:0]'   
        rd_3 = self.helper.hdl_read(path_3)
        rd_final = rd + rd_1*16**2 + rd_2*16**4 + rd_3*16**6
        rdata_final = hex(rd_final)
        print(rdata_final)
        print(addr_start)
        if rd_final != golden_value:
            self.helper.perror("backdoor read wrong for addr %s" % str(addr))
    
    def change_frequency_bm(self,div):
        erot.CLOCK.NVEROT_CLOCK_IO_CTL.SW_QSPI1_CLK_RCM_CFG_0.update(DIV_SEL_DIV_SW=div)

    def gdma_transfer_rbi(self, src_addr, dst_addr, n_trans_words, is_posted=0):
        erot.FSP.GDMA_CHAN_COMMON_CONFIG_0.update(MEMQ=0, RR_WEIGHT=1)
        erot.FSP.GDMA_CHAN_SRC_ADDR_HI_0.update(VAL=src_addr>>32)
        erot.FSP.GDMA_CHAN_SRC_ADDR_0.update(VAL=(src_addr&0xffffffff))
        erot.FSP.GDMA_CHAN_DEST_ADDR_HI_0.update(VAL=dst_addr>>32)
        erot.FSP.GDMA_CHAN_DEST_ADDR_0.update(VAL=(dst_addr&0xffffffff))
        erot.FSP.GDMA_CHAN_TRANS_CONFIG0_0.update(LENGTH=n_trans_words, SUBCHAN=0, COMPLETE_IRQEN=0)
        erot.FSP.GDMA_CHAN_TRANS_CONFIG1_0.update(SRC_ADDR_MODE="INC")
        erot.FSP.GDMA_CHAN_TRANS_CONFIG1_0.update(DEST_ADDR_MODE="INC")
        erot.FSP.GDMA_CHAN_TRANS_CONFIG1_0.update(DEST_POSTED=is_posted)
        # trigger
        erot.FSP.GDMA_CHAN_TRANS_CONFIG0_0.update(LAUNCH=1)
        start_time = self.helper.get_sim_time()
        print(start_time)
        erot.FSP.GDMA_CHAN_STATUS_0.poll(BUSY=0)
        end_time = self.helper.get_sim_time()
        print(end_time)
        time_1 = float(start_time[0:-2])
        time_2 = float(end_time[0:-2])
        time_scale = time_2 - time_1
        trans_word = n_trans_words / 256
        trans_byte = (n_trans_words + 1)/256
        bandwidth =  trans_word * (10**6) / time_scale
        print("performace for %sKB RBI read is %sMB/S" % (str(int(trans_byte)) ,str(int(bandwidth))) )

    def fsp_burst_read_rbi(self, src_addr, n_words, is_posted=0):
        """"
        FSP priv burst read in address increment mode
        src_addr: 32-bit aligned source address in absolute address map to incrementally read from, 
                  i.e. must take AMAP offset on chip into account
        n_words: number of 32-bit data to read
        is_posted: if in post mode, i.e. if wait for priv ack
        """
        # prepare space to store read data in dmem
        dmem_end_addr = 0x00200000
        dst_addr = dmem_end_addr - 4*n_words
        self.gdma_transfer_rbi(src_addr, dst_addr, n_words, is_posted)

        ans = []
        for i in range(n_words):
            sw_addr = dst_addr + 4*i
            tval = self.helper.read_lmem(sw_addr)
            self.helper.pdebug(f"read {hex(tval)} @ {hex(sw_addr)}")
            ans += [tval]

        return ans