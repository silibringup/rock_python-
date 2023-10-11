#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import * 
import re


LIGHT_ON_LIST = [
    #{'name' : 'I2C_IB0',        'reg' : erot.I2C_IB0.I2C_CMD_DATA1_0                    }, 
    {'name' : 'I2C_IB1',        'reg' : erot.I2C_IB1.I2C_CMD_DATA2_0                    }, 
    {'name' : 'IO_EXPANDER',    'reg' : erot.IO_EXPANDER.I2C_CMD_DATA2_0                }, 
    {'name' : 'SPI_IB0',        'reg' : erot.SPI_IB0.COMMAND2_0                         }, 
    {'name' : 'SPI_IB1',        'reg' : erot.SPI_IB1.COMMAND2_0                         }, 
    {'name' : 'OOBHUB_SPI',     'reg' : erot.OOBHUB_SPI.COMMAND2_0                      }, 
    {'name' : 'QSPI0',          'reg' : erot.QSPI0.QSPI.CMB_SEQ_ADDR_0                  }, 
    {'name' : 'QSPI1',          'reg' : erot.QSPI1.QSPI.CMB_SEQ_ADDR_0                  }, 
    {'name' : 'BOOT_QSPI',      'reg' : erot.BOOT_QSPI.QSPI.CMB_SEQ_ADDR_0              }, 
    {'name' : 'I3C_IB0' ,       'reg' : erot.I3C_IB0.QUEUE_THLD_CTRL_0                  }, 
    {'name' : 'I3C_IB1' ,       'reg' : erot.I3C_IB1.QUEUE_THLD_CTRL_0                  }, 
    {'name' : 'GPIO',           'reg' : erot.GPIO.A_VM_00_0                             }, 
    {'name' : 'MRAM',           'reg' : erot.MRAM.mram_cfg_b_mtp_region_start_0_0       }, 
    {'name' : 'CLOCK' ,         'reg' : erot.CLOCK.NVEROT_CLOCK_IO_CTL.DEBUG_PROBE_CFG_0     }, 
    {'name' : 'RESET',          'reg' : erot.RESET.NVEROT_RESET_CFG.SW_POR_LOG_RST_0    }, 
    {'name' : 'THERM',          'reg' : erot.THERM.DUMMY_0                              }, 
    {'name' : 'UART' ,          'reg' : erot.UART.UARTIBRD_0                            }, 
    {'name' : 'FUSE' ,          'reg' : erot.FUSE.EN_SW_OVERRIDE_0                      }, 
    {'name' : 'RTS'  ,          'reg' : erot.RTS.MER_0                                  }, 
    {'name' : 'OOBHUB',         'reg' : erot.OOBHUB.RCV_INDIRECT_DATA_0                 }, 
    {'name' : 'NV_PBUS',        'reg' : erot.NV_PBUS.DEBUG_0_0                          }, 
    {'name' : 'SPI_MON0',       'reg' : erot.SPI_MON0.aper_lock_0          		}, 
    {'name' : 'SPI_MON1',       'reg' : erot.SPI_MON1.aper_lock_0         		} 
]

with Test(sys.argv) as t:
    def parse_args():
        t.parser.add_argument("--unit", action='store', help="Unit To Light On, Support Regular Expression", default='.*')
        opts, unknown = t.parser.parse_known_args(sys.argv[1:])
        return opts

    def validate_unit(unit):
        LOG("VALIDATING UNIT %s" % unit['name'])   
        unit['reg'].write(0x5a5a5a5a)
        rd = unit['reg'].read()
        print(rd)
        if rd.value != 0x5a5a5a5a & unit['reg'].read_mask:
            helper.perror("Reg Read/Write Fail -> %s" % str(unit['reg']))
    
    options = parse_args() 
    LOG("Start Verification with UNIT Pattern = %s" % options.unit)

    test_api.reset_init()

    for unit in LIGHT_ON_LIST:
        if re.match(f'^{options.unit}$', unit['name']) or options.unit == 'ALL' :
            validate_unit(unit) 
        else:
            LOG("SKIP UNIT %s" % unit['name']) 

