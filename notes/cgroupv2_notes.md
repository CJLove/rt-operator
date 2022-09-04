# Notes regarding cgroupv2 directory layout

## Kubernetes 1.25.0 w/cri-o runtime

- Base directory is `/sys/fs/cgroup/kubepods.slice`
- Guaranteed QoS pod directory is `/sys/fs/cgroup/kubepods.slice/kubepods-podXXX.slice`
- Container directory is `/sys/fs/cgroup/kubepods.slice/kubepods-podXXX.slice/crio-YYYYYY.scope`

