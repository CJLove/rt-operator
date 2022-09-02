import logging

# Placeholder for Kubernetes with cgroupv2

class cgroup_v2:
    def __init__(self):
        self.log = logging.getLogger('RtOperator')

    def type(self):
        return "cgroup_v2"

    def has_valid_rt_annotation(self, name, container_id, annotations):
        self.log.debug(f"Pod {name} checking realtime annotations for cgroupv2")
        return False

    def set_rt_pod(self, name, container_id, annotations):
        self.log.debug(f"Pod {name} setting realtime capabilities for cgorupv2")
        return False