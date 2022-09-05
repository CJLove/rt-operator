import logging
from pathlib import Path

class containerd:
    base_dir = Path('/sys/fs/cgroup/cpu,cpuacct/kubepods')
    def __init__(self):
        self.log = logging.getLogger('RtOperator')

    def type(self):
        return 'containerd'

    def get_base_path(self):
        return self.base_dir

    def get_cpu_list(self):
        cpu_list = [d for d in self.base_dir.glob('pod*/*/cpu.rt_runtime_us') if d.is_file()]
        return cpu_list

    def get_container_dir(self, container_id):
        cont_dirs = [ d for d in self.base_dir.glob('pod*/'+container_id) if d.is_dir()]
        return cont_dirs

    
    
