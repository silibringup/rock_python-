#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
import os
import time
import importlib
from driver import *

BMC_I2C_SLV_ADDR = 0x69
BMC_I2C_ID = 3


Testlist = []


def default_cms_selection():
    helper.pinfo("Polling DEVICE_STATUS = RECOVERY_MODE ...")
    success = helper.SMBus_poll(0x3, 0xff, OOB.SMCommand.DEVICE_STATUS, 20)
    if success:
        helper.pinfo("Found DEVICE_STATUS = RECOVERY_MODE")
    
    helper.pinfo("Polling RECOVERY_STATUS = AWITING_RECOVERY_IMAGE ...")
    success = helper.SMBus_poll(0x1, 0xff, OOB.SMCommand.RECOVERY_STATUS, 20)
    if success:
        helper.pinfo("Found RECOVERY_STATUS = AWITING_RECOVERY_IMAGE")

    helper.pinfo("Use Recovery Image from memory window (CMS) ...")
    helper.SMBus_write(OOB.SMCommand.RECOVERY_CTRL, [0x00, 0x01, 0x00])
    helper.pinfo("Used Recovery Image from memory window (CMS)")
    
    helper.pinfo("Polling DEVICE_STATUS = RECOVERY_PENDING ...")
    success = helper.SMBus_poll(0x4, 0xff, OOB.SMCommand.DEVICE_STATUS, 20)
    if success:
        helper.pinfo("Found DEVICE_STATUS = RECOVERY_PENDING")

    helper.pinfo("Polling RECOVERY_STATUS = AWITING_RECOVERY_IMAGE ...")
    success = helper.SMBus_poll(0x1, 0xff, OOB.SMCommand.RECOVERY_STATUS, 20)
    if success:
        helper.pinfo("Found RECOVERY_STATUS = AWITING_RECOVERY_IMAGE")



def fsp_fmc_loading(opts):
    helper.pinfo("Trigger indirect ctrl for image loading ...")
    helper.SMBus_write(OOB.SMCommand.INDIRECT_CTRL, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    helper.pinfo("Trigger indirect ctrl for image loading completed")

    helper.pinfo("Starts loading image ...")
    fmc_bytes = None
    with open(opts.fmc_bin, 'rb') as f:
        fmc_bytes = list(f.read())

    len_indirect_data = 252
    while len(fmc_bytes) > 0:
        if len(fmc_bytes) > len_indirect_data:
            wr_data = fmc_bytes[:len_indirect_data]
            fmc_bytes = fmc_bytes[len_indirect_data:]
        else:
            wr_data = fmc_bytes
            fmc_bytes = []

        helper.pinfo("Sending one image data section ...")
        helper.SMBus_write(OOB.SMCommand.INDIRECT_DATA, wr_data)
        helper.wait_sim_time("us", 100)
        time.sleep(0.1)
        helper.pinfo("Sent one image data section")
        
        helper.pinfo("Waiting for loading acknowledge ...")
        if not helper.SMBus_poll(0x4, 0x4, OOB.SMCommand.INDIRECT_STATUS, 100, False):
            helper.perror("polling INDIRECT_STATUS.ACK = 1 during fmc loading failed")
            return None
        
        helper.pinfo("Found acknowledge. INDIRECT_STATUS ACK = 1")

        helper.pinfo("Clear acknowledge ...")
        helper.SMBus_write(OOB.SMCommand.INDIRECT_STATUS, [0x00])
        helper.pinfo("Acknowledge cleared")
    helper.pinfo("Completes loading image")


def image_activation():
    #read DEVICE_STATUS = RECOVERY_PENDING
    helper.pinfo("polling DEVICE_STATUS = RECOVERY_PENDING ...")
    success = helper.SMBus_poll(0x4, 0xff, OOB.SMCommand.DEVICE_STATUS, 200)
    if success:
        helper.pinfo(f"Found DEVICE_STATUS = RECOVERY_PENDING")

    #write RECOVERY_CTRL, CMS=0x0, RECOVERY_IMAGE_SELECTION=0x1, ACTIVATE_RECOVERY_IMAGE=0xf
    helper.pinfo("Sending image activatition command ...")
    helper.SMBus_write(OOB.SMCommand.RECOVERY_CTRL, [0x00, 0x01, 0x0f])
    helper.pinfo("Sent image activatition command")

    #read RECOVERY_STATUS = BOOTING_RECOVERY_IMG
    helper.pinfo("polling RECOVERY_STATUS = BOOTING_RECOVERY_IMG ...")
    success = helper.SMBus_poll(0x2, 0xff, OOB.SMCommand.RECOVERY_STATUS, 200)
    if success:
        helper.pinfo(f"Found RECOVERY_STATUS = BOOTING_RECOVERY_IMG")


def boot_up_recovery_image():
    #read DEVICE_STATUS = RUNNING_RECOVERY_IMAGE
    helper.pinfo("polling DEVICE_STATUS = RUNNING_RECOVERY_IMAGE ...")
    success = helper.SMBus_poll(0x5, 0xff, OOB.SMCommand.DEVICE_STATUS, 200)
    if success:
        helper.pinfo(f"Found DEVICE_STATUS = RUNNING_RECOVERY_IMAGE")



def trigger_recovery():
    helper.pinfo("wait at least 760 VrefRO cycle(0.02us) + 990us fuse sense for L3 reset tp release ...")
    helper.pinfo("Refer to https://confluence.nvidia.com/display/GROOT/SR01+System+GFD+-+Resets+Clocks")
    helper.wait_sim_time("us", 0.02*760 + 1005)
    helper.pinfo("L3 reset release wait completed")

    helper.pinfo("Sending recovery reset command ...")
    helper.SMBus_write(OOB.SMCommand.RESET, [0x01, 0x0f, 0x00])
    helper.pinfo("Sent recovery reset command")

    helper.pinfo("Reset command will trigger L1 reset, wait reset for one more round")
    helper.pinfo("wait at least 760 VrefRO cycle(0.02us) + 990us fuse sense for L3 reset tp release ...")
    helper.pinfo("Refer to https://confluence.nvidia.com/display/GROOT/SR01+System+GFD+-+Resets+Clocks")
    helper.wait_sim_time("us", 0.02*760 + 1005)
    helper.pinfo("L3 reset release wait completed")

    # wait FSP to finish startup self certification
    helper.pinfo("Wait for boot rom to finish self certification before sending next command")
    helper.wait_sim_time("us", 500)
    time.sleep(5)


def wait_boot_complete():
    cnt = 0
    while True:
        cnt += 1
        nbr_byte, oob_dev_status = helper.erot_rcvy_block_read(slv_addr=BMC_I2C_SLV_ADDR, cmd_code=OOB.SMCommand.DEVICE_STATUS, ret_bytes_nbr=True)
        oob_dev_status = oob_dev_status.to_bytes(nbr_byte, 'little')
        vecdor_status_length = int(oob_dev_status[6])
        if vecdor_status_length > 0:
            if (oob_dev_status[12] & 0x3) == 0x3:
                helper.pinfo("Detect boot success")
                break

        if cnt >= 200:
            helper.perror("Fail to find boot success")
            break


def interacting_with_fmc():
    helper.pinfo("Start interacting with FMC ...")
    gdata = 0xccddeeff
    dmem_end_addr = 0x00200000
    addr = dmem_end_addr - 4

    helper.pinfo(f"Write {hex(gdata)} to {hex(addr)}")
    helper.i2c_proxy_write(3, 0, addr, gdata, addr_space_id=2)
    helper.pinfo(f"Read data from {hex(addr)} to check")
    rdata = helper.i2c_proxy_read(3, 0, addr, addr_space_id=2)
    if rdata != gdata:
        helper.perror(f"Mismatch, exp: {hex(gdata)}, act: {hex(rdata)}")
    else:
        helper.pinfo(f"Match {hex(gdata)}@{hex(addr)}")


def get_testlist(opts):
    if not os.path.exists(opts.testlist):
        raise ValueError(f"{opts.testlist} No such file")
    
    tests = os.listdir(opts.testlist)
    for t in [i.strip() for i in tests if i.strip() != ""]:
        abst = f"{opts.testlist}/{t}"
        if not os.path.exists(abst):
            raise ValueError(f"{abst} No such file")
        Testlist.append(abst)
    

with Test(sys.argv) as t:
    def parse_args():
        t.parser.add_argument("--fmc_bin", type=str, default=None, help="")
        t.parser.add_argument("--testlist",type=str, required=True,help="testlist dir")
        opts, unknown = t.parser.parse_known_args(sys.argv[1:])
        return opts

    opts = parse_args()
    if not os.path.exists(opts.fmc_bin):
        raise Exception(f"{opts.fmc_bin} No such file. Provide fmc file to run.")

    get_testlist(opts)

    helper.hdl_force("ntb_top.gpio26", 0)
    helper.hdl_force("ntb_top.gpio27", 0)
    helper.hdl_force("ntb_top.gpio28", 0)

    trigger_recovery()
    
    helper.pinfo("start default cms selection")
    default_cms_selection()
    helper.pinfo("default cms selection completed")

    helper.pinfo("start fsp fmc")
    fsp_fmc_loading(opts)
    helper.pinfo("fsp fmc completed")

    # wait manifest
    time.sleep(5)

    helper.pinfo("start image activation")
    image_activation()
    helper.pinfo("image activation completed")

    helper.pinfo("start boot up recovery image")
    boot_up_recovery_image()
    helper.pinfo("boot up recovery image completed")
    
    # give time for fsp to run to main()
    helper.wait_sim_time("us", 1500)
    wait_boot_complete()
    time.sleep(5)

    interacting_with_fmc()



for t in Testlist:
    helper.pinfo(f"Running Test: {t}")
    spec = importlib.util.spec_from_file_location("module.name", t)
    py = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(py)
    helper.pinfo(f"Test finished: {t}")


helper.pinfo("Regression Completed")
