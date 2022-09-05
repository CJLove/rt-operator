import logging
from pathlib import Path

class crio:
    base_dir = Path('/sys/fs/cgroup/cpu,cpuacct/kubepods.slice')
    def __init__(self):
        self.log = logging.getLogger('RtOperator')

    def type(self):
        return 'cri-o'

    def get_base_path(self):
        return self.base_dir

    def get_cpu_list(self):
        cpu_list = [d for d in self.base_dir.glob('kubepods-pod*/*/cpu.rt_runtime_us') if d.is_file()]
        return cpu_list

    def get_container_dir(self, container_id):
        cont_dirs = [ d for d in self.base_dir.glob('kubepods-pod*/crio-'+container_id+'*') if d.is_dir()]
        return cont_dirs