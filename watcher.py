import logging

from kubernetes import (
    client,
    config,
    watch
)

class watcher:
    def __init__(self, node_name, cgroup_handler):
        self.node_name = node_name
        self.cgroup_handler = cgroup_handler
        self.log = logging.getLogger('RtOperator')

    def watch_pods(self):
        v1 = client.CoreV1Api()

        while True:
            try:

                w = watch.Watch()
                for event in w.stream(v1.list_pod_for_all_namespaces):

                    # print(event['raw_object'])
                    raw = event['raw_object']
                    type = event['type']
                    name=''
                    container_id=''
                    rt_runtime_us = 0
                    # try to extract necessary fields from raw_object and filter based
                    # on extracted fields
                    try:
                        name = raw['metadata']['name']
                        qos = raw['status']['qosClass']
                        statuses = raw['status']['containerStatuses']
                        node = raw['spec']['nodeName'].split('.')[0]

                    except:
                        self.log.error("Unable to extract fields from event data")
                        continue

                    else:                    
                        # Filter on pods in Guaranteed QoS class
                        if (qos != 'Guaranteed'):
                            continue

                        # Filter on pods with 'realtime' annotation and 'rt_runtime_us' value
                        if 'annotations' not in raw['metadata']:
                            continue
                        annotations = raw['metadata']['annotations']

                        is_rt = False
                        if 'realtime' not in annotations:
                            continue
                        is_rt = annotations['realtime'] == "true"
                        if (not is_rt):
                            continue
                        if 'rt_runtime_us' not in annotations:
                            continue
                        rt_runtime_str = annotations['rt_runtime_us']
                        try:
                            # Convert 'rt_runtime_us' annotation to integer
                            rt_runtime_us = int(rt_runtime_str)
                        except:
                            # Log error and continue if rt_runtime_us annotation is invalid
                            self.log.error(f"Pod {name} invalid rt_runtime_us annotation: {rt_runtime_str}")
                            continue
                        # See if container_id is populated
                        if len(statuses) > 0:
                            status = statuses[0]
                            str = status['containerID']
                            container_id = str.lstrip('containerd://')
                
                        # Filter if container_id isn't populated
                        if container_id == "":
                            continue

                        # Filter if pod isn't scheduled on this node
                        if self.node_name != node:
                            continue

                        self.log.debug(f"Event {type} Pod {name} Qos {qos} Node {node} rt_runtime_us {rt_runtime_us} container_id {container_id}")           
                        self.cgroup_handler.set_rt_runtime_us(container_id, rt_runtime_us)

            except KeyboardInterrupt:
                # Handle service exit
                break
            except Exception as e:
                self.log.error("Caught exception %s" % e)
                pass   