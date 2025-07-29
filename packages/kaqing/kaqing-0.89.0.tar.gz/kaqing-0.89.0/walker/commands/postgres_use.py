import requests

from walker.commands.command import Command
# from walker.commands.postgres import Postgres
from walker.commands.postgres_ls import PostgresLs
from walker.commands.postgres_session import PostgresSession
from walker.commands.reaper_session import ReaperSession
from walker.config import Config
from walker.k8s_utils import get_secret_data, list_secrets
from walker.repl_state import ReplState, RequiredState
from walker.utils import convert_seconds, epoch, lines_to_tabular, log, log2

class PostgresUse(Command):
    COMMAND = 'pg use'
    reaper_login = None

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(PostgresUse, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return PostgresUse.COMMAND

    def required(self):
        return RequiredState.CLUSTER

    def run(self, cmd: str, s0: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, s0)

        state, args = self.apply_state(args, s0)
        if not self.validate_state(state):
            return state

        pg = state.pg
        if len(args) > 0:
            pg = args[0]

        if not pg:
            log2('pg-name is missing.')

            log2(lines_to_tabular(PostgresSession.instances(state)))

            return state

        self.use_pg(s0, pg)

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
        return f'{PostgresUse.COMMAND}: set to postgres db'