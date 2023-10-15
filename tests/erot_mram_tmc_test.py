#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import * 
import random

with Test(sys.argv) as t:
    mram = erot.MRAM


    def get_mram_32bx8_list_backdoor(idx_256b):
        data32b_list = []
        helper.log("idx_256b = %0d" % idx_256b)
        for i in range(8):
            mem_element_dir_dw = "ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.mram_inst.core.main_mem[%d][%s:%s]" % (idx_256b, i*32+31, i*32)
            data32b = helper.hdl_read(mem_element_dir_dw)
            data32b_list.append(data32b)
        return data32b_list

    def write_256b_through_tmc_aperture(xadr, yadr, data_32b=0x5a5a5a5a):
        if yadr > 31:
            helper.perror("yadr > 32")
        if xadr > 4095:
            helper.perror("xadr > 4095")
        mram.mram_cfg_b_apert_mmio_acl_0.update(tmc_aperture_mmio_readable=0,tmc_aperture_mmio_writable=1)
        exp_data_list = []
        for i in range(8):
            wr_data_reg = mram.get_reg_by_name("mram_tmc_udin_i" + str(i) + "_0")
            wr_data = data_32b#random.randint(0, 0xffffffff)
            exp_data_list.append(wr_data)
            wr_data_reg.write(wr_data)
        mram.mram_tmc_xadr_i_0.write(xadr)
        mram.mram_tmc_yadr_i_0.write(yadr)
        mram.mram_tmc_cmd_i_0.update(load=1)
        mram.mram_tmc_cmd_i_0.update(write=1)
        # change to use real fpga delay method
        helper.wait_sim_time("us", 10)
        index_256b = xadr*32+yadr
        if helper.target in ["fpga", "simv_fpga"]:
            helper.log("fpga can not check the write fail status, so not to check the write result")
        else:
            # fpga can not check the write fail status
            backdoor_result_list = get_mram_32bx8_list_backdoor(index_256b)
            if backdoor_result_list != exp_data_list:
                helper.perror("Mismatch, write fail")
        return exp_data_list

    def read_256b_through_tmc_aperture(xadr, yadr):
        if yadr > 31:
            helper.perror("yadr > 32")
        if xadr > 4095:
            helper.perror("xadr > 4095")
        mram.mram_cfg_b_apert_mmio_acl_0.update(tmc_aperture_mmio_readable=1,tmc_aperture_mmio_writable=0)
        mram.mram_tmc_xadr_i_0.write(xadr)
        mram.mram_tmc_yadr_i_0.write(yadr)
        mram.mram_tmc_cmd_i_0.update(read=1)
        # change to use real fpga delay method
        helper.wait_sim_time("us", 10)
        act_data_list = []
        for i in range(8):
            rd_data_reg = mram.get_reg_by_name("mram_tmc_udout_o" + str(i) + "_0")
            rd = rd_data_reg.read()
            act_data_list.append(rd.value)
        return act_data_list

    def check_tmc_error_status():
        for err_key in range(1, 32):
            # recall_key_err should fire recall_err
            if err_key & 0x10 == 16 and err_key & 0x8 == 0:
                continue
            helper.hdl_force("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.bistmc_top_0.tmc_top.i_tmc_if.tmc_err_type", err_key)
            if err_key != 0:
                helper.hdl_force("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.bistmc_top_0.tmc_top.i_tmc_if.tmc_err", 1)
            helper.wait_sim_time("ns", 40)
            helper.hdl_force("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.bistmc_top_0.tmc_top.i_tmc_if.tmc_err", 0)
            helper.hdl_force("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.bistmc_top_0.tmc_top.i_tmc_if.tmc_err_type", 0)
            helper.wait_sim_time("us", 1)
            rd = mram.mram_tmc_error_status_o_0.read()
            helper.log("rd.value = %x, err_key = %x" % (rd.value, err_key))
            if rd.value != err_key:
                helper.perror("-- Cannot fetch tmc_err_type through mram_tmc_error_status_o_0")
            mram.mram_tmc_err_clr_0.write(0x1)
            rd = mram.mram_tmc_error_status_o_0.read()
            if rd.value != 0:
                helper.perror("-- Cannot clear tmc_err_type through mram_tmc_err_clr_0")
            rd = mram.mram_tmc_err_clr_0.read()
            if rd.value != 0:
                helper.perror("-- mram_tmc_err_clr_0's value doesn't return to 0 after clearing")

    def check_ecc_err_loc():
        for i in range(274):
            bank_idx = int(i/32)
            bit_idx = int(i%32)
            ecc_err_bit_str = "ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.bistmc_top_0.tmc_top.tmc_ecc_err_loc"
            helper.hdl_force(ecc_err_bit_str, int(1<<i))
            helper.hdl_force("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.bistmc_top_0.tmc_top.i_tmc_if.tmc_err_type", 4)

            helper.log("i = %0d, bank_idx = %0d, bit_idx = %0d" % (i, bank_idx, bit_idx))
            err_log_reg = mram.get_reg_by_name("mram_tmc_ecc_err_loc_" + str(bank_idx) + "_0")
            rd = err_log_reg.read()
            if rd.value != (1<<bit_idx):
                helper.perror("Mismatch, err_loc_%0d_0, bit %0d" % (bank_idx, bit_idx))
            for j in range(9):
                if j == bank_idx:
                    continue
                err_log_reg = mram.get_reg_by_name("mram_tmc_ecc_err_loc_" + str(j) + "_0")
                rd = err_log_reg.read()
                if rd.value != 0:
                    helper.perror("Unexpect ecc error in bank %0d" % j)
            # confirm that the reg cannot be re-write without clearing
            #helper.hdl_force("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.bistmc_top_0.tmc_top.tmc_ecc_err_loc", 0)
            helper.hdl_force(ecc_err_bit_str, 0)
            #old_bank_idx = bank_idx
            #old_bit_idx = bit_idx
            err_log_reg = mram.get_reg_by_name("mram_tmc_ecc_err_loc_" + str(bank_idx) + "_0")
            rd = err_log_reg.read()
            if rd.value == 0:
                helper.perror("err_loc_%0d_0, bit %0d, shouldn't be rewrote before clearing" % (bank_idx, bit_idx))
            helper.hdl_force("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.bistmc_top_0.tmc_top.i_tmc_if.tmc_err_type", 0)
            mram.mram_tmc_ecc_err_loc_clr_0.write(0x1)
            mram.mram_tmc_ecc_err_loc_clr_0.write(0x0)
            for j in range(9):
                err_log_reg = mram.get_reg_by_name("mram_tmc_ecc_err_loc_" + str(j) + "_0")
                rd = err_log_reg.read()
                if rd.value != 0:
                    helper.perror("everything should be cleared for mram_tmc_ecc_err_loc_%0d" % j)




    drive_pin_list = [
        "mram_tmc_lpr_i_0",
        "mram_tmc_grpsel_i_0",
        "mram_tmc_info_i_0",
        "mram_tmc_xadr_i_0",
        "mram_tmc_yadr_i_0",
        "mram_tmc_tdin_i_0",
        "mram_tmc_info1_i_0",
        "mram_tmc_reden_i_0",
        "mram_tmc_sram_dma_i_0",
        "mram_tmc_cfg_vbl_ext_vmax_0",
        "mram_tmc_otp_i_0"
    ]

    pin_ro_list = [
        "mram_tmc_udout_o0_0",
        "mram_tmc_udout_o1_0",
        "mram_tmc_udout_o2_0",
        "mram_tmc_udout_o3_0",
        "mram_tmc_udout_o4_0",
        "mram_tmc_udout_o5_0",
        "mram_tmc_udout_o6_0",
        "mram_tmc_udout_o7_0",
        "mram_tmc_regif_dout_o_0",
        "mram_tmc_ecc_err_loc_0_0",
        "mram_tmc_ecc_err_loc_1_0",
        "mram_tmc_ecc_err_loc_2_0",
        "mram_tmc_ecc_err_loc_3_0",
        "mram_tmc_ecc_err_loc_4_0",
        "mram_tmc_ecc_err_loc_5_0",
        "mram_tmc_ecc_err_loc_6_0",
        "mram_tmc_ecc_err_loc_7_0",
        "mram_tmc_ecc_err_loc_8_0",
        "mram_tmc_tdout_o_0",
        "mram_tmc_sram_dout_o0_0",
        "mram_tmc_sram_dout_o1_0"
    ]

#                    "mram_tmc_sram_dout_o0_0",
#                    "mram_tmc_sram_dout_o1_0",






    

    helper.log("Test starts")
    tmc_hier_name = "ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.bistmc_top_0.tmc_top."

    helper.log("Check mram_tmc_tdout_o_0")
    mram.mram_cfg_b_mtp_wport_acl_0_0.update(out_region=1)
    mram.mram_cfg_b_mtp_rport_acl_0_0.update(out_region=1)
    wr_data_list = []
    wr_addr = 1*32
    for i in range(9):
        if i < 8:
            wr_data_reg = mram.get_reg_by_name("mram_mtp_wport_data_" + str(i) + "_0")
            wr_data = random.randint(0, 0xffffffff)
            wr_data_list.append(wr_data)
            wr_data_reg.write(wr_data)
        else:
            mram.mram_mtp_wport_addr_0.write(VAL=wr_addr)
    mram.mram_mtp_wport_cmd_0.write(TRIG=1)
    mram.mram_mtp_wport_state_0.poll(BUSY=0)

    mram.mram_mtp_rport_addr_0.write(VAL=wr_addr)
    mram.mram_mtp_rport_cmd_0.write(TRIG=1)
    mram.mram_mtp_rport_state_0.poll(BUSY=0)

    rd = mram.mram_tmc_tdout_o_0.read()
    if rd.value == 0:
        helper.perror("With ECC default enable, mram_tmc_tdout_o_0's value should not be 0 after a MTP rd")


    helper.log("Cfg TSMC TMC reg")
    mram.mram_tmc_udin_i0_0.write(wr_buf=0x1)
    mram.mram_tmc_xadr_i_0.write(0x0)
    mram.mram_tmc_cmd_i_0.update(wrt_config=1)
    mram.mram_tmc_udin_i0_0.write(wr_buf=0x34880061)
    mram.mram_tmc_xadr_i_0.write(0x1)
    mram.mram_tmc_cmd_i_0.update(wrt_config=1)
    mram.mram_tmc_xadr_i_0.write(0x1)
    mram.mram_tmc_cmd_i_0.update(read_config=1)
    while True:
        rd = mram.mram_tmc_regif_dout_o_0.read()
        if rd['rd_buf'] & 0xc == 0:
            break

#                    "mram_tmc_sram_dout_o0_0",
#                    "mram_tmc_sram_dout_o1_0",

    if helper.target in ["fpga", "simv_fpga"]:
        helper.log("FPGA cannot use force so not to test some conditions")
    else:
        helper.log("Check mram_tmc_sram_dout_o0_0")
        #exp_data = random.randint(0, 0x3ffffffffffff)
        exp_data = 0x25a5a5a5a5a5a
        helper.hdl_force("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.bistmc_top_0.tmc_top.tmc_sram_dout[31:0]", (exp_data & 0xffffffff))
        helper.hdl_force("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.bistmc_top_0.tmc_top.tmc_sram_dout[49:32]", ((exp_data>>32) & 0x3ffff))
        rd = mram.mram_tmc_sram_dout_o0_0.read()
        sram_dout_31_0 = rd.value
        rd = mram.mram_tmc_sram_dout_o1_0.read()
        sram_dout_49_32 = rd.value & 0x3ffff

        if ((sram_dout_49_32<<32)|sram_dout_31_0) != exp_data:
            helper.perror("Mismatch to access mram_tmc_sram_dout_o0_0/mram_tmc_sram_dout_o1_0, exp: %x, act: %x" % (exp_data, ((sram_dout_49_32<<32)|sram_dout_31_0)))

        exp_data = 0x1a5a5a5a5a5a5
        helper.hdl_force("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.bistmc_top_0.tmc_top.tmc_sram_dout[31:0]", (exp_data & 0xffffffff))
        helper.hdl_force("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.bistmc_top_0.tmc_top.tmc_sram_dout[49:32]", ((exp_data>>32) & 0x3ffff))
        rd = mram.mram_tmc_sram_dout_o0_0.read()
        sram_dout_31_0 = rd.value
        rd = mram.mram_tmc_sram_dout_o1_0.read()
        sram_dout_49_32 = rd.value & 0x3ffff

        if ((sram_dout_49_32<<32)|sram_dout_31_0) != exp_data:
            helper.perror("Mismatch to access mram_tmc_sram_dout_o0_0/mram_tmc_sram_dout_o1_0, exp: %x, act: %x" % (exp_data, ((sram_dout_49_32<<32)|sram_dout_31_0)))

        exp_data = 0x25a5a5a5a5a5a
        helper.hdl_force("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.bistmc_top_0.tmc_top.tmc_sram_dout[31:0]", (exp_data & 0xffffffff))
        helper.hdl_force("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.bistmc_top_0.tmc_top.tmc_sram_dout[49:32]", ((exp_data>>32) & 0x3ffff))
        rd = mram.mram_tmc_sram_dout_o0_0.read()
        sram_dout_31_0 = rd.value
        rd = mram.mram_tmc_sram_dout_o1_0.read()
        sram_dout_49_32 = rd.value & 0x3ffff

        if ((sram_dout_49_32<<32)|sram_dout_31_0) != exp_data:
            helper.perror("Mismatch to access mram_tmc_sram_dout_o0_0/mram_tmc_sram_dout_o1_0, exp: %x, act: %x" % (exp_data, ((sram_dout_49_32<<32)|sram_dout_31_0)))

        helper.log("Check bypassBIST_tmc_regif_dout")
        #exp_data = random.randint(0, 0x3ffffffffffff)
        exp_data = 0x5a5a5a5a
        helper.hdl_force("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.bistmc_top_0.tmc_top.tmc_regif_dout[31:0]", exp_data)
        rd = mram.mram_tmc_regif_dout_o_0.read()
        regif_dout_31_0 = rd.value

        if regif_dout_31_0 != exp_data:
            helper.perror("Mismatch to access mram_tmc_regif_dout_o_0, exp: %x, act: %x" % (exp_data, regif_dout_31_0))

        exp_data = 0xa5a5a5a5
        helper.hdl_force("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.bistmc_top_0.tmc_top.tmc_regif_dout[31:0]", exp_data)
        rd = mram.mram_tmc_regif_dout_o_0.read()
        regif_dout_31_0 = rd.value

        if regif_dout_31_0 != exp_data:
            helper.perror("Mismatch to access mram_tmc_regif_dout_o_0, exp: %x, act: %x" % (exp_data, regif_dout_31_0))
   
        exp_data = 0x5a5a5a5a
        helper.hdl_force("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.bistmc_top_0.tmc_top.tmc_regif_dout[31:0]", exp_data)
        rd = mram.mram_tmc_regif_dout_o_0.read()
        regif_dout_31_0 = rd.value

        if regif_dout_31_0 != exp_data:
            helper.perror("Mismatch to access mram_tmc_regif_dout_o_0, exp: %x, act: %x" % (exp_data, regif_dout_31_0))

        helper.log("Drive pin test")

        
        rand_32b_value = 0
        tmp_32b_idx = -1
        for reg_name in drive_pin_list:
            helper.log("Test reg {%s}" % reg_name)
            m = re.search('mram_(.+)(\d+)_\d+$', reg_name)
            if m != None:
                tmc_pin_name = m.group(1)
                tmp_32b_idx = int(m.group(2))
                upper_bit = (tmp_32b_idx+1)*32-1
                lower_bit = tmp_32b_idx*32
                pin_full_dir = tmc_hier_name + tmc_pin_name + "[" + str(upper_bit) + ":" + str(lower_bit) + "]"
            else:
                m = re.search('mram_(.+)_\d+$', reg_name)
                tmc_pin_name = m.group(1)
                if tmc_pin_name == "tmc_cfg_vbl_ext_vmax":
                    tmc_pin_name = "tmc_cfg_vbl_ext_vmax_i"
                elif tmc_pin_name == "tmc_otp_i":
                    tmc_pin_name = "tmc_otpen_i"
                pin_full_dir = tmc_hier_name + tmc_pin_name
           
            helper.log("reg_name is %s" % reg_name)
            reg = mram.get_reg_by_name(reg_name)
            if len(reg.field_list) > 1:
                helper.perror("-- A pin drive reg should only drive 1 pin")

            field_obj = reg.field_list[0]
            msb,lsb = field_obj['msb'],field_obj['lsb']
            fld_name = field_obj['name']
            while True:
                exp = random.randint(0, 2**(msb-lsb+1) - 1)
                if exp != field_obj['default']:
                    break
            reg.write(None, **{fld_name: exp})

            act_pin_value = helper.hdl_read(pin_full_dir)
            if isinstance(act_pin_value, str):
                helper.perror("-- Unexpected, tmc pin value is X or Z")
            elif act_pin_value != exp:
                helper.perror("-- Unexpected, reg {%s} cannot drive tmc pin {%s} with value %x" % (reg_name, pin_full_dir, exp))

            exp = field_obj['default']
            reg.write(None, **{fld_name: exp})
            
            act_pin_value = helper.hdl_read(pin_full_dir)
            if isinstance(act_pin_value, str):
                helper.perror("-- Unexpected, tmc pin value is X or Z")
            elif act_pin_value != exp:
                helper.perror("-- Unexpected, reg {%s} cannot drive tmc pin {%s} with value %x" % (reg_name, pin_full_dir, exp))

        exp = 0x1
        mram.mram_tmc_grpsel_i_0.write(exp)
        act = helper.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.bistmc_top_0.tmc_top.tmc_grpsel_i")
        if isinstance(act, str):
            helper.perror("-- Unexpected, tmc pin value is X or Z")
        elif act != exp:
            helper.perror("-- Unexpected, reg mram_tmc_grpsel_i_0 cannot drive tmc pin tmc_grpsel_i with value %x" % exp)

        exp = 0x2
        mram.mram_tmc_grpsel_i_0.write(exp)
        act = helper.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.bistmc_top_0.tmc_top.tmc_grpsel_i")
        if isinstance(act, str):
            helper.perror("-- Unexpected, tmc pin value is X or Z")
        elif act != exp:
            helper.perror("-- Unexpected, reg mram_tmc_grpsel_i_0 cannot drive tmc pin tmc_grpsel_i with value %x" % exp)

        exp = 0x1
        mram.mram_tmc_grpsel_i_0.write(exp)
        act = helper.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.bistmc_top_0.tmc_top.tmc_grpsel_i")
        if isinstance(act, str):
            helper.perror("-- Unexpected, tmc pin value is X or Z")
        elif act != exp:
            helper.perror("-- Unexpected, reg mram_tmc_grpsel_i_0 cannot drive tmc pin tmc_grpsel_i with value %x" % exp)

        exp = 0x5a5a5a
        mram.mram_tmc_tdin_i_0.write(exp)
        act = helper.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.bistmc_top_0.tmc_top.tmc_tdin_i")
        if isinstance(act, str):
            helper.perror("-- Unexpected, tmc pin value is X or Z")
        elif act != exp:
            helper.perror("-- Unexpected, reg mram_tmc_tdin_i_0 cannot drive tmc pin tmc_tdin_i with value %x" % exp)

        exp = 0xa5a5a5
        mram.mram_tmc_tdin_i_0.write(exp)
        act = helper.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.bistmc_top_0.tmc_top.tmc_tdin_i")
        if isinstance(act, str):
            helper.perror("-- Unexpected, tmc pin value is X or Z")
        elif act != exp:
            helper.perror("-- Unexpected, reg mram_tmc_tdin_i_0 cannot drive tmc pin tmc_tdin_i with value %x" % exp)

        exp = 0x5a5a5a
        mram.mram_tmc_tdin_i_0.write(exp)
        act = helper.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.bistmc_top_0.tmc_top.tmc_tdin_i")
        if isinstance(act, str):
            helper.perror("-- Unexpected, tmc pin value is X or Z")
        elif act != exp:
            helper.perror("-- Unexpected, reg mram_tmc_tdin_i_0 cannot drive tmc pin tmc_tdin_i with value %x" % exp)


    helper.log("write MRAM through TMC aperture")
    wr_data_list = write_256b_through_tmc_aperture(xadr=0, yadr=5)
    rd_data_list = read_256b_through_tmc_aperture(xadr=0, yadr=5)
    if rd_data_list != wr_data_list:
        helper.perror("-- Mismatch, xadr = 0, yadr = 5")

    wr_data_list = write_256b_through_tmc_aperture(xadr=4095, yadr=31, data_32b=0xa5a5a5a5)
    rd_data_list = read_256b_through_tmc_aperture(xadr=4095, yadr=31)
    if rd_data_list != wr_data_list:
        helper.perror("-- Mismatch, xadr = 4095, yadr = 31")
        

    helper.log("Start test mram_tmc_error_status")
        # change to use real fpga delay method
    helper.wait_sim_time("us", 10)
    # cannot test in real fpga with some force function
    if helper.target in ["fpga", "simv_fpga"]:
        helper.log("cannot test tmc error status in real fpga with some force function")
    else:
        check_tmc_error_status() 
     
    mram.mram_tmc_ecc_err_loc_clr_0.write(0x1)
    mram.mram_tmc_ecc_err_loc_clr_0.write(0x0)
    helper.log("Start check ecc err loc")
    #check_ecc_err_loc()

    
    


 

    helper.log("Test done")






