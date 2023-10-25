#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import * 

###################################################
# This test intends to cover:
# 1. *addr[0] to L1/L2 fabric targets
# 2. *_req_priv_level from fabric to L1 targets
# 3. *_req_source_id from fabric to L1 targets
###################################################
with Test(sys.argv) as t:
    def parse_args():
        t.parser.add_argument("--Fabric", action='store', help="Accessing upper and lower boundary of L1/L2 fabric targets", default='L1')
        opts, unknown = t.parser.parse_known_args(sys.argv[1:])
        return opts

    fuse_path = 'ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.'
    L1_FABRIC_TARGET = [
#        {'name' : 'OOBHUB',      'addr_upper_boundary' : 0x8abffc,      'addr_lower_boundary' : 0x8a8000},
#        {'name' : 'FUSE',        'addr_upper_boundary' : 0x827ffc,      'addr_lower_boundary' : 0x820000},
#        {'name' : 'SYSCTRL',     'addr_upper_boundary' : 0x22ffc,       'addr_lower_boundary' : 0       }, #NVPTOP, NV_PMC
#        {'name' : 'CLOCK',       'addr_upper_boundary' : 0x29ffc,       'addr_lower_boundary' : 0x23000 },
#        {'name' : 'RESET',       'addr_upper_boundary' : 0x34ffc,       'addr_lower_boundary' : 0x33000 },
#        {'name' : 'THERM',       'addr_upper_boundary' : 0x2ffc,        'addr_lower_boundary' : 0x2000  },
#        {'name' : 'RTS',         'addr_upper_boundary' : 0x4a4ffc,      'addr_lower_boundary' : 0x4a3000},
#        {'name' : 'MRAM',        'addr_upper_boundary' : 0x13ffffc,     'addr_lower_boundary' : 0xfc0000},
#        {'name' : 'BT_QSPI',     'addr_upper_boundary' : 0x44ffc,       'addr_lower_boundary' : 0x43000 }, #upper boundary of boot_qspi_core
#        {'name' : 'QSPI0',       'addr_upper_boundary' : 0x147ffc,      'addr_lower_boundary' : 0x146000},
#        {'name' : 'QSPI1',       'addr_upper_boundary' : 0x24affc,      'addr_lower_boundary' : 0x249000},
#        {'name' : 'SPI_MON0',    'addr_upper_boundary' : 0x472ffc,      'addr_lower_boundary' : 0x463000},
#        {'name' : 'SPI_MON1',    'addr_upper_boundary' : 0x492ffc,      'addr_lower_boundary' : 0x483000},
#        {'name' : 'PUF_DBG',     'addr_upper_boundary' : 0x4a5ffc,      'addr_lower_boundary' : 0x4a5000},
        {'name' : 'L1_CSR',      'addr_upper_boundary' : 0x13ffc,       'addr_lower_boundary' : 0x13000 },
#        {'name' : 'JTAG',        'addr_upper_boundary' : 0x4a63fc,      'addr_lower_boundary' : 0x4a6000},
    ]

    L2_FABRIC_TARGET = [
#        {'name' : 'FSP',            'addr_upper_boundary' : 0x8f3ffc,   'addr_lower_boundary' : 0x8f0000},
#        {'name' : 'OOBHUB_SPI',     'addr_upper_boundary' : 0x903ffc,   'addr_lower_boundary' : 0x8f4000},
#        {'name' : 'SPI_IB0',        'addr_upper_boundary' : 0x913ffc,   'addr_lower_boundary' : 0x904000},
#        {'name' : 'I2C_IB0',        'addr_upper_boundary' : 0x923ffc,   'addr_lower_boundary' : 0x914000},
#        {'name' : 'I3C_IB0',        'addr_upper_boundary' : 0x933ffc,   'addr_lower_boundary' : 0x924000},
#        {'name' : 'SPI_IB1',        'addr_upper_boundary' : 0x943ffc,   'addr_lower_boundary' : 0x934000},
#        {'name' : 'I2C_IB1',        'addr_upper_boundary' : 0x953ffc,   'addr_lower_boundary' : 0x944000},
#        {'name' : 'I3C_IB1',        'addr_upper_boundary' : 0x963ffc,   'addr_lower_boundary' : 0x954000},
#        {'name' : 'IO_EXPANDER',    'addr_upper_boundary' : 0x973ffc,   'addr_lower_boundary' : 0x964000},
#        {'name' : 'UART',           'addr_upper_boundary' : 0x983ffc,   'addr_lower_boundary' : 0x974000},
#        {'name' : 'GPIO',           'addr_upper_boundary' : 0x98cffc,   'addr_lower_boundary' : 0x984000},
#        {'name' : 'PADCTRL_N',      'addr_upper_boundary' : 0x994ffc,   'addr_lower_boundary' : 0x994000,   'lowest_reg_addr' : 0x994038},
#        {'name' : 'PADCTRL_S',      'addr_upper_boundary' : 0x998ffc,   'addr_lower_boundary' : 0x998000},
#        {'name' : 'PADCTRL_E',      'addr_upper_boundary' : 0x99cffc,   'addr_lower_boundary' : 0x99c000},
#        {'name' : 'PADCTRL_W',      'addr_upper_boundary' : 0x9a0ffc,   'addr_lower_boundary' : 0x9a0000},
        {'name' : 'L2_CSR',         'addr_upper_boundary' : 0x9a4ffc,   'addr_lower_boundary' : 0x9a4000},
    ]

    def L3_reset():
        erot.RESET.NVEROT_RESET_CFG.SW_L3_RST_0.write(0, 1)
        helper.log("L3 Reset Triggered")
        #Wait reset finish
        helper.wait_sim_time("us", 2)
        test_api.clk_init()
        test_api.reset_init()
        erot.RESET.NVEROT_RESET_CFG.SW_L3_RST_0.poll(RESET_LEVEL3=1)
        helper.log("L3 Reset Recovered")

    def check_ip(target, boundary, write_value, priv_id, priv_level):
        helper.log("Accessing %s by writing %x" % (target['name'], write_value))
        if(priv_id == 0):
            if  helper.target in ["fpga", "simv_fpga"]:
                helper.log("use JTAG to access the %s" % (target['name']))
                helper.j2h_write(target[boundary], write_value)
                read_value = helper.j2h_read(target[boundary])
                if((target['name'] == 'L1_CSR' or target['name'] == 'L2_CSR') and (boundary == 'addr_upper_boundary')):
                    if(read_value != 0xdead1001):
                        helper.perror("read_rdata value mismatch, exp: %x, act: %x" %(0xdead1001, read_value))
                elif(boundary == 'addr_lower_boundary'):
                    if(read_value != write_value):
                        helper.perror("read_rdata value mismatch with write value, exp: %x, act: %x" %(write_value, read_value))
                helper.log("Read value from %s: %x" %(target['name'], read_value))
            else:
                helper.write(target[boundary], write_value, 0, priv_level)
                read_value = helper.read(target[boundary], 0, priv_level)
                if((target['name'] == 'L1_CSR' or target['name'] == 'L2_CSR') and (boundary == 'addr_upper_boundary')):
                    if(read_value != 0xdead1001):
                        helper.perror("read_rdata value mismatch, exp: %x, act: %x" %(0xdead1001, read_value))
                elif(boundary == 'addr_lower_boundary'):
                    if(read_value != write_value):
                        helper.perror("read_rdata value mismatch with write value, exp: %x, act: %x" %(write_value, read_value))
                helper.log("Read value from %s: %x" %(target['name'], read_value))
        else:
            if helper.target in ["fpga", "simv_fpga"]:
                helper.write(target[boundary], write_value)
                read_value = helper.read(target[boundary])
                helper.log("Read value from %s: %x" % (target['name'], read_value))
                if((target['name'] == 'L1_CSR' or target['name'] == 'L2_CSR') and (boundary == 'addr_upper_boundary')):
                    if(read_value != 0xdead1001):
                        helper.perror("read_rdata value mismatch, exp: %x, act: %x" %(0xdead1001, read_value))
                elif(boundary == 'addr_lower_boundary'):
                    if(read_value != write_value):
                        helper.perror("read_rdata value mismatch with write value, exp: %x, act: %x" %(write_value, read_value))
            else:
                addr_list = []
                data_list = []
                cmd_list = []
                addr_list.append(target[boundary])
                data_list.append(write_value)
                cmd_list.append(3)
                write_return_list = helper.burst_operation(addr_list, data_list, cmd_list, priv_id, 0, priv_level)#addr_list, data_list, cmd_list, priv_id, wait_tick, priv_level
                write_rdata = write_return_list[0][0]
                write_resp_err = write_return_list[1][0]
                if((target['name'] == 'L1_CSR' or target['name'] == 'L2_CSR') and (boundary == 'addr_upper_boundary')):
                    if(write_rdata != 0xdead1001):
                        helper.perror("write_rdata value mismatch, exp: %x, act: %x" %(0xdead1001, write_rdata))
                    if(write_resp_err != 1):
                        helper.perror("write_resp_err value mismatch, exp: %x, act: %x" %(1, write_resp_err))
                cmd_list = []
                cmd_list.append(0)
                read_return_list = helper.burst_operation(addr_list, data_list, cmd_list, priv_id, 0, priv_level)
                read_rdata = read_return_list[0][0]
                read_resp_err = read_return_list[1][0]
                helper.log("Read value from %s: %x" % (target['name'], read_rdata))
                if((target['name'] == 'L1_CSR' or target['name'] == 'L2_CSR') and (boundary == 'addr_upper_boundary')):
                    if(read_rdata != 0xdead1001):
                        helper.perror("read_rdata value mismatch, exp: %x, act: %x" %(0xdead1001, read_rdata))
                    if(read_resp_err != 1):
                        helper.perror("read_resp_err value mismatch, exp: %x, act: %x" %(1, read_resp_err))
    
    options = parse_args()
   #test_api.boot_qspi_init()
   #test_api.boot_qspi_clk_init()
   #test_api.padctl_init()

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
        
        helper.pinfo(f'test the addr_upper_boundary')
        if(options.Fabric == 'L1'):
            for target in L1_FABRIC_TARGET:
                check_ip(target, 'addr_upper_boundary', 0xffffffff, 0, 3) #use jtag to access, PL3
        elif(options.Fabric == 'L2'):
            for target in L2_FABRIC_TARGET:
                check_ip(target, 'addr_upper_boundary', 0xffffffff, 0, 3) #use jtag to access, PL3
        
        helper.pinfo(f'test the addr_lower_boundary')
        if(options.Fabric == 'L1'):
            for target in L1_FABRIC_TARGET:
                if helper.target in ["fpga", "simv_fpga"]:
                    check_ip(target, 'addr_lower_boundary', 0xffffffff, 0, 0) #use jtag to access, PL0
                else:
                    check_ip(target, 'addr_lower_boundary', 0xffffffff, 0, 0) #use jtag to access, PL0
                #check_ip(target, 'addr_lower_boundary', 0, 0, 0) #use jtag to access, PL0
        elif(options.Fabric == 'L2'):
            for target in L2_FABRIC_TARGET:
                check_ip(target, 'addr_lower_boundary', 0xffffffff, 0, 0) #use jtag to access, PL0
                # To toggle nverot_fabric_l2_apb_source_fab2padctrl_n_prdata[31]
                if(target['name'] == 'PADCTRL_N'):
                    check_ip(target, 'lowest_reg_addr', 0x11df, 0, 0) # write value == write mask

        helper.log("Force fabric fuse 1 start")
        test_api.fuse_opts_override("opt_secure_pri_source_isolation_en", 1)
        test_api.fuse_opts_override("opt_priv_sec_en", 1)
        helper.log("Force fabric fuse 1 done")

        if(options.Fabric == 'L1'):
            for target in L1_FABRIC_TARGET:
                check_ip(target, 'addr_upper_boundary', 0, 0, 0) #use jtag to access
        elif(options.Fabric == 'L2'):
            for target in L2_FABRIC_TARGET:
                check_ip(target, 'addr_upper_boundary', 0, 0, 0) #use jtag to access, PL0
        

        if(options.Fabric == 'L1'):
            for target in L1_FABRIC_TARGET:
                check_ip(target, 'addr_lower_boundary', 0, 0, 0) #use jtag to access, PL0
        elif(options.Fabric == 'L2'):
            for target in L2_FABRIC_TARGET:
                check_ip(target, 'addr_lower_boundary', 0, 0, 0) #use jtag to access, PL0
                # To toggle nverot_fabric_l2_apb_source_fab2padctrl_n_prdata[31]
                if(target['name'] == 'PADCTRL_N'):
                    check_ip(target, 'lowest_reg_addr', 0, 0, 0)

    else:
        if(options.Fabric == 'L1'):
            for target in L1_FABRIC_TARGET:
                check_ip(target, 'addr_upper_boundary', 0xffffffff, 0, 3) #use jtag to access, PL3
        elif(options.Fabric == 'L2'):
            for target in L2_FABRIC_TARGET:
                check_ip(target, 'addr_upper_boundary', 0xffffffff, 3, 3) #use oobhub to access, PL3
        
        helper.log("Force fabric fuse 1 start")
        helper.hdl_force(fuse_path+'opt_priv_sec_en', 1)
        helper.hdl_force(fuse_path+'opt_secure_pri_source_isolation_en', 1)
        helper.log("Force fabric fuse 1 done")

        if(options.Fabric == 'L1'):
            for target in L1_FABRIC_TARGET:
                check_ip(target, 'addr_upper_boundary', 0, 1, 0) #use sysctrl to access, PL0
        elif(options.Fabric == 'L2'):
            for target in L2_FABRIC_TARGET:
                check_ip(target, 'addr_upper_boundary', 0, 3, 0) #use oobhub to access, PL0
        
        helper.log("Force fabric fuse 0 start")
        helper.hdl_force(fuse_path+'opt_priv_sec_en', 0)
        helper.hdl_force(fuse_path+'opt_secure_pri_source_isolation_en', 0)
        helper.log("Force fabric fuse 0 done")

        if(options.Fabric == 'L1'):
            for target in L1_FABRIC_TARGET:
                check_ip(target, 'addr_lower_boundary', 0xffffffff, 1, 0) #use sysctrl to access, PL0
                #check_ip(target, 'addr_lower_boundary', 0, 0, 0) #use jtag to access, PL0
        elif(options.Fabric == 'L2'):
            for target in L2_FABRIC_TARGET:
                check_ip(target, 'addr_lower_boundary', 0xffffffff, 3, 0) #use oobhub to access, PL0
                # To toggle nverot_fabric_l2_apb_source_fab2padctrl_n_prdata[31]
                if(target['name'] == 'PADCTRL_N'):
                    check_ip(target, 'lowest_reg_addr', 0x11df, 3, 0) # write value == write mask
        
        helper.log("Force fabric fuse 1 start")
        helper.hdl_force(fuse_path+'opt_priv_sec_en', 1)
        helper.hdl_force(fuse_path+'opt_secure_pri_source_isolation_en', 1)
        helper.log("Force fabric fuse 1 done")

        if(options.Fabric == 'L1'):
            for target in L1_FABRIC_TARGET:
                check_ip(target, 'addr_lower_boundary', 0, 0, 0) #use jtag to access, PL0
        elif(options.Fabric == 'L2'):
            for target in L2_FABRIC_TARGET:
                check_ip(target, 'addr_lower_boundary', 0, 3, 0) #use oobhub to access, PL0
                # To toggle nverot_fabric_l2_apb_source_fab2padctrl_n_prdata[31]
                if(target['name'] == 'PADCTRL_N'):
                    check_ip(target, 'lowest_reg_addr', 0, 3, 0)

        #to toggle source_id:
        helper.log("Force fabric fuse 0 start")
        helper.hdl_force(fuse_path+'opt_priv_sec_en', 0)
        helper.hdl_force(fuse_path+'opt_secure_pri_source_isolation_en', 0)
        helper.log("Force fabric fuse 0 done")

        if(options.Fabric == 'L1'):
            for target in L1_FABRIC_TARGET:
                check_ip(target, 'addr_upper_boundary', 0, 0, 0) #source_id == 1f
        elif(options.Fabric == 'L2'):
            for target in L2_FABRIC_TARGET:
                check_ip(target, 'addr_upper_boundary', 0, 3, 0) #source_id == 1f
            
    helper.log("test finish")
