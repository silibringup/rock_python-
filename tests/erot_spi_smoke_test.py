#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
import os
import re
from driver import *

golden_value = 0xa5a5

with Test(sys.argv) as t:
    AP0_SPI = 0
    AP1_SPI = 1
    BMC_SPI = 2

    #config slave
    def setup_spi(spi):
        spi.MISC_0.update(CLKEN_OVERRIDE=1,EXT_CLK_EN=1)
        spi.MISC_0.poll(timeout=100,CLKEN_OVERRIDE=1,EXT_CLK_EN=1)
        spi.COMMAND_0.update(PIO='PIO',M_S='SLAVE',BIT_LENGTH=15,Rx_EN='ENABLE',CS_POL_INACTIVE0=1,PACKED=1)
        LOG("setup spi done")
    
    def setup_transmit(spi):
        spi.TX_FIFO_0.write(golden_value)
        spi.MISC_0.update(CLKEN_OVERRIDE=1,EXT_CLK_EN=1)
        spi.MISC_0.poll(timeout=100,CLKEN_OVERRIDE=1,EXT_CLK_EN=1)
        spi.COMMAND_0.update(PIO='PIO',M_S='SLAVE',BIT_LENGTH=15,Tx_EN='ENABLE',CS_POL_INACTIVE0=1,PACKED=1)

    def regroup_data(in_data, mode=0):
        if mode == 0: #PACKED, LSBi=0, LSBy=0
            byte_array = in_data.to_bytes(2,'little')
            out_data = int.from_bytes(byte_array, 'big')
            return out_data

    def wait_spi_done(spi):
        spi.TRANSFER_STATUS_0.poll(timeout=100,RDY=1)
        rd = spi.RX_FIFO_0.read()
        read_data = regroup_data(rd.value,0)
        if read_data != golden_value:
            helper.perror("Reg Read/Write Fail,act value 0x%x, exp value 0x%x" % (read_data,golden_value))
    
    def check_tx_data(spi,cs):
        read_bytes = helper.spi_read(spi_port=spi, cs_id=cs, n_data_lane=1, nbr_rd_bytes=2,n_instruction_lane=1, n_instruction_bits=0, instruction=[], n_address_lane=1, n_address_bits=0, address=[])
        read_value = int.from_bytes(read_bytes, "big")
        vip_rd = regroup_data(read_value)
        if vip_rd != golden_value:
            helper.perror("Reg Read/Write Fail,act value 0x%x, exp value 0x%x" % (vip_rd,golden_value))


    test_api.reset_init()
    test_api.enable_vip_connection()

    LOG("START SPI SMOKE TEST : RX")

    setup_spi(erot.SPI_IB0)
    helper.spi_write(spi_port=AP0_SPI, cs_id=2, n_data_lane=1, data=list(golden_value.to_bytes(2,'big')), 
            n_instruction_lane=1, n_instruction_bits=0, instruction=[],
            n_address_lane=1, n_address_bits=0, address=[])
    wait_spi_done(erot.SPI_IB0)

    LOG("START SPI SMOKE TEST : TX")

    setup_transmit(erot.SPI_IB0)
    check_tx_data(AP0_SPI,2) 