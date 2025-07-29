from walker.commands.command import Command
from walker.repl_state import ReplState
from walker.k8s_utils import is_pod_name, list_sts_names, pod_names, pod_names_by_host_id
from walker.utils import log2

class Cd(Command):
    COMMAND = 'cd'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Cd, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return Cd.COMMAND

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        if len(args) < 2:
            return state

        arg = args[1]
        for dir in arg.split('/'):
            if dir == '..':
                if state.pod:
                    state.pod = None
                else:
                    state.sts = None
            else:
                if not state.sts:
                    ss_and_ns = dir.split('@')
                    state.sts = ss_and_ns[0]
                    state.namespace = ss_and_ns[1]
                elif not state.pod:
                    p, _ = is_pod_name(dir)
                    if p:
                        state.pod = p
                    else:
                        names = pod_names_by_host_id(state.sts, state.namespace);
                        if dir in names:
                            state.pod = names[dir]
                        else:
                            log2('Not a valid pod name or host id.')

        return state

    def completion(self, state: ReplState):
        if state.pod:
            return {Cd.COMMAND: {'..': None}}
        elif state.sts:
            return {Cd.COMMAND: {'..': None} | {p: None for p in pod_names(state.sts, state.namespace)}}
        else:
            return {Cd.COMMAND: {p: None for p in list_sts_names()}}

        return {}

    def help(self, _: ReplState):
        return f'{Cd.COMMAND} <path> | .. : move around'