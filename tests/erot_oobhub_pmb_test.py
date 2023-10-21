#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
#This test ensure that fsp can write and read data to OOBHUB peregrine imem/dmem by config PMB in OOBHUB peregrine
from driver import * 
import random
import falcondma_lib

with Test(sys.argv) as t:
    def parse_args():
        t.parser.add_argument("--unit", action='store', help="Unit To Light On, Support Regular Expression", default='.*')
        t.parser.add_argument("--single", action='store_true', help="single slave or two slaves in this test")
        opts, unknown = t.parser.parse_known_args(sys.argv[1:])
        return opts

    options = parse_args()

    #Test start
    #variables setup
    engine = "OOBHUB"
    msg_size = random.randrange(1,129)
    send_msg = [random.randrange(0xffffffff) for i in range(msg_size)]
    imem_addr = random.randrange(0,0x200-len(send_msg))<<8
    dmem_addr = random.randrange(0,0x200-len(send_msg))<<8

    # PEREGRINE_RISCV_BCR_CTRL._CORE_SELECT = _RISCV
    erot.OOBHUB.PEREGRINE_RISCV_BCR_CTRL_0.update(CORE_SELECT=1)
    
    helper.pinfo(f'access to IMEM address {hex(imem_addr)}')
    #IMEM write through pmb
    falcondma_lib.write_falcon_mem(engine, imem_addr, send_msg, len(send_msg), is_imem=True)
    #IMEM read through pmb
    rx_rd_message = falcondma_lib.read_falcon_mem(engine, imem_addr, len(send_msg), is_imem=True)
    if rx_rd_message != send_msg:
        helper.perror(f'IMEM read message Fail, read out {rx_rd_message}')

    helper.pinfo(f'access to DMEM address {hex(dmem_addr)}')
    #DMEM write through pmb
    falcondma_lib.write_falcon_mem(engine, dmem_addr, send_msg, len(send_msg), is_imem=False)
    #DMEM read through pmb
    rx_rd_message = falcondma_lib.read_falcon_mem(engine, dmem_addr, len(send_msg), is_imem=False)
    if rx_rd_message != send_msg:
        helper.perror(f'DMEM read message Fail, read out {rx_rd_message}')
