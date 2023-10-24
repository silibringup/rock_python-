#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
import os
import re
from driver import *
from driver.components.spi_mst import SPI_SCLK_FREQ_SEL

#golden_value = 0xe7 #f0 dummy -> dbe884??
golden_value = 0x7e #f0 dummy -> bde884??


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
        spi.COMMAND2_0.update(SI_RM_DUAL_SPI_ENABLE=1,SI_RM_CMD_BIT_LENGTH=7, SI_RM_ADDRESS_BIT_LENGTH=23)
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
            helper.perror("Reg Read/Write 1st Fail,act value 0x%x, exp value 0x%x" % (read_data,rt_value1))

        rd = spi.RX_FIFO_0.read()
        LOG("2nd read data is %d" % rd.value)
        read_data = rd.value
        #read_data = regroup_data(2, rd.value,0)
        if read_data != golden_value:
            helper.perror("Reg Read/Write 2nd Fail,act value 0x%x, exp value 0x%x" % (read_data,golden_value))

    def unpack_check(spi):
        spi.TRANSFER_STATUS_0.poll(timeout=100,RDY=1)
        rd = spi.RX_FIFO_0.read()#06
        rd = spi.RX_FIFO_0.read()#0658
        rd = spi.RX_FIFO_0.read()#0658c2
        rd = spi.RX_FIFO_0.read()#0658c274
        LOG("1st read data is %d" % rd.value)

        read_data = regroup_data(4, rd.value,0)
        if read_data != rt_value1:
            helper.perror("Reg Read/Write 1st Fail -> %s" % str(read_data))

        rd = spi.RX_FIFO_0.read()
        LOG("2nd read data is %d" % rd.value)
        #read_data = rd.value
        read_data = regroup_data(4, rd.value,0)
        if read_data != 0x58c274e7:
            helper.perror("Reg Read/Write 2nd Fail -> %s" % str(read_data))



    def spi_vip_write(spi,cs):
        helper.spi_write(spi_port=spi, cs_id=cs, n_data_lane=2, data=[golden_value], 
            n_instruction_lane=1, n_instruction_bits=8, instruction=[0x06],
            n_address_lane=1, n_address_bits=24, address=[0x58,0xc2,0x74])



    LOG("START SPI SLAVE RX TEST")

    test_api.enable_vip_connection()
    test_api.reset_init()

    #setup_imr(erot.SPI_IB0)
    setup_sink(erot.SPI_IB0)
    spi_vip_write(AP0_SPI,2)
    wait_sink_done(erot.SPI_IB0)
    #unpack_check(erot.SPI_IB0)



