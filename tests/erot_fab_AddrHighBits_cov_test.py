#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import *

###################################################
# This test intends to cover:
# 1. *req_addr[0] and *req_addr[25] from 4 masters
# 2. *_resp_pri_error from fabric to master
###################################################
with Test(sys.argv) as t:
    fuse_path = 'ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.'

    ##force these two fuse to fabric to 1 to enable all source_id and priv level
    if helper.target in ["fpga", "simv_fpga"]:
        helper.log("FPGA cannot control the fuse now")
    else:
        helper.log("Force fabric fuse start")
        helper.hdl_force(fuse_path+'opt_priv_sec_en', 1)
        helper.hdl_force(fuse_path+'opt_secure_pri_source_isolation_en', 1)
        helper.log("Force fabric fuse done")

    #Access with j2h
    if helper.target in ["fpga", "simv_fpga"]:
        helper.log("FPGA will use j2h to access the invalid address later")
    else:
        helper.log("Accessing with priv_id 0")
        helper.write(0x3ffffff, 0xffffffff, 0)
        read_value = helper.read(0x3ffffff, 0)
        helper.log("Read value: %x" % read_value)

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
        fpga_rdata = helper.j2h_read(0x3ffffff)
        if (fpga_rdata != 0xbadf5040):
            helper.perror("j2h fpga_rdata value mismatch, exp: %x, act: %x" %(0xbadf5040, fpga_rdata))
        else:
            helper.log("get the correct error code")
    else:
        #SYSCTRL, FSP and OOBHUB
        for priv_id in range(1, 4):
           #helper.log("Accessing with priv_id %d" % i)
           #helper.write(0x3ffffff, 0xffffffff, i)
           #read_value = helper.read(0x3ffffff, i)
           #helper.log("Read value: %x" % read_value)
            helper.log("Accessing with priv_id %d" %priv_id)
            addr_list = [0x3ffffff]
            data_list = [0xffffffff]
            cmd_list = [3]
            write_return_list = helper.burst_operation(addr_list, data_list, cmd_list, priv_id)#addr_list, data_list, cmd_list, priv_id, wait_tick, priv_level
            write_rdata = write_return_list[0][0]
            write_resp_err = write_return_list[1][0]
            if(write_rdata != 0xbadf5040):
                helper.perror("write_rdata value mismatch, exp: %x, act: %x" %(0xbadf5040, write_rdata))
            if(write_resp_err != 1):
                helper.perror("write_resp_err value mismatch, exp: %x, act: %x" %(1, write_resp_err))
            cmd_list = [0]
            read_return_list = helper.burst_operation(addr_list, data_list, cmd_list, priv_id)
            read_rdata = read_return_list[0][0]
            read_resp_err = read_return_list[1][0]
            if(read_rdata != 0xbadf5040):
                helper.perror("read_rdata value mismatch, exp: %x, act: %x" %(0xbadf5040, read_rdata))
            if(read_resp_err != 1):
                helper.perror("read_resp_err value mismatch, exp: %x, act: %x" %(1, read_resp_err))
    helper.log("test finish")
