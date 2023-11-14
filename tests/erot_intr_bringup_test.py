#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import * 
from driver.components.spi_mst import SPI_SCLK_FREQ_SEL

with Test(sys.argv) as t:
    
    def parse_args():
        t.parser.add_argument("--engine", action='store', help="Check the interrupt transfer path", default='FSP')
        opts, unknown = t.parser.parse_known_args(sys.argv[1:])
        return opts

    OOBHUB_IP_LIST = [
#        {'name' : 'UART',            'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_sbsa_uart.sbsa_uart_intr',       'read_value' : 0x2000},
#        {'name' : 'I2C_IO_Expander', 'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_i2c_io_expander.i2c_rupt',          'read_value' : 0x4000},
#        {'name' : 'SPI_OOBHUB',      'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_oobhub_spi.intr',                   'read_value' : 0x8000},
        {'name' : 'GPIO_CRTL0',      'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_GPIO_ctl0.gpioctl0_rupt[0]',     'read_value' : 0x10000},
#        {'name' : 'GPIO_CRTL1',      'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_GPIO_ctl0.gpioctl0_rupt[1]',     'read_value' : 0x20000},
#        {'name' : 'GPIO_CRTL2',      'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_GPIO_ctl0.gpioctl0_rupt[2]',     'read_value' : 0x40000},
#        {'name' : 'GPIO_CRTL3',      'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_GPIO_ctl0.gpioctl0_rupt[3]',     'read_value' : 0x80000},
#        {'name' : 'GPIO_CRTL4',      'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_GPIO_ctl0.gpioctl0_rupt[4]',     'read_value' : 0x100000},
#        {'name' : 'GPIO_CRTL5',      'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_GPIO_ctl0.gpioctl0_rupt[5]',     'read_value' : 0x200000},
#        {'name' : 'GPIO_CRTL6',      'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_GPIO_ctl0.gpioctl0_rupt[6]',     'read_value' : 0x400000},
#        {'name' : 'GPIO_CRTL7',      'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_GPIO_ctl0.gpioctl0_rupt[7]',     'read_value' : 0x800000},
#        {'name' : 'SPI_AP0',         'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_spi_ib0.intr',                      'read_value' : 0x1000000},
#        {'name' : 'I2C_AP0',         'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_i2c_ib0.i2c_rupt',                  'read_value' : 0x2000000},
#        {'name' : 'I3C_AP0',         'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_i3c_ib0.ic_intr',                   'read_value' : 0x4000000},
#        {'name' : 'SPI_AP1',         'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_spi_ib1.intr',                      'read_value' : 0x10000000},
#        {'name' : 'I2C_AP1',         'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_i2c_ib1.i2c_rupt',                  'read_value' : 0x20000000},
#        {'name' : 'I3C_AP1',         'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_i3c_ib1.ic_intr',                   'read_value' : 0x40000000},
    ]
    FSP_IP_LIST = [
    #    {'name' : 'OOBHUB',          'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_oobhub.oobhub2sys_intr',                    'read_value' : 0x1000000},
    #    {'name' : 'THERM',           'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fsi_therm.therm2bpmp_intr',                 'read_value' : 0x2000000},
    #    {'name' : 'MRAM',            'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.nverot_mwrap_interrupt',       'read_value' : 0x4000000},
    #    {'name' : 'QSPI_NVM',        'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_boot_qspi.intr',                               'read_value' : 0x8000000},
        {'name' : 'SPIMON_AP0',      'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_bypmon0.nverot_bypmon_interrupt',    'read_value' : 0x10000000},
    #    {'name' : 'QSPI_AP0',        'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_qspi0.intr',                                   'read_value' : 0x20000000},
    #    {'name' : 'SPIMON_AP1',      'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_bypmon1.nverot_bypmon_interrupt',    'read_value' : 0x40000000},
    #    {'name' : 'QSPI_AP1',        'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_qspi1.intr',                                   'read_value' : 0x80000000},
    ]

    def enable_bypass_monitor(bm):
        bm.int_en_0.update(recov_err=1)
        bm.bmon_cfg_0.update(mon_mode=2,ap_flash_acc_en=1)

    def config_bm_filter(bm):
        bm.mem_permission_0.update(region_0=1)

        #read_only for addr(0x0-0x20_0000)
        bm.reg0_start_address_0.write(0x0)
        bm.reg0_end_address_0.write(0x200)

        bm.flash_cfg_0.update(dummy_cyc=8)
        #write enable
        bm.cmd_filter_cmd_0_0.update(dis_cmd=0,cmd_type=0,addr_phase=0,data_io_mode=0,cs_term=1,dum_cyc_en=0,instr_4b=0,cmd_log=0,instr_code=0x06,valid=1)
        #1-1-1 write opcode, illegal rcv 
        bm.cmd_filter_cmd_1_0.update(dis_cmd=3,cmd_type=2,addr_phase=1,data_io_mode=1,cs_term=1,dum_cyc_en=0,instr_4b=0,cmd_log=3,instr_code=0x02,valid=1)
        #1-1-1 read opcode 
        bm.cmd_filter_cmd_2_0.update(dis_cmd=2,cmd_type=1,addr_phase=1,data_io_mode=1,cs_term=0,dum_cyc_en=1,instr_4b=0,cmd_log=3,instr_code=0x0b,valid=1) 
        #1-0-1 read config 
        bm.cmd_filter_cmd_3_0.update(dis_cmd=0,cmd_type=1,addr_phase=0,data_io_mode=1,cs_term=0,dum_cyc_en=0,instr_4b=0,cmd_log=0,instr_code=0x05,valid=1) 
        #1-1-0 erase block
        bm.cmd_filter_cmd_4_0.update(dis_cmd=2,cmd_type=3,addr_phase=1,data_io_mode=0,cs_term=0,dum_cyc_en=0,instr_4b=0,cmd_log=2,instr_code=0x20,valid=1) 
        #1-0-1 read flash config 
        bm.cmd_filter_cmd_5_0.update(dis_cmd=0,cmd_type=1,addr_phase=0,data_io_mode=1,cs_term=0,dum_cyc_en=0,instr_4b=0,cmd_log=0,instr_code=0x70,valid=1) 
        #1-0-1 read ID
        bm.cmd_filter_cmd_11_0.update(dis_cmd=0,cmd_type=1,addr_phase=0,data_io_mode=1,cs_term=0,dum_cyc_en=0,instr_4b=0,cmd_log=0,instr_code=0x9e,valid=1)
                  
    def ini_bm(monitor):
        config_bm_filter(monitor)
        enable_bypass_monitor(monitor)
        # simulation need to change the frequency, however fpga does not need
        if helper.target in ["simv_fpga"]:
            helper.spi_set_sclk_frequency(spi_port=0, freq_sel=SPI_SCLK_FREQ_SEL.SPI_SCLK_10MHZ)

    def validate_ap_access_flash(ap_id,bm_cs,monitor):
        ########################################################################
        ################################# MISC #################################
        ########################################################################
        LOG(f"##################################################################")
        LOG(f"############################ MISC ################################")
        LOG(f"##################################################################")
        #Enable VIP to send legal rd: read ID
        #1-0-1 read
        read_id = helper.spi_read(spi_port=ap_id, cs_id=bm_cs, 
                  n_instruction_lane=1, n_instruction_bits=8, instruction=[0x9e],
                  n_address_lane=1, n_address_bits=0, address=[], 
                  n_data_lane=1, nbr_rd_bytes=1)
        read_id_value = int.from_bytes(read_id, "big")
        LOG(f"1-0-1 read ID from Flash: {hex(read_id_value)}")


        ########################################################################
        ####################### 1-1-1 ILLEGAL WR (RCV) #########################
        ########################################################################
        LOG(f"##################################################################")
        LOG(f"#################### 1-1-1 ILLEGAL WR (RCV) ######################")
        LOG(f"##################################################################")
        #Enable VIP to send legal cfg: write enable 
        #1-0-0 config
        helper.spi_write(spi_port=ap_id, cs_id=bm_cs, 
                         n_instruction_lane=1, n_instruction_bits=0, instruction=[],
                         n_address_lane=1, n_address_bits=0, address=[], 
                         n_data_lane=1, data=[0x06])     
        LOG(f"legal 1-0-0 write enable to Flash")

        #Enable VIP to send illegal memory wr: 0x01_2300 - 0x01_2307(8 byte)
        #1-1-1 write
        helper.spi_write(spi_port=ap_id, cs_id=bm_cs, 
                         n_instruction_lane=1, n_instruction_bits=8, instruction=[0x02],
                         n_address_lane=1, n_address_bits=24, address=[0x01,0x23,0x00], 
                         n_data_lane=1, data=list(0xf1e2d3c4f2e3d4c5.to_bytes(8,"big")))
        LOG(f"1-1-1 write data to illegal Flash address 0x012300 - 0x012307: {hex(0xf1e2d3c4f2e3d4c5)}")
        LOG(f"----- BYP_MON enter RCV state -----")
        LOG(f"BYP_MON trigger interrupt")
        LOG(f"----- BYP_MON exit RCV state -----")

        
    def validate_ap_socv(qspi,monitor,ap,cs):
        ini_bm(monitor)
        helper.wait_sim_time("us", 15)    
        validate_ap_access_flash(ap,cs,monitor)

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

    def bypmon_trig_intr():
        deassert_sw_reset_l1()
        deassert_sw_reset_l3()
        test_api.qspi0_init()
        test_api.connect_to_micron_flash()
        test_api.enable_vip_connection()
        helper.wait_sim_time("us", 5)
        validate_ap_socv(erot.QSPI0.QSPI,erot.SPI_MON0,0,0)

    bidir_pad_reg = [['PADCTRL_E','AP0_BOOT_CTRL_0_N_GP01_0'], ['PADCTRL_E','AP0_BOOT_CTRL_1_N_GP02_0'], ['PADCTRL_E','EROT_REQ_AP0_N_GP03_0'], ['PADCTRL_E','EROT_GNT_AP0_N_GP04_0'], ['PADCTRL_E','AP0_FW_INTR_N_GP05_0'], ['PADCTRL_E','AP0_MUX_CTRL_N_GP06_0'], ['PADCTRL_E','AP0_PGOOD_GP07_0'], ['PADCTRL_E','AP0_RESET_N_GP08_0'], ['PADCTRL_E','AP0_RESET_IND_N_GP09_0'], ['PADCTRL_E','AP0_RESET_MON_N_GP10_0'], ['PADCTRL_E','AP0_SPI_PWR_KILL_GP11_0'],['PADCTRL_W','AP1_BOOT_CTRL_0_N_GP12_0'],['PADCTRL_W','AP1_BOOT_CTRL_1_N_GP13_0'], ['PADCTRL_W','EROT_REQ_AP1_N_GP14_0'], ['PADCTRL_W','EROT_GNT_AP1_N_GP15_0'], ['PADCTRL_W','AP1_FW_INTR_N_GP16_0'], ['PADCTRL_W','AP1_MUX_CTRL_N_GP17_0'], ['PADCTRL_W','AP1_PGOOD_GP18_0'], ['PADCTRL_W','AP1_RESET_N_GP19_0'], ['PADCTRL_W','AP1_RESET_IND_N_GP20_0'], ['PADCTRL_W','AP1_RESET_MON_N_GP21_0'], ['PADCTRL_W','AP1_SPI_PWR_KILL_GP22_0'], ['PADCTRL_S','EROT_LED_GP23_0'], ['PADCTRL_S','MISC_I2C_SCL_GP24_0'],['PADCTRL_S','MISC_I2C_SDA_GP25_0'], ['PADCTRL_S','OBS0_GP26_0'], ['PADCTRL_S','OBS1_GP27_0'], ['PADCTRL_S','HW_STRAP_GP28_0'], ['PADCTRL_N','BOOT_QSPI_IO3_GP29_0']]
    #bidir_pad_reg = [['PADCTRL_E','AP0_FW_INTR_N_GP05_0']]

    bidir_port_enable = ['A_ENABLE_CONFIG_00_0','A_ENABLE_CONFIG_01_0','A_ENABLE_CONFIG_02_0','A_ENABLE_CONFIG_03_0','A_ENABLE_CONFIG_04_0','A_ENABLE_CONFIG_05_0','A_ENABLE_CONFIG_06_0','B_ENABLE_CONFIG_00_0','B_ENABLE_CONFIG_01_0','B_ENABLE_CONFIG_02_0','B_ENABLE_CONFIG_03_0','C_ENABLE_CONFIG_00_0','C_ENABLE_CONFIG_01_0','C_ENABLE_CONFIG_02_0','C_ENABLE_CONFIG_03_0','C_ENABLE_CONFIG_04_0','C_ENABLE_CONFIG_05_0','C_ENABLE_CONFIG_06_0','D_ENABLE_CONFIG_00_0','D_ENABLE_CONFIG_01_0','D_ENABLE_CONFIG_02_0','D_ENABLE_CONFIG_03_0','E_ENABLE_CONFIG_01_0','E_ENABLE_CONFIG_03_0','E_ENABLE_CONFIG_04_0','E_ENABLE_CONFIG_05_0','E_ENABLE_CONFIG_06_0','E_ENABLE_CONFIG_07_0','F_ENABLE_CONFIG_00_0']
    #bidir_port_enable = ['A_ENABLE_CONFIG_04_0']

    intr_c = ['A_INTERRUPT_CLEAR_00_0','A_INTERRUPT_CLEAR_01_0','A_INTERRUPT_CLEAR_02_0','A_INTERRUPT_CLEAR_03_0','A_INTERRUPT_CLEAR_04_0','A_INTERRUPT_CLEAR_05_0','A_INTERRUPT_CLEAR_06_0','B_INTERRUPT_CLEAR_00_0','B_INTERRUPT_CLEAR_01_0','B_INTERRUPT_CLEAR_02_0','B_INTERRUPT_CLEAR_03_0','C_INTERRUPT_CLEAR_00_0','C_INTERRUPT_CLEAR_01_0','C_INTERRUPT_CLEAR_02_0','C_INTERRUPT_CLEAR_03_0','C_INTERRUPT_CLEAR_04_0','C_INTERRUPT_CLEAR_05_0','C_INTERRUPT_CLEAR_06_0','D_INTERRUPT_CLEAR_00_0','D_INTERRUPT_CLEAR_01_0','D_INTERRUPT_CLEAR_02_0','D_INTERRUPT_CLEAR_03_0','E_INTERRUPT_CLEAR_01_0','E_INTERRUPT_CLEAR_03_0','E_INTERRUPT_CLEAR_04_0','E_INTERRUPT_CLEAR_05_0','E_INTERRUPT_CLEAR_06_0','E_INTERRUPT_CLEAR_07_0','F_INTERRUPT_CLEAR_00_0']
    #intr_c = ['A_INTERRUPT_CLEAR_04_0']

    vm = ['A_VM_00_0','A_VM_01_0','A_VM_02_0','A_VM_03_0','A_VM_04_0','A_VM_05_0','A_VM_06_0','B_VM_00_0','B_VM_01_0','B_VM_02_0','B_VM_03_0','C_VM_00_0','C_VM_01_0','C_VM_02_0','C_VM_03_0','C_VM_04_0','C_VM_05_0','C_VM_06_0','D_VM_00_0','D_VM_01_0','D_VM_02_0','D_VM_03_0','E_VM_01_0','E_VM_03_0','E_VM_04_0','E_VM_05_0','E_VM_06_0','E_VM_07_0','F_VM_00_0']
    #vm = ['A_VM_04_0']
    
    bidir_hack_path = ['gpio1_reg','gpio2_reg','gpio3_reg','gpio4_reg','gpio5_reg','gpio6_reg','gpio7_reg','gpio8_reg','gpio9_reg','gpio10_reg','gpio11_reg','gpio12_reg','gpio13_reg','gpio14_reg','gpio15_reg','gpio16_reg','gpio17_reg','gpio18_reg','gpio19_reg','gpio20_reg','gpio21_reg','gpio22_reg','gpio23_reg','gpio24_reg','gpio25_reg','gpio26_reg','gpio27_reg','gpio28_reg','gpio29_reg','gpio30_reg']
    
    route = ['A_INT0_ROUTE_MAPPING_0','A_INT1_ROUTE_MAPPING_0','A_INT2_ROUTE_MAPPING_0','A_INT3_ROUTE_MAPPING_0','A_INT4_ROUTE_MAPPING_0','A_INT5_ROUTE_MAPPING_0','A_INT6_ROUTE_MAPPING_0','A_INT7_ROUTE_MAPPING_0','B_INT0_ROUTE_MAPPING_0','B_INT1_ROUTE_MAPPING_0','B_INT2_ROUTE_MAPPING_0','B_INT3_ROUTE_MAPPING_0','B_INT4_ROUTE_MAPPING_0','B_INT5_ROUTE_MAPPING_0','B_INT6_ROUTE_MAPPING_0','B_INT7_ROUTE_MAPPING_0','C_INT0_ROUTE_MAPPING_0','C_INT1_ROUTE_MAPPING_0','C_INT2_ROUTE_MAPPING_0','C_INT3_ROUTE_MAPPING_0','C_INT4_ROUTE_MAPPING_0','C_INT5_ROUTE_MAPPING_0','C_INT6_ROUTE_MAPPING_0','C_INT7_ROUTE_MAPPING_0','D_INT0_ROUTE_MAPPING_0','D_INT1_ROUTE_MAPPING_0','D_INT2_ROUTE_MAPPING_0','D_INT3_ROUTE_MAPPING_0','D_INT4_ROUTE_MAPPING_0','D_INT5_ROUTE_MAPPING_0','D_INT6_ROUTE_MAPPING_0','D_INT7_ROUTE_MAPPING_0','E_INT0_ROUTE_MAPPING_0','E_INT1_ROUTE_MAPPING_0','E_INT2_ROUTE_MAPPING_0','E_INT3_ROUTE_MAPPING_0','E_INT4_ROUTE_MAPPING_0','E_INT5_ROUTE_MAPPING_0','E_INT6_ROUTE_MAPPING_0','E_INT7_ROUTE_MAPPING_0','F_INT0_ROUTE_MAPPING_0','F_INT1_ROUTE_MAPPING_0','F_INT2_ROUTE_MAPPING_0','F_INT3_ROUTE_MAPPING_0','F_INT4_ROUTE_MAPPING_0','F_INT5_ROUTE_MAPPING_0','F_INT6_ROUTE_MAPPING_0','F_INT7_ROUTE_MAPPING_0']
    def clear_intr(reg):
        if (reg == 'A_INTERRUPT_CLEAR_04_0'):
            gpio_reg = erot.GPIO.get_reg_by_name(reg)
            gpio_reg.update(GPIO_INTERRUPT_CLEAR=1)

    def config_intr_enable(reg):
        if (reg == 'A_ENABLE_CONFIG_04_0'):
            gpio_reg = erot.GPIO.get_reg_by_name(reg)
            gpio_reg.update(GPIO_ENABLE=1, IN_OUT=0, TRIGGER_TYPE=2, TRIGGER_LEVEL=1, INTERRUPT_FUNCTION=1)

    def set_pad_input(reg_pair):
        if (reg_pair[1] == "AP0_FW_INTR_N_GP05_0"):
            pos_reg = erot.get_reg_by_name(reg_pair[0])
            pad_reg = pos_reg.get_reg_by_name(reg_pair[1])
            pad_reg.update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)
            pad_reg.poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=1)

    def pin_group(idx):
        reg = vm[idx]
        #A_VM_01_0
        if reg[0] == 'A':
            group = 0
        if reg[0] == 'B':
            group = 1
        if reg[0] == 'C':
            group = 2
        if reg[0] == 'D':
            group = 3
        if reg[0] == 'E':
            group = 4
        if reg[0] == 'F':
            group = 5
        return group
    
    def pin_idx(idx):
        reg = vm[idx]
        return int(reg[6])
    
    def set_vm(reg, des):
        if (reg == 'A_VM_04_0'):
            gpio_reg = erot.GPIO.get_reg_by_name(reg)
            gpio_reg.update(VM1=((des>>0)&0x01)*0x03,VM2=((des>>1)&0x01)*0x03,VM3=((des>>2)&0x01)*0x03,VM4=((des>>3)&0x01)*0x03,VM5=((des>>4)&0x01)*0x03,VM6=((des>>5)&0x01)*0x03,VM7=((des>>6)&0x01)*0x03,VM8=((des>>7)&0x01)*0x03)
            rd = gpio_reg.read()
            helper.log("Reg is %s" % str(rd))
    
#    def test_deposit(val):
#        #helper.gpio_write('ap0_fw_intr_n_gp05',val)
#        reg_num = len(bidir_port_enable)
#        path_head_wr = 'ntb_top.'
#        for onehot_loop in range(0, reg_num):
#            path = path_head_wr + bidir_hack_path[onehot_loop]
#            helper.hdl_deposit(path,val)
#            helper.wait_sim_time("ns", 1000)

    def set_route(reg, val):
        gpio_reg = erot.GPIO.get_reg_by_name(reg)
        gpio_reg.update(VAL=(0x1<<val))#onehot

    def gpio0_trig_intr():
        reg_num = len(bidir_port_enable)
        #? it seems not support the JTAG or HEAD platform, it is needed? 

        #helper.set_gpio_test(1)
        #test_api.oobhub_icd_init()

        helper.log("start set pad input")
        for port in range(0, reg_num):
            set_pad_input(bidir_pad_reg[port])

        helper.log("start gpio write ap0_fw_intr_n_gp05 to 0")
        helper.gpio_write('ap0_fw_intr_n_gp05',0)
        helper.log("after gpio write ap0_fw_intr_n_gp05, wait for 1 ms")
        helper.wait_rpi_time(1, 1) # wait 1000 us

        helper.log("start config intr enable")
        for port in range(0, reg_num):
            config_intr_enable(bidir_port_enable[port])

        helper.log("start clear intr enable")
        for port in range(0, reg_num):
            clear_intr(intr_c[port])
        
        helper.log("start set vm")
        vm_code = 0xc3
        for port in range(0, reg_num):
            set_vm(vm[port], vm_code)
        

        
        onehot_loop = 4
        group = pin_group(onehot_loop)
        idx = pin_idx(onehot_loop)

        #mapping = group*8+intr_out
        mapping = group*8+0

        set_route(route[mapping], idx)

        helper.log("SAtarting to make ap0_fw_intr_n_gp05 to 1")
        helper.gpio_write('ap0_fw_intr_n_gp05',1)
        #path_head_wr = 'ntb_top.'
        #path = path_head_wr + bidir_hack_path[onehot_loop]
        #helper.hdl_deposit(path,1)
        #helper.wait_sim_time("ns", 1000)
        helper.wait_rpi_time(1, 1) # wait 1000 us
        helper.log("end of ap0_fw_intr_n_gp05")

        #        for intr_loop in range(0,8):
        #            if(intr_loop == intr_out):
        #                check_intr_wire(intr_loop, 1)
        #            else:
        #                check_intr_wire(intr_loop, 0)


    def checking_interrupt(ip_list, reg):
        #assert interrupt -> read status regs -> de-assert --> read again
        for ip in ip_list:
            helper.log("Checking ip %s" % (ip['name']))
            if helper.target in ["fpga", "simv_fpga"]:
                if (options.engine == 'FSP'):
                    reg.poll(timeout=5, EXT=0)
                elif (options.engine == 'OOBHUB'):
                    reg.poll(timeout=5, EXT=0x2000000) # I2C_AP0 will have interrupt in fpga env
                   # reg.poll(timeout=5, EXT=0x0)
                 #   erot.FSP.RISCV_EXTIRQSTAT_0.poll(timeout=5, EXT=0x1000000) # FSP poll try
                else:
                    helper.perror("no engine %s" % (options.engine))

                helper.log("%s interrupt de-asserted and detected" % (ip['name']))
                
                if(ip['name'] == "SPIMON_AP0"):
                    bypmon_trig_intr()
                    helper.log("bypass monitor triggers the interrupt")
                elif(ip['name'] == "GPIO_CRTL0"):
                    gpio0_trig_intr()
                    helper.log("gpio0 triggers the interrupt")
                else:
                    helper.perror("%s cannot do the interrupt action in FPGA env" % (ip['name']))
                
                if (options.engine == 'FSP'):
                    reg.poll(timeout=10, EXT=ip['read_value'])
                elif (options.engine == 'OOBHUB'):
                    helper.log("OOBHUB interrupt register detect")
                    final_EXT = 0x2000000 + ip['read_value'] # add the I2C_AP0 interrupt value
                    reg.poll(timeout=5, EXT=final_EXT)
                    #reg.poll(timeout=5, EXT=ip['read_value'])
                  #  helper.log("FSP interrupt register detect")
                  #  erot.FSP.RISCV_EXTIRQSTAT_0.poll(EXT=0x1000000) #OOBHUB interface to FSP
                else:
                    helper.perror("no engine %s" % (options.engine))
                #reg.poll(timeout=20, EXT=ip['read_value'])
                #
                ## also check the FSP corresponding register value when OOBHUB has the interrupt

         #       #helper.log("%s interrupt asserted and detected" % (ip['name']))
            else:
                helper.hdl_force(ip['intr_force_path'],1)
                reg.poll(EXT=ip['read_value'])
                print(ip['name'] + " interrupt asserted and detected")
                helper.hdl_force(ip['intr_force_path'],0)
                reg.poll(EXT=0)
                print(ip['name'] + " interrupt de-asserted and detected")

    options = parse_args()
    #programming configuration regs
    if helper.target in ["fpga", "simv_fpga"]:
        helper.log("Programming START")
        if (options.engine == 'FSP'):
            erot.FSP.RISCV_EXTIRQMODE_0.write(0xffffffff)
            erot.FSP.RISCV_EXTIRQMSET_0.write(0xffffffff)
            erot.FSP.RISCV_EXTIRQMODE_0.poll(LVL_EXT=0xffffffff)
            erot.FSP.RISCV_EXTIRQMASK_0.poll(EXT=0xffffffff)
        elif(options.engine == 'OOBHUB'):
            #make sure l3 reset is released
            erot.RESET.NVEROT_RESET_CFG.SW_L3_RST_0.poll(timeout=10, RESET_LEVEL3=1)
            #reset gpio 
            erot.RESET.NVEROT_RESET_CFG.SW_GPIO_CTRL_RST_0.update(RESET_GPIO_CTRL=1)
            erot.OOBHUB.PEREGRINE_RISCV_EXTIRQMODE_0.write(0xffffffff) #level-base interrupt
           # erot.OOBHUB.PEREGRINE_RISCV_EXTIRQMSET_0.write(0xffdfffff) #mask set to all 1 besides the I2C AP0 interrupt
            erot.OOBHUB.PEREGRINE_RISCV_EXTIRQMSET_0.write(0x0) #mask set to all 1 besides the I2C AP0 interrupt
       #     erot.OOBHUB.PEREGRINE_RISCV_EXTIRQDEST_0.write(0xffffffff) #set interrupt destination to FSP
       #     erot.FSP.RISCV_EXTIRQMODE_0.write(0xffffffff)
       #     erot.FSP.RISCV_EXTIRQMSET_0.write(0xffffffff)
            erot.OOBHUB.PEREGRINE_RISCV_EXTIRQMODE_0.poll(LVL_EXT=0xffffffff)
            erot.OOBHUB.PEREGRINE_RISCV_EXTIRQMASK_0.poll(EXT=0x0)
            #erot.OOBHUB.PEREGRINE_RISCV_EXTIRQMASK_0.poll(EXT=0xffdfffff)
       #     erot.OOBHUB.PEREGRINE_RISCV_EXTIRQDEST_0.poll(0xffffffff)
       #     erot.FSP.RISCV_EXTIRQMODE_0.poll(LVL_EXT=0xffffffff)
       #     erot.FSP.RISCV_EXTIRQMASK_0.poll(EXT=0xffffffff)
        else:
            helper.perror("no engine %s" % (options.engine))
        helper.log("Programming DONE")
        
        helper.log("Starting to check the interrupt.")
        if (options.engine == 'FSP'):
            checking_interrupt(FSP_IP_LIST, erot.FSP.RISCV_EXTIRQSTAT_0)
        elif(options.engine == 'OOBHUB'):
            checking_interrupt(OOBHUB_IP_LIST, erot.OOBHUB.PEREGRINE_RISCV_EXTIRQSTAT_0)
        else:
            helper.perror("no engine %s" % (options.engine))
    else:
        helper.log("Programming START")
        erot.OOBHUB.PEREGRINE_RISCV_EXTIRQMODE_0.write(0xffffffff) #level-base interrupt
        erot.OOBHUB.PEREGRINE_RISCV_EXTIRQMSET_0.write(0xffffffff) #mask set to all 1
        erot.FSP.RISCV_EXTIRQMODE_0.write(0xffffffff)
        erot.FSP.RISCV_EXTIRQMSET_0.write(0xffffffff)
        helper.log("Programming DONE")
        erot.OOBHUB.PEREGRINE_RISCV_EXTIRQMODE_0.poll(LVL_EXT=0xffffffff)
        erot.OOBHUB.PEREGRINE_RISCV_EXTIRQMASK_0.poll(EXT=0xffffffff)
        erot.FSP.RISCV_EXTIRQMODE_0.poll(LVL_EXT=0xffffffff)
        erot.FSP.RISCV_EXTIRQMASK_0.poll(EXT=0xffffffff)

        helper.log("Starting to check the interrupt.")
        checking_interrupt(OOBHUB_IP_LIST, erot.OOBHUB.PEREGRINE_RISCV_EXTIRQSTAT_0)
        checking_interrupt(FSP_IP_LIST, erot.FSP.RISCV_EXTIRQSTAT_0)
