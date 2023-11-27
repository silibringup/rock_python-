#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import *
import time

with Test(sys.argv) as t:
    def parse_args():
        t.parser.add_argument("--vrefro_freqadj", action='store', help="VrefRO FREQADJ ovr value", default="0x9")
        return t.parser.parse_args(sys.argv[1:])

    helper.log("###################################################################################################")
    helper.log("##################################### VrefRO Char Test Starts! ####################################")
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
    vrefro_freqadj_ovr = hex(int(options.vrefro_freqadj,16))

    #############################################################################################################
    ############################################### JTAG unlock #################################################
    #############################################################################################################
    helper.jtag.Reset(0)
    helper.jtag.DRScan(100, hex(0x0)) #add some delay as jtag only work when nvjtag_sel stable in real case
    helper.jtag.Reset(1)
    helper.log("jtag_unlock sequence start")
    test_api.jtag_unlock()
    helper.log("jtag_unlock sequence finish")

    #############################################################################################################
    ############################################# JTAG wr: DBG PRB ##############################################
    #############################################################################################################
    # JTAG wr: safe clk mode
        # 0x0 => TCK
        # 0x1 => debug mux output
    helper.log("DBG_MUX SAFE_CLK_MODE_ WAR API Starts!")
    test_api.jtag_mux_ovr('dbg_mux_safe_clk_mode_', 0x1, 1)
    helper.wait_sim_time("us", 5)
    helper.log("DBG_MUX SAFE_CLK_MODE_ WAR API Ends!")
    time.sleep(1)

    # JTAG wr: OBS GPIO SEL & PAD direction
        # 0x0 => PAD as input
        # 0x1 => PAD as output, GPIO select debug mux output
    helper.log("OBS_PAD SEL WAR API Starts!")
    test_api.jtag_mux_ovr('obs_pad_sel', 0x1, 1)
    helper.wait_sim_time("us", 5)
    helper.log("OBS_PAD SEL WAR API Ends!")
    time.sleep(1)

    helper.log("OBS PAD ready!!!")

    #############################################################################################################
    ########################################## JTAG wr: VrefRO FREQADJ ##########################################
    #############################################################################################################
    helper.log("VrefRO FREQADJ WAR API Starts!")
    helper.log(f'VrefRO FREQADJ: {vrefro_freqadj_ovr}')
    test_api.jtag_mux_ovr('vrefro_freqadj', int(options.vrefro_freqadj,16), 1)
    helper.log("VrefRO FREQADJ WAR API Ends!")
    helper.wait_sim_time("us", 200)
    time.sleep(2)

    helper.log("NOTICE: check VrefRO freq thru scope...")
    helper.log("NOTICE: check SR01 GP26 @ B01 pin J38")

    helper.log("###################################################################################################")
    helper.log("##################################### VrefRO Char Test Ends! ######################################")
    helper.log("###################################################################################################")

