import time
from walker.commands.command import Command
from walker.repl_state import ReplState, RequiredState
from walker.utils import log2
from walker.k8s_utils import create_pod, get_pod, pod_exec, delete_pod
from walker.config import Config

class RepairScan(Command):
    COMMAND = 'repair scan'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(RepairScan, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return RepairScan.COMMAND

    def required(self):
        return RequiredState.CLUSTER

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)
        if not self.validate_state(state):
            return state

        n = "7"
        if len(args) == 1:
            n = str(args[0])
        image = Config().get('repair.image', 'ci-registry.c3iot.io/cloudops/cassrepair:2.0.11')
        secret = Config().get('repair.secret', 'ciregistryc3iotio')
        log_path = secret = Config().get('repair.log-path', '/home/cassrepair/logs/')
        ns = state.namespace
        pvc_name ='cassrepair-log-' + state.sts
        pod_name = 'repair-scan'

        try:
            create_pod(ns, pod_name, image, secret, {}, 'cassrepair-log', pvc_name, '/home/cassrepair/logs/', [ "sh", "-c", "tail -f /dev/null" ])
        except Exception as e:
            if e.status == 409:
                log2(f"Pod {pod_name} already exists")
            else:
                log2("Exception when calling BatchV1Apii->create_namespaced_job: %s\n" % e)

        msged = False
        while get_pod(ns, pod_name).status.phase != 'Running':
            if not msged:
                log2("Waiting for the scanner pod to start up...")
                msged = True
            time.sleep(5)

        try:
            pod_exec(pod_name, pod_name, ns, f"find {log_path} -type f -mtime -{n} -print0 | xargs -0 grep failed")
        finally:
            delete_pod(pod_name, ns)

        return state

    def completion(self, state: ReplState):
        if state.sts:
            return super().completion(state)

        return {}

    def help(self, _: ReplState):
        return f'{RepairScan.COMMAND} [n]: scan last n days repair log, default 7 days'