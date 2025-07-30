import click

from walker.commands.command import Command
from walker.commands.command_helpers import ClusterCommandHelper
from walker.commands.postgres_ls import PostgresLs
from walker.commands.postgres_session import PostgresSession
from walker.repl_state import ReplState, RequiredState
from walker.utils import lines_to_tabular, log, log2

class Postgres(Command):
    COMMAND = 'pg'
    reaper_login = None

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Postgres, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return Postgres.COMMAND

    # def required(self):
    #     return RequiredState.NAMESPACE

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)
        if not self.validate_state(state):
            return state

        if state.in_repl:
            if not args:
                log2('Please use SQL statement. e.g. pg \l')

                return 'command-missing'
            else:
                self.run_sql(state, args)
        else:
            if not args:
                log2('* Command or SQL statements is missing.')
                Command.display_help()

                return 'command-missing'
            else:
                # head with the Chain of Responsibility pattern
                cmds = Command.chain(Postgres.cmd_list())
                if not cmds.run(cmd, state) :
                    if not args:
                        log2('* Command or SQL statements is missing.')
                        Command.display_help()

                        return 'command-missing'
                    else:
                        self.run_sql(state, args)

        return state

    def cmd_list():
        return [PostgresLs()]

    def run_sql(self, state: ReplState, args: list[str]):
        if not state.pg_path:
            if state.in_repl:
                log2('Enter "use <pg-name>" first.')
            else:
                log2('* pg-name is missing.')

            return state

        PostgresSession(state.namespace, state.pg_path).run_sql(' '.join(args))

    def completion(self, state: ReplState):
        if state.sts:
            leaf = {'\h': None}
            if state.pg_path:
                leaf |= {
                    '\l': None,
                    '\d': None,
                    '\dt': None,
                    '\du': None,
                }

            return super().completion(state, leaf)

        return {}

    def help(self, _: ReplState):
        return f'[{Postgres.COMMAND}] <sql-statements>\t run psql with queries'

class PostgresCommandHelper(click.Command):
    def get_help(self, ctx: click.Context):
        log(super().get_help(ctx))
        log()
        ClusterCommandHelper.cluster_help()
        log('PG-Name: Kubernetes secret for Postgres credentials')
        log('         e.g. stgawsscpsr-c3-c3-k8spg-cs-001')