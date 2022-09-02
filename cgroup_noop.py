import logging



class cgroup_noop:
    def __init__(self):
        self.log = logging.getLogger('RtOperator')

    def type(self):
        return "noop"

    def has_valid_rt_annotation(self,annotations):
        return True

    def set_rt_pod(self, container_id, annotations):
        return True
        