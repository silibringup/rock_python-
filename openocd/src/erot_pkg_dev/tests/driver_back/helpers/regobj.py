import sys
import os
import json
import argparse
import driver.helpers.helper as hp
import random
from RoPy import constraint
import gzip

class DotDict(dict):

    def __init__(self,*args, **kwargs):
        super(DotDict,self).__init__(*args,**kwargs)

    def __getattr__(self,key):
        value = self[key]

class Rock_block():

    helper = hp.Helper()
    def __init__(self,name,base,parent):
        self.name       = name
        self.base       = base
        self.block_list = []
        self.reg_list   = []
        self.offset     = 0
        self.parent     = parent

    def __repr__(self):
        res = "Block Name = %s , BASE = %x\n" % (self.name,self.base)
        for block in self.block_list:
            res += str(block)
        for reg in self.reg_list:
            res += str(reg)
        return res

    def build(self):
        for block in self.block_list:
            block.build()
    
    def get_reg_by_name(self,regname):
        return self.__getattr__(regname)


    def __getattr__(self,regname):
        searched = 0
        for reg in self.reg_list+self.block_list:
            if reg.name == regname:
                searched = 1
                return reg
        if searched != 1:
            self.helper.perror("Block %s not detect Reg %s" % (self.name,regname))
    
    def get_fullname(self):
        if self.parent is None:
            return self.name
        return f"{self.parent.get_fullname()}.{self.name}"


class Rock_reg():

    helper = hp.Helper()

    def __init__(self,name,block):
        self.name       = name
        self.field_list = [] # a list of dict by keys(name,lsb,msb,value,enums,action,default)
        self.offset     = 0
        self.value      = 0
        self.block      = block
        self.parent     = self.block
        self.reset_val  = 0
        self.reset_mask = 0
        self.read_mask  = 0
        self.write_mask = 0
        self.abs_addr   = 0

    def get_value_from_field(self):
        res = 0
        for field_obj in self.field_list:
            msb  = field_obj['msb']
            lsb  = field_obj['lsb']
            if field_obj['value'] > 2 ** (msb-lsb+1):
                self.helper.perror("field too big for %s = %x" % (field_obj['name'], field_obj['value']))
            res |= field_obj['value'] << lsb 
        return res

    def set_field_from_value(self,value):
        for field_obj in self.field_list:
            msb  = field_obj['msb']
            lsb  = field_obj['lsb']
            if isinstance(value, str):
                value = value[::-1]
                field_value = value[lsb:msb+1]
                filed_value = field_value[::-1]
                if field_value.isnumeric():
                    field_value = int(field_value, 2)
                field_obj['value'] = field_value 
            else:
                field_obj['value'] = ( value >> lsb ) & ( (1<<(msb-lsb+1)) - 1 )

    def helper_write(self,addr,value,priv_id=0,wait_tick=1,*args):
        if self.block.name == 'FSP':
            self.helper.log(f"begin to write FSP internal register {self.name}")
            self.helper.write_l0(addr,value,*args)
        else:
            self.helper.write(addr,value,priv_id,wait_tick,*args)


    def helper_read(self,addr,priv_id=0,*args):
        if self.block.name == 'FSP':
            self.helper.log(f"begin to read FSP internal register {self.name}")
            return self.helper.read_l0(addr,*args)
        else:
            return self.helper.read(addr,priv_id,*args)

    def write_headless(self,value=None,priv_id=0,*args, **kw):
        addr = self.block.base + self.offset
        if value is not None:
            self.helper.write_headless_in_head_mode(addr,value,priv_id,*args)
        else :
            for field in kw:
                searched = 0
                for field_obj in self.field_list:
                    if field == field_obj['name']:
                        searched = 1
                        if isinstance(kw[field],int):
                            field_obj['value'] = kw[field]
                        else:
                            field_obj['value'] = field_obj['enums'][kw[field]]
                        break
                if searched != 1:
                    self.helper.perror("Not able to find %s in Register %s" % (field,self.name) )
            value = self.get_value_from_field()
            self.helper.write_headless_in_head_mode(addr,value,priv_id,*args)



    def write(self,value=None,priv_id=0,wait_tick=1,*args, **kw): # *args priv etc, **kw field settings
        self.helper.pdebug(f"Write {self.name} {value}")
        addr  = self.block.base + self.offset #TODO@Changliu to enhance if more than one layer is required

        if value is not None:
            self.helper_write(addr,value,priv_id,wait_tick,*args)
        else :
            for field in kw:
                searched = 0
                for field_obj in self.field_list:
                    if field == field_obj['name']:
                        searched = 1
                        if isinstance(kw[field],int):
                            field_obj['value'] = kw[field]
                        else:
                            field_obj['value'] = field_obj['enums'][kw[field]]
                        break
                if searched != 1:
                    self.helper.perror("Not able to find %s in Register %s" % (field,self.name) )
            value = self.get_value_from_field()
            self.helper_write(addr,value,priv_id,wait_tick,*args)

    def read_headless(self,priv_id=0,*args): #*args priv etc
        addr  = self.block.base + self.offset #TODO@Changliu to enhance if more than one layer is required
        value = self.helper.read_headless_in_head_mode(addr,priv_id,*args)
        self.set_field_from_value(value)
        res = DotDict()
        for field_obj in self.field_list:
            res[field_obj['name']] = field_obj['value']
        res.value = value
        return res

    def read(self,priv_id=0,*args): #*args priv etc
        addr  = self.block.base + self.offset #TODO@Changliu to enhance if more than one layer is required
        value = self.helper_read(addr,priv_id,*args)
        self.set_field_from_value(value)
        res = DotDict()
        for field_obj in self.field_list:
            res[field_obj['name']] = field_obj['value']
        res.value = value
        self.helper.pdebug(f"Read {self.name} {res}")
        return res 

    def update(self,priv_id=0,*args, **kwargs): # *args priv etc
        rd_obj = self.read(priv_id,*args)
 
        new_kwargs = {}
        for fld in rd_obj:
            new_kwargs[fld] = rd_obj[fld]

        for fld in kwargs:
            if fld in rd_obj:
                new_kwargs[fld] = kwargs[fld]
            else:
                self.helper.perror("Not able to find %s in Register %s" % (fld, self.name))
        self.write(priv_id=priv_id, *args, **new_kwargs)

    def poll(self, priv_id=0,timeout=100000, interval=0, *args, **kwargs):
        count = 0
        while count < timeout:
            rd_obj = self.read(priv_id,*args)

            matched_value = 1
            for fld in kwargs:
                if isinstance(kwargs[fld],int):
                    search_value = kwargs[fld]
                else:
                    for field_obj in self.field_list:
                        if fld == field_obj['name']:
                            search_value = field_obj['enums'][kwargs[fld]]
                            break
                if rd_obj[fld] != search_value:
                    matched_value = 0
                    break

            count += 1
            if matched_value:
                self.helper.log(f"Poll REG {self.name} done after {count} times. Reg value = {hex(rd_obj.value)}")
                return
            if interval:
                #self.helper.log(f"Waiting {interval} ns")
                self.helper.wait_sim_time('ns',interval)
        self.helper.perror(f"Poll timeout after {count} times try. Reg value = {hex(rd_obj.value)}")
        
    def __repr__(self):
        res = '0x%04x(%s)\t' % (self.offset,self.name)
        for field in self.field_list:
            res += '%s(%x)\t' % ( field['name'], field['value'])
        return res + '\n'

    def __str__(self):
        return self.get_fullname()

    def get_fullname(self):
        if self.parent is None:
            return self.name
        return f"{self.parent.get_fullname()}.{self.name}"



def gen_ip(ip_reg_dict):
    ip_reg_block = Rock_block(ip_reg_dict['name'],ip_reg_dict['base'],erot) 
    sub_blocks = ip_reg_dict['file']
    
    sub_block_keys = sub_blocks.keys()
    if len(sub_block_keys) > 1:
        multi_sub_block = 1
    else:
        multi_sub_block = 0

    for key in sub_block_keys:
        if multi_sub_block:
            ip_reg_sub_block = Rock_block(key,ip_reg_dict['base'],ip_reg_block)
        else:
            ip_reg_sub_block = ip_reg_block

        reg_list = sub_blocks[key]['register_list']
        for reg_name in reg_list:
            if sub_blocks[key][reg_name]['array'] is None:
                hp.perror("Reg %s not detect attribute 'array' !" % reg_name)
            if sub_blocks[key][reg_name]['array'] is False:
                reg = Rock_reg(reg_name,ip_reg_sub_block)
                reg.offset = sub_blocks[key][reg_name]['addr']
                reg.reset_val = sub_blocks[key][reg_name]['reset_val']
                reg.reset_mask = sub_blocks[key][reg_name]['reset_mask']
                reg.read_mask = sub_blocks[key][reg_name]['read_mask']
                reg.write_mask = sub_blocks[key][reg_name]['write_mask']
                reg.abs_addr = reg.block.base + reg.offset

                ip_reg_sub_block.reg_list.append(reg)
                field_list = sub_blocks[key][reg_name]['field_list']
                for field_name in field_list:
                    reg.field_list.append({'name'   :  field_name, 
                                            'value'  :  0,
                                            'lsb'    :  sub_blocks[key][reg_name][field_name]['lsb'],
                                            'msb'    :  sub_blocks[key][reg_name][field_name]['msb'],
                                            'enums'  :  sub_blocks[key][reg_name][field_name]['enums'],
                                            'action' :  sub_blocks[key][reg_name][field_name]['action'],
                                            'default':  sub_blocks[key][reg_name][field_name]['default']})

        if multi_sub_block:
            ip_reg_block.block_list.append(ip_reg_sub_block)
    erot.block_list.append(ip_reg_block)


erot = Rock_block("erot",0,None)
    
def erotbuild():
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", action='store', help="SIM_HEAD,SIM_HEADLESS,FPGA_HEAD,FPGA_HEADLESS", default='SIM_HEADLESS')
    parser.add_argument("--target",   type=str, default="simv_top", help="simv_top, simv_fpga,fpga")
    args, unknown = parser.parse_known_args()
    
    EROT_IP_REG_PY_LIST = []
    jname = "EROT_IP_REG_PY_LIST.json"
    
    if args.target != 'fpga':
        sys.path.append(os.environ['NVBUILD_PY_LIB'])
        import nvbuildutils
        nvbuild = nvbuildutils.NVBuild()
        reg_model_file = os.path.join(nvbuild.get_output_variant_dir('erot_verif/reg_gen'), jname)
    else:
        reg_model_file = f"{os.path.dirname(os.path.realpath(__file__))}/{jname}"

    if os.path.exists(reg_model_file):
        try:
            with gzip.open(reg_model_file, 'r') as f:
                EROT_IP_REG_PY_LIST = json.loads(f.read().decode('utf-8'))
        except:
            with open(reg_model_file, 'r') as f:
                EROT_IP_REG_PY_LIST = json.load(f)
    else:
        print(f"ERROR: No {jname} found in output's simv dir")
    
    for IP in EROT_IP_REG_PY_LIST:
        gen_ip(IP)

    global erot
    erot.build()


erotbuild()




class RandomSet(constraint.Problem):
    def __init__(self, seed=None):
        super(RandomSet, self).__init__()
        parser = argparse.ArgumentParser()
        parser.add_argument('--seed', default=1)
        args, unknown = parser.parse_known_args()
        self.__rng = random.Random()
        self.__seed = seed or args.seed
        self.__rng.seed(self.__seed)
        self.__rand_regs = {}

    def randomize(self):
        ans = self.__rng.sample(self.getSolutions(), 1)[0]
        for k, v in self.__rand_regs.items():
            v.value = ans[k]
        return ans

    def add_reg(self, var, ran=None):
        if not isinstance(var, Rock_reg):
            raise TypeError(f"{var} is not of type erot reg")
        _inside = ran or range(-(1<<32), (1<<32)-1)
        self.addVariable(str(var), _inside)
        self.__rand_regs[str(var)] = var
    
    def add_int(self, var, ran=None):
        if not isinstance(var, str):
            raise TypeError(f"{var} is not of type str")
        _inside = ran or range(-(1<<32), (1<<32)-1)
        self.addVariable(str(var), _inside)

    def add_constraint(self, f, vars):
        self.addConstraint(f, [str(i) for i in vars])
