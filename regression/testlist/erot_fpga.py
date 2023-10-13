
from nextp import *
root = Plan(claimed_feature="erot_fpga")
root.run_script = 'nvrun run_test'


PLATFORM_HEAD           = [ '--platform=HEAD',''' -rtlarg '+disable_falcon_mem_wakeup_scrubbing' ''']
PLATFORM_SIM_HEAD       = [ '--platform=SIM_HEAD',''' -rtlarg '+disable_falcon_mem_wakeup_scrubbing' '''] 
PLATFORM_SIM_HEADLESS   = [ '--platform=SIM_HEADLESS' ] 
PLATFORM_JTAG           = [ '--platform=JTAG' ] 

common_args = ['-u erot_fpga','''-rtlarg '-xlrm hier_inst_seed' ''','''-rtlarg '+UVM_TIMEOUT=500000000' ''','''-pyarg ' --target simv_fpga' ''']+PLATFORM_JTAG
br_rel      = '/home/ip/nvmsoc/uproc/peregrine_fsp_brom/1.0/69611591_tapeout_candidate/presil_hex'
RCV_BOOT    = [''' -pyarg ' --rcv_boot --replace_brom %s ' ''' % br_rel]

with feature('erot_fpga/lighton'):

    test_args   =   ['''-py erot_recovery_baisc_boot_test.py '''] + RCV_BOOT
    test_tags   =   ['boot','l0']
    AddTest(
        name    =   'erot_recovery_baisc_boot_test',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''light on each IP in chip'''
            )

    test_args   =   ['-py erot_light_on_test.py '] + RCV_BOOT
    test_tags   =   ['fabric','l0']
    AddTest(
        name    =   'erot_reg_light_on_test',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''light on each IP in chip'''
            )

    test_args   =   ['''-py erot_reset_l3_rst_light_on.py ''']
    test_tags   =   ['reset','as2']
    AddTest(
        name    =   'erot_reset_l3_light_on',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''light on each IP in chip'''
            )

    test_args   =   ['-py erot_rts_basic_test.py '] + RCV_BOOT
    test_tags   =   ['boot','l0']
    AddTest(
        name    =   'erot_rts_basic_test',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''RTS basic measurement logging test'''
            )

    test_args   =   ['''-py erot_j2h_debug_test.py ''']
    test_tags   =   ['j2h','l0','as2']
    AddTest(
        name    =   'erot_j2h_debug_test',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''light on each IP in chip'''
            )


    test_args   =   ['''-py erot_jtag_idcode_test.py ''']
    test_tags   =   ['j2h','l0','as2']
    AddTest(
        name    =   'erot_jtag_idcode_test',
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

    #test_args   =   ['''-py erot_oobhub_i2c_test.py -pyarg '--mst I2C_IB1 ' '''] + PLATFORM_HEAD
    #test_tags   =   ['lighton']
    #AddTest(
    #    name    =   'erot_oobhub_i2c_test' ,
    #    config  =   ['erot_fpga'],
    #    args    =   common_args+test_args,
    #    tags    =   test_tags,
    #    desc    =   '''light on each IP in chip'''
    #        )

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
