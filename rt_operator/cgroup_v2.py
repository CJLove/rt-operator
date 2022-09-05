import logging

# Placeholder for Kubernetes with cgroupv2

class cgroup_v2:
    def __init__(self, runtime):
        self.runtime = runtime
        self.log = logging.getLogger('RtOperator')

    def type(self):
        return "cgroup_v2"

    def has_valid_rt_annotation(self, name, container_id, annotations):
        # Currently no cgroup manipulation required for cgroupv2
        self.log.debug(f"Pod {name} with realtime annotations for cgroupv2")
        return False

    def set_rt_pod(self, name, container_id, annotations):
        # No action to take here
        self.log.debug(f"Pod {name} with realtime annotations for cgorupv2")
        return False