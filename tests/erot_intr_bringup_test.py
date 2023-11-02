#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import * 

with Test(sys.argv) as t:

    OOBHUB_IP_LIST = [
        {'name' : 'UART',            'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_sbsa_uart.sbsa_uart_intr',       'read_value' : 0x2000},
        {'name' : 'I2C_IO_Expander', 'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_i2c_io_expander.i2c_rupt',          'read_value' : 0x4000},
        {'name' : 'SPI_OOBHUB',      'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_oobhub_spi.intr',                   'read_value' : 0x8000},
        {'name' : 'GPIO_CRTL0',      'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_GPIO_ctl0.gpioctl0_rupt[0]',     'read_value' : 0x10000},
        {'name' : 'GPIO_CRTL1',      'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_GPIO_ctl0.gpioctl0_rupt[1]',     'read_value' : 0x20000},
        {'name' : 'GPIO_CRTL2',      'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_GPIO_ctl0.gpioctl0_rupt[2]',     'read_value' : 0x40000},
        {'name' : 'GPIO_CRTL3',      'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_GPIO_ctl0.gpioctl0_rupt[3]',     'read_value' : 0x80000},
        {'name' : 'GPIO_CRTL4',      'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_GPIO_ctl0.gpioctl0_rupt[4]',     'read_value' : 0x100000},
        {'name' : 'GPIO_CRTL5',      'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_GPIO_ctl0.gpioctl0_rupt[5]',     'read_value' : 0x200000},
        {'name' : 'GPIO_CRTL6',      'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_GPIO_ctl0.gpioctl0_rupt[6]',     'read_value' : 0x400000},
        {'name' : 'GPIO_CRTL7',      'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_GPIO_ctl0.gpioctl0_rupt[7]',     'read_value' : 0x800000},
        {'name' : 'SPI_AP0',         'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_spi_ib0.intr',                      'read_value' : 0x1000000},
        {'name' : 'I2C_AP0',         'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_i2c_ib0.i2c_rupt',                  'read_value' : 0x2000000},
        {'name' : 'I3C_AP0',         'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_i3c_ib0.ic_intr',                   'read_value' : 0x4000000},
        {'name' : 'SPI_AP1',         'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_spi_ib1.intr',                      'read_value' : 0x10000000},
        {'name' : 'I2C_AP1',         'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_i2c_ib1.i2c_rupt',                  'read_value' : 0x20000000},
        {'name' : 'I3C_AP1',         'intr_force_path' : 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_i3c_ib1.ic_intr',                   'read_value' : 0x40000000},
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

    def checking_interrupt(ip_list, reg):
        #assert interrupt -> read status regs -> de-assert --> read again
        for ip in ip_list:
            if helper.target in ["fpga", "simv_fpga"]:
                reg.poll(timeout=10, EXT=0)
                helper.log("%s interrupt de-asserted and detected" % (ip['name']))
                if(ip['name'] == "SPIMON_AP0"):
                    bypmon_trig_intr()
                    helper.log("bypass monitor triggers the interrupt")
                else:
                    helper.perror("%s cannot do the interrupt action in FPGA env" % (ip['name']))
                reg.poll(timeout=20, EXT=ip['read_value'])
                helper.log("%s interrupt asserted and detected" % (ip['name']))
            else:
                helper.hdl_force(ip['intr_force_path'],1)
                reg.poll(EXT=ip['read_value'])
                print(ip['name'] + " interrupt asserted and detected")
                helper.hdl_force(ip['intr_force_path'],0)
                reg.poll(EXT=0)
                print(ip['name'] + " interrupt de-asserted and detected")

    #programming configuration regs
    if helper.target in ["fpga", "simv_fpga"]:
#        #jtag unlock
#        helper.log("Test start")
#        helper.wait_sim_time("us", 50)
#        helper.hdl_force('ntb_top.u_nv_fpga_dut.u_nv_top_fpga.u_nv_top_wrapper.u_nv_top.nvjtag_sel', 1)
#
#        helper.jtag.Reset(0)
#        helper.jtag.DRScan(100, hex(0x0)) #add some delay as jtag only work when nvjtag_sel stable in real case
#        helper.jtag.Reset(1)
#
#
#        helper.pinfo(f'j2h_unlock sequence start')
#        helper.j2h_unlock()
#        helper.pinfo(f'j2h_unlock sequence finish')
#
#
#        helper.jtag.DRScan(100, hex(0x0)) #add some delay as jtag only work when nvjtag_sel stable in real case

        helper.log("Programming START")
    #    erot.OOBHUB.PEREGRINE_RISCV_EXTIRQMODE_0.write(0xffffffff) #level-base interrupt
    #    erot.OOBHUB.PEREGRINE_RISCV_EXTIRQMSET_0.write(0xffffffff) #mask set to all 1
        erot.FSP.RISCV_EXTIRQMODE_0.write(0xffffffff)
        erot.FSP.RISCV_EXTIRQMSET_0.write(0xffffffff)
        helper.log("Programming DONE")
    #    erot.OOBHUB.PEREGRINE_RISCV_EXTIRQMODE_0.poll(LVL_EXT=0xffffffff)
    #    erot.OOBHUB.PEREGRINE_RISCV_EXTIRQMASK_0.poll(EXT=0xffffffff)
        erot.FSP.RISCV_EXTIRQMODE_0.poll(LVL_EXT=0xffffffff)
        erot.FSP.RISCV_EXTIRQMASK_0.poll(EXT=0xffffffff)
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
    #checking_interrupt(OOBHUB_IP_LIST, erot.OOBHUB.PEREGRINE_RISCV_EXTIRQSTAT_0)
    checking_interrupt(FSP_IP_LIST, erot.FSP.RISCV_EXTIRQSTAT_0)
