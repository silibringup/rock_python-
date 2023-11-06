#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import * 
import random

with Test(sys.argv) as t:

    data_value_0 = 0xa5a5c4c4
    data_value_1 = 0xb3b3e5e5
    data_value_2 = 0xf1f1e2e2
    data_value_3 = 0xd5d57979
    dummy_cycle  = 0x8
    data_list = [data_value_0,data_value_1,data_value_2,data_value_3,data_value_3,data_value_2,data_value_1,data_value_0]
#    data_list = [data_value_0,data_value_1,data_value_2,data_value_3]  
    def parse_args():
        t.parser.add_argument("--qspi", action='store', help="Verify QSPI INTI and AP to access flash", default='0')
        t.parser.add_argument("--seed", action='store', help="random_seed", default='0')
        return t.parser.parse_args(sys.argv[1:])
      
    def config_bm_register(bm):
        # mem_address config 
        bm.mem_permission_0.update(region_0=7)
        #all access 0x0-0x10_0000
        bm.reg0_start_address_0.write(0x0)
        bm.reg0_end_address_0.write(0x100)
        bm.flash_cfg_0.update(addr_mode_4b=0,dummy_cyc=8)
        bm.cmd_filter_cmd_0_0.update(dis_cmd=0,cmd_type=2,addr_phase=0,data_io_mode=0,cs_term=0,dum_cyc_en=0,instr_4b=0,cmd_log=0,instr_code=0x06,valid=1)      
        bm.cmd_filter_cmd_1_0.update(dis_cmd=3,cmd_type=2,addr_phase=1,data_io_mode=1,cs_term=1,dum_cyc_en=0,instr_4b=0,cmd_log=1,instr_code=0x02,valid=1)
        bm.cmd_filter_cmd_2_0.update(dis_cmd=3,cmd_type=1,addr_phase=1,data_io_mode=1,cs_term=1,dum_cyc_en=1,instr_4b=0,cmd_log=1,instr_code=0x0b,valid=1)

    def config_write_data(spi,addr):
        spi.DMA_BLK_SIZE_0.write(63)
        for i in range(64):
            #data = addr+i*4
            #spi.TX_FIFO_0.write(data)      
            data = random.randint(0, 0xffffffff)
            spi.TX_FIFO_0.write(data)      

    def burst_read_check(start_addr, golden_words, is_posted=0):
        n_trans_words = len(golden_words)
        helper.pinfo(f"burst read from {hex(start_addr)}")
        rd_vals = helper.fsp_burst_read(start_addr, n_trans_words, is_posted=is_posted)
        if not rd_vals:
            helper.perror(f"No avaliable data read from {hex(start_addr)}, burst write was failed beforehand")
        else:
            if len(rd_vals) != n_trans_words:
                helper.perror(f"Burst Read Size Mismatch: number of words burst read from {hex(start_addr)} should be {n_trans_words}, but is {len(rd_vals)}")
            else:
                for i in range(n_trans_words):
                    if golden_words[i] != rd_vals[i]:
                        helper.perror(f"Burst Read Mismatch: rd_vals[{i}], expect = {hex(golden_words[i])}, actual = {hex(rd_vals[i])}")
                    else:
                        helper.pinfo(f"Burst Read Passed, rd_vals[{i}] = {hex(rd_vals[i])}")
                    
    def send_write_1_1_x_cmd(spi,opcode,address,address_size,data_line,):
        test_api.config_qspi_cmb_cmd(spi,opcode,0,address,address_size)
        config_write_data(spi,address)
        test_api.send_cmd(spi,1,0,31,data_line,0,0)
        
    def qspi_send_data_to_flash(master,flash,addr,qspi_rbi):
        for i in range(1):
            test_api.send_1_0_0_cmd(master,0x06,8)
            if qspi_rbi == 1:
                send_write_1_1_x_cmd(master,0x32,addr,24,2)
            elif qspi_rbi == 0 :
                send_write_1_1_x_cmd(master,0x02,addr,24,0)               
            #test_api.wait_socv_flash_write_done(flash)
            time.sleep(60)
            addr = addr + 0x100

    def check_rbi_data(addr,read_value):
        #exp_rdata_list = []
        #fsp_addr =  addr +  FSP.GLOBAL_IO_ADDR_SPACE_OFFSET
        #for i in range(256):
        #    exp_rdata_list.append(read_value)
        #    read_value = read_value + 4
        #burst_read_check(fsp_addr, exp_rdata_list, is_posted=0)        
        exp_rdata_list = []
        for i in range(256):
            exp_rdata_list.append(read_value)
            read_value = read_value + 4
        for i in range(64):
            rd = helper.read(addr+i*4)
            helper.pinfo(f'read out data : {hex(rd)}')
            helper.pinfo(f'data : {hex(exp_rdata_list[i])}')
            if rd != exp_rdata_list[i]:
                helper.perror(f"rbi read fail")
            time.sleep(30)

    def validate_qspi_rbi(master,master_rbi,addr,flash,flash_addr,qspi_base_addr,qspi_rbi):
        master_rbi.PROM_ADDRESS_OFFSET_0.write(flash_addr)
        if qspi_rbi == 1 :
            master_rbi.COMMAND_0.update(INTERFACE_WIDTH='QUAD',En_LE_Bit=0)  
            master_rbi.CMB_SEQ_CMD_0.update(COMMAND_VALUE=0x6b)
            master_rbi.CMB_SEQ_ADDR_CFG_0.update(ADDRESS_EN_LE_Byte=1)
            master_rbi.MISC_0.update(NUM_OF_DUMMY_CLK_CYCLES=8)

        elif qspi_rbi == 0:
            master_rbi.COMMAND_0.update(INTERFACE_WIDTH='DUAL',En_LE_Bit=0)  
            master_rbi.CMB_SEQ_CMD_0.update(COMMAND_VALUE=0x3b)   
            master_rbi.CMB_SEQ_ADDR_CFG_0.update(ADDRESS_EN_LE_Byte=1)
            master_rbi.MISC_0.update(NUM_OF_DUMMY_CLK_CYCLES=8)

        qspi_send_data_to_flash(master,flash,flash_addr+addr-qspi_base_addr,qspi_rbi)    
        master.DMA_BLK_SIZE_0.write(255)
        check_rbi_data(addr,flash_addr+addr-qspi_base_addr)
        wait_rbi_finish(master)       
    
    def wait_rbi_finish(master):
        master.FIFO_STATUS_0.poll(timeout=10000,RX_FIFO_EMPTY=1)
                 
    LOG("START QSPI INI TEST") 
    test_api.connect_to_micron_flash()    
    helper.wait_sim_time("us", 600)
    time.sleep(60)
    options = parse_args() 
    random.seed(options.seed)
    if options.qspi == '0' :
        test_api.qspi0_init()
        erot.QSPI0.QSPI.GLOBAL_TRIM_CNTRL_0.update(SEL=1)     
        erot.QSPI0.QSPI.GLOBAL_TRIM_CNTRL_0.poll(SEL=1)
        erot.CLOCK.NVEROT_CLOCK_IO_CTL.SW_QSPI0_CLK_RCM_CFG_0.update(DIV_SEL_DIV_SW=7) 
        #validate_qspi_rbi(erot.QSPI0.QSPI,erot.QSPI0.RBI,0x148000,0,0,0x148000,1)       
        validate_qspi_rbi(erot.QSPI0.QSPI,erot.QSPI0.RBI,0x149000,0,0x10000,0x148000,1)
    elif options.qspi == '1': 
        test_api.qspi1_init()
        erot.QSPI1.QSPI.GLOBAL_TRIM_CNTRL_0.update(SEL=1)     
        erot.QSPI1.QSPI.GLOBAL_TRIM_CNTRL_0.poll(SEL=1)
        erot.CLOCK.NVEROT_CLOCK_IO_CTL.SW_QSPI1_CLK_RCM_CFG_0.update(DIV_SEL_DIV_SW=7) 
        #validate_qspi_rbi(erot.QSPI1.QSPI,erot.QSPI1.RBI,0x24b000,2,0,0x24b000,1)
        validate_qspi_rbi(erot.QSPI1.QSPI,erot.QSPI1.RBI,0x24c000,2,0x10000,0x24b000,1)            
    elif options.qspi == '2':
        test_api.boot_qspi_init()
        test_api.boot_qspi_clk_init()
        erot.CLOCK.NVEROT_CLOCK_SYS_CTL.SW_BOOT_QSPI_CLK_RCM_CFG_0.update(DIV_SEL_DIV_SW=7)
        #validate_qspi_rbi(erot.BOOT_QSPI.QSPI,erot.BOOT_QSPI.RBI,0x45000,4,0,0x45000,0)  
        validate_qspi_rbi(erot.BOOT_QSPI.QSPI,erot.BOOT_QSPI.RBI,0x46000,4,0x10000,0x45000,0)    
    else:
        helper.perror("Wrong --qspi %s" % options.qspi)





