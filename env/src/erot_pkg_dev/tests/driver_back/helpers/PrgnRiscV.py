import re
import enum
import numpy as np
import os
from RoPy import rpinfo

class PrgnRiscV:
    ACTIVATE_XREG = 12
    RW_XREG       = 13 # 0 Write; 1 Read
    WDATA_XREG    = 14
    ADDR_XREG_LO  = 15
    ADDR_XREG_HI  = 16
    PLVL_XREG     = 17
    RDATA_XREG    = 18
    GOMAIN_XREG   = 19

    class MemType(enum.IntEnum):
        IMEM = 0
        DMEM = 1
        BMEM = 2

    def __init__(self, hdl_proxy=None, hdl_root=None,
                 imem_pa_start=None, imem_size=None,
                 dmem_pa_start=None, dmem_size=None,
                 memory_model="SIM"):
        super(PrgnRiscV, self).__init__()
        self.__hdl_proxy = hdl_proxy
        self.hdl_root = hdl_root
        self.imem_hdl_top = hdl_root
        self.dmem_hdl_top = hdl_root
        self.memory_model = memory_model
        self.imem_pa_start = imem_pa_start
        self.imem_size = imem_size
        self.imem_pa_end = self.imem_pa_start + self.imem_size
        self.dmem_pa_start = dmem_pa_start
        self.dmem_size = dmem_size
        self.dmem_pa_end = self.dmem_pa_start + self.dmem_size
        self.mem_data = {}

    def set_hdl_proxy(self, hdl_proxy,helper):
        self.__hdl_proxy = hdl_proxy
        self.helper = helper

    def batch_deposit(self,_list,filename):
        with open(filename,'w') as f:
            f.write('\n'.join([f"{hdl_path}={int.from_bytes(b, 'little')}".strip() for (hdl_path,b) in _list]))
        abs_file = os.path.abspath(filename)
        rpinfo(f"Peregrine Deposit {filename}")
        self.__hdl_proxy.BatchDepositVerilogPath(abs_file)

    def fill_imem_by_force_ports(self,txt,mem_start_offset):
        self.helper.log("Loading IMEM from Forcing Port of IMEM")
        im_rst = f'{self.hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_imem.imem_wrap.u_imem.reset_'
        im_a   = f'{self.hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_imem.imem_wrap.u_imem.im_a'
        im_di  = f'{self.hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_imem.imem_wrap.u_imem.im_di'
        im_re  = f'{self.hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_imem.imem_wrap.u_imem.im_re'
        im_we  = f'{self.hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_imem.imem_wrap.u_imem.im_we'
        im_clk = f'{self.hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_imem.imem_wrap.u_imem.msd_clk'
        self.helper.wait_sim_time("ns", 300)
        #self.helper.hdl_force(im_rst,0)
        self.helper.hdl_wait(im_clk,0)
        self.helper.hdl_wait(im_clk,1)
        for i in range(0,len(txt),16):
            addr = i + mem_start_offset
            end = 16 if i + 15 <= len(txt) else len(txt) - i
            bin = [ int(item) for item in txt[i:i+end]]
            bin_str = int.from_bytes(bin, byteorder='little')            
            if bin_str != 0 :
                self.helper.hdl_wait(im_clk,0)
                self.helper.hdl_force(im_di,bin)
                self.helper.hdl_force(im_a,addr >> 4)
                self.helper.hdl_force(im_re,0)
                self.helper.hdl_force(im_we,0xffff)
                self.helper.hdl_wait(im_clk,1)
                #self.helper.log(f"{hex(addr)} ->  {hex(bin_str)}")      
        self.helper.hdl_wait(im_clk,0)
        self.helper.hdl_wait(im_clk,1)
        self.helper.hdl_release(im_di)          
        self.helper.hdl_release(im_a)
        self.helper.hdl_release(im_re)
        self.helper.hdl_release(im_we)
        #self.helper.hdl_release(im_rst)

    def preload_imem(self, bin_path, file_start_offset=0, load_size=-1, mem_start_offset=0, has_parity=True):
        if load_size == 0:
            raise Exception(f"size cannot be 0")
        deposit_list = []
        with open(bin_path, 'rb') as f:
            txt = f.read()
            if file_start_offset > len(txt) - 1:
                raise Exception(f"{file_start_offset} exceeds {bin_path} size {len(txt)}")
            txt = txt[file_start_offset:]
            if load_size > 0:
                txt = txt[:min(load_size, len(txt))]
            if not self.helper.loadimem_frontdoor:
                for i in range(len(txt)):
                    addr = i + self.imem_pa_start + mem_start_offset
                    deposit_list.append(self.deposit_mem_byte(addr, txt[i], has_parity))
            else:
                self.fill_imem_by_force_ports(txt,mem_start_offset)
        if not self.helper.loadimem_frontdoor:
            self.batch_deposit(deposit_list, f'{self.hdl_root}.imem.dep')

    def preload_dmem(self, bin_path, file_start_offset=0, load_size=-1, mem_start_offset=0):
        if load_size == 0:
            raise Exception(f"size cannot be 0")
        deposit_list = []
        with open(bin_path, 'rb') as f:
            txt = f.read()
            if file_start_offset > len(txt) - 1:
                raise Exception(f"{file_start_offset} exceeds {bin_path} size {len(txt)}")
            txt = txt[file_start_offset:]
            if load_size > 0:
                txt = txt[:min(load_size, len(txt))]
            for i in range(len(txt)):
                addr = i + self.dmem_pa_start + mem_start_offset
                deposit_list.append(self.deposit_mem_byte(addr, txt[i], has_parity))
        self.batch_deposit(deposit_list, f'{self.hdl_root}.dmem.dep')

    def deposit_mem_byte(self, physical_addr, byte, has_parity=True):
        mem_type, mem_inst, mem_entry, entry_byte_offset = self.check_address(physical_addr)
        hdl = self.form_mem_hdl_path(mem_type, mem_inst, mem_entry, entry_byte_offset)
        hdl = self.helper.hdl_translate(hdl)
        mifp = re.search("(.+\.M)\[.+:.+\]$", hdl)
        if mifp and mifp not in self.mem_data:
            mifp = mifp.group(1)
            self.mem_data[mifp] = []

        if has_parity:
            parity =  self.byte_parity(byte)
            if mifp:
                self.mem_data[mifp].append(f"{((parity<<8) | byte):09b}")
            #print(f"{hdl} {parity}, {hex(byte)}")
            #self.__hdl_proxy.DepositVerilogPath(hdl, [byte, parity])
            return (hdl,[byte, parity])
        else:
            if mifp:
                self.mem_data[mifp].append(f"{(byte):08b}")
            #print(f"{hdl} {parity}, {hex(byte)}")
            #self.__hdl_proxy.DepositVerilogPath(hdl, [byte])
            return (hdl,[byte])


    def byte_parity(self, byte):
        ans = 1 if np.uint(np.bitwise_xor.reduce(np.array([int(i) for i in f"{byte:b}"]))) else 0
        return 0 if ans else 1

    def write_xreg(self, index, value):
        raise ValueError("Should use subclass to implement")
    
    def read_xreg(self, index, value):
        raise ValueError("Should use subclass to implement")

    def wait_xreg(self, index, value):
        raise ValueError("Should use subclass to implement")

    def write(self,addr,value,priv_level,secure):
        self.write_xreg(PrgnRiscV.ADDR_XREG_LO, addr & 0xffffffff)
        self.write_xreg(PrgnRiscV.ADDR_XREG_HI, addr >> 32)
        self.write_xreg(PrgnRiscV.WDATA_XREG,value)
        self.write_xreg(PrgnRiscV.RW_XREG,0)
        self.write_xreg(PrgnRiscV.PLVL_XREG,(priv_level<<6)+(secure<<11))
        self.write_xreg(PrgnRiscV.ACTIVATE_XREG,1)

        self.wait_xreg(PrgnRiscV.ACTIVATE_XREG,0)
        #while 1:
        #    rd = self.read_xreg(PrgnRiscV.ACTIVATE_XREG)
        #    self.__hdl_proxy.WaitSimTime("ns", 10)
        #    if int(rd) == 0:
         #       break

    def read(self,addr,priv_level,secure):
        self.write_xreg(PrgnRiscV.ADDR_XREG_LO, addr & 0xffffffff)
        self.write_xreg(PrgnRiscV.ADDR_XREG_HI, addr >> 32)
        self.write_xreg(PrgnRiscV.RW_XREG,1)
        self.write_xreg(PrgnRiscV.PLVL_XREG,(priv_level<<6)+(secure<<11))
        self.write_xreg(PrgnRiscV.ACTIVATE_XREG,1)
        
        self.wait_xreg(PrgnRiscV.ACTIVATE_XREG,0)
        #while 1:
        #    rd = self.read_xreg(PrgnRiscV.ACTIVATE_XREG)
        #    self.__hdl_proxy.WaitSimTime("ns", 10)
        #    if int(rd) == 0:
        #        break
        return self.read_xreg(PrgnRiscV.RDATA_XREG)




class FSP(PrgnRiscV):
    GLOBAL_IO_ADDR_SPACE_OFFSET = 0x2000000000000000
    LOCAL_IO_ADDR_SPACE_OFFSET = 0x1400000
    LOCAL_MEM_ADDR_SPACE_OFFSET = 0x0

    def __init__(self, hdl_proxy=None, hdl_root=None,
                 imem_pa_start=0x0100000, imem_size=0x8000,
                 dmem_pa_start=0x0180000, dmem_size=0x8000,
                 memory_model="SIM"):
        super(FSP, self).__init__(hdl_proxy, hdl_root, imem_pa_start, imem_size, dmem_pa_start, dmem_size, memory_model)
        self.__hdl_proxy = hdl_proxy
        self.__IMEM_DATA_WIDTH = 9
        self.__DMEM_DATA_WIDTH = 9
        self.imem_hdl_top = f"{hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_imem.imem_wrap.u_imem"
        self.dmem_hdl_top = f"{hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_dmem.dmem_wrap.u_dmem"

    def form_mem_hdl_path(self, mem_type, mem_inst, mem_entry, entry_byte_offset):
        hdl = ""
        if mem_type == PrgnRiscV.MemType.IMEM:
            hdl = f"{self.imem_hdl_top}.u_SCANBYPASS_imem_ram_{mem_inst}.s_nv_ram_parity_errProt"
            mem_data_width = self.__IMEM_DATA_WIDTH
        elif mem_type == PrgnRiscV.MemType.DMEM:
            hdl = f"{self.dmem_hdl_top}.u_SCANBYPASS_dmem_ram_{mem_inst}.s_nv_ram_parity_errProt"
            mem_data_width = self.__DMEM_DATA_WIDTH
        else:
            raise Exception(f"{mem_type.name} is not recognized")

        lsb = entry_byte_offset * mem_data_width
        msb = lsb + mem_data_width - 1
        if self.memory_model == "SIM":
            hdl = f"{hdl}.M[{mem_entry}][{msb}:{lsb}]"
        elif self.memory_model == "SYN":
            hdl = f"{hdl}.r_nv_ram_bspjn_e9_m4_8192x144.{self.syn_ram_hdl_addr_translate(mem_entry, msb, lsb)}"
        return hdl

    def syn_ram_hdl_addr_translate(self, mem_entry, msb, lsb):
        if      0 <= mem_entry <= 2047:
            ram_inst = "ram_Inst_2048X72_0_"
        elif 2048 <= mem_entry <= 4095:
            ram_inst = "ram_Inst_2048X72_2048_"
        elif 4096 <= mem_entry <= 6143:
            ram_inst = "ram_Inst_2048X72_4096_"
        else:
            ram_inst = "ram_Inst_2048X72_6144_"

        mem_piece = f"iow{ (mem_entry % 2048) // 512 }"
        if msb <= 71:
            ram_inst += f"0.ITOP.{mem_piece}.arr[{mem_entry % 512}]"
        else:
            ram_inst += f"72.ITOP.{mem_piece}.arr[{mem_entry % 512}]"
        
        hdl = f"{ram_inst}[{msb%72}:{lsb%72}]"
        return hdl

    def boot_from_imem(self, target):
        self.helper.hdl_force(f"{self.hdl_root}.fuse2fsp_debug_mode",1)
        self.helper.hdl_force(f"{self.hdl_root}.opt_fsp_riscv_debug_en",0)
        self.helper.hdl_force(f"{self.hdl_root}.u_peregrine.falcon.u_riscv.u_RISCV_dcls_core.u_main.UJ_dev_mode",1)
        self.helper.hdl_force(f"{self.hdl_root}.u_peregrine.falcon.u_riscv.u_RISCV_dcls_core.u_main.u_RISCV_rob.csr_rob_boot_vec_gen_nnx" , 0x00100200)
        if target != "simv_fpga":
            self.helper.hdl_force(f"{self.hdl_root}.u_peregrine.falcon.u_riscv.u_RISCV_dcls_core.u_dupl.UJ_dev_mode",1)
            self.helper.hdl_force(f"{self.hdl_root}.u_peregrine.falcon.u_riscv.u_RISCV_dcls_core.u_dupl.u_RISCV_rob.csr_rob_boot_vec_gen_nnx" , 0x00100200)
        self.helper.hdl_force(f"{self.hdl_root}.u_peregrine.falcon.u_riscv.riscv_bcr_ctrl_core_select", 0x1)
        self.helper.hdl_force(f"{self.hdl_root}.u_peregrine.falcon.u_riscv.riscv_boot_after_reset_en", 1)

    def check_address(self, physical_addr):
        if not (self.imem_pa_start <= physical_addr <= self.imem_pa_end) and \
           not (self.dmem_pa_start <= physical_addr <= self.dmem_pa_end):
            raise Exception(f"0x{physical_addr:x} is outside of legal range")

        if self.imem_pa_start <= physical_addr <= self.imem_pa_end:
            mem_type = PrgnRiscV.MemType.IMEM
            mem_addr = physical_addr - self.imem_pa_start
        elif self.dmem_pa_start <= physical_addr <= self.dmem_pa_end:
            mem_type = PrgnRiscV.MemType.DMEM
            mem_addr = physical_addr - self.dmem_pa_start

        addr_bin = f"{mem_addr:032b}"
        entry_byte_offset = int(addr_bin[28:32], 2)
        mem_inst = int(addr_bin[26:28], 2)
        mem_entry = int(addr_bin[0:26], 2)

        return mem_type, mem_inst, mem_entry, entry_byte_offset

    def decode_index(self, index):
        if index == PrgnRiscV.ACTIVATE_XREG:
            return "0_0"
        elif index == PrgnRiscV.RW_XREG:
            return "0_1"
        elif index == PrgnRiscV.WDATA_XREG:
            return "0_2"
        elif index == PrgnRiscV.ADDR_XREG_LO:
            return "0_3"
        elif index == PrgnRiscV.ADDR_XREG_HI:
            return "1_0"
        elif index == PrgnRiscV.RDATA_XREG:
            return "1_1"
        elif index == PrgnRiscV.PLVL_XREG:
            return "1_2"
        elif index == PrgnRiscV.GOMAIN_XREG:
            return "1_3"
        else:
            raise ValueError(f"index {index} is unknown")

    def write_xreg(self,index,value):
        idx = self.decode_index(index)
        hdl_path = f'{self.hdl_root}.u_peregrine.falcon.cfgregs.falcon_common_scratch_group_{idx}_val'
        if self.helper.target in ["simv_gate"]:     
            clk = 'ntb_top.u_nv_top.u_sra_sys0.fsp_clk'
            self.helper.hdl_wait(clk,0)
            for i in range(0,32):         
                #self.helper.hdl_deposit(f'{hdl_path}_reg_{i}_.vudpi0.q',( value & ( 1 << i ) ) >> i )
                self.helper.hdl_force(f'{hdl_path}_reg_{i}_.D',( value & ( 1 << i ) ) >> i )
            self.helper.hdl_wait(clk,1)
            self.helper.hdl_wait(clk,0)
            for i in range(0,32):
                self.helper.hdl_release(f'{hdl_path}_reg_{i}_.D')
        else:
            self.helper.hdl_deposit(hdl_path,list(int(value).to_bytes(8, 'little')))

    def wait_xreg(self,index,value):
        idx = self.decode_index(index)
        hdl_path = f'{self.hdl_root}.u_peregrine.falcon.cfgregs.falcon_common_scratch_group_{idx}_val'
        self.helper.hdl_wait(hdl_path,list(int(value).to_bytes(8, 'little')))


    def read_xreg(self,index):
        idx = self.decode_index(index)
        hdl_path = f'{self.hdl_root}.u_peregrine.falcon.cfgregs.falcon_common_scratch_group_{idx}_val'
        return self.helper.hdl_read(hdl_path)

    #### Peregrine Global IO access APIs, like IPs (fuse/sysctrl...) under L1/L2 fabric

    def write_gio(self,addr,value,priv_level=0x3,secure=0x1):
        addr = int(addr) + FSP.GLOBAL_IO_ADDR_SPACE_OFFSET
        self.write(addr,value,priv_level,secure)

    def read_gio(self,addr,priv_level=0x3,secure=0x1):
        addr = int(addr) + FSP.GLOBAL_IO_ADDR_SPACE_OFFSET
        return self.read(addr,priv_level,secure)

    #### Peregrine Local IO access APIs, like IPs (riscv/gdma...) under CSB bus

    def write_lio(self,addr,value,priv_level=0x3,secure=0x1):
        addr = int(addr) + FSP.LOCAL_IO_ADDR_SPACE_OFFSET
        self.write(addr,value,priv_level,secure)


    def read_lio(self,addr,priv_level=0x3,secure=0x1):
        addr = int(addr) + FSP.LOCAL_IO_ADDR_SPACE_OFFSET
        return self.read(addr,priv_level,secure)

    #### Peregrine Local mem access APIs, like dmem, imem, emem, etc..
    def write_lmem(self,addr,value,priv_level=0x3,secure=0x1):
        addr = int(addr) + FSP.LOCAL_MEM_ADDR_SPACE_OFFSET
        self.write(addr,value,priv_level,secure)

    def read_lmem(self,addr,priv_level=0x3,secure=0x1):
        addr = int(addr) + FSP.LOCAL_MEM_ADDR_SPACE_OFFSET
        return self.read(addr,priv_level,secure)


class OOB(PrgnRiscV):

    class SMCommand(enum.IntEnum):
        PROT_CAP = 34
        DEVICE_ID = 35
        DEVICE_STATUS = 36
        RESET = 37
        RECOVERY_CTRL = 38
        RECOVERY_STATUS = 39
        HW_STATUS = 40
        INDIRECT_CTRL = 41
        INDIRECT_STATUS = 42
        INDIRECT_DATA = 43
        VENDOR = 44

    def __init__(self, hdl_proxy=None, hdl_root=None,
                 imem_pa_start=0x0100000, imem_size=0x20000,
                 dmem_pa_start=0x0180000, dmem_size=0x20000,
                 memory_model="SIM"):
        super(OOB, self).__init__(hdl_proxy, hdl_root, imem_pa_start, imem_size, dmem_pa_start, dmem_size, memory_model)
        self.__hdl_proxy = hdl_proxy
        self.__IMEM_DATA_WIDTH = 8
        self.__DMEM_DATA_WIDTH = 8
        self.imem_hdl_top = f"{hdl_root}.u_peregrine_wrap.u_NV_OOB_falcon.l1tcm_wrap.l1tcm.u_imem.imem_wrap.u_imem" #.u_imem_ram_sim_0.u_ram
        self.dmem_hdl_top = f"{hdl_root}.u_peregrine_wrap.u_NV_OOB_falcon.l1tcm_wrap.l1tcm.u_dmem.dmem_wrap.u_dmem"

    def form_mem_hdl_path(self, mem_type, mem_inst, mem_entry, entry_byte_offset):
        hdl = ""
        if mem_type == PrgnRiscV.MemType.IMEM:
            hdl = f"{self.imem_hdl_top}.u_imem_ram_{mem_inst}.u_ram.M"
            mem_data_width = self.__IMEM_DATA_WIDTH
        elif mem_type == PrgnRiscV.MemType.DMEM:
            hdl = f"{self.dmem_hdl_top}.u_dmem_ram_{mem_inst}.u_ram.M"
            mem_data_width = self.__DMEM_DATA_WIDTH
        else:
            raise Exception(f"{mem_type.name} is not recognized")

        lsb = entry_byte_offset * mem_data_width
        msb = lsb + mem_data_width - 1
        hdl = f"{hdl}[{mem_entry}][{msb}:{lsb}]"
        return hdl

    def check_address(self, physical_addr):
        if not (self.imem_pa_start <= physical_addr <= self.imem_pa_end) and \
           not (self.dmem_pa_start <= physical_addr <= self.dmem_pa_end):
            raise Exception(f"0x{physical_addr:x} is outside of legal range")

        if self.imem_pa_start <= physical_addr <= self.imem_pa_end:
            mem_type = PrgnRiscV.MemType.IMEM
            mem_addr = physical_addr - self.imem_pa_start
        elif self.dmem_pa_start <= physical_addr <= self.dmem_pa_end:
            mem_type = PrgnRiscV.MemType.DMEM
            mem_addr = physical_addr - self.dmem_pa_start

        addr_bin = f"{mem_addr:032b}"
        entry_byte_offset = int(addr_bin[28:32], 2)
        mem_entry = int(addr_bin[0:28], 2)
        mem_inst = 0

        return mem_type, mem_inst, mem_entry, entry_byte_offset


    #
    # ??????????????????????????????????????????????????????????????????????????????????
    #

    # def boot_from_imem(self, target):
    #     self.__hdl_proxy.ForceVerilogPath32(f"{self.hdl_root}.fuse2fsp_debug_mode",1)
    #     self.__hdl_proxy.ForceVerilogPath32(f"{self.hdl_root}.opt_fsp_riscv_debug_en",0)
    #     #"{self.hdl_root}.u_peregrine.falcon.u_riscv.u_RISCV_dcls_core.u_main.u_RISCV_rob.rob_cur_pc_retx"
    #     self.__hdl_proxy.ForceVerilogPath32(f"{self.hdl_root}.u_peregrine.falcon.u_riscv.u_RISCV_dcls_core.u_main.u_RISCV_rob.rob_expt_target_retx" , 0x00100200)
    #     if target != "simv_fpga":
    #         self.__hdl_proxy.ForceVerilogPath32(f"{self.hdl_root}.u_peregrine.falcon.u_riscv.u_RISCV_dcls_core.u_dupl.u_RISCV_rob.rob_expt_target_retx" , 0x00100200)
    #     self.__hdl_proxy.ForceVerilogPath32(f"{self.hdl_root}.u_peregrine.falcon.riscv_bcr_ctrl_core_select", 0x1)
    #     self.__hdl_proxy.ForceVerilogPath32(f"{self.hdl_root}.u_peregrine.falcon.u_riscv.riscv_boot_after_reset_en", 1)

    def write_xreg(self,index,value):
        hdl_path = f'{self.hdl_root}.u_peregrine_wrap.u_NV_OOB_falcon.u_riscv.u_RISCV_core.u_RISCV_rob.gpr[{index}]'
        self.__hdl_proxy.DepositVerilogPath(hdl_path,list(int(value).to_bytes(8, 'little')))

    def wait_xreg(self,index,value):
        hdl_path = f'{self.hdl_root}.u_peregrine_wrap.u_NV_OOB_falcon.u_riscv.u_RISCV_core.u_RISCV_rob.gpr[{index}]'
        self.__hdl_proxy.WaitVerilogPath(hdl_path,list(int(value).to_bytes(8, 'little')))

    def read_xreg(self,index):
        hdl_path = f'{self.hdl_root}.u_peregrine_wrap.u_NV_OOB_falcon.u_riscv.u_RISCV_core.u_RISCV_rob.gpr[{index}]'
        return self.__hdl_proxy.ReadVerilogPath(hdl_path)

    #
    # ??????????????????????????????????????????????????????????????????????????????????
    #

    # #### Peregrine Global IO access APIs, like IPs (fuse/sysctrl...) under L1/L2 fabric

    # def write_gio(self,addr,value,priv_level=0x3,secure=0x1):
    #     addr = int(addr) + 0x2000000000000000
    #     self.write(addr,value,priv_level,secure)

    # def read_gio(self,addr,priv_level=0x3,secure=0x1):
    #     addr = int(addr) + 0x2000000000000000
    #     return self.read(addr,priv_level,secure)

    # #### Peregrine Local IO access APIs, like IPs (riscv/gdma...) under CSB bus

    # def write_lio(self,addr,value,priv_level=0x3,secure=0x1):
    #     addr = int(addr) + 0x1400000
    #     self.write(addr,value,priv_level,secure)


    # def read_lio(self,addr,priv_level=0x3,secure=0x1):
    #     addr = int(addr) + 0x1400000
    #     return self.read(addr,priv_level,secure)












