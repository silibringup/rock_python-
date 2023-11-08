#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import * 
from driver.components.spi_mst import SPI_SCLK_FREQ_SEL

with Test(sys.argv) as t:

    read_data    = 0
    write_data   = 0
    write_data_0 = 0x5a5a5a5a
    write_data_1 = 0xf1e2d3c4

    def parse_args():
        t.parser.add_argument("--monitor", action='store', help="Verify SPI_MON WITH QSPI VIP", default='0')
        return t.parser.parse_args(sys.argv[1:])

    def config_bm_filter(bm):
        bm.mem_permission_0.update(region_0=7,region_1=1)

        #all_access for addr(0x0-0x20_0000)
        bm.reg0_start_address_0.write(0x0)
        bm.reg0_end_address_0.write(0x200)

        #read_only for addr(0x20_0000-0x30_0000)
        bm.reg1_start_address_0.write(0x200)
        bm.reg1_end_address_0.write(0x300)

        bm.flash_cfg_0.update(dummy_cyc=dummy_cycle)
        #write enable 
        bm.cmd_filter_cmd_0_0.update(dis_cmd=0,cmd_type=0,addr_phase=0,data_io_mode=0,cs_term=1,dum_cyc_en=0,instr_4b=0,cmd_log=0,instr_code=0x06,valid=1)
        #1-1-1 write opcode 
        bm.cmd_filter_cmd_1_0.update(dis_cmd=3,cmd_type=2,addr_phase=1,data_io_mode=1,cs_term=0,dum_cyc_en=0,instr_4b=0,cmd_log=3,instr_code=0x02,valid=1)
        #1-1-2 write opcode
        bm.cmd_filter_cmd_2_0.update(dis_cmd=2,cmd_type=2,addr_phase=1,data_io_mode=2,cs_term=0,dum_cyc_en=0,instr_4b=0,cmd_log=3,instr_code=0xa2,valid=1)      
        #1-1-4 write opcode
        bm.cmd_filter_cmd_3_0.update(dis_cmd=2,cmd_type=2,addr_phase=1,data_io_mode=3,cs_term=0,dum_cyc_en=0,instr_4b=0,cmd_log=3,instr_code=0x32,valid=1) 
        #1-1-1 read opcode 
        bm.cmd_filter_cmd_4_0.update(dis_cmd=2,cmd_type=1,addr_phase=1,data_io_mode=1,cs_term=0,dum_cyc_en=1,instr_4b=0,cmd_log=3,instr_code=0x0b,valid=1) 
        #1-1-2 read opcode 
        bm.cmd_filter_cmd_5_0.update(dis_cmd=2,cmd_type=1,addr_phase=1,data_io_mode=2,cs_term=0,dum_cyc_en=1,instr_4b=0,cmd_log=3,instr_code=0x3b,valid=1) 
        #1-1-4 read opcode 
        bm.cmd_filter_cmd_6_0.update(dis_cmd=2,cmd_type=1,addr_phase=1,data_io_mode=3,cs_term=0,dum_cyc_en=1,instr_4b=0,cmd_log=3,instr_code=0x6b,valid=1) 
        #1-0-1 read config 
        bm.cmd_filter_cmd_7_0.update(dis_cmd=0,cmd_type=1,addr_phase=0,data_io_mode=1,cs_term=0,dum_cyc_en=0,instr_4b=0,cmd_log=0,instr_code=0x05,valid=1) 
        #1-1-0 erase block
        bm.cmd_filter_cmd_8_0.update(dis_cmd=2,cmd_type=3,addr_phase=1,data_io_mode=0,cs_term=0,dum_cyc_en=0,instr_4b=0,cmd_log=2,instr_code=0x20,valid=1) 
        #1-0-1 read flash config 
        bm.cmd_filter_cmd_9_0.update(dis_cmd=0,cmd_type=1,addr_phase=0,data_io_mode=1,cs_term=0,dum_cyc_en=0,instr_4b=0,cmd_log=0,instr_code=0x70,valid=1) 
        #1-1-1 slow read with no dummy_cycle
        bm.cmd_filter_cmd_10_0.update(dis_cmd=2,cmd_type=1,addr_phase=1,data_io_mode=1,cs_term=0,dum_cyc_en=0,instr_4b=0,cmd_log=3,instr_code=0x03,valid=1) 
        #1-0-1 read ID
        bm.cmd_filter_cmd_11_0.update(dis_cmd=0,cmd_type=1,addr_phase=0,data_io_mode=1,cs_term=0,dum_cyc_en=0,instr_4b=0,cmd_log=0,instr_code=0x9e,valid=1)
                  


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

    def bypmon_reg_write(bm_reg, write_data):
        bm_reg.write(write_data)
        LOG(f"write value: {hex(write_data)}")

    def bypmon_reg_check(bm_reg, write_data, after_lock):
        read_data = 0
        count = 0
        timeout = 20
        mask = bm_reg.read_mask
        exp = write_data & mask
        while count < timeout:
            read_data = bm_reg.read().value & mask
            count += 1
            if not after_lock:
                if read_data == exp:
                    helper.log(f"Poll REG {bm_reg.name} done after {count} times. Reg value = {hex(read_data)}. Exp value = {hex(exp)}")
                    return
            else:
                if read_data != exp:
                    helper.log(f"Poll REG {bm_reg.name} done after {count} times. Reg value = {hex(read_data)}. Exp value = {hex(exp)}")
                    return
        helper.perror(f"Poll timeout after {count} times try. Reg value = {hex(read_data)}. Exp value = {hex(exp)}")


    def chk_reg_rst_value(reg):
        if not isinstance(reg, Rock_reg):
            helper.perror("parameter is not a Rock_reg")
            return
        rd = reg.read()
        mask = reg.reset_mask & reg.read_mask
        act = rd.value & mask
        exp = reg.reset_val & mask
        LOG(f"read value: {hex(act)}")
        if act != exp:
            helper.perror("Mismatch, %s's value is not as expected" % reg.name)


    def validate_bypmon_reg_locker(bm):
        validate_cmd_fltr_aperture(bm)
        validate_cfg_aperture(bm)
        validate_cfgl_aperture(bm)

    def validate_cmd_fltr_aperture(bm):
        LOG(f"#################################################################")
        LOG(f"################## Validate CMD_FLTR aperture ###################")
        LOG(f"#################################################################")
        cur_reg = bm.cmd_filter_cmd_0_0
        LOG(f"========================= Unlock ========================")
        bypmon_reg_write(cur_reg, write_data_0)
        bypmon_reg_check(cur_reg, write_data_0, 0)
        bm.aper_lock_0.update(cmd_fltr_lock=0x1)
        helper.wait_sim_time("us", 5)
        LOG(f"========================== Lock =========================")
        # bypmon_reg_check(cur_reg, write_data_0, 1)
        bypmon_reg_write(cur_reg, write_data_1)
        bm.aper_lock_0.update(cmd_fltr_lock=0x0)
        helper.wait_sim_time("us", 5)
        LOG(f"========================= Unlock ========================")
        bypmon_reg_check(cur_reg, write_data_0, 0)
        bypmon_reg_write(cur_reg, write_data_1)
        bypmon_reg_check(cur_reg, write_data_1, 0)
        helper.wait_sim_time("us", 5)

    def validate_cfg_aperture(bm):
        LOG(f"#################################################################")
        LOG(f"##################### Validate CFG aperture #####################")
        LOG(f"#################################################################")
        cur_reg = bm.mem_permission_0
        LOG(f"========================= Unlock ========================")
        bypmon_reg_write(cur_reg, write_data_0)
        bypmon_reg_check(cur_reg, write_data_0, 0)
        bm.accs_lock_0.update(cfg_lock=0x1)
        helper.wait_sim_time("us", 5)
        LOG(f"========================== Lock =========================")
        bypmon_reg_check(cur_reg, write_data_0, 0)
        bypmon_reg_write(cur_reg, write_data_1)
        bm.accs_lock_0.update(cfg_lock=0x0)
        helper.wait_sim_time("us", 5)
        LOG(f"========================= Unlock ========================")
        bypmon_reg_check(cur_reg, write_data_0, 0)
        bypmon_reg_write(cur_reg, write_data_1)
        bypmon_reg_check(cur_reg, write_data_1, 0)
        helper.wait_sim_time("us", 5)
        
    def validate_cfgl_aperture(bm):
        LOG(f"#################################################################")
        LOG(f"#################### Validate CFGL aperture #####################")
        LOG(f"#################################################################")
        cur_reg = bm.flash_cfg_0
        LOG(f"========================= Unlock ========================")
        bypmon_reg_write(cur_reg, write_data_0)
        bypmon_reg_check(cur_reg, write_data_0, 0)
        bm.aper_lock_0.update(cfgl_lock=0x1)
        helper.wait_sim_time("us", 5)
        LOG(f"========================== Lock =========================")
        # bypmon_reg_check(cur_reg, write_data_0, 1)
        bypmon_reg_write(cur_reg, write_data_1)
        erot.RESET.NVEROT_RESET_CFG.SW_SPIMON0_RST_0.write(RESET_SPIMON0=0)
        helper.wait_sim_time("us", 1)
        erot.RESET.NVEROT_RESET_CFG.SW_SPIMON0_RST_0.write(RESET_SPIMON0=1)
        helper.wait_sim_time("us", 10)
        LOG(f"==================== Unlock (SW rst) ====================")
        chk_reg_rst_value(cur_reg)
        bypmon_reg_write(cur_reg, write_data_1)
        bypmon_reg_check(cur_reg, write_data_1, 0)
        helper.wait_sim_time("us", 5)



    LOG("START BYPMON_REG_LOCKER FPGA TEST")
    deassert_sw_reset_l1()
    deassert_sw_reset_l3()
    helper.wait_sim_time("us", 5)
    options = parse_args() 
    if options.monitor == '0' :
        validate_bypmon_reg_locker(erot.SPI_MON0)
    elif options.monitor == '1': 
        validate_bypmon_reg_locker(erot.SPI_MON1)
    else:
        helper.perror("Wrong --monitor %s" % options.monitor)
    helper.log("Test done")

