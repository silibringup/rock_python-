#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import * 

with Test(sys.argv) as t:
    def parse_args():
        t.parser.add_argument("--Testpoint", action='store', help="", default='fuse_connection')
        t.parser.add_argument("--IP", action='store', help="", default='FSP')
        opts, unknown = t.parser.parse_known_args(sys.argv[1:])
        return opts

    fuse_path = 'ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.'
    FSP_PLM_LIST = [
        {'fuse_name' : 'opt_secure_sec_fault_config_wr_secure',         'reg': erot.PFSP.EMP_FSP_PRIV_LEVEL_MASK_0,              'field': 'WRITE_PROTECTION',   'fuse1': 0,   'protected_reg': erot.PFSP.EMP_FSP_CTRL_1_0,   'ip_name': 'FSP'},
        #{'fuse_name' : 'opt_secure_gin_intr_ctrl_wr_secure',            'reg': erot.PFSP.FALCON_INTR_CTRL_PRIV_LEVEL_MASK_0,     'field': 'WRITE_PROTECTION',   'fuse1': 12},
#error when poll register        {'fuse_name' : '0',                                             'reg': erot.PFSP.FALCON_BRKPT_PRIV_LEVEL_MASK_0,         'field': 'READ_PROTECTION'}, #opt_fpf_fsp_plm_init_val_flip_en0
#        {'fuse_name' : '0',                                             'reg': erot.PFSP.FALCON_HSCTL_PRIV_LEVEL_MASK_0,         'field': 'SOURCE_ENABLE'}, #opt_fpf_fsp_plm_init_val_flip_en1
#        {'fuse_name' : '0',                                             'reg': erot.PFSP.FALCON_DIODT_PRIV_LEVEL_MASK_0,         'field': 'SOURCE_ENABLE'}, #opt_fpf_fsp_plm_init_val_flip_en2
#        {'fuse_name' : '0',                                             'reg': erot.PFSP.FALCON_DBGCTL_PRIV_LEVEL_MASK_0,        'field': 'WRITE_PROTECTION'}, #opt_fpf_fsp_plm_init_val_flip_en3
#        {'fuse_name' : '0',                                             'reg': erot.PFSP.FALCON_ICD_PRIV_LEVEL_MASK_0,           'field': 'READ_PROTECTION'}, #opt_fpf_fsp_plm_init_val_flip_en4
#        {'fuse_name' : '0',                                             'reg': erot.PFSP.FALCON_SHA_RAL_PRIV_LEVEL_MASK_0,       'field': 'READ_PROTECTION'}, #opt_fpf_fsp_plm_init_val_flip_en5
        #{'fuse_name' : '0',                                             'reg': erot.PFSP.FALCON_ECC_PRIV_LEVEL_MASK_0,           'field': 'WRITE_PROTECTION'}, #opt_secure_sec_sram_ecc_wr_secure
#        {'fuse_name' : 'opt_fsp_peregrine_reserved[0]',                 'reg': erot.PFSP.FALCON_BOOTVEC_PRIV_LEVEL_MASK_0,       'field': 'SOURCE_ENABLE' ,     'fuse1': 0},
    ]
    FUSE_PLM_LIST = [
        {'fuse_name' : 'opt_secure_reshift_gpc_rail_wr_secure',         'reg': erot.FUSE.RESHIFT_GPC_RAIL_PRIV_LEVEL_MASK_0,                'field': 'WRITE_PROTECTION',  'fuse1': 12,  'protected_reg': erot.FUSE.SESHIFT_TRIGGER_0,   'ip_name': 'FUSE'},
        {'fuse_name' : 'opt_secure_fuse_iddqinfo_rd_secure',            'reg': erot.FUSE.IDDQINFO_PRIV_LEVEL_MASK_0,                        'field': 'READ_PROTECTION',   'fuse1': 12},
        {'fuse_name' : 'opt_secure_fuse_ctrl_wr_secure',                'reg': erot.FUSE.FUSECTRL_PRIV_LEVEL_MASK_0,                        'field': 'WRITE_PROTECTION',  'fuse1': 8},
        {'fuse_name' : 'opt_secure_fuse_debugctrl_wr_secure',           'reg': erot.FUSE.DEBUGCTRL_PRIV_LEVEL_MASK_0,                       'field': 'WRITE_PROTECTION',  'fuse1': 8},
        {'fuse_name' : 'opt_secure_fuse_wdata_wr_secure',               'reg': erot.FUSE.WDATA_PRIV_LEVEL_MASK_0,                           'field': 'WRITE_PROTECTION',  'fuse1': 8},
        {'fuse_name' : 'opt_secure_fuse_kappainfo_rd_secure',           'reg': erot.FUSE.KAPPAINFO_PRIV_LEVEL_MASK_0,                       'field': 'READ_PROTECTION',   'fuse1': 12},
        {'fuse_name' : 'opt_secure_fuse_speedoinfo_rd_secure',          'reg': erot.FUSE.SPEEDOINFO_PRIV_LEVEL_MASK_0,                      'field': 'READ_PROTECTION',   'fuse1': 12},
# this fuse cannot be changed        {'fuse_name' : 'opt_skate_and_brp_dev_mode_en',                 'reg': erot.FUSE.SKATE_SW_FUSING_PRIV_LEVEL_MASK_0,                 'field': 'WRITE_PROTECTION',  'fuse1': 15}, 
    ]
    SYSCTRL_PLM_LIST =[
        {'fuse_name' : '0',                                             'reg': erot.NV_PTOP.FS_SCRATCH_0_PRIV_LEVEL_MASK_0,     'field': 'WRITE_PROTECTION',   'protected_reg': erot.NV_PTOP.FS_SCRATCH_0_0,   'ip_name': 'SYSCTRL'}, #opt_secure_ptop_fs_scratch_wr_secure
        {'fuse_name' : 'opt_secure_pmc_iff_debug_wr_secure',            'reg': erot.NV_PMC.IFF_DEBUG_PRIV_LEVEL_MASK_0,         'field': 'WRITE_PROTECTION',  'fuse1': 8},
        {'fuse_name' : 'opt_secure_pmc_iff_debug_rd_secure',            'reg': erot.NV_PMC.IFF_DEBUG_PRIV_LEVEL_MASK_0,         'field': 'READ_PROTECTION',   'fuse1': 8},
        {'fuse_name' : 'opt_secure_sec_fault_config_wr_secure',         'reg': erot.NV_PMC.SEC_FAULT_PRIV_LEVEL_MASK_0,         'field': 'WRITE_PROTECTION',  'fuse1': 8},
        {'fuse_name' : '0',                                             'reg': erot.NV_PMC.GRP0_PRIV_LEVEL_MASK_0,              'field': 'WRITE_PROTECTION'}, #opt_secure_sysctrl_pmc_elpg_enable_wr_secure
        {'fuse_name' : '0',                                             'reg': erot.NV_PBUS.DEBUG_BUS_PRIV_LEVEL_MASK_0,        'field': 'WRITE_PROTECTION'}, #opt_secure_sysctrl_pbus_dbg_bus_wr_secure
    ]
    BT_QSPI_PLM_LIST =[
        {'fuse_name' : 'opt_secure_qspi_cmn_cmd_addr_filt_wr_secure',   'reg': erot.BOOT_QSPI.QSPI_PROT.CMD_ADDR_FILT_PRIV_LEVEL_MASK_0,  'field': 'WRITE_PROTECTION',  'fuse1': 8,   'protected_reg': erot.BOOT_QSPI.QSPI_COMMAND_ADDR_FILT.ADDR_RANGE_0,   'ip_name': 'BT_QSPI'},
        {'fuse_name' : 'opt_secure_qspi_cmn_mutex_override_wr_secure',  'reg': erot.BOOT_QSPI.QSPI_PROT.MUTEX_OVERRIDE_PRIV_LEVEL_MASK_0, 'field': 'WRITE_PROTECTION',  'fuse1': 8},
        {'fuse_name' : 'opt_secure_qspi_cmn_rbi_wr_secure',             'reg': erot.BOOT_QSPI.QSPI_PROT.RBI_PRIV_LEVEL_MASK_0,            'field': 'WRITE_PROTECTION',  'fuse1': 8},
        {'fuse_name' : 'opt_secure_qspi_cmn_secure_wr_secure',          'reg': erot.BOOT_QSPI.QSPI_PROT.SECURE_PRIV_LEVEL_MASK_0,         'field': 'WRITE_PROTECTION',  'fuse1': 8},
        {'fuse_name' : 'opt_secure_qspi_cmn_core_wr_secure',            'reg': erot.BOOT_QSPI.QSPI_PROT.CORE_PRIV_LEVEL_MASK_0,           'field': 'WRITE_PROTECTION',  'fuse1': 8},
    ]
    QSPI0_PLM_LIST =[
        {'fuse_name' : 'opt_secure_qspi_cmn_cmd_addr_filt_wr_secure',   'reg': erot.QSPI0.QSPI_PROT.CMD_ADDR_FILT_PRIV_LEVEL_MASK_0,      'field': 'WRITE_PROTECTION',  'fuse1': 8,   'protected_reg': erot.QSPI0.QSPI_COMMAND_ADDR_FILT.ADDR_RANGE_0,   'ip_name': 'QSPI0'},
        {'fuse_name' : 'opt_secure_qspi_cmn_mutex_override_wr_secure',  'reg': erot.QSPI0.QSPI_PROT.MUTEX_OVERRIDE_PRIV_LEVEL_MASK_0,     'field': 'WRITE_PROTECTION',  'fuse1': 8},
        {'fuse_name' : 'opt_secure_qspi_cmn_rbi_wr_secure',             'reg': erot.QSPI0.QSPI_PROT.RBI_PRIV_LEVEL_MASK_0,                'field': 'WRITE_PROTECTION',  'fuse1': 8},
        {'fuse_name' : 'opt_secure_qspi_cmn_secure_wr_secure',          'reg': erot.QSPI0.QSPI_PROT.SECURE_PRIV_LEVEL_MASK_0,             'field': 'WRITE_PROTECTION',  'fuse1': 8},
        {'fuse_name' : 'opt_secure_qspi_cmn_core_wr_secure',            'reg': erot.QSPI0.QSPI_PROT.CORE_PRIV_LEVEL_MASK_0,               'field': 'WRITE_PROTECTION',  'fuse1': 8},
    ]
    QSPI1_PLM_LIST =[
        {'fuse_name' : 'opt_secure_qspi_cmn_cmd_addr_filt_wr_secure',   'reg': erot.QSPI1.QSPI_PROT.CMD_ADDR_FILT_PRIV_LEVEL_MASK_0,      'field': 'WRITE_PROTECTION',  'fuse1': 8,   'protected_reg': erot.QSPI1.QSPI_COMMAND_ADDR_FILT.ADDR_RANGE_0,   'ip_name': 'QSPI1'},
        {'fuse_name' : 'opt_secure_qspi_cmn_mutex_override_wr_secure',  'reg': erot.QSPI1.QSPI_PROT.MUTEX_OVERRIDE_PRIV_LEVEL_MASK_0,     'field': 'WRITE_PROTECTION',  'fuse1': 8},
        {'fuse_name' : 'opt_secure_qspi_cmn_rbi_wr_secure',             'reg': erot.QSPI1.QSPI_PROT.RBI_PRIV_LEVEL_MASK_0,                'field': 'WRITE_PROTECTION',  'fuse1': 8},
        {'fuse_name' : 'opt_secure_qspi_cmn_secure_wr_secure',          'reg': erot.QSPI1.QSPI_PROT.SECURE_PRIV_LEVEL_MASK_0,             'field': 'WRITE_PROTECTION',  'fuse1': 8},
        {'fuse_name' : 'opt_secure_qspi_cmn_core_wr_secure',            'reg': erot.QSPI1.QSPI_PROT.CORE_PRIV_LEVEL_MASK_0,               'field': 'WRITE_PROTECTION',  'fuse1': 8},
    ]
    OOBHUB_PLM_LIST =[
        {'fuse_name' : 'opt_secure_oobhub_device_reset_wr_secure',      'reg': erot.OOBHUB.RCV_RESET_PLM_0,                                 'field': 'SOURCE_ENABLE',           'fuse1': 2048,  'protected_reg': erot.OOBHUB.RCV_RESET_0_0,     'ip_name': 'OOBHUB'},
        {'fuse_name' : 'opt_secure_gin_intr_ctrl_wr_secure',            'reg': erot.OOBHUB.PEREGRINE_FALCON_INTR_CTRL_PRIV_LEVEL_MASK_0,    'field': 'WRITE_PROTECTION',        'fuse1': 12},
#        {'fuse_name' : 'opt_oobhub_peregrine_reserved[0]',              'reg': erot.OOBHUB.PEREGRINE_FALCON_IDLESTATE_PRIV_LEVEL_MASK_0,    'field': 'WRITE_PROTECTION',        'fuse1': 0},
        {'fuse_name' : '0',                                             'reg': erot.OOBHUB.PEREGRINE_FALCON_BRKPT_PRIV_LEVEL_MASK_0,        'field': 'WRITE_PROTECTION'}, #opt_fpf_oobhub_plm_init_val_flip_en0
        {'fuse_name' : '0',                                             'reg': erot.OOBHUB.PEREGRINE_FALCON_HSCTL_PRIV_LEVEL_MASK_0,        'field': 'SOURCE_ENABLE'}, #opt_fpf_oobhub_plm_init_val_flip_en1
        {'fuse_name' : '0',                                             'reg': erot.OOBHUB.PEREGRINE_FALCON_DBGCTL_PRIV_LEVEL_MASK_0,       'field': 'WRITE_PROTECTION'}, #opt_fpf_oobhub_plm_init_val_flip_en3
        {'fuse_name' : '0',                                             'reg': erot.OOBHUB.PEREGRINE_FALCON_ICD_PRIV_LEVEL_MASK_0,          'field': 'WRITE_PROTECTION'}, #opt_fpf_oobhub_plm_init_val_flip_en4
    ]
    # source id and fuse both cannot be access now by jtag
    JTAG_PLM_LIST =[
        {'fuse_name' : 'opt_secure_pjtag_access_wr_secure',             'reg': 0x4a6040,                                        'fuse1': 8,     'protected_reg': 0x4a6004,                      'ip_name': 'JTAG'},
    ]
    THERM_PLM_LIST =[
        {'fuse_name' : '0',                                             'reg': erot.THERM.GPC_TSENSE_PRIV_LEVEL_MASK_0,         'field': 'WRITE_PROTECTION',                  'protected_reg': erot.THERM.GPC_TSENSE_0,   'ip_name': 'THERM'}, #opt_secure_tsense_wr_secure
        {'fuse_name' : '0',                                             'reg': erot.THERM.INTRUPT_PRIV_LEVEL_MASK_0,            'field': 'WRITE_PROTECTION'}, #opt_secure_therm_intrupt_wr_secure
        {'fuse_name' : '0',                                             'reg': erot.THERM.THERMAL_PRIV_LEVEL_MASK_LOW_0,        'field': 'WRITE_PROTECTION'}, #opt_secure_therm_thermal_low_wr_secure
        {'fuse_name' : '0',                                             'reg': erot.THERM.THERMAL_PRIV_LEVEL_MASK_MED_HIGH_0_0, 'field': 'WRITE_PROTECTION'}, #opt_secure_therm_thermal_med_high_0_wr_secure
        {'fuse_name' : '0',                                             'reg': erot.THERM.THERMAL_PRIV_LEVEL_MASK_MED_HIGH_1_0, 'field': 'WRITE_PROTECTION'}, #opt_secure_therm_thermal_med_high_1_wr_secure
    ]

    #FUSE_LIST = [FSP_PLM_LIST, FUSE_PLM_LIST, SYSCTRL_PLM_LIST, BT_QSPI_PLM_LIST, QSPI0_PLM_LIST, QSPI1_PLM_LIST, OOBHUB_PLM_LIST, THERM_PLM_LIST, JTAG_PLM_LIST]
    #FUSE_LIST = [FSP_PLM_LIST, FUSE_PLM_LIST, SYSCTRL_PLM_LIST, BT_QSPI_PLM_LIST, QSPI0_PLM_LIST, QSPI1_PLM_LIST, OOBHUB_PLM_LIST, THERM_PLM_LIST]
    FUSE_LIST = [FSP_PLM_LIST, FUSE_PLM_LIST, SYSCTRL_PLM_LIST, BT_QSPI_PLM_LIST, OOBHUB_PLM_LIST, THERM_PLM_LIST]
    FUSE_LIST_FOR_PL = [FUSE_PLM_LIST, SYSCTRL_PLM_LIST, BT_QSPI_PLM_LIST, QSPI0_PLM_LIST, OOBHUB_PLM_LIST, THERM_PLM_LIST]
 #   FUSE_LIST_FOR_SRCID = [FUSE_PLM_LIST]
    FUSE_LIST_FOR_SRCID = [FUSE_PLM_LIST, SYSCTRL_PLM_LIST, BT_QSPI_PLM_LIST, QSPI0_PLM_LIST, OOBHUB_PLM_LIST, THERM_PLM_LIST]
    #FUSE_LIST_FOR_SRCID = [FUSE_PLM_LIST, SYSCTRL_PLM_LIST, BT_QSPI_PLM_LIST, OOBHUB_PLM_LIST, THERM_PLM_LIST]
 #   FUSE_LIST = [FSP_PLM_LIST]

    SINGLE_PLM_FOR_PL = []
    for i in FUSE_LIST_FOR_PL:
        SINGLE_PLM_FOR_PL.append(i[0])
    
    SINGLE_PLM_FOR_SRCID = []
    for i in FUSE_LIST_FOR_SRCID:
        SINGLE_PLM_FOR_SRCID.append(i[0])
    
    SINGLE_PLM = []
    for i in FUSE_LIST:
        SINGLE_PLM.append(i[0])
        
    def check_value(reg, exp_value, priv_id, priv_level):
        if helper.target in ["fpga", "simv_fpga"]:
            if priv_id==0:
                read_value = reg.debug_read()
            elif priv_id==2:
                read_value = reg.read(2,3)
            elif priv_id==3:
                #read_value = test_api.oobhub_icd_read(reg.abs_addr)
                helper.perror("will use oobhub ict to read later")
            else:
                helper.perror("Cannot use sysctrl to read now")
            # therm 13:0 bits are read_only
            if reg == erot.THERM.GPC_TSENSE_0:
                read_val_check_part = read_value.value & 0xffffc000
                exp_value_check_part = exp_value & 0xffffc000
                if (read_val_check_part != exp_value_check_part):
                    helper.perror("Therm reg value mismatch, exp: %x, act: %x" %(exp_value_check_part, read_val_check_part))
            else:
                if(read_value.value != exp_value):
                    helper.perror("Reg value mismatch, exp: %x, act: %x" %(exp_value, read_value.value))
        else:
            read_value = reg.read(priv_id, priv_level)
            if(read_value.value != exp_value):
                helper.perror("Reg value mismatch, exp: %x, act: %x" %(exp_value, read_value.value))
    
    def L3_reset():
        if helper.target in ["fpga", "simv_fpga"]:
            erot.RESET.NVEROT_RESET_CFG.SW_L3_RST_0.debug_write(0,False)
        else:
            erot.RESET.NVEROT_RESET_CFG.SW_L3_RST_0.write(0, 1)
        helper.log("L3 Reset Triggered")
        #Wait reset finish
        helper.wait_sim_time("us", 2)
        helper.log("After wait for 2 us")
        if helper.target in ["fpga", "simv_fpga"]:
            helper.log("FPGA env does not need clk and reset init")
        else:
            test_api.clk_init()
            test_api.reset_init()
        helper.log("reset init done")
        if helper.target in ["fpga", "simv_fpga"]:
            erot.RESET.NVEROT_RESET_CFG.SW_L3_RST_0.debug_poll(RESET_LEVEL3=1)
        else:
            erot.RESET.NVEROT_RESET_CFG.SW_L3_RST_0.poll(RESET_LEVEL3=1)
        helper.log("L3 Reset Recovered")
   
    def check_fuse0(fuse):
        if helper.target in ["fpga", "simv_fpga"]:
            if(fuse['fuse_name'] == 'opt_secure_pjtag_access_wr_secure'):
                helper.log("check fuse0 with fuse name %s" % (fuse['fuse_name']))
                jtag_plm_value = helper.debug_read(fuse['reg'])
                if(jtag_plm_value != 0xffffffff):
                    helper.perror("JTAG fuse0 check fail, PLM register value is %d" %jtag_plm_value)
            else:
                helper.log("check fuse0 with fuse field %s" % (fuse['field']))
                if(fuse['field'] == 'SOURCE_ENABLE'):
                    helper.log("Polling SOURCE_ENABLE")
                    fuse['reg'].debug_poll(SOURCE_ENABLE=1048575)
                else:
                    if(fuse['field'] == 'WRITE_PROTECTION'):
                        helper.log("Polling WRITE_PROTECTION")
                        if(fuse['fuse_name'] == 'opt_skate_and_brp_dev_mode_en'):
                            fuse['reg'].debug_poll(WRITE_PROTECTION=0)
                        else:
                            helper.log("CHecking reg %s has WRITE_PROTECTION=15" % (fuse['reg']))
                            fuse['reg'].debug_poll(WRITE_PROTECTION=15)
                    elif(fuse['field'] == 'READ_PROTECTION'):
                        helper.log("Polling READ_PROTECTION")
                        fuse['reg'].debug_poll(READ_PROTECTION=15)
        else:
            if(fuse['fuse_name'] == 'opt_secure_pjtag_access_wr_secure'):
                jtag_plm_value = helper.read(fuse['reg'])
                if(jtag_plm_value != 0xffffffff):
                    helper.perror("JTAG fuse0 check fail, PLM register value is %d" %jtag_plm_value)
            else:
                if(fuse['field'] == 'SOURCE_ENABLE'):
                    fuse['reg'].poll(SOURCE_ENABLE=1048575)
                else:
                    if(fuse['field'] == 'WRITE_PROTECTION'):
                        if(fuse['fuse_name'] == 'opt_skate_and_brp_dev_mode_en'):
                            fuse['reg'].poll(WRITE_PROTECTION=0)
                        else:
                            fuse['reg'].poll(WRITE_PROTECTION=15)
                    elif(fuse['field'] == 'READ_PROTECTION'):
                        fuse['reg'].poll(READ_PROTECTION=15)

    def check_fuse1(fuse):
        if helper.target in ["fpga", "simv_fpga"]:
            if(fuse['fuse_name'] == 'opt_secure_pjtag_access_wr_secure'):
                jtag_plm_value = helper.debug_read(fuse['reg'])
                if(jtag_plm_value != 0xffffff8f):
                    helper.perror("JTAG fuse1 check fail, PLM register value is %d" %jtag_plm_value)
            else:
                if(fuse['field'] == 'WRITE_PROTECTION'):
                    fuse['reg'].debug_poll(WRITE_PROTECTION=fuse['fuse1'])
                elif(fuse['field'] == 'READ_PROTECTION'):
                    fuse['reg'].debug_poll(READ_PROTECTION=fuse['fuse1'])
                elif(fuse['field'] == 'SOURCE_ENABLE'):
                    fuse['reg'].debug_poll(SOURCE_ENABLE=fuse['fuse1'])
        else:
            if(fuse['fuse_name'] == 'opt_secure_pjtag_access_wr_secure'):
                jtag_plm_value = helper.read(fuse['reg'])
                if(jtag_plm_value != 0xffffff8f):
                    helper.perror("JTAG fuse1 check fail, PLM register value is %d" %jtag_plm_value)
            else:
                if(fuse['field'] == 'WRITE_PROTECTION'):
                    fuse['reg'].poll(WRITE_PROTECTION=fuse['fuse1'])
                elif(fuse['field'] == 'READ_PROTECTION'):
                    fuse['reg'].poll(READ_PROTECTION=fuse['fuse1'])
                elif(fuse['field'] == 'SOURCE_ENABLE'):
                    fuse['reg'].poll(SOURCE_ENABLE=fuse['fuse1'])

    def test_fuse_fpga(IP_PLM_LIST):
        FULL_PLM_LIST = []
        for i in FUSE_LIST:
            for j in i:
                FULL_PLM_LIST.append(j)
        for fuse in IP_PLM_LIST:
            helper.log("FUSE0 Test: checking the fuse %s, and the reg is %s" % (fuse['fuse_name'], fuse['reg']))
            #check default value is *_FUSE0
            check_fuse0(fuse)

        helper.log("FUSE1 Test: make all chip options to 1")
        for fuse in IP_PLM_LIST:
            helper.log("FUSE1 Test: override the fuse %s to 1" % (fuse['fuse_name']))
            if(fuse['fuse_name'] != '0'):
                test_api.fuse_opts_override(fuse['fuse_name'], 1, debug_mode=1)
                helper.log("Force %s done" %(fuse['fuse_name']))
                
        #trigger L3 reset to update reg reset value
        L3_reset()
        helper.log("FUSE1 Test: test fuse 1")
        for fuse in IP_PLM_LIST:
            if(fuse['fuse_name'] != '0'):
                helper.log("FUSE1 Test: checking the fuse %s, and the reg is %s" % (fuse['fuse_name'], fuse['reg']))
                check_fuse1(fuse)
                #if helper.target in ["fpga", "simv_fpga"]:
                #    helper.log("Duo the time limitation, just choose one different fuse to check")
                #    for other_fuse in FULL_PLM_LIST:
                #        if(other_fuse['fuse_name'] != fuse['fuse_name']):
                #            helper.log("checking the other fuse %s, and the reg is %s" % (other_fuse['fuse_name'], other_fuse['reg']))
                #            check_fuse0(other_fuse)
                #            helper.log("checking the other fuse %s Done" % (other_fuse['fuse_name']))
                #            break
                #if helper.target in ["fpga", "simv_fpga"]:
                #    test_api.fuse_opts_override(fuse['fuse_name'], 0, debug_mode=1)
                #else:
                #    helper.hdl_force(fuse_path+fuse['fuse_name'], 0)
                #L3_reset()
    
    def test_fuse(IP_PLM_LIST):
        FULL_PLM_LIST = []
        for i in FUSE_LIST:
            for j in i:
                FULL_PLM_LIST.append(j)
        for fuse in IP_PLM_LIST:
            helper.log("checking the fuse %s, and the reg is %s" % (fuse['fuse_name'], fuse['reg']))
            #check default value is *_FUSE0
            check_fuse0(fuse)
            if(fuse['fuse_name'] != '0'):
                if helper.target in ["fpga", "simv_fpga"]:
                    test_api.fuse_opts_override(fuse['fuse_name'], 1, debug_mode=1)
                else:
                    helper.hdl_force(fuse_path+fuse['fuse_name'], 1)
                helper.log("Force %s done" %(fuse['fuse_name']))
                #trigger L3 reset to update reg reset value
                L3_reset()
                check_fuse1(fuse)
                if helper.target in ["fpga", "simv_fpga"]:
                    helper.log("Duo the time limitation, just choose one different fuse to check")
                    for other_fuse in FULL_PLM_LIST:
                        if(other_fuse['fuse_name'] != fuse['fuse_name']):
                            helper.log("checking the other fuse %s, and the reg is %s" % (other_fuse['fuse_name'], other_fuse['reg']))
                            check_fuse0(other_fuse)
                            helper.log("checking the other fuse %s Done" % (other_fuse['fuse_name']))
                            break
                else:
                    for other_fuse in FULL_PLM_LIST:
                        if(other_fuse['fuse_name'] != fuse['fuse_name']):
                            check_fuse0(other_fuse)
                        else:
                            check_fuse1(other_fuse)
                if helper.target in ["fpga", "simv_fpga"]:
                    test_api.fuse_opts_override(fuse['fuse_name'], 0, debug_mode=1)
                else:
                    helper.hdl_force(fuse_path+fuse['fuse_name'], 0)
                L3_reset()
            #else:
            #    check_fuse0(fuse)
    
    def check_value_exp_error(reg, exp_value, priv_id):
        if helper.target in ["fpga", "simv_fpga"]:
            if priv_id==0:
                read_value = reg.debug_read()
            elif priv_id==2:
                read_value = reg.read()
            elif priv_id==3:
                read_value = test_api.oobhub_icd_read(reg.abs_addr)
            else:
                helper.perror("Cannot use sysctrl to read now")
            if(read_value.value == exp_value):
                helper.perror("Reg value match, exp: %x, act: %x, but it is not expected" %(exp_value, read_value.value))
            else:
                helper.log("Reg value mismatch, exp: %x, act: %x, but it is expected" %(exp_value, read_value.value))
    
    def check_err_code_with_read(read_addr, exp_err_code, priv_id):
        if (priv_id == 0):
            jtag_read_value = helper.j2h_read(read_addr)
            if (jtag_read_value != exp_err_code):
                helper.perror("jtag read check mismatch, exp: %x, act: %x" %(exp_err_code, jtag_read_value))
        elif(priv_id == 3):
            oobhub_read_value = test_api.oobhub_icd_read(read_addr)
            if (oobhub_read_value != exp_err_code):
                helper.perror("oobhub read check mismatch, exp: %x, act: %x" %(exp_err_code, oobhub_read_value))

    def write_with_err_code_checking(reg, write_value, current_priv_id, allowed_priv_id, current_priv_level, allowed_priv_level):
        if helper.target in ["fpga", "simv_fpga"]:
            if(reg == 0x4a6004):
                write_addr = 0x4a6004
            else:
                write_addr = reg.abs_addr
            
            if(current_priv_id == 0): #JTAG
                reg.debug_write(write_value)
            elif(current_priv_id == 2): #FSP
                reg.write(write_value,2,current_priv_level)
            elif(current_priv_id == 3): #OOBHUB
                test_api.oobhub_icd_write(write_addr, write_value)
            else:
                helper.perror("sysctrl cannot be controlled now, OOBHUB cannot access L1 target, so not support these")

            # no response check now, just can tried to readm and get if real write in the value
            if(current_priv_id == allowed_priv_id and current_priv_level >= allowed_priv_level):
                check_value(reg, write_value, allowed_priv_id, 3)
            elif(current_priv_id == allowed_priv_id and current_priv_level < allowed_priv_level):
                check_value_exp_error(reg, write_value, allowed_priv_id)
            elif(current_priv_id != allowed_priv_id):
                check_value_exp_error(reg, write_value, allowed_priv_id)
                if(current_priv_id == 0):
                    check_err_code_with_read(write_addr, 0xbadf57e8, current_priv_id)
                elif (current_priv_id == 3):
                    if (reg.name == 'EMP_FSP_CTRL_1_0'):
                        check_err_code_with_read(write_addr, 0xbadf57ef, current_priv_id)
                    else:
                        check_err_code_with_read(write_addr, 0xbadf5040, current_priv_id)
                #if(current_priv_id == 0 and write_rdata != 0xbadf57e8):
                #    helper.perror("write_rdata value mismatch, exp: %x, act: %x" %(0xbadf57e8, write_rdata))
                #elif(current_priv_id == 2 and write_rdata != 0xbadf57eb):
                #    helper.perror("write_rdata value mismatch, exp: %x, act: %x" %(0xbadf57eb, write_rdata))
                #elif(current_priv_id == 3):
                #    if(reg != 0x4a6004):
                #        if(reg.name == 'EMP_FSP_CTRL_1_0' and write_rdata != 0xbadf57ef):
                #            helper.perror("write_rdata value mismatch, exp: %x, act: %x" %(0xbadf57ef, write_rdata))
                #        if(reg.name != 'EMP_FSP_CTRL_1_0' and write_rdata != 0xbadf5040):
                #            helper.perror("write_rdata value mismatch, exp: %x, act: %x" %(0xbadf5040, write_rdata))
            else:
                helper.perror("priv_level should not come here")
            #elif(current_priv_level < allowed_priv_level):
            #    if(write_resp_err != 1):
            #        helper.perror("write_resp_err value mismatch, exp: %x, act: %x" %(1, write_resp_err))
            #    if(allowed_priv_level == 3):
            #        if((current_priv_level == 2 and write_rdata != 0xbadf5128) or (current_priv_level == 1 and write_rdata != 0xbadf5118) or (current_priv_level == 0 and write_rdata != 0xbadf5108)):
            #            helper.perror("write_rdata value mismatch, exp: 0xbadf51%d8, act: %x" %(current_priv_level, write_rdata))
            #    elif(allowed_priv_level == 2):
            #        if((current_priv_level == 1 and write_rdata != 0xbadf511c) or (current_priv_level == 0 and write_rdata != 0xbadf510c)):
            #            helper.perror("write_rdata value mismatch, exp: 0xbadf51%dc, act: %x" %(current_priv_level, write_rdata))
            #    elif(allowed_priv_level == 1):
            #        if(current_priv_level == 0 and write_rdata != 0xbadf510e):
            #            helper.perror("write_rdata value mismatch, exp: 0xbadf51%de, act: %x" %(current_priv_level, write_rdata))
        else:
            addr_list = []
            data_list = []
            cmd_list = []
            if(reg == 0x4a6004):
                addr_list.append(0x4a6004)
            else:
                addr_list.append(reg.abs_addr)
            data_list.append(write_value)
            cmd_list.append(3)
            write_return_list = helper.burst_operation(addr_list, data_list, cmd_list, current_priv_id, 1, current_priv_level)#addr_list, data_list, cmd_list, priv_id, wait_tick, priv_level
            write_rdata = write_return_list[0][0]
            write_resp_err = write_return_list[1][0]
            if(current_priv_id == allowed_priv_id and current_priv_level >= allowed_priv_level):
                if(write_resp_err == 1):
                    helper.perror("write_resp_err value mismatch, exp: %x, act: %x" %(0, write_resp_err))
            elif(current_priv_id != allowed_priv_id):
                if(write_resp_err != 1):
                    helper.perror("write_resp_err value mismatch, exp: %x, act: %x" %(1, write_resp_err))
                if(current_priv_id == 0 and write_rdata != 0xbadf57e8):
                    helper.perror("write_rdata value mismatch, exp: %x, act: %x" %(0xbadf57e8, write_rdata))
                elif(current_priv_id == 1 and write_rdata != 0xbadf57e6):
                    helper.perror("write_rdata value mismatch, exp: %x, act: %x" %(0xbadf57e6, write_rdata))
                elif(current_priv_id == 2 and write_rdata != 0xbadf57eb):
                    helper.perror("write_rdata value mismatch, exp: %x, act: %x" %(0xbadf57eb, write_rdata))
                elif(current_priv_id == 3):
                    if(reg != 0x4a6004):
                        if(reg.name == 'EMP_FSP_CTRL_1_0' and write_rdata != 0xbadf57ef):
                            helper.perror("write_rdata value mismatch, exp: %x, act: %x" %(0xbadf57ef, write_rdata))
                        if(reg.name != 'EMP_FSP_CTRL_1_0' and write_rdata != 0xbadf5040):
                            helper.perror("write_rdata value mismatch, exp: %x, act: %x" %(0xbadf5040, write_rdata))
            elif(current_priv_level < allowed_priv_level):
                if(write_resp_err != 1):
                    helper.perror("write_resp_err value mismatch, exp: %x, act: %x" %(1, write_resp_err))
                if(allowed_priv_level == 3):
                    if((current_priv_level == 2 and write_rdata != 0xbadf5128) or (current_priv_level == 1 and write_rdata != 0xbadf5118) or (current_priv_level == 0 and write_rdata != 0xbadf5108)):
                        helper.perror("write_rdata value mismatch, exp: 0xbadf51%d8, act: %x" %(current_priv_level, write_rdata))
                elif(allowed_priv_level == 2):
                    if((current_priv_level == 1 and write_rdata != 0xbadf511c) or (current_priv_level == 0 and write_rdata != 0xbadf510c)):
                        helper.perror("write_rdata value mismatch, exp: 0xbadf51%dc, act: %x" %(current_priv_level, write_rdata))
                elif(allowed_priv_level == 1):
                    if(current_priv_level == 0 and write_rdata != 0xbadf510e):
                        helper.perror("write_rdata value mismatch, exp: 0xbadf51%de, act: %x" %(current_priv_level, write_rdata))

    def test_source_id_fpga(plm, wr_value, priv_id):
        # just use only JTAG try now
        source_priv_id = [0]
        for i in source_priv_id:
            if(i == priv_id):
                exp_value = wr_value
            else:
                if(plm['ip_name'] == 'JTAG'):
                    exp_value = 0
                else:
                    exp_value = plm['protected_reg'].reset_val
            if(plm['ip_name'] == 'FSP'):
                helper.log("Write with priv_id %d" %i)
                if(i != 2):
                    if(i == 0):# j2h cannot collect error info
                        plm['protected_reg'].debug_write(wr_value)
                    else:
                        write_with_err_code_checking(plm['protected_reg'], wr_value, i, priv_id, 3, 3)
                    check_value(plm['protected_reg'], exp_value, priv_id, 3)
                    if(i == 0):
                        plm['protected_reg'].debug_write(plm['protected_reg'].reset_val)
                    else:
                        write_with_err_code_checking(plm['protected_reg'], plm['protected_reg'].reset_val, i, priv_id, 3, 3)
            else:
                # OOBHUB just can check FSP
                if (i != 3):
                    if(plm['ip_name'] == 'JTAG'):
                        helper.log("Write with priv_id %d" %i)
                        if(i == 0):
                            helper.j2h_write(plm['protected_reg'], wr_value)
                        else:
                            write_with_err_code_checking(plm['protected_reg'], wr_value, i, priv_id, 3, 3)
                        
                        if priv_id == 0: #JTAG
                            jtag_protected_reg = helper.read(plm['protected_reg'], priv_id, 3)
                        elif priv_id == 2: #FSP
                            jtag_protected_reg = helper.read(plm['protected_reg'])
                        elif priv_id == 3: #OOBHUB
                            helper.perror("will use icd later")
                        else:
                            helper.perror("Not support priv_id = %d condition" % (priv_id))

                        if(jtag_protected_reg != exp_value):
                            helper.perror("JTAG PLM protected reg read value mismatch, exp: %d, act: %d" %(exp_value, jtag_protected_reg))
                        if(i == 0):
                            helper.debug_write(plm['protected_reg'], 0)
                        else:
                            write_with_err_code_checking(plm['protected_reg'], 0, i, priv_id, 3, 3)
                    else:
                        helper.log("Write with priv_id %d" %i)
                        if(i == 0):
                            plm['protected_reg'].debug_write(wr_value)
                        else:
                            write_with_err_code_checking(plm['protected_reg'], wr_value, i, priv_id, 3, 3)
                        check_value(plm['protected_reg'], exp_value, priv_id, 3)
                        if(i == 0):
                            plm['protected_reg'].debug_write(plm['protected_reg'].reset_val)
                        else:
                            write_with_err_code_checking(plm['protected_reg'], plm['protected_reg'].reset_val, i, priv_id, 3, 3)
    
    def test_source_id(plm, wr_value, priv_id):
        for i in range(4):
            if(i == priv_id):
                exp_value = wr_value
            else:
                if(plm['ip_name'] == 'JTAG'):
                    exp_value = 0
                else:
                    exp_value = plm['protected_reg'].reset_val
            if(plm['ip_name'] == 'FSP'):
                helper.log("Write with priv_id %d" %i)
                if(i != 2):
                    if(i == 0):# j2h cannot collect error info
                        plm['protected_reg'].write(wr_value, i, 1, 3)
                    else:
                        write_with_err_code_checking(plm['protected_reg'], wr_value, i, priv_id, 3, 3)
                    check_value(plm['protected_reg'], exp_value, priv_id, 3)
                    if(i == 0):
                        plm['protected_reg'].write(plm['protected_reg'].reset_val, i, 1, 3)
                    else:
                        write_with_err_code_checking(plm['protected_reg'], plm['protected_reg'].reset_val, i, priv_id, 3, 3)
            else:
                if(plm['ip_name'] == 'JTAG'):
                    helper.log("Write with priv_id %d" %i)
                    if(i == 0):
                        helper.write(plm['protected_reg'], wr_value, i, 3)
                    else:
                        write_with_err_code_checking(plm['protected_reg'], wr_value, i, priv_id, 3, 3)
                    jtag_protected_reg = helper.read(plm['protected_reg'], priv_id, 3)
                    if(jtag_protected_reg != exp_value):
                        helper.perror("JTAG PLM protected reg read value mismatch, exp: %d, act: %d" %(exp_value, jtag_protected_reg))
                    if(i == 0):
                        helper.write(plm['protected_reg'], 0, i, 3)
                    else:
                        write_with_err_code_checking(plm['protected_reg'], 0, i, priv_id, 3, 3)
                else:
                    helper.log("Write with priv_id %d" %i)
                    if(i == 0):
                        plm['protected_reg'].write(wr_value, i, 1, 3)
                    else:
                        write_with_err_code_checking(plm['protected_reg'], wr_value, i, priv_id, 3, 3)
                    check_value(plm['protected_reg'], exp_value, priv_id, 3)
                    if(i == 0):
                        plm['protected_reg'].write(plm['protected_reg'].reset_val, i, 1, 3)
                    else:
                        write_with_err_code_checking(plm['protected_reg'], plm['protected_reg'].reset_val, i, priv_id, 3, 3)
   
    
    def test_priv_level(plm, wr_value, priv_level):
        allowed_priv_levels = [0,3]
        for i in allowed_priv_levels:
        #for i in range(4):
            if(i >= priv_level):
                exp_value = wr_value
            else:
                if(plm['ip_name'] == 'JTAG'):
                    exp_value = 0
                else:
                    exp_value = plm['protected_reg'].reset_val
            helper.log("Start to test with priv level %d with write value %x, and exp_value is %x, and the reg reset value is %x" % (i, wr_value, exp_value, plm['protected_reg'].reset_val))
            if(plm['ip_name'] == 'JTAG'):
                #helper.write(plm['protected_reg'], wr_value, 1, i)
                write_with_err_code_checking(plm['protected_reg'], wr_value, 1, 1, i, priv_level)
                jtag_protected_reg = helper.read(plm['protected_reg'], 1, 3)
                if(jtag_protected_reg != exp_value):
                    helper.perror("JTAG PLM protected reg read value mismatch, exp: %d, act: %d" %(exp_value, jtag_protected_reg))
                #helper.write(plm['protected_reg'], plm['protected_reg'].reset_val, 1, priv_level)
                write_with_err_code_checking(plm['protected_reg'], 0, 1, 1, i, priv_level)
            else:
                if helper.target in ["fpga", "simv_fpga"]:
                    #plm['protected_reg'].write(wr_value, 1, 1, i)
                    helper.log("write with error code checking")
                    write_with_err_code_checking(plm['protected_reg'], wr_value, 2, 2, i, priv_level)
                    helper.log("checking if the register has the exp value")
                    check_value(plm['protected_reg'], exp_value, 2, priv_level)
                    if(i >= priv_level):
                        helper.log("writing the valur to reset val %x when i >= priv level" % (plm['protected_reg'].reset_val))
                        plm['protected_reg'].write(plm['protected_reg'].reset_val, 2, 3)
                        check_value(plm['protected_reg'], plm['protected_reg'].reset_val, 2, 3)
                    #plm['protected_reg'].write(plm['protected_reg'].reset_val, 1, 1, priv_level)
                    #write_with_err_code_checking(plm['protected_reg'], plm['protected_reg'].reset_val, 2, 2, i, priv_level)
                else:
                    #plm['protected_reg'].write(wr_value, 1, 1, i)
                    write_with_err_code_checking(plm['protected_reg'], wr_value, 1, 1, i, priv_level)
                    check_value(plm['protected_reg'], exp_value, 1, priv_level)
                    #plm['protected_reg'].write(plm['protected_reg'].reset_val, 1, 1, priv_level)
                    write_with_err_code_checking(plm['protected_reg'], plm['protected_reg'].reset_val, 1, 1, i, priv_level)

    def program_jtag_plm(write_value, priv_id, priv_level):
        if helper.target in ["fpga", "simv_fpga"]:
            if priv_id == 0:
                helper.j2h_write(0x4a6040, write_value)
                jtag_plm_value = helper.j2h_read(0x4a6040)
                if(jtag_plm_value != write_value):
                    helper.perror("JTAG PLM register read value not expected, exp: %d, act: %d" %(write_value, jtag_plm_value))
            elif priv_id == 2:
                helper.write(0x4a6040, write_value)
                jtag_plm_value = helper.read(0x4a6040)
                if(jtag_plm_value != write_value):
                    helper.perror("JTAG PLM register read value not expected, exp: %d, act: %d" %(write_value, jtag_plm_value))
        else:
            helper.write(0x4a6040, write_value, priv_id, priv_level)
            jtag_plm_value = helper.read(0x4a6040, priv_id, priv_level)
            if(jtag_plm_value != write_value):
                helper.perror("JTAG PLM register read value not expected, exp: %d, act: %d" %(write_value, jtag_plm_value))

    ##force these two fuse to fabric to 1 to enable all source_id and priv level
    options = parse_args()
    if helper.target in ["fpga", "simv_fpga"]:
        if((options.Testpoint == 'fuse_connection') or (options.Testpoint == 'SrcID')):
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
        
        helper.log("Force fabric fuse start")
        if((options.Testpoint == 'fuse_connection') or (options.Testpoint == 'SrcID')):
            test_api.fuse_opts_override("opt_secure_pri_source_isolation_en", 1, debug_mode=1)
        else:
            test_api.fuse_opts_override("opt_secure_pri_source_isolation_en", 1)
        # SrcID_PL check for making jtag to PL3, so not force "opt_priv_sec_en" to 1
        if(options.Testpoint == 'PL'):
            test_api.fuse_opts_override("opt_priv_sec_en", 1)
        #helper.hdl_force("ntb_top.u_nv_top.u_sra_sys0.u_l0_cluster.u_NV_fsp.u_peregrine.falcon.u_riscv.u_RISCV_dcls_core.u_main.UJ_dev_mode",1) # bug 4097271
        #helper.hdl_force("ntb_top.u_nv_top.u_sra_sys0.test_master.host_to_1500.opt_secure_host2jtag_standard_mode",1) # bug 4102635
        helper.log("Force fabric fuse done")

        #if (options.Testpoint == 'SrcID'):
        #    test_api.oobhub_icd_init()

        #Test Fuse
        if(options.Testpoint == 'fuse_connection'):
            FULL_PLM_LIST_for_conn = []
            for i in FUSE_LIST:
                FULL_PLM_LIST_for_conn.append(i[0])
            test_fuse(FULL_PLM_LIST_for_conn) # should change to full list when fsp pass

        if(options.Testpoint == 'SrcID'):
            #Test source_id
            helper.log("Starting source_id test")
            for plm in SINGLE_PLM_FOR_SRCID:
                helper.log("Testing source_id of %s" %(plm['ip_name']))
                if(plm['ip_name'] == 'JTAG'):
                    write_value = 0xaaaaaaaa
                else:
                    write_value = 0xffffffff & plm['protected_reg'].write_mask
                
                #Use JTAG with pl3 to config PLM regs, 
#                #source_id == SYSCTRL
#                helper.log("Start write PLM reg of %s" % plm['ip_name'])
#                if(plm['ip_name'] == 'JTAG'):
#                    program_jtag_plm(0x40fff, 1, 3)
#                else:
#                    plm['reg'].debug_write(0x40fff)
#                    #plm['reg'].write(0x40fff, 1, 1, 3) #0x6880: SOURCE_ENABLE[31:12] == 6(SYSCTRL), SOURCE_WRITE_CONTROL[11] == 1(BLOCKED), WRITE_VIOLATION[9] == 1(report error), WRITE_PROTECTION[7:4] == f(ALL_LEVEL_ENABLED), READ_PROTECTION[3:0] == f(all priv_level enabled), other fields are all 0, priv_id==1, wait_tick==1, priv_level==3
#                    check_value(plm['reg'], 0x40fff, 0, 3)
#                helper.log("Sysctrl allowed")
#                test_source_id_fpga(plm, write_value, 1)

                #source_id == JTAG
                if(plm['ip_name'] == 'JTAG'):
                    program_jtag_plm(0x100fff, 0, 3)
                else:
                    plm['reg'].debug_write(0x100fff)  #0x8880: SOURCE_ENABLE[31:12] == 8(JTAG)
                    check_value(plm['reg'], 0x100fff, 0, 3)
                helper.log("JTAG allowed")
                test_source_id_fpga(plm, write_value, 0)
                if(plm['ip_name'] != 'FSP'):
                    #source_id == FSP
                    if(plm['ip_name'] == 'JTAG'):
                        program_jtag_plm(0x800fff, 0, 3)
                    else:
                        plm['reg'].debug_write(0x800fff)  #0xb880: SOURCE_ENABLE[31:12] == b(FSP)
                        check_value(plm['reg'], 0x800fff, 0, 3)
                    helper.log("FSP allowed")
                    test_source_id_fpga(plm, write_value, 2)
                else: # will not check FSP 
                    #source_id == OOBHUB
                    plm['reg'].debug_write(0x8000fff) #0xf880: SOURCE_ENABLE[31:12] == f(OOBHUB)
                    check_value(plm['reg'], 0x8000fff, 0, 3)
                    helper.log("OOBHUB allowed")
                    test_source_id_fpga(plm, write_value, 3)
            
        if(options.Testpoint == 'PL'):
            helper.log("Starting priv_level test")
            for plm in SINGLE_PLM_FOR_PL:
                helper.log("Testing priv_level of %s" %(plm['ip_name']))
                if(plm['ip_name'] == 'JTAG'):
                    write_value = 0xffffffff
                else:
                    write_value = 0xffffffff & plm['protected_reg'].write_mask
                #PL3
                if(plm['ip_name'] == 'JTAG'):
                    program_jtag_plm(0xffffff8f, 2, 3) # acutally will not check JTAG now
                else:
                    if(plm['ip_name'] == 'THERM' or plm['ip_name'] == 'FUSE'):
                        plm['reg'].write(0xffffff8f, 2, 3) #therm and fuse plm regs are in L1 reset domain, have to program with priv_id 2
                    else:
                        plm['reg'].write(0xffffff8f, 2, 3)
                    check_value(plm['reg'], 0xffffff8f, 2, 3)
                helper.log("Priv level > 3 allowed")
                test_priv_level(plm, write_value, 3)
                #PL2
                if(plm['ip_name'] == 'JTAG'):
                    program_jtag_plm(0xffffffcf, 2, 3)
                else:
                    plm['reg'].write(0xffffffcf, 2, 3)
                    check_value(plm['reg'], 0xffffffcf, 2, 3)
                helper.log("Priv level > 2 allowed")
                test_priv_level(plm, write_value, 2)
                #PL1
                if(plm['ip_name'] == 'JTAG'):
                    program_jtag_plm(0xffffffef, 2, 3)
                else:
                    plm['reg'].write(0xffffffef, 2, 3)
                    check_value(plm['reg'], 0xffffffef, 2, 3)
                helper.log("Priv level > 1 allowed")
                test_priv_level(plm, write_value, 1)
                #PL0
                if(plm['ip_name'] == 'JTAG'):
                    program_jtag_plm(0xffffffff, 2, 3)
                else:
                    plm['reg'].write(0xffffffff, 2, 3)
                    check_value(plm['reg'], 0xffffffff, 2, 3)
                helper.log("Priv level > 0 allowed")
                test_priv_level(plm, write_value, 0)
                
        helper.wait_sim_time("ns", 300)
        helper.log("Test Finish")
    else:
        helper.log("Force fabric fuse start")
        helper.hdl_force(fuse_path+'opt_priv_sec_en', 1)
        helper.hdl_force(fuse_path+'opt_secure_pri_source_isolation_en', 1)
        helper.hdl_force("ntb_top.u_nv_top.u_sra_sys0.u_l0_cluster.u_NV_fsp.u_peregrine.falcon.u_riscv.u_RISCV_dcls_core.u_main.UJ_dev_mode",1) # bug 4097271
        helper.hdl_force("ntb_top.u_nv_top.u_sra_sys0.test_master.host_to_1500.opt_secure_host2jtag_standard_mode",1) # bug 4102635
        helper.log("Force fabric fuse done")

        #Test Fuse
        if(options.Testpoint == 'fuse_connection'):
            if(options.IP == 'FSP'):
                helper.log("Testing fuse of FSP")
                test_fuse(FSP_PLM_LIST)
            elif(options.IP == 'FUSE'):
                helper.log("Testing fuse of FUSE")
                test_fuse(FUSE_PLM_LIST)
            elif(options.IP == 'SYSCTRL'):
                helper.log("Testing fuse of SYSCTRL")
                test_fuse(SYSCTRL_PLM_LIST)
            elif(options.IP == 'BT_QSPI'):
                helper.log("Testing fuse of BT_QSPI")
                test_fuse(BT_QSPI_PLM_LIST)
            elif(options.IP == 'QSPI0'):
                helper.log("Testing fuse of QSPI0")
                test_fuse(QSPI0_PLM_LIST)
            elif(options.IP == 'QSPI1'):
                helper.log("Testing fuse of QSPI1")
                test_fuse(QSPI1_PLM_LIST)
            elif(options.IP == 'OOBHUB'):
                helper.log("Testing fuse of OOBHUB")
                test_fuse(OOBHUB_PLM_LIST)
            elif(options.IP == 'JTAG'):
                helper.log("Testing fuse of JTAG")
                test_fuse(JTAG_PLM_LIST)
            elif(options.IP == 'THERM'):
                helper.log("Testing fuse of THERM")
                test_fuse(THERM_PLM_LIST)

        if(options.Testpoint == 'SrcID_PL'):
            #Test source_id
            helper.log("Starting source_id test")
            for plm in SINGLE_PLM:
                helper.log("Testing source_id of %s" %(plm['ip_name']))
                if(plm['ip_name'] == 'JTAG'):
                    write_value = 0xaaaaaaaa
                else:
                    write_value = 0xffffffff & plm['protected_reg'].write_mask
                #Use SYSCTRL with pl3 to config PLM regs, source_id == SYSCTRL
                helper.log("Start write PLM reg of %s" % plm['ip_name'])
                if(plm['ip_name'] == 'JTAG'):
                    program_jtag_plm(0x40fff, 1, 3)
                else:
                    plm['reg'].write(0x40fff, 1, 1, 3) #0x6880: SOURCE_ENABLE[31:12] == 6(SYSCTRL), SOURCE_WRITE_CONTROL[11] == 1(BLOCKED), WRITE_VIOLATION[9] == 1(report error), WRITE_PROTECTION[7:4] == f(ALL_LEVEL_ENABLED), READ_PROTECTION[3:0] == f(all priv_level enabled), other fields are all 0, priv_id==1, wait_tick==1, priv_level==3
                    check_value(plm['reg'], 0x40fff, 1, 3)
                helper.log("Sysctrl allowed")
                test_source_id(plm, write_value, 1)
                #source_id == JTAG
                if(plm['ip_name'] == 'JTAG'):
                    program_jtag_plm(0x100fff, 1, 3)
                else:
                    plm['reg'].write(0x100fff, 1, 1, 3)  #0x8880: SOURCE_ENABLE[31:12] == 8(JTAG)
                    check_value(plm['reg'], 0x100fff, 1, 3)
                helper.log("JTAG allowed")
                test_source_id(plm, write_value, 0)
                if(plm['ip_name'] != 'FSP'):
                    #source_id == FSP
                    if(plm['ip_name'] == 'JTAG'):
                        program_jtag_plm(0x800fff, 0, 3)
                    else:
                        plm['reg'].write(0x800fff, 0, 1, 3)  #0xb880: SOURCE_ENABLE[31:12] == b(FSP)
                        check_value(plm['reg'], 0x800fff, 0, 3)
                    helper.log("FSP allowed")
                    test_source_id(plm, write_value, 2)
                else:
                    #source_id == OOBHUB
                    plm['reg'].write(0x8000fff, 0, 1, 3) #0xf880: SOURCE_ENABLE[31:12] == f(OOBHUB)
                    check_value(plm['reg'], 0x8000fff, 0, 3)
                    helper.log("OOBHUB allowed")
                    test_source_id(plm, write_value, 3)
            
            #Test priv level
            L3_reset() # to reset the configuration of PLM registers in source_id test
            helper.log("Force fabric start")
            helper.hdl_force(fuse_path+'opt_priv_sec_en', 1)
            helper.hdl_force(fuse_path+'opt_secure_pri_source_isolation_en', 1)
            helper.log("Force fabric done")
            
            helper.log("Starting priv_level test")
            for plm in SINGLE_PLM:
                helper.log("Testing priv_level of %s" %(plm['ip_name']))
                if(plm['ip_name'] == 'JTAG'):
                    write_value = 0xffffffff
                else:
                    write_value = 0xffffffff & plm['protected_reg'].write_mask
                #PL3
                if(plm['ip_name'] == 'JTAG'):
                    program_jtag_plm(0xffffff8f, 1, 3)
                else:
                    if(plm['ip_name'] == 'THERM' or plm['ip_name'] == 'FUSE'):
                        plm['reg'].write(0xffffff8f, 2, 1, 3) #therm and fuse plm regs are in L1 reset domain, have to program with priv_id 2
                    else:
                        plm['reg'].write(0xffffff8f, 1, 1, 3)
                    check_value(plm['reg'], 0xffffff8f, 1, 3)
                helper.log("Priv level > 3 allowed")
                test_priv_level(plm, write_value, 3)
                #PL2
                if(plm['ip_name'] == 'JTAG'):
                    program_jtag_plm(0xffffffcf, 1, 3)
                else:
                    plm['reg'].write(0xffffffcf, 1, 1, 3)
                    check_value(plm['reg'], 0xffffffcf, 1, 3)
                helper.log("Priv level > 2 allowed")
                test_priv_level(plm, write_value, 2)
                #PL1
                if(plm['ip_name'] == 'JTAG'):
                    program_jtag_plm(0xffffffef, 1, 3)
                else:
                    plm['reg'].write(0xffffffef, 1, 1, 3)
                    check_value(plm['reg'], 0xffffffef, 1, 3)
                helper.log("Priv level > 1 allowed")
                test_priv_level(plm, write_value, 1)
                #PL0
                if(plm['ip_name'] == 'JTAG'):
                    program_jtag_plm(0xffffffff, 1, 3)
                else:
                    plm['reg'].write(0xffffffff, 1, 1, 3)
                    check_value(plm['reg'], 0xffffffff, 1, 3)
                helper.log("Priv level > 0 allowed")
                test_priv_level(plm, write_value, 0)
                
        helper.wait_sim_time("ns", 300)
        helper.log("Test Finish")
