from pathlib import Path
import logging

# cgroup v1 notes for Kubernetes:
#
# pods in the Guaranteed QoS class will have pod-level cgroups under 
# /sys/fs/cgroup/cpu,cpuacct/kubepods/pod<PodID>
#
# container-level ccgroups will be under 
# /sys/fs/cgroup/cpu,cpuacct/kubepods/pod<PodID>/<containerID>

class cgroup_v1:
    base_dir = Path('/sys/fs/cgroup/cpu,cpuacct/kubepods')

    def __init__(self, cap):
        self.log = logging.getLogger('RtOperator')
        self.cap = cap
        self.log.info(f"Using cpu.rt_runtime_us capacity {cap} for real-time PODs")
        if self.__write_cpu_rt_runtime_us(self.base_dir, cap):
            self.log.debug(f"Wrote {cap} to kubepods.cpu.rt_runtime_us")

    def type(self):
        return "cgroup_v1"

    def has_valid_rt_annotation(self, name, container_id, annotations):
        if 'rt_runtime_us' in annotations:
            try:
                # Requested realtime allocation for this pod
                req_rt_runtime_us = int(annotations['rt_runtime_us'])
                # Current realtime allocation for this pod (could be 0)
                cur_rt_runtime_us = self.__current_rt_runtime_us(container_id)
                #
                aggregate_usage = self.__aggregate_rt_runtime_us()
                available = self.cap - aggregate_usage - cur_rt_runtime_us
                # rt_runtime_us annotation must be in range 0..self.cap
                valid = req_rt_runtime_us <= self.cap
                self.log.debug(f"Pod: {name} Current: {cur_rt_runtime_us} Requested: {req_rt_runtime_us} Capacity: {self.cap} Available: {available}")

                return valid

                # return cpu_rt_runtime_us <= self.cap - current_usage
            except:
                self.log.error(f"Pod {name} invalid rt_runtime_us annotation")
                return False

        self.log.error(f"Pod {name} missing rt_runtime_us annotation")
        return False

    def set_rt_pod(self, name, container_id, annotations):
        if 'rt_runtime_us' not in annotations:
            return False
        try:
            cpu_rt_runtime_us = int(annotations['rt_runtime_us'])
        except:
            self.log.error(f"Pod {name} invalid rt_runtime_us annotation")
            return False
        else:
            # Using Path.glob() find the pod subdirectory containing the specific container_id 
            # directory. Expect exactly 1 directory to match this
            cont_dirs = [ d for d in self.base_dir.glob('pod*/'+container_id) if d.is_dir()]
            if len(cont_dirs) == 1:
                # Get the container directory and the pod directory
                cont_dir = cont_dirs[0]
                pod_dir = cont_dir.parent

                if self.__write_cpu_rt_runtime_us(pod_dir,cpu_rt_runtime_us) and self.__write_cpu_rt_runtime_us(cont_dir, cpu_rt_runtime_us):
                    self.log.info(f"Pod {name} cpu.rt_runtime_us set to {cpu_rt_runtime_us}")
                    return True
        
            self.log.error(f"Pod {name} unable to find container cgroup using {container_id}")
            return False  

    # Return the current aggregate rt_runtime_us allocated for all Kubernetes pods on this node
    def __aggregate_rt_runtime_us(self):
        cpu_list = [d for d in self.base_dir.glob('pod*/*/cpu.rt_runtime_us') if d.is_file()]
        rt_runtime_us = 0
        for file in cpu_list:
            with open(file,'r') as f:
                str = f.read()
                try:
                    runtime_us = int(str)
                    rt_runtime_us += runtime_us
                except:
                    pass
        return rt_runtime_us

    def __current_rt_runtime_us(self, container_id):
        cont_dirs = [ d for d in self.base_dir.glob('pod*/'+container_id) if d.is_dir()]
        if len(cont_dirs) == 1:
            cont_file = cont_dirs[0].joinpath('cpu.rt_runtime_us')
            with open(cont_file,'r') as f:
                str = f.read()
                try:
                    rt_runtime_us = int(str)
                    return rt_runtime_us
                except:
                    return 0
        return 0 

             

    def __write_cpu_rt_runtime_us(self,path,rt_runtime_us):
        try:
            file = path.joinpath('cpu.rt_runtime_us')
            with open(file,'w') as f:
                f.write(str(rt_runtime_us))
                return True
        except IOError as e:
            self.log.error("Exception writing to %s: %s" % (file, e))
            return False
        except Exception as e:
            self.log.error("Exception writing to %s: %s" % (file, e))
            return False
