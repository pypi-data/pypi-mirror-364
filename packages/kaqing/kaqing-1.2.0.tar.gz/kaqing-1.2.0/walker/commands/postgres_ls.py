import copy

from walker.commands.command import Command
from walker.commands.ls import Ls
from walker.commands.postgres_session import PostgresSession
from walker.repl_state import ReplState, RequiredState
from walker.utils import lines_to_tabular, log

class PostgresLs(Command):
    COMMAND = 'pg ls'
    reaper_login = None

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(PostgresLs, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return PostgresLs.COMMAND

    def required(self):
        return RequiredState.NAMESPACE

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)
        if not self.validate_state(state):
            return state

        state.device = 'p'

        Ls().run('ls', state)

        return state

    def list_pg_hosts(self, state: ReplState):
        #  {'connection-string': '',
        #   'postgres-admin-password': '',
        #   'postgres-admin-username': '',
        #   'postgres-db-endpoint': '',
        #   'postgres-db-port': 'NTQzMg=='},
        def line(pg: PostgresSession):
            s1 = copy.copy(state)
            s1.pg = pg.path
            return f'{pg.path},{pg.endpoint(s1)}:{pg.port(s1)},{pg.username(s1)},{pg.password(s1)}'

        lines = [line(PostgresSession(state.namespace, pg)) for pg in PostgresSession.hosts(state)]

        log(lines_to_tabular(lines, 'NAME,ENDPOINT,USERNAME,PASSWORD', separator=','))

    def completion(self, state: ReplState):
        if state.sts:
            return super().completion(state)

        return {}

    def help(self, _: ReplState):
        return f'{PostgresLs.COMMAND}\t list postgres instances'