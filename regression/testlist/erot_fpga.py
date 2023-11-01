
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
    # fabric bring-up tests
    test_args   =   ['-py erot_light_on_test.py '] + RCV_BOOT
    test_tags   =   ['fabric','l0']
    AddTest(
        name    =   'erot_reg_light_on_test',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''light on each IP in chip'''
            )
    
    test_args   =   ['-py erot_fab_AddrHighBits_cov_test.py ']
    test_tags   =   ['fabric','l1']
    AddTest(
        name    =   'erot_fab_AddrHighBits_cov_test',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''fabric address hole check'''
            )
    
    test_args   =   ['''-py erot_fab_blf_lck_test.py  -pyarg ' --IP L1_FUSE' ''']
    test_tags   =   ['fabric','l1']
    AddTest(
        name    =   'erot_fab_blf_lck_test_l1_fuse',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''fabric blf lck test for fuse'''
            )

    test_args   =   ['''-py erot_fab_blf_lck_test.py  -pyarg ' --IP L1_PART1' ''']
    test_tags   =   ['fabric','l1']
    AddTest(
        name    =   'erot_fab_blf_lck_test_l1_part1',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''fabric blf lck test for l1 part1'''
            )

    test_args   =   ['''-py erot_fab_blf_lck_test.py  -pyarg ' --IP L1_PART2' ''']
    test_tags   =   ['fabric','l1']
    AddTest(
        name    =   'erot_fab_blf_lck_test_l1_part2',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''fabric blf lck test for l1 part2'''
            )

    test_args   =   ['''-py erot_fab_blf_lck_test.py  -pyarg ' --IP L2_PART1' ''']
    test_tags   =   ['fabric','l1']
    AddTest(
        name    =   'erot_fab_blf_lck_test_l2_part1',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''fabric blf lck test for l2 part1'''
            )

    test_args   =   ['''-py erot_fab_blf_lck_test.py  -pyarg ' --IP L2_PART2' ''']
    test_tags   =   ['fabric','l1']
    AddTest(
        name    =   'erot_fab_blf_lck_test_l2_part2',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''fabric blf lck test for L2 part2'''
            )
    
    test_args   =   ['''-py erot_fab_blf_lck_err_code_test.py  -pyarg ' --Fabric L1' ''']
    test_tags   =   ['fabric','l1']
    AddTest(
        name    =   'erot_fab_blf_lck_err_code_test_l1',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''fabric blf lck error check l1 part'''
            )
    
    test_args   =   ['''-py erot_fab_blf_lck_err_code_test.py  -pyarg ' --Fabric L2' ''']
    test_tags   =   ['fabric','l1']
    AddTest(
        name    =   'erot_fab_blf_lck_err_code_test_l2',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''fabric blf lck error check l2 part'''
            )
    # fabric bring-up tests END
    
    # mram bring-up tests
    test_args   =   ['-py erot_mram_tmc_test.py '] + RCV_BOOT
    test_tags   =   ['mram','l1']
    AddTest(
        name    =   'erot_mram_tmc_test',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''MRAM tmc feature check'''
            )
    
    test_args   =   ['-py erot_mram_region_protect_normal_test.py '] + RCV_BOOT
    test_tags   =   ['mram','l1']
    AddTest(
        name    =   'erot_mram_region_protect_normal_test',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''MRAM region WPEN/WP check'''
            )
    test_args   =   ['''-py erot_debug_mram_mtpr_test_sim_head.py '''] + RCV_BOOT
    test_tags   =   ['mram','l0']
    AddTest(
        name    =   'erot_debug_mram_mtpr_test_head' ,
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''mram mtpr test'''
            )
    # mram bring-up tests END
    
    # fuse api test
    test_args   =   ['-py erot_fuse_override_api_test.py ']
    test_tags   =   ['fuse_test']
    AddTest(
        name    =   'erot_fuse_override_api_test',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''test fuse api function'''
            )
    # fuse api bring-up tests END

    # reset bring-up tests
    test_args   =   ['''-py erot_reset_hw_boot_test_fpga.py ''']
    test_tags   =   ['reset','as2','l0']
    AddTest(
        name    =   'erot_reset_hw_boot_test_fpga',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''EROT HW boot'''
            )

    test_args   =   ['''-py erot_reset_l1_rst_domain_test_fpga.py ''']
    test_tags   =   ['reset','l1']
    AddTest(
        name    =   'erot_reset_l1_rst_domain_test_fpga',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''EROT L1 reset'''
            )

    test_args   =   ['''-py erot_reset_l3_rst_domain_test_fpga.py ''']
    test_tags   =   ['reset','l1']
    AddTest(
        name    =   'erot_reset_l3_rst_domain_test_fpga',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''EROT L3 reset'''
            )

    test_args   =   ['''-py erot_reset_sw_rst_test_fpga.py '''] + RCV_BOOT
    test_tags   =   ['reset','l2']
    AddTest(
        name    =   'erot_reset_sw_rst_test_fpga',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''EROT SW reset'''
            )

#    test_args   =   ['''-py erot_reset_l3_rst_light_on.py ''']
#    test_tags   =   ['reset','as2']
#    AddTest(
#        name    =   'erot_reset_l3_light_on',
#        config  =   ['erot_fpga'],
#        args    =   common_args+test_args,
#        tags    =   test_tags,
#        desc    =   '''light on each IP in chip'''
#            )
    # reset bring-up tests END

    # bypass monitor bring-up tests
    test_args   =   ['''-py erot_bypmon_legal_cmd_test_fpga.py '''] + RCV_BOOT
    test_tags   =   ['bypmon','l0']
    AddTest(
        name    =   'erot_bypmon_legal_cmd_test_fpga',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''EROT bypass monitor legal command bypass'''
            )

    test_args   =   ['''-py erot_bypmon_illegal_rd_test_fpga.py '''] + RCV_BOOT
    test_tags   =   ['bypmon','l1']
    AddTest(
        name    =   'erot_bypmon_illegal_rd_test_fpga',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''EROT bypass monitor illegal read command block'''
            )

    test_args   =   ['''-py erot_bypmon_no_pass_test_fpga.py '''] + RCV_BOOT
    test_tags   =   ['bypmon','l1']
    AddTest(
        name    =   'erot_bypmon_no_pass_test_fpga',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''EROT bypass monitor no_pass mode command block'''
            )

    test_args   =   ['''-py erot_bypmon_locker_test_fpga.py '''] + RCV_BOOT
    test_tags   =   ['bypmon','l2']
    AddTest(
        name    =   'erot_bypmon_locker_test_fpga',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''EROT bypass monitor reg aperture lock'''
            )

    # bypass monitor bring-up tests END

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


    #jtag bring-up tests
    test_args   =   ['''-py erot_j2h_pll_config_test.py --platform JTAG ''']
    test_tags   =   ['jtag_bring_up']
    AddTest(
        name    =   'erot_j2h_pll_config_test',
        config  =   ['erot_fpga'],
        args    =   common_args + test_args,
        tags    =   test_tags,
        desc    =   '''Ensure that jtag is able to config pll.'''
            )

    test_args   =   ['''-py erot_j2h_reg_scan_test.py --platform JTAG''']
    test_tags   =   ['jtag_bring_up']
    AddTest(
        name    =   'erot_j2h_reg_scan_test',
        config  =   ['erot_fpga'],
        args    =   common_args + test_args,
        tags    =   test_tags,
        desc    =   '''Ensure that jtag is able to acceess one internal register of all IPs.'''
            )    

    test_args   =   ['''-py erot_j2h_mram_mtpr_test.py --platform JTAG ''']
    test_tags   =   ['jtag_bring_up']
    AddTest(
        name    =   'erot_j2h_mram_mtpr_test',
        config  =   ['erot_fpga'],
        args    =   common_args + test_args,
        tags    =   test_tags,
        desc    =   '''access MRAM by j2h'''
            )

    test_args   =   ['''-py erot_j2h_rcv_reg_test.py -rtlarg '+disable_j2h_vip' -pyarg '--disable_peripheral_init_agent ' --platform JTAG '''] + RCV_BOOT
    test_tags   =   ['jtag_bring_up']
    AddTest(
        name    =   'erot_j2h_rcv_reg_test',
        config  =   ['erot_fpga'],
        args    =   common_args + test_args,
        tags    =   test_tags,
        desc    =   '''J2H and FSP access to OOBHUB recovery registers'''
            )
    
    test_args   =   ['''-py erot_jtag_idcode_test.py --platform JTAG ''']
    test_tags   =   ['jtag_bring_up']
    AddTest(
        name    =   'erot_jtag_idcode',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''Ensure that jtag instruction registers and data registers can be accessed before unlock'''
            )
    
    test_args   =   ['''-py erot_j2h_debug_test.py --platform JTAG ''']
    test_tags   =   ['jtag_bring_up']
    AddTest(
        name    =   'erot_j2h_debug_test',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''Ensure that jtag is able to acceess internal registers'''
            )   

    ## OOBHUB test

    test_args   =   ['''-py erot_oobhub_cms_queriable_test.py  '''] + RCV_BOOT
    test_tags   =   ['oobhub']
    AddTest(
        name    =   'erot_oobhub_cms_queriable',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''check CMS registers'''
            )

    test_args   =   ['''-py erot_oobhub_cmd_rcv_test.py  '''] + RCV_BOOT
    test_tags   =   ['oobhub']
    AddTest(
        name    =   'erot_oobhub_cmd_rcv_test',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''check CMS registers'''
            )

    test_args   =   ['''-py erot_oobhub_pmb_test.py  '''] + RCV_BOOT
    test_tags   =   ['oobhub']
    AddTest(
        name    =   'erot_oobhub_pmb',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''OOBHUB pmb'''
    )

    test_args   =   ['''-py erot_oobhub_cpu_boot.py  '''] + RCV_BOOT
    test_tags   =   ['oobhub']
    AddTest(
        name    =   'erot_oobhub_cpu_boot',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   '''OOBHUB peregrine boot'''
            )

    # SPI target test
    test_args   =   ['''-py erot_spi_smoke_test.py  '''] + RCV_BOOT
    test_tags   =   ['spi']
    AddTest(
        name    =   'erot_spi_smoke_test',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   'spi target smoke test'
            )
    test_args   =   ['''-py erot_spi_target_slave_imr_dspi_test.py  '''] + RCV_BOOT
    test_tags   =   ['spi']
    AddTest(
        name    =   'erot_spi_imr_dspi_test',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   'spi target smoke test'
            ) 

    test_args   =   ['''-py erot_spi_target_slave_imr_tx_dspi_test.py  '''] + RCV_BOOT
    test_tags   =   ['spi']
    AddTest(
        name    =   'erot_spi_imr_tx_dspi_test',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   'spi target smoke test'
            ) 
    test_args   =   ['''-py erot_spi_target_slave_imr_test.py  '''] + RCV_BOOT
    test_tags   =   ['spi']
    AddTest(
        name    =   'erot_spi_imr_test',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   'spi target smoke test'
            ) 

    test_args   =   ['''-py erot_spi_target_slave_imr_tx_test.py  '''] + RCV_BOOT
    test_tags   =   ['spi']
    AddTest(
        name    =   'erot_spi_imr_tx_test',
        config  =   ['erot_fpga'],
        args    =   common_args+test_args,
        tags    =   test_tags,
        desc    =   'spi target smoke test'
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
