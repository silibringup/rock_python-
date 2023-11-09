import os

class NVBuild(object):

    def __init__(self):
        pass

    def get_output_variant_dir(self,dir):
        return os.path.abspath(os.path.join(os.path.dirname(__file__),'../../../env/src/erot_pkg_dev/tests/utils'))

    def get_src_dir(self,dir):
        return os.path.abspath(os.path.join(os.path.dirname(__file__),'../../../env/src/erot_pkg_dev/tests/utils'))