#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
#This test ensure that BMC can send packet into oobhub i2c controller.
from driver import *
import random

def mctp_i2c_target_init(slv_addr):
    # Set _SLV_RESET_CNTRL_SOFT_RESET to _CLEARED
    test_api.oobhub_icd_write(0x14400ac,0x0)
    # Set _SLV_FIFO_CONTROL to 0
    test_api.oobhub_icd_write(0x14400c0,0x0)
    # Set NV_COOBHUB_I2C_I2C_INTERRUPT_SET_REGISTER to 0
    test_api.oobhub_icd_write(0x1440074,0x0)
    # Set NV_COOBHUB_I2C_I2C_CLKEN_OVERRIDE to 0
    test_api.oobhub_icd_write(0x1440090,0x0)
    # Set NV_COOBHUB_I2C_I2C_DEBUG_CONTROL to 0
    test_api.oobhub_icd_write(0x14400a4,0x0)
    # Set NV_COOBHUB_I2C_I2C_TLOW_SEXT to 0
    test_api.oobhub_icd_write(0x1440034,0x0)
    # Set NV_COOBHUB_I2C_I2C_SL_INT_SET to 0
    test_api.oobhub_icd_write(0x1440048,0x0)
    # Set NV_COOBHUB_I2C_I2C_SL_DELAY_COUNT to 0x1e
    test_api.oobhub_icd_write(0x144003c,0x1e)
    # Set NV_COOBHUB_I2C_I2C_SL_ADDR1_SL_ADDR0 to slave address
    test_api.oobhub_icd_write(0x144002c,slv_addr&0x7f)
    # Set NV_COOBHUB_I2C_I2C_SL_ADDR2 to 0
    test_api.oobhub_icd_write(0x1440030,0x0)
    # Set NV_COOBHUB_I2C_INTERRUPT_MASK_REGISTER to 0
    test_api.oobhub_icd_write(0x1440064,0x0)
    # Set NV_COOBHUB_I2C_I2C_SL_INT_MASK
    test_api.oobhub_icd_write(0x1440040,0xfd)
    # Set NV_COOBHUB_I2C_I2C_SL_CNFG_ENABLE_SL ENABLE
    test_api.oobhub_icd_write(0x1440020,0x8)
    # Set NV_COOBHUB_I2C_I2C_INTERFACE_TIMING_0 and NV_COOBHUB_I2C_I2C_INTERFACE_TIMING_1 for FM+ speed
    test_api.oobhub_icd_write(0x1440094,0x0101)
    test_api.oobhub_icd_write(0x1440098,0x02020202)
    # Set NV_COOBHUB_I2C_I2C_CONFIG_LOAD
    test_api.oobhub_icd_write(0x144008c,0x6)
    # Poll until NV_COOBHUB_I2C_I2C_CONFIG_LOAD_SLV_CONFIG_LOAD == 0
    rd = test_api.oobhub_icd_read(0x144008c)
    helper.pinfo(f'NV_COOBHUB_I2C_I2C_CONFIG_LOAD_SLV_CONFIG_LOAD read out {(rd&0x2)>>1}')
    while (rd & 0x2) == 0x2 :
        helper.wait_sim_time('us',100)
        rd = test_api.oobhub_icd_write(0x144008c)
        helper.pinfo("Wait for setting target's register")

def initiator_clk_divisor_setting(mst, divisor=5, tlow=1, thigh=1, tsu_sta=2, thd_sta=2, tsu_sto=2, tbuf=2):
    #set to FM+ speed
    helper.pinfo(f"{mst.name} Set I2C_CLK_DIVISOR_STD_FAST_MODE to {divisor} for read transaction")
    mst.I2C_CLK_DIVISOR_REGISTER_0.write(I2C_CLK_DIVISOR_STD_FAST_MODE = divisor)
    mst.I2C_INTERFACE_TIMING_0_0.write(THIGH = thigh, TLOW = tlow)
    mst.I2C_INTERFACE_TIMING_1_0.write(TBUF = tbuf, THD_STA = thd_sta, TSU_STA = tsu_sta, TSU_STO = tsu_sto)
    rd = mst.I2C_CLK_DIVISOR_REGISTER_0.read()
    helper.pinfo(f"Read I2C_CLK_DIVISOR_STD_FAST_MODE = {rd['I2C_CLK_DIVISOR_STD_FAST_MODE']}")
    rd = mst.I2C_INTERFACE_TIMING_0_0.read()
    helper.pinfo(f"Read I2C_INTERFACE_TIMING_0_0, THIGH = {rd['THIGH']}, TLOW = {rd['TLOW']}")
    rd = mst.I2C_INTERFACE_TIMING_1_0.read()
    helper.pinfo(f"Read I2C_INTERFACE_TIMING_1_0, TBUF = {rd['TBUF']}, THD_STA = {rd['THD_STA']}, TSU_STA = {rd['TSU_STA']}, TSU_STO = {rd['TSU_STO']}")
    mst.I2C_CONFIG_LOAD_0.write(MSTR_CONFIG_LOAD = 0x1)
    rd = mst.I2C_CONFIG_LOAD_0.read()
    while rd['MSTR_CONFIG_LOAD'] == 0x1 :
        rd = mst.I2C_CONFIG_LOAD_0.read()
        helper.pinfo("Wait for setting master's register")

def i2c_initiator_write(mst, slv_addr, slv_data):
    #configure master register and trigger transaction
    send = 1
    no_ack = 0
    cmd2 = 0 #write
    cmd1 = 0 #write
    length = 0 #in bytes
    mst_cnfg = (send<<9)+(no_ack<<8)+(cmd2<<7)+(cmd1<<6)+(length<<1)
    helper.pinfo("mst_cnfg = %d" % mst_cnfg)
    mst.I2C_CMD_ADDR0_0.write(slv_addr<<1)
    mst.I2C_CMD_DATA1_0.write(slv_data)
    mst.I2C_CNFG_0.write(mst_cnfg)

    #Wait for bus idle and check mst_cnfg
    #wait for target interrupt
    #read target.I2C_SL_STATUS
    rd = test_api.oobhub_icd_read(0x1440028)
    helper.pinfo(f'MCTP_I2C I2C_SL_STATUS read out {hex(rd)}')
    cnt = 0
    while (rd & 0xc != 0xc) & (cnt < 1000):
        helper.wait_sim_time('us',10)
        rd = test_api.oobhub_icd_read(0x1440028)
        helper.pinfo(f'MCTP_I2C I2C_SL_STATUS read out {hex(rd)}')
        cnt += 1
    if rd & 0xc != 0xc:
        helper.perror(f'[I2C write] MCTP_I2C I2C_SL_STATUS read out {hex(rd)}, expect 0xc')

    #clear target interrupt
    test_api.oobhub_icd_write(0x1440028,0xc)
    rd = test_api.oobhub_icd_read(0x1440028)
    helper.pinfo(f'MCTP_I2C I2C_SL_STATUS read out {hex(rd)}')
    cnt = 0
    while (rd & 0xc == 0xc) & (cnt < 10):
        rd = test_api.oobhub_icd_read(0x1440028)
        helper.pinfo(f'MCTP_I2C I2C_SL_STATUS read out {hex(rd&0xc)}')
        cnt +=1
    if rd & 0xc == 0xc:
        helper.perror(f'[I2C write] MCTP_I2C I2C_SL_STATUS read out {hex(rd&0xc)}, expect !=0xc')
       
    rd = test_api.oobhub_icd_read(0x1440028)
    helper.pinfo(f'MCTP_I2C I2C_SL_STATUS read out {hex(rd)}')
    cnt = 0
    while (rd & 0xc != 0x8) & (cnt < 10):
        rd = test_api.oobhub_icd_read(0x1440028)
        helper.pinfo(f'MCTP_I2C I2C_SL_STATUS read out {hex(rd&0xc)}')
        cnt +=1
    if rd & 0xc != 0x8:
        helper.perror(f'[I2C write] MCTP_I2C I2C_SL_STATUS read out {hex(rd&0xc)}, expect 0x8')

    test_api.oobhub_icd_write(0x1440028,0x8)

    #get target rcv data 
    slv_rcv_data = test_api.oobhub_icd_read(0x1440024) #I2C_SL_RCVD      
       
    #wait for initiator bus idle
    rd = mst.I2C_STATUS_0.read()
    helper.pinfo(f'{mst.name} I2C_STATUS_0 read out {rd}')
    while (rd.value & 0x100) == 0x100 :
        rd = mst.I2C_STATUS_0.read()
        helper.pinfo("Waiting for bus idle...") 
    if (slv_rcv_data != slv_data):
        helper.perror(f"[I2C write] Data transmission Fail -> EXP ={hex(slv_data)}, REAL = {hex(slv_rcv_data)}" )
    else:
        helper.pinfo(f"MCTP_I2C receive correct data: {hex(slv_data)}")

def i2c_initiator_read(mst, byte_num, slv_addr, slv_data):
    #configure initiator register and trigger transaction
    send = 1
    no_ack = 0
    cmd2 = 1 #read
    cmd1 = 1 #read
    length = byte_num-1 #in bytes
    mst.I2C_CMD_ADDR0_0.write((slv_addr<<1)+1)
    mst_cnfg = (no_ack<<8)+(cmd2<<7)+(cmd1<<6)+(length<<1)        
    helper.pinfo("mst_cnfg = %d" % mst_cnfg)
    mst.I2C_CNFG_0.write(mst_cnfg)    
    mst.I2C_CONFIG_LOAD_0.write(0x1)
    rd = mst.I2C_CONFIG_LOAD_0.read()
    helper.pinfo(f'{mst.name} I2C_CONFIG_LOAD_0 read out {rd}')
    cnt = 0
    while (rd.value & 0x1 == 0x1) & (cnt < 10) :
        rd = mst.I2C_CONFIG_LOAD_0.read()
        print ("Wait for setting master's register")
        cnt += 1
    if rd.value & 0x1 == 0x1:
        helper.perror(f'[I2C read] {mst.name} I2C_CONFIG_LOAD_0 read out {hex(rd.value&0x1)} expect !=1')
    mst.I2C_CNFG_0.write((send<<9)+mst_cnfg)
    rd = mst.I2C_CNFG_0.read()
    helper.pinfo(f'{mst.name} I2C_CNFG_0 read out {rd}')

    #wait for bus idle and check mst_cnfg
    #check target interrupt
    rd = test_api.oobhub_icd_read(0x1440028) #I2C_SL_STATUS
    helper.pinfo(f'MCTP_I2C I2C_SL_STATUS read out {hex(rd)}')
    cnt = 0
    while (rd & 0xc != 0xc) & (cnt < 30):
        rd = test_api.oobhub_icd_read(0x1440028) #I2C_SL_STATUS
        helper.pinfo(f'MCTP_I2C I2C_SL_STATUS read out {hex(rd)}')
        cnt += 1
    if rd & 0xc != 0xc:
        helper.perror(f'[I2C read] MCTP_I2C I2C_SL_STATUS read out {hex(rd&0xc)} expect 0xc')

    #clear target interrupt and write slave data               
    test_api.oobhub_icd_write(0x1440028,0xc) #I2C_SL_STATUS
    rd = test_api.oobhub_icd_read(0x1440028) #I2C_SL_STATUS
    helper.pinfo(f'MCTP_I2C I2C_SL_STATUS read out {hex(rd)}')
    cnt = 0
    while (rd & 0xc == 0xc) & (cnt < 10):
        rd = test_api.oobhub_icd_read(0x1440028) #I2C_SL_STATUS
        helper.pinfo(f'MCTP_I2C I2C_SL_STATUS read out {hex(rd)}')    
        cnt += 1
    if rd & 0xc == 0xc:
        helper.perror(f'[I2C read] MCTP_I2C I2C_SL_STATUS read out {hex(rd&0xc)} expect !=0xc')
    test_api.oobhub_icd_write(0x1440024,slv_data) #I2C_SL_RCVD, set data to be read

    #wait for initiator bus idle
    rd = mst.I2C_STATUS_0.read()
    helper.pinfo(f'{mst.name} I2C_STATUS_0 read out {rd}')
    cnt = 0
    while (rd.value & 0x100 == 0x100) & (cnt < 3000) :
        rd = mst.I2C_STATUS_0.read()
        helper.pinfo("Waiting for bus idle...")
        cnt += 1
        helper.wait_sim_time('us',10)
    if rd.value & 0x100 == 0x100:
        helper.perror(f'[I2C read] {mst.name} I2C_STATUS_0 read out {hex(rd.value&0x100)} expect !=0x100')

    #check data  
    rd = mst.I2C_CMD_DATA1_0.read()
    helper.pinfo(f'{mst.name} I2C_CMD_DATA1_0 read out {rd}') 
    if (rd['DATA1'] != slv_data):
        helper.perror(f"[I2C read] Data transmission Fail -> EXP = {hex(slv_data)}, REAL = {hex(rd['DATA1'])}")
    else:
        print(f"Target receive correct data: {hex(slv_data)}")

with Test(sys.argv) as t:
    def parse_args():
        t.parser.add_argument("--mst", action='store', help="select the i2c master in erot I2C_IB0/I2C_IB1", default='I2C_IB1')
        t.parser.add_argument("--single", action='store_true', help="single slave or two slaves in this test")
        opts, unknown = t.parser.parse_known_args(sys.argv[1:])
        return opts
  
    options = parse_args() 

    if options.mst == 'I2C_IB0':
        i2c_mst = erot.I2C_IB0
    elif options.mst == 'I2C_IB1':
        i2c_mst = erot.I2C_IB1

    ##Test start
    helper.set_loop_back(0)
    # Enable interface master
    helper.i2c_write(addr=0x69, data=0x0100000325, size=5, i2c_id=3, en_10bits_addr=0) #RESET_0, cmd='d37
    helper.set_loop_back(1)
    test_api.oobhub_icd_init()
    slv_1_addr = 0x18
    slv_1_data = 0x78

    #MCTP I2C target mode init
    mctp_i2c_target_init(slv_1_addr)

    #NV_COOBHUB_MCTP_PHY_INTF_SELECTION_0 to toggle disable_noni3c_compliant_i2c
    test_api.oobhub_icd_write(0x1442580, 0x1) 

    initiator_clk_divisor_setting(mst=i2c_mst)

    #WAR use I2C0 loopback
    ########### 
    #I2C write#
    ###########
    i2c_initiator_write(i2c_mst, slv_1_addr, slv_1_data)

    test_api.oobhub_icd_write(0x1442580, 0x0) #NV_COOBHUB_MCTP_PHY_INTF_SELECTION_0 to toggle disable_noni3c_compliant_i2c

    #clear all interrupts
    test_api.oobhub_icd_write(0x1440028,0xff) #I2C_SL_STATUS
    ########## 
    #I2C read#
    ##########
    i2c_initiator_read(i2c_mst, 1, slv_1_addr, slv_1_data)

    
    #Loop write/read
    slv_2_addr = 0x18
    slv_2_data = []
    for i in range(4):
        data = random.randint(0x0, 0xff)
        slv_2_data.append(data)

    for i in range(4):
        test_api.oobhub_icd_write(0x1440028,0xff) #I2C_SL_STATUS
        i2c_initiator_write(i2c_mst, slv_2_addr, slv_2_data[i])
        test_api.oobhub_icd_write(0x1440028,0xff) #I2C_SL_STATUS
        i2c_initiator_read(i2c_mst, 1, slv_2_addr, slv_2_data[i])
    
