#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
#This test ensure that JTAG can exchange rcv image with FSP using INDIRECT_DATA
from driver import *
import random

def indirect_cms_access(data):
    data_in = data & 0xffffffff
    #J2H write to INDIRECT_DATA
    #erot.OOBHUB.RCV_INDIRECT_DATA_0.write_headless(data_in)
    erot.OOBHUB.RCV_INDIRECT_DATA_0.debug_write(data_in)
    helper.pinfo(f'J2H write RCV_INDIRECT_DATA_0 with {hex(data_in)}')
    #FSP read RCV_INDIRECT_DATA
    rd = erot.OOBHUB.RCV_INDIRECT_DATA_0.read()
    if rd.value != data_in:
        helper.perror("FSP read RCV_INDIRECT_DATA_0 Fail, expect 0x%x but read out 0x%x" % (data_in, rd.value))
    else:
        helper.pinfo(f'FSP read out RCV_INDIRECT_DATA_0 {hex(rd.value)}')

def indirect_cms2_access():
    #FSP writes to INDRECT_CMS2_MEM_ADDR/DATA registers to load data (N DWORDS)
    data_l = []

    # several beats may have been locked by bootrom
    rd = erot.OOBHUB.RCV_INDIRECT_CMS2_MEM_LOCK_0.read()
    lock_size = rd['LOCKED_REGION_SIZE']

    mem_size = 0
    for field_obj in erot.OOBHUB.RCV_INDIRECT_CMS2_MEM_ADDR_0.field_list:
        if field_obj['name'] == "ADDR":
            msb, lsb = field_obj['msb'], field_obj['lsb']
            mem_size = (1<<(msb-lsb+1))
            break

    for i in range(lock_size, mem_size):
        wr_data = random.randint(0x0, 0xffffffff)
        data_l.append(wr_data)
        erot.OOBHUB.RCV_INDIRECT_CMS2_MEM_ADDR_0.write(i)
        erot.OOBHUB.RCV_INDIRECT_CMS2_MEM_DATA_0.write(wr_data)
        helper.pinfo(f'FSP write CMS2 addr{i} data with {hex(wr_data)}')
    #J2H read from INDRECT_CMS2_MEM_ADDR/DATA registers
    for i in range(lock_size, mem_size):
        exp_data = data_l[i-lock_size]
        erot.OOBHUB.RCV_INDIRECT_CMS2_MEM_RD_ADDR_0.debug_write(i)
        rd = erot.OOBHUB.RCV_INDIRECT_CMS2_MEM_RD_DATA_0.debug_read()
        if rd.value != exp_data:
            helper.perror(f'J2H read CMS2 addr{i} data Fail, expect {hex(exp_data)} but actual {hex(rd.value)}')
        else:
            helper.pinfo(f'J2H read CMS2 addr{i} data {hex(rd.value)}')

def peregrine_mailbox_access(data):
    data_in = data & 0xffffffff
    #J2H write to MAILBOX0
    erot.OOBHUB.PEREGRINE_FALCON_MAILBOX0_0.debug_write(data_in)
    helper.pinfo(f'J2H write PEREGRINE_FALCON_MAILBOX0_0 with {hex(data_in)}')
    #FSP read from MAILBOX0
    rd = erot.OOBHUB.PEREGRINE_FALCON_MAILBOX0_0.read()
    if rd.value != data_in:
        helper.perror(f'FSP read back PEREGRINE_FALCON_MAILBOX_0 Fail, expect {hex(data_in)} but actual {hex(rd.value)}')
    else:
        helper.pinfo(f'FSP read out PEREGRINE_FALCON_MAILBOX_0 {hex(rd.value)}')

with Test(sys.argv) as t:
    def parse_args():
        t.parser.add_argument("--unit", action='store', help="Unit To Light On, Support Regular Expression", default='.*')
        t.parser.add_argument("--fuse_set", action='store_true', help="fuse options set", default=False)
        opts, unknown = t.parser.parse_known_args(sys.argv[1:])
        return opts

    options = parse_args()

    if options.fuse_set == True:
        helper.hdl_force('ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.opt_secure_oobhub_device_reset_wr_secure', 1)
        helper.hdl_force('ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.opt_production_mode', 1)
        helper.hdl_force('ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.opt_security_mode', 1)
        helper.hdl_force('ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.opt_secure_pri_source_isolation_en', 1)
        helper.hdl_force('ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.opt_skate_secure_fusing_start', 1)
        helper.hdl_force('ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.opt_fsp_prod_sym_key_en', 1)
        helper.hdl_force('ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.opt_recovery_behavior_en', 1)
        helper.hdl_force('ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.u_fusegen_logic.u_ctrl.jtag_direct_access_disable', 1)
        helper.hdl_force('ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.u_fusegen_logic.u_intfc.opt_secure_scandebug_access_disable', 1)

    # Unlock J2H
    helper.wait_sim_time("us", 50)
    helper.hdl_force('ntb_top.u_nv_fpga_dut.u_nv_top_fpga.u_nv_top_wrapper.u_nv_top.nvjtag_sel', 1)

    helper.jtag.Reset(0)
    helper.jtag.DRScan(100, hex(0x0)) #add some delay as jtag only work when nvjtag_sel stable in real case
    helper.jtag.Reset(1)  

    #unlock j2h interface
    helper.pinfo(f'j2h_unlock sequence start')
    helper.j2h_unlock()
    helper.pinfo(f'j2h_unlock sequence finish') 


    #Test start
    for i in range(1):
        data_cms = random.randint(0x0, 0xffffffff)
        helper.log("Start indirect_cms_access")
        indirect_cms_access(data_cms)

        helper.log("Start indirect_cms2_access")
        indirect_cms2_access()

        data_mbx = random.randint(0x0, 0xffffffff)
        helper.log("Start peregrine_mailbox_access")
        peregrine_mailbox_access(data_mbx)
    
  
