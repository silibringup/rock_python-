#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
import os
import re
from driver import *
from driver.components.spi_mst import SPI_SCLK_FREQ_SEL

golden_value = 0xa5a5c6c6
golden_value_status = 0xaf734208

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
        spi.COMMAND2_0.update(SI_RM_DUMMY_CYC_LENGTH=0, SI_RM_DUAL_SPI_ENABLE=1)#no dummy
        spi.TX_FIFO_0.write(golden_value)#trigger STATUS
        #IMR ONLY
        #spi.DMA_BLK_SIZE_0.update(DMA_BLOCK_SIZE=5)
        #spi.DMA_BLK_SIZE_0.poll(timeout=30,DMA_BLOCK_SIZE=5)

        #SET STATUS POLL
        spi.POLL_STATUS_REGISTER_0.update(SI_RM_Poll_Status_Data = golden_value_status)

        spi.MISC_0.update(CLKEN_OVERRIDE=1,EXT_CLK_EN=1)
        spi.MISC_0.poll(timeout=100,CLKEN_OVERRIDE=1,EXT_CLK_EN=1)
        spi.COMMAND_0.update(M_S='SLAVE',SI_RM_EN='ENABLE',BIT_LENGTH=31,Rx_EN='ENABLE',Tx_EN='ENABLE',CS_POL_INACTIVE0=1,PACKED=1)
        spi.COMMAND_0.update(IMR_CONFIG_LOAD=1)
        spi.COMMAND_0.update(PIO='PIO')

    def wait_transmit_ready(spi):
        spi.TRANSFER_STATUS_0.poll(timeout=100,RDY=1)

    def regroup_data(in_data, mode=0):
        buff = in_data
        out = 0
        for i in range (0,32):
            bit = buff & 0x0001
            buff = buff >> 1
            out = (out << 1) | bit

        LOG("in is %x, out is %x" % (in_data,out))
        return out

    def check_tx_data(spi,cs):
        helper.pinfo('start qspi vip read')
        read_bytes = helper.spi_read(spi_port=spi, cs_id=cs, n_data_lane=2, nbr_rd_bytes=4,n_instruction_lane=1, n_instruction_bits=8, instruction=[0x80], n_address_lane=1, n_address_bits=0, address=[])
        helper.pinfo('end qspi vip read')
        read_value = int.from_bytes(read_bytes, "big")
        vip_rd = regroup_data(read_value)
        helper.pinfo(f'end qspi vip read : {hex(vip_rd)}')
        if vip_rd != golden_value_status:
            helper.perror("Reg Read/Write Fail -> %s, %s" % (str(vip_rd),str(read_bytes)))

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



    LOG("START SPI IMR STATUS POLL TEST")

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

    #setup_transmit(erot.SPI_IB1)
    #check_tx_data(AP1_SPI,2)

    #setup_transmit(erot.OOBHUB_SPI)
    #check_tx_data(BMC_SPI,0)


