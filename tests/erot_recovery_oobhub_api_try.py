#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
import os
import time
from driver import *

with Test(sys.argv) as t:
#    def parse_args():
#        t.parser.add_argument("--mfg", action="store_true", default=False, help="enable mfg")
#        opts, unknown = t.parser.parse_known_args(sys.argv[1:])
#        return opts
#
#    opts = parse_args()
    helper.OOBHUB_status_report()
