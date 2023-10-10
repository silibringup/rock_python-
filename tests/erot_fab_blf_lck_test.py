#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import *

with Test(sys.argv) as t:

    def parse_args():
        t.parser.add_argument("--IP", action='store', help="Test Fabric BLF locking reg", default='L1_ALL')
        opts, unknown = t.parser.parse_known_args(sys.argv[1:])
        return opts

    L1_FABRIC_TARGET = [
        #part1, 0
        {'name' : 'l1_csr',                     'CTL' : erot.L1_CSR.L1_CSR_BLF_CTL_0,                     'WRITE' : erot.L1_CSR.L1_CSR_BLF_WRITE_CTL_0,                     'READ' : erot.L1_CSR.L1_CSR_BLF_READ_CTL_0},
        #part2, 1-7
        {'name' : 'clock_vrefro_ctl',           'CTL' : erot.L1_CSR.CLOCK_VREFRO_CTL_BLF_CTL_0,           'WRITE' : erot.L1_CSR.CLOCK_VREFRO_CTL_BLF_WRITE_CTL_0,           'READ' : erot.L1_CSR.CLOCK_VREFRO_CTL_BLF_READ_CTL_0},
        {'name' : 'clock_sys_ctl',              'CTL' : erot.L1_CSR.CLOCK_SYS_CTL_BLF_CTL_0,              'WRITE' : erot.L1_CSR.CLOCK_SYS_CTL_BLF_WRITE_CTL_0,              'READ' : erot.L1_CSR.CLOCK_SYS_CTL_BLF_READ_CTL_0},
        {'name' : 'clock_io_ctl',               'CTL' : erot.L1_CSR.CLOCK_IO_CTL_BLF_CTL_0,               'WRITE' : erot.L1_CSR.CLOCK_IO_CTL_BLF_WRITE_CTL_0,               'READ' : erot.L1_CSR.CLOCK_IO_CTL_BLF_READ_CTL_0},
        {'name' : 'clock_status',               'CTL' : erot.L1_CSR.CLOCK_STATUS_BLF_CTL_0,               'WRITE' : erot.L1_CSR.CLOCK_STATUS_BLF_WRITE_CTL_0,               'READ' : erot.L1_CSR.CLOCK_STATUS_BLF_READ_CTL_0},
        {'name' : 'clock_cmn_pad_ctl',          'CTL' : erot.L1_CSR.CLOCK_CMN_PAD_CTL_BLF_CTL_0,          'WRITE' : erot.L1_CSR.CLOCK_CMN_PAD_CTL_BLF_WRITE_CTL_0,          'READ' : erot.L1_CSR.CLOCK_CMN_PAD_CTL_BLF_READ_CTL_0},
        {'name' : 'clock_podvmon',              'CTL' : erot.L1_CSR.CLOCK_PODVMON_BLF_CTL_0,              'WRITE' : erot.L1_CSR.CLOCK_PODVMON_BLF_WRITE_CTL_0,              'READ' : erot.L1_CSR.CLOCK_PODVMON_BLF_READ_CTL_0},
        {'name' : 'clock_fmon',                 'CTL' : erot.L1_CSR.CLOCK_FMON_BLF_CTL_0,                 'WRITE' : erot.L1_CSR.CLOCK_FMON_BLF_WRITE_CTL_0,                 'READ' : erot.L1_CSR.CLOCK_FMON_BLF_READ_CTL_0},
        #part3, 8-10
        {'name' : 'boot_qspi_core',             'CTL' : erot.L1_CSR.BOOT_QSPI_CORE_BLF_CTL_0,             'WRITE' : erot.L1_CSR.BOOT_QSPI_CORE_BLF_WRITE_CTL_0,             'READ' : erot.L1_CSR.BOOT_QSPI_CORE_BLF_READ_CTL_0},
        {'name' : 'boot_qspi_nv_prom_data',     'CTL' : erot.L1_CSR.BOOT_QSPI_NV_PROM_DATA_BLF_CTL_0,     'WRITE' : erot.L1_CSR.BOOT_QSPI_NV_PROM_DATA_BLF_WRITE_CTL_0,     'READ' : erot.L1_CSR.BOOT_QSPI_NV_PROM_DATA_BLF_READ_CTL_0},
        {'name' : 'boot_qspi_nv_prom_2_data',   'CTL' : erot.L1_CSR.BOOT_QSPI_NV_PROM_2_DATA_BLF_CTL_0,   'WRITE' : erot.L1_CSR.BOOT_QSPI_NV_PROM_2_DATA_BLF_WRITE_CTL_0,   'READ' : erot.L1_CSR.BOOT_QSPI_NV_PROM_2_DATA_BLF_READ_CTL_0},
        #part4, 11
        {'name' : 'fuse',                       'CTL' : erot.L1_CSR.FUSE_BLF_CTL_0,                       'WRITE' : erot.L1_CSR.FUSE_BLF_WRITE_CTL_0,                       'READ' : erot.L1_CSR.FUSE_BLF_READ_CTL_0},
        #part5, 12
        {'name' : 'jtag',                       'CTL' : erot.L1_CSR.JTAG_BLF_CTL_0,                       'WRITE' : erot.L1_CSR.JTAG_BLF_WRITE_CTL_0,                       'READ' : erot.L1_CSR.JTAG_BLF_READ_CTL_0},
        #part6, 13-17
        {'name' : 'mram_cfg',                   'CTL' : erot.L1_CSR.MRAM_CFG_BLF_CTL_0,                   'WRITE' : erot.L1_CSR.MRAM_CFG_BLF_WRITE_CTL_0,                   'READ' : erot.L1_CSR.MRAM_CFG_BLF_READ_CTL_0},
        {'name' : 'mram_tmc',                   'CTL' : erot.L1_CSR.MRAM_TMC_BLF_CTL_0,                   'WRITE' : erot.L1_CSR.MRAM_TMC_BLF_WRITE_CTL_0,                   'READ' : erot.L1_CSR.MRAM_TMC_BLF_READ_CTL_0},
        {'name' : 'mram_otp',                   'CTL' : erot.L1_CSR.MRAM_OTP_BLF_CTL_0,                   'WRITE' : erot.L1_CSR.MRAM_OTP_BLF_WRITE_CTL_0,                   'READ' : erot.L1_CSR.MRAM_OTP_BLF_READ_CTL_0},
        {'name' : 'mram_mtp',                   'CTL' : erot.L1_CSR.MRAM_MTP_BLF_CTL_0,                   'WRITE' : erot.L1_CSR.MRAM_MTP_BLF_WRITE_CTL_0,                   'READ' : erot.L1_CSR.MRAM_MTP_BLF_READ_CTL_0},
        {'name' : 'mram_mtpr',                  'CTL' : erot.L1_CSR.MRAM_MTPR_BLF_CTL_0,                  'WRITE' : erot.L1_CSR.MRAM_MTPR_BLF_WRITE_CTL_0,                  'READ' : erot.L1_CSR.MRAM_MTPR_BLF_READ_CTL_0},
        #part7, 18
        {'name' : 'oobhub',                     'CTL' : erot.L1_CSR.OOBHUB_BLF_CTL_0,                     'WRITE' : erot.L1_CSR.OOBHUB_BLF_WRITE_CTL_0,                     'READ' : erot.L1_CSR.OOBHUB_BLF_READ_CTL_0},
        #part8, 19
        {'name' : 'puf_dbg',                    'CTL' : erot.L1_CSR.PUF_DBG_BLF_CTL_0,                    'WRITE' : erot.L1_CSR.PUF_DBG_BLF_WRITE_CTL_0,                    'READ' : erot.L1_CSR.PUF_DBG_BLF_READ_CTL_0},
        #part9, 20-22
        {'name' : 'qspi0_core',                 'CTL' : erot.L1_CSR.QSPI0_CORE_BLF_CTL_0,                 'WRITE' : erot.L1_CSR.QSPI0_CORE_BLF_WRITE_CTL_0,                 'READ' : erot.L1_CSR.QSPI0_CORE_BLF_READ_CTL_0},
        {'name' : 'qspi0_nv_prom_data',         'CTL' : erot.L1_CSR.QSPI0_NV_PROM_DATA_BLF_CTL_0,         'WRITE' : erot.L1_CSR.QSPI0_NV_PROM_DATA_BLF_WRITE_CTL_0,         'READ' : erot.L1_CSR.QSPI0_NV_PROM_DATA_BLF_READ_CTL_0},
        {'name' : 'qspi0_nv_prom_2_data',       'CTL' : erot.L1_CSR.QSPI0_NV_PROM_2_DATA_BLF_CTL_0,       'WRITE' : erot.L1_CSR.QSPI0_NV_PROM_2_DATA_BLF_WRITE_CTL_0,       'READ' : erot.L1_CSR.QSPI0_NV_PROM_2_DATA_BLF_READ_CTL_0},
        #part10, 23-25
        {'name' : 'qspi1_core',                 'CTL' : erot.L1_CSR.QSPI1_CORE_BLF_CTL_0,                 'WRITE' : erot.L1_CSR.QSPI1_CORE_BLF_WRITE_CTL_0,                 'READ' : erot.L1_CSR.QSPI1_CORE_BLF_READ_CTL_0},
        {'name' : 'qspi1_nv_prom_data',         'CTL' : erot.L1_CSR.QSPI1_NV_PROM_DATA_BLF_CTL_0,         'WRITE' : erot.L1_CSR.QSPI1_NV_PROM_DATA_BLF_WRITE_CTL_0,         'READ' : erot.L1_CSR.QSPI1_NV_PROM_DATA_BLF_READ_CTL_0},
        {'name' : 'qspi1_nv_prom_2_data',       'CTL' : erot.L1_CSR.QSPI1_NV_PROM_2_DATA_BLF_CTL_0,       'WRITE' : erot.L1_CSR.QSPI1_NV_PROM_2_DATA_BLF_WRITE_CTL_0,       'READ' : erot.L1_CSR.QSPI1_NV_PROM_2_DATA_BLF_READ_CTL_0},
        #par11, 26-27
        {'name' : 'reset_reg',                  'CTL' : erot.L1_CSR.RESET_REG_BLF_CTL_0,                  'WRITE' : erot.L1_CSR.RESET_REG_BLF_WRITE_CTL_0,                  'READ' : erot.L1_CSR.RESET_REG_BLF_READ_CTL_0},
        {'name' : 'reset_status',               'CTL' : erot.L1_CSR.RESET_STATUS_BLF_CTL_0,               'WRITE' : erot.L1_CSR.RESET_STATUS_BLF_WRITE_CTL_0,               'READ' : erot.L1_CSR.RESET_STATUS_BLF_READ_CTL_0},
        #part12, 28
        {'name' : 'rts',                        'CTL' : erot.L1_CSR.RTS_BLF_CTL_0,                        'WRITE' : erot.L1_CSR.RTS_BLF_WRITE_CTL_0,                        'READ' : erot.L1_CSR.RTS_BLF_READ_CTL_0},
        #part13, 29
        {'name' : 'spi_mon0',                   'CTL' : erot.L1_CSR.SPI_MON0_BLF_CTL_0,                   'WRITE' : erot.L1_CSR.SPI_MON0_BLF_WRITE_CTL_0,                   'READ' : erot.L1_CSR.SPI_MON0_BLF_READ_CTL_0},
        #part14, 30
        {'name' : 'spi_mon1',                   'CTL' : erot.L1_CSR.SPI_MON1_BLF_CTL_0,                   'WRITE' : erot.L1_CSR.SPI_MON1_BLF_WRITE_CTL_0,                   'READ' : erot.L1_CSR.SPI_MON1_BLF_READ_CTL_0},
        #part15, 31-33
        {'name' : 'nv_pmc',                     'CTL' : erot.L1_CSR.NV_PMC_BLF_CTL_0,                     'WRITE' : erot.L1_CSR.NV_PMC_BLF_WRITE_CTL_0,                     'READ' : erot.L1_CSR.NV_PMC_BLF_READ_CTL_0},
        {'name' : 'nv_pbus',                    'CTL' : erot.L1_CSR.NV_PBUS_BLF_CTL_0,                    'WRITE' : erot.L1_CSR.NV_PBUS_BLF_WRITE_CTL_0,                    'READ' : erot.L1_CSR.NV_PBUS_BLF_READ_CTL_0},
        {'name' : 'nv_ptop',                    'CTL' : erot.L1_CSR.NV_PTOP_BLF_CTL_0,                    'WRITE' : erot.L1_CSR.NV_PTOP_BLF_WRITE_CTL_0,                    'READ' : erot.L1_CSR.NV_PTOP_BLF_READ_CTL_0},
        #part16, 34
        {'name' : 'therm',                      'CTL' : erot.L1_CSR.THERM_BLF_CTL_0,                      'WRITE' : erot.L1_CSR.THERM_BLF_WRITE_CTL_0,                      'READ' : erot.L1_CSR.THERM_BLF_READ_CTL_0},
    ]

    L2_FABRIC_TARGET = [
        #part1, 0
        {'name' : 'l2_csr',             'CTL' : erot.L2_CSR.L2_CSR_BLF_CTL_0,               'WRITE' : erot.L2_CSR.L2_CSR_BLF_WRITE_CTL_0,           'READ' : erot.L2_CSR.L2_CSR_BLF_READ_CTL_0},
        #part2, 1-4
        {'name' : 'gpio_cmn',           'CTL' : erot.L2_CSR.GPIO_CMN_BLF_CTL_0,             'WRITE' : erot.L2_CSR.GPIO_CMN_BLF_WRITE_CTL_0,         'READ' : erot.L2_CSR.GPIO_CMN_BLF_READ_CTL_0},
        {'name' : 'gpio_vm1',           'CTL' : erot.L2_CSR.GPIO_VM1_BLF_CTL_0,             'WRITE' : erot.L2_CSR.GPIO_VM1_BLF_WRITE_CTL_0,         'READ' : erot.L2_CSR.GPIO_VM1_BLF_READ_CTL_0},
        {'name' : 'gpio_vm2',           'CTL' : erot.L2_CSR.GPIO_VM2_BLF_CTL_0,             'WRITE' : erot.L2_CSR.GPIO_VM2_BLF_WRITE_CTL_0,         'READ' : erot.L2_CSR.GPIO_VM2_BLF_READ_CTL_0},
        {'name' : 'gpio_vm3',           'CTL' : erot.L2_CSR.GPIO_VM3_BLF_CTL_0,             'WRITE' : erot.L2_CSR.GPIO_VM3_BLF_WRITE_CTL_0,         'READ' : erot.L2_CSR.GPIO_VM3_BLF_READ_CTL_0},
        #part3, 5-9
        {'name' : 'gpio_vm4',           'CTL' : erot.L2_CSR.GPIO_VM4_BLF_CTL_0,             'WRITE' : erot.L2_CSR.GPIO_VM4_BLF_WRITE_CTL_0,         'READ' : erot.L2_CSR.GPIO_VM4_BLF_READ_CTL_0},
        {'name' : 'gpio_vm5',           'CTL' : erot.L2_CSR.GPIO_VM5_BLF_CTL_0,             'WRITE' : erot.L2_CSR.GPIO_VM5_BLF_WRITE_CTL_0,         'READ' : erot.L2_CSR.GPIO_VM5_BLF_READ_CTL_0},
        {'name' : 'gpio_vm6',           'CTL' : erot.L2_CSR.GPIO_VM6_BLF_CTL_0,             'WRITE' : erot.L2_CSR.GPIO_VM6_BLF_WRITE_CTL_0,         'READ' : erot.L2_CSR.GPIO_VM6_BLF_READ_CTL_0},
        {'name' : 'gpio_vm7',           'CTL' : erot.L2_CSR.GPIO_VM7_BLF_CTL_0,             'WRITE' : erot.L2_CSR.GPIO_VM7_BLF_WRITE_CTL_0,         'READ' : erot.L2_CSR.GPIO_VM7_BLF_READ_CTL_0},
        {'name' : 'gpio_vm8',           'CTL' : erot.L2_CSR.GPIO_VM8_BLF_CTL_0,             'WRITE' : erot.L2_CSR.GPIO_VM8_BLF_WRITE_CTL_0,         'READ' : erot.L2_CSR.GPIO_VM8_BLF_READ_CTL_0},
        #part4, 10
        {'name' : 'i2c_ib0',            'CTL' : erot.L2_CSR.I2C_IB0_BLF_CTL_0,              'WRITE' : erot.L2_CSR.I2C_IB0_BLF_WRITE_CTL_0,          'READ' : erot.L2_CSR.I2C_IB0_BLF_READ_CTL_0},
        #part5, 11
        {'name' : 'i2c_ib1',            'CTL' : erot.L2_CSR.I2C_IB1_BLF_CTL_0,              'WRITE' : erot.L2_CSR.I2C_IB1_BLF_WRITE_CTL_0,          'READ' : erot.L2_CSR.I2C_IB1_BLF_READ_CTL_0},
        #part6, 12
        {'name' : 'i3c_ib0',            'CTL' : erot.L2_CSR.I3C_IB0_BLF_CTL_0,              'WRITE' : erot.L2_CSR.I3C_IB0_BLF_WRITE_CTL_0,          'READ' : erot.L2_CSR.I3C_IB0_BLF_READ_CTL_0},
        #part7, 13
        {'name' : 'i3c_ib1',            'CTL' : erot.L2_CSR.I3C_IB1_BLF_CTL_0,              'WRITE' : erot.L2_CSR.I3C_IB1_BLF_WRITE_CTL_0,          'READ' : erot.L2_CSR.I3C_IB1_BLF_READ_CTL_0},
        #part8, 14
        {'name' : 'io_expander',        'CTL' : erot.L2_CSR.IO_EXPANDER_BLF_CTL_0,          'WRITE' : erot.L2_CSR.IO_EXPANDER_BLF_WRITE_CTL_0,      'READ' : erot.L2_CSR.IO_EXPANDER_BLF_READ_CTL_0},
        #part9, 15
        {'name' : 'fsp',                'CTL' : erot.L2_CSR.FSP_BLF_CTL_0,                  'WRITE' : erot.L2_CSR.FSP_BLF_WRITE_CTL_0,              'READ' : erot.L2_CSR.FSP_BLF_READ_CTL_0},
        #part10, 16
        {'name' : 'oobhub_spi',         'CTL' : erot.L2_CSR.OOBHUB_SPI_BLF_CTL_0,           'WRITE' : erot.L2_CSR.OOBHUB_SPI_BLF_WRITE_CTL_0,       'READ' : erot.L2_CSR.OOBHUB_SPI_BLF_READ_CTL_0},
        #part11, 17-20
        {'name' : 'padctrl_e',          'CTL' : erot.L2_CSR.PADCTRL_E_BLF_CTL_0,            'WRITE' : erot.L2_CSR.PADCTRL_E_BLF_WRITE_CTL_0,        'READ' : erot.L2_CSR.PADCTRL_E_BLF_READ_CTL_0},
        {'name' : 'padctrl_n',          'CTL' : erot.L2_CSR.PADCTRL_N_BLF_CTL_0,            'WRITE' : erot.L2_CSR.PADCTRL_N_BLF_WRITE_CTL_0,        'READ' : erot.L2_CSR.PADCTRL_N_BLF_READ_CTL_0},
        {'name' : 'padctrl_s',          'CTL' : erot.L2_CSR.PADCTRL_S_BLF_CTL_0,            'WRITE' : erot.L2_CSR.PADCTRL_S_BLF_WRITE_CTL_0,        'READ' : erot.L2_CSR.PADCTRL_S_BLF_READ_CTL_0},
        {'name' : 'padctrl_w',          'CTL' : erot.L2_CSR.PADCTRL_W_BLF_CTL_0,            'WRITE' : erot.L2_CSR.PADCTRL_W_BLF_WRITE_CTL_0,        'READ' : erot.L2_CSR.PADCTRL_W_BLF_READ_CTL_0},
        #part12, 21
        {'name' : 'spi_ib0',            'CTL' : erot.L2_CSR.SPI_IB0_BLF_CTL_0,              'WRITE' : erot.L2_CSR.SPI_IB0_BLF_WRITE_CTL_0,          'READ' : erot.L2_CSR.SPI_IB0_BLF_READ_CTL_0},
        #part13, 22
        {'name' : 'spi_ib1',            'CTL' : erot.L2_CSR.SPI_IB1_BLF_CTL_0,              'WRITE' : erot.L2_CSR.SPI_IB1_BLF_WRITE_CTL_0,          'READ' : erot.L2_CSR.SPI_IB1_BLF_READ_CTL_0},
        #part14, 23
        {'name' : 'uart',               'CTL' : erot.L2_CSR.UART_BLF_CTL_0,                 'WRITE' : erot.L2_CSR.UART_BLF_WRITE_CTL_0,             'READ' : erot.L2_CSR.UART_BLF_READ_CTL_0},
    ]

    L1_FABRIC_TARGET_L1_CSR = []
    L1_FABRIC_TARGET_CLOCK = []
    L1_FABRIC_TARGET_BOOTQSPI = []
    L1_FABRIC_TARGET_FUSE = []
    L1_FABRIC_TARGET_JTAG = []
    L1_FABRIC_TARGET_MRAM = []
    L1_FABRIC_TARGET_OOBHUB = []
    L1_FABRIC_TARGET_PUFDBG = []
    L1_FABRIC_TARGET_QSPI0 = []
    L1_FABRIC_TARGET_QSPI1 = []
    L1_FABRIC_TARGET_RESET = []
    L1_FABRIC_TARGET_RTS = []
    L1_FABRIC_TARGET_SPIMON0 = []
    L1_FABRIC_TARGET_SPIMON1 = []
    L1_FABRIC_TARGET_SYSCTRL = []
    L1_FABRIC_TARGET_THERM = []
    L1_FABRIC_TARGET_ALL = []

    L2_FABRIC_TARGET_L2_CSR = []
    L2_FABRIC_TARGET_GPIO1 = []
    L2_FABRIC_TARGET_GPIO2 = []
    L2_FABRIC_TARGET_I2CIB0 = []
    L2_FABRIC_TARGET_I2CIB1 = []
    L2_FABRIC_TARGET_I3CIB0 = []
    L2_FABRIC_TARGET_I3CIB1 = []
    L2_FABRIC_TARGET_IOEXPD = []
    L2_FABRIC_TARGET_FSP = []
    L2_FABRIC_TARGET_OOBHUBSPI = []
    L2_FABRIC_TARGET_PADCTRL = []
    L2_FABRIC_TARGET_SPIIB0 = []
    L2_FABRIC_TARGET_SPIIB1 = []
    L2_FABRIC_TARGET_UART = []

    for i in range(0, 1):
        L1_FABRIC_TARGET_L1_CSR.append(L1_FABRIC_TARGET[i])
    for i in range(1, 8):
        L1_FABRIC_TARGET_CLOCK.append(L1_FABRIC_TARGET[i])
    for i in range(8, 11):
        L1_FABRIC_TARGET_BOOTQSPI.append(L1_FABRIC_TARGET[i])
    for i in range(11, 12):
        L1_FABRIC_TARGET_FUSE.append(L1_FABRIC_TARGET[i])
    for i in range(12, 13):
        L1_FABRIC_TARGET_JTAG.append(L1_FABRIC_TARGET[i])
    for i in range(13, 18):
        L1_FABRIC_TARGET_MRAM.append(L1_FABRIC_TARGET[i])
    for i in range(18, 19):
        L1_FABRIC_TARGET_OOBHUB.append(L1_FABRIC_TARGET[i])
    for i in range(20, 23):
        L1_FABRIC_TARGET_QSPI0.append(L1_FABRIC_TARGET[i])
    for i in range(23, 26):
        L1_FABRIC_TARGET_QSPI1.append(L1_FABRIC_TARGET[i])
    for i in range(26, 28):
        L1_FABRIC_TARGET_RESET.append(L1_FABRIC_TARGET[i])
    for i in range(28, 29):
        L1_FABRIC_TARGET_RTS.append(L1_FABRIC_TARGET[i])
    for i in range(29, 30):
        L1_FABRIC_TARGET_SPIMON0.append(L1_FABRIC_TARGET[i])
    for i in range(30, 31):
        L1_FABRIC_TARGET_SPIMON1.append(L1_FABRIC_TARGET[i])
    for i in range(31, 34):
        L1_FABRIC_TARGET_SYSCTRL.append(L1_FABRIC_TARGET[i])
    for i in range(34, 35):
        L1_FABRIC_TARGET_THERM.append(L1_FABRIC_TARGET[i])
    for i in range(0, 35):
        L1_FABRIC_TARGET_ALL.append(L1_FABRIC_TARGET[i])

    for i in range(0, 1):
        L2_FABRIC_TARGET_L2_CSR.append(L2_FABRIC_TARGET[i])
    for i in range(1, 5):
        L2_FABRIC_TARGET_GPIO1.append(L2_FABRIC_TARGET[i])
    for i in range(5, 10):
        L2_FABRIC_TARGET_GPIO2.append(L2_FABRIC_TARGET[i])
    for i in range(10, 11):
        L2_FABRIC_TARGET_I2CIB0.append(L2_FABRIC_TARGET[i])
    for i in range(11, 12):
        L2_FABRIC_TARGET_I2CIB1.append(L2_FABRIC_TARGET[i])
    for i in range(12, 13):
        L2_FABRIC_TARGET_I3CIB0.append(L2_FABRIC_TARGET[i])
    for i in range(13, 14):
        L2_FABRIC_TARGET_I3CIB1.append(L2_FABRIC_TARGET[i])
    for i in range(14, 15):
        L2_FABRIC_TARGET_IOEXPD.append(L2_FABRIC_TARGET[i])
    for i in range(15, 16):
        L2_FABRIC_TARGET_FSP.append(L2_FABRIC_TARGET[i])
    for i in range(16, 17):
        L2_FABRIC_TARGET_OOBHUBSPI.append(L2_FABRIC_TARGET[i])
    for i in range(17, 21):
        L2_FABRIC_TARGET_PADCTRL.append(L2_FABRIC_TARGET[i])
    for i in range(21, 22):
        L2_FABRIC_TARGET_SPIIB0.append(L2_FABRIC_TARGET[i])
    for i in range(22, 23):
        L2_FABRIC_TARGET_SPIIB1.append(L2_FABRIC_TARGET[i])
    for i in range(23, 24):
        L2_FABRIC_TARGET_UART.append(L2_FABRIC_TARGET[i])

    def L3_reset():
        #erot.RESET.NVEROT_RESET_CFG.SW_L3_RST_0.debug_write(0, 1)
        erot.RESET.NVEROT_RESET_CFG.SW_L3_RST_0.debug_write(0,False)
        helper.log("L3 Reset Triggered")
        #Wait reset finish
        helper.wait_sim_time("us", 2)
        helper.log("After wait for 2 us")
        if helper.target in ["fpga", "simv_fpga"]:
            helper.log("FPGA env does not need clk and reset init")
        else:
            test_api.clk_init()
            test_api.reset_init()
        helper.log("reset init done")
        erot.RESET.NVEROT_RESET_CFG.SW_L3_RST_0.debug_poll(RESET_LEVEL3=1)
        helper.log("L3 Reset Recovered")

    def check_value(reg, exp_value):
        act_value = reg.debug_read()
        if(act_value.value != exp_value):
            #print(exp_value, act_value.value)
            helper.perror("Reg value mismatch, exp: %x, act: %x" %(exp_value, act_value.value))
            reg.debug_poll()
        else:
            reg.debug_poll()

    def check_csr(t, target_list, reg, w_value):
        if(reg == 'CTL'):
            t['WRITE'].debug_write(0xffffffff)
            t['READ'].debug_write(0xffffffff)
            check_value(t['WRITE'], 0xffffffff)
            check_value(t['READ'], 0xffffffff)
            check_value(t[reg], 0) #Check whether reg default value is 0
            t['CTL'].debug_write(w_value)
            check_value(t['CTL'], w_value)
            check_value(t['WRITE'], 0xffffffff) #check CTL will not affect WRITE and READ
            check_value(t['READ'], 0xffffffff)
            for other_target in target_list:
                if(other_target['name'] != t['name']):
                    check_value(other_target['WRITE'], 0)
                    check_value(other_target['READ'], 0)
                    check_value(other_target['CTL'], 0)
        else:
            check_value(t[reg], 0) #Check whether reg default value is 0
            t[reg].debug_write(w_value)
            check_value(t[reg], w_value)
            for key in t: #Check whether other regs will be affected
                if(key != reg and key != 'name'):
                    check_value(t[key], 0)
            for other_target in target_list:
                if(other_target['name'] != t['name']):
                    check_value(other_target['WRITE'], 0)
                    check_value(other_target['READ'], 0)
                    check_value(other_target['CTL'], 0)
            t[reg].debug_write(0)
            check_value(t[reg], 0)

    def write_and_check(t, target_list, reg, w_value):
        check_value(t[reg], 0)
        t[reg].debug_write(w_value)
        check_value(t[reg], w_value)
        for key in t:
            if(key != reg and key != 'name'):
                check_value(t[key], 0)
        for other_target in target_list:
            if(other_target['name'] != t['name']):
                if(other_target['name'] == 'l1_csr' or other_target['name'] == 'l2_csr'):
                    check_value(other_target['WRITE'], 0xffffffff)
                    check_value(other_target['READ'], 0xffffffff)
                    check_value(other_target['CTL'], 0x30000)
                else:
                    check_value(other_target['WRITE'], 0)
                    check_value(other_target['READ'], 0)
                    check_value(other_target['CTL'], 0)
        t[reg].debug_write(0)
        check_value(t[reg], 0)

    def normal_write_read(t):
        if(t['name'] == 'l1_csr' or t['name'] == 'l2_csr'):
            t['CTL'].debug_write(0)
            t['READ'].debug_write(0)
            t['WRITE'].debug_write(0)
            check_value(t['CTL'], 0)
            check_value(t['READ'], 0)
            check_value(t['WRITE'], 0)
            t['WRITE'].debug_write(0xffffffff)
            t['READ'].debug_write(0xffffffff)
            t['CTL'].debug_write(0x30000)
            check_value(t['WRITE'], 0xffffffff)
            check_value(t['READ'], 0xffffffff)
            check_value(t['CTL'], 0x30000)
        else:
            t['WRITE'].debug_write(0xffffffff)
            t['READ'].debug_write(0xffffffff)
            t['CTL'].debug_write(0x30000)
            check_value(t['WRITE'], 0xffffffff)
            check_value(t['READ'], 0xffffffff)
            check_value(t['CTL'], 0x30000)
            t['WRITE'].debug_write(0)
            t['READ'].debug_write(0)
            t['CTL'].debug_write(0)
            check_value(t['WRITE'], 0)
            check_value(t['READ'], 0)
            check_value(t['CTL'], 0)

    def first_write_read(t, target_list):
        write_and_check(t, target_list, 'WRITE', 0xffffffff)
        write_and_check(t, target_list, 'READ', 0xffffffff)
        write_and_check(t, target_list, 'CTL', 0x30000)#set bit 16 (REN) and bit 17 (WEN) to 1

    options = parse_args()
    fabric = options.IP

    #unlock j2h interface
    helper.log("Test start")
    helper.wait_sim_time("us", 50)
    helper.hdl_force('ntb_top.u_nv_fpga_dut.u_nv_top_fpga.u_nv_top_wrapper.u_nv_top.nvjtag_sel', 1)

    helper.jtag.Reset(0)
    helper.jtag.DRScan(100, hex(0x0)) #add some delay as jtag only work when nvjtag_sel stable in real case
    helper.jtag.Reset(1)


    helper.pinfo(f'j2h_unlock sequence start')
    helper.j2h_unlock()
    helper.pinfo(f'j2h_unlock sequence finish')

    #if(options.IP == 'L1_PART1' or options.IP == 'L1_PART2' or options.IP == 'L1_PART3' or options.IP == 'L1_PART4'):
    full_list = L1_FABRIC_TARGET if(fabric[0:2] == 'L1') else L2_FABRIC_TARGET
    if(fabric[0:2] == 'L1'):
        if(options.IP == 'L1_CSR'):
            check_csr(L1_FABRIC_TARGET_L1_CSR[0], full_list, 'WRITE', 0xffffffff)
            check_csr(L1_FABRIC_TARGET_L1_CSR[0], full_list, 'READ', 0xffffffff)
            check_csr(L1_FABRIC_TARGET_L1_CSR[0], full_list, 'CTL', 0x30000)#Check CSR BLF regs
        else:
            erot.L1_CSR.L1_CSR_BLF_WRITE_CTL_0.debug_write(0xffffffff)
            erot.L1_CSR.L1_CSR_BLF_READ_CTL_0.debug_write(0xffffffff)
            erot.L1_CSR.L1_CSR_BLF_CTL_0.debug_write(0x30000)
    elif(fabric[0:2] == 'L2'):
        if(options.IP == 'L2_CSR'):
            check_csr(L2_FABRIC_TARGET_L2_CSR[0], full_list, 'WRITE', 0xffffffff)
            check_csr(L2_FABRIC_TARGET_L2_CSR[0], full_list, 'READ', 0xffffffff)
            check_csr(L2_FABRIC_TARGET_L2_CSR[0], full_list, 'CTL', 0x30000)#Check CSR BLF regs
        else:
            erot.L2_CSR.L2_CSR_BLF_WRITE_CTL_0.debug_write(0xffffffff)
            erot.L2_CSR.L2_CSR_BLF_READ_CTL_0.debug_write(0xffffffff)
            erot.L2_CSR.L2_CSR_BLF_CTL_0.debug_write(0x30000)
    else:
        helper.perror("wrong pyarg option(1): %s" %fabric[0:2])

    def check_BLF_Lock(target_list):
        for target in target_list:
            helper.log("================= %s check start================" %target['name'])
            #Check all blf regs can be read and write by default
            if(target['name'] != 'l1_csr' and target['name'] != 'l2_csr'):
                first_write_read(target, target_list)
            #Set the lock bit to 1
            target['CTL'].debug_write(0x80000000) #bit 31
            helper.log("Lock bit set to 1")
            #try to write to blf regs
            target['CTL'].debug_write(0x30000)
            if(target['name'] != 'l1_csr' and target['name'] != 'l2_csr'):
                target['WRITE'].debug_write(0xffffffff)
                target['READ'].debug_write(0xffffffff)
            else:
                target['WRITE'].debug_write(0)
                target['READ'].debug_write(0)
            #read_blf_err(target['name'])
            #Check blf regs can be read as previous value
            check_value(target['CTL'], 0x80000000)
            if(target['name'] != 'l1_csr' and target['name'] != 'l2_csr'):
                check_value(target['WRITE'], 0)
                check_value(target['READ'], 0)
            else:
                check_value(target['WRITE'], 0xffffffff) #for L1_CSR/L2_CSR, previous value is 0xffffffff
                check_value(target['READ'], 0xffffffff)
            #Check blf regs of other targets can be read and write normally
            for other_target in full_list:
                if(other_target['name'] != target['name']):
                    normal_write_read(other_target)
            #Trigger SW L3 reset
            L3_reset()
            #Check blf regs in all targets can be read and write -> only need to check the locked reg can be again read and write
           #setup L1_CSR/L2_CSR
            if(fabric[0:2] == 'L1'):
                erot.L1_CSR.L1_CSR_BLF_WRITE_CTL_0.debug_write(0xffffffff)
                erot.L1_CSR.L1_CSR_BLF_READ_CTL_0.debug_write(0xffffffff)
                erot.L1_CSR.L1_CSR_BLF_CTL_0.debug_write(0x30000)
            elif(fabric[0:2] == 'L2'):
                erot.L2_CSR.L2_CSR_BLF_WRITE_CTL_0.debug_write(0xffffffff)
                erot.L2_CSR.L2_CSR_BLF_READ_CTL_0.debug_write(0xffffffff)
                erot.L2_CSR.L2_CSR_BLF_CTL_0.debug_write(0x30000)
            else:
                helper.perror("wrong pyarg option(2): %s" %fabric[0:2])
            normal_write_read(target)
            helper.log("================= %s check finish================" %target['name'])

    if(options.IP == 'L1_CSR'):
        check_BLF_Lock(L1_FABRIC_TARGET_L1_CSR)
    elif(options.IP == 'L1_CLOCK'):
        check_BLF_Lock(L1_FABRIC_TARGET_CLOCK)
    elif(options.IP == 'L1_BOOTQSPI'):
        check_BLF_Lock(L1_FABRIC_TARGET_BOOTQSPI)
    elif(options.IP == 'L1_FUSE'):
        check_BLF_Lock(L1_FABRIC_TARGET_FUSE)
    elif(options.IP == 'L1_JTAG'):
        check_BLF_Lock(L1_FABRIC_TARGET_JTAG)
    elif(options.IP == 'L1_MRAM'):
        check_BLF_Lock(L1_FABRIC_TARGET_MRAM)
    elif(options.IP == 'L1_OOBHUB'):
        check_BLF_Lock(L1_FABRIC_TARGET_OOBHUB)
    elif(options.IP == 'L1_PUFDBG'):
        check_BLF_Lock(L1_FABRIC_TARGET_PUFDBG)
    elif(options.IP == 'L1_QSPI0'):
        check_BLF_Lock(L1_FABRIC_TARGET_QSPI0)
    elif(options.IP == 'L1_QSPI1'):
        check_BLF_Lock(L1_FABRIC_TARGET_QSPI1)
    elif(options.IP == 'L1_RESET'):
        check_BLF_Lock(L1_FABRIC_TARGET_RESET)
    elif(options.IP == 'L1_RTS'):
        check_BLF_Lock(L1_FABRIC_TARGET_RTS)
    elif(options.IP == 'L1_SPIMON0'):
        check_BLF_Lock(L1_FABRIC_TARGET_SPIMON0)
    elif(options.IP == 'L1_SPIMON1'):
        check_BLF_Lock(L1_FABRIC_TARGET_SPIMON1)
    elif(options.IP == 'L1_SYSCTRL'):
        check_BLF_Lock(L1_FABRIC_TARGET_SYSCTRL)
    elif(options.IP == 'L1_THERM'):
        check_BLF_Lock(L1_FABRIC_TARGET_THERM)
    elif(options.IP == 'L2_CSR'):
        check_BLF_Lock(L2_FABRIC_TARGET_L2_CSR)
    elif(options.IP == 'L2_GPIO1'):
        check_BLF_Lock(L2_FABRIC_TARGET_GPIO1)
    elif(options.IP == 'L2_GPIO2'):
        check_BLF_Lock(L2_FABRIC_TARGET_GPIO2)
    elif(options.IP == 'L2_I2CIB0'):
        check_BLF_Lock(L2_FABRIC_TARGET_I2CIB0)
    elif(options.IP == 'L2_I2CIB1'):
        check_BLF_Lock(L2_FABRIC_TARGET_I2CIB1)
    elif(options.IP == 'L2_I3CIB0'):
        check_BLF_Lock(L2_FABRIC_TARGET_I3CIB0)
    elif(options.IP == 'L2_I3CIB1'):
        check_BLF_Lock(L2_FABRIC_TARGET_I3CIB1)
    elif(options.IP == 'L2_IOEXPD'):
        check_BLF_Lock(L2_FABRIC_TARGET_IOEXPD)
    elif(options.IP == 'L2_FSP'):
        check_BLF_Lock(L2_FABRIC_TARGET_FSP)
    elif(options.IP == 'L2_OOBHUBSPI'):
        check_BLF_Lock(L2_FABRIC_TARGET_OOBHUBSPI)
    elif(options.IP == 'L2_PADCTRL'):
        check_BLF_Lock(L2_FABRIC_TARGET_PADCTRL)
    elif(options.IP == 'L2_SPIIB0'):
        check_BLF_Lock(L2_FABRIC_TARGET_SPIIB0)
    elif(options.IP == 'L2_SPIIB1'):
        check_BLF_Lock(L2_FABRIC_TARGET_SPIIB1)
    elif(options.IP == 'L2_UART'):
        check_BLF_Lock(L2_FABRIC_TARGET_UART)
    elif(options.IP == 'L1_ALL'):
	    check_BLF_Lock(L1_FABRIC_TARGET_ALL)
    else:
        helper.perror("Wrong --IP %s" % options.monitor)
    helper.log("Test Finish")

