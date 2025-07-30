from concurrent.futures import ThreadPoolExecutor
import copy

from walker.commands.command import Command
from walker.commands.display_utils import show_pods
from walker.commands.postgres_session import PostgresSession
from walker.repl_state import ReplState
from walker.k8s_utils import cassandra_nodes_exec, cassandra_nodes_run, get_app_ids, get_cr_name, get_host_id, in_cluster_namespace, list_pods, list_sts_names
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

        if len(args) > 0:
            arg = args[0]
            if arg in ['p:', 'c:'] and arg != f'{state.device}:':
                state = copy.copy(state)
                state.device = arg.replace(':', '')

        if state.device == 'p':
            if state.pg_path:
                pg = PostgresSession(state.namespace, state.pg_path)
                if pg.db:
                    self.show_pg_tables(pg)
                else:
                    self.show_pg_databases(pg)
            else:
                self.show_pg_hosts(state)
        else:
            if state.pod:
                pass
            elif state.sts and state.namespace:
                def get_host_id_with_pod(pod, ns):
                    return (get_host_id(pod, ns), pod)

                def body(executor: ThreadPoolExecutor, pod, ns, show_out):
                    if executor:
                        return executor.submit(get_host_id_with_pod, pod, ns)

                    id = get_host_id(pod, ns)

                    return (id, pod)

                host_ids_by_pod = {pod: id for id, pod in cassandra_nodes_run(state.sts, state.namespace, body, action='get-host-id', show_out=False)}
                # cassandra_nodes_exec(state.sts, state.namespace, command, action='nodetool')
                show_pods(list_pods(state.sts, state.namespace), state.namespace, show_namespace=not in_cluster_namespace(), host_ids_by_pod=host_ids_by_pod)
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

    def show_pg_hosts(self, state: ReplState):
        def line(pg: PostgresSession):
            return f'{pg.directory()},{pg.endpoint()}:{pg.port()},{pg.username()},{pg.password()}'

        lines = [line(PostgresSession(state.namespace, pg)) for pg in PostgresSession.hosts(state)]

        log(lines_to_tabular(lines, 'NAME,ENDPOINT,USERNAME,PASSWORD', separator=','))

    def show_pg_databases(self, pg: PostgresSession):
        lines = [db["name"] for db in pg.databases() if db["owner"] == pg.default_owner()]

        log(lines_to_tabular(lines, 'DATABASE', separator=','))

    def show_pg_tables(self, pg: PostgresSession):
        lines = [db["name"] for db in pg.tables() if db["schema"] == pg.default_schema()]

        log(lines_to_tabular(lines, 'NAME', separator=','))

    def completion(self, state: ReplState):
        if state.pod:
            return {}

        if not state.sts:
            return {Ls.COMMAND: {n: None for n in list_sts_names()}}

        return {Ls.COMMAND: None}

    def help(self, _: ReplState):
        return f'{Ls.COMMAND} [device:]\t list clusters|nodes|pg hosts|pg databases'