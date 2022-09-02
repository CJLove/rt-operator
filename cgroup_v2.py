import logging

# Placeholder for Kubernetes with cgroupv2

class cgroup_v2:
    def __init__(self):
        self.log = logging.getLogger('RtOperator')

    def type(self):
        return "cgroup_v2"

    def current_rt_runtime_us(self):
        return 0

    def set_rt_runtime_us(self, container_id, rt_runtime_us):
        return True
        