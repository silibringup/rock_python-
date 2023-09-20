#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
#This test ensure that BMC can send packet into oobhub i3c controller.
from driver import *
import random

def i3c_initiator_init(mst, dynamic_addr, static_addr):
    #I3C0
    mst.DEVICE_CTRL_0.write(0x0)
    #device mode selection
    mst.DEVICE_CTRL_EXTENDED_0.write(DEV_OPERATION_MODE = 0) #master
    mst.DEVICE_ADDR_0.write(DYNAMIC_ADDR = 0x30, DYNAMIC_ADDR_VALID = 1)

    #program timing register
    scl_i3c_id_timing_0_value = 0x7f*(2**16)+0x7f
    scl_i3c_pp_timing_0_value = 0x4f*(2**16)+0x4f
    scl_i2c_fm_timing_0_value = 0x10*(2**16)+0x10
    scl_i2c_fmp_timing_0_value = 0x20*(2**16)+0x28
    print(f"set SCL_I3C_OD_TIMING_0 to {hex(scl_i3c_id_timing_0_value)}")
    print(f"set SCL_I3C_PP_TIMING_0 to {hex(scl_i3c_pp_timing_0_value)}")
    print(f"set SCL_I2C_FM_TIMING_0 to {hex(scl_i2c_fm_timing_0_value)}")
    print(f"set SCL_I2C_FMP_TIMING_0 to {hex(scl_i2c_fmp_timing_0_value)}")
    mst.SCL_I3C_OD_TIMING_0.write(scl_i3c_id_timing_0_value)
    mst.SCL_I3C_PP_TIMING_0.write(scl_i3c_pp_timing_0_value)
    mst.SCL_I2C_FM_TIMING_0.write(scl_i2c_fm_timing_0_value)
    mst.SCL_I2C_FMP_TIMING_0.write(scl_i2c_fmp_timing_0_value)

    #device address table
    mst.DEV_ADDR_TABLE1_LOC1_0.write(DEV_DYNAMIC_ADDR = dynamic_addr)
    rd = mst.DEV_ADDR_TABLE1_LOC1_0.read()
    helper.pinfo(f'mst DEV_ADDR_TABLE1_LOC1_0 read out {rd}')
    
    #enable all interrupt
    mst.INTR_STATUS_EN_0.write(0xFFFF)
    mst.INTR_SIGNAL_EN_0.write(0xFFFF)

    #enable controller
    mst.DEVICE_CTRL_0.write(ENABLE = 1)
    rd = mst.DEVICE_CTRL_0.read()
    helper.pinfo(f'mst DEVICE_CTRL_0 read out {rd}')

def i3c_target_init(mst, static_addr):
    # MCTP_I3C
    # Set NV_COOBHUB_I3C_DEVICE_CTRL to 0
    test_api.oobhub_icd_write(0x1440400,0x0)

    # Set NV_COOBHUB_I3C_DEVICE_CTRL_EXTENDED_DEV_OPERATION_MODE to slave
    rd = test_api.oobhub_icd_read(0x14404b0)
    test_api.oobhub_icd_write(0x14404b0,(rd&0x4)+0x1)
    # Set NV_COOBHUB_I3C_DEVICE_ADDR STATIC_ADDR_VALID to valid and STATIC_ADDR to slave_static_addr
    test_api.oobhub_icd_write(0x1440404,static_addr+(1<<15))
    # Set NV_COOBHUB_I3C_SLV_MIPI_ID_VALUE
    test_api.oobhub_icd_write(0x1440470,0x39c1)
    # Set NV_COOBHUB_I3C_SLV_PID_VALUE
    test_api.oobhub_icd_write(0x1440474,0x4c85ae0f)
    # Set NV_COOBHUB_I3C_SLV_CHAR_CTRL DCR and BCR
    test_api.oobhub_icd_write(0x1440478,(0xd4<<8)+(1<<5)+1)

    # Set NV_COOBHUB_I3C_DATA_BUFFER_THLD_CTRL RX_START_THLD, TX_START_THLD, RX_BUF_THLD, TX_EMPTY_BUF_THLD
    test_api.oobhub_icd_write(0x1440420,(1<<24)+(1<<16)+(1<<8)+1)
    # Set NV_COOBHUB_I3C_QUEUE_THLD_CTRL IBI_STATUS_THLD, RESP_BUF_THLD, CMD_EMPTY_BUF_THLD
    test_api.oobhub_icd_write(0x144041c,(1<<24)+(1<<8)+1)
    # Set NV_COOBHUB_I3C_SLV_EVENT_STATUS_HJ_EN to 0
    test_api.oobhub_icd_write(0x1440438,0x0)
    # Set NV_COOBHUB_I3C_DEVICE_CTRL_ENABLE to 1
    test_api.oobhub_icd_write(0x1440400,1<<31)
    # Enable all interrupts
    test_api.oobhub_icd_write(0x1440440,0xffff)
    test_api.oobhub_icd_write(0x1440444,0xffff)
 
    rd = mst.DEVICE_ADDR_0.read()
    helper.pinfo(f"mst DEVICE_ADDR_0 read out {rd}")
    rd = test_api.oobhub_icd_read(0x1440404)
    helper.pinfo(f"MCTP_I3C DEVICE_ADDR read out {hex(rd)}")

def dynamic_addr_assign(mst):
    CMD_ATTR = 3 #address assign command
    CMD = 0x7 #ENTDAA
    DEV_INDEX = 0 #from DEV_ADDR_TABLE1
    DEV_COUNT = 1 #only 1 slave present
    ROC = 0
    TOC = 1
    command_queue_port_value = (CMD_ATTR<<0)+(CMD<<7)+(DEV_INDEX<<16)+(DEV_COUNT<<21)+(ROC<<26)+(TOC<<30)
    print(f"command_queue_port_value = {hex(command_queue_port_value)}")
    mst.COMMAND_QUEUE_PORT_0.write(command_queue_port_value)

    rd = mst.RESPONSE_QUEUE_PORT_0.read()
    helper.pinfo(f"mst RESPONSE_QUEUE_PORT_0 read out {rd}")


    rd = mst.PRESENT_STATE_0.read()
    helper.pinfo(f'mst PRESENT_STATE_0 read out {rd}')
    mst.PRESENT_STATE_0.poll(CONTROLLER_IDLE=1, timeout=1000)

    #check slave dynamic address
    helper.wait_sim_time("us",100)
    rd = mst.DEVICE_ADDR_0.read()
    helper.pinfo(f"mst DEVICE_ADDR_0 read out {rd}")
    rd = test_api.oobhub_icd_read(0x1440404)
    helper.pinfo(f"MCTP_I3C DEVICE_ADDR read out {hex(rd)}")

    if (rd&0x807f0000 == (dynamic_addr<<16)+(0x1<<31)):
        helper.pinfo("MCTP_I3C's dynamic address is correctly set")
    else:
        helper.perror(f"ENTDAA is not work MCTP_I3C: {hex(rd&0x807f0000)}")

def private_write(mst, DATA_BYTE_1 = 0x0F, DATA_BYTE_2 = 0x0E, DATA_BYTE_3 = 0x0D):
    #Short data argument
    CMD_ATTR = 2
    BYTE_STRB = 0x7
    command_queue_port_value = (CMD_ATTR<<0) + (BYTE_STRB<<3) + (DATA_BYTE_1<<8) + (DATA_BYTE_2<<16) + (DATA_BYTE_3<<24)
    helper.pinfo(f"command_queue_port_value = {hex(command_queue_port_value)}")
    mst.COMMAND_QUEUE_PORT_0.write(command_queue_port_value)
    helper.wait_sim_time("us",50)
    rd = mst.PRESENT_STATE_0.read()
    helper.pinfo(f'mst PRESENT_STATE_0 read out {rd}')

    #Transfer command
    CMD_ATTR = 0
    TID = 5
    CMD = 0x7 #ENTDAA
    CP = 0
    DEV_INDEX = 0
    SPEED = 0 
    DBP = 0
    ROC = 0 #not response after transfer complete
    SDAP = 1
    RnW = 0
    TOC = 1
    PEC = 0
    command_queue_port_value = (CMD_ATTR<<0) + (TID<<3) + (CMD<<7) + (CP<<15) + (DEV_INDEX<<16) + (SPEED<<21) + (DBP<<25) + (ROC<<26) + (SDAP<<27) + (RnW<<28) + (TOC<<30) + (PEC<<31)
    helper.pinfo(f"command_queue_port_value = {hex(command_queue_port_value)}")
    mst.COMMAND_QUEUE_PORT_0.write(command_queue_port_value)

    #Wait for controller idle
    rd = mst.PRESENT_STATE_0.read()
    helper.pinfo(f'mst PRESENT_STATE_0 read out {rd}')
    mst.PRESENT_STATE_0.poll(CONTROLLER_IDLE=1, timeout=500)
    '''while (rd['CONTROLLER_IDLE'] == 0x0):
        rd = mst.PRESENT_STATE_0.read()
        helper.pinfo(f'mst PRESENT_STATE_0 read out {rd}')
        helper.pinfo("wait for master controller idle")
        helper.wait_sim_time("us",100)'''

    rd = test_api.oobhub_icd_read(0x144043c) #INTR_STATUS
    helper.pinfo(f"MCTP_I3C interrupt : {hex(rd)}")
    rd = test_api.oobhub_icd_read(0x1440410) #RESPONSE_QUEUE_PORT
    helper.pinfo(f"MCTP_I3C: RESPONSE_QUEUE_PORT_0 = {hex(rd)}")
    rd = test_api.oobhub_icd_read(0x1440414) #TX_DATA_PORT
    if rd != (DATA_BYTE_1) + (DATA_BYTE_2<<8) + (DATA_BYTE_3<<16):
        helper.perror(f"MCTP_I3C TX_DATA_PORT: {hex(rd)} but expect {hex((DATA_BYTE_1)+(DATA_BYTE_2<<8)+(DATA_BYTE_3<<16))}")
    else:
        helper.pinfo(f"MCTP_I3C TX_DATA_PORT: {hex(rd)}")
    test_api.oobhub_icd_write(0x144043c,0xffff) #INTR_STATUS
    helper.pinfo("clear all MCTP_I3C interrupt")

def private_read(mst, data = 0x123456, data_length = 0x3):
    #config data to be read
    #data = 0x123456
    #data_length = 0x3
    command_queue_port_value = data_length << 16
    print(f"MCTP_I3C: write command_queue_port_value = {hex(command_queue_port_value)}")
    test_api.oobhub_icd_write(0x144040c,command_queue_port_value) #COMMAND_QUEUE_PORT
    rd = test_api.oobhub_icd_read(0x144043c) #INTR_STATUS
    print(f"MCTP_I3C interrupt : {hex(rd)}")
    if rd & 0x10 == 0x10: #INTR_STATUS_RESP_READY_STS
        rd = rd = test_api.oobhub_icd_read(0x1440410) #RESPONSE_QUEUE_PORT
        print(f"MCTP_I3C: RESPONSE_QUEUE_PORT = {hex(rd)}")

    data_to_send = data
    while data_length > 0:
        test_api.oobhub_icd_write(0x1440414,data_to_send&0xffffffff) #TX_DATA_PORT
        data_to_send = data_to_send >> 32
        data_length = data_length - 4  

    test_api.oobhub_icd_write(0x144043c,0x111b) #INTR_STATUS

    #Transfer command
    CMD_ATTR = 0
    TID = 5
    CMD = 0x7 #ENTDAA
    CP = 0
    DEV_INDEX = 0
    SPEED = 0 
    DBP = 0
    ROC = 0 #not response after transfer complete
    SDAP = 1
    RnW = 1
    TOC = 1
    PEC = 0
    command_queue_port_value = (CMD_ATTR<<0) + (TID<<3) + (CMD<<7) + (CP<<15) + (DEV_INDEX<<16) + (SPEED<<21) + (DBP<<25) + (ROC<<26) + (SDAP<<27) + (RnW<<28) + (TOC<<30) + (PEC<<31)
    helper.pinfo(f"command_queue_port_value = {hex(command_queue_port_value)}")
    mst.COMMAND_QUEUE_PORT_0.write(command_queue_port_value)
    #Wait for controller idle
    rd = mst.PRESENT_STATE_0.read()
    x = 0
    while (rd['CM_TFR_ST_STS'] != 0x0):
        helper.pinfo("wait for transfer state status become idle")
        helper.wait_sim_time("us",100)
        rd = mst.PRESENT_STATE_0.read()
        helper.pinfo(f'mst PRESENT_STATE_0 read out {rd}')
        x = x+1
        if x > 2:
            helper.perror("timeout error")
            break

    rd = mst.TX_DATA_PORT_0.read()
    helper.pinfo(f"mst TX_DATA_PORT: {hex(rd.value)}")
    if rd.value == data:
        helper.pinfo(f"correct data received from slave: {hex(rd.value)}")
    else:
        helper.perror(f"exp = {hex(data)}, real = {hex(rd.value)}")

with Test(sys.argv) as t:
    def parse_args():
        t.parser.add_argument("--unit", action='store', help="Unit To Light On, Support Regular Expression", default='.*')
        t.parser.add_argument("--single", action='store_true', help="single slave or two slaves in this test")
        t.parser.add_argument("--i3c",type = int, default=1)
        opts, unknown = t.parser.parse_known_args(sys.argv[1:])
        return opts
  
    options = parse_args() 

    if options.i3c == 0:
        mst = erot.I3C_IB0
        helper.pinfo(f'use {mst.name} as initiator')
    elif options.i3c == 1:
        mst = erot.I3C_IB1
        helper.pinfo(f'use {mst.name} as initiator')
    else:
        helper.perror(f'Invaild AP I3C')

    #Test start
    helper.set_loop_back(0)
    # Enable interface master
    helper.i2c_write(addr=0x69, data=0x0100000325, size=5, i2c_id=3, en_10bits_addr=0) #RESET_0, cmd='d37

    helper.set_loop_back(1)
    test_api.oobhub_icd_init()

    dynamic_addr = 0x45
    static_addr = 0x68

    #initialize master register
    i3c_initiator_init(mst, dynamic_addr, static_addr)
    
    #initialize slave register
    i3c_target_init(mst, static_addr)
    
    #ENTDAA
    dynamic_addr_assign(mst)
    
    #Private write transfer without 0x7E
    private_write(mst)    
    #Private read without 0x7E
    private_read(mst)

    #write/read with random data
    wr_data_1 = random.randint(0x0, 0xff)
    wr_data_2 = random.randint(0x0, 0xff)
    wr_data_3 = random.randint(0x0, 0xff)
    rd_date = random.randint(0x0, 0xffffff)
    private_write(mst, wr_data_1, wr_data_2, wr_data_3)
    private_read(mst, rd_date)
