#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
#This test ensure the sysctrl recovery sticky bit set before sending request to reset model for L1 reset in the scenario that forced recovery through oobhub cmd
from driver import * 

with Test(sys.argv) as t:
    def parse_args():
        t.parser.add_argument("--unit", action='store', help="Unit To Light On, Support Regular Expression", default='.*')
        t.parser.add_argument("--single", action='store_true', help="single slave or two slaves in this test")
        opts, unknown = t.parser.parse_known_args(sys.argv[1:])
        return opts
  
    options = parse_args()
    helper.set_loop_back(0)

    #Test start
    #Force recovery by OOBHUB cmd, set RESET_0.force_recovery 
    helper.i2c_write(addr = 0x69, data = 0x0f000225, size = 4, i2c_id=3, en_10bits_addr=0) #RESET_0, cmd='d37

    #Poll stiky bit and check if set
    erot.NV_PMC.RECOVERY_STATUS_0.poll(FORCED_RECOVERY_ON_NEXT_BOOT=1, timeout=500)

