from walker.commands.command import Command
from walker.repl_state import ReplState
from walker.k8s_utils import is_pod_name, list_sts_names, pod_names, pod_names_by_host_id
from walker.utils import log2

class DevicePostgres(Command):
    COMMAND = 'p:'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(DevicePostgres, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return DevicePostgres.COMMAND

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state.device = 'p'

        return state

    def completion(self, state: ReplState):
        return super().completion(state)

    def help(self, _: ReplState):
        return f'{DevicePostgres.COMMAND}\t move to Postgres Operations device'