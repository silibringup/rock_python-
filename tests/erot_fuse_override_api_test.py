#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import *

###################################################
# This test intends to cover:
# 1. *req_addr[0] and *req_addr[25] from 4 masters
# 2. *_resp_pri_error from fabric to master
###################################################
with Test(sys.argv) as t:
    helper.log("test start")
    test_api.fuse_opts_override("opt_secure_pri_source_isolation_en", 1)

    helper.log("test finish")
