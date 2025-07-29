import re

from walker.commands.reaper_session import ReaperSession
from walker.config import Config
from walker.k8s_utils import in_cluster_namespace, list_pods
from walker.repl_state import ReplState

class KubectlAssist:
    def values(state: ReplState, collapse = False):
        # node-exec-?, nodetool-?, cql-?, reaper-exec, reaper-forward, reaper-ui, reaper-usernae, reaper-password
        d = {}

        if state.sts:
            pod_names: list[str] = [pod.metadata.name for pod in list_pods(state.sts, state.namespace)]
        else:
            pod_names = [state.pod]

        if collapse:
            pod_names = pod_names[:1]
            pod_names[0] = pod_names[0].replace('-0', '-?')

        if in_cluster_namespace():
            d |= {
                f'node-exec-{"?" if collapse else i}': f'kubectl exec -it {pod} -c cassandra -- bash' for i, pod in enumerate(pod_names)
            }
        else:
            d |= {
                f'node-exec-{"?" if collapse else i}': f'kubectl exec -it {pod} -c cassandra -n {state.namespace} -- bash' for i, pod in enumerate(pod_names)
            }

        ncd = {}
        nuser, npw = state.user_pass()
        cuser, cpw = state.user_pass(secret_path='cql.secret')
        if in_cluster_namespace():
            # ping cs-a526330d23-cs-a526330d23-default-sts-0.cs-a526330d23-cs-a526330d23-all-pods-service.stgawsscpsr.svc.cluster.local
            groups = re.match(r'(.*?-.*?-.*?-.*?-).*', state.pod if state.pod else state.sts)
            if groups:
                svc = Config().get('cassandra.service-name', 'all-pods-service')
                ncd |= {
                    f'nodetool-{"?" if collapse else i}': f'nodetool -h {pod}.{groups[1]}{svc} -u {nuser} -pw {npw}' for i, pod in enumerate(pod_names)
                }

                ncd |= {
                    f'cql-{"?" if collapse else i}': f'cqlsh -u {cuser} -p {cpw} {pod}.{groups[1]}{svc}' for i, pod in enumerate(pod_names)
                }

        if not ncd:
            ncd |= {
                f'nodetool-{"?" if collapse else i}': f'kubectl exec -it {pod} -c cassandra -n {state.namespace} -- nodetool -u {nuser} -pw {npw}' for i, pod in enumerate(pod_names)
            }

            user, pw = state.user_pass(secret_path='cql.secret')
            ncd |= {
                f'cql-{"?" if collapse else i}': f'kubectl exec -it {pod} -c cassandra -n {state.namespace} -- cqlsh -u {cuser} -p {cpw}' for i, pod in enumerate(pod_names)
            }

        d |= ncd

        if r := ReaperSession.create(state):
            reaper = r.reaper_spec(state)
            d |= {
                'reaper-exec': reaper["exec"],
                'reaper-forward': reaper["forward"],
                'reaper-ui': reaper["web-uri"],
                'reaper-username': reaper["username"],
                'reaper-password': reaper["password"]
            }

        return d