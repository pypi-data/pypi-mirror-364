import base64
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import re
import sys
import time
from typing import List, TypeVar, cast
from kubernetes import client, config as kconfig
from kubernetes.stream import stream
from kubernetes.stream.ws_client import ERROR_CHANNEL

from walker.config import Config
from walker.pod_exec_result import PodExecResult
from walker.utils import elapsed_time, lines_to_tabular, log2

T = TypeVar('T')
_TEST_POD_EXEC_OUTS: PodExecResult = None

class KubeContext:
    in_cluster = False

def set_test_pod_exec_outs(outs: PodExecResult):
    global _TEST_POD_EXEC_OUTS
    _TEST_POD_EXEC_OUTS = outs

    return _TEST_POD_EXEC_OUTS

def list_pods(sts_name: str, namespace: str) -> List[client.V1Pod]:
    v1 = client.CoreV1Api()

    # this filters out with labels first -> saves about 1 second
    # cassandra.datastax.com/cluster: cs-9834d85c68
    # cassandra.datastax.com/datacenter: cs-9834d85c68
    # cassandra.datastax.com/rack: default
    # cs-9834d85c68-cs-9834d85c68-default-sts-0
    # cs-d0767a536f-cs-d0767a536f-reaper-946969766-rws92
    groups = re.match(r'(.*?-.*?)-(.*?-.*?)-(.*?)-.*', sts_name)
    label_selector = f'cassandra.datastax.com/cluster={groups[1]},cassandra.datastax.com/datacenter={groups[2]},cassandra.datastax.com/rack={groups[3]}'

    pods = cast(List[client.V1Pod], v1.list_namespaced_pod(namespace, label_selector=label_selector).items)
    statefulset_pods = []

    for pod in pods:
        if pod.metadata.owner_references:
            for owner in pod.metadata.owner_references:
                if owner.kind == "StatefulSet" and owner.name == sts_name:
                    statefulset_pods.append(pod)
                    break

    return statefulset_pods

def delete_pod(pod_name: str, namespace: str):
    try:
        v1 = client.CoreV1Api()
        api_response = v1.delete_namespaced_pod(pod_name, namespace)
    except Exception as e:
        log2("Exception when calling CoreV1Api->delete_namespaced_pod: %s\n" % e)

def in_cluster_namespace():
    if 'NAMESPACE' in os.environ:
        return os.environ['NAMESPACE']

    return None

def list_sts(label_selector="app.kubernetes.io/name=cassandra") -> List[client.V1StatefulSet]:
    apps_v1_api = client.AppsV1Api()
    if ns := in_cluster_namespace():
        statefulsets = apps_v1_api.list_namespaced_stateful_set(ns, label_selector=label_selector)
    else:
        statefulsets = apps_v1_api.list_stateful_set_for_all_namespaces(label_selector=label_selector)

    return statefulsets.items

def list_sts_name_and_ns():
    return [(statefulset.metadata.name, statefulset.metadata.namespace) for statefulset in list_sts()]

def list_sts_names(show_namespace = True):
    if show_namespace:
        return [f"{sts}@{ns}" for sts, ns in list_sts_name_and_ns()]
    else:
        return [f"{sts}" for sts, _ in list_sts_name_and_ns()]

def get_host_id(pod_name, ns):
    try:
        user, pw = get_user_pass(pod_name, ns)
        command = f'echo "SELECT host_id FROM system.local; exit" | cqlsh --no-color -u {user} -p {pw}'
        result = cassandra_pod_exec(pod_name, ns, command, show_out=False)
        next = False
        for line in result.stdout.splitlines():
            if next:
                return line.strip(' ')
            if line.startswith('----------'):
                next = True
                continue
    except Exception as e:
        return str(e)

    return 'Unknown'

def get_user_pass(ss_name: str, namespace: str, secret_path: str = 'cql.secret'):
    # cs-d0767a536f-cs-d0767a536f-default-sts ->
    # cs-d0767a536f-superuser
    # cs-d0767a536f-reaper-ui
    user = 'superuser'
    if secret_path == 'reaper.secret':
        user = 'reaper-ui'
    groups = re.match(Config().get(f'{secret_path}.cluster-regex', r'(.*?-.*?)-.*'), ss_name)
    secret_name = Config().get(f'{secret_path}.name', '{cluster}-' + user).replace('{cluster}', groups[1], 1)
    v1 = client.CoreV1Api()
    try:
        secret = v1.read_namespaced_secret(secret_name, namespace)
        for key, value in secret.data.items():
            #  username password
            decoded_value = base64.b64decode(value).decode("utf-8")
            if key == Config().get(f'{secret_path}.password-item', 'password'):
                return (secret_name, decoded_value)
    except client.ApiException as e:
        log2(f"Error reading secret: {e}")
        raise e

def cassandra_nodes_exec(statefulset: str, namespace: str, command: str, action: str = 'action', max_workers=0, show_out=True) -> list[PodExecResult]:
    pods = pod_names(statefulset, namespace)
    if not max_workers:
        max_workers = Config().action_workers(action, 0)
    if max_workers > 0:
        # if parallel, node sampling is suppressed
        if show_out:
            log2(f'Executing on all nodes from statefulset in parallel...')
        start_time = time.time()
        try:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # disable stdout from the pod_exec, then show the output in a for loop
                futures = [executor.submit(cassandra_pod_exec, pod, namespace, command, False, False,) for pod in pods]
                if len(futures) == 0:
                    return cast(list[T], [])

            rs = [future.result() for future in as_completed(futures)]
            if show_out:
                for result in rs:
                    print(result.command)
                    if result.stdout:
                        print(result.stdout)
                    if result.stderr:
                        log2(result.stderr, file=sys.stderr)

            return rs
        finally:
            log2(f"Parallel {action} elapsed time: {elapsed_time(start_time)} with {max_workers} workers")
    else:
        results: list[PodExecResult] = []

        samples = Config().action_node_samples(action, sys.maxsize)
        l = min(len(pods), samples)
        adj = 'all'
        if l < len(pods):
            adj = f'{l} sample'
        if show_out:
            log2(f'Executing on {adj} nodes from statefulset...')
        for pod_name in pods:
            try:
                result = cassandra_pod_exec(pod_name, namespace, command, show_out=show_out, throw_err=True)
                results.append(result)
                if result.exit_code() == 0:
                    l -= 1
                    if not l:
                        break
            except Exception as e:
                log2(e)

        return results

def cassandra_pod_exec(pod_name: str, namespace: str, command: str, show_out = True, throw_err = False):
    return pod_exec(pod_name, "cassandra", namespace, command, show_out, throw_err)

def pod_exec(pod_name: str, container: str, namespace: str, command: str, show_out = True, throw_err = False, interaction: Callable[[any, list[str]], any] = None):
    if _TEST_POD_EXEC_OUTS:
        return _TEST_POD_EXEC_OUTS

    api = client.CoreV1Api()

    exec_command = ["/bin/sh", "-c", command]
    k_command = f'kubectl exec -it {pod_name} -c {container} -n {namespace} -- {command}'
    if show_out:
        print(k_command)

    resp = stream(
        api.connect_get_namespaced_pod_exec,
        pod_name,
        namespace,
        command=exec_command,
        container=container,
        stderr=True,
        stdin=True,
        stdout=True,
        tty=True,
        _preload_content=False,
    )

    stdout = []
    stderr = []
    error_output = None
    try:
        while resp.is_open():
            resp.update(timeout=1)
            if resp.peek_stdout():
                frag = resp.read_stdout()
                stdout.append(frag)
                if show_out: print(frag, end="")

                if interaction:
                    interaction(resp, stdout)
            if resp.peek_stderr():
                frag = resp.read_stderr()
                stderr.append(frag)
                if show_out: print(frag, end="")

        try:
            # get the exit code from server
            error_output = resp.read_channel(ERROR_CHANNEL)
        except Exception:
            pass
    except Exception as e:
        if throw_err:
            raise e
        else:
            log2(e)
    finally:
        resp.close()

    return PodExecResult("".join(stdout), "".join(stderr), k_command, error_output)

def pod_names(ss: str, ns: str):
    pods = list_pods(ss, ns)

    return [pod.metadata.name for pod in pods]

def pod_names_by_host_id(ss: str, ns: str):
    pods = list_pods(ss, ns)
    return {get_host_id(pod.metadata.name, ns): pod.metadata.name for pod in pods}

def get_app_ids():
    app_ids_by_ss: dict[str, str] = {}

    group = Config().get('app.cr.group', 'ops.c3.ai')
    v = Config().get('app.cr.v', 'v2')
    plural = Config().get('app.cr.plural', 'c3cassandras')
    label = Config().get('app.label', 'c3__app_id-0')
    strip = Config().get('app.strip', '0')

    v1 = client.CustomObjectsApi()
    try:
        c3cassandras = v1.list_cluster_custom_object(group=group, version=v, plural=plural)
        for c in c3cassandras.items():
            if c[0] == 'items':
                for item in c[1]:
                    app_ids_by_ss[f"{item['metadata']['name']}@{item['metadata']['namespace']}"] = item['metadata']['labels'][label].strip(strip)
    except Exception:
        pass

    return app_ids_by_ss

def get_cr_name(cluster: str, namespace: str = None):
    nn = cluster.split('@')
    # cs-9834d85c68-cs-9834d85c68-default-sts
    if not namespace and len(nn) > 1:
        namespace = nn[1]
    if not namespace:
        namespace = in_cluster_namespace()
    groups = re.match(Config().get('app.cr.cluster-regex', r"(.*?-.*?)-.*"), nn[0])

    return f"{groups[1]}@{namespace}"

def init_config(config: str = None):
    # try with kubeconfig file first
    # then, try in-cluster access
    loaded = False
    msg = None
    if not config:
        config = os.getenv('KUBECONFIG')

    if config:
        try:
            kconfig.load_kube_config(config_file=config)
            loaded = True
        except:
            msg = f'Kubernetes config file: {config} does not exist or is not valid.'
    else:
        msg = 'Use --config or set KUBECONFIG env variable to path to your config file.'

    if not loaded:
        try:
            kconfig.load_incluster_config()
            loaded = True
            KubeContext.in_cluster = True
            msg = "Kubernetes access initialized with in-cluster access."
        except kconfig.ConfigException:
            pass

    if msg:
        log2(msg)
    if not loaded:
        exit(1)

def init_params(params_file: str, param_ovrs: list[str]):
    Config(params_file)

    def err():
        log2('Use -v <key>=<value> format.')
        log2()
        lines = [f'{key}\t{Config().get(key, None)}' for key in Config().keys()]
        log2(lines_to_tabular(lines, separator='\t'))

    for p in param_ovrs:
        tokens = p.split('=')
        if len(tokens) == 2:
            if m := Config().set(tokens[0], tokens[1]):
                log2(f'set {tokens[0]} {tokens[1]}')
                log2(m)
            else:
                err()
                return None
        else:
            err()
            return None

    return Config().params

def is_pod_name(name: str):
    namespace = None
    # cs-d0767a536f-cs-d0767a536f-default-sts-0
    nn = name.split('@')
    if len(nn) > 1:
        namespace = nn[1]
    groups = re.match(r"^cs-.*-sts-\d+$", nn[0])
    if groups:
        return (nn[0], namespace)

    return (None, None)

def is_sts_name(name: str):
    namespace = None
    # cs-d0767a536f-cs-d0767a536f-default-sts
    nn = name.split('@')
    if len(nn) > 1:
        namespace = nn[1]
    groups = re.match(r"^cs-.*-sts$", nn[0])
    if groups:
        return (nn[0], namespace)

    return (None, None)

def get_metrics(namespace: str, pod_name: str, container_name: str = None) -> dict[str, any]:
    # 'containers': [
    #     {
    #     'name': 'cassandra',
    #     'usage': {
    #         'cpu': '31325875n',
    #         'memory': '17095800Ki'
    #     }
    #     },
    #     {
    #     'name': 'medusa',
    #     'usage': {
    #         'cpu': '17947213n',
    #         'memory': '236456Ki'
    #     }
    #     },
    #     {
    #     'name': 'server-system-logger',
    #     'usage': {
    #         'cpu': '49282n',
    #         'memory': '1608Ki'
    #     }
    #     }
    # ]
    for pod in list_metrics_crs(namespace)['items']:
        p_name = pod["metadata"]["name"]
        if p_name == pod_name:
            if not container_name:
                return pod

            for container in pod["containers"]:
                if container["name"] == container_name:
                    return container

    return None

def list_metrics_crs(namespace: str, plural = "pods") -> dict[str, any]:
    group = "metrics.k8s.io"
    version = "v1beta1"

    api = client.CustomObjectsApi()

    return api.list_namespaced_custom_object(group=group, version=version, namespace=namespace, plural=plural)

def get_container(namespace: str, pod_name: str, container_name: str):
    pod = get_pod(namespace, pod_name)
    if not pod:
        return None

    for container in pod.spec.containers:
        if container_name == container.name:
            return container

    return None


def get_pod(namespace: str, pod_name: str):
    v1 = client.CoreV1Api()
    return v1.read_namespaced_pod(name=pod_name, namespace=namespace)


def create_pvc(name: str, storage: int, namespace: str):
    v1 = client.CoreV1Api()
    pvc = client.V1PersistentVolumeClaim(
        metadata=client.V1ObjectMeta(name=name),
        spec=client.V1PersistentVolumeClaimSpec(
            access_modes=["ReadWriteOnce"],
            resources=client.V1ResourceRequirements(
                requests={"storage": str(storage)+"Gi"}
            ))
    )
    try:
        v1.create_namespaced_persistent_volume_claim(namespace=namespace, body=pvc)
    except Exception as e:
        if e.status == 409:
            log2("PVC already exists, continue...")
        else:
            raise
    return

def create_pod_spec(name: str, image: str, image_pull_secret: str, envs: list, volume_name: str, pvc_name:str, mount_path:str, command: list[str]=None):
    container = client.V1Container(name=name, image=image, env=envs, command=command, 
                                   volume_mounts=[client.V1VolumeMount(mount_path=mount_path, name=volume_name)])
    pod_spec = client.V1PodSpec(
        restart_policy="Never", 
        containers=[container],
        image_pull_secrets=[client.V1LocalObjectReference(name=image_pull_secret)],
        security_context=client.V1PodSecurityContext(run_as_user=1001, run_as_group=1001, fs_group=1001),
        volumes=[client.V1Volume(name=volume_name, persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(claim_name=pvc_name))]
        )
    return pod_spec
    
def create_pod(namespace: str, pod_name: str, image: str, secret: str, env: dict[str, any], volume_name: str, pvc_name:str, mount_path:str, command: list[str]=None):
    v1 = client.CoreV1Api()
    envs = []
    for k, v in env.items():
        envs.append(client.V1EnvVar(name=str(k), value=str(v)))
    pod = create_pod_spec(pod_name, image, secret, envs, volume_name, pvc_name, mount_path, command)
    return v1.create_namespaced_pod(namespace=namespace, 
                                    body=client.V1Pod(spec=pod, metadata=client.V1ObjectMeta(name=pod_name)))

def create_job(job_name: str, namespace: str, image: str, image_pull_secret: str, env: dict[str, any], env_from: dict[str, any], 
               volume_name: str, pvc_name: str, mount_path: str, command: list[str]=None):
    envs = []
    for k, v in env.items():
        envs.append(client.V1EnvVar(name=k.upper(), value=str(v)))
    for k, v in env_from.items():
        envs.append(client.V1EnvVar(name=k.upper(), value_from=client.V1EnvVarSource(secret_key_ref=client.V1SecretKeySelector(key=k, name=v))))
    template = create_pod_spec(job_name, image, image_pull_secret, envs, volume_name, pvc_name, mount_path, command)
    spec = client.V1JobSpec(template=client.V1PodTemplateSpec(spec=template), backoff_limit=1, ttl_seconds_after_finished=300)
    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=job_name),
        spec=spec)
    
    try:
        client.BatchV1Api().create_namespaced_job(body=job, namespace=namespace)
        log2(f"Job {job_name} created in {namespace}")
    except Exception as e:
        log2("Exception when calling BatchV1Apii->create_namespaced_job: %s\n" % e)
    return

def delete_job(job_name: str, namespace: str):
    try:
        client.BatchV1Api().delete_namespaced_job(name=job_name, namespace=namespace)
        log2(f"Job {job_name} in {namespace} deleted.")
    except Exception as e:
        log2("Exception when calling BatchV1Apii->delete_namespaced_job: %s\n" % e)
    return

def get_job_logs(job_name: str, namespace: str):
    v1 = client.CoreV1Api()
    try:
        pod_name = v1.list_namespaced_pod(namespace=namespace, label_selector=f'job-name={job_name}').items[0].metadata.name
    except Exception as e:
        log2("Exception when calling CorV1Apii->list_namespaced_pod, cannot find job pod: %s\n" % e)
    
    log2(v1.read_namespaced_pod_log(name=pod_name, namespace=namespace))