# rt-operator

Kubernetes operator supporting containers with real-time threads

Runtimes supported:
- containerd
- docker

## Dependencies
- Python3
- Modules: kubernetes and its dependencies
    - cachetools (4.2.4)
    - certifi (2022.6.15)
    - charset-normalizer (2.0.12)
    - google-auth (2.11.0)
    - idna (3.3)
    - kubernetes (24.2.0)
    - oauthlib (3.2.0)
    - pip (9.0.3)
    - pyasn1 (0.4.8)
    - pyasn1-modules (0.2.8)
    - python-dateutil (2.8.2)
    - PyYAML (6.0)
    - requests (2.27.1)
    - requests-oauthlib (1.3.1)
    - rsa (4.9)
    - setuptools (39.2.0)
    - six (1.16.0)
    - urllib3 (1.26.12)
    - websocket-client (1.3.1)

## Configuration
Settings in `rt-operator.yaml` config file:
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

## Running under systemd
### Installing and enabling
- Adjust paths in `rt-operator.service` as necessary
- Adjust `After` setting in `rt-operator.service` to after the `Kubelet.service` for Kubernetes or `k3s.service` for K3S

```bash
$ sudo cp rt-operator.service /etc/systemd/system/
$ sudo systemctl enable rt-operator
$ sudo systemctl start rt-operator
```

### Monitoring & Logs
```bash
$ systemctl status rt-operator
$ journalctl -u rt-operator -f
```
