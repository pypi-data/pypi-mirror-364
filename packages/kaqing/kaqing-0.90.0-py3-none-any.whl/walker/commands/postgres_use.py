import copy

from walker.commands.command import Command
from walker.commands.postgres_session import PostgresSession
from walker.k8s_utils import get_secret_data
from walker.repl_state import ReplState, RequiredState
from walker.utils import lines_to_tabular, log2

class UsePostgres(Command):
    COMMAND = 'use'
    reaper_login = None

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(UsePostgres, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return UsePostgres.COMMAND

    def required(self):
        return RequiredState.CLUSTER

    def run(self, cmd: str, s0: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, s0)

        state, args = self.apply_state(args, s0, resolve_pg=False)
        if not self.validate_state(state):
            return state

        if len(args) < 1:
            log2('pg-name is missing.')
            log2()

            # log2(lines_to_tabular(PostgresSession.instances(state)))
            def line(pg: PostgresSession):
                s1 = copy.copy(state)
                s1.pg = pg.name
                return f'{pg.name},{pg.endpoint(s1)}:{pg.port(s1)},{pg.username(s1)},{pg.password(s1)}'

            lines = [line(PostgresSession(pg)) for pg in PostgresSession.instances(state)]

            log2(lines_to_tabular(lines, separator=','))

            return state

        self.use_pg(s0, args[0])

        return state

    def use_pg(self, state: ReplState, pg: str):
        if get_secret_data(state.namespace, pg):
            state.pg = pg
            log2(f'Postgres is set to {pg}.')
        else:
            log2(f'Cannot find or connect to {pg}.')

    def completion(self, state: ReplState):
        if state.sts:
            leaf = {id: None for id in PostgresSession.instances(state)}
            return super().completion(state, leaf)

        return {}

    def help(self, _: ReplState):
        return f'{UsePostgres.COMMAND} <pg-name>: set to postgres db'