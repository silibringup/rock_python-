#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import *
#This test is for csr condition coverage: when blk lock set to 1, access blf regs with one-hot data

with Test(sys.argv) as t:
    def parse_args():
        t.parser.add_argument("--Fabric", action='store', help="", default='L1')
        opts, unknown = t.parser.parse_known_args(sys.argv[1:])
        return opts

    L1_FABRIC_TARGET = [
        {'name' : 'l1_csr',                     'CTL' : erot.L1_CSR.L1_CSR_BLF_CTL_0,                     'WRITE' : erot.L1_CSR.L1_CSR_BLF_WRITE_CTL_0,                     'READ' : erot.L1_CSR.L1_CSR_BLF_READ_CTL_0},
        {'name' : 'clock_vrefro_ctl',           'CTL' : erot.L1_CSR.CLOCK_VREFRO_CTL_BLF_CTL_0,           'WRITE' : erot.L1_CSR.CLOCK_VREFRO_CTL_BLF_WRITE_CTL_0,           'READ' : erot.L1_CSR.CLOCK_VREFRO_CTL_BLF_READ_CTL_0},
        {'name' : 'clock_sys_ctl',              'CTL' : erot.L1_CSR.CLOCK_SYS_CTL_BLF_CTL_0,              'WRITE' : erot.L1_CSR.CLOCK_SYS_CTL_BLF_WRITE_CTL_0,              'READ' : erot.L1_CSR.CLOCK_SYS_CTL_BLF_READ_CTL_0},
        {'name' : 'clock_io_ctl',               'CTL' : erot.L1_CSR.CLOCK_IO_CTL_BLF_CTL_0,               'WRITE' : erot.L1_CSR.CLOCK_IO_CTL_BLF_WRITE_CTL_0,               'READ' : erot.L1_CSR.CLOCK_IO_CTL_BLF_READ_CTL_0},
        {'name' : 'clock_status',               'CTL' : erot.L1_CSR.CLOCK_STATUS_BLF_CTL_0,               'WRITE' : erot.L1_CSR.CLOCK_STATUS_BLF_WRITE_CTL_0,               'READ' : erot.L1_CSR.CLOCK_STATUS_BLF_READ_CTL_0},
        {'name' : 'clock_cmn_pad_ctl',          'CTL' : erot.L1_CSR.CLOCK_CMN_PAD_CTL_BLF_CTL_0,          'WRITE' : erot.L1_CSR.CLOCK_CMN_PAD_CTL_BLF_WRITE_CTL_0,          'READ' : erot.L1_CSR.CLOCK_CMN_PAD_CTL_BLF_READ_CTL_0},
        {'name' : 'clock_podvmon',              'CTL' : erot.L1_CSR.CLOCK_PODVMON_BLF_CTL_0,              'WRITE' : erot.L1_CSR.CLOCK_PODVMON_BLF_WRITE_CTL_0,              'READ' : erot.L1_CSR.CLOCK_PODVMON_BLF_READ_CTL_0},
        {'name' : 'clock_fmon',                 'CTL' : erot.L1_CSR.CLOCK_FMON_BLF_CTL_0,                 'WRITE' : erot.L1_CSR.CLOCK_FMON_BLF_WRITE_CTL_0,                 'READ' : erot.L1_CSR.CLOCK_FMON_BLF_READ_CTL_0},
        {'name' : 'boot_qspi_core',             'CTL' : erot.L1_CSR.BOOT_QSPI_CORE_BLF_CTL_0,             'WRITE' : erot.L1_CSR.BOOT_QSPI_CORE_BLF_WRITE_CTL_0,             'READ' : erot.L1_CSR.BOOT_QSPI_CORE_BLF_READ_CTL_0},
        {'name' : 'boot_qspi_nv_prom_data',     'CTL' : erot.L1_CSR.BOOT_QSPI_NV_PROM_DATA_BLF_CTL_0,     'WRITE' : erot.L1_CSR.BOOT_QSPI_NV_PROM_DATA_BLF_WRITE_CTL_0,     'READ' : erot.L1_CSR.BOOT_QSPI_NV_PROM_DATA_BLF_READ_CTL_0},
        {'name' : 'boot_qspi_nv_prom_2_data',   'CTL' : erot.L1_CSR.BOOT_QSPI_NV_PROM_2_DATA_BLF_CTL_0,   'WRITE' : erot.L1_CSR.BOOT_QSPI_NV_PROM_2_DATA_BLF_WRITE_CTL_0,   'READ' : erot.L1_CSR.BOOT_QSPI_NV_PROM_2_DATA_BLF_READ_CTL_0},
        {'name' : 'fuse',                       'CTL' : erot.L1_CSR.FUSE_BLF_CTL_0,                       'WRITE' : erot.L1_CSR.FUSE_BLF_WRITE_CTL_0,                       'READ' : erot.L1_CSR.FUSE_BLF_READ_CTL_0},
        {'name' : 'jtag',                       'CTL' : erot.L1_CSR.JTAG_BLF_CTL_0,                       'WRITE' : erot.L1_CSR.JTAG_BLF_WRITE_CTL_0,                       'READ' : erot.L1_CSR.JTAG_BLF_READ_CTL_0},
        {'name' : 'mram_cfg',                   'CTL' : erot.L1_CSR.MRAM_CFG_BLF_CTL_0,                   'WRITE' : erot.L1_CSR.MRAM_CFG_BLF_WRITE_CTL_0,                   'READ' : erot.L1_CSR.MRAM_CFG_BLF_READ_CTL_0},
        {'name' : 'mram_tmc',                   'CTL' : erot.L1_CSR.MRAM_TMC_BLF_CTL_0,                   'WRITE' : erot.L1_CSR.MRAM_TMC_BLF_WRITE_CTL_0,                   'READ' : erot.L1_CSR.MRAM_TMC_BLF_READ_CTL_0},
        {'name' : 'mram_otp',                   'CTL' : erot.L1_CSR.MRAM_OTP_BLF_CTL_0,                   'WRITE' : erot.L1_CSR.MRAM_OTP_BLF_WRITE_CTL_0,                   'READ' : erot.L1_CSR.MRAM_OTP_BLF_READ_CTL_0},
        {'name' : 'mram_mtp',                   'CTL' : erot.L1_CSR.MRAM_MTP_BLF_CTL_0,                   'WRITE' : erot.L1_CSR.MRAM_MTP_BLF_WRITE_CTL_0,                   'READ' : erot.L1_CSR.MRAM_MTP_BLF_READ_CTL_0},
        {'name' : 'mram_mtpr',                  'CTL' : erot.L1_CSR.MRAM_MTPR_BLF_CTL_0,                  'WRITE' : erot.L1_CSR.MRAM_MTPR_BLF_WRITE_CTL_0,                  'READ' : erot.L1_CSR.MRAM_MTPR_BLF_READ_CTL_0},
        {'name' : 'oobhub',                     'CTL' : erot.L1_CSR.OOBHUB_BLF_CTL_0,                     'WRITE' : erot.L1_CSR.OOBHUB_BLF_WRITE_CTL_0,                     'READ' : erot.L1_CSR.OOBHUB_BLF_READ_CTL_0},
        {'name' : 'puf_dbg',                    'CTL' : erot.L1_CSR.PUF_DBG_BLF_CTL_0,                    'WRITE' : erot.L1_CSR.PUF_DBG_BLF_WRITE_CTL_0,                    'READ' : erot.L1_CSR.PUF_DBG_BLF_READ_CTL_0},
        {'name' : 'qspi0_core',                 'CTL' : erot.L1_CSR.QSPI0_CORE_BLF_CTL_0,                 'WRITE' : erot.L1_CSR.QSPI0_CORE_BLF_WRITE_CTL_0,                 'READ' : erot.L1_CSR.QSPI0_CORE_BLF_READ_CTL_0},
        {'name' : 'qspi0_nv_prom_data',         'CTL' : erot.L1_CSR.QSPI0_NV_PROM_DATA_BLF_CTL_0,         'WRITE' : erot.L1_CSR.QSPI0_NV_PROM_DATA_BLF_WRITE_CTL_0,         'READ' : erot.L1_CSR.QSPI0_NV_PROM_DATA_BLF_READ_CTL_0},
        {'name' : 'qspi0_nv_prom_2_data',       'CTL' : erot.L1_CSR.QSPI0_NV_PROM_2_DATA_BLF_CTL_0,       'WRITE' : erot.L1_CSR.QSPI0_NV_PROM_2_DATA_BLF_WRITE_CTL_0,       'READ' : erot.L1_CSR.QSPI0_NV_PROM_2_DATA_BLF_READ_CTL_0},
        {'name' : 'qspi1_core',                 'CTL' : erot.L1_CSR.QSPI1_CORE_BLF_CTL_0,                 'WRITE' : erot.L1_CSR.QSPI1_CORE_BLF_WRITE_CTL_0,                 'READ' : erot.L1_CSR.QSPI1_CORE_BLF_READ_CTL_0},
        {'name' : 'qspi1_nv_prom_data',         'CTL' : erot.L1_CSR.QSPI1_NV_PROM_DATA_BLF_CTL_0,         'WRITE' : erot.L1_CSR.QSPI1_NV_PROM_DATA_BLF_WRITE_CTL_0,         'READ' : erot.L1_CSR.QSPI1_NV_PROM_DATA_BLF_READ_CTL_0},
        {'name' : 'qspi1_nv_prom_2_data',       'CTL' : erot.L1_CSR.QSPI1_NV_PROM_2_DATA_BLF_CTL_0,       'WRITE' : erot.L1_CSR.QSPI1_NV_PROM_2_DATA_BLF_WRITE_CTL_0,       'READ' : erot.L1_CSR.QSPI1_NV_PROM_2_DATA_BLF_READ_CTL_0},
        {'name' : 'reset_reg',                  'CTL' : erot.L1_CSR.RESET_REG_BLF_CTL_0,                  'WRITE' : erot.L1_CSR.RESET_REG_BLF_WRITE_CTL_0,                  'READ' : erot.L1_CSR.RESET_REG_BLF_READ_CTL_0},
        {'name' : 'reset_status',               'CTL' : erot.L1_CSR.RESET_STATUS_BLF_CTL_0,               'WRITE' : erot.L1_CSR.RESET_STATUS_BLF_WRITE_CTL_0,               'READ' : erot.L1_CSR.RESET_STATUS_BLF_READ_CTL_0},
        {'name' : 'rts',                        'CTL' : erot.L1_CSR.RTS_BLF_CTL_0,                        'WRITE' : erot.L1_CSR.RTS_BLF_WRITE_CTL_0,                        'READ' : erot.L1_CSR.RTS_BLF_READ_CTL_0},
        {'name' : 'spi_mon0',                   'CTL' : erot.L1_CSR.SPI_MON0_BLF_CTL_0,                   'WRITE' : erot.L1_CSR.SPI_MON0_BLF_WRITE_CTL_0,                   'READ' : erot.L1_CSR.SPI_MON0_BLF_READ_CTL_0},
        {'name' : 'spi_mon1',                   'CTL' : erot.L1_CSR.SPI_MON1_BLF_CTL_0,                   'WRITE' : erot.L1_CSR.SPI_MON1_BLF_WRITE_CTL_0,                   'READ' : erot.L1_CSR.SPI_MON1_BLF_READ_CTL_0},
        {'name' : 'nv_pmc',                     'CTL' : erot.L1_CSR.NV_PMC_BLF_CTL_0,                     'WRITE' : erot.L1_CSR.NV_PMC_BLF_WRITE_CTL_0,                     'READ' : erot.L1_CSR.NV_PMC_BLF_READ_CTL_0},
        {'name' : 'nv_pbus',                    'CTL' : erot.L1_CSR.NV_PBUS_BLF_CTL_0,                    'WRITE' : erot.L1_CSR.NV_PBUS_BLF_WRITE_CTL_0,                    'READ' : erot.L1_CSR.NV_PBUS_BLF_READ_CTL_0},
        {'name' : 'nv_ptop',                    'CTL' : erot.L1_CSR.NV_PTOP_BLF_CTL_0,                    'WRITE' : erot.L1_CSR.NV_PTOP_BLF_WRITE_CTL_0,                    'READ' : erot.L1_CSR.NV_PTOP_BLF_READ_CTL_0},
        {'name' : 'therm',                      'CTL' : erot.L1_CSR.THERM_BLF_CTL_0,                      'WRITE' : erot.L1_CSR.THERM_BLF_WRITE_CTL_0,                      'READ' : erot.L1_CSR.THERM_BLF_READ_CTL_0},
    ]

    L2_FABRIC_TARGET = [
        {'name' : 'l2_csr',             'CTL' : erot.L2_CSR.L2_CSR_BLF_CTL_0,               'WRITE' : erot.L2_CSR.L2_CSR_BLF_WRITE_CTL_0,           'READ' : erot.L2_CSR.L2_CSR_BLF_READ_CTL_0},
        {'name' : 'gpio_cmn',           'CTL' : erot.L2_CSR.GPIO_CMN_BLF_CTL_0,             'WRITE' : erot.L2_CSR.GPIO_CMN_BLF_WRITE_CTL_0,         'READ' : erot.L2_CSR.GPIO_CMN_BLF_READ_CTL_0},
        {'name' : 'gpio_vm1',           'CTL' : erot.L2_CSR.GPIO_VM1_BLF_CTL_0,             'WRITE' : erot.L2_CSR.GPIO_VM1_BLF_WRITE_CTL_0,         'READ' : erot.L2_CSR.GPIO_VM1_BLF_READ_CTL_0},
        {'name' : 'gpio_vm2',           'CTL' : erot.L2_CSR.GPIO_VM2_BLF_CTL_0,             'WRITE' : erot.L2_CSR.GPIO_VM2_BLF_WRITE_CTL_0,         'READ' : erot.L2_CSR.GPIO_VM2_BLF_READ_CTL_0},
        {'name' : 'gpio_vm3',           'CTL' : erot.L2_CSR.GPIO_VM3_BLF_CTL_0,             'WRITE' : erot.L2_CSR.GPIO_VM3_BLF_WRITE_CTL_0,         'READ' : erot.L2_CSR.GPIO_VM3_BLF_READ_CTL_0},
        {'name' : 'gpio_vm4',           'CTL' : erot.L2_CSR.GPIO_VM4_BLF_CTL_0,             'WRITE' : erot.L2_CSR.GPIO_VM4_BLF_WRITE_CTL_0,         'READ' : erot.L2_CSR.GPIO_VM4_BLF_READ_CTL_0},
        {'name' : 'gpio_vm5',           'CTL' : erot.L2_CSR.GPIO_VM5_BLF_CTL_0,             'WRITE' : erot.L2_CSR.GPIO_VM5_BLF_WRITE_CTL_0,         'READ' : erot.L2_CSR.GPIO_VM5_BLF_READ_CTL_0},
        {'name' : 'gpio_vm6',           'CTL' : erot.L2_CSR.GPIO_VM6_BLF_CTL_0,             'WRITE' : erot.L2_CSR.GPIO_VM6_BLF_WRITE_CTL_0,         'READ' : erot.L2_CSR.GPIO_VM6_BLF_READ_CTL_0},
        {'name' : 'gpio_vm7',           'CTL' : erot.L2_CSR.GPIO_VM7_BLF_CTL_0,             'WRITE' : erot.L2_CSR.GPIO_VM7_BLF_WRITE_CTL_0,         'READ' : erot.L2_CSR.GPIO_VM7_BLF_READ_CTL_0},
        {'name' : 'gpio_vm8',           'CTL' : erot.L2_CSR.GPIO_VM8_BLF_CTL_0,             'WRITE' : erot.L2_CSR.GPIO_VM8_BLF_WRITE_CTL_0,         'READ' : erot.L2_CSR.GPIO_VM8_BLF_READ_CTL_0},
        {'name' : 'i2c_ib0',            'CTL' : erot.L2_CSR.I2C_IB0_BLF_CTL_0,              'WRITE' : erot.L2_CSR.I2C_IB0_BLF_WRITE_CTL_0,          'READ' : erot.L2_CSR.I2C_IB0_BLF_READ_CTL_0},
        {'name' : 'i2c_ib1',            'CTL' : erot.L2_CSR.I2C_IB1_BLF_CTL_0,              'WRITE' : erot.L2_CSR.I2C_IB1_BLF_WRITE_CTL_0,          'READ' : erot.L2_CSR.I2C_IB1_BLF_READ_CTL_0},
        {'name' : 'i3c_ib0',            'CTL' : erot.L2_CSR.I3C_IB0_BLF_CTL_0,              'WRITE' : erot.L2_CSR.I3C_IB0_BLF_WRITE_CTL_0,          'READ' : erot.L2_CSR.I3C_IB0_BLF_READ_CTL_0},
        {'name' : 'i3c_ib1',            'CTL' : erot.L2_CSR.I3C_IB1_BLF_CTL_0,              'WRITE' : erot.L2_CSR.I3C_IB1_BLF_WRITE_CTL_0,          'READ' : erot.L2_CSR.I3C_IB1_BLF_READ_CTL_0},
        {'name' : 'io_expander',        'CTL' : erot.L2_CSR.IO_EXPANDER_BLF_CTL_0,          'WRITE' : erot.L2_CSR.IO_EXPANDER_BLF_WRITE_CTL_0,      'READ' : erot.L2_CSR.IO_EXPANDER_BLF_READ_CTL_0},
        {'name' : 'fsp',                'CTL' : erot.L2_CSR.FSP_BLF_CTL_0,                  'WRITE' : erot.L2_CSR.FSP_BLF_WRITE_CTL_0,              'READ' : erot.L2_CSR.FSP_BLF_READ_CTL_0},
        {'name' : 'oobhub_spi',         'CTL' : erot.L2_CSR.OOBHUB_SPI_BLF_CTL_0,           'WRITE' : erot.L2_CSR.OOBHUB_SPI_BLF_WRITE_CTL_0,       'READ' : erot.L2_CSR.OOBHUB_SPI_BLF_READ_CTL_0},
        {'name' : 'padctrl_e',          'CTL' : erot.L2_CSR.PADCTRL_E_BLF_CTL_0,            'WRITE' : erot.L2_CSR.PADCTRL_E_BLF_WRITE_CTL_0,        'READ' : erot.L2_CSR.PADCTRL_E_BLF_READ_CTL_0},
        {'name' : 'padctrl_n',          'CTL' : erot.L2_CSR.PADCTRL_N_BLF_CTL_0,            'WRITE' : erot.L2_CSR.PADCTRL_N_BLF_WRITE_CTL_0,        'READ' : erot.L2_CSR.PADCTRL_N_BLF_READ_CTL_0},
        {'name' : 'padctrl_s',          'CTL' : erot.L2_CSR.PADCTRL_S_BLF_CTL_0,            'WRITE' : erot.L2_CSR.PADCTRL_S_BLF_WRITE_CTL_0,        'READ' : erot.L2_CSR.PADCTRL_S_BLF_READ_CTL_0},
        {'name' : 'padctrl_w',          'CTL' : erot.L2_CSR.PADCTRL_W_BLF_CTL_0,            'WRITE' : erot.L2_CSR.PADCTRL_W_BLF_WRITE_CTL_0,        'READ' : erot.L2_CSR.PADCTRL_W_BLF_READ_CTL_0},
        {'name' : 'spi_ib0',            'CTL' : erot.L2_CSR.SPI_IB0_BLF_CTL_0,              'WRITE' : erot.L2_CSR.SPI_IB0_BLF_WRITE_CTL_0,          'READ' : erot.L2_CSR.SPI_IB0_BLF_READ_CTL_0},
        {'name' : 'spi_ib1',            'CTL' : erot.L2_CSR.SPI_IB1_BLF_CTL_0,              'WRITE' : erot.L2_CSR.SPI_IB1_BLF_WRITE_CTL_0,          'READ' : erot.L2_CSR.SPI_IB1_BLF_READ_CTL_0},
        {'name' : 'uart',               'CTL' : erot.L2_CSR.UART_BLF_CTL_0,                 'WRITE' : erot.L2_CSR.UART_BLF_WRITE_CTL_0,             'READ' : erot.L2_CSR.UART_BLF_READ_CTL_0},
    ]

    def write_and_read(reg, locked, write_value, exp_value):
        #reg.write(write_value)
        #WRITE will be blocked
        if helper.target in ["fpga", "simv_fpga"]:
            helper.j2h_write(reg.abs_addr, write_value)
            if(locked == 1):
                fpga_write_rdata = helper.j2h_read(reg.abs_addr)
                if(fpga_write_rdata == write_value):
                    helper.perror("write in data value match, it seems lock failed, exp: %x, act: %x" %(write_value, fpga_write_rdata))
                #if(fpga_wdata != 0xdead1001):
                #    helper.perror("write_rdata value mismatch, exp: %x, act: %x" %(0xdead1001, fpga_wdata))
            else:
                fpga_write_rdata = helper.j2h_read(reg.abs_addr)
                if(fpga_write_rdata != write_value):
                    helper.perror("write in data value mismatch, exp: %x, act: %x" %(write_value, fpga_write_rdata))
            #READ is allowed
            fpga_rdata = helper.j2h_read(reg.abs_addr)
            if(fpga_rdata != exp_value):
                helper.perror("read_rdata value mismatch, exp: %x, act: %x" %(exp_value, fpga_rdata))
        else:
            addr_list = []
            data_list = []
            cmd_list = []
            addr_list.append(reg.abs_addr)
            data_list.append(write_value)
            cmd_list.append(3)
            write_return_list = helper.burst_operation(addr_list, data_list, cmd_list, 2)
            write_rdata = write_return_list[0][0]
            write_resp_err = write_return_list[1][0]
            if(locked == 1):
                if(write_rdata != 0xdead1001):
                    helper.perror("write_rdata value mismatch, exp: %x, act: %x" %(0xdead1001, write_rdata))
                if(write_resp_err != 1):
                    helper.perror("write_resp_err value mismatch, exp: %x, act: %x" %(1, write_resp_err))
            else:
                #if(write_rdata != 0):
                    #helper.perror("write_rdata value mismatch, exp: %x, act: %x" %(0, write_rdata))
                if(write_resp_err != 0):
                    helper.perror("write_resp_err value mismatch, exp: %x, act: %x" %(0, write_resp_err))
            
            #READ is allowed
            cmd_list = []
            cmd_list.append(0)
            read_return_list = helper.burst_operation(addr_list, data_list, cmd_list, 2)
            read_rdata = read_return_list[0][0]
            read_resp_err = read_return_list[1][0]
            if(read_rdata != exp_value):
                helper.perror("read_rdata value mismatch, exp: %x, act: %x" %(exp_value, read_rdata))
            if(read_resp_err != 0):
                helper.perror("read_resp_err value mismatch, exp: %x, act: %x" %(0, read_resp_err))
    
    def noraml_case(target):
        #normal write and read before BLF lock
        helper.log("Write 0xffffffff to WRITE_CTL reg of %s" %(target['name']))
        write_and_read(target['WRITE'], 0, 0xffffffff, 0xffffffff)
        helper.log("Write 0xffffffff to READ_CTL reg of %s" %(target['name']))
        write_and_read(target['READ'], 0, 0xffffffff, 0xffffffff)
        helper.log("Write 0x30000 to CTL reg of %s" %(target['name']))
        write_and_read(target['CTL'], 0, 0x30000, 0x30000)

    def test_blf_lock(target):
        #set blf lock bit to 1
        if helper.target in ["fpga", "simv_fpga"]:
            target['CTL'].debug_write(0x80000000)
        else:
            target['CTL'].write(0x80000000)
        helper.log("BLF locked")
        helper.log("Write 0x30000 to CTL reg of %s" %(target['name']))
        write_and_read(target['CTL'], 1, 0x30000, 0x80000000)
        helper.log("Write 0xffffffff to WRITE_CTL reg of %s" %(target['name']))
        write_and_read(target['WRITE'], 1, 0, 0xffffffff)
        helper.log("Write 0xffffffff to READ_CTL reg of %s" %(target['name']))
        write_and_read(target['READ'], 1, 0, 0xffffffff)

   
    options = parse_args()
    if helper.target in ["fpga", "simv_fpga"]:
        #jtag unlock
        helper.log("Test start")
        helper.wait_sim_time("us", 50)
        helper.hdl_force('ntb_top.u_nv_fpga_dut.u_nv_top_fpga.u_nv_top_wrapper.u_nv_top.nvjtag_sel', 1)

        helper.jtag.Reset(0)
        helper.jtag.DRScan(100, hex(0x0)) #add some delay as jtag only work when nvjtag_sel stable in real case
        helper.jtag.Reset(1)


        helper.pinfo(f'j2h_unlock sequence start')
        helper.j2h_unlock()
        helper.pinfo(f'j2h_unlock sequence finish')

        helper.jtag.DRScan(100, hex(0x0)) #add some delay as jtag only work when nvjtag_sel stable in real case

    if(options.Fabric == 'L1'):
        for target in L1_FABRIC_TARGET:
            noraml_case(target)
        for target in L1_FABRIC_TARGET:
            test_blf_lock(target)
    elif(options.Fabric == 'L2'):
        for target in L2_FABRIC_TARGET:
            noraml_case(target)
        for target in L2_FABRIC_TARGET:
            test_blf_lock(target)
    else:
        helper.perror("Wrong --Fabric %s" % options.monitor)

    helper.log("Test Finish")
