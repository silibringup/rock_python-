#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
import os
import re
from driver import *
from driver.components.spi_mst import SPI_SCLK_FREQ_SEL

golden_value = 0x1234
rx_value = 0xf055ff55

with Test(sys.argv) as t:
    AP0_SPI = 0
    AP1_SPI = 1
    BMC_SPI = 2

    def parse_args():
        t.parser.add_argument("--clkratio", "-c", action='store_true', help="Enable 75Mhz clk", default=False)
        opts, unknown = t.parser.parse_known_args(sys.argv[1:])
        return opts


    #config slave
    def setup_transmit(spi):
        spi.COMMAND2_0.update(SI_RM_DUMMY_CYC_LENGTH=8,SI_RM_CMD_BIT_LENGTH=7, SI_RM_ADDRESS_BIT_LENGTH=23)#no dummy
        spi.TX_FIFO_0.write(golden_value)
        #IMR ONLY
        spi.DMA_BLK_SIZE_0.update(DMA_BLOCK_SIZE=5)
        spi.DMA_BLK_SIZE_0.poll(timeout=30,DMA_BLOCK_SIZE=5)

        spi.MISC_0.update(CLKEN_OVERRIDE=1,EXT_CLK_EN=1)
        spi.MISC_0.poll(timeout=100,CLKEN_OVERRIDE=1,EXT_CLK_EN=1)
        spi.COMMAND_0.update(M_S='SLAVE',SI_RM_EN='ENABLE',BIT_LENGTH=7,Rx_EN='ENABLE',Tx_EN='ENABLE',CS_POL_INACTIVE0=1,PACKED=1)
        spi.COMMAND_0.update(IMR_CONFIG_LOAD=1)
        spi.COMMAND_0.update(PIO='PIO')

    def wait_transmit_ready(spi):
        spi.TRANSFER_STATUS_0.poll(timeout=100,RDY=1)

    def regroup_data(num, in_data, mode=0):
        if mode == 0: #PACKED, LSBi=0, LSBy=0
            byte_array = in_data.to_bytes(num,'little')
            out_data = int.from_bytes(byte_array, 'big')
            return out_data

    def check_tx_data(spi,cs):
        read_bytes = helper.spi_read(spi_port=spi, cs_id=cs, n_data_lane=1, nbr_rd_bytes=2,n_instruction_lane=1, n_instruction_bits=8, instruction=[0xf0], n_address_lane=1, n_address_bits=24, address=[0x55,0xff,0x55],dummy_cycles=8)
        read_value = int.from_bytes(read_bytes, "big")
        vip_rd = regroup_data(2,read_value)
        if vip_rd != golden_value:
            helper.perror("Reg Read/Write Fail -> %s, %s" % (str(vip_rd),str(read_bytes)))
        else:
            LOG("Check Passed for %s" % spi)

    def check_rx_fifo(spi):
        rd = spi.RX_FIFO_0.read()
        read_data = regroup_data(4, rd.value,0)
        if read_data != rx_value:
            helper.perror("Reg Read/Write RX FIFO Fail -> %s" % str(read_data))

    def ap0_tristate_init():
        erot.PADCTRL_E.AP0_QSPI_CLK_0.update(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_CS0_N_0.update(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_CS1_N_0.update(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_IO0_0.update(TRISTATE=1)
        erot.PADCTRL_E.AP0_QSPI_IO1_0.update(TRISTATE=1)
        erot.PADCTRL_E.AP0_QSPI_IO2_0.update(TRISTATE=1)
        erot.PADCTRL_E.AP0_QSPI_IO3_0.update(TRISTATE=1)

        erot.PADCTRL_E.AP0_QSPI_CLK_0.poll(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_CS0_N_0.poll(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_CS1_N_0.poll(TRISTATE=0)
        erot.PADCTRL_E.AP0_QSPI_IO0_0.poll(TRISTATE=1)
        erot.PADCTRL_E.AP0_QSPI_IO1_0.poll(TRISTATE=1)
        erot.PADCTRL_E.AP0_QSPI_IO2_0.poll(TRISTATE=1)
        erot.PADCTRL_E.AP0_QSPI_IO3_0.poll(TRISTATE=1)



    LOG("START SPI SLAVE TX TEST")

    #test_api.ap0_qspi_init()
    #ap0_tristate_init()

    options = parse_args()

    if options.clkratio :
        helper.spi_set_sclk_frequency(spi_port=AP0_SPI, freq_sel=SPI_SCLK_FREQ_SEL.SPI_SCLK_75MHZ)
        helper.spi_set_sclk_frequency(spi_port=AP1_SPI, freq_sel=SPI_SCLK_FREQ_SEL.SPI_SCLK_75MHZ)
        helper.spi_set_sclk_frequency(spi_port=BMC_SPI, freq_sel=SPI_SCLK_FREQ_SEL.SPI_SCLK_75MHZ)

    test_api.enable_vip_connection()
    test_api.reset_init()

    setup_transmit(erot.SPI_IB0)
    check_tx_data(AP0_SPI,2)
    check_rx_fifo(erot.SPI_IB0)

    #setup_transmit(erot.SPI_IB1)
    #check_tx_data(AP1_SPI,2)
    #check_rx_fifo(erot.SPI_IB1)

    #setup_transmit(erot.OOBHUB_SPI)
    #check_tx_data(BMC_SPI,0)
    #check_rx_fifo(erot.OOBHUB_SPI)


