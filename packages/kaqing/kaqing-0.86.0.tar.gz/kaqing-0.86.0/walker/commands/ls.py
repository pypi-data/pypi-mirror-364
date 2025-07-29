from walker.commands.command import Command
from walker.commands.display_utils import show_pods
from walker.repl_state import ReplState
from walker.k8s_utils import get_app_ids, get_cr_name, in_cluster_namespace, list_pods, list_sts_names
from walker.utils import lines_to_tabular, log, log2

class Ls(Command):
    COMMAND = 'ls'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Ls, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return Ls.COMMAND

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)

        if state.pod:
            pass
        elif state.sts and state.namespace:
            show_pods(list_pods(state.sts, state.namespace), state.namespace, show_namespace=not in_cluster_namespace())
        else:
            self.show_statefulsets()

        return state

    def show_statefulsets(self):
        ss = list_sts_names(show_namespace=not in_cluster_namespace())
        if len(ss) == 0:
            log2('No cassandra statefulsets found.')
            return

        app_ids = get_app_ids()
        list = []
        for s in ss:
            cr_name = get_cr_name(s)
            app_id = 'Unknown'
            if cr_name in app_ids:
                app_id = app_ids[cr_name]
            list.append(f"{s} {app_id}")

        header = 'STATEFULSET_NAME@NAMESPACE APP_ID'
        if in_cluster_namespace():
            header = 'STATEFULSET_NAME APP_ID'
        log(lines_to_tabular(list, header))

    def completion(self, state: ReplState):
        if state.pod:
            return {}

        if not state.sts:
            return {Ls.COMMAND: {n: None for n in list_sts_names()}}

        return {Ls.COMMAND: None}

    def help(self, _: ReplState):
        return f'{Ls.COMMAND}: list clusters|nodes'