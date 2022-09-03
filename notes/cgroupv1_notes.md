# Notes regarding cgroupv1 directory layout

## K3S (containerd runtime)
- Base directory is `/sys/fs/cgroup/cpu,cpu_acct/kubepods`
- Guaranteed QoS pod directory is `/sys/fs/cgroup/cpu,cpu_acct/kubepods/podXXXXX/`
- Container directory is `/sys/fs/cgroup/cpu,cpu_acct/kubepods/podXXXXX/YYYYYYYYY/`

## Kubernetes 1.23.5 w/Docker runtime
- Base directory is `/sys/fs/cgroup/cpu,cpu_acct/kubepods.slice`
- Guaranteed QoS pod directory is `/sys/fs/cgroup/cpu,cpu_acct/kubepods.slice/kubepods-podXXXXX.slice/`
- Container directory is `/sys/fs/cgroup/cpu,cpu_acct/kubepods.slice/kubepods-podXXX.slice/docker-YYYYYY.scope/`

## Kubernetes 1.25.0 w/cri-o runtime
- Base directory is `/sys/fs/cgroup/cpu,cpuacct/kubepods.slice`
- Guaranteed QoS pod directory is `/sys/fs/cgroup/cpu,cpuacct/kubepods.slice/kubepods-podXXX.slice`
- Container directory is `/sys/fs/cgroup/cpu,cpuacct/kubepods.slice/kubepods-podXXX.slice/crio-YYYYYY.scope`
