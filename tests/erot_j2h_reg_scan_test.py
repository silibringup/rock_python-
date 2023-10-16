#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import * 
import re
import argparse
import os

RESET_BASE_ADDR =  0x33000

REG_LIST = [
    {'addr': 0x1080,    'mask': 0xffffffff, 'name': 'NV_PBUS',     'reg': erot.NV_PBUS.DEBUG_0_0}, 
    {'addr': 0x204c,    'mask': 0x1,        'name': 'THERM',       'reg': erot.THERM.DUMMY_0},
    {'addr': 0x25030,   'mask': 0x300ffff,  'name': 'CLOCK' ,      'reg': erot.CLOCK.NVEROT_CLOCK_IO_CTL.DEBUG_PROBE_CFG_0},
    {'addr': 0x33000,   'mask': 0x1,        'name': 'RESET',       'reg': erot.RESET.NVEROT_RESET_CFG.SW_POR_LOG_RST_0},
    {'addr': 0x431a8,   'mask': 0xffffffff, 'name': 'BOOT_QSPI',   'reg': erot.BOOT_QSPI.QSPI.CMB_SEQ_ADDR_0},
    {'addr': 0x1461a8,  'mask': 0xffffffff, 'name': 'QSPI0',       'reg': erot.QSPI0.QSPI.CMB_SEQ_ADDR_0},
    {'addr': 0x2491a8,  'mask': 0xffffffff, 'name': 'QSPI1',       'reg': erot.QSPI1.QSPI.CMB_SEQ_ADDR_0},
    {'addr': 0x464000,  'mask': 0x1,        'name': 'SPI_MON0',    'reg': erot.SPI_MON0.aper_lock_0}, 
    {'addr': 0x484000,  'mask': 0x1,        'name': 'SPI_MON1',    'reg': erot.SPI_MON1.aper_lock_0},
    {'addr': 0x4a3024,  'mask': 0xffffffff, 'name': 'RTS'  ,       'reg': erot.RTS.MER_0},
    {'addr': 0x820040,  'mask': 0x1,        'name': 'FUSE' ,       'reg': erot.FUSE.EN_SW_OVERRIDE_0},
    {'addr': 0x8aa15c,  'mask': 0xffffffff, 'name': 'OOBHUB',      'reg': erot.OOBHUB.RCV_INDIRECT_DATA_0},
    {'addr': 0x8f308c,  'mask': 0xffff    , 'name': 'FSP',         'reg': erot.FSP.SCPM_FSP_DATAPATH_DEL_SEL_0},
    {'addr': 0x8f4004,  'mask': 0xffffffff, 'name': 'OOBHUB_SPI',  'reg': erot.OOBHUB_SPI.COMMAND2_0},
    {'addr': 0x904004,  'mask': 0xffffffff, 'name': 'SPI_IB0',     'reg': erot.SPI_IB0.COMMAND2_0},
    {'addr': 0x91400c,  'mask': 0xffffffff, 'name': 'I2C_IB0',     'reg': erot.I2C_IB0.I2C_CMD_DATA1_0}, 
    {'addr': 0x92401c,  'mask': 0xffffffff, 'name': 'I3C_IB0' ,    'reg': erot.I3C_IB0.QUEUE_THLD_CTRL_0},
    {'addr': 0x934004,  'mask': 0xffffffff, 'name': 'SPI_IB1',     'reg': erot.SPI_IB1.COMMAND2_0},
    {'addr': 0x944010,  'mask': 0xffffffff, 'name': 'I2C_IB1',     'reg': erot.I2C_IB1.I2C_CMD_DATA2_0},
    {'addr': 0x95401c,  'mask': 0xffffffff, 'name': 'I3C_IB1' ,    'reg': erot.I3C_IB1.QUEUE_THLD_CTRL_0},
    {'addr': 0x964010,  'mask': 0xffffffff, 'name': 'IO_EXPANDER', 'reg': erot.IO_EXPANDER.I2C_CMD_DATA2_0}, 
    {'addr': 0x974024,  'mask': 0xffff,     'name': 'UART' ,       'reg': erot.UART.UARTIBRD_0},
    {'addr': 0x984000,  'mask': 0xffff,     'name': 'GPIO',        'reg': erot.GPIO.A_VM_00_0},
    {'addr': 0xfc000c,  'mask': 0xffffffff, 'name': 'MRAM',        'reg': erot.MRAM.mram_cfg_b_mtp_region_start_0_0} 
]

with Test(sys.argv) as t:
    def parse_args():
        t.parser.add_argument("--unit", action='store', help="Unit To Light On, Support Regular Expression", default='.*')
        opts, unknown = t.parser.parse_known_args(sys.argv[1:])
        return opts
    def j2h_reset_init():
        helper.j2h_write(RESET_BASE_ADDR + 0X4, 0x1) #erot.RESET.NVEROT_RESET_CFG.SW_GPIO_CTRL_RST_0.update(RESET_GPIO_CTRL=1)
        helper.j2h_write(RESET_BASE_ADDR + 0X8, 0x1)# erot.RESET.NVEROT_RESET_CFG.SW_SPIMON0_RST_0.update(RESET_SPIMON0=1)
        helper.j2h_write(RESET_BASE_ADDR + 0Xc, 0x1)# erot.RESET.NVEROT_RESET_CFG.SW_SPIMON1_RST_0.update(RESET_SPIMON1=1)
        helper.j2h_write(RESET_BASE_ADDR + 0X14, 0x1)# erot.RESET.NVEROT_RESET_CFG.SW_IB0_SPI_RST_0.update(RESET_IB0_SPI=1)
        helper.j2h_write(RESET_BASE_ADDR + 0X18, 0x1)# erot.RESET.NVEROT_RESET_CFG.SW_IB1_SPI_RST_0.update(RESET_IB1_SPI=1)
        helper.j2h_write(RESET_BASE_ADDR + 0X1c, 0x1)# erot.RESET.NVEROT_RESET_CFG.SW_OOB_SPI_RST_0.update(RESET_OOB_SPI=1)
        helper.j2h_write(RESET_BASE_ADDR + 0X20, 0x1)# erot.RESET.NVEROT_RESET_CFG.SW_IB0_I2C_RST_0.update(RESET_IB0_I2C=1)
        helper.j2h_write(RESET_BASE_ADDR + 0X24, 0x1)# erot.RESET.NVEROT_RESET_CFG.SW_IB1_I2C_RST_0.update(RESET_IB1_I2C=1)
        helper.j2h_write(RESET_BASE_ADDR + 0X28, 0x1)# erot.RESET.NVEROT_RESET_CFG.SW_IO_EXP_RST_0.update(RESET_IO_EXP=1)
        helper.j2h_write(RESET_BASE_ADDR + 0X2c, 0x1)# erot.RESET.NVEROT_RESET_CFG.SW_UART_RST_0.update(RESET_UART=1)

        helper.wait_sim_time('us', 50) # add some delay

    def j2h_validate_unit(unit):
        LOG("VALIDATING UNIT %s" % unit['name'])   
        helper.j2h_write(unit['addr'], 0x5a5a5a5a)
        rd = helper.j2h_read(unit['addr'])
        if rd != 0x5a5a5a5a & unit['reg'].read_mask:
            helper.perror(f'{unit["name"]} read out {hex(rd)} but expect 0x5a5a5a5a')
        else:
            helper.pinfo(f'        {unit["name"]} read out data {hex(rd)}')

    options = parse_args() 

    helper.pinfo("JTAG J2H Reg Scan Test Starts!")
    helper.wait_sim_time('us', 50)
    if helper.target == "simv_fpga":
        helper.hdl_force('ntb_top.u_nv_fpga_dut.u_nv_top_fpga.u_nv_top_wrapper.u_nv_top.nvjtag_sel', 1)
    if helper.target != "simv_fpga":
        helper.pinfo(f'remove fuse force')
        #helper.hdl_force('ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.opt_nvjtag_protection_enable_final', 0)
        #helper.hdl_force('ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.opt_secure_jtag_secureID_valid', 0)
        #helper.hdl_force('ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.static_chip_option_sense_done', 1)
        #helper.hdl_force('ntb_top.u_nv_top.u_sra_sys0.u_l1_cluster.u_NV_fuse.opt_secure_jtag_secureID_valid_inv', 1)
        helper.hdl_force('ntb_top.u_nv_top.nvjtag_sel', 1)

    helper.jtag.Led(1)  # Start Testing
    
    helper.jtag.Reset(0)
    helper.jtag.DRScan(100, hex(0x0)) #add some delay as jtag only work when nvjtag_sel stable in real case
    helper.jtag.Reset(1)  

    #unlock j2h interface
    helper.pinfo(f'j2h_unlock sequence start')
    helper.j2h_unlock()
    helper.pinfo(f'j2h_unlock sequence finish')
    
    #poll L3 reset released
    cnt = 0
    l3_released = 0
    while l3_released == 0 and cnt < 100:
        rd = helper.j2h_read(0x33010, check_ack=False) #erot.RESET.NVEROT_RESET_CFG.SW_L3_RST_0
        cnt += 1
        if rd & 0x1 == 1:
            l3_released = 1
    if l3_released == 0:
        helper.perror(f'L3_reset not released before w/r registers')   
    
    j2h_reset_init()

    LOG("Start Verification with UNIT Pattern = %s" % options.unit)

    for unit in REG_LIST:
        if re.match(f'^{options.unit}$', unit['name']) or options.unit == 'ALL' :
            j2h_validate_unit(unit) 
        else:
            LOG("SKIP UNIT %s" % unit['name']) 
    
    helper.jtag.Led(0)  # End Testing
    
    helper.pinfo("JTAG J2H Reg Scan Test Ends!")   