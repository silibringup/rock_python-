#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import * 

with Test(sys.argv) as t:
    def misc_i2c_read_io_expander(mst, golden_data ,slv_addr, io_expander_cmd=0x00, divisor = 25):
        #for prdata[19:20] coverage
        rd =  mst.I2C_CLK_DIVISOR_REGISTER_0.read()
        helper.log(rd)
        mst.I2C_CLK_DIVISOR_REGISTER_0.write(I2C_CLK_DIVISOR_STD_FAST_MODE = 0xFFFF)
        rd =  mst.I2C_CLK_DIVISOR_REGISTER_0.read()
        helper.log(rd)
        if (rd['I2C_CLK_DIVISOR_STD_FAST_MODE'] != 0xFFFF):
            helper.perror("Wrong I2C_CLK_DIVISOR_STD_FAST_MODE read value")

        #set to SM/FM/FM+ speed
        divisor_value = divisor
        helper.log(f"{mst.name} Set I2C_CLK_DIVISOR_STD_FAST_MODE to {divisor_value} for read transaction")
        mst.I2C_CLK_DIVISOR_REGISTER_0.write(I2C_CLK_DIVISOR_STD_FAST_MODE = divisor_value)
        rd =  mst.I2C_CLK_DIVISOR_REGISTER_0.read()
        helper.log(f"Read I2C_CLK_DIVISOR_STD_FAST_MODE = {rd['I2C_CLK_DIVISOR_STD_FAST_MODE']}")
        mst.I2C_CONFIG_LOAD_0.write(MSTR_CONFIG_LOAD = 0x1)
        rd = mst.I2C_CONFIG_LOAD_0.read()
        while rd['MSTR_CONFIG_LOAD'] == 0x1 :
            rd = mst.I2C_CONFIG_LOAD_0.read()
            helper.log ("Wait for setting master's register")

        #pre-step: define master and slave
        send = 1
        no_ack = 0
        cmd2 = 1 #read
        cmd1 = 0 #write
        length =  0 #in bytes
        slv2 = 1 #

        #seq2: configure master register and trigger transaction
        mst.I2C_CMD_ADDR0_0.write((slv_addr<<1)+0) 
        mst.I2C_CMD_ADDR1_0.write((slv_addr<<1)+1) # read after write

        mst.I2C_CMD_DATA1_0.write(io_expander_cmd)
        mst_cnfg = (no_ack<<8)+(cmd2<<7)+(cmd1<<6)+(slv2<<4)+(length<<1)        
        helper.log (f"{mst.name} mst_cnfg = %d for read transaction" % mst_cnfg)
        mst.I2C_CNFG_0.write(mst_cnfg)    
        mst.I2C_CONFIG_LOAD_0.write(0x1)
        rd = mst.I2C_CONFIG_LOAD_0.read()
        helper.log (rd)
        while rd.value & 0x1 == 0x1 :
            rd = mst.I2C_CONFIG_LOAD_0.read()
            helper.log ("Wait for setting master's register")
        mst.I2C_CNFG_0.write((send<<9)+mst_cnfg)
        rd = mst.I2C_CNFG_0.read()

        #wait for master bus idle
        rd = mst.I2C_STATUS_0.read()
        while (rd['BUSY'] == 0x1) :
            rd = mst.I2C_STATUS_0.read()
            helper.log("Waiting for bus idle...")

        rd = mst.I2C_CMD_DATA2_0.read()
        helper.pinfo(rd.value)
        #if (rd != golden_data):
        #    helper.perror() 

    
    test_api.ap_i2c_init()
    slave_io_expander_addr_1 = 0x20
    slave_io_expander_addr_2 = 0x21
    
    io_expander_read_golden_1 = 0x5a
    io_expander_read_golden_2 = 0xa5
    
    #IO_EXPANDER master write
    helper.pinfo('check io expander 1')
    misc_i2c_read_io_expander(mst = erot.IO_EXPANDER, golden_data=io_expander_read_golden_1 ,slv_addr = slave_io_expander_addr_1, io_expander_cmd = 0x00, divisor = 25)
    helper.pinfo('check io expander 2')
    misc_i2c_read_io_expander(mst = erot.IO_EXPANDER, golden_data=io_expander_read_golden_2 ,slv_addr = slave_io_expander_addr_2, io_expander_cmd = 0x00, divisor = 25)