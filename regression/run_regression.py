#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3 -B
import argparse
import os
import re
import sys
import subprocess


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


    grouptag = options.grouptag
    grouptest = options.grouptest
    batch = options.batch




    