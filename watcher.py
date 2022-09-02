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
# 4. Other realtime annotations satisfying cgroup handler conditions
class watcher:
    def __init__(self, node_name, cgroup_handler):
        self.node_name = node_name
        self.cgroup_handler = cgroup_handler
        self.log = logging.getLogger('RtOperator')

    def __is_node_match(self,object):
        try:
            name = object['spec']['nodeName'].split('.')[0]
        except Exception as e:
            self.log.debug(f"Exception: {e}")
            return ('',False)
        else:
            return (name, self.node_name == name)

    def __is_rt_pod(self,annotations):
        if 'realtime' not in annotations:
            return False
        return annotations['realtime'] == "true"

    def __is_guaranteed_qos(self, object):
        try:
            qos = object['status']['qosClass']
        except Exception as e:
            self.log.debug(f"Exception: {e}")
            return False
        else:
            return qos == 'Guaranteed'

    def __has_container_id(self, object):
        try:
            statuses = object['status']['containerStatuses']
        except Exception as e:
            self.log.debug(f"Exception:: {e}")
            return ('', False)
        else:
            # See if containerID is populated
            if len(statuses) > 0:
                
                self.log.debug(f"statuses {statuses}")
                status = statuses[0]
                str = status['containerID']
                container_id = str
                # Strip leading 'containerd://' prefix
                if str.startswith('containerd://'):
                    container_id = str[len('containerd://'):]
                # TBD: other container runtimes
                return (container_id, True)
        return ('', False)

    def __get_pod_name(self, object):
        try:
            name = object['metadata']['name']
        except:
            return ''
        else:
            return name

    def watch_pods(self):
        v1 = client.CoreV1Api()

        while True:
            try:

                w = watch.Watch()
                for event in w.stream(v1.list_pod_for_all_namespaces):

                    # print(event['raw_object'])
                    raw = event['raw_object']
                    type = event['type']

                    # Filter based on QoS class
                    if not self.__is_guaranteed_qos(raw):
                        continue

                    # Get the pod's node name and whether it matches this node's name
                    (node, is_node_match) = self.__is_node_match(raw)
                    if not is_node_match:
                        continue

                    # Filter pod without annotations
                    if 'annotations' not in raw['metadata']:
                        continue
                    annotations = raw['metadata']['annotations']

                    # Filter on whether pod as 'realtime' annotation
                    if not self.__is_rt_pod(annotations):
                        continue

                    # Filter on whether pod has container_id populated
                    (container_id, has_container_id) = self.__has_container_id(raw)
                    if not has_container_id:
                        continue

                    # Get the pod name
                    name = self.__get_pod_name(raw)

                    # Filter pod without valid annotation(s) for the cgroup handler
                    if not self.cgroup_handler.has_valid_rt_annotation(name, container_id, annotations):
                        continue


                    # We have a pod which should be made realtime-capable
                    self.log.debug(f"Event {type} Pod {name} Node {node} container_id {container_id}")           
                    self.cgroup_handler.set_rt_pod(name, container_id, annotations)

            except KeyboardInterrupt:
                # Handle service exit
                break
            except Exception as e:
                self.log.error("Caught exception %s but resuming watcher" % e)
                pass   