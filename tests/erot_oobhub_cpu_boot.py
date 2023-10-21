#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3

from driver import *
import random

# nvrun run_test -rtlarg '+disable_falcon_mem_wakeup_scrubbing' --platform SIM_HEAD -py erot_oobhub_cpu_boot.py

def boot_oobhub(gdata):
    # PEREGRINE_RISCV_BCR_CTRL._VALID = _TRUE, _CORE_SELECT = _RISCV
    erot.OOBHUB.PEREGRINE_RISCV_BCR_CTRL_0.write(0x00000011)
    # PEREGRINE_RISCV_BOOT_VECTOR_LO._VECTOR = IMEM_START
    erot.OOBHUB.PEREGRINE_RISCV_BOOT_VECTOR_LO_0.write(0x00100000)
    # PEREGRINE_RISCV_BOOT_VECTOR_HI._VECTOR = 0
    erot.OOBHUB.PEREGRINE_RISCV_BOOT_VECTOR_HI_0.write(0x00000000)
    # PEREGRINE_FALCON_IMEMC(0)._AINCW = _TRUE
    erot.OOBHUB.PEREGRINE_FALCON_IMEMC_0.write(0x01000000)
    # PEREGRINE_FALCON_IMEMD(0)._DATA: write a data to PRGNLCL_FALCON_MAILBOX0
    inst = [0x01400637, 0x0406061b, (gdata<<20) | 0x00000693, 0x00d62023]
    for i in inst:
        erot.OOBHUB.PEREGRINE_FALCON_IMEMD_0.write(i)
    # PEREGRINE_RISCV_CPUCTL._STARTCPU = _TRUE
    erot.OOBHUB.PEREGRINE_RISCV_CPUCTL_0.write(0x00000001)

with Test(sys.argv) as t:
    # Bug 4071704, should remove after fix
    #helper.hdl_force("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.opt_fsp_ecc_en", 1)

    with open("oob_imem_scrub.bin", "wb") as f:
        f.write(b'\x00'*16*8192)
    helper.oob_boot_init("oob_imem_scrub.bin")
    
    gdata = random.randint(0, 0x7ff)
    boot_oobhub(gdata)
    helper.pinfo(f"Wrote {hex(gdata)} to mailbox")
    erot.OOBHUB.PEREGRINE_FALCON_MAILBOX0_0.poll(DATA=gdata, timeout=100)

