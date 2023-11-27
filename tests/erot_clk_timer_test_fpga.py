#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import *

with Test(sys.argv) as t:

    # wait for time to set valid bits of NV_PMC_ZB_BOOT_TIMESTAMPS(i), i=[6:12];
    # check the fields of NV_PMC_ZB_BOOT_TIMESTAMPS_NUM_32NS_TICKS respectively

    def trig_evt(exp_interv_us):
        reg = erot.NV_PMC.BOOT_TIMESTAMPS_TRIGGER_EVENTS_0
        field_list = [
            "BOOTROM_START",
            "BOOTROM_LEDGER_PROCESS_DONE",
            "FFL_TRY0_START",
            "FFL_TRY0_DONE",
            "FFL_TRY1_START",
            "FFL_TRY1_DONE",
            "BOOTROM_DONE"
        ]
        for fld in field_list:
            helper.log("TO TRIGGER EVENT [%s]" % fld)
            reg.update(**{fld:"TRIGGER"})
            wait_us(exp_interv_us)

    def wait_us(num):
        helper.log("START TO WAIT [%d] US ..." % num)
        helper.wait_rpi_time(num)
        helper.log("DONE WAITING")

    def check_time(exp_interv_us):
        reg_list = [
            erot.NV_PMC.BOOT_TIMESTAMPS_6,
            erot.NV_PMC.BOOT_TIMESTAMPS_7,
            erot.NV_PMC.BOOT_TIMESTAMPS_8,
            erot.NV_PMC.BOOT_TIMESTAMPS_9,
            erot.NV_PMC.BOOT_TIMESTAMPS_10,
            erot.NV_PMC.BOOT_TIMESTAMPS_11,
            erot.NV_PMC.BOOT_TIMESTAMPS_12,
        ]
        time_list = []
        for idx in range(len(reg_list)):
            test_api.fuse_check_reg_log(reg_list[idx], field_name="VALID", exp=0x1)
            time_num_ = reg_list[idx].read()
            num_ = time_num_['NUM_32NS_TICKS']
            time = 32 * num_
            helper.log("TIME OF REG [%s] IS [%d] NS, NOTICED to * 40 for SR01 " %(reg_list[idx].name, time))
            time_list.append(time)
        # check intervals only
        # tolerance = exp_interv_us * 1000 * 0.1 # 10%, unit = ns
        tolerance = 5 * 1000  # set 5 us fix tolerance
        for j in range(len(time_list)-1):
            intv = (time_list[j+1] - time_list[j]) * 40     # bug 4097696 
            if ( (intv < exp_interv_us*1000 - tolerance) or (intv > exp_interv_us*1000 + tolerance) ) and ('fpga' not in helper.target):
                helper.perror("INTERVAL BETWEEN [%s] AND [%s] WRONG: ACT = [%d] NS; EXP = [%d +/- %d] NS" % (reg_list[j].name, reg_list[j+1].name, intv, exp_interv_us*1000, tolerance) )
            else:
                helper.log("INTERVAL BETWEEN [%s] AND [%s] CORRECT: ACT = [%d] NS; EXP = [%d +/- %d] NS" % (reg_list[j].name, reg_list[j+1].name, intv, exp_interv_us*1000, tolerance) )


    # L0 RST RELEASE : 1453.88 ns   * as beginning *
    # L1 RST RELEASE : 16193.88 ns
    # L3 RST RELEASE : 23013.88 ns

    helper.log("###################################################################################################")
    helper.log("####################################### Timer Test Starts! ########################################")
    helper.log("###################################################################################################")

    exp_interv_us = 50
    trig_evt(exp_interv_us)
    check_time(exp_interv_us)

    helper.log("###################################################################################################")
    helper.log("######################################### Timer Test Ends! ########################################")
    helper.log("###################################################################################################")


