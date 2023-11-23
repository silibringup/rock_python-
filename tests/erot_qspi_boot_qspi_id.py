#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import * 

with Test(sys.argv) as t:

    def parse_args():
        t.parser.add_argument("--qspi", action='store', help="Verify QSPI INTI and AP to access flash", default='0')
        return t.parser.parse_args(sys.argv[1:])

    def send_read_1_1_x_cmd_flash(spi,cs,opcode,address,address_size,data_line,data_byte,dummy_cycle):
        test_api.config_qspi_cmb_cmd(spi,opcode,0,address,address_size)  
        spi.DMA_BLK_SIZE_0.write(data_byte)
        test_api.send_cmd(spi,0,1,31,data_line,dummy_cycle,cs) 

    LOG("START QSPI INI TEST") 
    test_api.connect_to_micron_flash()

    helper.wait_sim_time("us", 600)
    test_api.boot_qspi_init()
    test_api.boot_qspi_clk_init()
    erot.CLOCK.NVEROT_CLOCK_SYS_CTL.SW_BOOT_QSPI_CLK_RCM_CFG_0.update(DIV_SEL_DIV_SW=7)
    send_read_1_1_x_cmd_flash(erot.BOOT_QSPI.QSPI,0,0x90,0,24,0,0,0x0)
    rd = erot.BOOT_QSPI.QSPI.RX_FIFO_0.read()
    helper.pinfo(f'boot qspi read out winbond id: {rd.value}')   
