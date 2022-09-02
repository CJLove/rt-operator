import logging



class cgroup_noop:
    def __init__(self):
        self.log = logging.getLogger('RtOperator')

    def type(self):
        return "noop"

    def current_rt_runtime_us(self):
        return 0

    def set_rt_runtime_us(self, container_id, rt_runtime_us):
        return True
        