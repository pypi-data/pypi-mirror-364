import click
import psycopg2

from walker.commands.command import Command
from walker.commands.command_helpers import ClusterCommandHelper
from walker.commands.postgres_ls import PostgresLs
from walker.commands.postgres_session import PostgresSession
from walker.commands.postgres_use import PostgresUse
from walker.commands.reaper_forward import ReaperForward
from walker.commands.reaper_forward_stop import ReaperForwardStop
from walker.commands.reaper_restart import ReaperRestart
from walker.commands.reaper_run_abort import ReaperRunAbort
from walker.commands.reaper_runs import ReaperRuns
from walker.commands.reaper_runs_abort import ReaperRunsAbort
from walker.commands.reaper_schedule_activate import ReaperScheduleActivate
from walker.commands.reaper_schedule_start import ReaperScheduleStart
from walker.commands.reaper_schedule_stop import ReaperScheduleStop
from walker.commands.reaper_schedules import ReaperSchedules
from walker.commands.reaper_status import ReaperStatus
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

    def required(self):
        return RequiredState.CLUSTER

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)
        if not self.validate_state(state):
            return state

        if state.in_repl:
            if not args:
                log(lines_to_tabular([c.help(ReplState()) for c in Postgres.cmd_list()], separator=':'))

                return 'command-missing'
            else:
                self.run_sql(state, args)
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

    def run_sql(self, state: ReplState, args: list[str]):
        if not state.pg:
            if state.in_repl:
                log2('Use <pg-name> first.')
            else:
                log2('* pg-name is missing.')

            return state

        PostgresSession(state.pg).run_sql(state, ' '.join(args))

    def cmd_list():
        return [PostgresLs(), PostgresUse()]

    def completion(self, state: ReplState):
        if state.sts:
            return super().completion(state)

        return {}

    def help(self, _: ReplState):
        return None

class PostgresCommandHelper(click.Command):
    def get_help(self, ctx: click.Context):
        log(super().get_help(ctx))
        log()
        log('Sub-Commands:')

        log(lines_to_tabular([c.help(ReplState()).replace(f'{Postgres.COMMAND} ', '  ', 1) for c in [PostgresLs()]], separator=':'))
        log()
        ClusterCommandHelper.cluster_help()
        log('PG-Name: Kubernetes secret for Postgres credentials')
        log('         e.g. stgawsscpsr-c3-c3-k8spg-cs-001')