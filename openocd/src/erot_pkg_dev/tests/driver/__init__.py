import os
import re
import sys
import argparse
import subprocess
import time
import RoPy
import glob
import driver.helpers.helper as hp
import driver.apis.TestAPIs as apis
from driver.helpers.regobj import *
from driver.helpers.rock_thread import *
from driver.helpers.PrgnRiscV import FSP, OOB
import importlib


class HeartBeat(rock_thread):
    def __init__(self,interval):
        rock_thread.__init__(self, 'HeartBeat')
        self.interval = interval

    def run(self):
        while(1):
            time.sleep(self.interval)   
            hp.Helper().log("!!! Rock PY is with You !!!")
            

def LOG(s):
    hp.Helper().log(s)

DRV_DIR  = os.path.dirname(os.path.realpath(__file__))
BINFILE = '%s/../ucode/build/run.bin' % DRV_DIR


helper = hp.Helper()
test_api = apis.TestAPIs()


def px(f):
    import importlib

    if not os.path.exists(f):
        raise ValueError(f"{f} No such file or directory")
    spec = importlib.util.spec_from_file_location("module.name", f)
    p = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(p)
    

class Test:
    def __init__(self,argv):
        self.argv = argv
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("--platform", action='store', help="SIM_HEAD,SIM_HEADLESS,JTAG,HEAD", default='SIM_HEADLESS')
        self.parser.add_argument("--port",     action='store', help="socket Port", default = "1234")
        self.parser.add_argument("--ip",       action='store', help="socket ip", default = "127.0.0.1")
        self.parser.add_argument("--ucode",    type=str, default=None, help="HEAD mode binary path")
        self.parser.add_argument("--target",   type=str, default="simv_top", help="simv_top, simv_fpga,fpga")
        self.parser.add_argument("--memory_model",   type=str, default="SIM", help="memory_model used in test, can be: SIM or SYN")
        self.parser.add_argument("--heartbeat",   type=int, default=0, help="heartbeat of simv and python")
        self.parser.add_argument("--prex","-px",  type=str, default="", help="pre run")
        self.parser.add_argument("--activate_error", type=str, default="", help="error id to activate, erra errb errc ...")
        self.parser.add_argument("--disable_peripheral_init_agent", action="store_true", default=False, help="disable auto peripheral initialization agency at the beginning of test")
        self.parser.add_argument("--rcv_boot", action="store_true", default=False, help="run recovery boot before normal test and load genric proxy ucode")
        self.parser.add_argument("--fmc_bin",    type=str, default=None, help="JTAG mode recovery proxy image")
        self.parser.add_argument('--seed', default=1)
        self.parser.add_argument('--loadimem_frontdoor',action="store_true", default=False)
        self.parser.add_argument('--debug_hdl',action="store_true", default=False)
        self.parser.add_argument("--replace_brom", type=str, default=None, help="Released Boot Rom directory path pointer. Provide it to change Boot Rom version. e.g., /home/ip/nvmsoc/uproc/peregrine_fsp/3.7/<???>/ip/peregrine/3.0/defs/public/rv_brom/spark/obj/xchip_fsp/hex")
        self.parser.add_argument('--eos',type=str, default=None)
        self.options, unknown = self.parser.parse_known_args(argv[1:])

        global helper
        global test_api
        
        helper.init(link=RoPy.PystLink(host=self.options.ip, port=self.options.port), platform=self.options.platform, target=self.options.target, memory_model=self.options.memory_model, regblk_top=erot)
        helper.pdebug(f"PLATFORM = {helper.platform}")
        helper.pdebug(f"TARGET = {helper.target}")
        helper.debug_hdl = self.options.debug_hdl
        if helper.target in ["simv_gate","simv_synth"]:
            self.options.loadimem_frontdoor = True
        
        helper.loadimem_frontdoor = self.options.loadimem_frontdoor

        self.disable_peripheral_init_agent = self.options.disable_peripheral_init_agent

        if self.options.platform == 'JTAG':
            self.disable_peripheral_init_agent = 1

        if self.options.platform not in ["SIM_HEAD", "SIM_HEADLESS", "JTAG", "HEAD"]:
            s = f"Wrong platform argument: {self.options.platform}"
            helper.perror(s)
            raise ValueError(s)
        
        self.activate_error = [i for i in self.options.activate_error.split(' ') if i.strip()]
        if self.activate_error:
            helper.pinfo(f"Intend to activate: {' '.join(self.activate_error)}")
        
        if self.options.prex:
            px(self.options.prex)
        
        if self.options.heartbeat:
            heartbeat_thread = HeartBeat(self.options.heartbeat)
            heartbeat_thread.daemon = True
            heartbeat_thread.start()
        
        if self.options.replace_brom is not None:
            if not os.path.exists(self.options.replace_brom):
                helper.pfatal(f"{self.options.replace_brom} No such file or directory")
            helper.replace_brom = self.options.replace_brom
            helper.pinfo(f"Replacing Boot Rom content based on {self.options.replace_brom} ...")
            helper.backdoor_init_bootrom(self.options.replace_brom)
            helper.pinfo(f"Replacing Boot Rom content completes")

        test_api.init(helper=helper)
        helper.pinfo("RockPY Initilized")

    def __enter__(self):
        global helper
        global test_api
        global BINFILE
        helper.log("Test starts ...")
        if helper.target == 'simv_fpga':
            helper.hdl_force('ntb_top.u_nv_fpga_dut.u_nv_top_fpga.u_nv_top_wrapper.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.u_fusegen_logic.u_decomp.state',0) # bug 4191399 
        if helper.platform in {'SIM_HEAD', "HEAD" } and helper.target != 'fpga':
            if not self.options.loadimem_frontdoor:
                helper.fsp_dis_clob()
        test_api.power_on_seq()
        if helper.platform in {'SIM_HEAD', "HEAD" } and helper.target != 'fpga':
            with open(BINFILE, 'rb') as f:
                txtsize = int.from_bytes(f.read(8), 'little')
                datsize = int.from_bytes(f.read(8), 'little')
            if not self.options.ucode:
                self.options.ucode = BINFILE
            elif not os.path.exists(self.options.ucode):
                RoPy.rperror(f"{self.options.ucode} No such a file or directory")
            helper.pdebug(f"start to boot fsp")
            helper.fsp_boot_init(bin_path=self.options.ucode, i_file_start_offset=0x200, i_mem_start_offset=0x200, i_load_size=0x6000+datsize,
                d_file_start_offset=0x8000, d_load_size=0)
            helper.pdebug(f"end to boot fsp in %s mode" % helper.platform)
        if not self.disable_peripheral_init_agent:
            test_api.test_init()
        if 'fpga' in helper.target:
            if self.options.fmc_bin:
                test_api.fmc_bin = self.options.fmc_bin
            elif helper.target == 'simv_fpga':
                test_api.fmc_bin = '%s/../ucode/build/mashUpBin.bin' % DRV_DIR
            elif helper.target == 'fpga':
                test_api.fmc_bin = os.path.join(os.path.dirname(os.path.realpath(__file__)),'../recovery_test','mashUpBin.bin')
            if self.options.rcv_boot:
                test_api.rcv_load_image(test_api.fmc_bin,0x69)
        return self

    def eos_check(self):
        pattern = self.options.eos
        helper.pinfo(f"Start End of Simulation Check : <{pattern}>")
        if pattern:
            eos_files = glob.glob(f'{DRV_DIR}/../eos/*.check')
            for eos_file in eos_files:
                if re.search(pattern,eos_file): 
                    helper.pinfo(f"Activate {eos_file} end of sim checking")               
                    with open(eos_file,'r') as f:
                        for line in f:
                            (signal,exp_value)=line.rstrip().split('=')
                            act_value = str(helper.hdl_read(signal))
                            if act_value != exp_value:
                                helper.perror(f'EOS CHECKER ERROR : Signal {signal}, expected {exp_value}, actual {act_value}')
                            else:
                                helper.pinfo(f'EOS CHECKER INFO(MATCHED) : Signal {signal}, expected {exp_value}, actual {act_value}')


    def __exit__(self,exc_type,exc_val,exc_tb):
        self.eos_check()

        helper.done()
        print("Test finished")

    def add_stuckat_error(self, err_id, hdl, value):
        if err_id in self.activate_error:
            global helper
            helper.pinfo(f"[StuckAtErrorInjection]({err_id}) {hdl}={value}")
            helper.hdl_force(hdl, value)


class ErrorInject:
    def __init__(self, _helper=None):
        global helper
        self.helper = _helper or helper
        
    def __enter__(self):
        RoPy.rpinfo("Error inject started")
        return self

    def tieHDL(self, path, value):
        self.helper.hdl_force(path, value)

    def __exit__(self,exc_type,exc_val,exc_tb):
        self.helper.pinfo("Error inject completed")



# class Test:
#     def __init__(self, argv):
#         self.argv = argv
#         self.parser = argparse.ArgumentParser()
#         self.parser.add_argument("--platform", action='store', help="SIM_HEAD,SIM_HEADLESS,FPGA_HEAD,FPGA_HEADLESS", default='SIM_HEADLESS')
#         self.parser.add_argument("--port",     action='store', help="socket Port", default = "1234")
#         self.parser.add_argument("--ip",       action='store', help="socket ip", default = "127.0.0.1")
#         self.options, unknown = self.parser.parse_known_args(argv[1:])
#         self.helper = hp.Helper()
        
#     def __enter__(self):
#         self.helper.log("Test starts ...")
#         return self

#     def __exit__(self,exc_type,exc_val,exc_tb):
#         self.helper.done()
#         self.helper.log("Test finished")



# def build_erot_reg_block(platform, link):
#     reg_spec = 'reg_spec'
#     if "SIM" in platform:
#         sys.path.append(os.environ['NVBUILD_PY_LIB'])
#         import nvbuildutils
#         nvbuild = nvbuildutils.NVBuild()
#         reg_spec = os.path.join(nvbuild.get_output_variant_dir('erot_verif/stand_sim/top/simv_top'), reg_spec)
#     else:
#         reg_spec = f"{os.path.dirname(os.path.realpath(__file__))}/{reg_spec}"

#     if not os.path.exists(reg_spec):
#         raise ValueError(f"{reg_spec} No such file or directory")

#     blks = []
#     for i in os.listdir(reg_spec):
#         m = re.search("^(.+)-([0-9]+).json", i)
#         blknm = m.group(1)
#         base = int(m.group(2))
#         k = RoPy.RPRegisterBlock(regjson=f"{reg_spec}/{i}", link=link, blknm=blknm, base=base)
#         blks.append(k)
#     return blks



# def start_init():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--platform", action='store', help="SIM_HEAD,SIM_HEADLESS,FPGA_HEAD,FPGA_HEADLESS", default='SIM_HEADLESS')
#     parser.add_argument("--port",     action='store', help="socket Port", default = "1234")
#     parser.add_argument("--ip",       action='store', help="socket ip", default = "127.0.0.1")
#     args, unknown = parser.parse_known_args()
#     link = RoPy.PystLink(host=args.ip, port=args.port)
#     _helper = hp.Helper()
#     _helper.init(link=link, platform=args.platform, log=RoPy.rpinfo, error=RoPy.rperror, warning=RoPy.rpwarning)

#     blks = build_erot_reg_block(args.platform, link)
#     global erot
#     for i in blks:
#         setattr(erot, i.name, i)


# start_init()




from binascii import unhexlify
def long_to_bytes(val, endianness='big'):
    width = val.bit_length()
    width += 8 - ((width%8) or 8)
    fmt = '%%0%dx' % (width//4)
    s = unhexlify('00') if fmt % val == '0' else unhexlify(fmt % val)
    if endianness == 'little':
        s = s[::-1]
    return s
