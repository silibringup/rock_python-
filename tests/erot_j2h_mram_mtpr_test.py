#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import * 
import random

with Test(sys.argv) as t:
    MRAM_BASE_ADDR = 0xfc0000
    MRAM_MTPR_BASE_ADDR = 0x1000000

    def mram_mtp_write(addr, data_list, rand_shuffle=0):
        if not isinstance(data_list, list):
            self.perror("data_list should be a list")
            return
        if len(data_list) != 8:
            self.perror("data_list's size should == 0")
            return
        idx_list = list(range(9))
        if rand_shuffle == 1:
            random.shuffle(idx_list)
        for i in idx_list:
            if i < 8:
                #Prepare 256-bit data to write in MRAM_MTP_WPORT_DATA[0-7]
                helper.j2h_write(MRAM_BASE_ADDR+0x30004+(i*4), data_list[i])
            else:
                 #Prepare target MTP offset-to-write in MRAM_MTP_WPORT_ADDR
                 helper.j2h_write(MRAM_BASE_ADDR+0x30000, addr)
        #Write to MRAM_MTP_WPORT_CMD triggers a MRAM MTP write task (TRIG=1)
        helper.j2h_write(MRAM_BASE_ADDR+0x30024, 1)
        #Poll a write completion with MRAM_MTP_WPORT_STATE (BUSY=0)
        rd = helper.j2h_read(MRAM_BASE_ADDR+0x30028)
        cnt = 0
        while rd & 0x1 != 0 and cnt < 10:
            rd = helper.j2h_read(MRAM_BASE_ADDR+0x30028)
            cnt += 1
        if rd & 0x1 != 0:
            helper.perror(f'poll mram_mtp_rport_state_0 fail, BUSY = {rd & 0x1}')

    '''def mram_mtp_read(addr):
        #Prepare target MTP offset-to-read in MRAM_MTP_RPORT_ADDR
        helper.j2h_write(MRAM_BASE_ADDR+0x30800, addr)
        #Write to MRAM_MTP_RPORT_CMD(i) triggers a MRAM MTP read task (TRIG=1)
        helper.j2h_write(MRAM_BASE_ADDR+0x30824, 1)
        #Poll a write completion with MRAM_MTP_RPORT_STATE (BUSY=0)
        rd = helper.j2h_read(MRAM_BASE_ADDR+0x30828)
        cnt = 0
        while rd & 0x1 != 0 and cnt < 10:
            rd = helper.j2h_read(MRAM_BASE_ADDR+0x30828)
            cnt += 1
        if rd & 0x1 != 0:
            helper.perror(f'poll mram_mtp_rport_state_0 fail, BUSY = {rd & 0x1}')
        rd_data_list = []
        rd_addr_list = []
        for i in range(8):
            #The 256-bit read data is captured on MRAM_MTP_RPORT_DATA[0-7]
            rd = helper.j2h_read(MRAM_BASE_ADDR+0x30804+(i*4))
            rd_data_list.append(rd)
        return rd_data_list'''


    helper.pinfo("Test start") 
    helper.wait_sim_time('us', 50)
    if helper.target == "simv_fpga":
        helper.hdl_force('ntb_top.u_nv_fpga_dut.u_nv_top_fpga.u_nv_top_wrapper.u_nv_top.nvjtag_sel', 1)
    if helper.target != "simv_fpga":
        helper.pinfo(f'remove fuse force')
        #helper.hdl_force('ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.opt_nvjtag_protection_enable_final', 0)
        #helper.hdl_force('ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.opt_secure_jtag_secureID_valid', 0)
        #helper.hdl_force('ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.static_chip_option_sense_done', 1)
        #helper.hdl_force('ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.opt_secure_jtag_secureID_valid_inv', 1)
        helper.hdl_force('ntb_top.u_nv_top.nvjtag_sel', 1)

    helper.jtag.Led(1)
    helper.jtag.Reset(0)
    helper.jtag.DRScan(100, hex(0x0)) #add some delay as jtag only work when nvjtag_sel stable in real case
    helper.jtag.Reset(1)  

    #unlock j2h interface
    helper.j2h_unlock()

    #poll L3 reset released
    cnt = 0
    l3_released = 0
    while l3_released == 0 and cnt < 10:
        rd = helper.j2h_read(0x33010, check_ack=False) #erot.RESET.NVEROT_RESET_CFG.SW_L3_RST_0
        cnt += 1
        if rd & 0x1 == 1:
            l3_released = 1
    if l3_released == 0:
        helper.perror(f'L3_reset not released before w/r registers')
    
    helper.pinfo("Init the start 50*256b in MRAM")
    for i in range(50):
        wr_addr = i*32
        wr_data_list = []
        rd_data_list = []
        for j in range(8):
            exp_data = random.randint(0,(1<<32)-1)
            wr_data_list.append(exp_data)

        helper.pinfo(f'wr_data_list_{i} = {wr_data_list}, address offset {hex(wr_addr)}')
        mram_mtp_write(wr_addr, wr_data_list, rand_shuffle=1)
        helper.pinfo(f'{i}th mram_mtp_write finished')

        for k in range(8):
            rd = helper.j2h_read(MRAM_MTPR_BASE_ADDR + (i*32) + (k*4))
            rd_data_list.append(rd)
        helper.pinfo(f'mram_mtp_read_{i} {rd_data_list}, address {hex(MRAM_MTPR_BASE_ADDR+(i*32))} to {hex(MRAM_MTPR_BASE_ADDR+(i*32)+28)}')
        helper.pinfo(f'{i}th mram_mtp_read finished')

        if rd_data_list != wr_data_list:
            helper.perror(f'Mismatch at loop {i}, read out data = {rd_data_list} while write in data = {wr_data_list}')
            
    helper.jtag.Led(0)
    helper.pinfo("Test done")
        
