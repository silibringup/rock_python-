#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import * 

with Test(sys.argv) as t:

    data_value_0 = 0xa5a5c4c4
    data_value_1 = 0xb3b3e5e5
    data_value_2 = 0xf1f1e2e2
    data_value_3 = 0xd5d57979
    dummy_cycle  = 0x8
    data_list = [data_value_0,data_value_1,data_value_2,data_value_3,data_value_3,data_value_2,data_value_1,data_value_0]
 
    def parse_args():
        t.parser.add_argument("--qspi", action='store', help="Verify QSPI INTI and AP to access flash", default='0')
        return t.parser.parse_args(sys.argv[1:])
                 
    def backdoor_check(flash,addr):
        for i in range(len(data_list)):
            test_api.back_door_read_flash(flash,addr,data_list[i])
            addr = addr + 4 

    def send_1_0_0_cmd(spi,cs,data,size):
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
        spi.TRANSFER_STATUS_0.poll(timeout=1000,RDY=1)
        spi.TRANSFER_STATUS_0.write(RDY=1) 

    def send_write_1_1_x_cmd(spi,cs,opcode,address,address_size,data_line,data_byte,data0,data1,data2,data3):
        test_api.config_qspi_cmb_cmd(spi,opcode,0,address,address_size)
        if data_byte == 3 :
            test_api.config_16B_write_data(spi,data0,data1,data2,data3)
        else:
            test_api.config_32B_write_data(spi,data0,data1,data2,data3)
        test_api.send_cmd(spi,1,0,31,data_line,0,cs)

    def send_read_1_1_x_cmd_flash(spi,cs,opcode,address,address_size,data_line,data_byte,dummy_cycle):
        test_api.config_qspi_cmb_cmd(spi,opcode,0,address,address_size)  
        spi.DMA_BLK_SIZE_0.write(data_byte)
        test_api.send_cmd(spi,0,1,31,data_line,dummy_cycle,cs) 


    def qspi_send_data_to_flash(master,cs,flash,addr,boot):
        if boot == 0 :
            send_1_0_0_cmd(master,cs,0x06,8)
            #1-1-1 write mode and 32byte for one command
            send_write_1_1_x_cmd(master,cs,0x02,addr,24,0,7,data_value_0,data_value_1,data_value_2,data_value_3)
            #test_api.wait_socv_flash_write_done(flash)
            time.sleep(100)
            send_1_0_0_cmd(master,cs,0x06,8)
            #1-1-2 write mode and 32byte for one command
            send_write_1_1_x_cmd(master,cs,0xa2,addr+32,24,1,7,data_value_0,data_value_1,data_value_2,data_value_3)
            #test_api.wait_socv_flash_write_done(flash)   
            time.sleep(100)
            send_1_0_0_cmd(master,cs,0x06,8) 
            #1-1-4 write mode and 32byte for one command
            send_write_1_1_x_cmd(master,cs,0x32,addr+64,24,2,7,data_value_0,data_value_1,data_value_2,data_value_3)
            #test_api.wait_socv_flash_write_done(flash) 
            time.sleep(100)
        elif boot == 1 :
            send_1_0_0_cmd(master,cs,0x06,8)
            #1-1-1 write mode and 32byte for one command
            send_write_1_1_x_cmd(master,cs,0x02,addr,24,0,7,data_value_0,data_value_1,data_value_2,data_value_3)
            #test_api.wait_socv_flash_write_done(flash)
            time.sleep(100)
            send_1_0_0_cmd(master,cs,0x06,8)
            #1-1-2 write mode and 32byte for one command
            send_write_1_1_x_cmd(master,cs,0xa2,addr+32,24,1,7,data_value_0,data_value_1,data_value_2,data_value_3)
            #test_api.wait_socv_flash_write_done(flash)
            time.sleep(100) 

    def validate_qspi_read(master,cs,addr,boot):
        if boot == 0 :
        #1-1-1 read mode for 32 btye
            send_read_1_1_x_cmd_flash(master,cs,0x0b,addr,24,0,7,0x8)
            for i in range(len(data_list)):    
                test_api.read_flash_data_for_check(master,data_list[i]) 
            helper.wait_sim_time("us", 1)               
        #1-1-2 read mode for 32 btye
            send_read_1_1_x_cmd_flash(master,cs,0x3b,addr+32,24,1,7,0x8)
            for i in range(len(data_list)):    
                test_api.read_flash_data_for_check(master,data_list[i]) 
            helper.wait_sim_time("us", 1)
        #1-1-4 read mode for 32 btye
            send_read_1_1_x_cmd_flash(master,cs,0x6b,addr+64,24,2,7,0x8)
            for i in range(len(data_list)):    
                test_api.read_flash_data_for_check(master,data_list[i]) 
            helper.wait_sim_time("us", 1)    
        elif boot == 1 :
        #1-1-1 read mode for 32 btye
            send_read_1_1_x_cmd_flash(master,cs,0x0b,addr,24,0,7,0x8)
            for i in range(len(data_list)):    
                test_api.read_flash_data_for_check(master,data_list[i]) 
            helper.wait_sim_time("us", 1)               
        #1-1-2 read mode for 32 btye
            send_read_1_1_x_cmd_flash(master,cs,0x3b,addr+32,24,1,7,0x8)
            for i in range(len(data_list)):    
                test_api.read_flash_data_for_check(master,data_list[i]) 
            helper.wait_sim_time("us", 1)            

    def validate_qspi_flash(master,cs,flash_num,boot,addr):
        flash = flash_num * 2 + cs
        qspi_send_data_to_flash(master,cs,flash,addr,boot)
        validate_qspi_read(master,cs,addr,boot)

    LOG("START QSPI INI TEST") 
    test_api.connect_to_micron_flash()
    options = parse_args() 
    if options.qspi == '0' :
        helper.wait_sim_time("us", 600)
        test_api.qspi0_init()
        #test_api.qspi0_clk_init()
        erot.QSPI0.QSPI.GLOBAL_TRIM_CNTRL_0.update(SEL=1)     
        erot.QSPI0.QSPI.GLOBAL_TRIM_CNTRL_0.poll(SEL=1)
        validate_qspi_flash(erot.QSPI0.QSPI,0,0,0,0x0)
        validate_qspi_flash(erot.QSPI0.QSPI,1,0,0,0x0)    
        if helper.target != 'simv_fpga':
            test_api.fuse_force_l1_rst()
            helper.wait_sim_time("us", 600)        
            test_api.qspi0_init()
            validate_qspi_flash(erot.QSPI0.QSPI,0,0,0,0x1000)
            validate_qspi_flash(erot.QSPI0.QSPI,1,0,0,0x1000)             
    elif options.qspi == '1': 
        helper.wait_sim_time("us", 600)        
        test_api.qspi1_init()
        #test_api.qspi1_clk_init()
        erot.QSPI1.QSPI.GLOBAL_TRIM_CNTRL_0.update(SEL=1)     
        erot.QSPI1.QSPI.GLOBAL_TRIM_CNTRL_0.poll(SEL=1)           
        validate_qspi_flash(erot.QSPI1.QSPI,0,1,0,0x0)
        validate_qspi_flash(erot.QSPI1.QSPI,1,1,0,0x0) 
        if helper.target != 'simv_fpga':
            test_api.fuse_force_l1_rst()    
            helper.wait_sim_time("us", 600)        
            test_api.qspi1_init()
            validate_qspi_flash(erot.QSPI1.QSPI,0,1,0,0x1000)
            validate_qspi_flash(erot.QSPI1.QSPI,1,1,0,0x1000)                   
    elif options.qspi == '2':
        helper.wait_sim_time("us", 600)
        test_api.boot_qspi_init()
        test_api.boot_qspi_clk_init()
        erot.CLOCK.NVEROT_CLOCK_SYS_CTL.SW_BOOT_QSPI_CLK_RCM_CFG_0.update(DIV_SEL_DIV_SW=7)
        validate_qspi_flash(erot.BOOT_QSPI.QSPI,0,2,1,0x0)    
        if helper.target != 'simv_fpga':
            test_api.fuse_force_l1_rst() 
            helper.wait_sim_time("us", 600)
            test_api.boot_qspi_init()
            test_api.boot_qspi_clk_init()
            erot.CLOCK.NVEROT_CLOCK_SYS_CTL.SW_BOOT_QSPI_CLK_RCM_CFG_0.update(DIV_SEL_DIV_SW=7)
            validate_qspi_flash(erot.BOOT_QSPI.QSPI,0,2,1,0x1000)             
    else:
        helper.perror("Wrong --qspi %s" % options.qspi)
