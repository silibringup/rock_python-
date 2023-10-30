#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import * 

with Test(sys.argv) as t:

    def parse_args():
        t.parser.add_argument("--Fabric", action='store', help="Check BLF function of L1/L2 fabric", default='L1')
        opts, unknown = t.parser.parse_known_args(sys.argv[1:])
        return opts
    
    L1_FABRIC_TARGET = [
#        {'name' : 'l1_csr',                   'reg' : erot.L1_CSR,                           'addr_low_boundary' : 0x13000,      'CTL' : erot.L1_CSR.L1_CSR_BLF_CTL_0,                      'WRITE' : erot.L1_CSR.L1_CSR_BLF_WRITE_CTL_0,                     'READ' : erot.L1_CSR.L1_CSR_BLF_READ_CTL_0},
#        {'name' : 'clock_vrefro_ctl',         'reg' : erot.CLOCK.NVEROT_CLOCK_VREFRO_CTL,    'addr_low_boundary' : 0x23000,      'CTL' : erot.L1_CSR.CLOCK_VREFRO_CTL_BLF_CTL_0,            'WRITE' : erot.L1_CSR.CLOCK_VREFRO_CTL_BLF_WRITE_CTL_0,           'READ' : erot.L1_CSR.CLOCK_VREFRO_CTL_BLF_READ_CTL_0},
#        {'name' : 'clock_sys_ctl',            'reg' : erot.CLOCK.NVEROT_CLOCK_SYS_CTL,       'addr_low_boundary' : 0x24000,      'CTL' : erot.L1_CSR.CLOCK_SYS_CTL_BLF_CTL_0,               'WRITE' : erot.L1_CSR.CLOCK_SYS_CTL_BLF_WRITE_CTL_0,              'READ' : erot.L1_CSR.CLOCK_SYS_CTL_BLF_READ_CTL_0},
#        {'name' : 'clock_io_ctl',             'reg' : erot.CLOCK.NVEROT_CLOCK_IO_CTL,        'addr_low_boundary' : 0x25000,      'CTL' : erot.L1_CSR.CLOCK_IO_CTL_BLF_CTL_0,                'WRITE' : erot.L1_CSR.CLOCK_IO_CTL_BLF_WRITE_CTL_0,               'READ' : erot.L1_CSR.CLOCK_IO_CTL_BLF_READ_CTL_0},
#        {'name' : 'clock_status',             'reg' : erot.CLOCK.NVEROT_CLOCK_STATUS,        'addr_low_boundary' : 0x26000,      'CTL' : erot.L1_CSR.CLOCK_STATUS_BLF_CTL_0,                'WRITE' : erot.L1_CSR.CLOCK_STATUS_BLF_WRITE_CTL_0,               'READ' : erot.L1_CSR.CLOCK_STATUS_BLF_READ_CTL_0},
#        {'name' : 'clock_cmn_pad_ctl',        'reg' : erot.CLOCK.NVEROT_CLOCK_CMN_PAD_CTL,   'addr_low_boundary' : 0x27000,      'CTL' : erot.L1_CSR.CLOCK_CMN_PAD_CTL_BLF_CTL_0,           'WRITE' : erot.L1_CSR.CLOCK_CMN_PAD_CTL_BLF_WRITE_CTL_0,          'READ' : erot.L1_CSR.CLOCK_CMN_PAD_CTL_BLF_READ_CTL_0},
#        {'name' : 'clock_podvmon',            'reg' : erot.CLOCK.NVEROT_CLOCK_PODVMON,       'addr_low_boundary' : 0x28000,      'CTL' : erot.L1_CSR.CLOCK_PODVMON_BLF_CTL_0,               'WRITE' : erot.L1_CSR.CLOCK_PODVMON_BLF_WRITE_CTL_0,              'READ' : erot.L1_CSR.CLOCK_PODVMON_BLF_READ_CTL_0},
#        {'name' : 'clock_fmon',               'reg' : erot.CLOCK.NVEROT_CLOCK_FMON,          'addr_low_boundary' : 0x29000,      'CTL' : erot.L1_CSR.CLOCK_FMON_BLF_CTL_0,                  'WRITE' : erot.L1_CSR.CLOCK_FMON_BLF_WRITE_CTL_0,                 'READ' : erot.L1_CSR.CLOCK_FMON_BLF_READ_CTL_0},
#        {'name' : 'boot_qspi_nv_prom_data',   'reg' : 'none',                                'addr_low_boundary' : 0x45000,      'CTL' : erot.L1_CSR.BOOT_QSPI_NV_PROM_DATA_BLF_CTL_0,      'WRITE' : erot.L1_CSR.BOOT_QSPI_NV_PROM_DATA_BLF_WRITE_CTL_0,     'READ' : erot.L1_CSR.BOOT_QSPI_NV_PROM_DATA_BLF_READ_CTL_0},
#        {'name' : 'boot_qspi_nv_prom_2_data', 'reg' : 'none',                                'addr_low_boundary' : 0x145000,     'CTL' : erot.L1_CSR.BOOT_QSPI_NV_PROM_2_DATA_BLF_CTL_0,    'WRITE' : erot.L1_CSR.BOOT_QSPI_NV_PROM_2_DATA_BLF_WRITE_CTL_0,   'READ' : erot.L1_CSR.BOOT_QSPI_NV_PROM_2_DATA_BLF_READ_CTL_0},
#        {'name' : 'fuse',                     'reg' : erot.FUSE,                             'addr_low_boundary' : 0x820000,     'CTL' : erot.L1_CSR.FUSE_BLF_CTL_0,                        'WRITE' : erot.L1_CSR.FUSE_BLF_WRITE_CTL_0,                       'READ' : erot.L1_CSR.FUSE_BLF_READ_CTL_0},
        {'name' : 'jtag',                     'reg' : 'none',                                'addr_low_boundary' : 0x4a6000,     'CTL' : erot.L1_CSR.JTAG_BLF_CTL_0,                        'WRITE' : erot.L1_CSR.JTAG_BLF_WRITE_CTL_0,                       'READ' : erot.L1_CSR.JTAG_BLF_READ_CTL_0},
        {'name' : 'mram_cfg',                 'reg' : 'none',                                'addr_low_boundary' : 0xfc0000,     'CTL' : erot.L1_CSR.MRAM_CFG_BLF_CTL_0,                    'WRITE' : erot.L1_CSR.MRAM_CFG_BLF_WRITE_CTL_0,                   'READ' : erot.L1_CSR.MRAM_CFG_BLF_READ_CTL_0},
       {'name' : 'mram_tmc',                 'reg' : 'none',                                'addr_low_boundary' : 0xfd0000,     'CTL' : erot.L1_CSR.MRAM_TMC_BLF_CTL_0,                    'WRITE' : erot.L1_CSR.MRAM_TMC_BLF_WRITE_CTL_0,                   'READ' : erot.L1_CSR.MRAM_TMC_BLF_READ_CTL_0},
        {'name' : 'mram_otp',                 'reg' : 'none',                                'addr_low_boundary' : 0xfe0000,     'CTL' : erot.L1_CSR.MRAM_OTP_BLF_CTL_0,                    'WRITE' : erot.L1_CSR.MRAM_OTP_BLF_WRITE_CTL_0,                   'READ' : erot.L1_CSR.MRAM_OTP_BLF_READ_CTL_0},
        {'name' : 'mram_mtp',                 'reg' : 'none',                                'addr_low_boundary' : 0xff0000,     'CTL' : erot.L1_CSR.MRAM_MTP_BLF_CTL_0,                    'WRITE' : erot.L1_CSR.MRAM_MTP_BLF_WRITE_CTL_0,                   'READ' : erot.L1_CSR.MRAM_MTP_BLF_READ_CTL_0},
        {'name' : 'mram_mtpr',                'reg' : 'none',                                'addr_low_boundary' : 0x1000000,    'CTL' : erot.L1_CSR.MRAM_MTPR_BLF_CTL_0,                   'WRITE' : erot.L1_CSR.MRAM_MTPR_BLF_WRITE_CTL_0,                  'READ' : erot.L1_CSR.MRAM_MTPR_BLF_READ_CTL_0},
        {'name' : 'oobhub',                   'reg' : erot.OOBHUB,                           'addr_low_boundary' : 0x8a8000,     'CTL' : erot.L1_CSR.OOBHUB_BLF_CTL_0,                      'WRITE' : erot.L1_CSR.OOBHUB_BLF_WRITE_CTL_0,                     'READ' : erot.L1_CSR.OOBHUB_BLF_READ_CTL_0},
        {'name' : 'puf_dbg',                  'reg' : erot.PUF_DBG,                          'addr_low_boundary' : 0x4a5000,     'CTL' : erot.L1_CSR.PUF_DBG_BLF_CTL_0,                     'WRITE' : erot.L1_CSR.PUF_DBG_BLF_WRITE_CTL_0,                    'READ' : erot.L1_CSR.PUF_DBG_BLF_READ_CTL_0},
        {'name' : 'qspi0_nv_prom_data',       'reg' : 'none',                                'addr_low_boundary' : 0x148000,     'CTL' : erot.L1_CSR.QSPI0_NV_PROM_DATA_BLF_CTL_0,          'WRITE' : erot.L1_CSR.QSPI0_NV_PROM_DATA_BLF_WRITE_CTL_0,         'READ' : erot.L1_CSR.QSPI0_NV_PROM_DATA_BLF_READ_CTL_0},
        {'name' : 'qspi0_nv_prom_2_data',     'reg' : 'none',                                'addr_low_boundary' : 0x248000,     'CTL' : erot.L1_CSR.QSPI0_NV_PROM_2_DATA_BLF_CTL_0,        'WRITE' : erot.L1_CSR.QSPI0_NV_PROM_2_DATA_BLF_WRITE_CTL_0,       'READ' : erot.L1_CSR.QSPI0_NV_PROM_2_DATA_BLF_READ_CTL_0},
        {'name' : 'qspi0_core',               'reg' : 'none',                                'addr_low_boundary' : 0x146000,     'CTL' : erot.L1_CSR.QSPI0_CORE_BLF_CTL_0,                  'WRITE' : erot.L1_CSR.QSPI0_CORE_BLF_WRITE_CTL_0,                 'READ' : erot.L1_CSR.QSPI0_CORE_BLF_READ_CTL_0},
        {'name' : 'qspi1_nv_prom_data',       'reg' : 'none',                                'addr_low_boundary' : 0x24b000,     'CTL' : erot.L1_CSR.QSPI1_NV_PROM_DATA_BLF_CTL_0,          'WRITE' : erot.L1_CSR.QSPI1_NV_PROM_DATA_BLF_WRITE_CTL_0,         'READ' : erot.L1_CSR.QSPI1_NV_PROM_DATA_BLF_READ_CTL_0},
        {'name' : 'qspi1_nv_prom_2_data',     'reg' : 'none',                                'addr_low_boundary' : 0x34b000,     'CTL' : erot.L1_CSR.QSPI1_NV_PROM_2_DATA_BLF_CTL_0,        'WRITE' : erot.L1_CSR.QSPI1_NV_PROM_2_DATA_BLF_WRITE_CTL_0,       'READ' : erot.L1_CSR.QSPI1_NV_PROM_2_DATA_BLF_READ_CTL_0},
        {'name' : 'qspi1_core',               'reg' : 'none',                                'addr_low_boundary' : 0x249000,     'CTL' : erot.L1_CSR.QSPI1_CORE_BLF_CTL_0,                  'WRITE' : erot.L1_CSR.QSPI1_CORE_BLF_WRITE_CTL_0,                 'READ' : erot.L1_CSR.QSPI1_CORE_BLF_READ_CTL_0},
        {'name' : 'boot_qspi_core',           'reg' : 'none',                                'addr_low_boundary' : 0x43000,      'CTL' : erot.L1_CSR.BOOT_QSPI_CORE_BLF_CTL_0,              'WRITE' : erot.L1_CSR.BOOT_QSPI_CORE_BLF_WRITE_CTL_0,             'READ' : erot.L1_CSR.BOOT_QSPI_CORE_BLF_READ_CTL_0},
        {'name' : 'reset_reg',                'reg' : erot.RESET.NVEROT_RESET_CFG,           'addr_low_boundary' : 0x33000,      'CTL' : erot.L1_CSR.RESET_REG_BLF_CTL_0,                   'WRITE' : erot.L1_CSR.RESET_REG_BLF_WRITE_CTL_0,                  'READ' : erot.L1_CSR.RESET_REG_BLF_READ_CTL_0},
        {'name' : 'reset_status',             'reg' : erot.RESET.NVEROT_RESET_STATUS,        'addr_low_boundary' : 0x34000,      'CTL' : erot.L1_CSR.RESET_STATUS_BLF_CTL_0,                'WRITE' : erot.L1_CSR.RESET_STATUS_BLF_WRITE_CTL_0,               'READ' : erot.L1_CSR.RESET_STATUS_BLF_READ_CTL_0},
        {'name' : 'rts',                      'reg' : erot.RTS,                              'addr_low_boundary' : 0x4a3000,     'CTL' : erot.L1_CSR.RTS_BLF_CTL_0,                         'WRITE' : erot.L1_CSR.RTS_BLF_WRITE_CTL_0,                        'READ' : erot.L1_CSR.RTS_BLF_READ_CTL_0},
        {'name' : 'spi_mon0',                 'reg' : erot.SPI_MON0,                         'addr_low_boundary' : 0x463000,     'CTL' : erot.L1_CSR.SPI_MON0_BLF_CTL_0,                    'WRITE' : erot.L1_CSR.SPI_MON0_BLF_WRITE_CTL_0,                   'READ' : erot.L1_CSR.SPI_MON0_BLF_READ_CTL_0},
        {'name' : 'spi_mon1',                 'reg' : erot.SPI_MON1,                         'addr_low_boundary' : 0x483000,     'CTL' : erot.L1_CSR.SPI_MON1_BLF_CTL_0,                    'WRITE' : erot.L1_CSR.SPI_MON1_BLF_WRITE_CTL_0,                   'READ' : erot.L1_CSR.SPI_MON1_BLF_READ_CTL_0},
        {'name' : 'nv_pmc',                   'reg' : erot.NV_PMC,                           'addr_low_boundary' : 0,            'CTL' : erot.L1_CSR.NV_PMC_BLF_CTL_0,                      'WRITE' : erot.L1_CSR.NV_PMC_BLF_WRITE_CTL_0,                     'READ' : erot.L1_CSR.NV_PMC_BLF_READ_CTL_0},
        {'name' : 'nv_pbus',                  'reg' : erot.NV_PBUS,                          'addr_low_boundary' : 0x1000,       'CTL' : erot.L1_CSR.NV_PBUS_BLF_CTL_0,                     'WRITE' : erot.L1_CSR.NV_PBUS_BLF_WRITE_CTL_0,                    'READ' : erot.L1_CSR.NV_PBUS_BLF_READ_CTL_0},
        {'name' : 'nv_ptop',                  'reg' : erot.NV_PTOP,                          'addr_low_boundary' : 0x22000,      'CTL' : erot.L1_CSR.NV_PTOP_BLF_CTL_0,                     'WRITE' : erot.L1_CSR.NV_PTOP_BLF_WRITE_CTL_0,                    'READ' : erot.L1_CSR.NV_PTOP_BLF_READ_CTL_0},
        {'name' : 'therm',                    'reg' : erot.THERM,                            'addr_low_boundary' : 0x2000,       'CTL' : erot.L1_CSR.THERM_BLF_CTL_0,                       'WRITE' : erot.L1_CSR.THERM_BLF_WRITE_CTL_0,                      'READ' : erot.L1_CSR.THERM_BLF_READ_CTL_0},
    ]

    L2_FABRIC_TARGET = [
        {'name' : 'l2_csr',        'reg' : erot.L2_CSR,         'addr_low_boundary' : 0x9a4000,    'CTL' : erot.L2_CSR.L2_CSR_BLF_CTL_0,       'WRITE' : erot.L2_CSR.L2_CSR_BLF_WRITE_CTL_0,           'READ' : erot.L2_CSR.L2_CSR_BLF_READ_CTL_0},
        {'name' : 'gpio_cmn',      'reg' : 'none',              'addr_low_boundary' : 0x984000,    'CTL' : erot.L2_CSR.GPIO_CMN_BLF_CTL_0,     'WRITE' : erot.L2_CSR.GPIO_CMN_BLF_WRITE_CTL_0,         'READ' : erot.L2_CSR.GPIO_CMN_BLF_READ_CTL_0},
#        {'name' : 'gpio_vm1',      'reg' : 'none',              'addr_low_boundary' : 0x985000,    'CTL' : erot.L2_CSR.GPIO_VM1_BLF_CTL_0,     'WRITE' : erot.L2_CSR.GPIO_VM1_BLF_WRITE_CTL_0,         'READ' : erot.L2_CSR.GPIO_VM1_BLF_READ_CTL_0},
#        {'name' : 'gpio_vm2',      'reg' : 'none',              'addr_low_boundary' : 0x986000,    'CTL' : erot.L2_CSR.GPIO_VM2_BLF_CTL_0,     'WRITE' : erot.L2_CSR.GPIO_VM2_BLF_WRITE_CTL_0,         'READ' : erot.L2_CSR.GPIO_VM2_BLF_READ_CTL_0},
#        {'name' : 'gpio_vm3',      'reg' : 'none',              'addr_low_boundary' : 0x987000,    'CTL' : erot.L2_CSR.GPIO_VM3_BLF_CTL_0,     'WRITE' : erot.L2_CSR.GPIO_VM3_BLF_WRITE_CTL_0,         'READ' : erot.L2_CSR.GPIO_VM3_BLF_READ_CTL_0},
#        {'name' : 'gpio_vm4',      'reg' : 'none',              'addr_low_boundary' : 0x988000,    'CTL' : erot.L2_CSR.GPIO_VM4_BLF_CTL_0,     'WRITE' : erot.L2_CSR.GPIO_VM4_BLF_WRITE_CTL_0,         'READ' : erot.L2_CSR.GPIO_VM4_BLF_READ_CTL_0},
#        {'name' : 'gpio_vm5',      'reg' : 'none',              'addr_low_boundary' : 0x989000,    'CTL' : erot.L2_CSR.GPIO_VM5_BLF_CTL_0,     'WRITE' : erot.L2_CSR.GPIO_VM5_BLF_WRITE_CTL_0,         'READ' : erot.L2_CSR.GPIO_VM5_BLF_READ_CTL_0},
#        {'name' : 'gpio_vm6',      'reg' : 'none',              'addr_low_boundary' : 0x98a000,    'CTL' : erot.L2_CSR.GPIO_VM6_BLF_CTL_0,     'WRITE' : erot.L2_CSR.GPIO_VM6_BLF_WRITE_CTL_0,         'READ' : erot.L2_CSR.GPIO_VM6_BLF_READ_CTL_0},
#        {'name' : 'gpio_vm7',      'reg' : 'none',              'addr_low_boundary' : 0x98b000,    'CTL' : erot.L2_CSR.GPIO_VM7_BLF_CTL_0,     'WRITE' : erot.L2_CSR.GPIO_VM7_BLF_WRITE_CTL_0,         'READ' : erot.L2_CSR.GPIO_VM7_BLF_READ_CTL_0},
#        {'name' : 'gpio_vm8',      'reg' : 'none',              'addr_low_boundary' : 0x98c000,    'CTL' : erot.L2_CSR.GPIO_VM8_BLF_CTL_0,     'WRITE' : erot.L2_CSR.GPIO_VM8_BLF_WRITE_CTL_0,         'READ' : erot.L2_CSR.GPIO_VM8_BLF_READ_CTL_0},
#        {'name' : 'i2c_ib0',       'reg' : erot.I2C_IB0,        'addr_low_boundary' : 0x914000,    'CTL' : erot.L2_CSR.I2C_IB0_BLF_CTL_0,      'WRITE' : erot.L2_CSR.I2C_IB0_BLF_WRITE_CTL_0,          'READ' : erot.L2_CSR.I2C_IB0_BLF_READ_CTL_0},
#        {'name' : 'i2c_ib1',       'reg' : erot.I2C_IB1,        'addr_low_boundary' : 0x944000,    'CTL' : erot.L2_CSR.I2C_IB1_BLF_CTL_0,      'WRITE' : erot.L2_CSR.I2C_IB1_BLF_WRITE_CTL_0,          'READ' : erot.L2_CSR.I2C_IB1_BLF_READ_CTL_0},
#        {'name' : 'i3c_ib0',       'reg' : erot.I3C_IB0,        'addr_low_boundary' : 0x924000,    'CTL' : erot.L2_CSR.I3C_IB0_BLF_CTL_0,      'WRITE' : erot.L2_CSR.I3C_IB0_BLF_WRITE_CTL_0,          'READ' : erot.L2_CSR.I3C_IB0_BLF_READ_CTL_0},
#        {'name' : 'i3c_ib1',       'reg' : erot.I3C_IB1,        'addr_low_boundary' : 0x954000,    'CTL' : erot.L2_CSR.I3C_IB1_BLF_CTL_0,      'WRITE' : erot.L2_CSR.I3C_IB1_BLF_WRITE_CTL_0,          'READ' : erot.L2_CSR.I3C_IB1_BLF_READ_CTL_0},
#        {'name' : 'io_expander',   'reg' : erot.IO_EXPANDER,    'addr_low_boundary' : 0x964000,    'CTL' : erot.L2_CSR.IO_EXPANDER_BLF_CTL_0,  'WRITE' : erot.L2_CSR.IO_EXPANDER_BLF_WRITE_CTL_0,      'READ' : erot.L2_CSR.IO_EXPANDER_BLF_READ_CTL_0},
#        {'name' : 'fsp',           'reg' : erot.PFSP,           'addr_low_boundary' : 0x8f0000,    'CTL' : erot.L2_CSR.FSP_BLF_CTL_0,          'WRITE' : erot.L2_CSR.FSP_BLF_WRITE_CTL_0,              'READ' : erot.L2_CSR.FSP_BLF_READ_CTL_0},
#        {'name' : 'oobhub_spi',    'reg' : erot.OOBHUB_SPI,     'addr_low_boundary' : 0x8f4000,    'CTL' : erot.L2_CSR.OOBHUB_SPI_BLF_CTL_0,   'WRITE' : erot.L2_CSR.OOBHUB_SPI_BLF_WRITE_CTL_0,       'READ' : erot.L2_CSR.OOBHUB_SPI_BLF_READ_CTL_0},
#        {'name' : 'padctrl_e',     'reg' : erot.PADCTRL_E,      'addr_low_boundary' : 0x99c000,    'CTL' : erot.L2_CSR.PADCTRL_E_BLF_CTL_0,    'WRITE' : erot.L2_CSR.PADCTRL_E_BLF_WRITE_CTL_0,        'READ' : erot.L2_CSR.PADCTRL_E_BLF_READ_CTL_0},
#        {'name' : 'padctrl_n',     'reg' : erot.PADCTRL_N,      'addr_low_boundary' : 0x994000,    'CTL' : erot.L2_CSR.PADCTRL_N_BLF_CTL_0,    'WRITE' : erot.L2_CSR.PADCTRL_N_BLF_WRITE_CTL_0,        'READ' : erot.L2_CSR.PADCTRL_N_BLF_READ_CTL_0},
#        {'name' : 'padctrl_s',     'reg' : erot.PADCTRL_S,      'addr_low_boundary' : 0x998fff,    'CTL' : erot.L2_CSR.PADCTRL_S_BLF_CTL_0,    'WRITE' : erot.L2_CSR.PADCTRL_S_BLF_WRITE_CTL_0,        'READ' : erot.L2_CSR.PADCTRL_S_BLF_READ_CTL_0},
#        {'name' : 'padctrl_w',     'reg' : erot.PADCTRL_W,      'addr_low_boundary' : 0x9a0000,    'CTL' : erot.L2_CSR.PADCTRL_W_BLF_CTL_0,    'WRITE' : erot.L2_CSR.PADCTRL_W_BLF_WRITE_CTL_0,        'READ' : erot.L2_CSR.PADCTRL_W_BLF_READ_CTL_0},
#        {'name' : 'spi_ib0',       'reg' : erot.SPI_IB0,        'addr_low_boundary' : 0x904000,    'CTL' : erot.L2_CSR.SPI_IB0_BLF_CTL_0,      'WRITE' : erot.L2_CSR.SPI_IB0_BLF_WRITE_CTL_0,          'READ' : erot.L2_CSR.SPI_IB0_BLF_READ_CTL_0},
#        {'name' : 'spi_ib1',       'reg' : erot.SPI_IB1,        'addr_low_boundary' : 0x934000,    'CTL' : erot.L2_CSR.SPI_IB1_BLF_CTL_0,      'WRITE' : erot.L2_CSR.SPI_IB1_BLF_WRITE_CTL_0,          'READ' : erot.L2_CSR.SPI_IB1_BLF_READ_CTL_0},
#        {'name' : 'uart',          'reg' : erot.UART,           'addr_low_boundary' : 0x974000,    'CTL' : erot.L2_CSR.UART_BLF_CTL_0,         'WRITE' : erot.L2_CSR.UART_BLF_WRITE_CTL_0,             'READ' : erot.L2_CSR.UART_BLF_READ_CTL_0},
    ]

    def write_with_err_code_checking(address, write_value, blocked_priv_id, current_priv_id, current_priv_level):
        if helper.target in ["fpga", "simv_fpga"]:
            test_read_value = 0
            #use jtag to write
            if(current_priv_id == 0):
                helper.j2h_write(address, 0xabcdef00)
            #use fsp to check
            elif (current_priv_id == 2):
                helper.write(address, 0xabcdef00)
            else:
                helper.perror("NOT support priv_id %d" %(current_priv_id))
            if(blocked_priv_id == 0):
                test_read_value = helper.read(address)
            else:
                test_read_value = helper.j2h_read(address)
            if(current_priv_id == blocked_priv_id):
                if (test_read_value == 0xabcdef00):
                    helper.perror("blocked_priv_id has been written in the test value, priv_id is %d" %(current_priv_id))
            else:
                if (test_read_value != 0xabcdef00):
                    helper.perror("NON blocked_priv_id does not write in the test value, priv_id is %d, blocked_priv_id is %d" %(current_priv_id, blocked_priv_id))
                #use jtag to write
                if(current_priv_id == 0):
                    helper.j2h_write(address, write_value)
                #use fsp to check
                elif (current_priv_id == 2):
                    helper.write(address, write_value)
                else:
                    helper.perror("NOT support priv_id %d" %(current_priv_id))
        else:
            addr_list = []
            data_list = []
            cmd_list = []
            addr_list.append(address)
            data_list.append(write_value)
            cmd_list.append(3)
            write_return_list = helper.burst_operation(addr_list, data_list, cmd_list, current_priv_id, 1, current_priv_level)#addr_list, data_list, cmd_list, priv_id, wait_tick, priv_level
            write_rdata = write_return_list[0][0]
            write_resp_err = write_return_list[1][0]
            if(current_priv_id == blocked_priv_id):
                if(write_resp_err != 1):
                    helper.perror("write_resp_err value mismatch, exp: %x, act: %x" %(1, write_resp_err))
                if(write_rdata != 0xdead1100):
                    helper.perror("write_rdata value mismatch, exp: %x, act: %x" %(0xdead1100, write_rdata))
            else:
                if(write_rdata == 0xdead1100):
                    helper.perror("write_rdata is 0xdead1100 while write access is allowed")

    def read_with_err_code_checking(address, blocked_priv_id, current_priv_id, current_priv_level):
        if helper.target in ["fpga", "simv_fpga"]:
            read_rdata = 0
            #use jtag to write
            if(current_priv_id == 0):
                read_rdata = helper.j2h_read(address)
            #use fsp to check
            elif (current_priv_id == 2):
                read_rdata = helper.read(address)
            else:
                helper.perror("NOT support priv_id %d" %(current_priv_id))
            if(current_priv_id == blocked_priv_id):
                if (read_rdata != 0xdead1010):
                    helper.perror("blocked_priv_id %d does not read the error code, exp: %x, act: %x" %(blocked_priv_id, 0xdead1010, read_rdata))
            else:
                if (read_rdata == 0xdead1010):
                    helper.perror("read_rdata is 0xdead1010 while read access is allowed")
        else:
            addr_list = []
            data_list = []
            cmd_list = []
            addr_list.append(address)
            data_list.append(0)
            cmd_list.append(0)
            read_return_list = helper.burst_operation(addr_list, data_list, cmd_list, current_priv_id, 1, current_priv_level)#addr_list, data_list, cmd_list, priv_id, wait_tick, priv_level
            read_rdata = read_return_list[0][0]
            read_resp_err = read_return_list[1][0]
            if(current_priv_id == blocked_priv_id):
                if(read_resp_err != 1):
                    helper.perror("read_resp_err value mismatch, exp: %x, act: %x" %(1, read_resp_err))
                if(read_rdata != 0xdead1010):
                    helper.perror("read_rdata value mismatch, exp: %x, act: %x" %(0xdead1010, read_rdata))
            else:
                if(read_rdata == 0xdead1010):
                    helper.perror("read_rdata is 0xdead1010 while read access is allowed")
                 
    def check_BLF_function(target_list, source_id_list):
        for ip in target_list:
            for source_id in source_id_list:
                if(source_id == 0xffffffbf):
                    blocked_priv_id = 1
                    source = 'SYSCTRL'
                elif(source_id == 0xfffffeff):
                    blocked_priv_id = 0
                    source = 'JTAG'
                elif(source_id == 0xfffff7ff):
                    blocked_priv_id = 2
                    source = 'FSP'
                elif(source_id == 0xffff7fff):
                    blocked_priv_id = 3
                    source = 'OOBHUB'
                #check write block
                helper.log("Checking BLF write block of %s, blocked source: %s" %(ip['name'], source))
                if((ip['name'] == 'l1_csr' or ip['name'] == 'l2_csr') and source_id == 0xfffff7ff):
                    if helper.target in ["fpga", "simv_fpga"]:
                        helper.j2h_write(ip['WRITE'].abs_addr, source_id)
                        helper.j2h_write(ip['READ'].abs_addr, source_id)
                        helper.j2h_write(ip['CTL'].abs_addr, 0x30000)
                    #if(source_id == 0xfffff7ff): #now jtag is blocked, so use sysctrl to write to csr
                    else:
                        helper.write(ip['WRITE'].abs_addr, source_id, 1, 3)
                        helper.write(ip['READ'].abs_addr, source_id, 1, 3)
                        helper.write(ip['CTL'].abs_addr, 0x30000, 1, 3)
                else:
                    if helper.target in ["fpga", "simv_fpga"]:
                        ip['WRITE'].debug_write(source_id)
                        ip['READ'].debug_write(source_id)
                        ip['CTL'].debug_write(0x30000)
                    else:
                        ip['WRITE'].write(source_id)
                        if((ip['name'] == 'l1_csr' or ip['name'] == 'l2_csr') and source_id == 0xfffffeff): #now jtag is blocked, so use sysctrl to write to READ CTRL register
                            helper.write(ip['READ'].abs_addr, source_id, 1, 3)
                            helper.write(ip['CTL'].abs_addr, 0x30000, 1, 3)
                        else:
                            ip['READ'].write(source_id)
                            ip['CTL'].write(0x30000)
                if helper.target in ["fpga", "simv_fpga"]:
                    if (options.Fabric == 'L1'):
                        fpga_allowed_priv_id_list = [0]
                    else:
                        fpga_allowed_priv_id_list = [0, 3]
                    cannot_change_ip_list = ['clock_vrefro_ctl','clock_sys_ctl', 'clock_io_ctl', 'clock_status', 'clock_cmn_pad_ctl', 'clock_podvmon', 'clock_fmon', 'fuse', 'mram_tmc', 'puf_dbg', 'mram_cfg', 'mram_otp', 'mram_mtp', 'mram_mtpr']
                    do_not_have_resp_ip_list = ['boot_qspi_nv_prom_data', 'boot_qspi_nv_prom_2_data', 'qspi0_nv_prom_data', 'qspi0_nv_prom_2_data', 'qspi1_nv_prom_data', 'qspi1_nv_prom_2_data', 'jtag']
                    for priv_id in fpga_allowed_priv_id_list:
                        helper.log("Write %s with priv_id %d" %(ip['name'], priv_id))
                        if ((ip['name'] == 'l1_csr' or ip['name'] == 'l2_csr') and (priv_id != blocked_priv_id)):
                            helper.log("%s should be changed, so not to check the write" % (ip['name']))
                        elif ((ip['name'] in cannot_change_ip_list) and (priv_id != blocked_priv_id)):
                            helper.log("%s cannot be changed, so not to check the write" % (ip['name']))
                        elif ((ip['name'] in do_not_have_resp_ip_list)):
                            helper.log("%s does not have response when use jtag to access, so not to check the write" % (ip['name']))
                        else:
                            if(ip['reg'] != 'none'):
                                write_with_err_code_checking(ip['reg'].base + ip['reg'].reg_list[0].offset, ip['reg'].reg_list[0].reset_val, blocked_priv_id, priv_id, 3)
                            else:
                                write_with_err_code_checking(ip['addr_low_boundary'], 0, blocked_priv_id, priv_id, 3)
                    #check read block
                    helper.log("Checking BLF read block of %s, blocked source: %s" %(ip['name'], source))
                    for priv_id in fpga_allowed_priv_id_list:
                        helper.log("Read %s with priv_id %d" %(ip['name'], priv_id))
                        if ((ip['name'] in do_not_have_resp_ip_list) and (priv_id != blocked_priv_id)):
                            helper.log("%s does not have response when use jtag to access, so not to check the read" % (ip['name']))
                        else:
                            if(ip['reg'] != 'none'):
                                read_with_err_code_checking(ip['reg'].base + ip['reg'].reg_list[0].offset, blocked_priv_id, priv_id, 3)
                            else:
                                read_with_err_code_checking(ip['addr_low_boundary'], blocked_priv_id, priv_id, 3)
                    
                    # reset the BLF config
                    if (source_id == 0xfffffeff):
                        helper.write(ip['CTL'].abs_addr, 0x0)
                        ip['CTL'].poll(BLF_LCK=0,WEN=0,REN=0)
                    else:
                        helper.j2h_write(ip['CTL'].abs_addr, 0x0)
                else:
                    for priv_id in range(1, 4): #jtag cannot call burst_operation to collect error
                        helper.log("Write %s with priv_id %d" %(ip['name'], priv_id))
                        if(ip['reg'] != 'none'):
                            write_with_err_code_checking(ip['reg'].base + ip['reg'].reg_list[0].offset, ip['reg'].reg_list[0].reset_val, blocked_priv_id, priv_id, 3)
                        else:
                            write_with_err_code_checking(ip['addr_low_boundary'], 0, blocked_priv_id, priv_id, 3)
                    #check read block
                    helper.log("Checking BLF read block of %s, blocked source: %s" %(ip['name'], source))
                    for priv_id in range(1, 4):
                        helper.log("Read %s with priv_id %d" %(ip['name'], priv_id))
                        if(ip['reg'] != 'none'):
                            read_with_err_code_checking(ip['reg'].base + ip['reg'].reg_list[0].offset, blocked_priv_id, priv_id, 3)
                        else:
                            read_with_err_code_checking(ip['addr_low_boundary'], blocked_priv_id, priv_id, 3)
    
    def check_block_mnoc(target_list):
        sub_id = 0
        if(options.Fabric == 'L1_MNOC'):
            max_subid = 16 #sub_id range of FSP id 0~f
        elif(options.Fabric == 'L2_MNOC'):
            max_subid = 3 #sub_id range of FSP id 0~2
        for ip in target_list:
            #check write block
            if(sub_id != 0):
                sub_id = sub_id + 1
            helper.log("Checking BLF write block of %s, blocked source: MNOC" %ip['name'])
            ip['WRITE'].write(0xFFEFFFFF)
            ip['READ'].write(0xFFEFFFFF)
            ip['CTL'].write(0x30000)
            for priv_id in range(1, 4): #jtag cannot call burst_operation to collect error
                addr_list = []
                data_list = []
                cmd_list = []
                helper.log("Write %s with priv_id %d" %(ip['name'], priv_id))
                if(ip['reg'] != 'none'):
                    addr_list.append(ip['reg'].base + ip['reg'].reg_list[0].offset)
                    data_list.append(ip['reg'].reg_list[0].reset_val)
                    cmd_list.append(3)
                else:
                    addr_list.append(ip['addr_low_boundary'])
                    data_list.append(0)
                    cmd_list.append(3)
                
                write_return_list = helper.burst_operation(addr_list, data_list, cmd_list, priv_id, 1, 3)#addr_list, data_list, cmd_list, priv_id, wait_tick, priv_level
                write_rdata_0 = write_return_list[0][0]
                write_resp_err_0 = write_return_list[1][0]
                if((sub_id%max_subid == 0) and ((options.Fabric == 'L1_MNOC' and priv_id == 2) or (options.Fabric == 'L2_MNOC' and priv_id == 3))): #transaction with sub_id 0 is from MNOC
                    if(write_resp_err_0 != 1):
                        helper.perror("write_resp_err value mismatch, exp: %x, act: %x" %(1, write_resp_err_0))
                    if(write_rdata_0 != 0xdead1100):
                        helper.perror("write_rdata value mismatch, exp: %x, act: %x" %(0xdead1100, write_rdata_0))
                else:
                    if(write_rdata_0 == 0xdead1100):
                        helper.perror("write_rdata is 0xdead1100 while write access is allowed")
            #check read block
            sub_id = sub_id + 1
            helper.log("Checking BLF read block of %s, blocked source: MNOC" %ip['name'])
            for priv_id in range(1, 4):
                addr_list = []
                data_list = []
                cmd_list = []
                helper.log("Read %s with priv_id %d" %(ip['name'], priv_id))
                if(ip['reg'] != 'none'):
                    addr_list.append(ip['reg'].base + ip['reg'].reg_list[0].offset)
                    data_list.append(0)
                    cmd_list.append(0)
                else:
                    addr_list.append(ip['addr_low_boundary'])
                    data_list.append(0)
                    cmd_list.append(0)
                read_return_list = helper.burst_operation(addr_list, data_list, cmd_list, priv_id, 1, 3)#addr_list, data_list, cmd_list, priv_id, wait_tick, priv_level
                read_rdata_0 = read_return_list[0][0]
                read_resp_err_0 = read_return_list[1][0]
                if((sub_id%max_subid == 0) and ((options.Fabric == 'L1_MNOC' and priv_id == 2) or (options.Fabric == 'L2_MNOC' and priv_id == 3))):
                    if(read_resp_err_0 != 1):
                        helper.perror("read_resp_err value mismatch, exp: %x, act: %x" %(1, read_resp_err_0))
                    if(read_rdata_0 != 0xdead1010):
                        helper.perror("read_rdata value mismatch, exp: %x, act: %x" %(0xdead1010, read_rdata_0))
                else:
                    if(read_rdata_0 == 0xdead1010):
                        helper.perror("read_rdata is 0xdead1010 while read access is allowed")

    def check_block_1f(target_list):
        #check blocking when source id mapping in fabric is disabled
        if(options.Fabric == 'L1_DISABLE_MAPPING'):
            priv_id_list = [1, 2]
        elif(options.Fabric == 'L2_DISABLE_MAPPING'):
            priv_id_list = [3]
        for ip in target_list:
            helper.log("Checking BLF write block of %s, blocked source: ALL(0x1f)" %ip['name'])
            ip['WRITE'].write(0x7fffffff)
            ip['READ'].write(0x7fffffff)
            ip['CTL'].write(0x30000)
            if helper.target in ["fpga", "simv_fpga"]:
                helper.log("default fuse options are 0")
            else:
                helper.hdl_force(fuse_path+'opt_priv_sec_en', 0)
                helper.hdl_force(fuse_path+'opt_secure_pri_source_isolation_en', 0)
            for priv_id in priv_id_list: #jtag cannot call burst_operation to collect error
                addr_list = []
                data_list = []
                cmd_list = []
                address_test = 0
                data_test = 0
                helper.log("Write %s with priv_id %d" %(ip['name'], priv_id))
                if(ip['reg'] != 'none'):
                    addr_list.append(ip['reg'].base + ip['reg'].reg_list[0].offset)
                    data_list.append(ip['reg'].reg_list[0].reset_val)
                    cmd_list.append(3)
                    address_test = ip['reg'].base + ip['reg'].reg_list[0].offset
                    data_test = ip['reg'].reg_list[0].reset_val
                else:
                    addr_list.append(ip['addr_low_boundary'])
                    data_list.append(0)
                    cmd_list.append(3)
                    address_test = ip['addr_low_boundary']
                    data_test = 0
                
                if helper.target in ["fpga", "simv_fpga"]:
                    helper.write(address_test, 0xabcdef00,priv_id,1,3)
                    test_read_value = helper.j2h_read(address_test)
                    if (test_read_value == 0xabcdef00):
                        helper.perror("priv_id has been written in the test value, priv_id is %d" %(priv_id))
                        helper.write(address_test, data_test,priv_id,1,3)
                else:
                    write_return_list = helper.burst_operation(addr_list, data_list, cmd_list, priv_id, 1, 3)#addr_list, data_list, cmd_list, priv_id, wait_tick, priv_level
                    write_rdata_0 = write_return_list[0][0]
                    write_resp_err_0 = write_return_list[1][0]
                    if(write_resp_err_0 != 1):
                        helper.perror("write_resp_err value mismatch, exp: %x, act: %x" %(1, write_resp_err_0))
                    if(write_rdata_0 != 0xdead1100):
                        helper.perror("write_rdata value mismatch, exp: %x, act: %x" %(0xdead1100, write_rdata_0))
            helper.log("Checking BLF read block of %s, blocked source: ALL(0x1f)" %ip['name'])
            for priv_id in priv_id_list:
                addr_list = []
                data_list = []
                cmd_list = []
                address_test = 0
                data_test = 0
                helper.log("Read %s with priv_id %d" %(ip['name'], priv_id))
                if(ip['reg'] != 'none'):
                    addr_list.append(ip['reg'].base + ip['reg'].reg_list[0].offset)
                    data_list.append(0)
                    cmd_list.append(0)
                    address_test = ip['reg'].base + ip['reg'].reg_list[0].offset
                    data_test = 0
                else:
                    addr_list.append(ip['addr_low_boundary'])
                    data_list.append(0)
                    cmd_list.append(0)
                    address_test = ip['addr_low_boundary']
                    data_test = 0
                
                if helper.target in ["fpga", "simv_fpga"]:
                    read_rdata = helper.read(address_test,priv_id,1,3)
                    if (read_rdata != 0xdead1010):
                        helper.perror("priv_id %d does not read the error code, exp: %x, act: %x" %(priv_id, 0xdead1010, read_rdata))
                else:
                    read_return_list = helper.burst_operation(addr_list, data_list, cmd_list, priv_id, 1, 3)#addr_list, data_list, cmd_list, priv_id, wait_tick, priv_level
                    read_rdata_0 = read_return_list[0][0]
                    read_resp_err_0 = read_return_list[1][0]
                    if(read_resp_err_0 != 1):
                        helper.perror("read_resp_err value mismatch, exp: %x, act: %x" %(1, read_resp_err_0))
                    if(read_rdata_0 != 0xdead1010):
                        helper.perror("read_rdata value mismatch, exp: %x, act: %x" %(0xdead1010, read_rdata_0))

            if helper.target in ["fpga", "simv_fpga"]:
                helper.log("Should not force to 1 when fpga because cannot be overrided back to 0 when option is opt_secure_pri_source_isolation_en")
            else:
                helper.hdl_force(fuse_path+'opt_priv_sec_en', 1)
                helper.hdl_force(fuse_path+'opt_secure_pri_source_isolation_en', 1)

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
        
        if ((options.Fabric == 'L1_DISABLE_MAPPING') or (options.Fabric == 'L2_DISABLE_MAPPING')):
            helper.log("Do not need to force the fuse options to 1")
        else:
            helper.log("Force fabric fuse 1 start")
            test_api.fuse_opts_override("opt_secure_pri_source_isolation_en", 1)
            # BLF does not care the PL
            #test_api.fuse_opts_override("opt_priv_sec_en", 1)
            helper.log("Force fabric fuse 1 done")
    else:
        fuse_path = 'ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.'
        helper.log("Force fabric fuse 1 start")
        helper.hdl_force(fuse_path+'opt_priv_sec_en', 1)
        helper.hdl_force(fuse_path+'opt_secure_pri_source_isolation_en', 1)
        helper.log("Force fabric fuse 1 done")
    #test_api.boot_qspi_init()
    #test_api.boot_qspi_clk_init()
    #test_api.qspi0_init()
    #test_api.qspi1_init()
    #test_api.ap0_qspi_init()
    #test_api.ap1_qspi_init()

    if(options.Fabric == 'L1'):
        if helper.target in ["fpga", "simv_fpga"]:
            source_id_list = [0xffffffbf, 0xfffffeff, 0xfffff7ff] # JTAG, FSP
        else:
            source_id_list = [0xffffffbf, 0xfffffeff, 0xfffff7ff] # SYSCTRL, JTAG, FSP
        check_BLF_function(L1_FABRIC_TARGET, source_id_list)
    elif(options.Fabric == 'L2'):
        source_id_list = [0xffff7fff] #OOBHUB
        check_BLF_function(L2_FABRIC_TARGET, source_id_list)
    # TODO how to change the sub id ???
    #elif(options.Fabric == 'L1_MNOC'):
    #    check_block_mnoc(L1_FABRIC_TARGET)
    #elif(options.Fabric == 'L2_MNOC'):
    #    check_block_mnoc(L2_FABRIC_TARGET)
    elif(options.Fabric == 'L1_DISABLE_MAPPING'):
        check_block_1f(L1_FABRIC_TARGET)
    elif(options.Fabric == 'L2_DISABLE_MAPPING'):
        check_block_1f(L2_FABRIC_TARGET)
    else:
        helper.perror("Wrong --Fabric %s" % options.monitor)
