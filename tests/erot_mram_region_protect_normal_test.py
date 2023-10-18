#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import * 
import random

with Test(sys.argv) as t:
    mram = erot.MRAM
    exp_addr_data_dist = {}
    MRAM_MTPR_BASE = mram.base + int(64*1024*4)
    MRAM_MTPR_SIZE = int(4*1024*1024)

    def mram_mtp_write(addr, data_list, priv_id=0, rand_shuffle=0):
        idx_list = list(range(9))
        if rand_shuffle == 1:
            random.shuffle(idx_list)
        if priv_id == 0: #J2H
            for i in idx_list:
                if i < 8:
                    wr_data_reg = mram.get_reg_by_name("mram_mtp_wport_data_" + str(i) + "_0")
                    wr_data_reg.write(VAL=data_list[i])
                else:
                    mram.mram_mtp_wport_addr_0.write(VAL=addr)
        elif priv_id == 1 or priv_id == 2: #fsp
            l_cmd_list = []
            l_addr_list = []
            l_data_list = []
            # prepare addr+data
            for i in idx_list:
                l_cmd_list.append(random.randint(2,3))
                if i < 8:
                    wr_data_reg = mram.get_reg_by_name("mram_mtp_wport_data_" + str(i) + "_0")
                    l_addr_list.append(wr_data_reg.offset + mram.base)
                    l_data_list.append(data_list[i])
                else: 
                    l_addr_list.append(mram.mram_mtp_wport_addr_0.offset + mram.base)
                    l_data_list.append(addr)
            # wport_cmd.trig
            l_cmd_list.append(random.randint(2,3))
            l_addr_list.append(mram.mram_mtp_wport_cmd_0.offset + mram.base)
            l_data_list.append(0x1)
            helper.burst_operation(l_addr_list, l_data_list, l_cmd_list, priv_id=priv_id)
        mram.mram_mtp_wport_state_0.poll(BUSY=0,priv_id=priv_id)

    def mram_mtp_read(addr, priv_id):
        if priv_id == 0:
            mram.mram_mtp_rport_addr_0.write(VAL=addr)
            mram.mram_mtp_rport_cmd_0.write(TRIG=1)
            mram.mram_mtp_rport_state_0.poll(BUSY=0)
            rd_data_list = []
            for i in range(8):
                rd_data_reg = mram.get_reg_by_name("mram_mtp_rport_data_" + str(i) + "_0")
                rd = rd_data_reg.read(priv_id=priv_id)
                rd_data_list.append(rd.value)
            return rd_data_list
        elif priv_id == 1 or priv_id == 2:
            l_cmd_list = []
            l_addr_list = []
            l_data_list = []
            
            l_cmd_list.append(random.randint(2,3))
            l_addr_list.append(mram.mram_mtp_rport_addr_0.offset + mram.base)
            l_data_list.append(addr)

            l_cmd_list.append(random.randint(2,3))
            l_addr_list.append(mram.mram_mtp_rport_cmd_0.offset + mram.base)
            l_data_list.append(0x1)
            helper.burst_operation(l_addr_list, l_data_list, l_cmd_list, priv_id=priv_id)
            mram.mram_mtp_rport_state_0.poll(BUSY=0,priv_id=priv_id)
        
            # get read data
            l_cmd_list = []
            l_addr_list = []
            l_data_list = []
            idx_list = list(range(8))
            random.shuffle(idx_list)
            for i in range(8):
                l_cmd_list.append(0)
                l_addr_list.append(0)
                l_data_list.append(random.randint(0,0xffffffff))

            for i in idx_list:
                rd_data_reg = mram.get_reg_by_name("mram_mtp_rport_data_" + str(i) + "_0")
                l_addr_list[i] = (rd_data_reg.offset + mram.base)
            [act_rdata_list, act_resp_err_list] = helper.burst_operation(l_addr_list, l_data_list, l_cmd_list, priv_id=priv_id)
            return act_rdata_list

    def get_mram_32bx8_list_backdoor(addr):
        data32b_list = []
        for i in range(8):
            mem_element_dir_dw = "ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.mram_inst.core.main_mem[%d][%s:%s]" % (addr>>5, i*32+31, i*32)
            data32b = helper.hdl_read(mem_element_dir_dw)
            data32b_list.append(data32b)
        return data32b_list

    def Check_result(wr_addr_list, exp_addr_datlist_dict, frontdoor=0, expect_fail=0):
        for i in range(len(wr_addr_list)):
            if frontdoor == 0:
                actual_32b_list = get_mram_32bx8_list_backdoor(wr_addr_list[i])
            else:
                if helper.target in ["fpga", "simv_fpga"]:
                    l_priv_id = 0
                else:
                    l_priv_id = random.randint(0,2)
                actual_32b_list = mram_mtp_read(wr_addr_list[i], priv_id=l_priv_id)
            exp_32b_list = exp_addr_datlist_dict[wr_addr_list[i]]
            if expect_fail == 0:
                if actual_32b_list != exp_32b_list:
                    helper.perror("Mismatch, addr: %x" % wr_addr_list[i])
                    helper.log("act: %s" % [hex(x) for x in actual_32b_list])
                    helper.log("exp: %s" % [hex(x) for x in exp_32b_list])
            else:
                if actual_32b_list == exp_32b_list:
                    helper.perror("Unexpected match, addr: %x" % wr_addr_list[i])
                    helper.log("act/exp: %s" % [hex(x) for x in actual_32b_list]) 
    
    def disable_ecc_in_mram():
        mram.mram_cfg_b_apert_mmio_acl_0.update(tmc_aperture_mmio_readable=1,tmc_aperture_mmio_writable=1)
        mram.mram_tmc_udin_i0_0.write(wr_buf=0x1)
        mram.mram_tmc_xadr_i_0.write(0x0)
        mram.mram_tmc_cmd_i_0.update(wrt_config=1)
        mram.mram_tmc_udin_i0_0.write(wr_buf=0x34880061)
        mram.mram_tmc_xadr_i_0.write(0x1)
        mram.mram_tmc_cmd_i_0.update(wrt_config=1)
        mram.mram_tmc_xadr_i_0.write(0x1)
        mram.mram_tmc_cmd_i_0.update(read_config=1)
        while True:
            rd = mram.mram_tmc_regif_dout_o_0.read()
            if rd['rd_buf'] & 0xc == 0:
                break

    def init_mram_backdoor(start_idx_256b, size_256b):
        for i in range(start_idx_256b, start_idx_256b+size_256b):
            for j in range(8):
                mem_element_dir_dw = "ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.mram_inst.core.main_mem[%s][%s:%s]" % (i, j*32+31, j*32)
                exp_data = random.randint(0,(1<<32))
                helper.hdl_deposit(mem_element_dir_dw, exp_data)
                exp_addr_data_dist[MRAM_MTPR_BASE+i*32+j*4] = exp_data

    def init_mram_frontdoor(start_idx_256b, size_256b):
        for i in range(start_idx_256b, start_idx_256b+size_256b):
            wr_addr = i*32
            wr_data_list = []
            for j in range(8):
                exp_data = random.randint(0,(1<<32))
                wr_data_list.append(exp_data)
                exp_addr_data_dist[MRAM_MTPR_BASE+i*32+j*4] = exp_data
            test_api.mram_mtp_write(wr_addr, wr_data_list, rand_shuffle=1)
        helper.log("Finish MRAM frontdoor initialization")
    
    def reset_region_cfg():
        for i in range(8):
            region_start_reg = mram.get_reg_by_name("mram_cfg_b_mtp_region_start_" + str(i) + "_0")
            region_end_reg   = mram.get_reg_by_name("mram_cfg_b_mtp_region_end_" + str(i) + "_0")
            region_start_reg.write(0xffffffff)
            region_end_reg.write(0xffffffff)

    def set_a_region(idx, clear_previous_cfg=1):
        if clear_previous_cfg == 1:
            for i in range(8):
                region_start_reg = mram.get_reg_by_name("mram_cfg_b_mtp_region_start_" + str(i) + "_0")
                region_end_reg   = mram.get_reg_by_name("mram_cfg_b_mtp_region_end_" + str(i) + "_0")
                region_start_reg.write(0xffffffff)
                region_end_reg.write(0xffffffff)
        region_start_reg = mram.get_reg_by_name("mram_cfg_b_mtp_region_start_" + str(idx) + "_0")
        region_end_reg   = mram.get_reg_by_name("mram_cfg_b_mtp_region_end_" + str(idx) + "_0")
        rand_region_start_addr = random.randint(0, MRAM_MTPR_SIZE-1)
        rand_region_start_addr = rand_region_start_addr & 0xfffff000 # region boundary should be 4KB aligned
        rand_region_end_addr = rand_region_start_addr + random.randint(1, 1024)*0x1000
        if rand_region_end_addr > MRAM_MTPR_SIZE:
            rand_region_end_addr = MRAM_MTPR_SIZE
        # leave mram_cfg_b_mtp_region_acl_0_0 without touching, so its writeable/readable == 1 defaultly
        region_start_reg.write(rand_region_start_addr)
        region_end_reg.write(rand_region_end_addr)
        return [rand_region_start_addr, rand_region_end_addr]

    def region_acl_reg_clear():
        for i in range(8):
            region_acl_reg = mram.get_reg_by_name("mram_cfg_b_mtp_region_acl_" + str(i) + "_0")
            region_acl_reg.write(wpen=0,writable=0,readable=0)

    def check_content(addr_data_dist):
        for addr, value in addr_data_dist.items():
            mtp_addr = addr - MRAM_MTPR_BASE
            idx_256b = (mtp_addr>>5)
            idx_32b  = (mtp_addr&0x0000001f) >> 2
            mem_element_dir_dw = "ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.mram_inst.core.main_mem[%s][%s:%s]" % (idx_256b, idx_32b*32+31, idx_32b*32)
            act_data = helper.hdl_read(mem_element_dir_dw)
            if value != act_data:
                helper.perror("Mismatch, addr %x, exp: %x, act: %x" % (addr, value, act_data))




    helper.log("Test start")
    disable_ecc_in_mram()

    if helper.target in ["fpga", "simv_fpga"]:
        #jtag unlock
        helper.log("Test start")
        helper.wait_sim_time("us", 50)
        helper.hdl_force('ntb_top.u_nv_fpga_dut.u_nv_top_fpga.u_nv_top_wrapper.u_nv_top.nvjtag_sel', 1)

        helper.jtag.Reset(0)
        helper.jtag.DRScan(100, hex(0x0)) #add some delay as jtag only work when nvjtag_sel stable in real case
        helper.jtag.Reset(1)  
 

        helper.pinfo(f'j2h_unlock sequence start')
        helper.j2h_unlock()
        helper.pinfo(f'j2h_unlock sequence finish')


        helper.jtag.DRScan(100, hex(0x0)) #add some delay as jtag only work when nvjtag_sel stable in real case
        
        
        helper.log("Scenario 1: Config a region")
        reset_region_cfg()
        region_acl_reg_clear()
        region_idx = random.randint(0,7)
        [region_start, region_end] = set_a_region(region_idx)
        helper.log("region %0d, region_start = %x, region_end = %x" % (region_idx, region_start, region_end))

        # Scenario 1:  WPEN=0, WP=0(pin wp_n = 1)
        helper.log("Scenario 1, WPEN=0, WP=0(pin wp_n = 1)")
        region_acl_reg = mram.get_reg_by_name("mram_cfg_b_mtp_region_acl_" + str(region_idx) + "_0")
        region_acl_reg.update(wpen=0)
        #FIXME, now the FPGA cannot change the value of mram_wp_n, and default is 1
        #helper.hdl_force("ntb_top.mram_wp_n", 1)


        # 1.0 
        helper.log("-- 1.0 -- region %0d writeable=0, readable=0, MTP write/read, MTPR should be blocked" % region_idx)
        region_acl_reg.update(readable=0,writable=0)
        # init 100 256b elements in MRAM
        exp_addr_data_dist.clear()
        init_mram_frontdoor((region_start>>5), 100)
        helper.log("-- 1.0.0 -- check MTPR should be blocked")

        addr_list = []
        cmd_list = []
        data_list = []
        real_address = 0
        for i in range(3):
            if i == 0:
                real_address = MRAM_MTPR_BASE+region_start
            elif i == 1:
                real_address = MRAM_MTPR_BASE+region_end-1
            else:
                real_address = random.randint(MRAM_MTPR_BASE+region_start, MRAM_MTPR_BASE+region_end-1)
            fpga_rdata = helper.j2h_read(real_address)
            helper.log(f"the data read from address {real_address} is {fpga_rdata}")
        # HOW TO CHECK: read data should be different with write data(or check if read is 0, 0 means error)
            if fpga_rdata == 0:
                helper.log("MTPR is blocked, it is expected")
            else:
                helper.perror("MTPR to region%0d whose readable==0 should return an error" % region_idx)
        

        helper.log("-- 1.0.1 -- check MTP read should be blocked with readable=0")
        mtp_addr = 0
        for i in range(4):
            if i == 1:
                mtp_addr = region_start
            elif i == 2:
                mtp_addr = region_end-1
            else:
                mtp_addr = random.randint(region_start, region_end-1)#region_start+random.randint(0,32*100-1)
            helper.log("mtp_addr = %x" % mtp_addr)

            mram_mtp_read(mtp_addr, priv_id=0)
            rd = mram.mram_mtp_rport_state_0.read()
            if rd['ERROR'] != 1:
                helper.perror("Unexpected, MTP read to a readable=0 region should return an ERROR")
            mram.mram_mtp_rport_state_0.write(ERROR=1)
        
        helper.log("-- 1.0.2 -- check MTP write should be blocked with writeable=0/WPEN=0/WP=0")
        exp_dict = {}
        wr_addr_list = []
        for i in range(8):
            if i == 0:
                mtp_wr_addr = region_start
            elif i == 1:
                mtp_wr_addr = region_end-1
            elif i < 6:
                mtp_wr_addr = region_start+random.randint(0,32*100-1)
            else:
                mtp_wr_addr = random.randint(region_start, region_end-1)
            wr_addr_list.append(mtp_wr_addr)
            wr_data_list = []
            for j in range(8):
                wr_data_list.append(random.randint(0,(1<<32)-1))
            exp_dict[mtp_wr_addr&0xffffffe0] = wr_data_list
            test_api.mram_mtp_write(mtp_wr_addr, wr_data_list, rand_shuffle=1)
            rd = mram.mram_mtp_wport_state_0.read()
            helper.log("mram_mtp_wport_state_0 read result:")
            helper.log(rd)
            if rd['ERROR'] != 1:
                helper.perror("MTP write to a region with writable=0/WPEN=0/WP=0 should return an ERROR")
            mram.mram_mtp_wport_state_0.write(ERROR=1)

        for i in range(len(wr_addr_list)):
            wr_addr_list[i] = wr_addr_list[i] & 0xffffffe0
        Check_result(wr_addr_list, exp_dict, frontdoor=1,expect_fail=1)
        #check_content(exp_addr_data_dist)


        helper.log("Scenario 2: Config a region")
        reset_region_cfg()
        region_acl_reg_clear()
        region_idx = random.randint(0,7)
        [region_start, region_end] = set_a_region(region_idx)
        helper.log("region %0d, region_start = %x, region_end = %x" % (region_idx, region_start, region_end))

        # Scenario 2:  WPEN=1, WP=0(pin wp_n = 1)
        helper.log("Scenario 1, WPEN=1, WP=0(pin wp_n = 1)")
        region_acl_reg = mram.get_reg_by_name("mram_cfg_b_mtp_region_acl_" + str(region_idx) + "_0")
        region_acl_reg.update(wpen=1)
        #FIXME add the control after FPGA can control it
        #helper.hdl_force("ntb_top.mram_wp_n", 1)
        
        
        # 2.0 
        helper.log("-- 2.0 -- region %0d writeable=0, readable=0, MTP write/read, MTPR should be blocked" % region_idx)
        region_acl_reg.update(readable=0,writable=0)
        # init 100 256b elements in MRAM, not need to inti because not to change the value before
        #exp_addr_data_dist.clear()
        #init_mram_backdoor((region_start>>5), 100)
        helper.log("-- 2.0.0 -- check MTPR should be blocked")

        addr_list = []
        cmd_list = []
        data_list = []
        real_address = 0
        for i in range(3):
            if i == 0:
                real_address = MRAM_MTPR_BASE+region_start
            elif i == 1:
                real_address = MRAM_MTPR_BASE+region_end-1
            else:
                real_address = random.randint(MRAM_MTPR_BASE+region_start, MRAM_MTPR_BASE+region_end-1)
            fpga_rdata = helper.j2h_read(real_address)
        # HOW TO CHECK: read data should be different with write data(or check if read is 0, 0 means error)
            if fpga_rdata == 0:
                helper.log("MTPR is blocked, it is expected")
            else:
                helper.perror("MTPR to region%0d whose readable==0 should return an error" % region_idx)
        

        helper.log("-- 2.0.1 -- check MTP read should be blocked with readable=0")
        mtp_addr = 0
        for i in range(4):
            if i == 1:
                mtp_addr = region_start
            elif i == 2:
                mtp_addr = region_end-1
            else:
                mtp_addr = random.randint(region_start, region_end-1)#region_start+random.randint(0,32*100-1)
            helper.log("mtp_addr = %x" % mtp_addr)

            mram_mtp_read(mtp_addr, priv_id=0)
            rd = mram.mram_mtp_rport_state_0.read()
            if rd['ERROR'] != 1:
                helper.perror("Unexpected, MTP read to a readable=0 region should return an ERROR")
            mram.mram_mtp_rport_state_0.write(ERROR=1)
        
        helper.log("-- 2.0.2 -- check MTP write should be blocked with writeable=0/WPEN=1/WP=0")
        exp_dict = {}
        wr_addr_list = []
        for i in range(8):
            if i == 0:
                mtp_wr_addr = region_start
            elif i == 1:
                mtp_wr_addr = region_end-1
            elif i < 6:
                mtp_wr_addr = region_start+random.randint(0,32*100-1)
            else:
                mtp_wr_addr = random.randint(region_start, region_end-1)
            wr_addr_list.append(mtp_wr_addr)
            wr_data_list = []
            for j in range(8):
                wr_data_list.append(random.randint(0,(1<<32)-1))
            exp_dict[mtp_wr_addr&0xffffffe0] = wr_data_list
            test_api.mram_mtp_write(mtp_wr_addr, wr_data_list, rand_shuffle=1)
            rd = mram.mram_mtp_wport_state_0.read()
            if rd['ERROR'] != 1:
                helper.perror("MTP write to a region with writable=0/WPEN=1/WP=0 should return an ERROR")
            mram.mram_mtp_wport_state_0.write(ERROR=1)

        for i in range(len(wr_addr_list)):
            wr_addr_list[i] = wr_addr_list[i] & 0xffffffe0
        Check_result(wr_addr_list, exp_dict, frontdoor=1,expect_fail=1)
       # check_content(exp_addr_data_dist)

    else:
        helper.log("Scenario 0: WPEN=0, WP=1")
        # Scenario 0:  WPEN=0, WP=1(pin wp_n = 0)
        #default wp_n = 1
        reset_region_cfg()
        region_acl_reg_clear()
        region_idx = random.randint(0,7)
        [region_start, region_end] = set_a_region(region_idx)
        helper.log("region %0d, region_start = %x, region_end = %x" % (region_idx, region_start, region_end))

        helper.log("-- 0 -- WPEN=0, WP=1(pin wp_n = 0)")
        region_acl_reg = mram.get_reg_by_name("mram_cfg_b_mtp_region_acl_" + str(region_idx) + "_0")
        region_acl_reg.update(wpen=0)
        # ask Chang how to control the pin value
        helper.hdl_force("ntb_top.mram_wp_n", 0)

        # 0.0 
        helper.log("-- 0.0 -- region %0d writeable=0, readable=0, MTP write/read, MTPR should be blocked" % region_idx)
        region_acl_reg.update(readable=0,writable=0)
        # init 100 256b elements in MRAM
        exp_addr_data_dist.clear()
        # change to use frontdoor to write
        init_mram_backdoor((region_start>>5), 100)
        helper.log("-- 0.0.0 -- check MTPR should be blocked")

        addr_list = []
        cmd_list = []
        data_list = []
        for i in range(20):
            if i == 0:
                addr_list.append(MRAM_MTPR_BASE+region_start)
            elif i == 1:
                addr_list.append(MRAM_MTPR_BASE+region_end-1)
            else:
                addr_list.append(random.randint(MRAM_MTPR_BASE+region_start, MRAM_MTPR_BASE+region_end-1))
            cmd_list.append(0)
            data_list.append(random.randint(0,0xffffffff))
        [resp_data_list, resp_err_list] = helper.burst_operation(addr_list, data_list, cmd_list, priv_id=2)
        for resp_err_item in resp_err_list:
            if resp_err_item != 1:
                helper.perror("MTPR to region%0d whose readable==0 should return an error" % region_idx)
        

        helper.log("-- 0.0.1 -- check MTP read should be blocked with readable=0")
        mtp_addr = 0
        for i in range(10):
            if i == 1:
                mtp_addr = region_start
            elif i == 2:
                mtp_addr = region_end-1
            else:
                mtp_addr = random.randint(region_start, region_end-1)#region_start+random.randint(0,32*100-1)
            helper.log("mtp_addr = %x" % mtp_addr)

            mram_mtp_read(mtp_addr, priv_id=2)
            rd = mram.mram_mtp_rport_state_0.read()
            if rd['ERROR'] != 1:
                helper.perror("Unexpected, MTP read to a readable=0 region should return an ERROR")
            mram.mram_mtp_rport_state_0.write(ERROR=1)
        
        helper.log("-- 0.0.2 -- check MTP write should be blocked with writeable=0/WPEN=0/WP=1")
        exp_dict = {}
        wr_addr_list = []
        for i in range(10):
            if i == 0:
                mtp_wr_addr = region_start
            elif i == 1:
                mtp_wr_addr = region_end-1
            elif i < 6:
                mtp_wr_addr = region_start+random.randint(0,32*100-1)
            else:
                mtp_wr_addr = random.randint(region_start, region_end-1)
            wr_addr_list.append(mtp_wr_addr)
            wr_data_list = []
            for j in range(8):
                wr_data_list.append(random.randint(0,(1<<32)-1))
            exp_dict[mtp_wr_addr&0xffffffe0] = wr_data_list
            # change to use priv_id=0
            mram_mtp_write(mtp_wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)
            rd = mram.mram_mtp_wport_state_0.read()
            if rd['ERROR'] != 1:
                helper.perror("MTP write to a region with writable=0/WPEN=0/WP=1 should return an ERROR")
            mram.mram_mtp_wport_state_0.write(ERROR=1)

        for i in range(len(wr_addr_list)):
            wr_addr_list[i] = wr_addr_list[i] & 0xffffffe0
        Check_result(wr_addr_list, exp_dict, frontdoor=0,expect_fail=1)
        check_content(exp_addr_data_dist)



        
        #0.1
        helper.log("-- 0.1 -- region %0d writeable=1, readable=0, MTP write should pass, MTP read and MTPR should be blocked" % region_idx)
        region_acl_reg.update(readable=0,writable=1)
        # init 100 256b elements in MRAM
        helper.log("-- 0.1.0 -- check MTPR should be blocked")
        exp_addr_data_dist.clear()
        init_mram_backdoor((region_start>>5), 100)

        addr_list = []
        cmd_list = []
        data_list = []
        for i in range(20):
            if i == 0:
                addr_list.append(MRAM_MTPR_BASE+region_start)
            elif i == 1:
                addr_list.append(MRAM_MTPR_BASE+region_end-1)
            else:
                addr_list.append(random.randint(MRAM_MTPR_BASE+region_start, MRAM_MTPR_BASE+region_end-1))
            cmd_list.append(0)
            data_list.append(random.randint(0,0xffffffff))
        [resp_data_list, resp_err_list] = helper.burst_operation(addr_list, data_list, cmd_list, priv_id=2)
        for resp_err_item in resp_err_list:
            if resp_err_item != 1:
                helper.perror("MTPR to region%0d whose readable==0 should return an error" % region_idx)
        

        helper.log("-- 0.1.1 -- check MTP read should be blocked with readable=0")
        mtp_addr = 0
        for i in range(10):
            if i == 1:
                mtp_addr = region_start
            elif i == 2:
                mtp_addr = region_end-1
            else:
                mtp_addr = random.randint(region_start, region_end-1)#region_start+random.randint(0,32*100-1)
            helper.log("mtp_addr = %x" % mtp_addr)

            mram_mtp_read(mtp_addr, priv_id=2)
            rd = mram.mram_mtp_rport_state_0.read()
            if rd['ERROR'] != 1:
                helper.perror("Unexpected, MTP read to a readable=0 region should return an ERROR")
            mram.mram_mtp_rport_state_0.write(ERROR=1)
        
        helper.log("-- 0.1.2 -- check MTP write should pass with writeable=1/WPEN=0/WP=1")
        exp_dict = {}
        wr_addr_list = []
        for i in range(10):
            if i == 0:
                mtp_wr_addr = region_start
            elif i == 1:
                mtp_wr_addr = region_end-1
            elif i < 6:
                mtp_wr_addr = region_start+random.randint(0,32*100-1)
            else:
                mtp_wr_addr = random.randint(region_start, region_end-1)
            wr_addr_list.append(mtp_wr_addr)
            wr_data_list = []
            for j in range(8):
                tmp_wr_data = random.randint(0,(1<<32)-1)
                wr_data_list.append(tmp_wr_data)
                exp_addr_data_dist[MRAM_MTPR_BASE+(mtp_wr_addr&0xffffffe0)+4*j] = tmp_wr_data
            helper.log("For addr %x" % mtp_wr_addr)
            for k in range(len(wr_data_list)):
                helper.log("wr_data_list[%0d] = %x" % (k, wr_data_list[k]))
                
            exp_dict[mtp_wr_addr&0xffffffe0] = wr_data_list

            mram_mtp_write(mtp_wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)
            rd = mram.mram_mtp_wport_state_0.read()
            if rd['ERROR'] == 1:
                helper.perror("MTP write to a region with writable=1/WPEN=0/WP=1 should pass")
            mram.mram_mtp_wport_state_0.write(ERROR=1)

        for i in range(len(wr_addr_list)):
            wr_addr_list[i] = wr_addr_list[i] & 0xffffffe0
        Check_result(wr_addr_list, exp_dict, frontdoor=0,expect_fail=0)
        check_content(exp_addr_data_dist)



        #0.2
        helper.log("-- 0.2 -- region %0d writeable=0, readable=1, MTP write should be blocked, MTP read, MTPR should pass" % region_idx)
        region_acl_reg.update(readable=1,writable=0)
        # init 100 256b elements in MRAM
        helper.log("-- 0.2.0 -- check MTPR should pass")
        exp_addr_data_dist.clear()
        init_mram_backdoor((region_start>>5), 100)

        addr_list = []
        cmd_list = []
        data_list = []
        for i in range(20):
            if i == 0:
                addr_list.append(MRAM_MTPR_BASE+region_start)
            elif i == 1:
                addr_list.append(MRAM_MTPR_BASE+region_end-1)
            elif i < 10:
                addr_list.append(MRAM_MTPR_BASE+region_start+random.randint(0,32*100-1))
            else:
                addr_list.append(random.randint(MRAM_MTPR_BASE+region_start, MRAM_MTPR_BASE+region_end-1))
            cmd_list.append(0)
            data_list.append(random.randint(0,0xffffffff))
        [resp_data_list, resp_err_list] = helper.burst_operation(addr_list, data_list, cmd_list, priv_id=2)
        for resp_err_item in resp_err_list:
            if resp_err_item == 1:
                helper.perror("MTPR to region%0d whose readable==1 should not return an error" % region_idx)
        for i in range(len(resp_data_list)):
            if addr_list[i] < MRAM_MTPR_BASE + region_start + 32*100:
                addr_32b = addr_list[i] & 0xfffffffc
                if resp_data_list[i] != exp_addr_data_dist[addr_32b]:
                    helper.perror("MTPR Mismatch, addr: %x, exp: %x, act: %x" % (addr_32b, exp_addr_data_dist[addr_32b], resp_data_list[i]))
        

        helper.log("-- 0.2.1 -- check MTP read should pass with readable=1")
        mtp_addr = 0
        for i in range(10):
            if i == 1:
                mtp_addr = region_start
            elif i == 2:
                mtp_addr = region_end-1
            elif i < 6:
                mtp_addr = region_start+random.randint(0,32*100-1)
            else:
                mtp_addr = random.randint(region_start, region_end-1)#region_start+random.randint(0,32*100-1)
            helper.log("mtp_addr = %x" % mtp_addr)

            rd_data_list = mram_mtp_read(mtp_addr, priv_id=2)
            rd = mram.mram_mtp_rport_state_0.read()
            if rd['ERROR'] == 1:
                helper.perror("Unexpected, MTP read to a readable=1 region should not return an ERROR")
            mram.mram_mtp_rport_state_0.write(ERROR=1)

            if mtp_addr < region_start + 32*100:
                for j in range(8):
                    if exp_addr_data_dist[MRAM_MTPR_BASE+(mtp_addr&0xffffffe0)+j*4] != rd_data_list[j]:
                        helper.perror("MTP rd Mismatch, addr: %x, exp: %x, act: %x" % (MRAM_MTPR_BASE+(mtp_addr&0xffffffe0)+j*4, exp_addr_data_dist[MRAM_MTPR_BASE+(mtp_addr&0xffffffe0)+j*4], rd_data_list[j]))
                

        helper.log("-- 0.2.2 -- check MTP write should be block with writeable=0/WPEN=0/WP=1")
        exp_dict = {}
        wr_addr_list = []
        for i in range(10):
            if i == 0:
                mtp_wr_addr = region_start
            elif i == 1:
                mtp_wr_addr = region_end-1
            elif i < 6:
                mtp_wr_addr = region_start+random.randint(0,32*100-1)
            else:
                mtp_wr_addr = random.randint(region_start, region_end-1)
            wr_addr_list.append(mtp_wr_addr)
            wr_data_list = []
            for j in range(8):
                tmp_wr_data = random.randint(0,(1<<32)-1)
                wr_data_list.append(tmp_wr_data)
            exp_dict[mtp_wr_addr&0xffffffe0] = wr_data_list

            mram_mtp_write(mtp_wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)
            rd = mram.mram_mtp_wport_state_0.read()
            if rd['ERROR'] != 1:
                helper.perror("MTP write to a region with writable=0/WPEN=0/WP=1 should return an ERROR")
            mram.mram_mtp_wport_state_0.write(ERROR=1)

        for i in range(len(wr_addr_list)):
            wr_addr_list[i] = wr_addr_list[i] & 0xffffffe0
        Check_result(wr_addr_list, exp_dict, frontdoor=0,expect_fail=1)
        check_content(exp_addr_data_dist)



        #0.3
        helper.log("-- 0.3 -- region %0d writeable=1, readable=1, MTP write, MTP read, MTPR should pass" % region_idx)
        region_acl_reg.update(readable=1,writable=1)
        # init 100 256b elements in MRAM
        helper.log("-- 0.3.0 -- check MTPR should pass")
        exp_addr_data_dist.clear()
        init_mram_backdoor((region_start>>5), 100)

        addr_list = []
        cmd_list = []
        data_list = []
        for i in range(20):
            if i == 0:
                addr_list.append(MRAM_MTPR_BASE+region_start)
            elif i == 1:
                addr_list.append(MRAM_MTPR_BASE+region_end-1)
            elif i < 10:
                addr_list.append(MRAM_MTPR_BASE+region_start+random.randint(0,32*100-1))
            else:
                addr_list.append(random.randint(MRAM_MTPR_BASE+region_start, MRAM_MTPR_BASE+region_end-1))
            cmd_list.append(0)
            data_list.append(random.randint(0,0xffffffff))
        [resp_data_list, resp_err_list] = helper.burst_operation(addr_list, data_list, cmd_list, priv_id=2)
        for resp_err_item in resp_err_list:
            if resp_err_item == 1:
                helper.perror("MTPR to region%0d whose readable==1 should not return an error" % region_idx)
        for i in range(len(resp_data_list)):
            if addr_list[i] < MRAM_MTPR_BASE + region_start + 32*100:
                addr_32b = addr_list[i] & 0xfffffffc
                if resp_data_list[i] != exp_addr_data_dist[addr_32b]:
                    helper.perror("MTPR Mismatch, addr: %x, exp: %x, act: %x" % (addr_32b, exp_addr_data_dist[addr_32b], resp_data_list[i]))
        

        helper.log("-- 0.3.1 -- check MTP read should pass with readable=1")
        mtp_addr = 0
        for i in range(10):
            if i == 1:
                mtp_addr = region_start
            elif i == 2:
                mtp_addr = region_end-1
            elif i < 6:
                mtp_addr = region_start+random.randint(0,32*100-1)
            else:
                mtp_addr = random.randint(region_start, region_end-1)#region_start+random.randint(0,32*100-1)
            helper.log("mtp_addr = %x" % mtp_addr)

            rd_data_list = mram_mtp_read(mtp_addr, priv_id=2)
            rd = mram.mram_mtp_rport_state_0.read()
            if rd['ERROR'] == 1:
                helper.perror("Unexpected, MTP read to a readable=1 region should not return an ERROR")
            mram.mram_mtp_rport_state_0.write(ERROR=1)

            if mtp_addr < region_start + 32*100:
                for j in range(8):
                    if exp_addr_data_dist[MRAM_MTPR_BASE+(mtp_addr&0xffffffe0)+j*4] != rd_data_list[j]:
                        helper.perror("MTP rd Mismatch, addr: %x, exp: %x, act: %x" % (MRAM_MTPR_BASE+(mtp_addr&0xffffffe0)+j*4, exp_addr_data_dist[MRAM_MTPR_BASE+(mtp_addr&0xffffffe0)+j*4], rd_data_list[j]))
                

        helper.log("-- 0.3.2 -- check MTP write should pass with writeable=1/WPEN=0/WP=1")
        exp_dict = {}
        wr_addr_list = []
        for i in range(10):
            if i == 0:
                mtp_wr_addr = region_start
            elif i == 1:
                mtp_wr_addr = region_end-1
            elif i < 6:
                mtp_wr_addr = region_start+random.randint(0,32*100-1)
            else:
                mtp_wr_addr = random.randint(region_start, region_end-1)
            wr_addr_list.append(mtp_wr_addr)
            wr_data_list = []
            for j in range(8):
                tmp_wr_data = random.randint(0,(1<<32)-1)
                wr_data_list.append(tmp_wr_data)
                exp_addr_data_dist[MRAM_MTPR_BASE+(mtp_wr_addr&0xffffffe0)+4*j] = tmp_wr_data
            exp_dict[mtp_wr_addr&0xffffffe0] = wr_data_list

            mram_mtp_write(mtp_wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)
            rd = mram.mram_mtp_wport_state_0.read()
            if rd['ERROR'] == 1:
                helper.perror("MTP write to a region with writable=1/WPEN=0/WP=1 should pass")
            mram.mram_mtp_wport_state_0.write(ERROR=1)
            

        for i in range(len(wr_addr_list)):
            wr_addr_list[i] = wr_addr_list[i] & 0xffffffe0
        Check_result(wr_addr_list, exp_dict, frontdoor=0,expect_fail=0)
        check_content(exp_addr_data_dist)

   


        helper.log("Scenario 1: Config a region")
        reset_region_cfg()
        region_acl_reg_clear()
        region_idx = random.randint(0,7)
        [region_start, region_end] = set_a_region(region_idx)
        helper.log("region %0d, region_start = %x, region_end = %x" % (region_idx, region_start, region_end))

        # Scenario 1:  WPEN=0, WP=0(pin wp_n = 1)
        helper.log("Scenario 1, WPEN=0, WP=0(pin wp_n = 1)")
        region_acl_reg = mram.get_reg_by_name("mram_cfg_b_mtp_region_acl_" + str(region_idx) + "_0")
        region_acl_reg.update(wpen=0)
        helper.hdl_force("ntb_top.mram_wp_n", 1)


        # 1.0 
        helper.log("-- 1.0 -- region %0d writeable=0, readable=0, MTP write/read, MTPR should be blocked" % region_idx)
        region_acl_reg.update(readable=0,writable=0)
        # init 100 256b elements in MRAM
        exp_addr_data_dist.clear()
        init_mram_backdoor((region_start>>5), 100)
        helper.log("-- 1.0.0 -- check MTPR should be blocked")

        addr_list = []
        cmd_list = []
        data_list = []
        for i in range(20):
            if i == 0:
                addr_list.append(MRAM_MTPR_BASE+region_start)
            elif i == 1:
                addr_list.append(MRAM_MTPR_BASE+region_end-1)
            else:
                addr_list.append(random.randint(MRAM_MTPR_BASE+region_start, MRAM_MTPR_BASE+region_end-1))
            cmd_list.append(0)
            data_list.append(random.randint(0,0xffffffff))
        # HOW TO CHECK: read data should be different with write data(or check if read is 0, 0 means error)
        [resp_data_list, resp_err_list] = helper.burst_operation(addr_list, data_list, cmd_list, priv_id=2)
        for resp_err_item in resp_err_list:
            if resp_err_item != 1:
                helper.perror("MTPR to region%0d whose readable==0 should return an error" % region_idx)
        

        helper.log("-- 1.0.1 -- check MTP read should be blocked with readable=0")
        mtp_addr = 0
        for i in range(10):
            if i == 1:
                mtp_addr = region_start
            elif i == 2:
                mtp_addr = region_end-1
            else:
                mtp_addr = random.randint(region_start, region_end-1)#region_start+random.randint(0,32*100-1)
            helper.log("mtp_addr = %x" % mtp_addr)

            mram_mtp_read(mtp_addr, priv_id=2)
            rd = mram.mram_mtp_rport_state_0.read()
            if rd['ERROR'] != 1:
                helper.perror("Unexpected, MTP read to a readable=0 region should return an ERROR")
            mram.mram_mtp_rport_state_0.write(ERROR=1)
        
        helper.log("-- 1.0.2 -- check MTP write should be blocked with writeable=0/WPEN=0/WP=0")
        exp_dict = {}
        wr_addr_list = []
        for i in range(10):
            if i == 0:
                mtp_wr_addr = region_start
            elif i == 1:
                mtp_wr_addr = region_end-1
            elif i < 6:
                mtp_wr_addr = region_start+random.randint(0,32*100-1)
            else:
                mtp_wr_addr = random.randint(region_start, region_end-1)
            wr_addr_list.append(mtp_wr_addr)
            wr_data_list = []
            for j in range(8):
                wr_data_list.append(random.randint(0,(1<<32)-1))
            exp_dict[mtp_wr_addr&0xffffffe0] = wr_data_list
            mram_mtp_write(mtp_wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)
            rd = mram.mram_mtp_wport_state_0.read()
            if rd['ERROR'] != 1:
                helper.perror("MTP write to a region with writable=0/WPEN=0/WP=0 should return an ERROR")
            mram.mram_mtp_wport_state_0.write(ERROR=1)

        for i in range(len(wr_addr_list)):
            wr_addr_list[i] = wr_addr_list[i] & 0xffffffe0
        Check_result(wr_addr_list, exp_dict, frontdoor=0,expect_fail=1)
        check_content(exp_addr_data_dist)



        
        #1.1
        helper.log("-- 1.1 -- region %0d writeable=1, readable=0, MTP write should pass, MTP read and MTPR should be blocked" % region_idx)
        region_acl_reg.update(readable=0,writable=1)
        # init 100 256b elements in MRAM
        helper.log("-- 1.1.0 -- check MTPR should be blocked")
        exp_addr_data_dist.clear()
        init_mram_backdoor((region_start>>5), 100)

        addr_list = []
        cmd_list = []
        data_list = []
        for i in range(20):
            if i == 0:
                addr_list.append(MRAM_MTPR_BASE+region_start)
            elif i == 1:
                addr_list.append(MRAM_MTPR_BASE+region_end-1)
            else:
                addr_list.append(random.randint(MRAM_MTPR_BASE+region_start, MRAM_MTPR_BASE+region_end-1))
            cmd_list.append(0)
            data_list.append(random.randint(0,0xffffffff))
        [resp_data_list, resp_err_list] = helper.burst_operation(addr_list, data_list, cmd_list, priv_id=2)
        for resp_err_item in resp_err_list:
            if resp_err_item != 1:
                helper.perror("MTPR to region%0d whose readable==0 should return an error" % region_idx)
        

        helper.log("-- 1.1.1 -- check MTP read should be blocked with readable=0")
        mtp_addr = 0
        for i in range(10):
            if i == 1:
                mtp_addr = region_start
            elif i == 2:
                mtp_addr = region_end-1
            else:
                mtp_addr = random.randint(region_start, region_end-1)#region_start+random.randint(0,32*100-1)
            helper.log("mtp_addr = %x" % mtp_addr)

            mram_mtp_read(mtp_addr, priv_id=2)
            rd = mram.mram_mtp_rport_state_0.read()
            if rd['ERROR'] != 1:
                helper.perror("Unexpected, MTP read to a readable=0 region should return an ERROR")
            mram.mram_mtp_rport_state_0.write(ERROR=1)
        
        helper.log("-- 1.1.2 -- check MTP write should pass with writeable=1/WPEN=0/WP=0")
        exp_dict = {}
        wr_addr_list = []
        for i in range(10):
            if i == 0:
                mtp_wr_addr = region_start
            elif i == 1:
                mtp_wr_addr = region_end-1
            elif i < 6:
                mtp_wr_addr = region_start+random.randint(0,32*100-1)
            else:
                mtp_wr_addr = random.randint(region_start, region_end-1)
            wr_addr_list.append(mtp_wr_addr)
            wr_data_list = []
            for j in range(8):
                tmp_wr_data = random.randint(0,(1<<32)-1)
                wr_data_list.append(tmp_wr_data)
                exp_addr_data_dist[MRAM_MTPR_BASE+(mtp_wr_addr&0xffffffe0)+4*j] = tmp_wr_data
            exp_dict[mtp_wr_addr&0xffffffe0] = wr_data_list

            mram_mtp_write(mtp_wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)
            rd = mram.mram_mtp_wport_state_0.read()
            if rd['ERROR'] == 1:
                helper.perror("MTP write to a region with writable=1/WPEN=0/WP=0 should pass")
            mram.mram_mtp_wport_state_0.write(ERROR=1)

        for i in range(len(wr_addr_list)):
            wr_addr_list[i] = wr_addr_list[i] & 0xffffffe0
        Check_result(wr_addr_list, exp_dict, frontdoor=0,expect_fail=0)
        check_content(exp_addr_data_dist)



        #1.2
        helper.log("-- 1.2 -- region %0d writeable=0, readable=1, MTP write should be blocked, MTP read, MTPR should pass" % region_idx)
        region_acl_reg.update(readable=1,writable=0)
        # init 100 256b elements in MRAM
        helper.log("-- 1.2.0 -- check MTPR should pass")
        exp_addr_data_dist.clear()
        init_mram_backdoor((region_start>>5), 100)

        addr_list = []
        cmd_list = []
        data_list = []
        for i in range(20):
            if i == 0:
                addr_list.append(MRAM_MTPR_BASE+region_start)
            elif i == 1:
                addr_list.append(MRAM_MTPR_BASE+region_end-1)
            elif i < 10:
                addr_list.append(MRAM_MTPR_BASE+region_start+random.randint(0,32*100-1))
            else:
                addr_list.append(random.randint(MRAM_MTPR_BASE+region_start, MRAM_MTPR_BASE+region_end-1))
            cmd_list.append(0)
            data_list.append(random.randint(0,0xffffffff))
        [resp_data_list, resp_err_list] = helper.burst_operation(addr_list, data_list, cmd_list, priv_id=2)
        for resp_err_item in resp_err_list:
            if resp_err_item == 1:
                helper.perror("MTPR to region%0d whose readable==1 should not return an error" % region_idx)
        for i in range(len(resp_data_list)):
            if addr_list[i] < MRAM_MTPR_BASE + region_start + 32*100:
                addr_32b = addr_list[i] & 0xfffffffc
                if resp_data_list[i] != exp_addr_data_dist[addr_32b]:
                    helper.perror("MTPR Mismatch, addr: %x, exp: %x, act: %x" % (addr_32b, exp_addr_data_dist[addr_32b], resp_data_list[i]))
        

        helper.log("-- 1.2.1 -- check MTP read should pass with readable=1")
        mtp_addr = 0
        for i in range(10):
            if i == 1:
                mtp_addr = region_start
            elif i == 2:
                mtp_addr = region_end-1
            elif i < 6:
                mtp_addr = region_start+random.randint(0,32*100-1)
            else:
                mtp_addr = random.randint(region_start, region_end-1)#region_start+random.randint(0,32*100-1)
            helper.log("mtp_addr = %x" % mtp_addr)

            rd_data_list = mram_mtp_read(mtp_addr, priv_id=2)
            rd = mram.mram_mtp_rport_state_0.read()
            if rd['ERROR'] == 1:
                helper.perror("Unexpected, MTP read to a readable=1 region should not return an ERROR")
            mram.mram_mtp_rport_state_0.write(ERROR=1)

            if mtp_addr < region_start + 32*100:
                for j in range(8):
                    if exp_addr_data_dist[MRAM_MTPR_BASE+(mtp_addr&0xffffffe0)+j*4] != rd_data_list[j]:
                        helper.perror("MTP rd Mismatch, addr: %x, exp: %x, act: %x" % (MRAM_MTPR_BASE+(mtp_addr&0xffffffe0)+j*4, exp_addr_data_dist[MRAM_MTPR_BASE+(mtp_addr&0xffffffe0)+j*4], rd_data_list[j]))
                

        helper.log("-- 1.2.2 -- check MTP write should be block with writeable=0/WPEN=0/WP=0")
        exp_dict = {}
        wr_addr_list = []
        for i in range(10):
            if i == 0:
                mtp_wr_addr = region_start
            elif i == 1:
                mtp_wr_addr = region_end-1
            elif i < 6:
                mtp_wr_addr = region_start+random.randint(0,32*100-1)
            else:
                mtp_wr_addr = random.randint(region_start, region_end-1)
            wr_addr_list.append(mtp_wr_addr)
            wr_data_list = []
            for j in range(8):
                tmp_wr_data = random.randint(0,(1<<32)-1)
                wr_data_list.append(tmp_wr_data)
            exp_dict[mtp_wr_addr&0xffffffe0] = wr_data_list

            mram_mtp_write(mtp_wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)
            rd = mram.mram_mtp_wport_state_0.read()
            if rd['ERROR'] != 1:
                helper.perror("MTP write to a region with writable=0/WPEN=0/WP=0 should return an ERROR")
            mram.mram_mtp_wport_state_0.write(ERROR=1)

        for i in range(len(wr_addr_list)):
            wr_addr_list[i] = wr_addr_list[i] & 0xffffffe0
        Check_result(wr_addr_list, exp_dict, frontdoor=0,expect_fail=1)
        check_content(exp_addr_data_dist)



        #1.3
        helper.log("-- 1.3 -- region %0d writeable=1, readable=1, MTP write, MTP read, MTPR should pass" % region_idx)
        region_acl_reg.update(readable=1,writable=1)
        # init 100 256b elements in MRAM
        helper.log("-- 1.3.0 -- check MTPR should pass")
        exp_addr_data_dist.clear()
        init_mram_backdoor((region_start>>5), 100)

        addr_list = []
        cmd_list = []
        data_list = []
        for i in range(20):
            if i == 0:
                addr_list.append(MRAM_MTPR_BASE+region_start)
            elif i == 1:
                addr_list.append(MRAM_MTPR_BASE+region_end-1)
            elif i < 10:
                addr_list.append(MRAM_MTPR_BASE+region_start+random.randint(0,32*100-1))
            else:
                addr_list.append(random.randint(MRAM_MTPR_BASE+region_start, MRAM_MTPR_BASE+region_end-1))
            cmd_list.append(0)
            data_list.append(random.randint(0,0xffffffff))
        [resp_data_list, resp_err_list] = helper.burst_operation(addr_list, data_list, cmd_list, priv_id=2)
        for resp_err_item in resp_err_list:
            if resp_err_item == 1:
                helper.perror("MTPR to region%0d whose readable==1 should not return an error" % region_idx)
        for i in range(len(resp_data_list)):
            if addr_list[i] < MRAM_MTPR_BASE + region_start + 32*100:
                addr_32b = addr_list[i] & 0xfffffffc
                if resp_data_list[i] != exp_addr_data_dist[addr_32b]:
                    helper.perror("MTPR Mismatch, addr: %x, exp: %x, act: %x" % (addr_32b, exp_addr_data_dist[addr_32b], resp_data_list[i]))
        

        helper.log("-- 1.3.1 -- check MTP read should pass with readable=1")
        mtp_addr = 0
        for i in range(10):
            if i == 1:
                mtp_addr = region_start
            elif i == 2:
                mtp_addr = region_end-1
            elif i < 6:
                mtp_addr = region_start+random.randint(0,32*100-1)
            else:
                mtp_addr = random.randint(region_start, region_end-1)#region_start+random.randint(0,32*100-1)
            helper.log("mtp_addr = %x" % mtp_addr)

            rd_data_list = mram_mtp_read(mtp_addr, priv_id=2)
            rd = mram.mram_mtp_rport_state_0.read()
            if rd['ERROR'] == 1:
                helper.perror("Unexpected, MTP read to a readable=1 region should not return an ERROR")
            mram.mram_mtp_rport_state_0.write(ERROR=1)

            if mtp_addr < region_start + 32*100:
                for j in range(8):
                    if exp_addr_data_dist[MRAM_MTPR_BASE+(mtp_addr&0xffffffe0)+j*4] != rd_data_list[j]:
                        helper.perror("MTP rd Mismatch, addr: %x, exp: %x, act: %x" % (MRAM_MTPR_BASE+(mtp_addr&0xffffffe0)+j*4, exp_addr_data_dist[MRAM_MTPR_BASE+(mtp_addr&0xffffffe0)+j*4], rd_data_list[j]))
                

        helper.log("-- 1.3.2 -- check MTP write should pass with writeable=1/WPEN=0/WP=0")
        exp_dict = {}
        wr_addr_list = []
        for i in range(10):
            if i == 0:
                mtp_wr_addr = region_start
            elif i == 1:
                mtp_wr_addr = region_end-1
            elif i < 6:
                mtp_wr_addr = region_start+random.randint(0,32*100-1)
            else:
                mtp_wr_addr = random.randint(region_start, region_end-1)
            wr_addr_list.append(mtp_wr_addr)
            wr_data_list = []
            for j in range(8):
                tmp_wr_data = random.randint(0,(1<<32)-1)
                wr_data_list.append(tmp_wr_data)
                exp_addr_data_dist[MRAM_MTPR_BASE+(mtp_wr_addr&0xffffffe0)+4*j] = tmp_wr_data
            exp_dict[mtp_wr_addr&0xffffffe0] = wr_data_list

            mram_mtp_write(mtp_wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)
            rd = mram.mram_mtp_wport_state_0.read()
            if rd['ERROR'] == 1:
                helper.perror("MTP write to a region with writable=1/WPEN=0/WP=0 should pass")
            mram.mram_mtp_wport_state_0.write(ERROR=1)

        for i in range(len(wr_addr_list)):
            wr_addr_list[i] = wr_addr_list[i] & 0xffffffe0
        Check_result(wr_addr_list, exp_dict, frontdoor=0,expect_fail=0)
        check_content(exp_addr_data_dist)


        helper.log("Scenario 2: Config a region")
        reset_region_cfg()
        region_acl_reg_clear()
        region_idx = random.randint(0,7)
        [region_start, region_end] = set_a_region(region_idx)
        helper.log("region %0d, region_start = %x, region_end = %x" % (region_idx, region_start, region_end))

        # Scenario 2:  WPEN=1, WP=0(pin wp_n = 1)
        helper.log("Scenario 1, WPEN=1, WP=0(pin wp_n = 1)")
        region_acl_reg = mram.get_reg_by_name("mram_cfg_b_mtp_region_acl_" + str(region_idx) + "_0")
        region_acl_reg.update(wpen=1)
        helper.hdl_force("ntb_top.mram_wp_n", 1)
        
        
        # 2.0 
        helper.log("-- 2.0 -- region %0d writeable=0, readable=0, MTP write/read, MTPR should be blocked" % region_idx)
        region_acl_reg.update(readable=0,writable=0)
        # init 100 256b elements in MRAM
        exp_addr_data_dist.clear()
        init_mram_backdoor((region_start>>5), 100)
        helper.log("-- 2.0.0 -- check MTPR should be blocked")

        addr_list = []
        cmd_list = []
        data_list = []
        for i in range(20):
            if i == 0:
                addr_list.append(MRAM_MTPR_BASE+region_start)
            elif i == 1:
                addr_list.append(MRAM_MTPR_BASE+region_end-1)
            else:
                addr_list.append(random.randint(MRAM_MTPR_BASE+region_start, MRAM_MTPR_BASE+region_end-1))
            cmd_list.append(0)
            data_list.append(random.randint(0,0xffffffff))
        [resp_data_list, resp_err_list] = helper.burst_operation(addr_list, data_list, cmd_list, priv_id=2)
        for resp_err_item in resp_err_list:
            if resp_err_item != 1:
                helper.perror("MTPR to region%0d whose readable==0 should return an error" % region_idx)
        

        helper.log("-- 2.0.1 -- check MTP read should be blocked with readable=0")
        mtp_addr = 0
        for i in range(10):
            if i == 1:
                mtp_addr = region_start
            elif i == 2:
                mtp_addr = region_end-1
            else:
                mtp_addr = random.randint(region_start, region_end-1)#region_start+random.randint(0,32*100-1)
            helper.log("mtp_addr = %x" % mtp_addr)

            mram_mtp_read(mtp_addr, priv_id=2)
            rd = mram.mram_mtp_rport_state_0.read()
            if rd['ERROR'] != 1:
                helper.perror("Unexpected, MTP read to a readable=0 region should return an ERROR")
            mram.mram_mtp_rport_state_0.write(ERROR=1)
        
        helper.log("-- 2.0.2 -- check MTP write should be blocked with writeable=0/WPEN=1/WP=0")
        exp_dict = {}
        wr_addr_list = []
        for i in range(10):
            if i == 0:
                mtp_wr_addr = region_start
            elif i == 1:
                mtp_wr_addr = region_end-1
            elif i < 6:
                mtp_wr_addr = region_start+random.randint(0,32*100-1)
            else:
                mtp_wr_addr = random.randint(region_start, region_end-1)
            wr_addr_list.append(mtp_wr_addr)
            wr_data_list = []
            for j in range(8):
                wr_data_list.append(random.randint(0,(1<<32)-1))
            exp_dict[mtp_wr_addr&0xffffffe0] = wr_data_list
            mram_mtp_write(mtp_wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)
            rd = mram.mram_mtp_wport_state_0.read()
            if rd['ERROR'] != 1:
                helper.perror("MTP write to a region with writable=0/WPEN=1/WP=0 should return an ERROR")
            mram.mram_mtp_wport_state_0.write(ERROR=1)

        for i in range(len(wr_addr_list)):
            wr_addr_list[i] = wr_addr_list[i] & 0xffffffe0
        Check_result(wr_addr_list, exp_dict, frontdoor=0,expect_fail=1)
        check_content(exp_addr_data_dist)



        
        #1.1
        helper.log("-- 2.1 -- region %0d writeable=1, readable=0, MTP write should pass, MTP read and MTPR should be blocked" % region_idx)
        region_acl_reg.update(readable=0,writable=1)
        # init 100 256b elements in MRAM
        helper.log("-- 2.1.0 -- check MTPR should be blocked")
        exp_addr_data_dist.clear()
        init_mram_backdoor((region_start>>5), 100)

        addr_list = []
        cmd_list = []
        data_list = []
        for i in range(20):
            if i == 0:
                addr_list.append(MRAM_MTPR_BASE+region_start)
            elif i == 1:
                addr_list.append(MRAM_MTPR_BASE+region_end-1)
            else:
                addr_list.append(random.randint(MRAM_MTPR_BASE+region_start, MRAM_MTPR_BASE+region_end-1))
            cmd_list.append(0)
            data_list.append(random.randint(0,0xffffffff))
        [resp_data_list, resp_err_list] = helper.burst_operation(addr_list, data_list, cmd_list, priv_id=2)
        for resp_err_item in resp_err_list:
            if resp_err_item != 1:
                helper.perror("MTPR to region%0d whose readable==0 should return an error" % region_idx)
        

        helper.log("-- 2.1.1 -- check MTP read should be blocked with readable=0")
        mtp_addr = 0
        for i in range(10):
            if i == 1:
                mtp_addr = region_start
            elif i == 2:
                mtp_addr = region_end-1
            else:
                mtp_addr = random.randint(region_start, region_end-1)#region_start+random.randint(0,32*100-1)
            helper.log("mtp_addr = %x" % mtp_addr)

            mram_mtp_read(mtp_addr, priv_id=2)
            rd = mram.mram_mtp_rport_state_0.read()
            if rd['ERROR'] != 1:
                helper.perror("Unexpected, MTP read to a readable=0 region should return an ERROR")
            mram.mram_mtp_rport_state_0.write(ERROR=1)
        
        helper.log("-- 2.1.2 -- check MTP write should pass with writeable=1/WPEN=1/WP=0")
        exp_dict = {}
        wr_addr_list = []
        for i in range(10):
            if i == 0:
                mtp_wr_addr = region_start
            elif i == 1:
                mtp_wr_addr = region_end-1
            elif i < 6:
                mtp_wr_addr = region_start+random.randint(0,32*100-1)
            else:
                mtp_wr_addr = random.randint(region_start, region_end-1)
            wr_addr_list.append(mtp_wr_addr)
            wr_data_list = []
            for j in range(8):
                tmp_wr_data = random.randint(0,(1<<32)-1)
                wr_data_list.append(tmp_wr_data)
                exp_addr_data_dist[MRAM_MTPR_BASE+(mtp_wr_addr&0xffffffe0)+4*j] = tmp_wr_data
            exp_dict[mtp_wr_addr&0xffffffe0] = wr_data_list

            mram_mtp_write(mtp_wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)
            rd = mram.mram_mtp_wport_state_0.read()
            if rd['ERROR'] == 1:
                helper.perror("MTP write to a region with writable=1/WPEN=1/WP=0 should pass")
            mram.mram_mtp_wport_state_0.write(ERROR=1)

        for i in range(len(wr_addr_list)):
            wr_addr_list[i] = wr_addr_list[i] & 0xffffffe0
        Check_result(wr_addr_list, exp_dict, frontdoor=0,expect_fail=0)
        check_content(exp_addr_data_dist)



        #2.2
        helper.log("-- 2.2 -- region %0d writeable=0, readable=1, MTP write should be blocked, MTP read, MTPR should pass" % region_idx)
        region_acl_reg.update(readable=1,writable=0)
        # init 100 256b elements in MRAM
        helper.log("-- 2.2.0 -- check MTPR should pass")
        exp_addr_data_dist.clear()
        init_mram_backdoor((region_start>>5), 100)

        addr_list = []
        cmd_list = []
        data_list = []
        for i in range(20):
            if i == 0:
                addr_list.append(MRAM_MTPR_BASE+region_start)
            elif i == 1:
                addr_list.append(MRAM_MTPR_BASE+region_end-1)
            elif i < 10:
                addr_list.append(MRAM_MTPR_BASE+region_start+random.randint(0,32*100-1))
            else:
                addr_list.append(random.randint(MRAM_MTPR_BASE+region_start, MRAM_MTPR_BASE+region_end-1))
            cmd_list.append(0)
            data_list.append(random.randint(0,0xffffffff))
        [resp_data_list, resp_err_list] = helper.burst_operation(addr_list, data_list, cmd_list, priv_id=2)
        for resp_err_item in resp_err_list:
            if resp_err_item == 1:
                helper.perror("MTPR to region%0d whose readable==1 should not return an error" % region_idx)
        for i in range(len(resp_data_list)):
            if addr_list[i] < MRAM_MTPR_BASE + region_start + 32*100:
                addr_32b = addr_list[i] & 0xfffffffc
                if resp_data_list[i] != exp_addr_data_dist[addr_32b]:
                    helper.perror("MTPR Mismatch, addr: %x, exp: %x, act: %x" % (addr_32b, exp_addr_data_dist[addr_32b], resp_data_list[i]))
        

        helper.log("-- 2.2.1 -- check MTP read should pass with readable=1")
        mtp_addr = 0
        for i in range(10):
            if i == 1:
                mtp_addr = region_start
            elif i == 2:
                mtp_addr = region_end-1
            elif i < 6:
                mtp_addr = region_start+random.randint(0,32*100-1)
            else:
                mtp_addr = random.randint(region_start, region_end-1)#region_start+random.randint(0,32*100-1)
            helper.log("mtp_addr = %x" % mtp_addr)

            rd_data_list = mram_mtp_read(mtp_addr, priv_id=2)
            rd = mram.mram_mtp_rport_state_0.read()
            if rd['ERROR'] == 1:
                helper.perror("Unexpected, MTP read to a readable=1 region should not return an ERROR")
            mram.mram_mtp_rport_state_0.write(ERROR=1)

            if mtp_addr < region_start + 32*100:
                for j in range(8):
                    if exp_addr_data_dist[MRAM_MTPR_BASE+(mtp_addr&0xffffffe0)+j*4] != rd_data_list[j]:
                        helper.perror("MTP rd Mismatch, addr: %x, exp: %x, act: %x" % (MRAM_MTPR_BASE+(mtp_addr&0xffffffe0)+j*4, exp_addr_data_dist[MRAM_MTPR_BASE+(mtp_addr&0xffffffe0)+j*4], rd_data_list[j]))
                

        helper.log("-- 2.2.2 -- check MTP write should be block with writeable=0/WPEN=1/WP=0")
        exp_dict = {}
        wr_addr_list = []
        for i in range(10):
            if i == 0:
                mtp_wr_addr = region_start
            elif i == 1:
                mtp_wr_addr = region_end-1
            elif i < 6:
                mtp_wr_addr = region_start+random.randint(0,32*100-1)
            else:
                mtp_wr_addr = random.randint(region_start, region_end-1)
            wr_addr_list.append(mtp_wr_addr)
            wr_data_list = []
            for j in range(8):
                tmp_wr_data = random.randint(0,(1<<32)-1)
                wr_data_list.append(tmp_wr_data)
            exp_dict[mtp_wr_addr&0xffffffe0] = wr_data_list

            mram_mtp_write(mtp_wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)
            rd = mram.mram_mtp_wport_state_0.read()
            if rd['ERROR'] != 1:
                helper.perror("MTP write to a region with writable=0/WPEN=1/WP=0 should return an ERROR")
            mram.mram_mtp_wport_state_0.write(ERROR=1)

        for i in range(len(wr_addr_list)):
            wr_addr_list[i] = wr_addr_list[i] & 0xffffffe0
        Check_result(wr_addr_list, exp_dict, frontdoor=0,expect_fail=1)
        check_content(exp_addr_data_dist)



        #2.3
        helper.log("-- 2.3 -- region %0d writeable=1, readable=1, MTP write, MTP read, MTPR should pass" % region_idx)
        region_acl_reg.update(readable=1,writable=1)
        # init 100 256b elements in MRAM
        helper.log("-- 2.3.0 -- check MTPR should pass")
        exp_addr_data_dist.clear()
        init_mram_backdoor((region_start>>5), 100)

        addr_list = []
        cmd_list = []
        data_list = []
        for i in range(20):
            if i == 0:
                addr_list.append(MRAM_MTPR_BASE+region_start)
            elif i == 1:
                addr_list.append(MRAM_MTPR_BASE+region_end-1)
            elif i < 10:
                addr_list.append(MRAM_MTPR_BASE+region_start+random.randint(0,32*100-1))
            else:
                addr_list.append(random.randint(MRAM_MTPR_BASE+region_start, MRAM_MTPR_BASE+region_end-1))
            cmd_list.append(0)
            data_list.append(random.randint(0,0xffffffff))
        [resp_data_list, resp_err_list] = helper.burst_operation(addr_list, data_list, cmd_list, priv_id=2)
        for resp_err_item in resp_err_list:
            if resp_err_item == 1:
                helper.perror("MTPR to region%0d whose readable==1 should not return an error" % region_idx)
        for i in range(len(resp_data_list)):
            if addr_list[i] < MRAM_MTPR_BASE + region_start + 32*100:
                addr_32b = addr_list[i] & 0xfffffffc
                if resp_data_list[i] != exp_addr_data_dist[addr_32b]:
                    helper.perror("MTPR Mismatch, addr: %x, exp: %x, act: %x" % (addr_32b, exp_addr_data_dist[addr_32b], resp_data_list[i]))
        

        helper.log("-- 2.3.1 -- check MTP read should pass with readable=1")
        mtp_addr = 0
        for i in range(10):
            if i == 1:
                mtp_addr = region_start
            elif i == 2:
                mtp_addr = region_end-1
            elif i < 6:
                mtp_addr = region_start+random.randint(0,32*100-1)
            else:
                mtp_addr = random.randint(region_start, region_end-1)#region_start+random.randint(0,32*100-1)
            helper.log("mtp_addr = %x" % mtp_addr)

            rd_data_list = mram_mtp_read(mtp_addr, priv_id=2)
            rd = mram.mram_mtp_rport_state_0.read()
            if rd['ERROR'] == 1:
                helper.perror("Unexpected, MTP read to a readable=1 region should not return an ERROR")
            mram.mram_mtp_rport_state_0.write(ERROR=1)

            if mtp_addr < region_start + 32*100:
                for j in range(8):
                    if exp_addr_data_dist[MRAM_MTPR_BASE+(mtp_addr&0xffffffe0)+j*4] != rd_data_list[j]:
                        helper.perror("MTP rd Mismatch, addr: %x, exp: %x, act: %x" % (MRAM_MTPR_BASE+(mtp_addr&0xffffffe0)+j*4, exp_addr_data_dist[MRAM_MTPR_BASE+(mtp_addr&0xffffffe0)+j*4], rd_data_list[j]))
                

        helper.log("-- 2.3.2 -- check MTP write should pass with writeable=1/WPEN=1/WP=0")
        exp_dict = {}
        wr_addr_list = []
        for i in range(10):
            if i == 0:
                mtp_wr_addr = region_start
            elif i == 1:
                mtp_wr_addr = region_end-1
            elif i < 6:
                mtp_wr_addr = region_start+random.randint(0,32*100-1)
            else:
                mtp_wr_addr = random.randint(region_start, region_end-1)
            wr_addr_list.append(mtp_wr_addr)
            wr_data_list = []
            for j in range(8):
                tmp_wr_data = random.randint(0,(1<<32)-1)
                wr_data_list.append(tmp_wr_data)
                exp_addr_data_dist[MRAM_MTPR_BASE+(mtp_wr_addr&0xffffffe0)+4*j] = tmp_wr_data
            exp_dict[mtp_wr_addr&0xffffffe0] = wr_data_list

            mram_mtp_write(mtp_wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)
            rd = mram.mram_mtp_wport_state_0.read()
            if rd['ERROR'] == 1:
                helper.perror("MTP write to a region with writable=1/WPEN=1/WP=0 should pass")
            mram.mram_mtp_wport_state_0.write(ERROR=1)

        for i in range(len(wr_addr_list)):
            wr_addr_list[i] = wr_addr_list[i] & 0xffffffe0
        Check_result(wr_addr_list, exp_dict, frontdoor=0,expect_fail=0)
        check_content(exp_addr_data_dist)



        ######################
        ####################################################################################
        helper.log("Scenario 3: Config a region")
        reset_region_cfg()
        region_acl_reg_clear()
        region_idx = random.randint(0,7)
        [region_start, region_end] = set_a_region(region_idx)
        helper.log("region %0d, region_start = %x, region_end = %x" % (region_idx, region_start, region_end))

        # Scenario 3:  WPEN=1, WP=1(pin wp_n = 0)
        helper.log("Scenario 3, WPEN=1, WP=0(pin wp_n = 1)")
        region_acl_reg = mram.get_reg_by_name("mram_cfg_b_mtp_region_acl_" + str(region_idx) + "_0")
        region_acl_reg.update(wpen=1)
        helper.hdl_force("ntb_top.mram_wp_n", 0)

        
        # 3.0 
        helper.log("-- 3.0 -- region %0d writeable=0, readable=0, MTP write/read, MTPR should be blocked" % region_idx)
        region_acl_reg.update(readable=0,writable=0)
        # init 100 256b elements in MRAM
        exp_addr_data_dist.clear()
        init_mram_backdoor((region_start>>5), 100)
        helper.log("-- 3.0.0 -- check MTPR should be blocked")

        addr_list = []
        cmd_list = []
        data_list = []
        for i in range(20):
            if i == 0:
                addr_list.append(MRAM_MTPR_BASE+region_start)
            elif i == 1:
                addr_list.append(MRAM_MTPR_BASE+region_end-1)
            else:
                addr_list.append(random.randint(MRAM_MTPR_BASE+region_start, MRAM_MTPR_BASE+region_end-1))
            cmd_list.append(0)
            data_list.append(random.randint(0,0xffffffff))
        [resp_data_list, resp_err_list] = helper.burst_operation(addr_list, data_list, cmd_list, priv_id=2)
        for resp_err_item in resp_err_list:
            if resp_err_item != 1:
                helper.perror("MTPR to region%0d whose readable==0 should return an error" % region_idx)
        

        helper.log("-- 3.0.1 -- check MTP read should be blocked with readable=0")
        mtp_addr = 0
        for i in range(10):
            if i == 1:
                mtp_addr = region_start
            elif i == 2:
                mtp_addr = region_end-1
            else:
                mtp_addr = random.randint(region_start, region_end-1)#region_start+random.randint(0,32*100-1)
            helper.log("mtp_addr = %x" % mtp_addr)

            mram_mtp_read(mtp_addr, priv_id=2)
            rd = mram.mram_mtp_rport_state_0.read()
            if rd['ERROR'] != 1:
                helper.perror("Unexpected, MTP read to a readable=0 region should return an ERROR")
            mram.mram_mtp_rport_state_0.write(ERROR=1)
        
        helper.log("-- 3.0.2 -- check MTP write should be blocked with writeable=0/WPEN=1/WP=1")
        exp_dict = {}
        wr_addr_list = []
        for i in range(10):
            if i == 0:
                mtp_wr_addr = region_start
            elif i == 1:
                mtp_wr_addr = region_end-1
            elif i < 6:
                mtp_wr_addr = region_start+random.randint(0,32*100-1)
            else:
                mtp_wr_addr = random.randint(region_start, region_end-1)
            wr_addr_list.append(mtp_wr_addr)
            wr_data_list = []
            for j in range(8):
                wr_data_list.append(random.randint(0,(1<<32)-1))
            exp_dict[mtp_wr_addr&0xffffffe0] = wr_data_list
            mram_mtp_write(mtp_wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)
            rd = mram.mram_mtp_wport_state_0.read()
            if rd['ERROR'] != 1:
                helper.perror("MTP write to a region with writable=0/WPEN=1/WP=1 should return an ERROR")
            mram.mram_mtp_wport_state_0.write(ERROR=1)

        for i in range(len(wr_addr_list)):
            wr_addr_list[i] = wr_addr_list[i] & 0xffffffe0
        Check_result(wr_addr_list, exp_dict, frontdoor=0,expect_fail=1)
        check_content(exp_addr_data_dist)



        
        #3.1
        helper.log("-- 3.1 -- region %0d writeable=1/WPEN=1/WP=1, readable=0, MTP write, MTP read and MTPR should be blocked" % region_idx)
        region_acl_reg.update(readable=0,writable=1)
        # init 100 256b elements in MRAM
        helper.log("-- 3.1.0 -- check MTPR should be blocked")
        exp_addr_data_dist.clear()
        init_mram_backdoor((region_start>>5), 100)

        addr_list = []
        cmd_list = []
        data_list = []
        for i in range(20):
            if i == 0:
                addr_list.append(MRAM_MTPR_BASE+region_start)
            elif i == 1:
                addr_list.append(MRAM_MTPR_BASE+region_end-1)
            else:
                addr_list.append(random.randint(MRAM_MTPR_BASE+region_start, MRAM_MTPR_BASE+region_end-1))
            cmd_list.append(0)
            data_list.append(random.randint(0,0xffffffff))
        [resp_data_list, resp_err_list] = helper.burst_operation(addr_list, data_list, cmd_list, priv_id=2)
        for resp_err_item in resp_err_list:
            if resp_err_item != 1:
                helper.perror("MTPR to region%0d whose readable==0 should return an error" % region_idx)
        

        helper.log("-- 3.1.1 -- check MTP read should be blocked with readable=0")
        mtp_addr = 0
        for i in range(10):
            if i == 1:
                mtp_addr = region_start
            elif i == 2:
                mtp_addr = region_end-1
            else:
                mtp_addr = random.randint(region_start, region_end-1)#region_start+random.randint(0,32*100-1)
            helper.log("mtp_addr = %x" % mtp_addr)

            mram_mtp_read(mtp_addr, priv_id=2)
            rd = mram.mram_mtp_rport_state_0.read()
            if rd['ERROR'] != 1:
                helper.perror("Unexpected, MTP read to a readable=0 region should return an ERROR")
            mram.mram_mtp_rport_state_0.write(ERROR=1)
        
        helper.log("-- 3.1.2 -- check MTP write should be block with writeable=1/WPEN=1/WP=1")
        exp_dict = {}
        wr_addr_list = []
        for i in range(10):
            if i == 0:
                mtp_wr_addr = region_start
            elif i == 1:
                mtp_wr_addr = region_end-1
            elif i < 6:
                mtp_wr_addr = region_start+random.randint(0,32*100-1)
            else:
                mtp_wr_addr = random.randint(region_start, region_end-1)
            wr_addr_list.append(mtp_wr_addr)
            wr_data_list = []
            for j in range(8):
                tmp_wr_data = random.randint(0,(1<<32)-1)
                wr_data_list.append(tmp_wr_data)
            exp_dict[mtp_wr_addr&0xffffffe0] = wr_data_list

            mram_mtp_write(mtp_wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)
            rd = mram.mram_mtp_wport_state_0.read()
            if rd['ERROR'] != 1:
                helper.perror("MTP write to a region with writable=1/WPEN=1/WP=1 should return an ERROR")
            mram.mram_mtp_wport_state_0.write(ERROR=1)

        for i in range(len(wr_addr_list)):
            wr_addr_list[i] = wr_addr_list[i] & 0xffffffe0
        Check_result(wr_addr_list, exp_dict, frontdoor=0,expect_fail=1)
        check_content(exp_addr_data_dist)



        #3.2
        helper.log("-- 3.2 -- region %0d writeable=0, readable=1, MTP write should be blocked, MTP read, MTPR should pass" % region_idx)
        region_acl_reg.update(readable=1,writable=0)
        # init 100 256b elements in MRAM
        helper.log("-- 3.2.0 -- check MTPR should pass")
        exp_addr_data_dist.clear()
        init_mram_backdoor((region_start>>5), 100)

        addr_list = []
        cmd_list = []
        data_list = []
        for i in range(20):
            if i == 0:
                addr_list.append(MRAM_MTPR_BASE+region_start)
            elif i == 1:
                addr_list.append(MRAM_MTPR_BASE+region_end-1)
            elif i < 10:
                addr_list.append(MRAM_MTPR_BASE+region_start+random.randint(0,32*100-1))
            else:
                addr_list.append(random.randint(MRAM_MTPR_BASE+region_start, MRAM_MTPR_BASE+region_end-1))
            cmd_list.append(0)
            data_list.append(random.randint(0,0xffffffff))
        [resp_data_list, resp_err_list] = helper.burst_operation(addr_list, data_list, cmd_list, priv_id=2)
        for resp_err_item in resp_err_list:
            if resp_err_item == 1:
                helper.perror("MTPR to region%0d whose readable==1 should not return an error" % region_idx)
        for i in range(len(resp_data_list)):
            if addr_list[i] < MRAM_MTPR_BASE + region_start + 32*100:
                addr_32b = addr_list[i] & 0xfffffffc
                if resp_data_list[i] != exp_addr_data_dist[addr_32b]:
                    helper.perror("MTPR Mismatch, addr: %x, exp: %x, act: %x" % (addr_32b, exp_addr_data_dist[addr_32b], resp_data_list[i]))
        

        helper.log("-- 3.2.1 -- check MTP read should pass with readable=1")
        mtp_addr = 0
        for i in range(10):
            if i == 1:
                mtp_addr = region_start
            elif i == 2:
                mtp_addr = region_end-1
            elif i < 6:
                mtp_addr = region_start+random.randint(0,32*100-1)
            else:
                mtp_addr = random.randint(region_start, region_end-1)#region_start+random.randint(0,32*100-1)
            helper.log("mtp_addr = %x" % mtp_addr)

            rd_data_list = mram_mtp_read(mtp_addr, priv_id=2)
            rd = mram.mram_mtp_rport_state_0.read()
            if rd['ERROR'] == 1:
                helper.perror("Unexpected, MTP read to a readable=1 region should not return an ERROR")
            mram.mram_mtp_rport_state_0.write(ERROR=1)

            if mtp_addr < region_start + 32*100:
                for j in range(8):
                    if exp_addr_data_dist[MRAM_MTPR_BASE+(mtp_addr&0xffffffe0)+j*4] != rd_data_list[j]:
                        helper.perror("MTP rd Mismatch, addr: %x, exp: %x, act: %x" % (MRAM_MTPR_BASE+(mtp_addr&0xffffffe0)+j*4, exp_addr_data_dist[MRAM_MTPR_BASE+(mtp_addr&0xffffffe0)+j*4], rd_data_list[j]))
                

        helper.log("-- 3.2.2 -- check MTP write should be block with writeable=0/WPEN=1/WP=1")
        exp_dict = {}
        wr_addr_list = []
        for i in range(10):
            if i == 0:
                mtp_wr_addr = region_start
            elif i == 1:
                mtp_wr_addr = region_end-1
            elif i < 6:
                mtp_wr_addr = region_start+random.randint(0,32*100-1)
            else:
                mtp_wr_addr = random.randint(region_start, region_end-1)
            wr_addr_list.append(mtp_wr_addr)
            wr_data_list = []
            for j in range(8):
                tmp_wr_data = random.randint(0,(1<<32)-1)
                wr_data_list.append(tmp_wr_data)
            exp_dict[mtp_wr_addr&0xffffffe0] = wr_data_list

            mram_mtp_write(mtp_wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)
            rd = mram.mram_mtp_wport_state_0.read()
            if rd['ERROR'] != 1:
                helper.perror("MTP write to a region with writable=0/WPEN=1/WP=1 should return an ERROR")
            mram.mram_mtp_wport_state_0.write(ERROR=1)

        for i in range(len(wr_addr_list)):
            wr_addr_list[i] = wr_addr_list[i] & 0xffffffe0
        Check_result(wr_addr_list, exp_dict, frontdoor=0,expect_fail=1)
        check_content(exp_addr_data_dist)



        #2.3
        helper.log("-- 3.3 -- region %0d writeable=1/WPEN=1/WP=1, readable=1, MTP write should be block, MTP read, MTPR should pass" % region_idx)
        region_acl_reg.update(readable=1,writable=1)
        # init 100 256b elements in MRAM
        helper.log("-- 3.3.0 -- check MTPR should pass")
        exp_addr_data_dist.clear()
        init_mram_backdoor((region_start>>5), 100)

        addr_list = []
        cmd_list = []
        data_list = []
        for i in range(20):
            if i == 0:
                addr_list.append(MRAM_MTPR_BASE+region_start)
            elif i == 1:
                addr_list.append(MRAM_MTPR_BASE+region_end-1)
            elif i < 10:
                addr_list.append(MRAM_MTPR_BASE+region_start+random.randint(0,32*100-1))
            else:
                addr_list.append(random.randint(MRAM_MTPR_BASE+region_start, MRAM_MTPR_BASE+region_end-1))
            cmd_list.append(0)
            data_list.append(random.randint(0,0xffffffff))
        [resp_data_list, resp_err_list] = helper.burst_operation(addr_list, data_list, cmd_list, priv_id=2)
        for resp_err_item in resp_err_list:
            if resp_err_item == 1:
                helper.perror("MTPR to region%0d whose readable==1 should not return an error" % region_idx)
        for i in range(len(resp_data_list)):
            if addr_list[i] < MRAM_MTPR_BASE + region_start + 32*100:
                addr_32b = addr_list[i] & 0xfffffffc
                if resp_data_list[i] != exp_addr_data_dist[addr_32b]:
                    helper.perror("MTPR Mismatch, addr: %x, exp: %x, act: %x" % (addr_32b, exp_addr_data_dist[addr_32b], resp_data_list[i]))
        

        helper.log("-- 3.3.1 -- check MTP read should pass with readable=1")
        mtp_addr = 0
        for i in range(10):
            if i == 1:
                mtp_addr = region_start
            elif i == 2:
                mtp_addr = region_end-1
            elif i < 6:
                mtp_addr = region_start+random.randint(0,32*100-1)
            else:
                mtp_addr = random.randint(region_start, region_end-1)#region_start+random.randint(0,32*100-1)
            helper.log("mtp_addr = %x" % mtp_addr)

            rd_data_list = mram_mtp_read(mtp_addr, priv_id=2)
            rd = mram.mram_mtp_rport_state_0.read()
            if rd['ERROR'] == 1:
                helper.perror("Unexpected, MTP read to a readable=1 region should not return an ERROR")
            mram.mram_mtp_rport_state_0.write(ERROR=1)

            if mtp_addr < region_start + 32*100:
                for j in range(8):
                    if exp_addr_data_dist[MRAM_MTPR_BASE+(mtp_addr&0xffffffe0)+j*4] != rd_data_list[j]:
                        helper.perror("MTP rd Mismatch, addr: %x, exp: %x, act: %x" % (MRAM_MTPR_BASE+(mtp_addr&0xffffffe0)+j*4, exp_addr_data_dist[MRAM_MTPR_BASE+(mtp_addr&0xffffffe0)+j*4], rd_data_list[j]))
                

        helper.log("-- 3.3.2 -- check MTP write should pass with writeable=1/WPEN=1/WP=1")
        exp_dict = {}
        wr_addr_list = []
        for i in range(10):
            if i == 0:
                mtp_wr_addr = region_start
            elif i == 1:
                mtp_wr_addr = region_end-1
            elif i < 6:
                mtp_wr_addr = region_start+random.randint(0,32*100-1)
            else:
                mtp_wr_addr = random.randint(region_start, region_end-1)
            wr_addr_list.append(mtp_wr_addr)
            wr_data_list = []
            for j in range(8):
                tmp_wr_data = random.randint(0,(1<<32)-1)
                wr_data_list.append(tmp_wr_data)
            exp_dict[mtp_wr_addr&0xffffffe0] = wr_data_list

            mram_mtp_write(mtp_wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)
            rd = mram.mram_mtp_wport_state_0.read()
            if rd['ERROR'] != 1:
                helper.perror("MTP write to a region with writable=1/WPEN=1/WP=1 should return an error")
            mram.mram_mtp_wport_state_0.write(ERROR=1)

        for i in range(len(wr_addr_list)):
            wr_addr_list[i] = wr_addr_list[i] & 0xffffffe0
        Check_result(wr_addr_list, exp_dict, frontdoor=0,expect_fail=1)
        check_content(exp_addr_data_dist)

    helper.log("Test done")
