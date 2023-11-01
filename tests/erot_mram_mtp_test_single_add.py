#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3                                                                                                                                                                                           
from driver import *
import random

with Test(sys.argv) as t:
    mram = erot.MRAM

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
            helper.log("poll busy state")
            mram.mram_mtp_rport_state_0.poll(BUSY=0)
            helper.log("poll busy state = 0 end")
            mram_read_result = mram.mram_mtp_rport_state_0.read()
            mram_read_error_bit = mram_read_result['ERROR']
            helper.log(f"mram read address {addr}, the error bit value is {mram_read_error_bit}")
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
                    helper.log("FPGA just use priv = 0 is OK")
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
                    helper.log(" addr: %x" % wr_addr_list[i])
                    helper.log("act: %s" % [hex(x) for x in actual_32b_list])
                    helper.log("exp: %s" % [hex(x) for x in exp_32b_list])
            else:
                if actual_32b_list == exp_32b_list:
                    helper.perror("Unexpected match, addr: %x" % wr_addr_list[i])
                    helper.log("act/exp: %s" % [hex(x) for x in actual_32b_list])


    helper.log("Test start")
    # 4MB space, each MTP write covers 32Bytes, need 128*1024 write operations
    helper.log("#0, addr[4:0] != 0, to confirm that mtp_addr is based on 256bits(32Bytes)")
    exp_dict = {}
    wr_addr_list = []
    wr_addr_32B = random.randint(0,128*1024-1)*32
    for i in range(0, 1):
        #wr_addr = wr_addr_32B+i
        wr_addr = int("3629a0", 16)
        wr_addr_list.append(wr_addr)
        wr_data_list = []
        for j in range(8):
            wr_data_list.append(random.randint(0,0xffffffff))
        exp_dict[wr_addr] = wr_data_list
        if helper.target in ["fpga", "simv_fpga"]:
            test_api.mram_mtp_write(wr_addr, wr_data_list, rand_shuffle=1)
        else:
            mram_mtp_write(wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)

    # all those addresses should be written to a single 32bytes
    for key in exp_dict:
        exp_dict[key] = exp_dict[list(exp_dict)[-1]]
    if helper.target in ["fpga", "simv_fpga"]:
        helper.log("FPGA should be frontdoor, so no need to check the backdoor condition")
    else:
        Check_result(wr_addr_list, exp_dict, frontdoor=0)
    Check_result(wr_addr_list, exp_dict, frontdoor=1)

    if helper.target in ["fpga", "simv_fpga"]:
        helper.log("For decreasing the complex of FPGA test, will test less address")
        #helper.log("#1, Test the start addresses with wr_data/addr's configurations")
        #exp_dict = {}
        #wr_addr_list = []
        #for i in range(2):
        #    wr_addr = i*32
        #    wr_addr_list.append(wr_addr)
        #    wr_data_list = []
        #    for j in range(8):
        #        wr_data_list.append(random.randint(0,0xffffffff))
        #    exp_dict[wr_addr] = wr_data_list
        #    test_api.mram_mtp_write(wr_addr, wr_data_list, rand_shuffle=1)
        #Check_result(wr_addr_list, exp_dict, frontdoor=1)

        #helper.log("#2, Test the end addresses with wr_data/addr's configurations in order")
        #exp_dict = {}
        #wr_addr_list = []
        #for i in range(128*1024-2, 128*1024):
        #    wr_addr = i*32+random.randint(0,31)
        #    wr_addr_list.append(wr_addr)
        #    wr_data_list = []
        #    for j in range(8):
        #        wr_data_list.append(random.randint(0,0xffffffff))
        #    exp_dict[wr_addr] = wr_data_list
        #    test_api.mram_mtp_write(wr_addr, wr_data_list, rand_shuffle=1)

        #Check_result(wr_addr_list, exp_dict, frontdoor=1)


        #helper.log("#3, Test the middle addresses with wr_data/addr's configurations in order")
        #exp_dict = {}
        #wr_addr_list = []
        #for i in range(64*1024-1, 64*1024):
        #    #wr_addr = i*32+random.randint(0,31)
        #    wr_addr = int("1ffff2", 16)
        #    wr_addr_list.append(wr_addr)
        #    wr_data_list = []
        #    for j in range(8):
        #        wr_data_list.append(random.randint(0,(1<<32)-1))
        #    exp_dict[wr_addr] = wr_data_list
        #    test_api.mram_mtp_write(wr_addr, wr_data_list, rand_shuffle=1)

        #Check_result(wr_addr_list, exp_dict, frontdoor=1)


        #helper.log("#4, Test the middle addresses with wr_data/addr's configurations in order")
        #exp_dict = {}
        #wr_addr_list = []
        #for i in range(2):
        #    wr_addr = random.randint(0, (128*1024-1))*32
        #    wr_addr_list.append(wr_addr)
        #    wr_data_list = []
        #    for j in range(8):
        #        wr_data_list.append(random.randint(0,0xffffffff))
        #    exp_dict[wr_addr] = wr_data_list
        #    test_api.mram_mtp_write(wr_addr, wr_data_list, rand_shuffle=1)

        #Check_result(wr_addr_list, exp_dict, frontdoor=1)


        #helper.log("#5, access the same 256bits")
        #exp_dict = {}
        #wr_addr_list = []
        #for i in range(2):
        #    wr_addr = 0
        #    wr_addr_list.append(wr_addr)
        #    wr_data_list = []
        #    for j in range(8):
        #        wr_data_list.append(random.randint(0,0xffffffff))
        #    exp_dict[wr_addr] = wr_data_list
        #    test_api.mram_mtp_write(wr_addr, wr_data_list, rand_shuffle=1)

        #Check_result(wr_addr_list, exp_dict, frontdoor=1)

        #exp_dict = {}
        #wr_addr_list = []
        #wr_addr_256b = random.randint(0, (128*1024-1))
        #for i in range(5):
        #    wr_addr = wr_addr_256b*32
        #    wr_addr_list.append(wr_addr)
        #    wr_data_list = []
        #    for j in range(8):
        #        wr_data_list.append(random.randint(0,0xffffffff))
        #    exp_dict[wr_addr] = wr_data_list
        #    test_api.mram_mtp_write(wr_addr, wr_data_list, rand_shuffle=1)

        #Check_result(wr_addr_list, exp_dict, frontdoor=1)

        #helper.log("#6, access out of 4MB")
        #exp_dict = {}
        #wr_addr_list = []
        #for i in range(2):
        #    if i == 4:
        #        wr_addr = (128*1024+32+i)*32+random.randint(0,31)
        #    else:
        #        wr_addr = (128*1024+i)*32
        #    wr_addr_list.append(wr_addr)
        #    wr_data_list = []
        #    for j in range(8):
        #        wr_data_list.append(random.randint(0,0xffffffff))
        #    exp_dict[wr_addr] = wr_data_list
        #    test_api.mram_mtp_write(wr_addr, wr_data_list, rand_shuffle=1)
        #    rd = mram.mram_mtp_wport_state_0.read()
        #    if rd['ERROR'] != 1:
        #        helper.perror("Write to out of region should get an ERROR")
        #    mram.mram_mtp_wport_state_0.write(ERROR=0)
        #    mram.mram_mtp_wport_state_0.write(ERROR=1)

        #Check_result(wr_addr_list, exp_dict, frontdoor=1, expect_fail=1)
        #rd = mram.mram_mtp_rport_state_0.read()
        #if rd['ERROR'] != 1:
        #    helper.perror("Read to out of region should get an ERROR")
        #mram.mram_mtp_rport_state_0.write(ERROR=0)
        #mram.mram_mtp_rport_state_0.write(ERROR=1)
    else:
        helper.log("#1, Test the start addresses with wr_data/addr's configurations")
        exp_dict = {}
        wr_addr_list = []
        for i in range(80):
            wr_addr = i*32
            wr_addr_list.append(wr_addr)
            wr_data_list = []
            for j in range(8):
                wr_data_list.append(random.randint(0,0xffffffff))
            exp_dict[wr_addr] = wr_data_list
            mram_mtp_write(wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)
        Check_result(wr_addr_list, exp_dict, frontdoor=0)
        Check_result(wr_addr_list, exp_dict, frontdoor=1)

        helper.log("#2, Test the end addresses with wr_data/addr's configurations in order")
        exp_dict = {}
        wr_addr_list = []
        for i in range(128*1024-80, 128*1024):
            wr_addr = i*32+random.randint(0,31)
            wr_addr_list.append(wr_addr)
            wr_data_list = []
            for j in range(8):
                wr_data_list.append(random.randint(0,0xffffffff))
            exp_dict[wr_addr] = wr_data_list
            mram_mtp_write(wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)

        Check_result(wr_addr_list, exp_dict, frontdoor=0)
        Check_result(wr_addr_list, exp_dict, frontdoor=1)


        helper.log("#3, Test the middle addresses with wr_data/addr's configurations in order")
        exp_dict = {}
        wr_addr_list = []
        for i in range(64*1024-50, 64*1024+50):
            wr_addr = i*32+random.randint(0,31)
            wr_addr_list.append(wr_addr)
            wr_data_list = []
            for j in range(8):
                wr_data_list.append(random.randint(0,(1<<32)-1))
            exp_dict[wr_addr] = wr_data_list
            mram_mtp_write(wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)

        Check_result(wr_addr_list, exp_dict, frontdoor=0)
        Check_result(wr_addr_list, exp_dict, frontdoor=1)


        helper.log("#4, Test the middle addresses with wr_data/addr's configurations in order")
        exp_dict = {}
        wr_addr_list = []
        for i in range(100):
            wr_addr = random.randint(0, (128*1024-1))*32
            wr_addr_list.append(wr_addr)
            wr_data_list = []
            for j in range(8):
                wr_data_list.append(random.randint(0,0xffffffff))
            exp_dict[wr_addr] = wr_data_list
            mram_mtp_write(wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)

        Check_result(wr_addr_list, exp_dict, frontdoor=0)
        Check_result(wr_addr_list, exp_dict, frontdoor=1)


        helper.log("#5, access the same 256bits")
        exp_dict = {}
        wr_addr_list = []
        for i in range(10):
            wr_addr = 0
            wr_addr_list.append(wr_addr)
            wr_data_list = []
            for j in range(8):
                wr_data_list.append(random.randint(0,0xffffffff))
            exp_dict[wr_addr] = wr_data_list
            mram_mtp_write(wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)

        Check_result(wr_addr_list, exp_dict, frontdoor=0)
        Check_result(wr_addr_list, exp_dict, frontdoor=1)

        exp_dict = {}
        wr_addr_list = []
        wr_addr_256b = random.randint(0, (128*1024-1))
        for i in range(10):
            wr_addr = wr_addr_256b*32
            wr_addr_list.append(wr_addr)
            wr_data_list = []
            for j in range(8):
                wr_data_list.append(random.randint(0,0xffffffff))
            exp_dict[wr_addr] = wr_data_list
            mram_mtp_write(wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)

        Check_result(wr_addr_list, exp_dict, frontdoor=0)
        Check_result(wr_addr_list, exp_dict, frontdoor=1)

        helper.log("#6, access out of 4MB")
        exp_dict = {}
        wr_addr_list = []
        for i in range(5):
            if i == 4:
                wr_addr = (128*1024+32+i)*32+random.randint(0,31)
            else:
                wr_addr = (128*1024+i)*32
            wr_addr_list.append(wr_addr)
            wr_data_list = []
            for j in range(8):
                wr_data_list.append(random.randint(0,0xffffffff))
            exp_dict[wr_addr] = wr_data_list
            mram_mtp_write(wr_addr, wr_data_list, priv_id=2, rand_shuffle=1)
            rd = mram.mram_mtp_wport_state_0.read()
            if rd['ERROR'] != 1:
                helper.perror("Write to out of region should get an ERROR")
            mram.mram_mtp_wport_state_0.write(ERROR=0)
            mram.mram_mtp_wport_state_0.write(ERROR=1)

        Check_result(wr_addr_list, exp_dict, frontdoor=0, expect_fail=1)
        Check_result(wr_addr_list, exp_dict, frontdoor=1, expect_fail=1)
        rd = mram.mram_mtp_rport_state_0.read()
        if rd['ERROR'] != 1:
            helper.perror("Read to out of region should get an ERROR")
        mram.mram_mtp_rport_state_0.write(ERROR=0)
        mram.mram_mtp_rport_state_0.write(ERROR=1)

    helper.log("Test done")
