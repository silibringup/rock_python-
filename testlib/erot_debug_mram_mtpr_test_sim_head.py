#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import *
import random

with Test(sys.argv) as t:
    mram = erot.MRAM
    exp_addr_data_dist = {}
    MRAM_MTPR_BASE = mram.base + int(64*1024*4)
    MRAM_MTPR_SIZE = int(4*1024*1024)

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
                wr_data_reg = mram.get_reg_by_name("mram_mtp_wport_data_" + str(i) + "_0")
                wr_data_reg.write(VAL=data_list[i])
            else:
                mram.mram_mtp_wport_addr_0.write(VAL=addr)
        mram.mram_mtp_wport_cmd_0.write(TRIG=1)
        mram.mram_mtp_wport_state_0.poll(BUSY=0)
    def mram_mtp_read(addr):
        mram.mram_mtp_rport_addr_0.write(VAL=addr)
        mram.mram_mtp_rport_cmd_0.write(TRIG=1)
        mram.mram_mtp_rport_state_0.poll(BUSY=0)
        rd_data_list = []
        for i in range(8):
            rd_data_reg = mram.get_reg_by_name("mram_mtp_rport_data_" + str(i) + "_0")
            rd = rd_data_reg.read()
            rd_data_list.append(rd['VALUE'])
        return rd_data_list



    def check_rd_result(addr_list, act_data_list):
        if len(addr_list) != len(act_data_list):
            helper.perror("Addr-Actdata length mismatch")
            return
        for i in range(len(act_data_list)):
            if act_data_list[i] != exp_addr_data_dist[addr_list[i]]:
                helper.perror("Mismatch, Addr: %x, Act: %x, Exp: %x" % (addr_list[i], act_data_list[i], exp_addr_data_dist[addr_list[i]]))

    helper.log("Test start")
    mram.mram_cfg_b_mtp_wport_acl_0_0.update(out_region=1)
    mram.mram_cfg_b_mtp_rport_acl_0_0.update(out_region=1)


    helper.log("Step 1: Init the start 100*256b in MRAM")
    for i in range(100):
        wr_addr = i*32
        abs_addr = MRAM_MTPR_BASE + wr_addr
        wr_data_list = []
        for j in range(8):
            exp_data = random.randint(0,(1<<32)-1)
            #exp_data = 0xaa063029
            #exp_data = 0x0
            wr_data_list.append(exp_data)
            exp_addr_data_dist[abs_addr + j*4] = exp_data
        mram_mtp_write(wr_addr, wr_data_list, rand_shuffle=1)
    helper.log("Finish initialization")


    helper.log("#1, MPTR continuously read per 32b at start addr")
    addr_list = []
    act_rdata_list = []
    for i in range(500):
        addr_list.append(MRAM_MTPR_BASE+i*4)
        act_rdata_list.append(helper.read(MRAM_MTPR_BASE+i*4))
    check_rd_result(addr_list, act_rdata_list)

    helper.log("#2, MTPR read interleave on different 256b")
    addr_list = []
    act_rdata_list = []
    for i in range(80):
        addr_list.append(MRAM_MTPR_BASE+i*32)
        act_rdata_list.append(helper.read(MRAM_MTPR_BASE+i*32))
    check_rd_result(addr_list, act_rdata_list)

    helper.log("#3, MTPR mix ")
    addr_list = []
    act_rdata_list = []
    for i in range(80):
        addr = random.randint(MRAM_MTPR_BASE, MRAM_MTPR_BASE+32*100-1)
        addr = ((addr>>2)<<2)
        addr_list.append(addr)
        act_rdata_list.append(helper.read(addr))

    check_rd_result(addr_list, act_rdata_list)

    helper.log("Test done")
