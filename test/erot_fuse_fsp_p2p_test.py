#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import *

'''    
16x16b encoded fuse opt_fpf_fsp_ucode{1~16}_version -(translated in Fuse) -> 16x8b encoded val at Fuse Tx -(transmitted via p2p) -> 16 FSP Prgrn Rx reg *FALCON_UCODE_VERSION(0..15) field _VER[7:0]
'''

with Test(sys.argv) as t:

    def parse_args():
        t.parser.add_argument('--config', default='', help='path of config file of raw ucode version (16b * 16b) to be preloaded into fuse macros')
        return t.parser.parse_args(sys.argv[1:])    

    def check_state():  # The _HWVER_VALID bit of *FALCON_KFUSE_LOAD_CTRL reg will be set when transaction done
        reg_status = erot.FSP.FALCON_KFUSE_LOAD_CTL_0
        helper.pinfo("START TO POLL REG [%s] HWVER_VALID == TRUE ..." % reg_status.name)
        reg_status.poll(HWVER_VALID=1) # TRUE
        helper.pinfo("UCODE VERSION TRANSMISSION DONE !")

    def check_uc_ver(exp_list):
        for idx in range(16):
            reg_path = eval(f'erot.FSP.FALCON_UCODE_VERSION_{idx}')
            rd = reg_path.read()
            act, exp = rd['VER'], exp_list[idx]    # 8 bit decimal each
            if act != exp:
                helper.perror("UCODE VERSION INDEX [%d] CHECK FAIL: ACT = [%d]; EXP = [%d]" % (idx, act, exp))
            else:
                helper.pinfo("UCODE VERSION INDEX [%d] CHECK PASS: VAL = [%d]" % (idx, act))

    def get_exp():
        ver_list = []
        options = parse_args()
        fuse_config_path = options.config
        with open(fuse_config_path) as f:
            for line in f.readlines():
                line_cfg = line.strip()
                l = re.match(r'opt_fpf_fsp_ucode(\d+)_version\s+0x(\w+)', line_cfg)
                if l is None:
                    helper.perror("UCODE FUSE NOT FOUND IN CONFIG FILE !")
                else:
                    idx, ver = int(l.group(1)), int(l.group(2), 16)
                    helper.pinfo("[DEBUG] GETTING RAW DATA FROM FUSE: INDEX = [%d], VERSION = [0x%x]" % (idx, ver))
                    ver_list.append(trans_fuse(ver))
        helper.pinfo("LIST OF UCODE VERSION TRANSLATED: \n%r" % ver_list)
        return ver_list

    def trans_fuse(raw_16): # detect msb
        for ver_8 in range(16, -1, -1): # versions range from 0 to 16, both included
            if (2**ver_8) & raw_16:
                return ver_8 + 1
                break
        return 0


    check_state()
    exp_list = get_exp()
    check_uc_ver(exp_list)

