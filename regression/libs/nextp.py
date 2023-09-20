#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3

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
    configs = list(set(mk_str_list(test_dict.pop('config'))))
    for config in configs:
        test_dict['config'] = config
        testObj = Test(**test_dict)
        testObjs += [testObj]

class Test:
    def __init__(self, name='', **kwargs):
        self.tags = []
        self.args = []
        self.name = ''
        if 'tags' in kwargs:
            self.tags = kwargs['tags']
        if 'args' in kwargs:
            self.args = kwargs['args']
        if 'name' in kwargs:
            self.name = kwargs['name']

    def gen_cmd(self):
        pass

