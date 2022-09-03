#!/usr/bin/env python3

import logging
import os
from pathlib import Path
import sys
import ast
import logs
import socket
import cgroup_noop
import cgroup_v1
import cgroup_v2
import docker
import containerd
import crio
import watcher
import yaml

from kubernetes import (
    config,
    client
)

logs.configure()
log = logging.getLogger('RtOperator')

def main():
    config_file = 'rt-operator.yaml'
    if len(sys.argv) == 2:
        config_file = sys.argv[1]

    # Default user path for finding kubernetes credentials
    user_kubeconfig = Path(os.path.expanduser("~")).joinpath('.kube', 'config')

    # Default cgroup v1 capacity to be managed by the rt-operator on this node
    cgroup_v1_capacity = 950000

    # Default cgroup handler
    cgroup_handler = None

    # Default: use system hostname
    node_name = get_node_name()

    try:
        with open(config_file) as file:
            log.info(f"Using {config_file}")
            config = yaml.safe_load(file)

            if 'log_level' in config:
                try:
                    log.setLevel(config['log_level'])
                except:
                    pass

            if 'kube_path' in config:
                kube_path = config['kube_path']
                user_kubeconfig = Path(kube_path)

            if 'cgroup_v1_capacity' in config:
                try:
                    cgroup_v1_capacity = int(config['cgroup_v1_capacity'])
                except:
                    pass

            if 'node_name' in config:
                node_name = config['node_name']

            if 'cgroup_handler' in config:
                cgroup_handler = config['cgroup_handler']

    except:
        log.error(f"Error parsing {config_file}")

    load_kube_credentials(user_kubeconfig)

    runtime = get_container_runtime(node_name)
    if runtime == None:
        log.error("Couldn't determine container runtime")

    # Create the cgroup_handler based on detecting it or by what was
    # specified in the config file
    if cgroup_handler == None:
        if os.path.isdir('/sys/fs/cgroup/cpu,cpuacct'):
            # System is running cgroups v1
            cgroup_handler = cgroup_v1.cgroup_v1(runtime, cgroup_v1_capacity)
        elif os.path.isdir('/sys/fs/cgroup/system.slice'):
            # Future: support cgroups v2       
            cgroup_handler = cgroup_v2.cgroup_v2(runtime)
        else:
            cgroup_handler = cgroup_noop.cgroup_noop()
    elif cgroup_handler == "noop":
        cgroup_handler = cgroup_noop.cgroup_noop(runtime)
    elif cgroup_handler == "cgroup_v1":
        cgroup_handler = cgroup_v1.cgroup_v1(runtime, cgroup_v1_capacity)
    elif cgroup_handler == "cgroup_v2":
        cgroup_handler = cgroup_v2.cgroup_v2(runtime)    

    log.info("Using %s runtime" % runtime.type())
    log.info("Using %s cgroup handler" % cgroup_handler.type())
    log.info("Using node name %s" % node_name)

    watch = watcher.watcher(node_name,cgroup_handler)
    watch.watch_pods()

def get_node_name():
    node = socket.gethostname().split('.')[0]
    return node

def get_container_runtime(node_name):
    runtime = None
    v1 = client.CoreV1Api()
    nodes = v1.list_node()
    node = nodes.items[0]
    runtime_version = node.status.node_info.container_runtime_version
    if runtime_version.startswith('docker'):
        runtime = docker.docker()
    elif runtime_version.startswith('containerd'):
        runtime = containerd.containerd()
    elif runtime_version.startswith('cri-o'):
        runtime = crio.crio()
    return runtime


def load_kube_credentials(user_kubeconfig):

    log.debug("Looking for credentials...")
    dev_kubeconfig = Path(__file__).joinpath('..', '..', '..',
                                             '.tmp', 'serviceaccount',
                                             'dev_kubeconfig.yml').resolve()

    if dev_kubeconfig.exists():
        log.info("Loading from dev kube config")
        config.load_kube_config(config_file=str(dev_kubeconfig))
    elif user_kubeconfig.exists():
        log.info("Loading user kube config")
        config.load_kube_config(config_file=str(user_kubeconfig))
    else:
        log.info("Loading in-cluster kube config")
        try:
            config.load_incluster_config()
        except config.ConfigException:
            log.error("Unable to load in-cluster config file. Exiting.")
            sys.exit(1)



if __name__ == "__main__":
    main()