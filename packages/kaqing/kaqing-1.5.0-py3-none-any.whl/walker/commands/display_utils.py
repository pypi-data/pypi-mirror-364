from kubernetes import client
from typing import List

from walker.k8s_utils import get_host_id
from walker.utils import lines_to_tabular, log, log2

def show_pods(pods: List[client.V1Pod], ns: str, show_namespace = True, show_host_id = True, host_ids_by_pod = {}):
    if len(pods) == 0:
        log2('No pods found.')
        return

    def line(pod: client.V1Pod):
        pod_cnt = len(pod.status.container_statuses)
        ready = 0
        if pod.status.container_statuses:
            for container_status in pod.status.container_statuses:
                if container_status.ready:
                    ready += 1

        status = pod.status.phase
        if pod.metadata.deletion_timestamp:
            status = 'Terminating'

        pod_name = pod.metadata.name
        line = ""
        if show_host_id:
            if pod_name in host_ids_by_pod:
                line = line + f"{host_ids_by_pod[pod_name]} "
            else:
                line = line + f"{get_host_id(pod_name, ns)} "
        line += pod_name
        if show_namespace:
            line += f"@{ns}"
        return line + f" {ready}/{pod_cnt} {status}"

    pod_names = [line(pod) for pod in pods]

    log(lines_to_tabular(pod_names, 'HOST_ID POD_NAME READY POD_STATUS' if show_host_id else 'POD_NAME READY POD_STATUS'))