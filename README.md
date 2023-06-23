# rt-operator

Experimental Kubernetes operator supporting containers with real-time threads on a cgroups v1 host like RHEL 7/CentOS 7. This operator runs a service on the host with a path to credentials for the cluster.
As pod(s) are deployed with the following annotations present, the pod's containers' cgroup will be modified to have necessary capabilities to run real-time threads.

```yaml
annotations:
  realtime: "true"
  rt_runtime_us: "25000"
```
Where
- realtime: set to either "true" or "false"
- rt_runtime_us: set to this container's `rt_runtime_us` value in microseconds

See `example/threadtest.yaml` for full pod deployment yaml showing the annotations. See [CJLove/thread-playground](https://github.com/CJLove/thread-playground) for the source for building a container with real-time threads.

Container runtimes supported:
- containerd
- docker
- cri-o

## Dependencies
- Python3
- Modules: kubernetes and its dependencies (see requirements.txt)

## Building wheel
```bash
$ python3 setup.py bdist_wheel
```

## Installing wheel
```bash
# pip3 install rt_operator-0.1.0-py3-none-any.wh
```

## Running under systemd
### Installing and enabling
- Adjust paths in `rt-operator.service` as necessary
- Adjust `After` setting in `rt-operator.service` to after the `Kubelet.service` for Kubernetes or `k3s.service` for K3S

```bash
$ sudo cp /usr/local/service/rt-operator.service /etc/systemd/system/
$ sudo systemctl enable rt-operator
$ sudo systemctl start rt-operator
```

## Configuration
Settings in `/usr/local/etc/rt-operator.yaml` config file:
```yaml
---
### rt-operator configuration settings

# Log level: WARN | INFO | DEBUG 
log_level: "DEBUG"

# Full path to kubernetes credentials file (override ~/.kube/config)
kube_path: /path/to/.kube/config

# Override system hostname used for comparisons with pod's node allocation
node_name: myhostname

# Override cgroup handler: noop | cgroup_v1 | cgroup_v2
# cgroup_handler: noop

# Override cgroup v1 handler settings:
# cpu.rt_runtime_capacity for all real-time pods on this node
cgroup_v1_capacity: 950000
```

### Monitoring & Logs
```bash
$ systemctl status rt-operator
$ journalctl -u rt-operator -f
```
