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
                if helper.target in ["fpga", "simv_fpga"]:
                    rd = rd_data_reg.read()
                else:
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

    
    def reset_region_cfg():
        for i in range(8):
            region_start_reg = mram.get_reg_by_name("mram_cfg_b_mtp_region_start_" + str(i) + "_0")
            region_end_reg   = mram.get_reg_by_name("mram_cfg_b_mtp_region_end_" + str(i) + "_0")
            region_start_reg.write(0xffffffff)
            region_end_reg.write(0xffffffff)

    def setup_a_region(i):
        region_start_reg = mram.get_reg_by_name("mram_cfg_b_mtp_region_start_" + str(i) + "_0")
        region_end_reg   = mram.get_reg_by_name("mram_cfg_b_mtp_region_end_" + str(i) + "_0")
        rand_region_start_addr = random.randint(0, MRAM_MTPR_SIZE-1)
        rand_region_start_addr = rand_region_start_addr & 0xfffff000 # region boundary should be 4KB aligned
        rand_region_end_addr = rand_region_start_addr + random.randint(1, 1024)*0x1000
        if rand_region_end_addr > MRAM_MTPR_SIZE:
            rand_region_end_addr = MRAM_MTPR_SIZE
        # leave mram_cfg_b_mtp_region_acl_0_0 without touching, so its writeable/readable == 1 defaultly
        region_start_reg.write(rand_region_start_addr)
        region_end_reg.write(rand_region_end_addr)
        return [rand_region_start_addr, rand_region_end_addr]


    def reset_xport_acl():
        mram.mram_cfg_b_mtp_wport_acl_0_0.write(region0=1,region1=1,region2=1,region3=1,region4=1,region5=1,region6=1,region7=1,out_region=1)
        mram.mram_cfg_b_mtp_rport_acl_0_0.write(region0=1,region1=1,region2=1,region3=1,region4=1,region5=1,region6=1,region7=1,out_region=1)
        mram.mram_cfg_b_mtpr_acl_0.write(region0=1,region1=1,region2=1,region3=1,region4=1,region5=1,region6=1,region7=1,out_region=1)

    def config_region_x_block_port0(region_i, rd_allowed, wr_allowed, mtpr_allowed):
        reset_xport_acl()
        if region_i == 0:
            mram.mram_cfg_b_mtp_wport_acl_0_0.update(region0=wr_allowed)
            mram.mram_cfg_b_mtp_rport_acl_0_0.update(region0=rd_allowed)
            mram.mram_cfg_b_mtpr_acl_0.update(region0=mtpr_allowed)
        elif region_i == 1:
            mram.mram_cfg_b_mtp_wport_acl_0_0.update(region1=wr_allowed)
            mram.mram_cfg_b_mtp_rport_acl_0_0.update(region1=rd_allowed)
            mram.mram_cfg_b_mtpr_acl_0.update(region1=mtpr_allowed)
        elif region_i == 2:
            mram.mram_cfg_b_mtp_wport_acl_0_0.update(region2=wr_allowed)
            mram.mram_cfg_b_mtp_rport_acl_0_0.update(region2=rd_allowed)
            mram.mram_cfg_b_mtpr_acl_0.update(region2=mtpr_allowed)
        elif region_i == 3:
            mram.mram_cfg_b_mtp_wport_acl_0_0.update(region3=wr_allowed)
            mram.mram_cfg_b_mtp_rport_acl_0_0.update(region3=rd_allowed)
            mram.mram_cfg_b_mtpr_acl_0.update(region3=mtpr_allowed)
        elif region_i == 4:
            mram.mram_cfg_b_mtp_wport_acl_0_0.update(region4=wr_allowed)
            mram.mram_cfg_b_mtp_rport_acl_0_0.update(region4=rd_allowed)
            mram.mram_cfg_b_mtpr_acl_0.update(region4=mtpr_allowed)
        elif region_i == 5:
            mram.mram_cfg_b_mtp_wport_acl_0_0.update(region5=wr_allowed)
            mram.mram_cfg_b_mtp_rport_acl_0_0.update(region5=rd_allowed)
            mram.mram_cfg_b_mtpr_acl_0.update(region5=mtpr_allowed)
        elif region_i == 6:
            mram.mram_cfg_b_mtp_wport_acl_0_0.update(region6=wr_allowed)
            mram.mram_cfg_b_mtp_rport_acl_0_0.update(region6=rd_allowed)
            mram.mram_cfg_b_mtpr_acl_0.update(region6=mtpr_allowed)
        elif region_i == 7:
            mram.mram_cfg_b_mtp_wport_acl_0_0.update(region7=wr_allowed)
            mram.mram_cfg_b_mtp_rport_acl_0_0.update(region7=rd_allowed)
            mram.mram_cfg_b_mtpr_acl_0.update(region7=mtpr_allowed)

    def setup_8_regions(without_overlap=1, clear_previous_cfg=1):
        if clear_previous_cfg == 1:
            for i in range(8):
                region_start_reg = mram.get_reg_by_name("mram_cfg_b_mtp_region_start_" + str(i) + "_0")
                region_end_reg   = mram.get_reg_by_name("mram_cfg_b_mtp_region_end_" + str(i) + "_0")
                region_start_reg.write(0xffffffff)
                region_end_reg.write(0xffffffff)
        start_idx_list = []
        end_idx_list = []
        if without_overlap == 1:
            for i in range(8):
                while True:
                    start_idx = random.randint(0,1023)
                    find_same_idx = 0
                    for j in range(len(start_idx_list)):
                        if start_idx_list[j] == start_idx:
                            find_same_idx = 1
                            break
                    if find_same_idx == 0:
                        helper.log("Get start_idx %0d" % start_idx)
                        start_idx_list.append(start_idx)
                        break
            # get 8 start_idx done
            start_idx_list.sort()
            for i in range(len(start_idx_list)):
                helper.log("start_idx_list[%0d] = %0d" % (i, start_idx_list[i]))

            for i in range(8):
                while True:
                    end_idx = random.randint(0,1023)
                    if i < 7:
                        if (end_idx > start_idx_list[i]) and (end_idx <= start_idx_list[i+1]):
                            helper.log("0, Get end_idx %0d" % end_idx)
                            end_idx_list.append(end_idx)
                            break
                    else:
                        if start_idx_list[7] == 1023:
                            helper.log("1, Get end_idx 1024")
                            end_idx_list.append(1024)
                            break

                        if end_idx > start_idx_list[7]:
                            helper.log("2, Get end_idx %0d" % end_idx)
                            end_idx_list.append(end_idx)
                            break

        else:
            for i in range(8):
                start_idx = random.randint(0,1023)
                while True:
                    end_idx = random.randint(0,1023) 
                    if end_idx > start_idx:
                        break
                start_idx_list.append(start_idx)
                end_idx_list.append(end_idx)

        for i in range(8):
            region_start_reg = mram.get_reg_by_name("mram_cfg_b_mtp_region_start_" + str(i) + "_0")
            region_end_reg   = mram.get_reg_by_name("mram_cfg_b_mtp_region_end_" + str(i) + "_0")
            region_start_reg.write(start_idx_list[i]*0x1000)
            region_end_reg.write(end_idx_list[i]*0x1000)
        return [start_idx_list, end_idx_list]


    def init_mram_with_frontdoor():
        exp_dict = {}
        for i in range(8):
            if i == 0:
                wr_addr = 0
            elif i == 1:
                wr_addr = 32
            elif i == 2:
                wr_addr = 32*2
            elif i == 3:
                wr_addr = 32*32
            elif i == 4:
                wr_addr = 128*1024*32-32
            elif i == 5:
                wr_addr = 128*1024*32-32*2
            elif i == 6:
                wr_addr = 128*1024*32-32*32
            else:
                wr_addr = 128*1024*32-32*32*2
            #wr_addr_list.append(wr_addr)
            wr_data_list = []
            for j in range(8):
                wr_data_list.append(random.randint(0,0xffffffff))
            exp_dict[wr_addr] = wr_data_list

            # try MTP write to the whole MRAM, it shouldn't be covered by any region
            test_api.mram_mtp_write(wr_addr, wr_data_list, rand_shuffle=1)

        return exp_dict

    helper.log("Test start")

    if helper.target in ["fpga", "simv_fpga"]:
        helper.log("init mram with frontdoor in some fixed address")
        reset_xport_acl()
        real_data_dict = init_mram_with_frontdoor() # some fixed address write
        helper.log("print the init data in MRAM")
        for add_idx in real_data_dict:
            helper.log("The address %x data is: "%(add_idx))
            for data in real_data_dict[add_idx]:
                helper.log("%x" % (data))

        helper.log("Scenario 0: out_region, mram_cfg_b_mtp_wport_acl_0_0.out_region = 0, will block MTP Write trans")
        mram.mram_cfg_b_mtp_wport_acl_0_0.update(out_region=0)

        rd = mram.mram_cfg_b_mtp_wport_acl_0_0.read()
        if rd['out_region'] != 0:
            helper.perror("Failed to configure mram_cfg_b_mtp_wport_acl_0_0.out_region to 0")
        helper.log("-- 0.0 -- MTP write to out_region should be block when mram_cfg_b_mtp_wport_acl_0_0.out_region = 0")
        exp_dict = {}
        wr_addr_list = []
        
        for i in range(8):
            if i == 0:
                wr_addr = 0
            elif i == 1:
                wr_addr = 32
            elif i == 2:
                wr_addr = 32*2
            elif i == 3:
                wr_addr = 32*32
            elif i == 4:
                wr_addr = 128*1024*32-32
            elif i == 5:
                wr_addr = 128*1024*32-32*2
            elif i == 6:
                wr_addr = 128*1024*32-32*32
            else:
                wr_addr = 128*1024*32-32*32*2
            wr_addr_list.append(wr_addr)
            wr_data_list = []
            for j in range(8):
                wr_data_list.append(random.randint(0,0xffffffff))
            exp_dict[wr_addr] = wr_data_list

            # try MTP write to the whole MRAM, it shouldn't be covered by any region
            test_api.mram_mtp_write(wr_addr, wr_data_list, rand_shuffle=1)
            rd = mram.mram_mtp_wport_state_0.read()
            if rd['ERROR'] != 1:
                helper.perror("MTP write to out_region with port block should return an ERROR")
            mram.mram_mtp_wport_state_0.write(ERROR=1)
        Check_result(wr_addr_list, exp_dict, frontdoor=1, expect_fail=1)

        helper.log("-- 0.1 -- MTP Read to out_region should be block when mram_cfg_b_mtp_rport_acl_0_0.out_region = 0")
        reset_xport_acl()
        mram.mram_cfg_b_mtp_rport_acl_0_0.update(out_region=0)
        rd = mram.mram_cfg_b_mtp_rport_acl_0_0.read()
        if rd['out_region'] != 0:
            helper.perror("Failed to configure mram_cfg_b_mtp_rport_acl_0_0.out_region to 0")
        
        for i in range(8):
            if i == 0:
                rd_addr = 0
            elif i == 1:
                rd_addr = 32
            elif i == 2:
                rd_addr = 32*2
            elif i == 3:
                rd_addr = 32*32
            elif i == 4:
                rd_addr = 128*1024*32-32
            elif i == 5:
                rd_addr = 128*1024*32-32*2
            elif i == 6:
                rd_addr = 128*1024*32-32*32
            else:
                rd_addr = 128*1024*32-32*32*2

            mram_mtp_read(rd_addr, priv_id=0)
            rd = mram.mram_mtp_rport_state_0.read()
            if rd['ERROR'] != 1:
                helper.perror("MTP read to out_region with port block should return an ERROR")
            mram.mram_mtp_rport_state_0.write(ERROR=1)

        helper.log("-- 0.2 -- MTPR to out_region should be block when mram_cfg_b_mtpr_rport_acl_0_0.out_region = 0")
        reset_xport_acl()
        for i in range(8):
            if i == 0:
                rd_addr = 0 + MRAM_MTPR_BASE
            elif i == 1:
                rd_addr = 32 + MRAM_MTPR_BASE
            elif i == 2:
                rd_addr = 32*2 + MRAM_MTPR_BASE
            elif i == 3:
                rd_addr = 32*32 + MRAM_MTPR_BASE
            elif i == 4:
                rd_addr = MRAM_MTPR_BASE + MRAM_MTPR_SIZE - 32*2
            elif i == 5:
                rd_addr = MRAM_MTPR_BASE + MRAM_MTPR_SIZE - 32
            elif i == 6:
                rd_addr = MRAM_MTPR_BASE + MRAM_MTPR_SIZE - 32*32
            else:
                rd_addr = MRAM_MTPR_BASE + MRAM_MTPR_SIZE - 32*32*2
            rd_resp = helper.read(rd_addr)
            if rd_resp != real_data_dict[rd_addr][0]:
                helper.perror("MTPR to out_region with mram_cfg_b_mtpr_acl_0_0.out_region = 1 should return an correct data, but now is %x, address is %x" % (rd_resp, rd_addr))
            else:
                helper.log("MTPR with address %x return %x, the correct data is %x" % (rd_addr, rd_resp, real_data_dict[rd_addr][0])
        #mram.mram_cfg_b_mtp_rport_acl_0_0.update(out_region=0)
        mram.mram_cfg_b_mtpr_acl_0.update(out_region=0)
        rd = mram.mram_cfg_b_mtpr_acl_0.read()
        if rd['out_region'] != 0:
            helper.perror("Failed to configure mram_cfg_b_mtpr_acl_0.out_region to 0")

        for i in range(8):
            if i == 0:
                rd_addr = 0 + MRAM_MTPR_BASE
            elif i == 1:
                rd_addr = 32 + MRAM_MTPR_BASE
            elif i == 2:
                rd_addr = 32*2 + MRAM_MTPR_BASE
            elif i == 3:
                rd_addr = 32*32 + MRAM_MTPR_BASE
            elif i == 4:
                rd_addr = MRAM_MTPR_BASE + MRAM_MTPR_SIZE - 32*2
            elif i == 5:
                rd_addr = MRAM_MTPR_BASE + MRAM_MTPR_SIZE - 32
            elif i == 6:
                rd_addr = MRAM_MTPR_BASE + MRAM_MTPR_SIZE - 32*32
            else:
                rd_addr = MRAM_MTPR_BASE + MRAM_MTPR_SIZE - 32*32*2
            rd_resp = helper.read(rd_addr)
            if rd_resp == real_data_dict[rd_addr][0]:
                helper.perror("MTPR to out_region with mram_cfg_b_mtpr_acl_0_0.out_region = 0 should return an incorrect data, but now is %x, address is %x" % (rd_resp, rd_addr))
            else:
                helper.log("MTPR with address %x return %x, the correct data is %x" % (rd_addr, rd_resp, real_data_dict[rd_addr][0])
        
        
#        helper.log("Scenario 1, configure region x, with writeable/readable = 1, try to access this region")
#        for i in range(8):
#            helper.log("-- 1.%0d --" % i)
#            helper.log("Test region %0d" % i)
#           
#            reset_region_cfg()
#            [region_start_addr, region_end_addr] = setup_a_region(i)
#
#
#            helper.log("Check MTP write block for region %0d" % i)
#            config_region_x_block_port0(i,rd_allowed=1,wr_allowed=0,mtpr_allowed=1)
#            exp_dict = {}
#            wr_addr_list = []
#            for j in range(10):
#                if j == 0:
#                    wr_addr = region_start_addr
#                elif j == 9:
#                    wr_addr = region_end_addr-32
#                else:
#                    wr_addr = random.randint(region_start_addr, region_end_addr-1)
#                    wr_addr = wr_addr & 0xffffffe0
#                wr_addr_list.append(wr_addr)
#                wr_data_list = []
#                for k in range(8):
#                    wr_data_list.append(random.randint(0,0xffffffff))
#                exp_dict[wr_addr] = wr_data_list
#
#                mram_mtp_write(wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)
#                rd = mram.mram_mtp_wport_state_0.read()
#                if rd['ERROR'] != 1:
#                    helper.perror("MTP write to region %0d with port block should return an ERROR" % i)
#                mram.mram_mtp_wport_state_0.write(ERROR=1)
#            Check_result(wr_addr_list, exp_dict, frontdoor=0, expect_fail=1)
#
#            helper.log("Check MTP read block for region %0d" % i)
#            config_region_x_block_port0(i,rd_allowed=0,wr_allowed=1,mtpr_allowed=1)
#            for j in range(10):
#                if j == 0:
#                    rd_addr = region_start_addr
#                elif j == 9:
#                    rd_addr = region_end_addr-32
#                else:
#                    rd_addr = random.randint(region_start_addr, region_end_addr-1)
#                    rd_addr = rd_addr & 0xffffffe0
#
#                mram_mtp_read(rd_addr, priv_id=2)
#                rd = mram.mram_mtp_rport_state_0.read()
#                if rd['ERROR'] != 1:
#                    helper.perror("MTP read to region %0d with port block should return an ERROR" % i)
#                mram.mram_mtp_rport_state_0.write(ERROR=1)
#           
#            helper.log("Check MTPR port block for region %0d" % i)
#            config_region_x_block_port0(i,rd_allowed=1,wr_allowed=1,mtpr_allowed=0)
#            addr_list = []
#            cmd_list = []
#            data_list = []
#            for j in range(20):
#                if j == 0:
#                    rd_addr = MRAM_MTPR_BASE + region_start_addr
#                elif j == 1:
#                    rd_addr = MRAM_MTPR_BASE + region_end_addr - 4
#                else:
#                    rd_addr = MRAM_MTPR_BASE + random.randint(region_start_addr, region_end_addr-1)
#                    rd_addr = rd_addr & 0xfffffffc
#                cmd_list.append(0)
#                addr_list.append(rd_addr)
#                data_list.append(random.randint(0, 0xffffffff))
#
#            [resp_data_list, resp_err_list] = helper.burst_operation(addr_list, data_list, cmd_list, priv_id=2)
#            for resp_err_item in resp_err_list:
#                if resp_err_item != 1:
#                    helper.perror("MTPR to region %0d with mram_cfg_b_mtp_rport_acl_0_0.region%0d = 0 should return an error" % (i, i))



    else:
        helper.log("Scenario 0: out_region, mram_cfg_b_mtp_wport_acl_0_0.out_region = 0, will block MTP Write trans")
        reset_xport_acl()
        mram.mram_cfg_b_mtp_wport_acl_0_0.update(out_region=0)

        rd = mram.mram_cfg_b_mtp_wport_acl_0_0.read()
        if rd['out_region'] != 0:
            helper.perror("Failed to configure mram_cfg_b_mtp_wport_acl_0_0.out_region to 0")
        helper.log("-- 0.0 -- MTP write to out_region should be block when mram_cfg_b_mtp_wport_acl_0_0.out_region = 0")
        exp_dict = {}
        wr_addr_list = []
        
        for i in range(20):
            if i == 0:
                wr_addr = 0
            elif i == 1:
                wr_addr = 32
            elif i == 3:
                wr_addr = 32*32
            elif i == 4:
                wr_addr = 128*1024*32-32
            elif i == 5:
                wr_addr = 128*1024*32-32*2
            elif i == 6:
                wr_addr = 128*1024*32-32*32
            else:
                wr_addr = random.randint(0,128*1024)*32
            wr_addr_list.append(wr_addr)
            wr_data_list = []
            for j in range(8):
                wr_data_list.append(random.randint(0,0xffffffff))
            exp_dict[wr_addr] = wr_data_list

            # try MTP write to the whole MRAM, it shouldn't be covered by any region
            mram_mtp_write(wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)
            rd = mram.mram_mtp_wport_state_0.read()
            if rd['ERROR'] != 1:
                helper.perror("MTP write to out_region with port block should return an ERROR")
            mram.mram_mtp_wport_state_0.write(ERROR=1)
        Check_result(wr_addr_list, exp_dict, frontdoor=0, expect_fail=1)

        helper.log("-- 0.1 -- MTP Read to out_region should be block when mram_cfg_b_mtp_rport_acl_0_0.out_region = 0")
        reset_xport_acl()
        mram.mram_cfg_b_mtp_rport_acl_0_0.update(out_region=0)
        rd = mram.mram_cfg_b_mtp_rport_acl_0_0.read()
        if rd['out_region'] != 0:
            helper.perror("Failed to configure mram_cfg_b_mtp_rport_acl_0_0.out_region to 0")
        
        for i in range(20):
            if i == 0:
                rd_addr = 0
            elif i == 1:
                rd_addr = 32
            elif i == 3:
                rd_addr = 32*32
            elif i == 4:
                rd_addr = 128*1024*32-32
            elif i == 5:
                rd_addr = 128*1024*32-32*2
            elif i == 6:
                rd_addr = 128*1024*32-32*32
            else:
                rd_addr = random.randint(0,128*1024)*32

            mram_mtp_read(rd_addr, priv_id=2)
            rd = mram.mram_mtp_rport_state_0.read(priv_id=2)
            if rd['ERROR'] != 1:
                helper.perror("MTP read to out_region with port block should return an ERROR")
            mram.mram_mtp_rport_state_0.write(ERROR=1)

        helper.log("-- 0.2 -- MTPR to out_region should be block when mram_cfg_b_mtp_rport_acl_0_0.out_region = 0")
        reset_xport_acl()
        #mram.mram_cfg_b_mtp_rport_acl_0_0.update(out_region=0)
        mram.mram_cfg_b_mtpr_acl_0.update(out_region=0)
        rd = mram.mram_cfg_b_mtpr_acl_0.read()
        if rd['out_region'] != 0:
            helper.perror("Failed to configure mram_cfg_b_mtpr_acl_0.out_region to 0")

        addr_list = []
        cmd_list = []
        data_list = []
        for i in range(50):
            if i == 0:
                rd_addr = 0 + MRAM_MTPR_BASE
            elif i == 1:
                rd_addr = 32 + MRAM_MTPR_BASE
            elif i == 3:
                rd_addr = 32*32 + MRAM_MTPR_BASE
            elif i == 4:
                rd_addr = MRAM_MTPR_BASE + MRAM_MTPR_SIZE - 4
            elif i == 5:
                rd_addr = MRAM_MTPR_BASE + MRAM_MTPR_SIZE - 32
            elif i == 6:
                rd_addr = MRAM_MTPR_BASE + MRAM_MTPR_SIZE - 32*32
            else:
                rd_addr = random.randint(MRAM_MTPR_BASE, MRAM_MTPR_BASE+MRAM_MTPR_SIZE-1)
            addr_list.append(rd_addr)
            cmd_list.append(0)
            data_list.append(random.randint(0,0xffffffff))
        [resp_data_list, resp_err_list] = helper.burst_operation(addr_list, data_list, cmd_list, priv_id=2)
        for resp_err_item in resp_err_list:
            if resp_err_item != 1:
                helper.perror("MTPR to out_region with mram_cfg_b_mtp_rport_acl_0_0.out_region = 0 should return an error")

        
        
        helper.log("Scenario 1, configure region x, with writeable/readable = 1, try to access this region")
        for i in range(8):
            helper.log("-- 1.%0d --" % i)
            helper.log("Test region %0d" % i)
           
            reset_region_cfg()
            [region_start_addr, region_end_addr] = setup_a_region(i)

            helper.log("Check MTP write block for region %0d" % i)
            config_region_x_block_port0(i,rd_allowed=1,wr_allowed=0,mtpr_allowed=1)
            exp_dict = {}
            wr_addr_list = []
            for j in range(10):
                if j == 0:
                    wr_addr = region_start_addr
                elif j == 9:
                    wr_addr = region_end_addr-32
                else:
                    wr_addr = random.randint(region_start_addr, region_end_addr-1)
                    wr_addr = wr_addr & 0xffffffe0
                wr_addr_list.append(wr_addr)
                wr_data_list = []
                for k in range(8):
                    wr_data_list.append(random.randint(0,0xffffffff))
                exp_dict[wr_addr] = wr_data_list

                mram_mtp_write(wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)
                rd = mram.mram_mtp_wport_state_0.read()
                if rd['ERROR'] != 1:
                    helper.perror("MTP write to region %0d with port block should return an ERROR" % i)
                mram.mram_mtp_wport_state_0.write(ERROR=1)
            Check_result(wr_addr_list, exp_dict, frontdoor=0, expect_fail=1)

            helper.log("Check MTP read block for region %0d" % i)
            config_region_x_block_port0(i,rd_allowed=0,wr_allowed=1,mtpr_allowed=1)
            for j in range(10):
                if j == 0:
                    rd_addr = region_start_addr
                elif j == 9:
                    rd_addr = region_end_addr-32
                else:
                    rd_addr = random.randint(region_start_addr, region_end_addr-1)
                    rd_addr = rd_addr & 0xffffffe0

                mram_mtp_read(rd_addr, priv_id=2)
                rd = mram.mram_mtp_rport_state_0.read()
                if rd['ERROR'] != 1:
                    helper.perror("MTP read to region %0d with port block should return an ERROR" % i)
                mram.mram_mtp_rport_state_0.write(ERROR=1)
           
            helper.log("Check MTPR port block for region %0d" % i)
            config_region_x_block_port0(i,rd_allowed=1,wr_allowed=1,mtpr_allowed=0)
            addr_list = []
            cmd_list = []
            data_list = []
            for j in range(20):
                if j == 0:
                    rd_addr = MRAM_MTPR_BASE + region_start_addr
                elif j == 1:
                    rd_addr = MRAM_MTPR_BASE + region_end_addr - 4
                else:
                    rd_addr = MRAM_MTPR_BASE + random.randint(region_start_addr, region_end_addr-1)
                    rd_addr = rd_addr & 0xfffffffc
                cmd_list.append(0)
                addr_list.append(rd_addr)
                data_list.append(random.randint(0, 0xffffffff))

            [resp_data_list, resp_err_list] = helper.burst_operation(addr_list, data_list, cmd_list, priv_id=2)
            for resp_err_item in resp_err_list:
                if resp_err_item != 1:
                    helper.perror("MTPR to region %0d with mram_cfg_b_mtp_rport_acl_0_0.region%0d = 0 should return an error" % (i, i))


        helper.log("Scenario 2, full regions config")
        reset_region_cfg()
        
        region_rd_port_allow_list = []
        region_wr_port_allow_list = []
        region_mtpr_allow_list = []
        for i in range(8):
            # 200KB per region, 200KB*8
            region_start_reg = mram.get_reg_by_name("mram_cfg_b_mtp_region_start_" + str(i) + "_0")
            region_end_reg   = mram.get_reg_by_name("mram_cfg_b_mtp_region_end_" + str(i) + "_0")
            region_start_addr = i*0x32000
            region_end_addr = (i+1)*0x32000
            region_start_reg.write(region_start_addr)
            region_end_reg.write(region_end_addr)

            region_rd_port_allow = random.randint(0,1)
            region_wr_port_allow = random.randint(0,1)
            region_mtpr_allow    = random.randint(0,1)
            region_rd_port_allow_list.append(region_rd_port_allow)
            region_wr_port_allow_list.append(region_wr_port_allow)
            region_mtpr_allow_list.append(region_mtpr_allow)
        
            fld_name = "region%0d" % i
            mram.mram_cfg_b_mtp_wport_acl_0_0.update(**{fld_name: region_wr_port_allow})
            mram.mram_cfg_b_mtp_rport_acl_0_0.update(**{fld_name: region_rd_port_allow})
            mram.mram_cfg_b_mtpr_acl_0.update(**{fld_name: region_mtpr_allow})
        mram.mram_cfg_b_mtp_wport_acl_0_0.update(out_region=0)
        mram.mram_cfg_b_mtp_rport_acl_0_0.update(out_region=0)
        mram.mram_cfg_b_mtpr_acl_0.update(out_region=0)

        for i in range(50):
            wr_addr = random.randint(0, 200*1024*8-1)
            k = 0
            for k in range(8):
                if (wr_addr >= 0x32000*k) and (wr_addr < 0x32000*(k+1)):
                    break
            
            wr_addr_list = []
            exp_dict = {}
            wr_addr_list.append(wr_addr & 0xffffffe0)
            
            wr_data_list = []
            for j in range(8):
                wr_data_list.append(random.randint(0,0xffffffff))

            exp_dict[wr_addr & 0xffffffe0] = wr_data_list 

            mram_mtp_write(wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)
            rd = mram.mram_mtp_wport_state_0.read()
            if (region_wr_port_allow_list[k] == 0) and rd['ERROR'] != 1:
                helper.perror("MTP write to region with port block should return an ERROR")
            mram.mram_mtp_wport_state_0.write(ERROR=1)

            if region_wr_port_allow_list[k] == 0:
                Check_result(wr_addr_list, exp_dict, frontdoor=0, expect_fail=1)
            else:
                Check_result(wr_addr_list, exp_dict, frontdoor=0, expect_fail=0)


            rd_addr = random.randint(0, 200*1024*8-1)
            k = 0
            for k in range(8):
                if (rd_addr >= 0x32000*k) and (rd_addr < 0x32000*(k+1)):
                    break
            mram_mtp_read(rd_addr, priv_id=2)
            rd = mram.mram_mtp_rport_state_0.read()
            if (region_rd_port_allow_list[k] == 0) and rd['ERROR'] != 1:
                helper.perror("MTP read to region with port block should return an ERROR")
            mram.mram_mtp_rport_state_0.write(ERROR=1)

            addr_list = []
            cmd_list = []
            data_list = []
            rd_addr = random.randint(0, 200*1024*8-1)
            k = 0
            for k in range(8):
                if (rd_addr >= 0x32000*k) and (rd_addr < 0x32000*(k+1)):
                    break
            addr_list.append(MRAM_MTPR_BASE+rd_addr)
            cmd_list.append(0)
            data_list.append(random.randint(0,0xffffffff))

            [resp_data_list, resp_err_list] = helper.burst_operation(addr_list, data_list, cmd_list, priv_id=2)
            for resp_err_item in resp_err_list:
                if (region_mtpr_allow_list[k] == 0) and resp_err_item != 1:
                    helper.perror("MTPR to region %0d with mram_cfg_b_mtp_rport_acl_0_0.region%0d = 0 should return an error" % (k, k))
            
        helper.log("-- 2.1 --, out region start")
        wr_addr = 0x190000
        wr_data_list = []
        for j in range(8):
            wr_data_list.append(random.randint(0,0xffffffff))
        mram_mtp_write(wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)
        rd = mram.mram_mtp_wport_state_0.read()
        if rd['ERROR'] != 1:
            helper.perror("MTP write to out_region start boundary with port block should return an ERROR")
        mram.mram_mtp_wport_state_0.write(ERROR=1)

        rd_addr = 0x190000
        mram_mtp_read(rd_addr, priv_id=2)
        rd = mram.mram_mtp_rport_state_0.read()
        if rd['ERROR'] != 1:
            helper.perror("MTP read to out_region start boundary with port block should return an ERROR")
        mram.mram_mtp_rport_state_0.write(ERROR=1)

        addr_list = []
        cmd_list = []
        data_list = []
        rd_addr = 0x190000
        addr_list.append(MRAM_MTPR_BASE+rd_addr)
        cmd_list.append(0)
        data_list.append(random.randint(0,0xffffffff))

        [resp_data_list, resp_err_list] = helper.burst_operation(addr_list, data_list, cmd_list, priv_id=2)
        for resp_err_item in resp_err_list:
            if resp_err_item != 1:
                helper.perror("MTPR to out_region start boundary with port block should return an error")

        helper.log("-- 2.2 --, out region end")
        wr_addr = 0x3fffff
        wr_data_list = []
        for j in range(8):
            wr_data_list.append(random.randint(0,0xffffffff))
        mram_mtp_write(wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)
        rd = mram.mram_mtp_wport_state_0.read()
        if rd['ERROR'] != 1:
            helper.perror("MTP write to out_region end boundary with port block should return an ERROR")
        mram.mram_mtp_wport_state_0.write(ERROR=1)

        rd_addr = 0x3fffff
        mram_mtp_read(rd_addr, priv_id=2)
        rd = mram.mram_mtp_rport_state_0.read()
        if rd['ERROR'] != 1:
            helper.perror("MTP read to out_region end boundary with port block should return an ERROR")
        mram.mram_mtp_rport_state_0.write(ERROR=1)

        addr_list = []
        cmd_list = []
        data_list = []
        rd_addr = 0x3fffff
        addr_list.append(MRAM_MTPR_BASE+rd_addr)
        cmd_list.append(0)
        data_list.append(random.randint(0,0xffffffff))

        [resp_data_list, resp_err_list] = helper.burst_operation(addr_list, data_list, cmd_list, priv_id=2)
        for resp_err_item in resp_err_list:
            if resp_err_item != 1:
                helper.perror("MTPR to out_region end boundary with port block should return an error")

        helper.log("-- 2.3 --, out region middle")
        wr_addr = random.randint(0x190000, 0x3fffff)
        wr_data_list = []
        for j in range(8):
            wr_data_list.append(random.randint(0,0xffffffff))
        mram_mtp_write(wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)
        rd = mram.mram_mtp_wport_state_0.read()
        if rd['ERROR'] != 1:
            helper.perror("MTP write to out_region middle with port block should return an ERROR")
        mram.mram_mtp_wport_state_0.write(ERROR=1)

        rd_addr = random.randint(0x190000, 0x3fffff)
        mram_mtp_read(rd_addr, priv_id=2)
        rd = mram.mram_mtp_rport_state_0.read()
        if rd['ERROR'] != 1:
            helper.perror("MTP read to out_region middle with port block should return an ERROR")
        mram.mram_mtp_rport_state_0.write(ERROR=1)

        addr_list = []
        cmd_list = []
        data_list = []
        rd_addr = random.randint(0x190000, 0x3fffff)
        addr_list.append(MRAM_MTPR_BASE+rd_addr)
        cmd_list.append(0)
        data_list.append(random.randint(0,0xffffffff))

        [resp_data_list, resp_err_list] = helper.burst_operation(addr_list, data_list, cmd_list, priv_id=2)
        for resp_err_item in resp_err_list:
            if resp_err_item != 1:
                helper.perror("MTPR to out_region middle with port block should return an error")


        helper.wait_sim_time("us", 20)
        helper.log("Random part")
        [region_start_idx_list, region_end_idx_list] = setup_8_regions(without_overlap=1, clear_previous_cfg=1)
        helper.log("Set region done")
   
        for i in range(8):
            helper.log("region_start_idx_list[%0d] = %0d, region_end_idx_list[%0d] = %0d" % (i, region_start_idx_list[i], i, region_end_idx_list[i]))

        wport_acl_bits = random.randint(0,511)
        rport_acl_bits = random.randint(0,511)
        mtpr_acl_bits  = random.randint(0,511)
        helper.log("wport_acl_bits = 0x%x, rport_acl_bits = 0x%x, mtpr_acl_bits = 0x%x" % (wport_acl_bits, rport_acl_bits, mtpr_acl_bits))

        mram.mram_cfg_b_mtp_wport_acl_0_0.write(region0=(wport_acl_bits&0x1),region1=((wport_acl_bits>>1)&0x1),region2=((wport_acl_bits>>2)&0x1),region3=((wport_acl_bits>>3)&0x1),region4=((wport_acl_bits>>4)&0x1),region5=((wport_acl_bits>>5)&0x1),region6=((wport_acl_bits>>6)&0x1),region7=((wport_acl_bits>>7)&0x1),out_region=((wport_acl_bits>>8)&0x1))
        mram.mram_cfg_b_mtp_rport_acl_0_0.write(region0=(rport_acl_bits&0x1),region1=((rport_acl_bits>>1)&0x1),region2=((rport_acl_bits>>2)&0x1),region3=((rport_acl_bits>>3)&0x1),region4=((rport_acl_bits>>4)&0x1),region5=((rport_acl_bits>>5)&0x1),region6=((rport_acl_bits>>6)&0x1),region7=((rport_acl_bits>>7)&0x1),out_region=((rport_acl_bits>>8)&0x1))
        mram.mram_cfg_b_mtpr_acl_0.write(region0=(mtpr_acl_bits&0x1),region1=((mtpr_acl_bits>>1)&0x1),region2=((mtpr_acl_bits>>2)&0x1),region3=((mtpr_acl_bits>>3)&0x1),region4=((mtpr_acl_bits>>4)&0x1),region5=((mtpr_acl_bits>>5)&0x1),region6=((mtpr_acl_bits>>6)&0x1),region7=((mtpr_acl_bits>>7)&0x1),out_region=((mtpr_acl_bits>>8)&0x1))

        helper.wait_sim_time("us",5)
        # out region
        mtp_addr = 0
        mtp_256_idx = 0
        out_region_idx_find = 0
        for i in range(500):
            mtp_256_idx = random.randint(0,128*1024)
            inside_a_region = 0
            for j in range(8):
                if ((mtp_256_idx*32) >= (region_start_idx_list[j]*0x1000)) and ((mtp_256_idx*32) < (region_end_idx_list[j]*0x1000)):
                    inside_a_region = 1
                    break
            if inside_a_region == 0:
                out_region_idx_find = 1
                break
        if out_region_idx_find == 1:
            mtp_addr = mtp_256_idx*32+random.randint(0,31)
            data_list = []
            for i in range(8):
                data_list.append(random.randint(0,0xffffffff))
            mram_mtp_write(mtp_addr, data_list, priv_id=2, rand_shuffle=1)
            rd = mram.mram_mtp_wport_state_0.read()
            if ((wport_acl_bits>>8)&0x1) == 1:
                if rd['ERROR'] == 1:
                    helper.perror("MTP write to out region with wport_acl.out_region == 1 should not return an ERROR")
            else:
                if rd['ERROR'] == 0:
                    helper.perror("MTP write to out region with wport_acl.out_region == 0 should return an ERROR")
            mram.mram_mtp_wport_state_0.write(ERROR=1)

            mram_mtp_read(mtp_addr, priv_id=2)
            rd = mram.mram_mtp_rport_state_0.read()
            if ((rport_acl_bits>>8)&0x1) == 1:
                if rd['ERROR'] == 1:
                    helper.perror("MTP read to out region with rport_acl.out_region == 1 should not return an ERROR")
            else:
                if rd['ERROR'] == 0:
                    helper.perror("MTP read to out region with rport_acl.out_region == 0 should return an ERROR")
            mram.mram_mtp_rport_state_0.write(ERROR=1)

            mtpr_addr = mtp_addr + MRAM_MTPR_BASE
            addr_list = []
            cmd_list = []
            data_list = []
            addr_list.append(mtpr_addr)
            cmd_list.append(0)
            data_list.append(random.randint(0,0xffffffff))
            [resp_data_list, resp_err_list] = helper.burst_operation(addr_list, data_list, cmd_list, priv_id=2)
            if ((mtpr_acl_bits>>8)&0x1) == 1:
                if resp_err_list[0] == 1:
                    helper.perror("Unexpected, MTPR to out-region with rpot_acl.out_region == 1 should not return an error")
            else:
                if resp_err_list[0] == 0:
                    helper.perror("Unexpected, MTPR to out-region with rpot_acl.out_region == 0 should return an error")
 


        # inside a region
        #rand_result_dict = rnd.randomize()
        sel_region_idx = random.randint(0,7)#rand_result_dict['dice0_7']
        
        helper.log("sel_region_idx = %0d" % sel_region_idx)
        mtp_addr = random.randint(region_start_idx_list[sel_region_idx]*0x1000, (region_end_idx_list[sel_region_idx]-1)*0x1000)
        
        helper.log("region_start_idx_list[sel_region_idx] = %x, region_end_idx_list[sel_region_idx] = %x" % (region_start_idx_list[sel_region_idx], region_end_idx_list[sel_region_idx]))
        helper.log("mtp_addr = %x" % mtp_addr)
        data_list = []
        for i in range(8):
            data_list.append(random.randint(0,0xffffffff))
        mram_mtp_write(mtp_addr, data_list, priv_id=2, rand_shuffle=1)
        rd = mram.mram_mtp_wport_state_0.read()
        if ((wport_acl_bits>>sel_region_idx)&0x1) == 1:
            if rd['ERROR'] == 1:
                helper.perror("MTP write to region %0d with wport_acl.out_region == 1 should not return an ERROR" % sel_region_idx)
        else:
            if rd['ERROR'] == 0:
                helper.perror("MTP write to region %0d with wport_acl.out_region == 0 should return an ERROR" % sel_region_idx)
        mram.mram_mtp_wport_state_0.write(ERROR=1)

        mram_mtp_read(mtp_addr, priv_id=2)
        rd = mram.mram_mtp_rport_state_0.read()
        if ((rport_acl_bits>>sel_region_idx)&0x1) == 1:
            if rd['ERROR'] == 1:
                helper.perror("MTP read to out region %0d with rport_acl.region == 1 should not return an ERROR" % sel_region_idx)
        else:
            if rd['ERROR'] == 0:
                helper.perror("MTP read to out region %0d with rport_acl.region == 0 should return an ERROR" % sel_region_idx)
        mram.mram_mtp_rport_state_0.write(ERROR=1)

        mtpr_addr = mtp_addr + MRAM_MTPR_BASE
        addr_list = []
        cmd_list = []
        data_list = []
        addr_list.append(mtpr_addr)
        cmd_list.append(0)
        data_list.append(random.randint(0,0xffffffff))
        [resp_data_list, resp_err_list] = helper.burst_operation(addr_list, data_list, cmd_list, priv_id=2)
        if ((mtpr_acl_bits>>sel_region_idx)&0x1) == 1:
            if resp_err_list[0] == 1:
                helper.perror("Unexpected, MTPR to region %0d with rpot_acl.region == 1 should not return an error" % sel_region_idx)
        else:
            if resp_err_list[0] == 0:
                helper.perror("Unexpected, MTPR to region %0d with rpot_acl.region == 0 should return an error" % sel_region_idx)



    helper.log("Test done")
