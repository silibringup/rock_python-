#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import *

with Test(sys.argv) as t:

    golden_value_list = [0x5b, 0xad, 0x00, 0xff]
    
    def parse_args():
        t.parser.add_argument("--baud", "-b", action='store', help="Select baud rate", type=int, default=0)
        opts, unknown = t.parser.parse_known_args(sys.argv[1:])
        return opts

    # Line control
    # BRK, PEN=ParityENable, STP2=2SToPbits, FEN=FifoENable, WLEN=WordLENgth, SPS=StickyParityS
    def set_line_control():
        erot.UART.UARTLCR_H_0.debug_update(BRK=0,PEN=0,STP2=0,FEN=1,WLEN=3,SPS=0)
        erot.UART.UARTLCR_H_0.debug_poll(timeout=1000,BRK=0,PEN=0,STP2=0,FEN=1,WLEN=3,SPS=0)

    def set_baud(idx):
        if (idx == 0):
            freq = 651
        elif (idx == 1):
            freq = 326 
        elif (idx == 2):
            freq = 217
        elif (idx == 3):
            #freq = 324
            freq = 163
        elif (idx == 4):
            freq = 109
        elif (idx == 5):
            freq = 81
        elif (idx == 6):
            freq = 54

        rd = erot.UART.UARTIBRD_0.read()
        LOG("BAUD is %s" % str(rd))

        erot.CLOCK.NVEROT_CLOCK_IO_CTL.SW_UART_CLK_DIVISOR_0.update(DIV_SEL_1_DIV=freq)
        erot.CLOCK.NVEROT_CLOCK_IO_CTL.SW_UART_CLK_DIVISOR_0.poll(timeout=100,DIV_SEL_1_DIV=freq)
        #erot.UART.UARTIBRD_0.update(BAUD_DIVINT=freq)
        #erot.UART.UARTIBRD_0.poll(timeout=100,BAUD_DIVINT=freq)

    # UARTDMACR_0


    # UARTIFLS_0
    # Tx/Rx FifoLevel Select
    def set_fifo_level():
        erot.UART.UARTIFLS_0.debug_update(RXIFLSEL=0,TXIFLSEL=0)
        erot.UART.UARTIFLS_0.debug_poll(timeout=1000,RXIFLSEL=0,TXIFLSEL=0)       


    # UARTIMSC_0


    # UARTCR_0
    # Contorl Registe
    def enable_tx_rx():
        erot.UART.UARTCR_0.debug_update(CTS_EN=0,RTS_EN=0,SIREN=0,SIRLP=0,LBE=0,RXE=1,TXE=1,UARTEN=0)
        erot.UART.UARTCR_0.debug_poll(timeout=1000,CTS_EN=0,RTS_EN=0,SIREN=0,SIRLP=0,LBE=0,RXE=1,TXE=1,UARTEN=0)

    # uart tx fifo write, plan to send 0x5a out
    def set_tx_data(tx_data):
        erot.UART.UARTDR_0.debug_write(DATA=tx_data)


    #enable rx and tx
    def enable_uart():
        erot.UART.UARTCR_0.debug_update(UARTEN=1)
        erot.UART.UARTCR_0.debug_poll(timeout=1000,UARTEN=1)
 
    #poll rx data ten times to check if it matches with 0x5a
    def check_rx_data(exp_rx_data=0,timeout=10):
        rd = erot.UART.UARTDR_0.debug_read()

        if rd['DATA'] != exp_rx_data:
            helper.perror("UART LOOPBACK ERROR, exp %x, received %x" % (exp_rx_data, rd['DATA']))
        else:
            print("Compare pass, exp_rx_data = %x" % exp_rx_data)
    def uart_init():
        erot.PADCTRL_S.UART_TX_0.debug_update(TRISTATE=0)
        erot.PADCTRL_S.UART_RX_0.debug_update(TRISTATE=0)       

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
    uart_init()
    set_line_control()
    set_fifo_level()
    enable_tx_rx()

    for i in range(4):
        set_tx_data(golden_value_list[i])

    enable_uart()

    # poll per 100us
    erot.UART.UARTRIS_0.debug_poll(timeout=10000, interval=100000, RXRIS=1)

    for i in range(4):
        #if golden_value_list[i]+1 >= 256:
        #    exp = golden_value_list[i]+1-256
        #else:
        #    exp = golden_value_list[i]+1
        check_rx_data(exp_rx_data=golden_value_list[i])
