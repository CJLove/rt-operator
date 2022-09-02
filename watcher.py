import logging

from kubernetes import (
    client,
    watch
)

# The watcher class is responsible for consuming a stream of pod-related
# events, filtering events down to those corresponding to pods meeting
# the following conditions:
# 1. Guaranteed QoS class
# 2. Allocated to this node
# 3. Containing the 'realtime': 'true' annotation
# 4. Containing a valid annotation for the cgroup_handler type
#    cgroup_v1: 'rt_runtime_us': annotation exists within the valid range (0 .. handler.capacity) 
class watcher:
    def __init__(self, node_name, cgroup_handler):
        self.node_name = node_name
        self.cgroup_handler = cgroup_handler
        self.log = logging.getLogger('RtOperator')

    def is_rt_pod(self,annotations):
        if 'realtime' not in annotations:
            return False
        return annotations['realtime'] == "true"

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

                        # Filter if pod isn't scheduled on this node
                        if self.node_name != node:
                            continue

                        # Filter pod without annotations
                        if 'annotations' not in raw['metadata']:
                            continue
                        annotations = raw['metadata']['annotations']

                        # Filter pod without "realtime" annotation
                        if not self.is_rt_pod(annotations):
                            continue
                        
                        # Filter pod without valid annotation(s) for the cgroup handler
                        if not self.cgroup_handler.has_valid_rt_annotation(annotations):
                            continue
                        
                        # See if container_id is populated
                        if len(statuses) > 0:
                            status = statuses[0]
                            str = status['containerID']
                            container_id = str.lstrip('containerd://')
                
                        # Filter if container_id isn't populated
                        if container_id == "":
                            continue

                        self.log.debug(f"Event {type} Pod {name} Qos {qos} Node {node} container_id {container_id}")           
                        self.cgroup_handler.set_rt_pod(container_id, annotations)

            except KeyboardInterrupt:
                # Handle service exit
                break
            except Exception as e:
                self.log.error("Caught exception %s" % e)
                pass   