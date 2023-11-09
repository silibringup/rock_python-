#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import *
import json

with Test(sys.argv) as t:
    
    # wp = (~fuse_program_en) | opt_disable_nonfpf_fuse_programming

    def parse_args():
        t.parser.add_argument('--hash', default='', help='path of FUSE info in json format')
        return t.parser.parse_args(sys.argv[1:])

    def burn_fuse_check(fuse_en, addr, wdata, is_ctrl, reg):
        test_api.fuse_burn(fuse_en, addr, wdata)
        test_api.fuse_resense(is_ctrl)
        exp = fuse_en & 0x1
        test_api.fuse_check_reg_log(reg, 'DATA', exp)

    
    test_api.fuse_init_sense()
    helper.pinfo("ROUND 0: NOTHING LOADED AND CHECK INITIAL STATE")    
    reg_en = erot.FUSE.ENABLE_FUSE_PROGRAM_STATUS_0
    test_api.fuse_check_reg_log(reg_en, 'DATA', 0)

    helper.pinfo("ROUND 1: TO BURN ENABLE_FUSE_PROGRAM - EXPECTING SUCCESS")
    row_addr0 = 0x0
    burn_fuse_check(1, row_addr0, 0x1, 1, reg_en)


