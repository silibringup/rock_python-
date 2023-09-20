#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3 -B
import argparse
import os
import re
import sys
import subprocess
import time
import importlib
sys.path.append(os.path.join(os.path.dirname(__file__),'libs'))

###################################
# Main
################################### 
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Regression script')

    parser.add_argument("--batch","-b",
                        type=str,
                        default="tmp_batch",
                        help="Specify the batch directory to run your regresssion, default is tmp_batch")
    parser.add_argument("--grouptag","-g",
                        type=str,
                        default = None,
                        help="Specify tests defined in test plan that are labeled with certain tag name to run")
    parser.add_argument("--grouptest","-t",
                        type=str,
                        default = None,
                        help="Specify test name pattern to search in defined in test plan to run")

    options = parser.parse_args()
    grouptag = options.grouptag
    grouptest = options.grouptest
    batch = options.batch

    testplan = os.path.join(os.path.dirname(__file__),'testlist','erot_fpga.py')

    spec = importlib.util.spec_from_file_location("module.name",testplan)
    plan = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(plan)





    