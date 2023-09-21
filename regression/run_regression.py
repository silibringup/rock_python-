#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3 -B
import argparse
import os
import re
import sys
import subprocess
import time
import importlib
sys.path.append(os.path.join(os.path.dirname(__file__),'libs'))
import stat

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

    lists = []
    if grouptag :
        for test in plan.testObjs:
            if grouptag in test.tags:
                lists.append(test)
    elif grouptest :
        for test in plan.testObjs:
            if re.match(grouptest,test.name):
                lists.append(test)
    else:
        for test in plan.testObjs:
            #print(test.gen_cmd())
            lists.append(test)

    batch_dir = os.path.join(os.path.dirname(__file__),batch)
    if not os.path.exists(batch_dir):
        os.mkdir(batch)

    infra_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'../openocd/src/erot_pkg_dev/tests'))
    cur_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    clean_file = os.path.join(os.path.dirname(__file__),'clean.sh')
    logcheck = os.path.join(os.path.dirname(__file__),'logcheck')
    openocd = os.path.abspath(os.path.join(os.path.dirname(__file__),'../openocd/src','openocd'))
    cfg = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','sr01.cfg'))

    testlist = os.path.join(batch_dir,'testlist.sh')
    with open(testlist,'w') as t:
        for test in lists:
            test_url = os.path.join(batch_dir,test.name)
            if not os.path.exists(test_url):
                os.mkdir(test_url)
            t.write(f'sh {test_url}/run.sh\n')
            test_cmd = os.path.join(test_url,'run.sh')
            with open(test_cmd,'w') as f:
                f.write(f'export PYTHONPATH={infra_path}\n')
                f.write(f'cd {test_url}\n\n')
                f.write(f'sudo {clean_file}\nsleep 1\n\n')
                f.write(f'sudo raspi-gpio set 23 op dl; sudo raspi-gpio set 23 op dh\nsleep 1\n\n')
                f.write(f'sudo {openocd} -f {cfg} -socket 1234 -no_scan_verbo & \n\n')
                f.write(f'python {cur_path}/run_test.py {test.gen_cmd()}')
                f.write('\n\n')
                f.write(f'sudo {clean_file}\nsleep 1\n\n')
                f.write(f'python {logcheck}\n')
            os.chmod(test_cmd,stat.S_IRWXU) 
    os.chmod(testlist,stat.S_IRWXU)            
            
    cmd = f"sh {testlist}"
    #pyproc = subprocess.Popen([cmd], shell=True) 






    