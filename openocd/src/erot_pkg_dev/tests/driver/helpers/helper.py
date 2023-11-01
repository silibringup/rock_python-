import os
import re
import struct
import subprocess
from driver.components.priv import Priv
from driver.components.gpio import Gpio
from driver.components.bm_sim import Bm_sim
from driver.components.i2c_mst import I2c_mst
from driver.components.spi_mst import SPIMaster
from driver.components.spi_mst import SPI_SCLK_FREQ_SEL
from driver.components.JTAG import JTAG
from driver.helpers.PrgnRiscV  import PrgnRiscV, FSP, OOB
from RoPy import RPCommon, rpinfo, rpdebug, rperror, rpwarning, rpfatal
import time

class Helper:
    __instance = None
    platform = "SIM_HEADLESS"  # SIM_HEAD, JTAG , HEAD
    target = "simv_top"  # simv_top, simv_fpga

    @classmethod
    def __new__(cls, *args):
        if cls.__instance is None:
            cls.__instance = object.__new__(*args)
        return cls.__instance

    def init(self, link, platform, target, memory_model, regblk_top):
        self.__link = link
        self.link = self.__link
        Helper.platform = platform
        Helper.target = target
        Helper.memory_model = memory_model
        self.__regblk_top = regblk_top
        self.__failure = False
        self.__priv = Priv()
        self.__gpio = Gpio()
        self.__bm_sim = Bm_sim()
        self.priv = self.__priv
        self.__i2c_mst = I2c_mst()
        self.__spi_mst = SPIMaster(self.__link)
        self.__common = RPCommon(self.__link)
        self.__jtag = JTAG(self.__link)
        self.jtag = self.__jtag
        if Helper.target == "simv_fpga":
            self.__fsp = FSP(hdl_root="ntb_top.u_nv_fpga_dut.u_nv_top_fpga.u_nv_top_wrapper.u_nv_top.u_sra_sys0.u_l0_cluster.u_NV_fsp", memory_model=Helper.memory_model)
            self.__oob = OOB(hdl_root="ntb_top.u_nv_fpga_dut.u_nv_top_fpga.u_nv_top_wrapper.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_oobhub", memory_model=Helper.memory_model)
            self.sys0_alias = 'ntb_top.u_nv_fpga_dut.u_nv_top_fpga.u_nv_top_wrapper.u_nv_top.u_sra_sys0'
        else:
            self.__fsp = FSP(hdl_root="ntb_top.u_nv_top.u_sra_sys0.u_l0_cluster.u_NV_fsp", memory_model=Helper.memory_model)
            self.__oob = OOB(hdl_root="ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_oobhub", memory_model=Helper.memory_model)
            self.sys0_alias = 'ntb_top.u_nv_top.u_sra_sys0'
        self.__fsp.set_hdl_proxy(self.__common,self)
        self.fsp = self.__fsp
        self.__oob.set_hdl_proxy(self.__common,self)

    def log(self, message):
        message = f'#{self.get_sim_time()}# {message}'
        rpinfo(message)

    def pinfo(self, message): #No SIMTIME for lite debug
        rpinfo(message)

    def pdebug(self, message): #No SIMTIME for lite debug
        rpdebug(message)

    def pfatal(self, message):
        rpfatal(message)

    def perror(self, message):
        message = f'#{self.get_sim_time()}# {message}'
        rperror(message)
        self.__failure = True
    
    def pwarning(self, message):
        message = f'#{self.get_sim_time()}# {message}'
        rpwarning(message)

    def pplatform_unsupport(self, fnm):
        self.pwarning(f"Running on {Helper.platform}. {fnm}() hasn't been supported")

    def done(self):
        self.__link.finish()
        if not self.__failure:
            rpinfo("TEST SUCCESS COMPLETED")
    
    ##################### GPIO operations ################################
    def gpio_write(self, intf_name, value):
        self.__gpio.write_gpio(self.__link, intf_name, value)

    def gpio_read(self, intf_name):
        return self.__gpio.read_gpio(self.__link, intf_name)

    def wait_rpi_time(self, value, wait_type=0):
        self.__gpio.wait_rpi_time(self.__link, value, wait_type)

    ##################### SPI master access ##############################
    def spi_write(self, spi_port, cs_id, 
                  n_instruction_lane, n_instruction_bits, instruction, 
                  n_address_lane, n_address_bits, address, 
                  n_data_lane, data):

        self.__spi_mst.write(self.__link, spi_port, cs_id, 
                             n_instruction_lane, n_instruction_bits, instruction, 
                             n_address_lane, n_address_bits, address, 
                             n_data_lane, data)

    def spi_read(self, spi_port, cs_id, 
                 n_instruction_lane, n_instruction_bits, instruction, 
                 n_address_lane, n_address_bits, address, 
                 n_data_lane, nbr_rd_bytes, dummy_cycles=0xFFFFFFFF):

              
        return self.__spi_mst.read(self.__link, spi_port, cs_id, 
                                   n_instruction_lane, n_instruction_bits, instruction, 
                                   n_address_lane, n_address_bits, address, 
                                   n_data_lane, nbr_rd_bytes, dummy_cycles)


    def spi_set_sclk_frequency(self, spi_port, freq_sel: SPI_SCLK_FREQ_SEL):
        self.__spi_mst.set_sclk_frequency(self.__link, spi_port, freq_sel)


    ##################### common access APIs for L1/L2 Fabric AMAP##############################
    def i2c_read(self, addr, size=16, i2c_id=0, en_10bits_addr=0, wo_ADDR=0, wo_STOP=0):
        return self.__i2c_mst.read(self.__link, addr, size, i2c_id, en_10bits_addr, wo_ADDR, wo_STOP)

    def i2c_write(self, addr, data, size=16, i2c_id=0, en_10bits_addr=0, wo_STOP=0):
        self.__i2c_mst.write(self.__link, addr, data, size, i2c_id, en_10bits_addr, wo_STOP)

    # used in SMBbus, only for I2C-3
    def i2c_wr_1byte_wo_STOP(self, addr, data):
        self.__i2c_mst.write(self.__link, addr, data, 1, 3, 0, 1)

    def i2c_rd_1byte_wo_STOP(self, addr):
        return self.__i2c_mst.read(self.__link, addr, 1, 3, 0, 0, 1)

    def i2c_rd_Nbytes_wo_ADDR(self, size, addr=0):
        return self.__i2c_mst.read(self.__link, addr, size, 3, 0, 1, 0)

    def erot_rcvy_block_read(self, slv_addr, cmd_code=52, ret_bytes_nbr=False):
        # wr command code wo STOP
        self.i2c_wr_1byte_wo_STOP(slv_addr, cmd_code)
        
        # rd byte cound need to rcvd wo ADDR phase
        ByteNum = self.i2c_rd_1byte_wo_STOP(slv_addr)
        
        if ByteNum == 0:
            if ret_bytes_nbr:
                return ByteNum, None
            return None
        else:
            # rd ByteNum bytes data back
            if ret_bytes_nbr:
                return ByteNum, self.i2c_rd_Nbytes_wo_ADDR(ByteNum)
            return self.i2c_rd_Nbytes_wo_ADDR(ByteNum)

    # Instructions
    # I2C Write 9 bytes always
    #   0 Byte   :  [1:0] priv_level, [2] RNW, [3] In L0 AMAP , [4-5] addr space id, [6-7] Resvered 
    #               addr_space_id: 0 - global io, 1 - local io, 2 - local mem
    #   1-4 Byte :  ADDR
    #   5-8 Byte :  WDATA Or 0
    # I2C Read 9 bytes always
    #   0~3 Byte :  RDATA
    #   4~8 Byte :  0
    def i2c_proxy_write(self, priv_level, l0, addr, data, addr_space_id=0):
        slv_addr1 = 0x12
        I2C_TARGET = 0
        pd = priv_level | (l0 << 3) | (addr_space_id << 4) | (addr << 8) | (data << 40)
        self.i2c_write(slv_addr1, pd, 9, I2C_TARGET)

    def i2c_proxy_read(self, priv_level, l0, addr, addr_space_id=0):
        slv_addr1 = 0x12
        I2C_TARGET = 0
        pd = priv_level | (1 << 2) | (l0 << 3) | (addr_space_id << 4) |  (addr << 8)
        self.i2c_write(slv_addr1, pd, 9, I2C_TARGET)
        return self.i2c_read(slv_addr1,9,I2C_TARGET)

    def hw_proxy_write(self, addr, data, addr_space_id=0):
        self.i2c_proxy_write(3, 0, addr, data, addr_space_id=addr_space_id)

    def hw_proxy_read(self, addr, addr_space_id=0):
        return self.i2c_proxy_read(3, 0, addr, addr_space_id=addr_space_id)

    def SMBus_poll(self, exp, mask, cmd_code, timeout=10, sayerr=True):
        BMC_I2C_SLV_ADDR = 0x69
        cnt = 0
        rd = exp - 1
        while (rd & mask) != exp:
            if cnt >= timeout:
                if sayerr:
                    self.perror(f"I2C read Fail, expect {hex(exp)} but read out {hex(rd & mask)}")
                return False
            rd = self.erot_rcvy_block_read(slv_addr=BMC_I2C_SLV_ADDR, cmd_code=cmd_code)
            cnt += 1
            self.pinfo(f"Polling cmd_code={cmd_code} {cnt} times")
            if rd is None:
                self.perror(f"I2C read back nothing")
        return True

    def SMBus_write(self, cmd, data):
        BMC_I2C_SLV_ADDR = 0x69
        BMC_I2C_ID = 3
        count = len(data)
        trans = [cmd, count] + data
        self.i2c_write(addr=BMC_I2C_SLV_ADDR, data=int.from_bytes(bytes(trans), 'little'), size=len(trans), i2c_id=BMC_I2C_ID)


    ##################### access APIs for Recovery SMB over i2c ##################################
    
    ##############################################################################################
    def jtag_IRScan(self, num_of_bits, data):
        scan_out = self.__jtag.IRScan(num_of_bits, hex(data))
        tdo_value = int.from_bytes(scan_out, "little")
        self.pdebug(f'scanIR {num_of_bits} bits, TDI = {hex(data)}, TDO = {hex(tdo_value)}')
        return tdo_value

    def jtag_DRScan(self, num_of_bits, data):
        scan_out = self.__jtag.DRScan(num_of_bits, hex(data))
        tdo_value = int.from_bytes(scan_out, "little")
        self.pdebug(f'scanDR {num_of_bits} bits, TDI = {hex(data)}, TDO = {hex(tdo_value)}')
        return tdo_value
    
    def j2h_read(self, addr, check_ack=True):
        self.pdebug("JTAG COMPONNET READ : 0x%x" % (addr) )
        START_READ_DR = 0x1<<(118+4) | addr<<(12+4) | 0xfa2<<(0+4) | 0
        END_READ_DR = addr<<(12+4) | 0xfa2<<(0+4) | 0
        self.pdebug("J2H read start")
        # ir_scan_out = self.jtag_IRScan(10, 0x0140)
        ir_scan_out = self.jtag_IRScan(16, 0x0520)
        ir_scan_out = self.jtag_IRScan(25, 0x00a10a0)
        dr_scan_out = self.jtag_DRScan(11, 0x220)
        dr_scan_out = self.jtag_DRScan(124, START_READ_DR)
        
        dummy_ir = 400
        for i in range(dummy_ir):
            self.__jtag.IRScan(25, hex(0x00a10a0)) #WAR for wait at idle, may up to 40000 cycles
        dr_scan_out = self.jtag_DRScan(124, END_READ_DR) #data shifted out
        actual_tdo_bin = bin(dr_scan_out).lstrip('0b').zfill(124)
        actual_data = actual_tdo_bin[124-121-1:124-90] #data on bits [121:90]
        actual_valid_bit = int(actual_tdo_bin[124-10-1]) #valid_bit on bit 10
        if actual_valid_bit == 0 and check_ack == True:
            self.perror(f"Read no ack after {dummy_ir*25} cycles. Scan-out value = {hex(dr_scan_out)}")
        
        ir_scan_out = self.jtag_IRScan(25, 0x00a90e0)
        dr_scan_out = self.jtag_DRScan(114, 0x000000000000000000000000000010)
        ir_scan_out = self.jtag_IRScan(10, 0x0140)
        self.pdebug("J2H read end")
        return int(actual_data,2)

    def j2h_write(self, addr, data, check_ack=True):
        self.pdebug("JTAG COMPONNET WRITE : 0x%x 0x%x " % (addr,data) )
        START_WRITE_DR = 0x1<<(118+4)| data<<(86+4) | addr<<(12+4) | 0xf22<<(0+4) | 0
        END_WRITE_DR = addr<<(7) | 0x79<<(0) | 0
        self.pdebug("J2H write start")
        ir_scan_out = self.jtag_IRScan(16, 0x0520)
        ir_scan_out = self.jtag_IRScan(25, 0x00a1520)
        dr_scan_out = self.jtag_DRScan(11, 0x220)
        dr_scan_out = self.jtag_DRScan(121, 0x0600000000000000002000000000220)
        ir_scan_out = self.jtag_IRScan(25, 0x00a10a0)
        dr_scan_out = self.jtag_DRScan(124, START_WRITE_DR)
        
        dummy_ir = 400
        for i in range(dummy_ir):
            self.__jtag.IRScan(25, hex(0x00a10a0)) #WAR for wait at idle, may up to 40000 cycles

        dr_scan_out = self.jtag_DRScan(124, 0x0) #valid_bit shifted out
        actual_tdo_bin = bin(dr_scan_out).lstrip('0b').zfill(124)
        actual_valid_bit = int(actual_tdo_bin[124-10-1]) #valid_bit on bit 10
        if actual_valid_bit == 0 and check_ack == True:
            self.perror(f"Write no ack after {dummy_ir*25} cycles. Scan-out value = {hex(dr_scan_out)}")

        ir_scan_out = self.jtag_IRScan(25, 0x00a90e0)
        dr_scan_out = self.jtag_DRScan(114, END_WRITE_DR)
        ir_scan_out = self.jtag_IRScan(10, 0x0140)
        self.pdebug("J2H write end")
        return actual_valid_bit

    def j2h_unlock(self):
        #align with FNL for the hardcode sequence
        ir_scan_out = self.jtag_IRScan(10, 0x018)
        dr_scan_out = self.jtag_DRScan(19, 0x00000)
        ir_scan_out = self.jtag_IRScan(16, 0x0600)
        dr_scan_out = self.jtag_DRScan(19, 0x00080)
        ir_scan_out = self.jtag_IRScan(16, 0x0520)
        ir_scan_out = self.jtag_IRScan(25, 0x0121520)
        dr_scan_out = self.jtag_DRScan(11, 0x620)
        dr_scan_out = self.jtag_DRScan(129, 0x009600000000000000003000000000220)
        ir_scan_out = self.jtag_IRScan(25, 0x0128280)
        dr_scan_out = self.jtag_DRScan(9, 0x00b)
        ir_scan_out = self.jtag_IRScan(10, 0x021)
        dr_scan_out = self.jtag_DRScan(17, 0x1ffff)
        ir_scan_out = self.jtag_IRScan(10, 0x014)
        ir_scan_out = self.jtag_IRScan(16, 0x8d00)
        dr_scan_out = self.jtag_DRScan(85, 0x0000000000000000000000)
        ir_scan_out = self.jtag_IRScan(16, 0x0900)
        dr_scan_out = self.jtag_DRScan(7, 0x40)
        dr_scan_out = self.jtag_DRScan(15, 0x0240)
        ir_scan_out = self.jtag_IRScan(16, 0x0530)
        ir_scan_out = self.jtag_IRScan(34, 0x014364d90)
        dr_scan_out = self.jtag_DRScan(13, 0x1ff0)
        ir_scan_out = self.jtag_IRScan(34, 0x3e5f97e50)
        ir_scan_out = self.jtag_IRScan(10, 0x3e5)
        dr_scan_out = self.jtag_DRScan(21, 0x000000)
        ir_scan_out = self.jtag_IRScan(10, 0x3e5)
        dr_scan_out = self.jtag_DRScan(21, 0x000000)
        ir_scan_out = self.jtag_IRScan(10, 0x014)
        ir_scan_out = self.jtag_IRScan(16, 0x3600)
        dr_scan_out = self.jtag_DRScan(7, 0x70)
        ir_scan_out = self.jtag_IRScan(34, 0x3e4f97e50)
        dr_scan_out = self.jtag_DRScan(57, 0x000010000400010)
        ir_scan_out = self.jtag_IRScan(34, 0x014f97e40)
        ir_scan_out = self.jtag_IRScan(25, 0x00a9560)
        dr_scan_out = self.jtag_DRScan(111, 0x3000000000000000018000000001)
        ir_scan_out = self.jtag_IRScan(10, 0x014)
        ir_scan_out = self.jtag_IRScan(16, 0x0520)
        ir_scan_out = self.jtag_IRScan(25, 0x00a17a0)
        dr_scan_out = self.jtag_DRScan(11, 0x220)
        dr_scan_out = self.jtag_DRScan(217, 0x0000007800000020000000000000000000000000000000000000220)
        ir_scan_out = self.jtag_IRScan(25, 0x00a97e0)
        dr_scan_out = self.jtag_DRScan(207, 0x000013c000000100000000000000000000000000000000000001)
        dr_scan_out = self.jtag_DRScan(207, 0x00001bc000000100000000000000000000000000000000000001)
        ir_scan_out = self.jtag_IRScan(10, 0x014)
        ir_scan_out = self.jtag_IRScan(16, 0x0520)
        ir_scan_out = self.jtag_IRScan(25, 0x00a1b20)
        dr_scan_out = self.jtag_DRScan(11, 0x3f0)
        ir_scan_out = self.jtag_IRScan(34, 0x01561d870)
        dr_scan_out = self.jtag_DRScan(61, 0x0000000000000201)
        ir_scan_out = self.jtag_IRScan(10, 0x014)
        ir_scan_out = self.jtag_IRScan(16, 0x0520)
        ir_scan_out = self.jtag_IRScan(25, 0x00a74a0)
        dr_scan_out = self.jtag_DRScan(11, 0x220)
        dr_scan_out = self.jtag_DRScan(509, 0x0039c7049000000004001e0184220058c7023804a1ac238023802380238022002380220000018000000ff0000000000000000000000000000000000004000a20)
        ir_scan_out = self.jtag_IRScan(25, 0x00a74b0)
        ir_scan_out = self.jtag_IRScan(34, 0x014364d90)
        dr_scan_out = self.jtag_DRScan(13, 0x0ff0)
        ir_scan_out = self.jtag_IRScan(34, 0x01511c470)
        dr_scan_out = self.jtag_DRScan(23, 0x004801)
        ir_scan_out = self.jtag_IRScan(10, 0x047)
        dr_scan_out = self.jtag_DRScan(23, 0x004805)
        ir_scan_out = self.jtag_IRScan(10, 0x014)
        ir_scan_out = self.jtag_IRScan(16, 0x0520)
        ir_scan_out = self.jtag_IRScan(25, 0x00a08a0)
        dr_scan_out = self.jtag_DRScan(11, 0x220)
        dr_scan_out = self.jtag_DRScan(33, 0x000904a20)
        ir_scan_out = self.jtag_IRScan(25, 0x00ae360)
        dr_scan_out = self.jtag_DRScan(24, 0x002801)
        ir_scan_out = self.jtag_IRScan(10, 0x31f)
        dr_scan_out = self.jtag_DRScan(24, 0x002801)
        ir_scan_out = self.jtag_IRScan(10, 0x014)
        ir_scan_out = self.jtag_IRScan(16, 0x0570)
        ir_scan_out = self.jtag_IRScan(10, 0x017)
        ir_scan_out = self.jtag_IRScan(10, 0x014)
        ir_scan_out = self.jtag_IRScan(16, 0x0520)
        ir_scan_out = self.jtag_IRScan(25, 0x00a1520)
        dr_scan_out = self.jtag_DRScan(11, 0x220)
        dr_scan_out = self.jtag_DRScan(121, 0x0600000000000000002000000000220)
                
    def j2h_unlock_on_dftlog(self, dft_runlog):
        with open(dft_runlog) as fi:
            lines = fi.readlines()
        for line in lines:
            # chomp then add a space
            line = line.rstrip('\n').rstrip() + ' '        
            # care lines
            shift_ir_list1   = re.findall(r'\ cycle \d+\s+.*?shift_ir\s+.*?\d+\s+.*?[0-9a-f]+\s', line)
            shift_ir_list2   = re.findall(r'\ cycle \d+\s+.*?shift_ir\s+.*?\s+.*?[0-9a-f].*?_', line)
            shift_dr_list1   = re.findall(r'\ cycle \d+\s+.*?shift_dr\s+.*?\d+\s+.*?[0-9a-f]+\s', line)
            shift_dr_list2   = re.findall(r'\ cycle \d+\s+.*?shift_dr\s+.*?\s+.*?[0-9a-f].*?_', line)
            expected_list1   = re.findall(r'\        expected .*?[0-1X]\s', line)
            expected_list2   = re.findall(r'\        expected .*?[0-1X].*?_', line)
            j2h_unlock_list = re.findall(r'\ ENTER procedure: write_to_host', line)
            # don't care lines
            comment_list = re.findall(r'^\s*\/\/', line)
            pound_list = re.findall(r'^\s*#', line)

            # // comment
            if comment_list:
                pass
            # # comment
            elif pound_list:
                pass
            # check shift_ir
            elif shift_ir_list1:
                for item in shift_ir_list1:
                    match = re.search(r'\ cycle (.*?\d+)\s+.*?shift_ir\s+(.*?\d+)\s+(.*?[0-9a-f]+)\s', item)
                    if match:
                        cycle_idx = match.group(1)
                        ir_width = match.group(2)
                        ir_value = match.group(3)
                        hexstring = '0x' + ir_value
                        ir_scan_out = self.jtag_IRScan(int(ir_width), int(hexstring,16))
            elif shift_ir_list2:
                for item in shift_ir_list2:
                    match = re.search(r'\ cycle (.*?\d+)\s+.*?shift_ir\s+(.*?\d+).(.*?\d+).+\s+(.*?[0-9a-f])_', item)
                    if match:
                        cycle_idx = match.group(1)
                        ir_width = match.group(2)
                        ir_value = match.group(4)
                        hexstring = '0x' + ir_value + '0'
                        ir_scan_out = self.jtag_IRScan(int(ir_width), int(hexstring,16))
            # check shift_dr
            elif shift_dr_list1:
                for item in shift_dr_list1:
                    match = re.search(r'\ cycle (.*?\d+)\s+.*?shift_dr\s+(.*?\d+)\s+(.*?[0-9a-f]+)\s', item)
                    if match:
                        cycle_idx = match.group(1)
                        dr_width = match.group(2)
                        dr_width_bytes = (int(dr_width) + 7) // 8 
                        dr_value = match.group(3)
                        hexstring = '0x' + dr_value
                        dr_scan_out = self.jtag_DRScan(int(dr_width), int(hexstring,16))
            elif shift_dr_list2:
                for item in shift_dr_list2:
                    match = re.search(r'\ cycle (.*?\d+)\s+.*?shift_dr\s+(.*?\d+).(.*?\d+).+\s+(.*?[0-9a-f])_', item)
                    if match:
                        cycle_idx = match.group(1)
                        dr_width = match.group(2)
                        dr_width_bytes = (int(dr_width) + 7) // 8
                        dr_value = match.group(4)
                        hexstring = '0x' + dr_value + '0'
                        dr_scan_out = self.jtag_DRScan(int(dr_width), int(hexstring,16))
            #J2H unlock flag
            elif j2h_unlock_list:
                self.pinfo("J2H unlocked")
                break

    def read_headless_in_head_mode(self, addr, priv_id=0, *args, **kwargs):
        if Helper.platform == "SIM_HEADLESS":
            self.perror("Use read_headless() in HEADLESS mode is unnecessary")
            self.pplatform_unsupport("read_headless")
        elif Helper.platform == "SIM_HEAD":
            return self.__priv.read(self.__link, addr, priv_id, *args, **kwargs)
        else:
            self.pplatform_unsupport("read_headless")

    def read(self, addr, priv_id=0, *args, **kwargs):
        self.pdebug(f"[{Helper.platform}]: read @ {hex(addr)}")
        if Helper.platform == "SIM_HEADLESS":
            if priv_id == 0: #J2H
                return self.__priv.read(self.__link, addr, priv_id, *args, **kwargs)
            else:
                addr_list = []
                data_list = []
                cmd_list = []
                addr_list.append(addr)
                data_list.append(0)
                cmd_list.append(0)
                [resp_data_list, resp_err_list] = self.__priv.burst_operation(self.__link, addr_list, data_list, cmd_list, priv_id, 0, *args, **kwargs)
                return resp_data_list[0]
        elif Helper.platform == "SIM_HEAD":
            if "cpu" in kwargs and kwargs["cpu"] == "OOB":
                return self.__oob.read_gio(addr,*args, **kwargs)    
            else:
                return self.__fsp.read_gio(addr,*args, **kwargs)
        elif Helper.platform == "HEAD" or (Helper.platform == "JTAG" and "fpga" in Helper.target):
            if len(args) > 0 :
                priv_level = args[0]
            else:
                priv_level = 3 
       
            pd = priv_level |  (1 << 2)  |  (0 << 3)  |  (addr << 8)
            self.i2c_write(0x12, pd, 9, 0)
            return self.i2c_read(0x12,9,0)
        elif Helper.platform == "JTAG":
            return self.j2h_read(addr)
        else :
            self.pplatform_unsupport("read")

    def write_headless_in_head_mode(self, addr, value, priv_id=0, *args, **kwargs):
        if Helper.platform == "SIM_HEADLESS":
            self.perror("Use read_headless() in HEADLESS mode is unnecessary")
            self.pplatform_unsupport("read_headless")
        elif Helper.platform == "SIM_HEAD":
            self.__priv.write(self.__link, addr, value, priv_id, *args, **kwargs)
        else:
            self.pplatform_unsupport("read_headless")

    def send_payload_to_bm(self, data_byte_list):
        self.__bm_sim.send_payload_to_bm(self.__link, data_byte_list)

    def write(self, addr, value, priv_id=0, *args, **kwargs):
        self.pdebug(f"[{Helper.platform}]: write {hex(value)} @ {hex(addr)}")
        if Helper.platform == "SIM_HEADLESS":
            if priv_id == 0: #J2H
                self.__priv.write(self.__link, addr, value, priv_id, *args, **kwargs)
            else: #1 for sysctrl, 2 for fsp, 3 for oobhub
                addr_list = []
                cmd_list = []
                data_list = []
                addr_list.append(addr)
                cmd_list.append(3)
                data_list.append(value)
                self.__priv.burst_operation(self.__link, addr_list, data_list, cmd_list, priv_id, *args, **kwargs)
        elif Helper.platform == "SIM_HEAD":
            if "cpu" in kwargs and kwargs["cpu"] == "OOB":
                self.__oob.write_gio(addr, value,*args, **kwargs)
            else:
                self.__fsp.write_gio(addr, value,*args, **kwargs)
        elif Helper.platform == "HEAD" or (Helper.platform == "JTAG" and "fpga" in Helper.target):
            if len(args) > 0 :
                priv_level = args[0]
            else:
                priv_level = 3 
            pd = priv_level | (0 << 3)  |  (addr << 8)  | (value << 40)
            self.i2c_write(0x12, pd, 9, 0)
        elif Helper.platform == "JTAG":
            self.j2h_write(addr, value)
        else:
            self.pplatform_unsupport("write")

    def poll(self,addr,value,timeout=100000,*args, **kwargs):
        self.pdebug("Poll Address 0x%x with 0x%x " % (addr, value))
        count = 0
        while count < timeout:
            rd_obj = self.read(addr,*args, **kwargs)

            matched_value = 1
            if rd_obj.value != value:
                matched_value = 0
                break

            count += 1
            if matched_value:
                self.helper.pdebug(f"Poll done after {count} times. poll value = {hex(rd_obj.value)}")
                return
        self.helper.perror(f"Poll timeout after {count} times try. poll value = {hex(rd_obj.value)}")

    def burst_read(self, addr_list, priv_id=1, *args, **kwargs): 
        if not isinstance(addr_list, list):
            self.helper.perror("the addr for burst_read should be a list")
            return
        #if priv_id != 1:
            #self.helper.perror("only sysctrl priv vip support burst read")
            #return    
        #default SIM_HEADLESS, use sysctrl2fab interface
        return self.__priv.burst_read(self.__link, addr_list, priv_id, *args, **kwargs)

    def burst_operation(self, addr_list, data_list, cmd_list, priv_id=1, *args, **kwargs):
        if isinstance(addr_list, list) == 0 or isinstance(data_list, list) == 0 or isinstance(cmd_list, list) == 0:
            self.helper.perror("addr, data, cmd in burst_operation() should be lists")
            return
        if priv_id == 0 or priv_id > 3:
            self.helper.perror("Cannot send burst operations in J2H or invalid priv")
            return
        if (len(addr_list) != len(data_list)) or (len(addr_list) != len(cmd_list)):
            self.helper.perror("The size of addr_list, data_list, cmd_list should be the same")
            return
        return self.__priv.burst_operation(self.__link, addr_list, data_list, cmd_list, priv_id, *args, **kwargs)


    def gdma_transfer(self, src_addr, dst_addr, n_trans_words, is_posted=0):
        self.__regblk_top.FSP.GDMA_CHAN_COMMON_CONFIG_0.update(MEMQ=0, RR_WEIGHT=1)
        self.__regblk_top.FSP.GDMA_CHAN_SRC_ADDR_HI_0.update(VAL=src_addr>>32)
        self.__regblk_top.FSP.GDMA_CHAN_SRC_ADDR_0.update(VAL=(src_addr&0xffffffff))
        self.__regblk_top.FSP.GDMA_CHAN_DEST_ADDR_HI_0.update(VAL=dst_addr>>32)
        self.__regblk_top.FSP.GDMA_CHAN_DEST_ADDR_0.update(VAL=(dst_addr&0xffffffff))
        self.__regblk_top.FSP.GDMA_CHAN_TRANS_CONFIG0_0.update(LENGTH=n_trans_words, SUBCHAN=0, COMPLETE_IRQEN=0)
        self.__regblk_top.FSP.GDMA_CHAN_TRANS_CONFIG1_0.update(SRC_ADDR_MODE="INC")
        self.__regblk_top.FSP.GDMA_CHAN_TRANS_CONFIG1_0.update(DEST_ADDR_MODE="INC")
        self.__regblk_top.FSP.GDMA_CHAN_TRANS_CONFIG1_0.update(DEST_POSTED=is_posted)
        # trigger
        self.__regblk_top.FSP.GDMA_CHAN_TRANS_CONFIG0_0.update(LAUNCH=1)
        self.__regblk_top.FSP.GDMA_CHAN_STATUS_0.poll(BUSY=0)


    def fsp_burst_write(self, dst_addr, words, is_posted=0):
        """"
        FSP priv burst write in address increment mode
        dst_addr: 32-bit aligned target address in absolute address map to incrementally write to, 
                  i.e. must take AMAP offset on chip into account
        words: list of 32-bit data to transfer
        is_posted: if in post mode, i.e. if wait for priv ack
        """
        if not isinstance(words, list):
            self.perror("words to burst write should be a list of 32-bit data")
            return
        # prepare data to send in dmem
        n_trans_words = len(words)
        dmem_end_addr = 0x00200000
        src_addr = dmem_end_addr - 4*n_trans_words
        for i, tval in enumerate(words):
            sw_addr = src_addr + 4*i
            self.write_lmem(sw_addr, tval)
            self.pdebug(f"prepared {hex(tval)} @ {hex(sw_addr)}")
        
        self.gdma_transfer(src_addr, dst_addr, n_trans_words, is_posted)


    def fsp_burst_read(self, src_addr, n_words, is_posted=0):
        """"
        FSP priv burst read in address increment mode
        src_addr: 32-bit aligned source address in absolute address map to incrementally read from, 
                  i.e. must take AMAP offset on chip into account
        n_words: number of 32-bit data to read
        is_posted: if in post mode, i.e. if wait for priv ack
        """
        # prepare space to store read data in dmem
        dmem_end_addr = 0x00200000
        dst_addr = dmem_end_addr - 4*n_words
        self.gdma_transfer(src_addr, dst_addr, n_words, is_posted)

        ans = []
        for i in range(n_words):
            sw_addr = dst_addr + 4*i
            tval = self.read_lmem(sw_addr)
            self.pdebug(f"read {hex(tval)} @ {hex(sw_addr)}")
            ans += [tval]

        return ans


    ##################### common access APIs for L0 Fabric AMAP##############################

    def read_l0(self, addr, *args, **kwargs):
        self.pdebug("READ Address 0x%x (%s)" % (addr, args))
        if Helper.platform == "SIM_HEAD":
            if "cpu" in kwargs and kwargs["cpu"] == "OOB":
                return self.__oob.read_lio(addr,*args, **kwargs)
            else:
                return self.__fsp.read_lio(addr,*args, **kwargs)
        elif Helper.platform == "HEAD":
            if "cpu" in kwargs and kwargs["cpu"] == "OOB":
                self.pplatform_unsupport("OOB read_l0")
            else:
                return self.i2c_proxy_read(3, 1, addr, addr_space_id=1)
        else :
            self.pplatform_unsupport("read_l0")

    def write_l0(self, addr, value, *args, **kwargs):
        self.pdebug("Write Address 0x%x -> 0x%x (%s)" % (addr, value, args))
        if Helper.platform == "SIM_HEAD":
            if "cpu" in kwargs and kwargs["cpu"] == "OOB":
                self.__oob.write_lio(addr, value,*args, **kwargs)
            else:
                self.__fsp.write_lio(addr, value,*args, **kwargs)
        elif Helper.platform == "HEAD":
            if "cpu" in kwargs and kwargs["cpu"] == "OOB":
                self.pplatform_unsupport("OOB write_l0")
            else:
                self.i2c_proxy_write(3, 1, addr, value, addr_space_id=1)
        else:
             self.pplatform_unsupport("write_l0")

    def poll_l0(self,addr, value,timeout=100000,*args, **kwargs):
        self.pdebug("Poll Address 0x%x with 0x%x " % (addr, value))
        count = 0
        while count < timeout:
            rd_obj = self.read_l0(addr,*args, **kwargs)

            matched_value = 1
            if rd_obj.value != value:
                matched_value = 0
                break

            count += 1
            if matched_value:
                self.helper.pdebug(f"Poll done after {count} times. poll value = {hex(rd_obj.value)}")
                return
        self.helper.perror(f"Poll timeout after {count} times try. poll value = {hex(rd_obj.value)}")


    def read_lmem(self, addr, *args, **kwargs):
        self.pdebug("READ Address 0x%x (%s)" % (addr, args))
        if Helper.platform == "SIM_HEAD":
            if "cpu" in kwargs and kwargs["cpu"] == "OOB":
                return self.__oob.read_lmem(addr,*args, **kwargs)
            else:
                return self.__fsp.read_lmem(addr,*args, **kwargs)
        elif Helper.platform == "HEAD":
            # i2c proxy read @ local mem space
            return self.i2c_proxy_read(3, 0, addr, addr_space_id=2)
        else :
            self.pplatform_unsupport("read_lmem")

    def write_lmem(self, addr, value, *args, **kwargs):
        self.pdebug("Write Address 0x%x -> 0x%x (%s)" % (addr, value, args))
        if Helper.platform == "SIM_HEAD":
            if "cpu" in kwargs and kwargs["cpu"] == "OOB":
                self.__oob.write_lmem(addr, value,*args, **kwargs)
            else:
                self.__fsp.write_lmem(addr, value,*args, **kwargs)
        elif Helper.platform == "HEAD":
            # i2c proxy write @ local mem space
            self.i2c_proxy_write(3, 0, addr, value, addr_space_id=2)
        else:
             self.pplatform_unsupport("write_lmem")


    ########################## Help API ##############################
    def wait_sim_time(self, unit, value):
        if Helper.target in ["simv_top", "simv_fpga", "simv_gate","simv_synth"]:
            self.__common.WaitSimTime(unit, value)
        else:
            self.pplatform_unsupport("wait_sim_time")

    def get_sim_time(self):
        if Helper.target in ["simv_top", "simv_fpga", "simv_gate","simv_synth"]:
            return self.__common.GetSimTime()
        else:
            return "null ns"

    def set_loop_back(self, value):
        if "SIM" in Helper.platform or (Helper.platform == "HEAD" and Helper.target == 'simv_fpga'):
            self.pdebug(f"set loop back: {hex(value)}")
            self.__common.ForceVerilogPath32("ntb_top.u_clk_rst_if.enable_loopback", value)
        else:
            self.pplatform_unsupport("set_loop_back")

    def set_gpio_loop_back(self, value):
        if "SIM" in Helper.platform:
            self.pdebug(f"set gpio loop back: {hex(value)}")
            self.__common.ForceVerilogPath32("ntb_top.u_clk_rst_if.enable_gpio_loopback", value)
        else:
            self.pplatform_unsupport("set_gpio_loop_back")

    def set_qspi_read_loop_back(self, value):
        if "SIM" in Helper.platform:
            self.log(f"set qspi read loop back: {hex(value)}")
            self.__common.ForceVerilogPath32("ntb_top.u_clk_rst_if.enable_qspi_read_loopback", value)
        else:
            self.pplatform_unsupport("set_qspi_read_loop_back")

    def set_spi_monitor_loopback(self, value):
        if "SIM" in Helper.platform:
            self.log(f"set spi monitor loopback: {hex(value)}")
            self.__common.ForceVerilogPath32("ntb_top.u_clk_rst_if.enable_bmonitor_test", value)
        else:
            self.pplatform_unsupport("set_spi_monitor_loopback")

    def set_gpio_test(self, value):
        if "SIM" in Helper.platform:
            self.pdebug(f"set gpio test: {hex(value)}")
            self.__common.ForceVerilogPath32("ntb_top.u_clk_rst_if.enable_gpio_test", value)
        else:
            self.pplatform_unsupport("set_gpio_test")

    def bin_to_mif(self, cpu="FSP"):
        mem_data = {}
        src_cpu = self.__fsp
        if cpu == "OOB":
            src_cpu = self.__oob
        for p, data in src_cpu.mem_data.items():
            if len(data) % 16 != 0:
                for i in range(16 - len(data)%16):
                    data.append("000000000")
            for i in range(0, len(data), 16):
                entry_data = ""
                for d in data[i:i+16]:
                    entry_data = f"{d}{entry_data}"
                if p not in mem_data:
                    mem_data[p] = []
                mem_data[p].append(entry_data)
            
            WIDTH = 144
            DEPTH = 8192

            if "imem_wrap.u_imem" in p:
                for i in range(8):
                    mem_data[p].insert(0, "0"*WIDTH)

            n_pad_entry = DEPTH - len(mem_data[p])
            if n_pad_entry > 0:
                for i in range(n_pad_entry):
                    mem_data[p].append("0"*WIDTH)

            with open(f"{p}.mif","w") as f:
                f.write(f"WIDTH={WIDTH};\nDEPTH={DEPTH};\nADDRESS_RADIX=HEX;\nDATA_RADIX=BIN;\n")
                f.write("\nCONTENT BEGIN\n")
                for n, i in enumerate(mem_data[p]):
                    f.write(f"\t{n:04x} : {i};\n")
                f.write("END;\n")

    def fsp_dis_clob(self):
            # close clobber in imem to avoid backdoor load flushed by clobber before reset
            for i in range(4):
                s = f"{self.__fsp.hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_imem.imem_wrap.u_imem.u_SCANBYPASS_imem_ram_{i}.s_nv_ram_parity_errProt"
                if self.target in ["simv_gate","simv_synth"]:
                    s = self.hdl_translate(s)
                    self.pwarning(f"{s}.array_clobbered doesn't exist in syn ram")
                else:
                    self.hdl_force(f"{s}.array_clobbered", 0)

            #self.hdl_force(f"{self.__fsp.hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_imem.imem_wrap.u_imem.u_SCANBYPASS_imem_ram_sim_0.s_nv_ram_parity_errProt.array_clobbered", 0)
            #self.hdl_force(f"{self.__fsp.hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_imem.imem_wrap.u_imem.u_SCANBYPASS_imem_ram_sim_1.s_nv_ram_parity_errProt.array_clobbered", 0)
            #self.hdl_force(f"{self.__fsp.hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_imem.imem_wrap.u_imem.u_SCANBYPASS_imem_ram_sim_2.s_nv_ram_parity_errProt.array_clobbered", 0)
            #self.hdl_force(f"{self.__fsp.hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_imem.imem_wrap.u_imem.u_SCANBYPASS_imem_ram_sim_3.s_nv_ram_parity_errProt.array_clobbered", 0)

            for i in range(4):
                s = f"{self.__fsp.hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_dmem.dmem_wrap.u_dmem.u_SCANBYPASS_dmem_ram_{i}.s_nv_ram_parity_errProt"
                if self.target in ["simv_gate","simv_synth"]:
                    s = self.hdl_translate(s)
                    self.pwarning(f"{s}.array_clobbered doesn't exist in syn ram")
                else:
                    self.hdl_force(f"{s}.array_clobbered", 0)
        
            #self.hdl_force(f"{self.__fsp.hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_dmem.dmem_wrap.u_dmem.u_SCANBYPASS_dmem_ram_sim_0.s_nv_ram_parity_errProt.array_clobbered", 0)
            #self.hdl_force(f"{self.__fsp.hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_dmem.dmem_wrap.u_dmem.u_SCANBYPASS_dmem_ram_sim_1.s_nv_ram_parity_errProt.array_clobbered", 0)
            #self.hdl_force(f"{self.__fsp.hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_dmem.dmem_wrap.u_dmem.u_SCANBYPASS_dmem_ram_sim_2.s_nv_ram_parity_errProt.array_clobbered", 0)
            #self.hdl_force(f"{self.__fsp.hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_dmem.dmem_wrap.u_dmem.u_SCANBYPASS_dmem_ram_sim_3.s_nv_ram_parity_errProt.array_clobbered", 0)

    def fsp_boot_init(self, bin_path, 
                      i_file_start_offset=0, i_load_size=-1, i_mem_start_offset=0,
                      d_file_start_offset=0, d_load_size=0, d_mem_start_offset=0, 
                      mode=0): # mode 0 : boot from imem, mode 1 : self-boot
        if not mode :
            self.wait_sim_time("ns", 100)
            self.__fsp.init_imem_zero()
            # close clobber in imem to avoid backdoor load flushed by clobber before reset
            #self.hdl_force(f"{self.__fsp.hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_imem.imem_wrap.u_imem.u_SCANBYPASS_imem_ram_0.s_nv_ram_parity_errProt.array_clobbered", 0)
            #self.hdl_force(f"{self.__fsp.hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_imem.imem_wrap.u_imem.u_SCANBYPASS_imem_ram_1.s_nv_ram_parity_errProt.array_clobbered", 0)
            #self.hdl_force(f"{self.__fsp.hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_imem.imem_wrap.u_imem.u_SCANBYPASS_imem_ram_2.s_nv_ram_parity_errProt.array_clobbered", 0)
            #self.hdl_force(f"{self.__fsp.hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_imem.imem_wrap.u_imem.u_SCANBYPASS_imem_ram_3.s_nv_ram_parity_errProt.array_clobbered", 0)

            #self.hdl_force(f"{self.__fsp.hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_dmem.dmem_wrap.u_dmem.u_SCANBYPASS_dmem_ram_0.s_nv_ram_parity_errProt.array_clobbered", 0)
            #self.hdl_force(f"{self.__fsp.hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_dmem.dmem_wrap.u_dmem.u_SCANBYPASS_dmem_ram_1.s_nv_ram_parity_errProt.array_clobbered", 0)
            #self.hdl_force(f"{self.__fsp.hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_dmem.dmem_wrap.u_dmem.u_SCANBYPASS_dmem_ram_2.s_nv_ram_parity_errProt.array_clobbered", 0)
            #self.hdl_force(f"{self.__fsp.hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_dmem.dmem_wrap.u_dmem.u_SCANBYPASS_dmem_ram_3.s_nv_ram_parity_errProt.array_clobbered", 0)

            if Helper.platform in [ "HEAD", "SIM_HEAD" ]:
                init_req_imem = f'{self.__fsp.hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_imem.imem_wrap.imem_scrub.mem_init_req'
                done_req_imem = f'{self.__fsp.hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_imem.imem_wrap.imem_scrub.mem_init_uncompelete_clamp'
                self.hdl_force(init_req_imem,0)
                self.hdl_force(done_req_imem,0)

            self.__fsp.preload_imem(bin_path, i_file_start_offset, i_load_size, i_mem_start_offset)
            if d_load_size != 0:
                self.__fsp.preload_dmem(bin_path, d_file_start_offset, d_load_size, d_mem_start_offset)

            self.__fsp.boot_from_imem(Helper.target)
            if Helper.platform != "HEAD":
                # don't jump to main
                self.hdl_force(f'{self.__fsp.hdl_root}.u_peregrine.falcon.cfgregs.falcon_common_scratch_group_{self.__fsp.decode_index(PrgnRiscV.GOMAIN_XREG)}_val', 1)
            self.wait_reset(f"{self.__fsp.hdl_root}.u_peregrine.NV_FSP_reset_reset_")

            if Helper.platform == "HEAD":
                self.wait_sim_time("us", 200) #Give FSP Time to Setup I2C Proxy

            self.bin_to_mif()
        else :
            self.pplatform_unsupport("mode 1 : self-boot")


    def oob_boot_init(self, bin_path, 
                      i_file_start_offset=0, i_load_size=-1, i_mem_start_offset=0,
                      d_file_start_offset=0, d_load_size=0, d_mem_start_offset=0):
        # close clobber in imem to avoid backdoor load flushed by clobber before reset
        self.hdl_force(f"{self.__oob.hdl_root}.u_peregrine_wrap.u_NV_OOB_falcon.l1tcm_wrap.l1tcm.u_imem.imem_wrap.u_imem.u_imem_ram_0.u_ram.array_clobbered", 0)
        self.hdl_force(f"{self.__oob.hdl_root}.u_peregrine_wrap.u_NV_OOB_falcon.l1tcm_wrap.l1tcm.u_dmem.dmem_wrap.u_dmem.u_dmem_ram_0.u_ram.array_clobbered", 0)

        self.__oob.preload_imem(bin_path, i_file_start_offset, i_load_size, i_mem_start_offset, has_parity=False)
        if d_load_size != 0:
            self.__oob.preload_dmem(bin_path, d_file_start_offset, d_load_size, d_mem_start_offset, has_parity=False)
    
        
    def wait_reset(self, reset):
        reset = self.hdl_translate(reset)
        if Helper.target in ["simv_top", "simv_fpga", "simv_gate","simv_synth"]:
            self.__common.WaitReset(reset)
        else :
            self.pplatform_unsupport("wait_reset")

 
    ########################## Advanced API ##############################

    def hdl_translate(self,hdl_path):
        if self.debug_hdl:
            self.pinfo(f"############ :  ACCESSING {hdl_path}")
        if self.target in ["simv_gate"]:
            hdl_path = hdl_path.replace('u_l0_cluster.u_NV_fsp.u_peregrine.falcon','\\u_l0_cluster/u_NV_fsp/u_peregrine/falcon ')
            hdl_path = hdl_path.replace('u_l0_cluster.u_NV_fsp.u_peregrine',       '\\u_l0_cluster/u_NV_fsp/u_peregrine/falcon ')
            hdl_path = hdl_path.replace('u_l0_cluster.u_NV_fsp',                   '\\u_l0_cluster/u_NV_fsp/u_peregrine/falcon ')
            if self.debug_hdl:
                self.pinfo(f"!!!!!!!!!!!! :  ACCESSING {hdl_path}")
        return hdl_path

    def hdl_release(self, hdl_path):
        hdl_path = self.hdl_translate(hdl_path)
        if Helper.target in ["simv_top", "simv_fpga", "simv_gate","simv_synth"]:
            self.__common.ReleaseVerilogPath(hdl_path)
        else:
            self.pplatform_unsupport("hdl_release")
    
    def hdl_deposit(self, hdl_path, value):
        hdl_path = self.hdl_translate(hdl_path)
        if Helper.target in ["simv_top", "simv_fpga", "simv_gate","simv_synth"]:
            if isinstance(value,list):
                self.__common.DepositVerilogPath(hdl_path, value)
            else:
                self.__common.DepositVerilogPath32(hdl_path, value)
        else:
            self.pplatform_unsupport("hdl_deposit")

    def hdl_force(self, hdl_path, value):
        hdl_path = self.hdl_translate(hdl_path)
        if Helper.target in ["simv_top", "simv_fpga", "simv_gate","simv_synth"]:
            if isinstance(value,list):
                self.__common.ForceVerilogPath(hdl_path, value)
            else:
                self.__common.ForceVerilogPath32(hdl_path, value)
        else:
            self.pplatform_unsupport("hdl_force")

    def hdl_read(self, hdl_path):
        hdl_path = self.hdl_translate(hdl_path)
        if Helper.target in ["simv_top", "simv_fpga", "simv_gate","simv_synth"]:
            return self.__common.ReadVerilogPath(hdl_path)
        else:
            self.pplatform_unsupport("hdl_read")

    def hdl_wait(self, hdl_path, value):
        hdl_path = self.hdl_translate(hdl_path)
        if Helper.target in ["simv_top", "simv_fpga", "simv_gate","simv_synth"]:
            if isinstance(value,list):
                self.__common.WaitVerilogPath(hdl_path, value)
            else:
                self.__common.WaitVerilogPath32(hdl_path, value)
        else:
            self.pplatform_unsupport("hdl_wait")

    def disable_unused_car(self, ip_name):
        clk_gating_reg_dict = {}
        clk_gating_reg_dict["mram"]      = self.__regblk_top.CLOCK.NVEROT_CLOCK_SYS_CTL.SW_BOOT_QSPI_CLK_RCM_CFG_0
        clk_gating_reg_dict["qspi0"]     = self.__regblk_top.CLOCK.NVEROT_CLOCK_IO_CTL.SW_QSPI0_CLK_RCM_CFG_0
        clk_gating_reg_dict["qspi1"]     = self.__regblk_top.CLOCK.NVEROT_CLOCK_IO_CTL.SW_QSPI1_CLK_RCM_CFG_0
        clk_gating_reg_dict["boot_qspi"] = self.__regblk_top.CLOCK.NVEROT_CLOCK_SYS_CTL.SW_BOOT_QSPI_CLK_RCM_CFG_0
        clk_gating_reg_dict["spi_mon0"]  = self.__regblk_top.CLOCK.NVEROT_CLOCK_IO_CTL.SW_BYPASS_MON0_CLK_RCM_CFG_0
        clk_gating_reg_dict["spi_mon1"]  = self.__regblk_top.CLOCK.NVEROT_CLOCK_IO_CTL.SW_BYPASS_MON1_CLK_RCM_CFG_0
        clk_gating_reg_dict["oob_spi"]   = self.__regblk_top.CLOCK.NVEROT_CLOCK_IO_CTL.SW_OOB_SPI_CLK_RCM_CFG_0
        clk_gating_reg_dict["inb0_spi"]  = self.__regblk_top.CLOCK.NVEROT_CLOCK_IO_CTL.SW_INB0_SPI_CLK_RCM_CFG_0
        clk_gating_reg_dict["inb1_spi"]  = self.__regblk_top.CLOCK.NVEROT_CLOCK_IO_CTL.SW_INB1_SPI_CLK_RCM_CFG_0
        clk_gating_reg_dict["uart"]      = self.__regblk_top.CLOCK.NVEROT_CLOCK_IO_CTL.SW_UART_CLK_RCM_CFG_0
        clk_gating_reg_dict["inb0_i3c"]  = self.__regblk_top.CLOCK.NVEROT_CLOCK_IO_CTL.SW_INB0_I3C_CLK_RCM_CFG_0
        clk_gating_reg_dict["inb1_i3c"]  = self.__regblk_top.CLOCK.NVEROT_CLOCK_IO_CTL.SW_INB1_I3C_CLK_RCM_CFG_0
        clk_gating_reg_dict["oob_i3c"]   = self.__regblk_top.CLOCK.NVEROT_CLOCK_SYS_CTL.SW_OOB_I3C_CLK_RCM_CFG_0

        sw_reset_reg_dict = {}
        sw_reset_reg_dict["gpio_ctrl"] = self.__regblk_top.RESET.NVEROT_RESET_CFG.SW_GPIO_CTRL_RST_0
        sw_reset_reg_dict["spi_mon0"]  = self.__regblk_top.RESET.NVEROT_RESET_CFG.SW_SPIMON0_RST_0
        sw_reset_reg_dict["spi_mon1"]  = self.__regblk_top.RESET.NVEROT_RESET_CFG.SW_SPIMON1_RST_0
        sw_reset_reg_dict["inb0_spi"]  = self.__regblk_top.RESET.NVEROT_RESET_CFG.SW_IB0_SPI_RST_0
        sw_reset_reg_dict["inb1_spi"]  = self.__regblk_top.RESET.NVEROT_RESET_CFG.SW_IB1_SPI_RST_0
        sw_reset_reg_dict["oob_spi"]   = self.__regblk_top.RESET.NVEROT_RESET_CFG.SW_OOB_SPI_RST_0
        sw_reset_reg_dict["inb0_i2c"]  = self.__regblk_top.RESET.NVEROT_RESET_CFG.SW_IB0_I2C_RST_0
        sw_reset_reg_dict["inb1_i2c"]  = self.__regblk_top.RESET.NVEROT_RESET_CFG.SW_IB1_I2C_RST_0
        sw_reset_reg_dict["io_exp"]    = self.__regblk_top.RESET.NVEROT_RESET_CFG.SW_IO_EXP_RST_0
        sw_reset_reg_dict["uart"]      = self.__regblk_top.RESET.NVEROT_RESET_CFG.SW_UART_RST_0

        if ip_name in clk_gating_reg_dict.keys():
            for ip, reg in clk_gating_reg_dict.items():
                if reg.name != clk_gating_reg_dict[ip_name].name:
                    if ip == "oob_i3c":
                        reg.update(GATE_CLK_DIV_SW=1)
                    else:
                        reg.update(CLK_DIS_STOP_ON=1)
        else:
            self.log("Unsupport IP %s in deassert clk" % ip_name)

        for ip, reg in sw_reset_reg_dict.items():
            if ip != ip_name:
                reg.write(0)
        self.log("disable_unused_car for IP %s done" % ip_name)
    
            

    ########################### APIs for clk monitor ##############################
    def get_clk_freq_float(self, clk_name):
        if Helper.target == "simv_fpga":
            self.log("Not support clk monitor in simv_fpga")
            return
        
        if clk_name == "VrefRO_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_clock_sys.u_clk_mon_VrefRO_clk.freq_bits")
        elif clk_name == "ref_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_top0.u_NV_nverot_clock_top.u_clk_mon_sys_clks_ref_clk_sw.freq_bits")
        elif clk_name == "ts_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_TSENSE_wrapper2.u_clk_mon_ts_clk.freq_bits")
        elif clk_name == "reset_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_reset.u_clk_mon_reset_clk.freq_bits")
        elif clk_name == "mram_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_mwrap.u_clk_mon_mram_clk.freq_bits")
        elif clk_name == "L1_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_clk_mon_L1_clk.freq_bits")
        elif clk_name == "therm_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fsi_therm.u_clk_mon_therm_clk.freq_bits")
        elif clk_name == "qspi0_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_qspi0.u_clk_mon_qspi0.freq_bits")
        elif clk_name == "qspi0_pm_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_top0.u_qspi0_pad_macros.u_clk_mon_pm_qspi0.freq_bits")
        elif clk_name == "qspi1_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_qspi1.u_clk_mon_qspi1.freq_bits")
        elif clk_name == "qspi1_pm_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_top0.u_qspi1_pad_macros.u_clk_mon_pm_qspi1.freq_bits")
        elif clk_name == "boot_qspi_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_boot_qspi.u_clk_mon_boot_qspi.freq_bits")
        elif clk_name == "boot_qspi_pm_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_top0.u_boot_qspi_pad_macros.u_clk_mon_pm_boot_qspi.freq_bits")
        elif clk_name == "spi_mon0_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_bypmon0.u_clk_mon_spi_mon0.freq_bits")
        elif clk_name == "spi_mon1_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_bypmon1.u_clk_mon_spi_mon1.freq_bits")
        elif clk_name == "fuse_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.u_clk_mon_fuse.freq_bits")
        elif clk_name == "fsp_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l0_cluster.u_NV_fsp.u_clk_mon_fsp.freq_bits")
        elif clk_name == "fsp_fuse_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l0_cluster.u_NV_fsp.u_clk_mon_fsp_fuse.freq_bits")
        elif clk_name == "L0_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l0_cluster.u_clk_mon_L0_clk.freq_bits")
        elif clk_name == "L2_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_clk_mon_L2_clk.freq_bits")
        elif clk_name == "oobhub_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_oobhub.u_clk_mon_oobhub_clk.freq_bits")
        elif clk_name == "gpio_ctl_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_GPIO_ctl0.u_clk_mon_gpio_ctl_clk.freq_bits")
        elif clk_name == "oobhub_spi_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_oobhub_spi.u_clk_mon_oobhub_spi_clk.freq_bits")
        elif clk_name == "oobhub_spi_pm_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_top0.u_oobhub_spi_pad_macro.u_clk_mon_oobhub_spi_pm.freq_bits")
        elif clk_name == "ib0_spi_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_spi_ib0.u_clk_mon_spi_ib0.freq_bits")
        elif clk_name == "ib0_spi_pm_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_top0.u_spi_ib0_pad_macro.u_clk_mon_spi_ib0_pm.freq_bits")
        elif clk_name == "ib1_spi_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_spi_ib1.u_clk_mon_spi_ib1.freq_bits")
        elif clk_name == "ib1_spi_pm_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_top0.u_spi_ib1_pad_macro.u_clk_mon_spi_ib1_pm.freq_bits")
        elif clk_name == "uart_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_sbsa_uart.u_clk_mon_uart_clk.freq_bits")
        elif clk_name == "ib0_i3c_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_i3c_ib0.u_clk_mon_i3c_ib0.freq_bits")
        elif clk_name == "ib0_i2c_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_i2c_ib0.u_clk_mon_i2c_ib0.freq_bits")
        elif clk_name == "ib1_i3c_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_i3c_ib1.u_clk_mon_i3c_ib1.freq_bits")
        elif clk_name == "ib1_i2c_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_i2c_ib1.u_clk_mon_i2c_ib1.freq_bits")
        elif clk_name == "mctp_i3c_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_oobhub.u_i3c_wrap.u_clk_mon_mctp_i3c.freq_bits")
        elif clk_name == "mctp_i2c_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_oobhub.u_i2c_wrap.u_clk_mon_mctp_i2c.freq_bits")
        elif clk_name == "recovery_i2c_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_oobhub.u_i2c_recovery_wrap.u_clk_mon_rcvry_i2c.freq_bits")
        elif clk_name == "ioexpander_i2c_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_i2c_io_expander.u_clk_mon_ioexpander_i2c.freq_bits")
        elif clk_name == "ib0_i2c_slow_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_i2c_ib0.u_clk_mon_i2c_ib0_slow.freq_bits")
        elif clk_name == "ib1_i2c_slow_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_i2c_ib1.u_clk_mon_i2c_ib1_slow.freq_bits")
        elif clk_name == "mctp_i2c_slow_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_oobhub.u_i2c_wrap.u_clk_mon_oobhub_i2c_slow.freq_bits")
        elif clk_name == "recovery_i2c_slow_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_oobhub.u_i2c_recovery_wrap.u_clk_mon_oobhub_rcvy_i2c_slow.freq_bits")
        elif clk_name == "ioexpander_i2c_slow_clk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_i2c_io_expander.u_clk_mon_ioexpander_i2c_slow.freq_bits")
        elif clk_name == "fsp_1us_tick":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l0_cluster.u_NV_fsp.u_peregrine.u_clk_mon_fsp_1us_tick.freq_bits")
        elif clk_name == "obs_gp26_dbgclk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_obs_debugclk_26.freq_bits")
        elif clk_name == "obs_gp27_dbgclk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_obs_debugclk_27.freq_bits")
        elif clk_name == "obs_gp28_dbgclk":
            freq_hex = self.hdl_read("ntb_top.u_nv_top.u_obs_debugclk_28.freq_bits")
        else:
            self.perror("Unsupported clk_name %s" % clk_name)
            return

        bytes_val = freq_hex.to_bytes(4, 'big')
        return struct.unpack('!f', bytes_val)[0]
    
    def get_reset_queue_size(self):
        return self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_reset.u_reset_monitor.reset_prop_q_size")

    def get_reset_queue_element(self, index):
        if index >= self.get_reset_queue_size():
            self.perror("index %d > size %d" % (index, get_reset_queue_size()))
        return self.hdl_read("ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_nverot_reset.u_reset_monitor.reset_prop_q[%d]" % index)


    def backdoor_fill_mram(self, binfile, start_entry_offset, wanna_corrupt=False, only_peek=False):
        mram = {}
        def deposit_mram_entry(entry_addr, data256):
            for j in range(256 // 32):
                split_wr_data = (data256 >> (32 * j)) & 0xffffffff
                hdl_path = f"{self.sys0_alias}.u_l1_cluster.u_NV_nverot_mwrap.u_mram_sys.mram_inst.core.main_mem[{entry_addr}][{(j + 1) * 32 - 1}:{j * 32}]"
                self.hdl_deposit(hdl_path, split_wr_data)
     
        with open(binfile, "rb") as f:
            B = f.read()
            entry_addr = start_entry_offset
            while B:
                if len(B) >= 32:
                    entry_data = B[:32]
                    B = B[32:]
                else:
                    entry_data = B
                    B = []
                entry_data = int.from_bytes(entry_data, 'little')
                if wanna_corrupt:
                    entry_data += 1
                if not only_peek:
                    deposit_mram_entry(entry_addr, entry_data)
                mram[entry_addr] = entry_data
                entry_addr += 1

        return mram


    def backdoor_init_mram(self, ledger_binfile, run_binfile, corrupt_img_a=False, corrupt_img_b=False, only_peek=False):
        if Helper.target in ["simv_top", "simv_fpga", "simv_gate","simv_synth"]:
            if not os.path.exists(ledger_binfile):
                raise Exception(f"{ledger_binfile} No such ledger file")
            
            if not os.path.exists(run_binfile):
                raise Exception(f"{run_binfile} No such fmc file")

            mram = {}
            m = self.backdoor_fill_mram(ledger_binfile, start_entry_offset=0, only_peek=only_peek)
            mram.update(m)
            m = self.backdoor_fill_mram(run_binfile, start_entry_offset=128, wanna_corrupt=corrupt_img_a, only_peek=only_peek)
            mram.update(m)
            m = self.backdoor_fill_mram(run_binfile, start_entry_offset=32896, wanna_corrupt=corrupt_img_b, only_peek=only_peek)
            mram.update(m)
            return mram
        else:
            self.pplatform_unsupport("backdoor_init_mram")


    def cms2_reference_data(self, file):
        ans = []
        if file is None:
            subprocess.call(["nvrun post_brom_cms2_check -dumpFmod 0 -dumpVmod 1 -dumpCmod 0 -SkateMfgBoot 0"], shell=True)
            file = "src/cms2_golden_data_byte_stream.txt"
        with open(file, "r") as f:
            t = f.read().strip()
            for i in range(0, len(t), 2):
                ans.append(int(t[i:i+2], 16))
        return bytes(ans)


    def backdoor_fill_fuse_macro(self, macro_idx, data):
        for i in range(len(data)):
            if Helper.target == 'simv_fpga':
                hdl_path = f"{self.sys0_alias}.u_l1_cluster.u_NV_fuse.u_fuse_macro_wrap.u_fuse_macro_{macro_idx}.u_fuse_macro_ram.u_mem.ram_1port_0.altera_syncram_component.mem_data[{i//32}][{i%32}]"
            else:
                hdl_path = f"{self.sys0_alias}.u_l1_cluster.u_NV_fuse.u_fuse_macro_wrap.u_fuse_macro_{macro_idx}.fuse_data[{i}]"
            self.hdl_deposit(hdl_path, int(data[i], 2))



    def backdoor_init_fuse(self, fuse_image_file):
        if Helper.target in ["simv_top", "simv_fpga", "simv_gate","simv_synth"]:
            if not os.path.exists(fuse_image_file):
                helper.pfatal(f"{fuse_image_file} No such fuse image file")
            with open(fuse_image_file, "r") as f:
                txt = f.read().strip()
                if not txt:
                    self.pfatal(f"fuse image is empty")
                t = re.sub(" |\n", "", txt)
                for macro_idx in range(4):
                    self.backdoor_fill_fuse_macro(macro_idx, t[macro_idx*(len(t)//4):(macro_idx+1)*(len(t)//4)])
        else:
            self.pplatform_unsupport("backdoor_init_fuse")


    def backdoor_init_bootrom(self, brom_init_dir):
        if not os.path.exists(brom_init_dir):
            raise Exception(f"{brom_init_dir} No such file or directory")

        fls = os.listdir(brom_init_dir)
        rom_txt = [f"CSTM_ROM_8192X32_SR01_I{i}_A1.txt" for i in range(1, 7)]
        for i in rom_txt:
            if i not in fls:
                raise Exception(f"No {i} exists in {brom_init_dir}")
        
        for i, txt in enumerate(rom_txt):
            rom_hdl = f"{self.__fsp.hdl_root}.u_peregrine.falcon.l1tcm_wrap.l1tcm.u_imem.imem_wrap.rvbrom.rom_nonstubout.u_SCANBYPASS_fsp_brom_{i}.r_nv_rom_j_8192x32_b_pSR01_I{i+1}.rom_Inst_8192X32.RomData"
            with open(f"{brom_init_dir}/{txt}", 'r') as f:
                for entry, line in enumerate(f.readlines()):
                    data = int(line.strip(), 2)
                    self.hdl_deposit(f"{rom_hdl}[{entry}]", data)


    def backdoor_fill_external_boot_flash(self, binfile, start_addr_offset, wanna_corrupt=False):

        def deposit_flash_32b(addr, data32):
            for i in range(4):
                hdl_path = f"ntb_top.qspi_flashes[4].u_macron_flash.mxArray[{addr+i}][7:0]"
                self.hdl_deposit(hdl_path, data32 >> i*8)

        with open(binfile, "rb") as f:
            B = f.read()
            addr = start_addr_offset
            while B:
                if len(B) >= 4:
                    data32 = B[:4]
                    B = B[4:]
                else:
                    data32 = B
                    B = []
                data32 = int.from_bytes(data32, 'little')
                if wanna_corrupt:
                    data32 += 1
                deposit_flash_32b(addr, data32)
                addr += 4


    def backdoor_init_external_boot_flash(self, ledger_binfile, run_binfile, corrupt_img_a=False, corrupt_img_b=False):
        if Helper.target in ["simv_top", "simv_fpga", "simv_gate","simv_synth"]:
            if not os.path.exists(ledger_binfile):
                raise Exception(f"{ledger_binfile} No such ledger file")
            
            if not os.path.exists(run_binfile):
                raise Exception(f"{run_binfile} No such fmc file")

            self.backdoor_fill_external_boot_flash(ledger_binfile, start_addr_offset=0)
            self.backdoor_fill_external_boot_flash(run_binfile, start_addr_offset=4096, wanna_corrupt=corrupt_img_a)
            self.backdoor_fill_external_boot_flash(run_binfile, start_addr_offset=1028*1024, wanna_corrupt=corrupt_img_b)
        else:
            self.pplatform_unsupport("backdoor_init_external_boot_flash")


    def backdoor_init_puf_ram(self, puf_ram_file, is_debug=False):
        if Helper.target in ["simv_top", "simv_fpga", "simv_gate","simv_synth"]:
            if not os.path.exists(puf_ram_file):
                self.pfatal(f"{puf_ram_file} No such file")

            puf_sram_hdl = f"{self.__fsp.hdl_root}.u_comp.u_puf.u_NOSCAN_prod_sram_wrapper.u_puf_prod_sram.M"
            if is_debug:
                puf_sram_hdl = f"{self.__fsp.hdl_root}.u_comp.u_puf.u_puf_debug_sram.M"
            with open(puf_ram_file, "r") as f:
                for row, data in enumerate(f.readlines()):
                    self.hdl_deposit(f"{puf_sram_hdl}[{row}]", int(data.strip(), 16))
        else:
            self.pplatform_unsupport("backdoor_init_puf_ram")


    def generate_boot_fuse_image(self, burn_fuse_opt):
        if not isinstance(burn_fuse_opt, dict):
            helper.pfatal(f"burn_fuse_opt should be a dict, 'opt_xx':1, 'opt_yy':0, ...]")
        
        fuse_cfg = "fuse_cfg"
        with open(f"{fuse_cfg}.pm", 'w') as f:
            fuse_opts = '\n'.join([f'   " -fuse_name {k} -fuse_value {hex(v)} ",' for k, v in burn_fuse_opt.items()])
            txt = \
f"""
@bootrom_patch_config = (
    {{
        'input_type' => 1,
        'patch_unit' => fsp,
        'record_type' => 0,
        'crc_type' => disable,
        'ecc_error' => disable,
        'patch_info' => [
            ["priv_jump",0x00001080,0xabcd1234]
        ]
    }}
);

@iff_patch_config = (
{fuse_opts}
);
"""
            f.write(txt)
        cmd = ["nvrun", "gen_brom_nop_block_index", "-pj", "sr01"]
        if hasattr(self, 'replace_brom'):
            cmd += ["-patch_loc_path", f"fsp={self.replace_brom}/patch_loc.txt"]
        subprocess.call(cmd)
        subprocess.call(f"nvrun gen_patch_record -cfg {fuse_cfg}.pm -en_fi -pj sr01 -nop_offset_file fsp=fsp_nop_offset_file -py".split(' '))
        return f"{fuse_cfg}.image", f"{fuse_cfg}_bootrom_patch_config.py"


    def get_dmem_bytes(self, dmem_dump_txt):
        binf = "dmem.bin"
        with open(dmem_dump_txt, 'r') as rf:
            rtxt = rf.read()
            rtxt = re.sub("DMEM:", "", rtxt)
            rtxt = re.sub("@[0-9a-z]+\n", "", rtxt).strip()
            with open("dmem.txt", 'w') as wf:
                wf.write(rtxt)
            subprocess.call(f"cat dmem.txt | xxd -r -p > {binf}", shell=True)
            subprocess.call("rm dmem.txt", shell=True)

        with open(binf, 'rb') as f:
            ans = f.read()

        return ans, binf


    def fuse_attestation_init(self, keystore_bin):
        if not os.path.exists(keystore_bin):
            self.pfatal(f"{keystore_bin} No such file")

        def row_translate(row):
            macro = int(row // 256)
            entry = row % 256
            return macro, entry
        
        def place_row_data(row, int32):
            macro, entry = row_translate(row)
            b32 = f"{int32:032b}"
            b_offset = entry * 32
            for n, b in enumerate(b32):
                hdl_path = f"{self.sys0_alias}.u_l1_cluster.u_NV_fuse.u_fuse_macro_wrap.u_fuse_macro_{macro}.fuse_data[{b_offset+31-n}]"
                self.hdl_deposit(hdl_path, int(b, 2))

        def place_section_at_row(row, section):
            for i in range(0, len(section), 4):
                int32 = int.from_bytes(section[i:i+4], 'little')
                place_row_data(row + int(i//4), int32)

        with open(keystore_bin, 'rb') as f:
            b = f.read()

            # refer section info at //hw/doc/mmplex/peregrine/3.0/arch/Metadata/BR/SR01_rot_keys.xlsx
            fuse_IV_offset = 209
            fuse_IV_size = int((96+32)//8)
            fuse_IV = b[fuse_IV_offset*4: fuse_IV_offset*4+fuse_IV_size*4]
            fuse_IV_section = [fuse_IV[i: i+fuse_IV_size] for i in range(0, fuse_IV_size*4, fuse_IV_size)]

            IK_PVT_offset = 225
            IK_PVT_size = int((384+128)//8)
            IK_PVT = b[IK_PVT_offset*4: IK_PVT_offset*4+IK_PVT_size]

            KEK_offset = 241
            KEK_size = int((256+128)//8)
            KEK = b[KEK_offset*4: KEK_offset*4+KEK_size]

            UDS_KDK_offset = 253
            UDS_KDK_size = int((256+128)//8)
            UDS_KDK = b[UDS_KDK_offset*4: UDS_KDK_offset*4+UDS_KDK_size]

            PDUK_offset = 265
            PDUK_size = int((256+128)//8)
            PDUK = b[PDUK_offset*4: PDUK_offset*4+PDUK_size]

            PMUK_offset = 277
            PMUK_size = int((256+128)//8)
            PMUK = b[PMUK_offset*4: PMUK_offset*4+PMUK_size]

            PUF_AC_offset = 289
            PUF_AC_size = int((6816+32)//8)
            PUF_AC = b[PUF_AC_offset*4: PUF_AC_offset*4+PUF_AC_size]

            # refer row info at //hw/doc/mmplex/peregrine/3.0/arch/Metadata/BR/SR01_rot_keys.xlsx
            # refer fsp_start_row info at /home/ip/nvmsoc/socip/fuse/2.1/68694234/ip/socd/fuse/2.1/vmod/fuse/xlitter/NV_FUSE_info.tcl
            fsp_start_row = 504
            fuse_IV_row = fsp_start_row + fuse_IV_offset
            IK_PVT_row = fsp_start_row + IK_PVT_offset
            KEK_row = fsp_start_row + KEK_offset
            UDS_KDK_row = fsp_start_row + UDS_KDK_offset
            PDUK_row = fsp_start_row + PDUK_offset
            PMUK_row = fsp_start_row + PMUK_offset
            PUF_AC_row = fsp_start_row + PUF_AC_offset

            place_section_at_row(fuse_IV_row, fuse_IV)
            place_section_at_row(IK_PVT_row, IK_PVT)
            place_section_at_row(KEK_row, KEK)
            place_section_at_row(UDS_KDK_row, UDS_KDK)
            place_section_at_row(PDUK_row, PDUK)
            place_section_at_row(PMUK_row, PMUK)
            place_section_at_row(PUF_AC_row, PUF_AC)


    def generate_boot_image(self, is_mfg=False, is_attestation=False, is_fwhasing=False, opt_secure_fsp_debug_dis=0, opt_production_mode=0):
        import sys
        sys.path.append(os.environ['NVBUILD_PY_LIB'])
        import nvbuildutils
        nvbuild = nvbuildutils.NVBuild()
        udir = f"{os.path.abspath(nvbuild.get_source_dir(''))}/erot_verif/stand_sim/top/tests/py/ucode"
        cmd = f"nvrun {udir}/gcc.py -m encrypted"
        if is_mfg:
            cmd = f"{cmd} --mfg"
        if is_attestation:
            cmd = f"{cmd} --attestation"
        if is_fwhasing:
            cmd = f"{cmd} --fwhashing"
        cmd = f"{cmd} --opt_secure_fsp_debug_dis {opt_secure_fsp_debug_dis} --opt_production_mode {opt_production_mode}"
        os.system(cmd)
        return os.path.abspath("build")


