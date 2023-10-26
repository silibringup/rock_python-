#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
import os
import re
from driver import *
from driver.components.spi_mst import SPI_SCLK_FREQ_SEL

golden_value = 0xc8 

rt_value1=0x0658c274

with Test(sys.argv) as t:
    AP0_SPI = 0
    AP1_SPI = 1
    BMC_SPI = 2

    def parse_args():
        t.parser.add_argument("--clkratio", "-c", action='store_true', help="Enable 75Mhz clk", default=False)
        opts, unknown = t.parser.parse_known_args(sys.argv[1:])
        return opts


    #config slave
    def setup_sink(spi):
        spi.COMMAND2_0.update(SI_RM_CMD_BIT_LENGTH=7, SI_RM_ADDRESS_BIT_LENGTH=23)
        spi.MISC_0.update(CLKEN_OVERRIDE=1,EXT_CLK_EN=1)
        spi.MISC_0.poll(timeout=100,CLKEN_OVERRIDE=1,EXT_CLK_EN=1)
        #IMR ONLY
        spi.DMA_BLK_SIZE_0.update(DMA_BLOCK_SIZE=5)
        spi.DMA_BLK_SIZE_0.poll(timeout=30,DMA_BLOCK_SIZE=5)
        spi.COMMAND_0.update(SI_RM_EN='ENABLE',Rx_EN='ENABLE',Tx_EN='ENABLE',M_S='SLAVE',BIT_LENGTH=7,CS_POL_INACTIVE0=1,PACKED=1)
        spi.COMMAND_0.update(IMR_CONFIG_LOAD=1)
        spi.COMMAND_0.update(PIO='PIO')

    def regroup_data(number, in_data, mode=0):
        if mode == 0: #PACKED, LSBi=0, LSBy=0
            byte_array = in_data.to_bytes(number,'little')
            out_data = int.from_bytes(byte_array, 'big')
            return out_data

    def wait_sink_done(spi):
        spi.TRANSFER_STATUS_0.poll(timeout=100,RDY=1)
        rd = spi.RX_FIFO_0.read()
        read_data = regroup_data(4, rd.value,0)
        if read_data != rt_value1:
            helper.perror("Reg Read/Write 1st Fail -> %s" % str(read_data))

        rd = spi.RX_FIFO_0.read()
        #read_data = regroup_data(2, rd.value,0)
        read_data = rd.value
        if read_data != golden_value:
            helper.perror("Reg Read/Write 2nd Fail -> %s" % str(read_data))

    def spi_vip_write(spi,cs):
        helper.spi_write(spi_port=spi, cs_id=cs, n_data_lane=1, data=[golden_value], 
            n_instruction_lane=1, n_instruction_bits=8, instruction=[0x06],
            n_address_lane=1, n_address_bits=24, address=[0x58,0xc2,0x74])



    LOG("START SPI SLAVE RX TEST")

    #test_api.ap0_qspi_init()
    #test_api.ap1_qspi_init()
    #test_api.oob_dspi_init()

    options = parse_args()

    if options.clkratio :
        helper.spi_set_sclk_frequency(spi_port=AP0_SPI, freq_sel=SPI_SCLK_FREQ_SEL.SPI_SCLK_75MHZ)
        helper.spi_set_sclk_frequency(spi_port=AP1_SPI, freq_sel=SPI_SCLK_FREQ_SEL.SPI_SCLK_75MHZ)
        helper.spi_set_sclk_frequency(spi_port=BMC_SPI, freq_sel=SPI_SCLK_FREQ_SEL.SPI_SCLK_75MHZ)

    test_api.enable_vip_connection()
    test_api.reset_init()

    setup_sink(erot.SPI_IB0)
    spi_vip_write(AP0_SPI,2)
    wait_sink_done(erot.SPI_IB0)

    #setup_sink(erot.SPI_IB1)
    #spi_vip_write(AP1_SPI,2)
    #wait_sink_done(erot.SPI_IB1)

    #setup_sink(erot.OOBHUB_SPI)
    #spi_vip_write(BMC_SPI,0)
    #wait_sink_done(erot.OOBHUB_SPI)





