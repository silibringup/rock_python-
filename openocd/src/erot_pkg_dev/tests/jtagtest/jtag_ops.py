#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import *

with Test(sys.argv) as t:
    def parse_args():
        t.parser.add_argument("--action", type=str, help="JTAG action: reset, irscan, drscan, j2hunlock, j2hread, j2hwrite")
        t.parser.add_argument("--nbr_scan_bits", type=int, help="number of bits for ircan or drscan in integer")
        t.parser.add_argument("--address", type=str, help="target address of j2hread read and j2hwrite action, e.g., 0x1080")
        t.parser.add_argument("--value", type=str, help="value to send via JTAG irscan, drscan and j2hwrite action, e.g., 0x11223344")
        opts, unknown = t.parser.parse_known_args(sys.argv[1:])
        return opts

    opts = parse_args()

    print(f"command = {opts.action}")
    if opts.action == "reset":
        helper.jtag.Reset(0)
        helper.jtag.Reset(1)
    elif opts.action == "irscan":
        helper.jtag.IRScan(opts.nbr_scan_bits, opts.value)
    elif opts.action == "drscan":
        helper.jtag.DRScan(opts.nbr_scan_bits, opts.value)
    elif opts.action == "j2hunlock":
        file_in = os.path.dirname(os.path.abspath(__file__)) + "dft_j2h_PFNL.log"
        helper.j2h_unlock(file_in)
    elif opts.action == "j2hread":
        print(f"read from {opts.address} ...")
        rd = helper.j2h_read(int(opts.address, 16))
        print(f"read back {hex(rd)}")
    elif opts.action == "j2hwrite":
        print(f"write {opts.value} to {opts.address} ...")
        helper.j2h_write(int(opts.address, 16), int(opts.value, 16))
