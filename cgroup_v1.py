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
        if self.write_cpu_rt_runtime_us(self.base_dir, cap):
            self.log.info(f"Wrote {cap} to kubepods.cpu.rt_runtime_us")

    def type(self):
        return "cgroup_v1"

    # Return the current allocation of realtime for Kubernetes pods
    def current_rt_runtime_us(self):
        #dir_list = [d for d in self.base_dir.glob('pod*/*') if d.is_dir()]
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

    def set_rt_runtime_us(self, container_id, rt_runtime_us):
        # Using Path.glob() find the pod subdirectory containing the specific container_id 
        # directory. Expect exactly 1 directory to match this
        cont_dirs = [ d for d in self.base_dir.glob('pod*/'+container_id) if d.is_dir()]
        if len(cont_dirs) == 1:
            # Get the container directory and the pod directory
            cont_dir = cont_dirs[0]
            pod_dir = cont_dir.parent

            if self.write_cpu_rt_runtime_us(pod_dir,rt_runtime_us) and self.write_cpu_rt_runtime_us(cont_dir, rt_runtime_us):
                self.log.info(f"Wrote {rt_runtime_us} for {container_id}")
                return True
        
        self.log.error(f"Unable to find container cgroup for {container_id}")
        return False

    def write_cpu_rt_runtime_us(self,path,rt_runtime_us):
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



# def main():
#     cg = cgroup_v1(950000)

#     runtime_us_usec = cg.current_rt_runtime_us()

#     print(f"cpu.rt_runtime_us = {runtime_us_usec}\n")

# if __name__ == "__main__":
#     main()