#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import * 
from driver.components.spi_mst import SPI_SCLK_FREQ_SEL
import time

with Test(sys.argv) as t:

    data_value_0 = 0xa5a5c4c4
    data_value_1 = 0xb3b3e5e5
    data_value_2 = 0xf1f1e2e2
    data_value_3 = 0xd5d57979
    dummy_cycle  = 0x8
    read_bytes   = []
    read_value   = 0
    write_data   = 0xf1e2d3c4f2e3d4c5
    write_data_1 = 0xc4c4a5a5e5e5b3b3
    default_data = 0xffffffffffffffff
    addr_list_0  = [0x01,0x23,0x00]
    addr_list_1  = [0x20,0x23,0x00]      
    erase_addr_1 = 0x012300
    erase_addr_2 = 0x202300   

    def parse_args():
        t.parser.add_argument("--monitor", action='store', help="Verify SPI_MON WITH QSPI VIP", default='0')
        return t.parser.parse_args(sys.argv[1:])

    def enable_bypass_monitor(bm):
        bm.bmon_cfg_0.update(mon_mode=0,ap_flash_acc_en=1)

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
                  
    def ap_wait_flash_write_done(ap_id,bm_cs):
        while True:
            helper.wait_sim_time("us", 1)
            read_bytes = helper.spi_read(spi_port=ap_id, cs_id=bm_cs, 
                n_instruction_lane=1, n_instruction_bits=8, instruction=[0x70],
                n_address_lane=1, n_address_bits=0, address=[], 
                n_data_lane=1, nbr_rd_bytes=1)  
            read_value = int.from_bytes(read_bytes, "big")
            WIP_valid = read_value & 0x80
            if WIP_valid != 0x0:
                print("Sector Erase/Program done")
                break   
    
    def qspi_wait_flash_write_done(qspi,cs):
        while True:
            helper.wait_sim_time("us", 1)
            test_api.send_read_1_0_x_socv(qspi,0x70,0,8,0,cs)
            rd = qspi.RX_FIFO_0.read()
            WIP_valid = rd.value & 0x80
            if WIP_valid != 0x0:
                print("Sector Erase/Program done")
                break 

    def ini_bm(monitor):
        helper.pinfo("config bypmon")
        config_bm_filter(monitor)
        helper.pinfo("enable bypmon")
        enable_bypass_monitor(monitor)
        #helper.spi_set_sclk_frequency(spi_port=0, freq_sel=SPI_SCLK_FREQ_SEL.SPI_SCLK_10MHZ)

    def validate_ap_access_flash(ap_id,bm_cs):
        ########################################################################
        ################################# MISC #################################
        ########################################################################
        LOG(f"##################################################################")
        LOG(f"############################## MISC ##############################")
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
        ########################## 1-0-0 LEGAL CFG #############################
        ########################################################################
        LOG(f"##################################################################")
        LOG(f"######################## 1-0-0 LEGAL CFG #########################")
        LOG(f"##################################################################")
        #Enable VIP to send legal cfg: write enable 
        #1-0-0 config
        helper.spi_write(spi_port=ap_id, cs_id=bm_cs, 
                     n_instruction_lane=1, n_instruction_bits=0, instruction=[],
                     n_address_lane=1, n_address_bits=0, address=[], 
                     n_data_lane=1, data=[0x06])
        LOG(f"legal 1-0-0 write enable to Flash")


        ########################################################################
        ########################### 1-1-1 LEGAL WR #############################
        ########################################################################
        LOG(f"##################################################################")
        LOG(f"######################## 1-1-1 LEGAL WR ##########################")
        LOG(f"##################################################################")
        #Enable VIP to send legal memory wr: 0x01_2300 - 0x01_2307(8 byte)
        #1-1-1 write
        helper.spi_write(spi_port=ap_id, cs_id=bm_cs, 
                     n_instruction_lane=1, n_instruction_bits=8, instruction=[0x02],
                     n_address_lane=1, n_address_bits=24, address=addr_list_0, 
                     n_data_lane=1, data=list(write_data.to_bytes(8,"big")))
        LOG(f"legal 1-1-1 write data to Flash address 0x01_2300 - 0x01_2307 : {hex(write_data)}")


        ########################################################################
        ########################### 1-1-1 LEGAL RD #############################
        ########################################################################
        LOG(f"##################################################################")
        LOG(f"######################## 1-1-1 LEGAL RD ##########################")
        LOG(f"##################################################################")
        #Enable VIP to send legal memory rd: 0x01_2300 - 0x01_2307(8 byte)
        #1-1-1 read
        helper.wait_sim_time("us", 1)
        read_bytes = helper.spi_read(spi_port=ap_id, cs_id=bm_cs, 
                     n_instruction_lane=1, n_instruction_bits=8, instruction=[0x03],
                     n_address_lane=1, n_address_bits=24, address=addr_list_0, 
                     n_data_lane=1, nbr_rd_bytes=8, dummy_cycles=0) 
        read_value = int.from_bytes(read_bytes, "big")
        LOG(f"legal 1-1-1 read data from Flash address 0x01_2300 - 0x01_2307 : {hex(read_value)}")
        if read_value == write_data:
            helper.perror("read data did not match write data")


        ########################################################################
        ########################## 1-1-0 LEGAL ERS #############################
        ########################################################################
        LOG(f"##################################################################")
        LOG(f"######################## 1-1-0 LEGAL ERS #########################")
        LOG(f"##################################################################")
        #Enable VIP to send legal cfg: write enable 
        #1-0-0 config
        helper.spi_write(spi_port=ap_id, cs_id=bm_cs, 
                     n_instruction_lane=1, n_instruction_bits=0, instruction=[],
                     n_address_lane=1, n_address_bits=0, address=[], 
                     n_data_lane=1, data=[0x06])
        LOG(f"legal 1-0-0 write enable to Flash")

        #Enable VIP to send legal memory ers: 0x01_2300 - 0x01_2b00(4 Kbyte)
        #1-1-0 erase
        helper.spi_write(spi_port=ap_id, cs_id=bm_cs, 
                     n_instruction_lane=1, n_instruction_bits=8, instruction=[0x20],
                     n_address_lane=1, n_address_bits=0, address=[], 
                     n_data_lane=1, data=list(erase_addr_1.to_bytes(3,"big")))
        LOG(f"legal 1-1-0 erase 4KB to Flash address 0x012300 - 0x012b00")

        # FIXME, be reminded to check PAD CS=1/SCK=0 in no_pass mode, after AP_FLASH_ACC_EN = AP
        LOG(f"FIXME, be reminded to check PAD CS=1/SCK=0 in no_pass mode, after AP_FLASH_ACC_EN = AP")
        
        
    def validate_qspi_access_flash(qspi,cs):    
        #config QSPI to send write command to address 0x02_2300 to 0x02_2307(8 bytes)
        test_api.send_1_0_0_socv(qspi,0x06,8,cs)
        test_api.send_write_1_1_x_socv(qspi,0x32,0x202300,24,2,3,data_value_0,data_value_1,data_value_2,data_value_3,cs)     
        qspi_wait_flash_write_done(qspi,cs)
        test_api.send_read_1_1_x_socv(qspi,0x0b,0x202300,24,0,3,8,cs)  
        helper.wait_sim_time("us", 1)   
        test_api.read_flash_data_for_check(qspi,data_value_0)
        test_api.read_flash_data_for_check(qspi,data_value_1)
        test_api.read_flash_data_for_check(qspi,data_value_2)
        test_api.read_flash_data_for_check(qspi,data_value_3)

    def check_flash_write_fail(ap_id,bm_cs):
        #enable VIP to send legal read command to check write data has not successed
        #1-1-1 read
        helper.wait_sim_time("us", 10)
        read_bytes = helper.spi_read(spi_port=ap_id, cs_id=bm_cs, 
                     n_instruction_lane=1, n_instruction_bits=8, instruction=[0x03],
                     n_address_lane=1, n_address_bits=24, address=addr_list_1, 
                     n_data_lane=1, nbr_rd_bytes=8, dummy_cycles=0) 
        read_value = int.from_bytes(read_bytes, "big")
        LOG(f"1-1-1 read value from address 0x022300: {hex(read_value)}")
        if read_value != write_data_1:
            helper.perror("read data did not match write data")

    def validate_ap_socv(qspi,monitor,ap,cs):
        helper.pinfo("begin to init bypmon")
        ini_bm(monitor)
        helper.wait_sim_time("us", 15)
        time.sleep(2)
        helper.pinfo("begin to validate bypmon")
        validate_ap_access_flash(ap,cs)

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


    LOG("START BYPMON_NO_PASS FPGA TEST")
    deassert_sw_reset_l1()
    deassert_sw_reset_l3()
    test_api.qspi0_init()
    test_api.qspi1_init()
    test_api.connect_to_micron_flash()
    test_api.enable_vip_connection()
    helper.wait_sim_time("us", 5)
    time.sleep(1)
    options = parse_args() 
    if options.monitor == '0' :
        validate_ap_socv(erot.QSPI0.QSPI,erot.SPI_MON0,0,0)
    elif options.monitor == '1': 
        validate_ap_socv(erot.QSPI1.QSPI,erot.SPI_MON1,1,0)
    else:
        helper.perror("Wrong --monitor %s" % options.monitor)
    helper.log("Test done")

