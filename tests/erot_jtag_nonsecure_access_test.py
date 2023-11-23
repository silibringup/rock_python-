#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import *
import re

with Test(sys.argv) as t:

    def read_out_sys_status_nonsecure(jtag_unlock=0, print=1):
        reg_field_info = {
            'earlyl1cold_rstn':84,
            'earlyl1warm_rstn':83,
            'earlyl2cold_rstn':82,
            'prebootl2warm_rstn':81,
            'pmc2dfd_reset_detector_buf':80,
            'pmc2dfd_reset_detector_shadow_inv_buf':79,
            'dft2dfd_reset_detector_buf':78,
            'dft2dfd_reset_detector_shadow_inv_buf':77,
            'production_mode_buf':76,
            'production_mode_inv_buf':75,
            'fuse2all_fuse_outputs_valid_buf':74,
            'fuse2all_fuse_outputs_valid_inv_buf':73,
            'global_deviceen':72,
            'global_jtag_enable_buf':71,
            'fuse_valid_AON':70,
            'jtag_secureID_valid_muxed':69,
            'zeroize_status[0]':68,
            'zeroize_status[1]':67,
            'oem_key_enable':66,
            'fuse_jtag_clk_ungate_req':65,
            'enable_cr_jtag_security_muxed':64,
            'reset2clk_early_pwron_reset_':63,
            'reset2fuse_reset_':62,
            'reset2clk_pwron_reset_':61,
            'l0_reset':60,
            'l1_reset':59,
            'l3_reset':58,
            'VrefRO_CK_OK':57,
            'sysctrl2all_sec_fault_device_lockdown':56,
            'sysctrl2all_sec_fault_function_lockdown':55,
            'sysctrl2rst_recovery_rst_req':54,
            'oobhub2reset_rst_req':53,
            'l1_reset_state[0]':52,
            'l1_reset_state[1]':51,
            'pll_lock':50,
            'vmon_plus_uv2sec_rst_req_n':49,
            'opt_production_mode':48,
            'opt_secure_sec_fault_lockdown_enable_by_default':47,
            'opt_recovery_behavior_en':46,
            'fuse2reset_security_monitor_nvjtag_sel':45,
            'chip_test_mode_sticky':44,
            'opt_security_mode':43,
            'opt_rma_enable':42,
            'opt_rma_disable':41,
            'opt_fa_mode':40,
            'oobhub_idle':39,
            'oobhub_rst_':38,
            'sysctrl2all_device_lockdown':37,
            'oobhub2sysctrl_force_recovery':36,
            'sysctrl2oobhub_recovery_pending':35,
            'oobhub_recovery_strap_id[0]':34,
            'oobhub_recovery_strap_id[1]':33,
            'oobhub_recovery_strap_id[2]':32,
            'fuse_rstn':31,
            'NV_FSP_reset_reset_':30,
            'fuse2all_brpa_effective':29,
            'fuse2all_sensitive_j_type_romdump_en':28,
            'opt_secure_scc_dis':27,
            'opt_secure_scandebug_access_disable_final':26,
            'opt_fsp_riscv_br_error_info_en':25,
            'opt_pkc_pk_selection':24,
            'opt_secure_fsp_phys_isolation_en':23,
            'opt_oaa_sel[0]':22,
            'opt_oaa_sel[1]':21,
            'opt_oaa_sel[2]':20,
            'fsp2sysctrl_sec_fault_l4_wdt':19,
            'fsp2sysctrl_sec_fault_l5_wdt':18,
            'fsp2host_status_idle':17,
            'fsp_riscv_dcls_security_trigger_reset':16,
            'sysctrl2fsp_iff_finish':15,
            'opt_secure_scandebug_access_disable_final':14,
            'opt_fsp_mbist_monitor_en':13,
            'opt_fsp_mbist_monitor_en_shadow_inv':12,
            'opt_fsp_testmode_monitor_en':11,
            'opt_fsp_testmode_monitor_en_shadow_inv':10,
            'fsp2sysctrl_sec_fault_emp':9,
            'fsp_fault_scpm':8,
            'fsp2sysctrl_sec_fault_uncorrectable_error':7,
            'NV_FSP_reset_reset_':6,
            'opt_skate_secure_fusing_start':5,
            'opt_skate_secure_fusing_cya_en':4,
            'opt_fsp_prod_sym_key_en':3,
            'opt_fsp_prod_sym_key_en_shadow_inv':2,
            'fuse2fsp_debug_mode':1,
            'fuse2fsp_poison_error_containment':0
        }
        if helper.target == "simv_fpga":
            helper.hdl_force('ntb_top.u_nv_fpga_dut.u_nv_top_fpga.u_nv_top_wrapper.u_nv_top.u_sra_top0.top_pads.u_GPIOB_pad_wrapper.GPIOB_pads.nvjtag_sel', 1)
        else:
            helper.hdl_force('ntb_top.u_nv_top.u_sra_top0.top_pads.u_GPIOB_pad_wrapper.GPIOB_pads.nvjtag_sel', 1)

        LOG("start to read out jtag sys_status_nonsecure reg")
        helper.jtag.Reset(0)
        helper.jtag.Reset(1)
        #jtag unlock
        if(jtag_unlock):
            ir_scan_out = helper.jtag_IRScan(10, 0x018) #Cycle 13
            dr_scan_out = helper.jtag_DRScan(19, 0x00000) #Cycle 30
            ir_scan_out = helper.jtag_IRScan(16, 0x0600) #Cycle 121
            dr_scan_out = helper.jtag_DRScan(19, 0x00080) #Cycle 143
            ir_scan_out = helper.jtag_IRScan(16, 0x0520) #Cycle 167
            ir_scan_out = helper.jtag_IRScan(25, 0x00a1520) #Cycle 189
            dr_scan_out = helper.jtag_DRScan(11, 0x220) #Cycle 220
            dr_scan_out = helper.jtag_DRScan(121, 0x0600000000000000003000000000220) #Cycle 236
            ir_scan_out = helper.jtag_IRScan(25, 0x00a1520) #Cycle 181307
            dr_scan_out = helper.jtag_DRScan(121, 0x0600000000000000003000000000220) #Cycle 181338
            ir_scan_out = helper.jtag_IRScan(25, 0x0120280) #Cycle 181468
            dr_scan_out = helper.jtag_DRScan(7, 0x40) #Cycle 181499
            dr_scan_out = helper.jtag_DRScan(15, 0x00c0) #Cycle 181511
            ir_scan_out = helper.jtag_IRScan(16, 0x0840) #Cycle 181535
            dr_scan_out = helper.jtag_DRScan(17, 0x1ffff) #Cycle 181557
            ir_scan_out = helper.jtag_IRScan(10, 0x014) #Cycle 181583
            ir_scan_out = helper.jtag_IRScan(16, 0x8800) #Cycle 181599
            dr_scan_out = helper.jtag_DRScan(7, 0x40) #Cycle 181621
            dr_scan_out = helper.jtag_DRScan(457, 0x0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000040) #Cycle 181633
            ir_scan_out = helper.jtag_IRScan(16, 0x0740) #Cycle 182099
            dr_scan_out = helper.jtag_DRScan(3076, 0x2000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001) #Cycle 182121
            ir_scan_out = helper.jtag_IRScan(10, 0x01d) #Cycle 185206
            dr_scan_out = helper.jtag_DRScan(3076, 0x4000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001) #Cycle 185222
            ir_scan_out = helper.jtag_IRScan(10, 0x01d) #Cycle 244307
            dr_scan_out = helper.jtag_DRScan(3076, 0x6000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001) #Cycle 244323
            ir_scan_out = helper.jtag_IRScan(10, 0x01d) #Cycle 247408
            dr_scan_out = helper.jtag_DRScan(3076, 0x8000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001) #Cycle 247424
            ir_scan_out = helper.jtag_IRScan(10, 0x025) #Cycle 250519
            dr_scan_out = helper.jtag_DRScan(9, 0x001) #Cycle 250535
            ir_scan_out = helper.jtag_IRScan(10, 0x014) #Cycle 250553
            ir_scan_out = helper.jtag_IRScan(16, 0x0530) #Cycle 250569
            ir_scan_out = helper.jtag_IRScan(34, 0x0d8364d90) #Cycle 250591
            dr_scan_out = helper.jtag_DRScan(13, 0x1ff0) #Cycle 250631
            ir_scan_out = helper.jtag_IRScan(34, 0x3e5f97e50) #Cycle 250649
            ir_scan_out = helper.jtag_IRScan(10, 0x3e5) #Cycle 250689
            dr_scan_out = helper.jtag_DRScan(21, 0x000000) #Cycle 250705
            ir_scan_out = helper.jtag_IRScan(10, 0x3e5) #Cycle 251735
            dr_scan_out = helper.jtag_DRScan(21, 0x000000) #Cycle 251751
            ir_scan_out = helper.jtag_IRScan(10, 0x014) #Cycle 251781
            ir_scan_out = helper.jtag_IRScan(16, 0x3600) #Cycle 251797
            dr_scan_out = helper.jtag_DRScan(7, 0x70) #Cycle 251819
            ir_scan_out = helper.jtag_IRScan(34, 0x3e4f97e50) #Cycle 251831
            dr_scan_out = helper.jtag_DRScan(57, 0x000010000400010) #Cycle 251871

        ir_scan_out = helper.jtag_IRScan(34, 0x234054150) #Cycle 252437
        dr_scan_out = helper.jtag_DRScan(85, 0x0000000000000000002000) #Cycle 252477
        ir_scan_out = helper.jtag_IRScan(34, 0x015054150) #Cycle 252600
        ir_scan_out = helper.jtag_IRScan(10, 0x017) #Cycle 252640
        ir_scan_out = helper.jtag_IRScan(10, 0x014) #Cycle 252656

        dr_scan_out = bin(dr_scan_out)
        helper.pinfo(f'scan out jtag sys_status_nonsecure reg dr scan : {dr_scan_out}')
        dr_scan_out = re.sub('0b','',dr_scan_out)
        dr_scan_out = dr_scan_out.zfill(85)
        sys_status_nonsecure = dr_scan_out
        helper.pinfo(f'scan out jtag sys_status_nonsecure reg : {sys_status_nonsecure}')
        read_out_dict = {}
        
        for key,value in reg_field_info.items():
            read_out_dict[key] = sys_status_nonsecure[value]
            if(print):
                helper.pinfo(f'{key} : {read_out_dict[key]}')
      
        return read_out_dict

    def read_out_jtag_fuse_nonsecure(jtag_unlock=0, print=1):
        reg_field_info = {
            'security_monitor_nvjtag_sel_jtag':[0,1],
            'fusegen_shift_status':[1,2],
            'burn_and_check_status':[2,3],
            'crc_status_h11':[3,6],
            'crc_status_h9':[6,9],
            'crc_status_h8':[9,12],
            'crc_status_h7':[12,15],
            'crc_status_h6':[15,18],
            'current_state_seshift_segment':[18,22],
            'jtag_status_seshift_segment':[22,23],
            'current_state_reshift_segment':[23,27],
            'jtag_reshift_segment_id':[27,37],
            'jtag_status_reshift_segment_3':[37,38],
            'sorter_current_state':[38,42],
            'fsp_sense_done':[42,43],
            'iff_sense_done':[43,44],
            'record_sense_done':[44,45],
            'fpf_sense_done':[45,46],
            'normal_sense_done':[46,47],
            'fuse_init_sense_done':[47,48],
            'intfc_current_state':[48,55],
            'decomp_current_state':[55,59],
            'fusectrl_current_state':[59,64],
            'hw_trig_reshift_segment':[64,65],
            'fuse_jtag_clk_ungate_req':[65,66],
            'fuse_reset_':[66,67],
            'fuse_ungate_jtag_unlock_status':[67,68],
            'static_chip_option_sense_done_status':[68,69],
            'jtag_skip_ram_repair_en':[69,70],
            'jtag_skip_ram_repair':[70,71],
            'gate_priv_signals':[71,72],
            'fuse2all_fuse_outputs_valid_status':[72,73],
            'fuse2all_fuses_sensed_status':[73,74],
            'jtag_ecid_chip_option_offset':[74,78],
            'jtag_ecid_data':[78,110],
        }
         
        if helper.target == "simv_fpga":
            helper.hdl_force('ntb_top.u_nv_fpga_dut.u_nv_top_fpga.u_nv_top_wrapper.u_nv_top.u_sra_top0.top_pads.u_GPIOB_pad_wrapper.GPIOB_pads.nvjtag_sel', 1)
        else:
            helper.hdl_force('ntb_top.u_nv_top.u_sra_top0.top_pads.u_GPIOB_pad_wrapper.GPIOB_pads.nvjtag_sel', 1)

        LOG("start to read out jtag jtag_fuse_nonsecure reg")
        helper.jtag.Reset(0)
        helper.jtag.Reset(1)
        #jtag unlock
        if(jtag_unlock):
            ir_scan_out = helper.jtag_IRScan(10, 0x018) #Cycle 13
            dr_scan_out = helper.jtag_DRScan(19, 0x00000) #Cycle 30
            ir_scan_out = helper.jtag_IRScan(16, 0x0600) #Cycle 121
            dr_scan_out = helper.jtag_DRScan(19, 0x00080) #Cycle 143
            ir_scan_out = helper.jtag_IRScan(16, 0x0520) #Cycle 167
            ir_scan_out = helper.jtag_IRScan(25, 0x00a1520) #Cycle 189
            dr_scan_out = helper.jtag_DRScan(11, 0x220) #Cycle 220
            dr_scan_out = helper.jtag_DRScan(121, 0x0600000000000000003000000000220) #Cycle 236
            ir_scan_out = helper.jtag_IRScan(25, 0x00a1520) #Cycle 181307
            dr_scan_out = helper.jtag_DRScan(121, 0x0600000000000000003000000000220) #Cycle 181338
            ir_scan_out = helper.jtag_IRScan(25, 0x0120280) #Cycle 181468
            dr_scan_out = helper.jtag_DRScan(7, 0x40) #Cycle 181499
            dr_scan_out = helper.jtag_DRScan(15, 0x00c0) #Cycle 181511
            ir_scan_out = helper.jtag_IRScan(16, 0x0840) #Cycle 181535
            dr_scan_out = helper.jtag_DRScan(17, 0x1ffff) #Cycle 181557
            ir_scan_out = helper.jtag_IRScan(10, 0x014) #Cycle 181583
            ir_scan_out = helper.jtag_IRScan(16, 0x8800) #Cycle 181599
            dr_scan_out = helper.jtag_DRScan(7, 0x40) #Cycle 181621
            dr_scan_out = helper.jtag_DRScan(457, 0x0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000040) #Cycle 181633
            ir_scan_out = helper.jtag_IRScan(16, 0x0740) #Cycle 182099
            dr_scan_out = helper.jtag_DRScan(3076, 0x2000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001) #Cycle 182121
            ir_scan_out = helper.jtag_IRScan(10, 0x01d) #Cycle 185206
            dr_scan_out = helper.jtag_DRScan(3076, 0x4000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001) #Cycle 185222
            ir_scan_out = helper.jtag_IRScan(10, 0x01d) #Cycle 244307
            dr_scan_out = helper.jtag_DRScan(3076, 0x6000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001) #Cycle 244323
            ir_scan_out = helper.jtag_IRScan(10, 0x01d) #Cycle 247408
            dr_scan_out = helper.jtag_DRScan(3076, 0x8000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001) #Cycle 247424
            ir_scan_out = helper.jtag_IRScan(10, 0x025) #Cycle 250519
            dr_scan_out = helper.jtag_DRScan(9, 0x001) #Cycle 250535
            ir_scan_out = helper.jtag_IRScan(10, 0x014) #Cycle 250553
            ir_scan_out = helper.jtag_IRScan(16, 0x0530) #Cycle 250569
            ir_scan_out = helper.jtag_IRScan(34, 0x0d8364d90) #Cycle 250591
            dr_scan_out = helper.jtag_DRScan(13, 0x1ff0) #Cycle 250631
            ir_scan_out = helper.jtag_IRScan(34, 0x3e5f97e50) #Cycle 250649
            ir_scan_out = helper.jtag_IRScan(10, 0x3e5) #Cycle 250689
            dr_scan_out = helper.jtag_DRScan(21, 0x000000) #Cycle 250705
            ir_scan_out = helper.jtag_IRScan(10, 0x3e5) #Cycle 251735
            dr_scan_out = helper.jtag_DRScan(21, 0x000000) #Cycle 251751
            ir_scan_out = helper.jtag_IRScan(10, 0x014) #Cycle 251781
            ir_scan_out = helper.jtag_IRScan(16, 0x3600) #Cycle 251797
            dr_scan_out = helper.jtag_DRScan(7, 0x70) #Cycle 251819
            ir_scan_out = helper.jtag_IRScan(34, 0x3e4f97e50) #Cycle 251831
            dr_scan_out = helper.jtag_DRScan(57, 0x000010000400010) #Cycle 251871
            ir_scan_out = helper.jtag_IRScan(34, 0x014f97e40) #Cycle 252437
            ir_scan_out = helper.jtag_IRScan(25, 0x00a1520) #Cycle 252477
            dr_scan_out = helper.jtag_DRScan(121, 0x16000000000000000030000000003e0) #Cycle 252508
            ir_scan_out = helper.jtag_IRScan(25, 0x00a1530) #Cycle 252720
            ir_scan_out = helper.jtag_IRScan(34, 0x015054150) #Cycle 252751
            ir_scan_out = helper.jtag_IRScan(10, 0x017) #Cycle 252791
            ir_scan_out = helper.jtag_IRScan(10, 0x014) #Cycle 252807       
        else:
            ir_scan_out = helper.jtag_IRScan(10, 0x018) #Cycle 13
            dr_scan_out = helper.jtag_DRScan(19, 0x00000) #Cycle 30
            ir_scan_out = helper.jtag_IRScan(16, 0x0600) #Cycle 121
            dr_scan_out = helper.jtag_DRScan(19, 0x00080) #Cycle 143
            ir_scan_out = helper.jtag_IRScan(16, 0x0520) #Cycle 167
            ir_scan_out = helper.jtag_IRScan(25, 0x00a1520) #Cycle 189
            dr_scan_out = helper.jtag_DRScan(11, 0x220) #Cycle 220
            dr_scan_out = helper.jtag_DRScan(121, 0x0600000000000000003000000000220) #Cycle 236

        dr_scan_out = bin(dr_scan_out)
        helper.pinfo(f'scan out jtag jtag_fuse_nonsecure reg dr scan : {dr_scan_out}')
        dr_scan_out = re.sub('0b','',dr_scan_out)
        dr_scan_out = dr_scan_out.zfill(121)
        dr_scan_out = dr_scan_out[1:111]
        dr_scan_out = dr_scan_out.zfill(110)
        jtag_fuse_nonsecure = dr_scan_out
        helper.pinfo(f'scan out jtag jtag_fuse_nonsecure reg : {jtag_fuse_nonsecure}')
        read_out_dict = {}
        
        for key,value in reg_field_info.items():
            read_out_dict[key] = jtag_fuse_nonsecure[value[0]:value[1]]
            if(print):
                helper.pinfo(f'{key} : {read_out_dict[key]}')
        
        return read_out_dict      
    
    LOG("jtag nonsecure access Test Starts!")
    read_out_sys_status_nonsecure()
    read_out_jtag_fuse_nonsecure()
    
    #read_out_sys_status_nonsecure(jtag_unlock=1)
    #read_out_jtag_fuse_nonsecure(jtag_unlock=1)    
    LOG("jtag nonsecure access Test Ends!")


