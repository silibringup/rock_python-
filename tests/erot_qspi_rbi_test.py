#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import * 

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
        spi.DMA_BLK_SIZE_0.debug_write(63)
        for i in range(64):
            data = addr+i*4
            spi.TX_FIFO_0.debug_write(data)      

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
        #test_api.config_qspi_cmb_cmd(spi,opcode,0,address,address_size)
        spi.GLOBAL_CONFIG_0.debug_update(CMB_SEQ_EN=1)
        spi.CMB_SEQ_CMD_CFG_0.debug_update(COMMAND_SIZE=7,NO_ADDR_PHASE=0)
        spi.CMB_SEQ_CMD_0.debug_write(opcode)
        spi.CMB_SEQ_ADDR_CFG_0.debug_update(ADDRESS_SIZE=address_size-1,ADDRESS_EN_LE_Byte=1)
        spi.CMB_SEQ_ADDR_0.debug_write(address) 
        spi.INTR_MASK_0.debug_update(RDY_INTR_MASK=0)        
        config_write_data(spi,address)
        #test_api.send_cmd(spi,1,0,31,data_line,0,0)
        spi.COMMAND_0.debug_update(M_S='MASTER',CS_SEL=0,BIT_LENGTH=31,Tx_EN=1,Rx_EN=0,PACKED='ENABLE',INTERFACE_WIDTH=data_line,En_LE_Byte=0,En_LE_Bit=0)
        spi.MISC_0.debug_update(NUM_OF_DUMMY_CLK_CYCLES=0)
        spi.COMMAND_0.debug_update(PIO='PIO')
        spi.TRANSFER_STATUS_0.debug_poll(timeout=1000,RDY=1)
        spi.TRANSFER_STATUS_0.debug_write(RDY=1)         
        
    def qspi_send_data_to_flash(master,flash,addr,qspi_rbi):
        for i in range(4):
            #test_api.send_1_0_0_cmd(master,0x06,8)
            master.GLOBAL_CONFIG_0.debug_update(CMB_SEQ_EN=0)
            master.CMB_SEQ_CMD_CFG_0.debug_update(COMMAND_SIZE=0)
            master.CMB_SEQ_CMD_0.debug_write(0x0)
            master.CMB_SEQ_ADDR_CFG_0.debug_update(ADDRESS_SIZE=0)
            master.CMB_SEQ_ADDR_0.debug_write(0x0)
            master.INTR_MASK_0.debug_update(RDY_INTR_MASK=0)
            master.DMA_BLK_SIZE_0.debug_write(0)
            master.MISC_0.debug_update(NUM_OF_DUMMY_CLK_CYCLES=0)        
            master.TX_FIFO_0.debug_write(0x06)
            master.COMMAND_0.debug_update(M_S='MASTER',BIT_LENGTH=7,Rx_EN='DISABLE',Tx_EN='ENABLE',PACKED='ENABLE',INTERFACE_WIDTH='SINGLE',En_LE_Byte=1,En_LE_Bit=0)
            master.COMMAND_0.debug_update(PIO='PIO')
            master.TRANSFER_STATUS_0.debug_poll(timeout=100,RDY=1)
            master.TRANSFER_STATUS_0.debug_write(RDY=1)            
            if qspi_rbi == 1:
                send_write_1_1_x_cmd(master,0x32,addr,24,2)
            elif qspi_rbi == 0 :
                send_write_1_1_x_cmd(master,0xa2,addr,24,1)               
            #test_api.wait_socv_flash_write_done(flash)
            time.sleep(10)
            addr = addr + 0x100
        
        

    def check_rbi_data(addr,read_value):
        exp_rdata_list = []
        #fsp_addr =  addr +  FSP.GLOBAL_IO_ADDR_SPACE_OFFSET
        for i in range(256):
            exp_rdata_list.append(read_value)
            read_value = read_value + 4
        #burst_read_check(fsp_addr, exp_rdata_list, is_posted=0)        
        for i in range(256):
            rd = helper.j2h_read(addr+i*4)
            helper.pinfo(f'read out data : {rd}')
            helper.pinfo(f'golden data : {exp_rdata_list[i]}')
            if rd != exp_rdata_list[i]:
                helper.perror(f"rbi read fail")
        

    def validate_qspi_rbi(master,master_rbi,addr,flash,flash_addr,qspi_base_addr,qspi_rbi):
        master_rbi.PROM_ADDRESS_OFFSET_0.debug_write(flash_addr)
        master_rbi.CMB_SEQ_ADDR_CFG_0.debug_update( ADDRESS_SIZE=23,ADDRESS_EN_LE_Byte=1)
        if qspi_rbi == 1 :
            master_rbi.COMMAND_0.debug_update(INTERFACE_WIDTH='QUAD')  
            master_rbi.CMB_SEQ_CMD_0.debug_update(COMMAND_VALUE=0x6b)
        qspi_send_data_to_flash(master,flash,flash_addr+addr-qspi_base_addr,qspi_rbi)    
        master.DMA_BLK_SIZE_0.debug_write(255)
        check_rbi_data(addr,flash_addr+addr-qspi_base_addr)
        wait_rbi_finish(master)       
    
    def wait_rbi_finish(master):
        master.FIFO_STATUS_0.debug_poll(timeout=10000,RX_FIFO_EMPTY=1)

    LOG("UNLOCK J2H") 
    helper.wait_sim_time('us', 100)
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
    while l3_released == 0 and cnt < 50:
        rd = helper.j2h_read(0x33010, check_ack=False) #erot.RESET.NVEROT_RESET_CFG.SW_L3_RST_0
        helper.pinfo(f'rd : {rd}')
        cnt += 1
        if rd & 0x1 == 1:
            l3_released = 1
    if l3_released == 0:
        helper.perror(f'L3_reset not released before w/r registers')                   

    LOG("START QSPI RBI TEST") 
    test_api.connect_to_micron_flash()    
    helper.wait_sim_time("us", 600)
    options = parse_args() 
    if options.qspi == '0' :
        #test_api.qspi0_init()

        helper.log('start to initialize QSPI0 I/O')
        erot.PADCTRL_E.EROT_QSPI0_CLK_0.debug_update(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_CS0_N_0.debug_update(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_CS1_N_0.debug_update(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_IO0_0.debug_update(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_IO1_0.debug_update(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_IO2_0.debug_update(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_IO3_0.debug_update(TRISTATE=0)

        erot.PADCTRL_E.EROT_QSPI0_CLK_0.debug_poll(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_CS0_N_0.debug_poll(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_CS1_N_0.debug_poll(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_IO0_0.debug_poll(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_IO1_0.debug_poll(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_IO2_0.debug_poll(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI0_IO3_0.debug_poll(TRISTATE=0)

        erot.QSPI0.QSPI.GLOBAL_TRIM_CNTRL_0.debug_update(SEL=1)     
        erot.QSPI0.QSPI.GLOBAL_TRIM_CNTRL_0.debug_poll(SEL=1)
        
        erot.CLOCK.NVEROT_CLOCK_IO_CTL.SW_QSPI0_CLK_RCM_CFG_0.debug_update(DIV_SEL_DIV_SW=7) 
        validate_qspi_rbi(erot.QSPI0.QSPI,erot.QSPI0.RBI,0x148000,0,0,0x148000,1)       
        #validate_qspi_rbi(erot.QSPI0.QSPI,erot.QSPI0.RBI,0x148000,0,0x10000,0x148000,1)
    elif options.qspi == '1': 
        #test_api.qspi1_init()
        helper.log('start to initialize QSPI0 I/O')
        erot.PADCTRL_E.EROT_QSPI1_CLK_0.debug_update(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI1_CS0_N_0.debug_update(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI1_CS1_N_0.debug_update(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI1_IO0_0.debug_update(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI1_IO1_0.debug_update(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI1_IO2_0.debug_update(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI1_IO3_0.debug_update(TRISTATE=0)

        erot.PADCTRL_E.EROT_QSPI1_CLK_0.debug_poll(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI1_CS0_N_0.debug_poll(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI1_CS1_N_0.debug_poll(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI1_IO0_0.debug_poll(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI1_IO1_0.debug_poll(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI1_IO2_0.debug_poll(TRISTATE=0)
        erot.PADCTRL_E.EROT_QSPI1_IO3_0.debug_poll(TRISTATE=0)

        erot.QSPI1.QSPI.GLOBAL_TRIM_CNTRL_0.debug_update(SEL=1)     
        erot.QSPI1.QSPI.GLOBAL_TRIM_CNTRL_0.debug_poll(SEL=1)
        erot.CLOCK.NVEROT_CLOCK_IO_CTL.SW_QSPI1_CLK_RCM_CFG_0.debug_update(DIV_SEL_DIV_SW=7) 
        validate_qspi_rbi(erot.QSPI1.QSPI,erot.QSPI1.RBI,0x24b000,2,0,0x24b000,1)
        validate_qspi_rbi(erot.QSPI1.QSPI,erot.QSPI1.RBI,0x24b000,2,0x10000,0x24b000,1)            
    elif options.qspi == '2':
        #test_api.boot_qspi_init()
        #test_api.boot_qspi_clk_init()
        self.log('start to initialize BOOT_QSPI I/O')
        erot.PADCTRL_N.BOOT_QSPI_CLK_0.debug_update(TRISTATE=0)
        erot.PADCTRL_N.BOOT_QSPI_CS_N_0.debug_update(TRISTATE=0)
        erot.PADCTRL_N.BOOT_QSPI_IO0_0.debug_update(TRISTATE=0)
        erot.PADCTRL_N.BOOT_QSPI_IO1_0.debug_update(TRISTATE=0)
        erot.PADCTRL_N.BOOT_QSPI_IO2_0.debug_update(TRISTATE=0)
        erot.PADCTRL_N.BOOT_QSPI_IO3_GP29_0.debug_update(TRISTATE=0)

        erot.PADCTRL_N.BOOT_QSPI_CLK_0.debug_poll(TRISTATE=0)
        erot.PADCTRL_N.BOOT_QSPI_CS_N_0.debug_poll(TRISTATE=0)
        erot.PADCTRL_N.BOOT_QSPI_IO0_0.debug_poll(TRISTATE=0)
        erot.PADCTRL_N.BOOT_QSPI_IO1_0.debug_poll(TRISTATE=0)
        erot.PADCTRL_N.BOOT_QSPI_IO2_0.debug_poll(TRISTATE=0)
        erot.PADCTRL_N.BOOT_QSPI_IO3_GP29_0.debug_poll(TRISTATE=0)       
        
        erot.BOOT_QSPI.QSPI.GLOBAL_TRIM_CNTRL_0.debug_update(SEL=1)     
        erot.BOOT_QSPI.QSPI.GLOBAL_TRIM_CNTRL_0.debug_poll(SEL=1)       
        
        erot.CLOCK.NVEROT_CLOCK_SYS_CTL.SW_BOOT_QSPI_CLK_RCM_CFG_0.update(DIV_SEL_DIV_SW=7)
        validate_qspi_rbi(erot.BOOT_QSPI.QSPI,erot.BOOT_QSPI.RBI,0x45000,4,0,0x45000,0)  
        validate_qspi_rbi(erot.BOOT_QSPI.QSPI,erot.BOOT_QSPI.RBI,0x46000,4,0x10000,0x45000,0)    
    else:
        helper.perror("Wrong --qspi %s" % options.qspi)





