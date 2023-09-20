
from nextp import *
root = Plan(claimed_feature="erot_fpga")
root.run_script = 'nvrun run_test'

common_args = ['-u erot_fpga','''-rtlarg '-xlrm hier_inst_seed' ''','''-rtlarg '+UVM_TIMEOUT=500000000' ''','''-pyarg 'NOT_DEFAULT_GO_MAIN --target simv_fpga' ''']

light_on_reg_list      = ['I2C_IB0','I2C_IB1','IO_EXPANDER','SPI_IB0','SPI_IB1','OOBHUB_SPI','QSPI0','QSPI1','BOOT_QSPI',
                          'I3C_IB0' ,'I3C_IB1','GPIO','MRAM','CLOCK' ,'RESET','THERM','UART',
                          'OOBHUB','RTS','FUSE','NV_PBUS']

failure_case      = ['OOBHUB','QSPI0','QSPI1','BOOT_QSPI']

as2_list          = [x for x in light_on_reg_list if x not in failure_case] 

PLATFORM_HEAD      = [ '--platform=HEAD',''' -rtlarg '+disable_falcon_mem_wakeup_scrubbing' ''']
PLATFORM_SIM_HEAD  = [ '--platform=SIM_HEAD',''' -rtlarg '+disable_falcon_mem_wakeup_scrubbing' '''] 
PLATFORM_SIM_HEADLESS = [ '--platform=SIM_HEADLESS' ] 

with feature('erot_fpga/lighton'):
    test_args   =   ['''-py erot_light_on_test.py ''']+PLATFORM_HEAD
    test_tags   =   ['lighton']
    AddTest(
        name    =   'erot_reg_light_on_test',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''light on each IP in chip'''
            )
    
    #AS2IP_REGEX = '|'.join(as2_list)
    #test_args   =   ['''-py erot_light_on_test.py -pyarg '--unit "(%s)" ' ''' % AS2IP_REGEX] + PLATFORM_SIM_HEADLESS
    #test_tags   =   ['lighton','as2']
    #AddTest(
    #    name    =   'erot_reg_access',
    #    config  =   ['erot_fpga'],
    #    args    =   common_args+test_args,
    #    tags    =   test_tags,
    #    desc    =   '''light on each IP in chip for AS2'''
    #        )

    #test_args   =   ['-py erot_uart_loopback_test.py ' ] + PLATFORM_SIM_HEADLESS
    #test_tags   =   ['lighton','as2']
    #AddTest(
    #    name    =   'erot_uart_loopback_test' ,
    #    config  =   ['erot_fpga'],
    #    args    =   common_args+test_args,
    #    tags    =   test_tags,
    #    desc    =   '''light on each IP in chip'''
    #        )

    test_args   =   ['''-py erot_oobhub_i2c_test.py -pyarg '--mst I2C_IB1 ' '''] + PLATFORM_HEAD
    test_tags   =   ['lighton']
    AddTest(
        name    =   'erot_oobhub_i2c_test' ,
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''light on each IP in chip'''
            )

    #test_args   =   ['''-py erot_oobhub_i3c_test.py -pyarg '--i3c 1 ' '''] + PLATFORM_HEAD
    #test_tags   =   ['lighton']
    #AddTest(
    #    name    =   'erot_oobhub_i3c_test' ,
    #    config  =   ['erot_fpga'],
    #    args    =   common_args+test_args,
    #    tags    =   test_tags,
    #    desc    =   '''light on each IP in chip'''
    #        )


    #test_args   =   ['''-py erot_debug_mram_mtpr_test_sim_head.py '''] + PLATFORM_HEAD
    #test_tags   =   ['lighton']
    #AddTest(
    #    name    =   'erot_debug_mram_mtpr_test_head' ,
    #    config  =   ['erot_fpga'],
    #    args    =   common_args+test_args,
    #    tags    =   test_tags,
    #    desc    =   '''light on each IP in chip'''
    #        )

    #test_args   =   ['''-py bm_fpga_vip_test.py ''',''' -rtlarg '+ENABLE_SPI_VIP' '''] + PLATFORM_HEAD
    #test_tags   =   ['lighton']
    #AddTest(
    #    name    =   'bm_fpga_vip_test' ,
    #    config  =   ['erot_fpga'],
    #    args    =   common_args+test_args,
    #    tags    =   test_tags,
    #    desc    =   '''light on each IP in chip'''
    #        )

    #br_rel      =   '/home/ip/nvmsoc/uproc/peregrine_fsp_brom/1.0/69611591_tapeout_candidate/presil_hex'
    #test_args   =   ['''-py erot_recovery_mfg_boot_test.py --platform JTAG -pyarg ' --replace_brom %s --disable_peripheral_init_agent ' ''' % (br_rel )]
    #test_tags   =   ['br']
    #AddTest(
    #    name    =   'erot_recovery_mfg_boot_test',
    #    config  =   ['erot_fpga'],
    #    args    =   common_args+test_args,
    #    tags    =   test_tags,
    #    desc    =   '''Recovery non-mfg boot test'''
    #        )

    #test_args   =   ['''-py erot_nominal_boot_test.py -pyarg '--replace_brom %s --disable_peripheral_init_agent ' --platform JTAG ''' % (br_rel)]
    #test_tags   =   ['br']
    #AddTest(
    #    name    =   'erot_br_nominal_boot_mram_test',
    #    config  =   ['erot_fpga'],
    #    args    =   common_args+test_args,
    #    tags    =   test_tags,
    #    desc    =   '''nominal boot, basic mode booting from MRAM'''
    #        )

    #test_args   =   ['''-py erot_debug_fsp_test.py '''] + PLATFORM_SIM_HEADLESS
    #test_tags   =   ['lighton','as2']
    #AddTest(
    #    name    =   'erot_fsp_boot_test',
    #    config  =   ['erot_fpga'],
    #    args    =   common_args+test_args,
    #    tags    =   test_tags,
    #    desc    =   '''light on each IP in chip'''
    #        )

    #test_args   =   ["""-py erot_debug_fsp_cfg_i2c.py -rtlarg '+disable_falcon_mem_wakeup_scrubbing' --platform HEAD """]
    #test_tags   =   ['lighton','as2']
    #AddTest(
    #    name    =   'erot_debug_fsp_cfg_i2c',
    #    config  =   ['erot_fpga'],
    #    args    =   common_args+test_args,
    #    tags    =   test_tags,
    #    desc    =   '''light on each IP in chip'''
    #        )
