#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import *

with Test(sys.argv) as t:

    golden_value_list = [0x5b, 0xad, 0x00, 0xff]


    # Line control
    # BRK, PEN=ParityENable, STP2=2SToPbits, FEN=FifoENable, WLEN=WordLENgth, SPS=StickyParityS
    def set_line_control():
        erot.UART.UARTLCR_H_0.update(BRK=0,PEN=0,STP2=0,FEN=1,WLEN=3,SPS=0)
        erot.UART.UARTLCR_H_0.poll(timeout=1,BRK=0,PEN=0,STP2=0,FEN=1,WLEN=3,SPS=0)


    # UARTDMACR_0


    # UARTIFLS_0
    # Tx/Rx FifoLevel Select
    def set_fifo_level():
        erot.UART.UARTIFLS_0.update(RXIFLSEL=0,TXIFLSEL=0)
        erot.UART.UARTIFLS_0.poll(timeout=1,RXIFLSEL=0,TXIFLSEL=0)

    # UARTIMSC_0


    # UARTCR_0
    # Contorl Registe
    def enable_tx_rx():
        erot.UART.UARTCR_0.update(CTS_EN=0,RTS_EN=0,SIREN=0,SIRLP=0,LBE=0,RXE=1,TXE=1,UARTEN=0)
        erot.UART.UARTCR_0.poll(timeout=1,CTS_EN=0,RTS_EN=0,SIREN=0,SIRLP=0,LBE=0,RXE=1,TXE=1,UARTEN=0)

    # uart tx fifo write, plan to send 0x5a out
    def set_tx_data(tx_data):
        erot.UART.UARTDR_0.update(DATA=tx_data)

    #enable rx and tx
    def enable_uart():
        erot.UART.UARTCR_0.update(UARTEN=1)
        erot.UART.UARTCR_0.poll(timeout=1,UARTEN=1)
    
    #poll rx data ten times to check if it matches with 0x5a
    def check_rx_data(exp_rx_data=0,timeout=10):
        rd = erot.UART.UARTDR_0.read()
        if rd['DATA'] != exp_rx_data:
            helper.perror("UART LOOPBACK ERROR, exp %x, received %x" % (exp_rx_data, rd['DATA']))
        else:
            print("Compare pass, exp_rx_data = %x" % exp_rx_data)



    helper.set_loop_back(1)
    LOG("START UART LOOPBACK TEST")
    test_api.uart_init()
    
    set_line_control()
    set_fifo_level()
    enable_tx_rx()

    for i in range(4):
        set_tx_data(golden_value_list[i])

    enable_uart()

    # poll per 100us
    erot.UART.UARTRIS_0.poll(timeout=30, interval=100000, RXRIS=1)

    for i in range(4):
        if golden_value_list[i]+1 >= 256:
            exp = golden_value_list[i]+1-256
        else:
            exp = golden_value_list[i]+1
        check_rx_data(exp_rx_data=exp)
