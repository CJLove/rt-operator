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
            name = object.spec.node_name.split('.')[0]
        except Exception as e:
            #self.log.debug(f"Exception: {e}")
            return ('',False)
        else:
            return (name, self.node_name == name)

    def __is_rt_pod(self,annotations):
        if 'realtime' not in annotations:
            return False
        return annotations['realtime'] == "true"

    def __is_guaranteed_qos(self, object):
        try:
            qos = object.status.qos_class
        except Exception as e:
            #self.log.debug(f"Exception: {e}")
            return False
        else:
            return qos == 'Guaranteed'

    def __has_container_id(self, object):
        try:
            statuses = object.status.container_statuses
        except Exception as e:
            #self.log.debug(f"Exception: {e}")
            return ('', False)
        else:
            # See if containerID is populated
            if statuses != None:
                if len(statuses) > 0:
                    status = statuses[0]
                    if status.container_id != None:
                        container_id = status.container_id
                        # Strip leading 'containerd://' prefix
                        if container_id.startswith('containerd://'):
                            container_id = container_id[len('containerd://'):]
                        # Strip leading 'docker-' prefix
                        if container_id.startswith('docker://'):
                            container_id = container_id[len('docker://'):]
                        return (container_id, True)
                    return ('', False)
        return ('', False)

    def __get_pod_name(self, object):
        try:
            name = object.metadata.name
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

                    object = event['object']
                    type = event['type']

                    # Filter based on type
                    if type == 'DELETED':
                        continue

                    # Filter based on QoS class
                    if not self.__is_guaranteed_qos(object):
                        continue

                    # Get the pod's node name and whether it matches this node's name
                    (node, is_node_match) = self.__is_node_match(object)
                    if not is_node_match:
                        continue

                    # Filter pod without annotations
                    annotations = object.metadata.annotations
                    if annotations == None:
                        continue

                    # Filter on whether pod as 'realtime' annotation
                    if not self.__is_rt_pod(annotations):
                        continue

                    # Filter on whether pod has container_id populated
                    (container_id, has_container_id) = self.__has_container_id(object)
                    if not has_container_id:
                        continue

                    # Get the pod name
                    name = self.__get_pod_name(object)

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