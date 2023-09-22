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
import signal
from termcolor import colored

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
    if os.path.exists(batch_dir):
        os.system(f'rm -rf {batch_dir}')
    os.mkdir(batch)

    infra_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'../openocd/src/erot_pkg_dev/tests'))
    cur_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    clean_file = os.path.join(os.path.dirname(__file__),'libs','clean.sh')
    logcheck = os.path.join(os.path.dirname(__file__),'libs','logcheck')
    openocd = os.path.abspath(os.path.join(os.path.dirname(__file__),'../openocd/src','openocd'))
    cfg = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','sr01.cfg'))

    testlist = os.path.join(batch_dir,'testlist.sh')
    with open(testlist,'w') as t:
        for test in lists:
            test_url = os.path.join(batch_dir,test.name)
            if not os.path.exists(test_url):
                os.mkdir(test_url)
            #t.write(f'sh {test_url}/run.sh > /dev/null 2>&1\n')
            #t.write(f'sudo {clean_file}\nsleep 1\n\n')
            t.write(f'sh {test_url}/run.sh \n\n')
            t.write(f'sudo {clean_file}\nsleep 1\n\n')
            test_cmd = os.path.join(test_url,'run.sh')
            with open(test_cmd,'w') as f:
                f.write(f'export PYTHONPATH={infra_path}\n')
                f.write(f'cd {test_url}\n\n')
                f.write(f'sleep 1\nsudo raspi-gpio set 23 op dl; sudo raspi-gpio set 23 op dh\nsleep 1\n\n')
                f.write(f'sudo {openocd} -f {cfg} -socket 1234 -no_scan_verbo & \n\n')
                f.write(f'python {cur_path}/run_test.py {test.gen_cmd()} 2>&1| tee rockpy.log\n\n')
                f.write(f'sudo killall -9 openocd\n\n')
                f.write('\n\n')
            os.chmod(test_cmd,stat.S_IRWXU) 
    os.chmod(testlist,stat.S_IRWXU)            

    def run_cmd(cmd):
        p = subprocess.Popen(cmd,shell=True) 
        p.communicate()
    
    
    print('\n\n|**************** regression start******************|\n')
    print(f' There are {len(lists)} tests in this regression')
    print('\n|**************** regression start******************|\n\n')

    for test in lists:
        print(f'\n\n|******* Test {test.name} Start Running *******|\n\n')
        test_url = os.path.join(batch_dir,test.name)
        test_cmd = os.path.join(test_url,'run.sh')
        run_cmd(f'sh {test_cmd}')
        print(f'\n\n|******* Test {test.name} Done ********|\n\n ')


    print('|**************** regression report ******************|\n')
    fail_list= []
    pass_list= []
    for test in lists:
        testout = os.path.join(batch_dir,test.name,'RoPy.log')
        if os.path.exists(testout):
            with open(testout,'r') as f:
                if not re.search('\[RockPy\].+TEST SUCCESS COMPLETED', f.read()):
                    fail_list.append(test.name)
                else :
                    pass_list.append(test.name)
        else:
            print(f'Attention : please check test {test.name} for Ropy.log which does not exist')
            fail_list.append(test.name)
    print(f'    Total Tests  : {len(lists)}')
    print(colored(f'    Pass  Tests  : {len(pass_list)}','green'))
    print(colored(f'    Fail  Tests  : {len(fail_list)}','red'))
    print('    Passing Rate : {:.2%}\n'.format(len(pass_list)/len(lists)))
    print('|**************** regression report ******************|\n\n')

    with open (os.path.join(batch_dir,'result.txt'),'w') as f:
        f.write(f'Result Summary :\n')
        f.write(f'  Total Tests  : {len(lists)}\n')
        f.write(f'  Pass  Tests  : {len(pass_list)}\n')
        f.write(f'  Fail  Tests  : {len(fail_list)}\n')
        f.write('  Passing Rate : {:.2%}\n'.format(len(pass_list)/len(lists)))
        f.write('\n\n')
        if len(fail_list):  
            f.write(f'----- FAIL TEST {len(fail_list)} -----\n') 
            for test in fail_list:
                f.write(f'   TEST {test}  FAIL  URL {os.path.join(batch_dir,test)}\n') 
            
        if len(pass_list):  
            f.write(f'----- PASS TEST {len(pass_list)} -----\n') 
            for test in pass_list:
                f.write(f'   TEST {test}  PASS  URL {os.path.join(batch_dir,test)}\n')         

    print('Regression Cleanup')
    run_cmd(f'sudo {clean_file}\nsleep 1\n\n')




    

    
