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
    parser = argparse.ArgumentParser(description='Test launch script')
    parser.add_argument("--python_test", "-py",
                        type=str,
                        default=None,
                        help="Denote python test name")
    parser.add_argument("--pyarg","-pyarg",
                        action="append",
                        default=[""],
                        help="python test options")

    options, unknown = parser.parse_known_args()
    python_test = options.python_test
    pyarg = ' '.join(options.pyarg)

    pyarg = f' --platform JTAG --target fpga --disable_peripheral_init_agent {pyarg} '

    if python_test:
        search_path = os.path.abspath(os.path.join(os.path.dirname(__file__),'../test'))
        searched_python_list = []
        for _root, _dir, _files in os.walk(search_path):
            for filename in _files:
                if filename == python_test or ( '%s.py' % python_test ) == filename:
                    searched_python_list.append(os.path.join(_root, filename))
        if len(searched_python_list)!= 1: 
            print("Error to find correct Python file %s" % python_test)
            sys.exit(1)
        python_exe = f'python -B {searched_python_list[0]}'
        pycmd = f"{python_exe} {pyarg} --port 1234 --ip 127.0.0.1 "
        print(pycmd) 
        pyproc = subprocess.Popen([pycmd], shell=True)

    if python_test and pyproc.wait():
        print(f"ERROR: {python_test} failed")
        sys.exit(1)