import logging



class cgroup_noop:
    def __init__(self, runtime):
        self.runtime = runtime
        self.log = logging.getLogger('RtOperator')

    def type(self):
        return "noop"

    def has_valid_rt_annotation(self,name, container_id, annotations):
        self.log.debug(f"Pod {name} checking realtime annotations for noop")
        return True

    def set_rt_pod(self, name, container_id, annotations):
        self.log.info(f"Pod {name} setting realtime capabilities for noop")
        return True
        