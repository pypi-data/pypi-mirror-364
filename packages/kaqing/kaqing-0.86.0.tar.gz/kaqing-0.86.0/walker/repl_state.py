import copy
from enum import Enum

from walker.k8s_utils import cassandra_nodes_exec, cassandra_pod_exec, get_user_pass, in_cluster_namespace, is_pod_name, is_sts_name
from walker.utils import display_help, log2, random_alphanumeric

class BashSession:
    def __init__(self):
        self.session_id = random_alphanumeric(6)

    def pwd(self, state: 'ReplState'):
        command = f'cat /tmp/.qing-{self.session_id}'

        if state.pod:
            rs = [cassandra_pod_exec(state.pod, state.namespace, command, show_out=False)]
        elif state.sts:
            rs = cassandra_nodes_exec(state.sts, state.namespace, command, action='bash', show_out=False)

        dir = None
        for r in rs:
            if r.exit_code(): # if fails to read the session file, ignore
                continue

            dir0 = r.stdout.strip(' \r\n')
            if dir:
                if dir != dir0:
                    log2('Inconsitent working dir found across multiple pods.')
                    return None
            else:
                dir = dir0

        return dir

class RequiredState(Enum):
    CLUSTER = 'cluster'
    POD = 'pod'
    CLUSTER_OR_POD = 'cluster_or_pod'

class ReplState:
    def __init__(self, sts: str = None, pod: str = None, namespace: str = None, ns_statefulset: str = None, in_repl = False, bash_session: BashSession = None, remote_dir = None):
        self.namespace = in_cluster_namespace()

        self.sts = sts
        self.pod = pod
        if namespace:
            self.namespace = namespace
        self.in_repl = in_repl
        self.bash_session = bash_session
        self.remote_dir = remote_dir
        self.wait_log_flag = False

        if ns_statefulset:
            nn = ns_statefulset.split('@')
            self.sts = nn[0]
            if len(nn) > 1:
                self.namespace = nn[1]

    def apply_args(self, args: list[str], cmd: list[str] = None) -> tuple['ReplState', list[str]]:
        state = self

        new_args = []
        for index, arg in enumerate(args):
            if index < 5:
                state = copy.copy(state)

                s, n = is_sts_name(arg)
                if s:
                    if not state.sts:
                        state.sts = s
                    if n and not state.namespace:
                        state.namespace = n

                p, n = is_pod_name(arg)
                if p:
                    if not state.pod:
                        state.pod = p
                    if n and not state.namespace:
                        state.namespace = n

                if not s and not p:
                    new_args.append(arg)
            else:
                new_args.append(arg)

        if cmd:
            new_args = new_args[len(cmd):]

        return (state, new_args)

    def validate(self, required: RequiredState = None):
        if required == RequiredState.CLUSTER:
            if not self.namespace or not self.sts:
                if self.in_repl:
                    log2('cd to a cluster first.')
                else:
                    log2('* cluster is missing.')
                    log2()
                    display_help()

                return False
        elif required == RequiredState.POD:
            if not self.namespace or not self.pod:
                if self.in_repl:
                    log2('cd to a pod first.')
                else:
                    log2('* Pod is missing.')
                    log2()
                    display_help()

                return False
        elif required == RequiredState.CLUSTER_OR_POD:
            if not self.namespace or not self.sts and not self.pod:
                if self.in_repl:
                    log2('cd to a cluster first.')
                else:
                    log2('* cluster or pod is missing.')
                    log2()
                    display_help()

                return False

        return True

    def user_pass(self, secret_path = 'cql.secret'):
        return get_user_pass(self.pod if self.pod else self.sts, self.namespace, secret_path=secret_path)

    def enter_bash(self, bash_session):
        self.bash_session = bash_session

    def exit_bash(self):
        self.bash_session = None

    def wait_log(self, msg: str):
        if not self.wait_log_flag:
            log2(msg)
            self.wait_log_flag = True

    def clear_wait_log_flag(self):
        self.wait_log_flag = False