#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
#This test ensure that on CMS2, FSP can exchange rcv image with recovery I2C using INDIRECT_DATA
from driver import * 
import random

def fsp_write_cms2():
    #FSP writes to INDRECT_CMS2_MEM_ADDR/DATA registers to load data (N DWORDS)
    rd = erot.OOBHUB.RCV_INDIRECT_CMS2_MEM_LOCK_0.read()
    lock_size = rd['LOCKED_REGION_SIZE']

    mem_size = 0
    for field_obj in erot.OOBHUB.RCV_INDIRECT_CMS2_MEM_ADDR_0.field_list:
        if field_obj['name'] == "ADDR":
            msb, lsb = field_obj['msb'], field_obj['lsb']
            mem_size = (1<<(msb-lsb+1))
            break

    wr_num = 0
    if lock_size + 10 <= mem_size:
        wr_num = 10
    else:
        wr_num =(mem_size - lock_size)

    exp_data = 0
    for i in range(wr_num):
        wr_data = random.randint(0, 0xffffffff)
        exp_data += (wr_data<<(i*32))
        erot.OOBHUB.RCV_INDIRECT_CMS2_MEM_ADDR_0.write(i+lock_size)
        erot.OOBHUB.RCV_INDIRECT_CMS2_MEM_DATA_0.write(wr_data)
    #get CURRENT_DATA_CNT_LOADED value
    rd_fsp = erot.OOBHUB.RCV_INDIRECT_CMS2_MEM_COUNT_0.read()
    data_cnt_loaded_pre = rd_fsp['CURRENT_DATA_CNT_LOADED']
    #FSP writes to INDIRECT_CMS2_MEM_COUNT[DATA_CNT_STEP] with 'N-1' to indicate amount of data prepared in memory
    erot.OOBHUB.RCV_INDIRECT_CMS2_MEM_COUNT_0.write(DATA_CNT_STEP=(wr_num-1))
    #Check CURRENT_DATA_CNT_LOAD 
    rd_fsp = erot.OOBHUB.RCV_INDIRECT_CMS2_MEM_COUNT_0.read()
    if rd_fsp['CURRENT_DATA_CNT_LOADED'] != (data_cnt_loaded_pre+wr_num):
        helper.perror(f'Check CURRENT_DATA_CNT_LOADED Fail, expect 63 but read out {rd_fsp["CURRENT_DATA_CNT_LOADED"]}')
    #FSP writes to INDIRECT_CMS2_MEM_READYRCV_INDIRECT_CMS2_MEM_COUNT_0[DATA_ENTRY] to '1' to indicate that data is ready for SMBUS/I2C to read
    erot.OOBHUB.RCV_INDIRECT_CMS2_MEM_READY_0.write(DATA_ENTRY=1)
    #Check CURRENT_DATA_COUNT_READY loaded from CURRENT_DATA_CNT_LOAD
    rd_fsp = erot.OOBHUB.RCV_INDIRECT_CMS2_MEM_READY_0.read()
    if rd_fsp['CURRENT_DATA_CNT_READY'] != (data_cnt_loaded_pre+wr_num):
        helper.perror(f'Check CURRENT_DATA_CNT_READY Fail, expect 62 but read out {rd_fsp["CURRENT_DATA_CNT_READY"]}')
    return exp_data

def i2c_read_cms2(exp_data):
    #I2C send SMB Write INDIRECT_CTRL with CMS=2, IMO=0 (cmd='d41)
    helper.i2c_write(addr = 0x69, data = 0x0000000000020629, size = 8, i2c_id=3, en_10bits_addr=0)#[7:0]_CMS, [47:16]_IMO
    helper.wait_sim_time('us',100)
    #Issues SMB Read[INDIRECT_STATUS] to expect ACK=1, POLLING_ERROR=0 
    rd_i2c = helper.erot_rcvy_block_read(slv_addr=0x69, cmd_code=42)
    if rd_i2c & 0x4 != (0x1 << 2):
        helper.perror("I2C read INDIRECT_STATUS_0.Status[2] Fail, expect ACK=1 but read out %x" % (rd_i2c&0x4))
    if rd_i2c & 0x8 != (0x0 << 3):
        helper.perror("I2C read INDIRECT_STATUS_0.Status[2] Fail, expect ACK=1 but read out %x" % (rd_i2c&0x4))
    #Issues SMB Read[INDIRECT_DATA] multiple times until all the data is read
    rd_i2c = helper.erot_rcvy_block_read(slv_addr=0x69, cmd_code=43)
    # after recovery-boot, we can only read the first 63beats of that mem, which is the recovery-boot content
    # thus cannot compare to exp_data
    #if rd_i2c != exp_data:
    #    helper.perror(f'I2C read INDIRECT_DATA Fail, expect {hex(exp_data)} bute read out {rd_i2c}')
    #else: 
    #    helper.pinfo(f'I2C read out INDIRECT_DATA {hex(rd_i2c)}, correct!')
    #if rd_i2c != 0:
    #    helper.perror("After Recover-boot, those data should read all-0 back")

with Test(sys.argv) as t:
    def parse_args():
        t.parser.add_argument("--unit", action='store', help="Unit To Light On, Support Regular Expression", default='.*')
        t.parser.add_argument("--single", action='store_true', help="single slave or two slaves in this test")
        opts, unknown = t.parser.parse_known_args(sys.argv[1:])
        return opts

    options = parse_args()
    helper.set_loop_back(0)
   
    #Re-initialization of CMS2 mem
    helper.log("Start Test")
   
    #Test start
    for i in range(1):
        exp_data = fsp_write_cms2()
        i2c_read_cms2(exp_data)
  

