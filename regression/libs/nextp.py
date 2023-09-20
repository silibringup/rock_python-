#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
import re

class Plan:
    def __init__(self, claimed_feature='', plan_level='system', plan='', skipvrt=False):
        self.run_script = ''

class feature:
    def __init__(self, tree=''):
        pass

    def __enter__(self):
        pass
    def __exit__(self,exc_type,exc_val,exc_tb):
        pass

def mk_str_list(str_or_list):
    if isinstance(str_or_list, str):
        return [str_or_list]
    elif isinstance(str_or_list, list):
        return str_or_list
    raise TypeError( "Error while mr_str_list from %s(%s)"%(str_or_list, type(str_or_list)) )

testObjs = []
def AddTest(**test_dict):
    global testObjs
    if 'tags' in test_dict:
        test_dict['tags'] = list(set(test_dict['tags']))
    testObj = Test(**test_dict)
    testObjs += [testObj]

class Test:
    def __init__(self,**kwargs):
        self.tags = []
        self.args = []
        self.cmd = ''
        if 'tags' in kwargs:
            self.tags = kwargs['tags']
        if 'args' in kwargs:
            self.args = kwargs['args']
        if 'name' in kwargs:
            self.name = kwargs['name']
        
        #print(self.args)
            

    def gen_cmd(self):
        self.cmd = 'python run_test.py'
        arg_str = ' '.join(self.args)

        py_result = re.findall('-py\s*\w+.py',arg_str)
        self.cmd = f'{self.cmd} {py_result[0]}'

        pyarg_result = re.findall('-pyarg\s*\'.*?\'',arg_str)
        for arg in pyarg_result:
            arg = arg.replace('NOT_DEFAULT_GO_MAIN','')
            arg = arg.replace('--target simv_fpga','')
            if not re.match("-pyarg\s*'\s*'\s*",arg):
                self.cmd = f'{self.cmd} {arg}'
        return self.cmd

                
