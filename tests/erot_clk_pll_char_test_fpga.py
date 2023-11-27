#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import *
import time

with Test(sys.argv) as t:
    def parse_args():
        t.parser.add_argument("--pll_pdiv", action='store', help="PLL PDIV value", default="0x14")
        return t.parser.parse_args(sys.argv[1:])

    helper.log("###################################################################################################")
    helper.log("###################################### PLL Char Test Starts! ######################################")
    helper.log("###################################################################################################")

    #############################################################################################################
    ################################# simv force, would be ignored on real silicon ##############################
    #############################################################################################################
    helper.wait_sim_time("us", 50)
    helper.hdl_force('ntb_top.u_nv_top.nvjtag_sel', 1)
    helper.hdl_force("ntb_top.u_clk_rst_if.enable_clk_debugout", 1)

    #############################################################################################################
    ############################################ argument decode ################################################
    #############################################################################################################
    options = parse_args() 
    pll_pdiv_ovr = hex(int(options.pll_pdiv,16))

    #############################################################################################################
    ############################################### J2H unlock ##################################################
    #############################################################################################################
    helper.jtag.Reset(0)
    helper.jtag.DRScan(100, hex(0x0)) #add some delay as jtag only work when nvjtag_sel stable in real case
    helper.jtag.Reset(1)
    helper.log("j2h_unlock sequence start")
    helper.j2h_unlock()
    helper.log("j2h_unlock sequence finish")

    #############################################################################################################
    ############################################# JTAG wr: DBG PRB ##############################################
    #############################################################################################################
    # debug mux sel
    # [7:0]     => OBS26
        # 0xff => VrefRO
        # 0xf7 => PLL
        # others => system internal clk
    # [11:8]    => OBS27
        # 0x0 => pll_freqlock
        # 0x1 => pll_lock
        # others => POD_VMON BE trigger
    # [15:12]   => OBS28
        # 0x0 => pll_freqlock
        # 0x1 => pll_enable
        # others => POD_VMON FE trigger
    helper.log("DBG_MUX CLK_SEL WAR API Starts!")
    test_api.jtag_mux_ovr('dbg_mux_clk_sel', 0x01f7, 1)
    helper.wait_sim_time("us", 1)
    helper.log("DBG_MUX CLK_SEL WAR API Ends!")

    # safe clk mode
        # 0x0 => TCK
        # 0x1 => debug mux output
    helper.log("DBG_MUX SAFE_CLK_MODE_ WAR API Starts!")
    test_api.jtag_mux_ovr('dbg_mux_safe_clk_mode_', 0x1, 1)
    helper.wait_sim_time("us", 1)
    helper.log("DBG_MUX SAFE_CLK_MODE_ WAR API Ends!")

    # OBS GPIO SEL & PAD direction
        # 0x0 => PAD as input
        # 0x1 => PAD as output, GPIO select debug mux output
    helper.log("OBS_PAD SEL WAR API Starts!")
    test_api.jtag_mux_ovr('obs_pad_sel', 0x1, 1)
    helper.wait_sim_time("us", 1)
    helper.log("OBS_PAD SEL WAR API Ends!")

    helper.log("OBS PAD ready!!!")

    #############################################################################################################
    ############################################ J2H wr: IDDQ/ENABLE ############################################
    #############################################################################################################
    # existing PLL config in BROM, J2H hack here for quick simv
    if helper.target == "simv_top":
        erot.CLOCK.NVEROT_CLOCK_SYS_CTL.SW_PLL_1_0.debug_write(IDDQ=0)
        helper.wait_sim_time("us", 5)
        time.sleep(1)
        erot.CLOCK.NVEROT_CLOCK_SYS_CTL.SW_PLL_1_0.debug_write(ENABLE=1)
        helper.wait_sim_time("us", 50)
        time.sleep(1)
        helper.log("PLL config done")

    #############################################################################################################
    ######################################## J2H/JTAG rd: PLL lock status #######################################
    #############################################################################################################
    # J2H rd
    erot.CLOCK.NVEROT_CLOCK_STATUS.PLL_LOCK_STATUS_0.debug_poll(PLL_LOCK=1)
    # JTAG rd
#    count = 0
#    timeout = 100000
#    while count < timeout:
#        count += 1
#        chain_value, pll_lock = test_api.jtag_reg_read('pll_lock')
#        helper.log(f"chain_value: {hex(chain_value)}")
#        helper.log(f'pll_lock: {str(pll_lock)}')
#        if pll_lock == 1:
#            helper.log(f"PLL locked @ {count} times try")
#            break
#        elif count == 99999:
#            helper.perror(f"Poll pll_lock timeout after {count} times try. Reg value = 0x0. Exp value = 0x1")
#            break
#        helper.wait_sim_time("us", 2)
            
    #############################################################################################################
    ############################################# JTAG wr: PLL PDIV #############################################
    #############################################################################################################
#    helper.log("PLL PDIV WAR API Starts!")
#    test_api.jtag_mux_ovr('pll_pdiv', 0x14, 1)
#    helper.wait_sim_time("us", 2)
#    helper.log("PLL PDIV WAR API Ends!")
    helper.log(f'PLL PDIV: {pll_pdiv_ovr}')
    erot.CLOCK.NVEROT_CLOCK_SYS_CTL.SW_PLL_0_0.debug_write(PDIV=int(options.pll_pdiv,16))
    helper.wait_sim_time("us", 100)

    helper.log("NOTICE: check PLL freq/lock/freqlock thru scope...")
    helper.log("NOTICE: check SR01 GP26 @ B01 pin J38")
    helper.log("NOTICE: check SR01 GP27 @ B01 pin J37")
    helper.log("NOTICE: check SR01 GP28 @ B01 pin J36")

    helper.log("###################################################################################################")
    helper.log("####################################### PLL Char Test Ends! #######################################")
    helper.log("###################################################################################################")
