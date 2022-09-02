import logging

# Placeholder for Kubernetes with cgroupv2

class cgroup_v2:
    def __init__(self):
        self.log = logging.getLogger('RtOperator')

    def type(self):
        return "cgroup_v2"

    def has_valid_rt_annotation(self,annotations):
        return True

    def set_rt_pod(self, container_id, annotations):
        return True