#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import *

with Test(sys.argv) as t:

    golden_value_list = [0x5b, 0xad, 0x00, 0xff]

    # Line control
    # BRK, PEN=ParityENable, STP2=2SToPbits, FEN=FifoENable, WLEN=WordLENgth, SPS=StickyParityS
    def set_line_control():
        if helper.target == 'simv_fpga':
            erot.UART.UARTLCR_H_0.debug_update(BRK=0,PEN=0,STP2=0,FEN=1,WLEN=3,SPS=0)
            erot.UART.UARTLCR_H_0.debug_poll(timeout=1000,BRK=0,PEN=0,STP2=0,FEN=1,WLEN=3,SPS=0)
        else:           
            erot.UART.UARTLCR_H_0.update(BRK=0,PEN=0,STP2=0,FEN=1,WLEN=3,SPS=0)
            erot.UART.UARTLCR_H_0.poll(timeout=1,BRK=0,PEN=0,STP2=0,FEN=1,WLEN=3,SPS=0)


    # UARTDMACR_0


    # UARTIFLS_0
    # Tx/Rx FifoLevel Select
    def set_fifo_level():
        if helper.target == 'simv_fpga':
            erot.UART.UARTIFLS_0.debug_update(RXIFLSEL=0,TXIFLSEL=0)
            erot.UART.UARTIFLS_0.debug_poll(timeout=1000,RXIFLSEL=0,TXIFLSEL=0)       
        else:
            erot.UART.UARTIFLS_0.update(RXIFLSEL=0,TXIFLSEL=0)
            erot.UART.UARTIFLS_0.poll(timeout=1,RXIFLSEL=0,TXIFLSEL=0)

    # UARTIMSC_0


    # UARTCR_0
    # Contorl Registe
    def enable_tx_rx():
        if helper.target == 'simv_fpga':
            erot.UART.UARTCR_0.debug_update(CTS_EN=0,RTS_EN=0,SIREN=0,SIRLP=0,LBE=0,RXE=1,TXE=1,UARTEN=0)
            erot.UART.UARTCR_0.debug_poll(timeout=1000,CTS_EN=0,RTS_EN=0,SIREN=0,SIRLP=0,LBE=0,RXE=1,TXE=1,UARTEN=0)
        else:
            erot.UART.UARTCR_0.update(CTS_EN=0,RTS_EN=0,SIREN=0,SIRLP=0,LBE=0,RXE=1,TXE=1,UARTEN=0)
            erot.UART.UARTCR_0.poll(timeout=1,CTS_EN=0,RTS_EN=0,SIREN=0,SIRLP=0,LBE=0,RXE=1,TXE=1,UARTEN=0)           

    # uart tx fifo write, plan to send 0x5a out
    def set_tx_data(tx_data):
        if helper.target == 'simv_fpga':
            erot.UART.UARTDR_0.debug_write(DATA=tx_data)
        else:
            erot.UART.UARTDR_0.write(DATA=tx_data)

    #enable rx and tx
    def enable_uart():
        if helper.target == 'simv_fpga':
            erot.UART.UARTCR_0.debug_update(UARTEN=1)
            erot.UART.UARTCR_0.debug_poll(timeout=1000,UARTEN=1)
        else:
            erot.UART.UARTCR_0.debug_update(UARTEN=1)
            erot.UART.UARTCR_0.debug_poll(timeout=1,UARTEN=1)   
    #poll rx data ten times to check if it matches with 0x5a
    def check_rx_data(exp_rx_data=0,timeout=10):
        if helper.target == 'simv_fpga':
            rd = erot.UART.UARTDR_0.debug_read()
        else:
            rd = erot.UART.UARTDR_0.read()

        if rd['DATA'] != exp_rx_data:
            helper.perror("UART LOOPBACK ERROR, exp %x, received %x" % (exp_rx_data, rd['DATA']))
        else:
            print("Compare pass, exp_rx_data = %x" % exp_rx_data)


    if helper.target == "simv_fpga":
        helper.wait_sim_time('us', 50)
        helper.hdl_force('ntb_top.u_nv_fpga_dut.u_nv_top_fpga.u_nv_top_wrapper.u_nv_top.nvjtag_sel', 1)

        helper.jtag.Reset(0)
        helper.jtag.DRScan(100, hex(0x0)) #add some delay as jtag only work when nvjtag_sel stable in real case
        helper.jtag.Reset(1)  

        #unlock j2h interface
        helper.pinfo(f'j2h_unlock sequence start')
        helper.j2h_unlock()
        helper.pinfo(f'j2h_unlock sequence finish')
        #make sure l3 reset is released
        erot.RESET.NVEROT_RESET_CFG.SW_L3_RST_0.debug_poll(timeout=10, RESET_LEVEL3=1)
        #reset uart 
        erot.RESET.NVEROT_RESET_CFG.SW_UART_RST_0.debug_write(RESET_UART=1)

    helper.set_loop_back(1)
    LOG("START UART LOOPBACK TEST")
    if helper.target == "simv_fpga":
        erot.PADCTRL_S.UART_TX_0.debug_update(TRISTATE=0)
        erot.PADCTRL_S.UART_RX_0.debug_update(TRISTATE=0)
    else:
        test_api.uart_init()
    set_line_control()
    set_fifo_level()
    enable_tx_rx()

    for i in range(4):
        set_tx_data(golden_value_list[i])

    enable_uart()

    # poll per 100us
    if helper.target == 'simv_fpga':
        erot.UART.UARTRIS_0.debug_poll(timeout=30, interval=100000, RXRIS=1)
    else:
        erot.UART.UARTRIS_0.poll(timeout=30, interval=100000, RXRIS=1)

    for i in range(4):
        if golden_value_list[i]+1 >= 256:
            exp = golden_value_list[i]+1-256
        else:
            exp = golden_value_list[i]+1
        check_rx_data(exp_rx_data=exp)
